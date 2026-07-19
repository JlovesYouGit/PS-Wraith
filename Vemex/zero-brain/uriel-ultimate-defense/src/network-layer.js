const EventEmitter = require('events');
const net = require('net');
const crypto = require('crypto');
const os = require('os');

class NetworkNode extends EventEmitter {
  constructor(options = {}) {
    super();
    this.nodeId = options.nodeId || `node_${crypto.randomBytes(4).toString('hex')}`;
    this.host = options.host || '0.0.0.0';
    this.port = options.port || 0;
    this.isServer = options.isServer !== false;
    this.maxConnections = options.maxConnections || 1000;
    this.connections = new Map();
    this.connectionIdCounter = 0;
    this.packetHandlers = new Map();
    this.trafficStats = {
      bytesIn: 0,
      bytesOut: 0,
      packetsIn: 0,
      packetsOut: 0,
      connectionsAccepted: 0,
      connectionsDropped: 0
    };
    this.rateLimiter = {
      maxPacketsPerSecond: options.maxPacketsPerSecond || 10000,
      windowMs: options.rateWindowMs || 1000,
      currentWindow: [],
      violations: 0
    };
    this.acl = new Map();
    this.encrypted = options.encrypted !== false;
    this.secureChannel = options.secureChannel || null;
    this.browserEndpoints = new Map();
    this.protocolVersion = options.protocolVersion || '1.0';
  }

  start() {
    if (this.isServer) {
      this.server = net.createServer((socket) => this._handleConnection(socket));
      this.server.maxConnections = this.maxConnections;
      this.server.listen(this.port, this.host, () => {
        const address = this.server.address();
        this.port = address.port;
        this.emit('listening', { nodeId: this.nodeId, host: this.host, port: this.port });
      });

      this.server.on('error', (err) => {
        this.emit('error', { nodeId: this.nodeId, error: err.message });
      });
    } else {
      this.emit('listening', { nodeId: this.nodeId, mode: 'client_only' });
    }

    this.emit('started', { nodeId: this.nodeId });
  }

  stop() {
    if (this.server) {
      this.server.close();
      this.server = null;
    }

    for (const [connId, conn] of this.connections) {
      this._closeConnection(connId);
    }

    this.emit('stopped', { nodeId: this.nodeId });
  }

  _handleConnection(socket) {
    const connId = `${this.nodeId}_conn_${++this.connectionIdCounter}`;
    const remoteAddress = socket.remoteAddress;
    const remotePort = socket.remotePort;

    if (!this._checkACL(remoteAddress)) {
      socket.destroy();
      this.trafficStats.connectionsDropped++;
      this.emit('connection_rejected', { connId, reason: 'ACL', remoteAddress });
      return;
    }

    if (this.connections.size >= this.maxConnections) {
      socket.destroy();
      this.trafficStats.connectionsDropped++;
      this.emit('connection_rejected', { connId, reason: 'MAX_CONNECTIONS' });
      return;
    }

    const connection = {
      id: connId,
      socket,
      remoteAddress,
      remotePort,
      nodeId: null,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      packetsReceived: 0,
      packetsSent: 0,
      bytesReceived: 0,
      bytesSent: 0,
      encrypted: this.encrypted && this.secureChannel
    };

    this.connections.set(connId, connection);
    this.trafficStats.connectionsAccepted++;

    socket.on('data', (data) => this._handleData(connId, data));
    socket.on('error', (err) => this._handleError(connId, err));
    socket.on('close', () => this._handleClose(connId));
    socket.on('timeout', () => this._handleTimeout(connId));

    this.emit('connection_accepted', { connId, remoteAddress, remotePort, nodeId: this.nodeId });
  }

  _handleData(connId, data) {
    const conn = this.connections.get(connId);
    if (!conn) return;

    if (!this._checkRateLimit()) {
      this.rateLimiter.violations++;
      this.emit('rate_limit_exceeded', { connId, nodeId: this.nodeId });
      this._closeConnection(connId);
      return;
    }

    conn.lastActivity = Date.now();
    conn.bytesReceived += data.length;
    this.trafficStats.bytesIn += data.length;

    const rawPackets = this._deserialize(data);
    for (const raw of rawPackets) {
      try {
        let packet = raw;
        if (this.encrypted && this.secureChannel && raw.v && raw.ct) {
          packet = this.secureChannel.decrypt(raw);
        }

        if (packet.from) conn.nodeId = packet.from;
        packet.addHop(this.nodeId);

        this.trafficStats.packetsIn++;
        conn.packetsReceived++;

        const handler = this.packetHandlers.get(packet.type);
        if (handler) {
          handler(packet, connId);
        } else {
          this.emit('packet', { packet, connId, nodeId: this.nodeId });
        }

        this.emit('packet_received', {
          packetId: packet.id,
          type: packet.type,
          from: packet.from,
          to: packet.to,
          connId,
          nodeId: this.nodeId
        });
      } catch (err) {
        this.emit('packet_error', { connId, error: err.message, raw });
      }
    }
  }

