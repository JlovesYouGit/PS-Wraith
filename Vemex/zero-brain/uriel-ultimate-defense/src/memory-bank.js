const EventEmitter = require('events');
const crypto = require('crypto');
const { Packet } = require('./secure-channel');

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const IV_LENGTH = 16;

class MemoryBank extends EventEmitter {
  constructor(options = {}) {
    super();
    this._store = new Map();
    this.indexes = {
      byNode: new Map(),
      byType: new Map(),
      byPriority: new Map()
    };
    this.maxSize = options.maxSize || 100000;
    this.defaultTTL = options.defaultTTL || 300000;
    this.encryptionEnabled = options.encryptionEnabled !== false;
    this.encryptionKey = options.encryptionKey || crypto.randomBytes(32);
    this.accessLog = [];
    this.maxLogEntries = options.maxLogEntries || 50000;
    this.totalBytesStored = 0;
    this.evictionPolicy = options.evictionPolicy || 'LRU';
  }

  store(packet) {
    if (this._store.size >= this.maxSize) {
      this._evict();
    }

    if (packet.isExpired()) {
      this.emit('expired', packet);
      return null;
    }

    const entry = {
      packet: packet.toJSON ? packet.toJSON() : packet,
      storedAt: Date.now(),
      accessCount: 0,
      lastAccess: Date.now(),
      encrypted: false
    };

    if (this.encryptionEnabled) {
      entry.packet = this._encryptEntry(entry.packet);
      entry.encrypted = true;
    }

    this._store.set(packet.id, entry);
    this._indexPacket(packet.id, packet);
    this._updateSize(packet.id, entry);

    this.accessLog.push({
      action: 'STORE',
      packetId: packet.id,
      from: packet.fromNode,
      to: packet.toNode,
      timestamp: Date.now()
    });

    if (this.accessLog.length > this.maxLogEntries) this.accessLog.shift();

    this.emit('stored', { packetId: packet.id, size: this._estimateSize(entry) });
    return packet.id;
  }

  retrieve(packetId) {
    const entry = this._store.get(packetId);
    if (!entry) {
      this.emit('miss', packetId);
      return null;
    }

    if (entry.packet.ttl && Date.now() - entry.packet.timestamp > entry.packet.ttl * 1000) {
      this.delete(packetId);
      this.emit('expired_on_access', packetId);
      return null;
    }

    entry.accessCount++;
    entry.lastAccess = Date.now();

    let packet = entry.packet;
    if (entry.encrypted) {
      packet = this._decryptEntry(packet);
    }

    this.accessLog.push({
      action: 'RETRIEVE',
      packetId,
      timestamp: Date.now()
    });

    if (this.accessLog.length > this.maxLogEntries) this.accessLog.shift();

    this.emit('retrieved', { packetId, accessCount: entry.accessCount });
    return Packet.fromJSON ? Packet.fromJSON(packet) : packet;
  }

  retrieveByNode(nodeId) {
    const ids = this.indexes.byNode.get(nodeId) || [];
    const results = [];
    for (const id of ids) {
      const entry = this._store.get(id);
      if (entry) {
        entry.accessCount++;
        entry.lastAccess = Date.now();
        let packet = entry.packet;
        if (entry.encrypted) packet = this._decryptEntry(packet);
        results.push(Packet.fromJSON ? Packet.fromJSON(packet) : packet);
      }
    }
    this.emit('node_retrieved', { nodeId, count: results.length });
    return results;
  }

  delete(packetId) {
    const entry = this._store.get(packetId);
    if (!entry) return false;

    this._removeFromIndexes(packetId, entry);
    const size = this._estimateSize(entry);
    this.totalBytesStored = Math.max(0, this.totalBytesStored - size);
    this._store.delete(packetId);

    this.accessLog.push({
      action: 'DELETE',
      packetId,
      timestamp: Date.now()
    });

    this.emit('deleted', packetId);
    return true;
  }

