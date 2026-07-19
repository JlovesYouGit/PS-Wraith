const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const IV_LENGTH = 16;
const AUTH_TAG_LENGTH = 16;
const HMAC_ALGORITHM = 'sha512';

class SecureChannel {
  constructor(options = {}) {
    this.nodeId = options.nodeId || 'default';
    this.sharedKeys = new Map();
    this.keyRotationInterval = options.keyRotationInterval || 3600000;
    this.auditLog = [];
    this.maxAuditEntries = options.maxAuditEntries || 10000;
    this.defaultKey = this._generateKey(options.secret || 'render_paradox_default_secret');
    this._startKeyRotation();
  }

  _generateKey(secret) {
    const hash = crypto.createHash('sha512').update(secret + this.nodeId + Date.now()).digest();
    return hash.slice(0, KEY_LENGTH);
  }

  _startKeyRotation() {
    this._keyRotationTimer = setInterval(() => {
      this.defaultKey = this._generateKey();
      this._logAudit('KEY_ROTATION', { nodeId: this.nodeId, timestamp: Date.now() });
    }, this.keyRotationInterval);
  }

  addSharedKey(peerId, sharedSecret) {
    const key = this._generateKey(sharedSecret);
    this.sharedKeys.set(peerId, key);
    this._logAudit('KEY_EXCHANGE', { peerId, nodeId: this.nodeId });
    return key;
  }

  encrypt(data, peerId = null) {
    const key = peerId && this.sharedKeys.has(peerId) ? this.sharedKeys.get(peerId) : this.defaultKey;
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag().toString('hex');

    const hmac = crypto.createHmac(HMAC_ALGORITHM, key)
      .update(encrypted + authTag)
      .digest('hex');

    return {
      v: 1,
      alg: ALGORITHM,
      iv: iv.toString('hex'),
      ct: encrypted,
      tag: authTag,
      hmac,
      from: this.nodeId,
      ts: Date.now()
    };
  }

  decrypt(packet) {
    const key = packet.from && this.sharedKeys.has(packet.from) ? this.sharedKeys.get(packet.from) : this.defaultKey;

    const hmac = crypto.createHmac(HMAC_ALGORITHM, key)
      .update(packet.ct + packet.tag)
      .digest('hex');

    if (hmac !== packet.hmac) {
      this._logAudit('HMAC_VERIFICATION_FAILED', { from: packet.from, nodeId: this.nodeId });
      throw new Error('HMAC verification failed');
    }

    const decipher = crypto.createDecipheriv(ALGORITHM, key, Buffer.from(packet.iv, 'hex'));
    decipher.setAuthTag(Buffer.from(packet.tag, 'hex'));

    let decrypted = decipher.update(packet.ct, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    this._logAudit('DECRYPT_SUCCESS', { from: packet.from, nodeId: this.nodeId });
    return JSON.parse(decrypted);
  }

  sign(data) {
    const signature = crypto.createHmac(HMAC_ALGORITHM, this.defaultKey)
      .update(JSON.stringify(data))
      .digest('hex');
    return { ...data, sig: signature, signed_by: this.nodeId, signed_at: Date.now() };
  }

  verifySignature(data) {
    if (!data.sig || !data.signed_by) return false;
    const expectedSig = crypto.createHmac(HMAC_ALGORITHM, this.defaultKey)
      .update(JSON.stringify(data))
      .digest('hex');
    return crypto.timingSafeEqual(Buffer.from(data.sig), Buffer.from(expectedSig));
  }

  _logAudit(event, details) {
    this.auditLog.push({
      event,
      details,
      timestamp: Date.now(),
      nodeId: this.nodeId
    });

    if (this.auditLog.length > this.maxAuditEntries) {
      this.auditLog.shift();
    }
  }

  getAuditLog() {
    return [...this.auditLog];
  }

  destroy() {
    if (this._keyRotationTimer) clearInterval(this._keyRotationTimer);
    this.sharedKeys.clear();
    this.auditLog.length = 0;
  }
}

class Packet {
  constructor(options = {}) {
    this.id = options.id || `pkt_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    this.type = options.type || 'DATA';
    this.fromNode = options.fromNode;
    this.toNode = options.toNode;
    this.payload = options.payload || {};
    this.priority = options.priority || 5;
    this.ttl = options.ttl || 300;
    this.route = options.route || [];
    this.metadata = options.metadata || {};
    this.timestamp = Date.now();
    this.checksum = this._computeChecksum();
  }

  _computeChecksum() {
    const data = `${this.id}:${this.type}:${this.fromNode}:${this.toNode}:${this.timestamp}`;
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  addHop(nodeId) {
    this.route.push({ node: nodeId, timestamp: Date.now() });
    this.timestamp = Date.now();
    this.checksum = this._computeChecksum();
  }

  isExpired() {
    return Date.now() - this.timestamp > this.ttl * 1000;
  }

  toJSON() {
    return {
      id: this.id,
      type: this.type,
      fromNode: this.fromNode,
      toNode: this.toNode,
      payload: this.payload,
      priority: this.priority,
      ttl: this.ttl,
      route: this.route,
      metadata: this.metadata,
      timestamp: this.timestamp,
      checksum: this.checksum
    };
  }

  static fromJSON(json) {
    const packet = new Packet({
      id: json.id,
      type: json.type,
      fromNode: json.fromNode,
      toNode: json.toNode,
      payload: json.payload,
      priority: json.priority,
      ttl: json.ttl,
      route: json.route,
      metadata: json.metadata
    });
    packet.timestamp = json.timestamp;
    packet.checksum = json.checksum;
    return packet;
  }
}

class PacketFactory {
  static createDataPacket(fromNode, toNode, payload, options = {}) {
    return new Packet({
      type: 'DATA',
      fromNode,
      toNode,
      payload,
      ...options
    });
  }

  static createControlPacket(fromNode, toNode, command, options = {}) {
    return new Packet({
      type: 'CONTROL',
      fromNode,
      toNode,
      payload: { command, params: options.params || {} },
      priority: options.priority || 10,
      ...options
    });
  }

  static createHeartbeatPacket(nodeId, stats = {}) {
    return new Packet({
      type: 'HEARTBEAT',
      fromNode: nodeId,
      toNode: 'broadcast',
      payload: { stats, uptime: process.uptime() },
      priority: 1,
      ttl: 60
    });
  }

  static createDiscoveryPacket(nodeId) {
    return new Packet({
      type: 'DISCOVERY',
      fromNode: nodeId,
      toNode: 'broadcast',
      payload: { capabilities: ['render_paradox', 'spectrum_hz', 'secure_channel'] },
      priority: 1,
      ttl: 120
    });
  }

  static createDominionPacket(fromNode, toNode, dominionHash, metrics, options = {}) {
    return new Packet({
      type: 'DOMINION',
      fromNode,
      toNode,
      payload: { dominion_hash: dominionHash, metrics, target: toNode },
      priority: 20,
      ttl: 600,
      ...options
    });
  }
}

module.exports = {
  SecureChannel,
  Packet,
  PacketFactory,
  ALGORITHM,
  KEY_LENGTH,
  IV_LENGTH,
  HMAC_ALGORITHM
};