  send(targetNodeId, packet) {
    packet.addHop(this.nodeId);

    const serialized = this.encrypted && this.secureChannel && packet.from
      ? this.secureChannel.encrypt(packet.toJSON ? packet.toJSON() : packet, packet.from)
      : (packet.toJSON ? packet.toJSON() : packet);

    const data = this._serialize(serialized);
    const sent = this._sendData(targetNodeId, data);

    if (sent) {
      this.trafficStats.packetsOut++;
      this.trafficStats.bytesOut += data.length;
      this.emit('packet_sent', {
        packetId: packet.id,
        targetNodeId,
        size: data.length,
        nodeId: this.nodeId
      });
    }

    return sent;
  }

  _sendData(targetNodeId, data) {
    if (targetNodeId === this.nodeId) {
      this.emit('packet', { packet: data, connId: 'self', nodeId: this.nodeId });
      return true;
    }

    for (const [connId, conn] of this.connections) {
      if (conn.nodeId === targetNodeId) {
        try {
          conn.socket.write(data);
          conn.packetsSent++;
          conn.bytesSent += data.length;
          conn.lastActivity = Date.now();
          return true;
        } catch (err) {
          this.emit('send_error', { connId, error: err.message });
          this._closeConnection(connId);
        }
      }
    }

    const browserConn = this.browserEndpoints.get(targetNodeId);
    if (browserConn && browserConn.readyState === 1) {
      try {
        browserConn.send(JSON.stringify(data));
        return true;
      } catch (err) {
        this.emit('send_error', { endpoint: targetNodeId, error: err.message });
      }
    }

    this.emit('route_not_found', { targetNodeId, nodeId: this.nodeId });
    return false;
  }

  registerPacketHandler(type, handler) {
    this.packetHandlers.set(type, handler);
    this.emit('handler_registered', { type, nodeId: this.nodeId });
    return true;
  }

  addACL(rule) {
    this.acl.set(rule.id || crypto.randomBytes(8).toString('hex'), rule);
    this.emit('acl_updated', { action: 'add', rule, nodeId: this.nodeId });
  }

  removeACL(ruleId) {
    const removed = this.acl.delete(ruleId);
    this.emit('acl_updated', { action: 'remove', ruleId, removed, nodeId: this.nodeId });
    return removed;
  }

  _checkACL(remoteAddress) {
    if (this.acl.size === 0) return true;

    for (const rule of this.acl.values()) {
      if (rule.action === 'deny' && this._matchesRule(remoteAddress, rule)) return false;
      if (rule.action === 'allow' && this._matchesRule(remoteAddress, rule)) return true;
    }

    return this.acl.size === 0 || Array.from(this.acl.values()).every(r => r.action !== 'deny');
  }

  _matchesRule(address, rule) {
    if (rule.subnet) {
      const [subnet, prefix] = rule.subnet.split('/');
      const mask = -1 << (32 - parseInt(prefix));
      const subnetNum = this._ipToNumber(subnet);
      const addrNum = this._ipToNumber(address);
      return (subnetNum & mask) === (addrNum & mask);
    }
    return rule.address === address || rule.address === '*';
  }