  clear() {
    this._store.clear();
    this.indexes.byNode.clear();
    this.indexes.byType.clear();
    this.indexes.byPriority.clear();
    this.totalBytesStored = 0;
    this.accessLog.length = 0;
    this.emit('cleared');
  }

  getStats() {
    return {
      totalPackets: this._store.size,
      totalBytes: this.totalBytesStored,
      maxSize: this.maxSize,
      utilization: (this._store.size / this.maxSize * 100).toFixed(2),
      byNode: Object.fromEntries(
        Array.from(this.indexes.byNode.entries()).map(([k, v]) => [k, v.length])
      ),
      byType: Object.fromEntries(
        Array.from(this.indexes.byType.entries()).map((k, v) => [k, v.length])
      ),
      accessLogSize: this.accessLog.length
    };
  }

  _indexPacket(packetId, packet) {
    const nodeKeys = [packet.fromNode, packet.toNode];
    for (const nodeId of nodeKeys) {
      if (!this.indexes.byNode.has(nodeId)) this.indexes.byNode.set(nodeId, []);
      if (!this.indexes.byNode.get(nodeId).includes(packetId)) {
        this.indexes.byNode.get(nodeId).push(packetId);
      }
    }

    if (!this.indexes.byType.has(packet.type)) this.indexes.byType.set(packet.type, []);
    if (!this.indexes.byType.get(packet.type).includes(packetId)) {
      this.indexes.byType.get(packet.type).push(packetId);
    }

    if (!this.indexes.byPriority.has(packet.priority)) this.indexes.byPriority.set(packet.priority, []);
    if (!this.indexes.byPriority.get(packet.priority).includes(packetId)) {
      this.indexes.byPriority.get(packet.priority).push(packetId);
    }
  }

  _removeFromIndexes(packetId, entry) {
    const packet = entry.packet;
    const nodeKeys = [packet.fromNode, packet.toNode];
    for (const nodeId of nodeKeys) {
      const arr = this.indexes.byNode.get(nodeId);
      if (arr) {
        const idx = arr.indexOf(packetId);
        if (idx > -1) arr.splice(idx, 1);
      }
    }

    const typeArr = this.indexes.byType.get(packet.type);
    if (typeArr) {
      const idx = typeArr.indexOf(packetId);
      if (idx > -1) typeArr.splice(idx, 1);
    }

    const priorityArr = this.indexes.byPriority.get(packet.priority);
    if (priorityArr) {
      const idx = priorityArr.indexOf(packetId);
      if (idx > -1) priorityArr.splice(idx, 1);
    }
  }

  _evict() {
    if (this._store.size === 0) return;

    let victimId;
    if (this.evictionPolicy === 'LRU') {
      let oldest = null;
      for (const [id, entry] of this._store) {
        if (!oldest || entry.lastAccess < oldest.lastAccess) oldest = { id, entry };
      }
      victimId = oldest.id;
    } else {
      const firstKey = this._store.keys().next().value;
      victimId = firstKey;
    }

    if (victimId) this.delete(victimId);
  }

  _updateSize(packetId, entry) {
    const size = this._estimateSize(entry);
    this.totalBytesStored += size;
  }

  _estimateSize(entry) {
    const json = JSON.stringify(entry.packet);
    return Buffer.byteLength(json, 'utf8');
  }

  _encryptEntry(data) {
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, this.encryptionKey, iv);
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return {
      v: 1,
      iv: iv.toString('hex'),
      ct: encrypted,
      tag: cipher.getAuthTag().toString('hex')
    };
  }

  _decryptEntry(encryptedData) {
    const decipher = crypto.createDecipheriv(ALGORITHM, this.encryptionKey, Buffer.from(encryptedData.iv, 'hex'));
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));
    let decrypted = decipher.update(encryptedData.ct, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return JSON.parse(decrypted);
  }

  destroy() {
    this.clear();
    this.removeAllListeners();
  }
}

module.exports = { MemoryBank };
