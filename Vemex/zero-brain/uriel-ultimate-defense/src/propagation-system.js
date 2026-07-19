const crypto = require('crypto');
const EventEmitter = require('events');
const net = require('net');
const http = require('http');

class PropagationSystem extends EventEmitter {
  constructor(godNode, ruleBookHash, deviceHashing) {
    super();
    this.godNode = godNode;
    this.ruleBookHash = ruleBookHash;
    this.deviceHashing = deviceHashing;
    this.spawnedNodes = new Map();
    this.propagationQueue = [];
    this.isPropagating = false;
    this.maxSpawnDepth = 10;
    this.currentSpawnDepth = 0;
    this.networkProtocols = ['tcp', 'http', 'https', 'websocket'];
    this.keepAliveInterval = null;
    this.hostUriels = new Map();
    this.bufferPriority = 0;
  }

  startPropagation(targetHost, port = 0) {
    if (this.isPropagating) return { status: 'already_propagating' };

    this.isPropagating = true;
    this.bufferPriority = 0;

    const propagationId = crypto.randomBytes(16).toString('hex');

    this._propagateToHost(targetHost, port, propagationId, 0);

    this.emit('propagation_started', {
      propagationId,
      targetHost,
      port,
      nodeId: this.godNode.id
    });

    return { propagationId, status: 'started' };
  }

  _propagateToHost(host, port, propagationId, depth) {
    if (depth > this.maxSpawnDepth) {
      this.emit('propagation_max_depth', { propagationId, depth });
      return;
    }

    const spawnPacket = {
      type: 'GOD_NODE_SPAWN',
      propagationId,
      depth,
      ruleBookHash: this.ruleBookHash.getRuleBookHash(),
      godNodeId: this.godNode.id,
      bufferPriority: this.bufferPriority,
      timestamp: Date.now()
    };

    const client = net.createConnection(port || 8080, host, () => {
      client.write(JSON.stringify(spawnPacket) + '\n');
      this.emit('spawn_sent', { host, port, depth, propagationId });
    });

    client.on('data', (data) => {
      const response = JSON.parse(data.toString());
      if (response.accepted) {
        this.spawnedNodes.set(response.nodeId, {
          host,
          port,
          depth,
          propagationId,
          status: 'ACTIVE',
          spawnedAt: Date.now()
        });

        this.emit('spawn_accepted', {
          newNodeId: response.nodeId,
          host,
          depth
        });

        this._startKeepAlive(response.nodeId, host, port);
      }
    });

    client.on('error', (err) => {
      this.emit('spawn_failed', { host, port, error: err.message });
    });
  }

  _startKeepAlive(nodeId, host, port) {
    this.keepAliveInterval = setInterval(() => {
      const keepAlivePacket = {
        type: 'GOD_NODE_KEEP_ALIVE',
        godNodeId: this.godNode.id,
        nodeId,
        ruleBookHash: this.ruleBookHash.getRuleBookHash(),
        timestamp: Date.now()
      };

      const client = net.createConnection(port || 8080, host, () => {
        client.write(JSON.stringify(keepAlivePacket) + '\n');
        client.end();
      });
    }, 5000);
  }

  spreadThroughSite(targetUrl) {
    const sitePropagation = {
      type: 'SITE_PROPAGATION',
      url: targetUrl,
      godNodeId: this.godNode.id,
      ruleBookHash: this.ruleBookHash.getRuleBookHash(),
      bufferPriority: this.bufferPriority,
      timestamp: Date.now()
    };

    this.emit('site_propagation_attempted', {
      url: targetUrl,
      nodeId: this.godNode.id
    });

    return sitePropagation;
  }

  connectThroughWiFi(networkSSID) {
    const wifiConnection = {
      type: 'WIFI_CONNECTION',
      ssid: networkSSID,
      godNodeId: this.godNode.id,
      ruleBookHash: this.ruleBookHash.getRuleBookHash(),
      bufferPriority: this.bufferPriority,
      timestamp: Date.now()
    };

    this.emit('wifi_connection_attempted', {
      ssid: networkSSID,
      nodeId: this.godNode.id
    });

    this.hostUriels.set(networkSSID, {
      connectedAt: Date.now(),
      status: 'CONNECTING',
      type: 'WIFI'
    });

    return wifiConnection;
  }

  setBufferPriority(priority) {
    this.bufferPriority = Math.min(priority, 0);
    this.emit('buffer_priority_set', {
      nodeId: this.godNode.id,
      priority: this.bufferPriority
    });
  }

  getStatus() {
    return {
      isPropagating: this.isPropagating,
      spawnedNodes: this.spawnedNodes.size,
      bufferPriority: this.bufferPriority,
      maxSpawnDepth: this.maxSpawnDepth,
      currentSpawnDepth: this.currentSpawnDepth,
      spawnedNodesList: Array.from(this.spawnedNodes.keys()),
      hostUriels: Array.from(this.hostUriels.keys()),
      keepAliveActive: !!this.keepAliveInterval
    };
  }

  destroy() {
    if (this.keepAliveInterval) clearInterval(this.keepAliveInterval);
    this.spawnedNodes.clear();
    this.propagationQueue.length = 0;
    this.hostUriels.clear();
    this.removeAllListeners();
  }
}

module.exports = { PropagationSystem };