  _ipToNumber(ip) {
    return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0) >>> 0;
  }

  _checkRateLimit() {
    const now = Date.now();
    this.rateLimiter.currentWindow = this.rateLimiter.currentWindow.filter(t => now - t < this.rateLimiter.windowMs);
    this.rateLimiter.currentWindow.push(now);

    return this.rateLimiter.currentWindow.length <= this.rateLimiter.maxPacketsPerSecond;
  }

  _handleError(connId, err) {
    this.emit('connection_error', { connId, error: err.message, nodeId: this.nodeId });
    this._closeConnection(connId);
  }

  _handleClose(connId) {
    const conn = this.connections.get(connId);
    if (conn) {
      this.emit('connection_closed', {
        connId,
        remoteAddress: conn.remoteAddress,
        uptime: Date.now() - conn.connectedAt,
        nodeId: this.nodeId
      });
      this.connections.delete(connId);
    }
  }

  _handleTimeout(connId) {
    this.emit('connection_timeout', { connId, nodeId: this.nodeId });
    this._closeConnection(connId);
  }

  _closeConnection(connId) {
    const conn = this.connections.get(connId);
    if (conn && conn.socket && !conn.socket.destroyed) {
      try { conn.socket.destroy(); } catch (e) {}
    }
    this.connections.delete(connId);
  }

  _serialize(data) {
    if (Buffer.isBuffer(data)) return data;
    if (typeof data === 'string') return Buffer.from(data, 'utf8');
    return Buffer.from(JSON.stringify(data), 'utf8');
  }

  _deserialize(buffer) {
    const str = buffer.toString('utf8');
    const packets = [];
    const lines = str.split('\n').filter(l => l.trim());

    for (const line of lines) {
      try {
        packets.push(JSON.parse(line));
      } catch (e) {
        packets.push({ raw: line, error: 'parse_failed' });
      }
    }

    return packets.length > 0 ? packets : [{ raw: str }];
  }

  getStats() {
    const connectionStats = {
      total: this.connections.size,
      byNode: {}
    };

    for (const conn of this.connections.values()) {
      connectionStats.byNode[conn.nodeId || 'unknown'] = (connectionStats.byNode[conn.nodeId || 'unknown'] || 0) + 1;
    }

    return {
      nodeId: this.nodeId,
      host: this.host,
      port: this.port,
      isServer: this.isServer,
      traffic: this.trafficStats,
      connections: connectionStats,
      rateLimiter: {
        current: this.rateLimiter.currentWindow.length,
        max: this.rateLimiter.maxPacketsPerSecond,
        violations: this.rateLimiter.violations
      },
      aclRules: this.acl.size,
      handlers: Array.from(this.packetHandlers.keys()),
      protocol: this.protocolVersion
    };
  }

  destroy() {
    this.stop();
    this.packetHandlers.clear();
    this.acl.clear();
    this.browserEndpoints.clear();
    this.removeAllListeners();
  }
}

class BrowserBridge {
  constructor(networkNode) {
    this.networkNode = networkNode;
    this.httpServer = null;
    this.wss = null;
    this.browserClients = new Map();
  }

  startHTTP(port = 8080) {
    const http = require('http');
    this.httpServer = http.createServer((req, res) => {
      if (req.url === '/api/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(this.networkNode.getStats()));
      } else if (req.url === '/api/packets') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ method: 'GET', path: req.url, status: 'endpoint_available' }));
      } else {
        res.writeHead(404);
        res.end('Not Found');
      }
    });

    this.httpServer.listen(port, () => {
      this.networkNode.emit('http_listening', { port, nodeId: this.networkNode.nodeId });
    });

    return this.httpServer;
  }

  registerBrowserClient(client, clientId) {
    this.browserClients.set(clientId || client.id, client);
    this.networkNode.browserEndpoints.set(clientId || client.id, client);

    client.on('message', (data) => {
      try {
        const packet = JSON.parse(data.toString());
        packet.from = clientId || client.id;
        this.networkNode.emit('packet', { packet, connId: `browser_${clientId}`, nodeId: this.networkNode.nodeId });
      } catch (e) {
        this.networkNode.emit('browser_error', { clientId, error: e.message });
      }
    });

    client.on('close', () => {
      this.browserClients.delete(clientId || client.id);
      this.networkNode.browserEndpoints.delete(clientId || client.id);
    });

    this.networkNode.emit('browser_registered', { clientId: clientId || client.id });
  }

  sendToBrowser(clientId, data) {
    const client = this.browserClients.get(clientId);
    if (client && client.readyState === 1) {
      client.send(JSON.stringify(data));
      return true;
    }
    return false;
  }

  broadcastToBrowsers(data) {
    let sent = 0;
    for (const [clientId, client] of this.browserClients) {
      if (client.readyState === 1) {
        try {
          client.send(JSON.stringify(data));
          sent++;
        } catch (e) {}
      }
    }
    return sent;
  }
}

module.exports = { NetworkNode, BrowserBridge };
