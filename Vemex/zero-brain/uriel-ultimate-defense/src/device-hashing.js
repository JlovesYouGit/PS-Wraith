const crypto = require('crypto');
const EventEmitter = require('events');

class DeviceHashingNaturalSystem extends EventEmitter {
  constructor() {
    super();
    this.deviceRegistry = new Map();
    this.naturalHashChain = [];
    this.originHash = null;
    this.coordinationRules = {
      GOD_NODE_PRIORITY: 0,
      SAFE_NODE_PRIORITY: 1,
      HOST_NODE_PRIORITY: 2,
      ADversary_NODE_PRIORITY: 99
    };
    this._startNaturalCoordination();
  }

  _startNaturalCoordination() {
    this._coordinationInterval = setInterval(() => {
      this._coordinateFromOrigin();
    }, 1000);
  }

  registerDevice(deviceId, deviceInfo) {
    const naturalHash = this._computeNaturalHash(deviceInfo);
    const deviceEntry = {
      deviceId,
      deviceInfo,
      naturalHash,
      registeredAt: Date.now(),
      lastSeen: Date.now(),
      position: this._assignPosition(deviceInfo),
      status: 'ACTIVE',
      tookOver: false,
      hijackAttempts: 0,
      protectionLevel: 'GOD_NODE'
    };

    this.deviceRegistry.set(deviceId, deviceEntry);
    this.naturalHashChain.push({
      deviceId,
      naturalHash,
      timestamp: Date.now(),
      position: deviceEntry.position
    });

    this.emit('device_registered', { deviceId, naturalHash, position: deviceEntry.position });
    return deviceEntry;
  }

  _computeNaturalHash(deviceInfo) {
    const naturalData = [
      deviceInfo.hostname || 'unknown',
      deviceInfo.platform || 'unknown',
      deviceInfo.arch || 'unknown',
      deviceInfo.macAddress || 'unknown',
      deviceInfo.cpuId || 'unknown',
      deviceInfo.gpuId || 'unknown',
      deviceInfo.biosId || 'unknown',
      Date.now().toString()
    ].join('|');

    return crypto.createHash('sha512').update(naturalData).digest('hex');
  }

  _assignPosition(deviceInfo) {
    const hashInt = parseInt(this._computeNaturalHash(deviceInfo).substring(0, 16), 16);
    if (hashInt % 3 === 0) return 'GOD_NODE';
    if (hashInt % 3 === 1) return 'HOST_NODE';
    return 'SAFE_NODE';
  }

  _coordinateFromOrigin() {
    if (!this.originHash && this.naturalHashChain.length > 0) {
      this.originHash = this.naturalHashChain[0].naturalHash;
    }

    if (this.originHash) {
      for (const [deviceId, device] of this.deviceRegistry) {
        if (device.status === 'ACTIVE' && device.position === 'GOD_NODE') {
          const coordinationSignal = this._generateCoordinationSignal(deviceId);
          this.emit('coordination_signal', {
            from: 'ORIGIN',
            to: deviceId,
            signal: coordinationSignal,
            timestamp: Date.now()
          });
        }
      }
    }
  }

  _generateCoordinationSignal(targetDeviceId) {
    const signalData = `${this.originHash}:${targetDeviceId}:${Date.now()}:COORDINATE`;
    return crypto.createHash('sha256').update(signalData).digest('hex');
  }

  getDeviceById(deviceId) {
    return this.deviceRegistry.get(deviceId);
  }

  getAllDevices() {
    return Array.from(this.deviceRegistry.values());
  }

  getDevicesByPosition(position) {
    return Array.from(this.deviceRegistry.values()).filter(d => d.position === position);
  }

  getGodNodes() {
    return this.getDevicesByPosition('GOD_NODE');
  }

  updateDeviceStatus(deviceId, status) {
    const device = this.deviceRegistry.get(deviceId);
    if (device) {
      device.status = status;
      device.lastSeen = Date.now();
      this.emit('device_status_updated', { deviceId, status });
    }
  }

  getStats() {
    return {
      totalDevices: this.deviceRegistry.size,
      godNodes: this.getGodNodes().length,
      hashChainLength: this.naturalHashChain.length,
      originHash: this.originHash,
      devices: Array.from(this.deviceRegistry.entries()).map(([id, d]) => ({
        deviceId: id,
        position: d.position,
        status: d.status,
        lastSeen: d.lastSeen
      }))
    };
  }

  destroy() {
    if (this._coordinationInterval) clearInterval(this._coordinationInterval);
    this.deviceRegistry.clear();
    this.naturalHashChain.length = 0;
    this.removeAllListeners();
  }
}

module.exports = { DeviceHashingNaturalSystem };
