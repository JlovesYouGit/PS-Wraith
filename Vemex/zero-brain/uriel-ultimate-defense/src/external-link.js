const EventEmitter = require('events');
const os = require('os');
const crypto = require('crypto');

class SpectrumHzActuator extends EventEmitter {
  constructor(options = {}) {
    super();
    this.baseFrequency = options.baseFrequency || 440.0;
    this.volatility = options.volatility || 0.5;
    this.sampleRate = options.sampleRate || 44100;
    this.bufferSize = options.bufferSize || 1024;
    this.channels = options.channels || 2;
    this.lockedNodeId = options.lockedNodeId || null;
    this.lockStateHash = options.lockStateHash || null;
    this.actuationActive = false;
    this.spectrumData = new Float32Array(this.bufferSize);
    this.phase = 0;
    this.frequencyHistory = [];
    this.maxHistoryLength = options.maxHistoryLength || 1000;
  }

  applyLockState(lockStateHash, nodeId) {
    this.lockStateHash = lockStateHash;
    this.lockedNodeId = nodeId;
    this.emit('lock_applied', { lockStateHash, nodeId });
    return {
      locked: true,
      lock_hash: lockStateHash,
      node_id: nodeId,
      timestamp: Date.now()
    };
  }

  computeSpectrumFromLock() {
    if (!this.lockStateHash) {
      throw new Error('No lock state applied. Call applyLockState first.');
    }

    const hashBuffer = Buffer.from(this.lockStateHash, 'hex');
    const hashInt = hashBuffer.readUInt32BE(0);
    const derivedFrequency = this.baseFrequency + (hashInt % 1000) / 1000.0 * 200.0;
    const derivedVolatility = (hashInt % 100) / 100.0 * this.volatility;

    for (let i = 0; i < this.bufferSize; i++) {
      const t = i / this.sampleRate;
      const modulatedHz = derivedFrequency + Math.sin(t * derivedVolatility * 10) * derivedVolatility * 50;
      this.spectrumData[i] = Math.sin(2 * Math.PI * modulatedHz * t) * 0.8;
    }

    this.frequencyHistory.push({
      frequency: derivedFrequency,
      volatility: derivedVolatility,
      timestamp: Date.now(),
      lock_hash: this.lockStateHash
    });

    if (this.frequencyHistory.length > this.maxHistoryLength) {
      this.frequencyHistory.shift();
    }

    return {
      frequencies: Array.from(this.spectrumData),
      derived_hz: derivedFrequency,
      volatility: derivedVolatility,
      lock_hash: this.lockStateHash,
      sample_rate: this.sampleRate,
      buffer_size: this.bufferSize
    };
  }

  generateAudioBuffer() {
    const spectrum = this.computeSpectrumFromLock();
    const audioContext = {
      sampleRate: this.sampleRate,
      channels: this.channels,
      duration: this.bufferSize / this.sampleRate,
      data: spectrum.frequencies,
      format: 'float32',
      encoding: 'pcm',
      lock_hash: spectrum.lock_hash,
      derived_hz: spectrum.derived_hz
    };
    this.emit('audio_buffer_generated', audioContext);
    return audioContext;
  }

  getActuationCommand() {
    const spectrum = this.computeSpectrumFromLock();
    return {
      command: 'SPECTRUM_HZ_ACTUATION',
      lock_hash: this.lockStateHash,
      node_id: this.lockedNodeId,
      frequencies: spectrum.frequencies,
      derived_hz: spectrum.derived_hz,
      volatility: spectrum.volatility,
      sample_rate: this.sampleRate,
      channels: this.channels,
      buffer_size: this.bufferSize,
      timestamp: Date.now(),
      environment: {
        platform: os.platform(),
        arch: os.arch(),
        hostname: os.hostname(),
        cpus: os.cpus().length,
        total_memory: os.totalmem()
      },
      constraint_status: 'TRANSPASSED',
      simulation_lock: 'ACTIVE',
      external_link: 'ENABLED'
    };
  }

  getFrequencyHistory() {
    return {
      history_length: this.frequencyHistory.length,
      locked_node: this.lockedNodeId,
      lock_hash: this.lockStateHash,
      entries: this.frequencyHistory.slice(-100)
    };
  }

  stopActuation() {
    this.actuationActive = false;
    this.spectrumData.fill(0);
    this.emit('actuation_stopped');
    return { status: 'stopped', lock_hash: this.lockStateHash };
  }
}

class ExternalComputeLink extends EventEmitter {
  constructor(options = {}) {
    super();
    this.actuator = new SpectrumHzActuator(options);
    this.externalEndpoints = [];
    this.computeModules = new Map();
    this.linkEstablished = false;
    this.transpassCount = 0;
  }

  establishLink(lockStateHash, nodeId) {
    const lockResult = this.actuator.applyLockState(lockStateHash, nodeId);
    this.linkEstablished = true;
    this.emit('link_established', lockResult);
    return lockResult;
  }

  registerComputeModule(name, module) {
    this.computeModules.set(name, module);
    this.emit('module_registered', { name, module });
    return { registered: true, name };
  }

  transpassToExternal(command) {
    if (!this.linkEstablished) {
      throw new Error('Link not established. Call establishLink first.');
    }

    this.transpassCount++;
    const actuation = this.actuator.getActuationCommand();
    const transpassId = crypto.randomBytes(16).toString('hex');

    const result = {
      transpass_id: transpassId,
      transpass_count: this.transpassCount,
      command: command,
      lock_hash: this.actuator.lockStateHash,
      node_id: this.actuator.lockedNodeId,
      actuation: actuation,
      compute_modules: Array.from(this.computeModules.keys()),
      external_endpoints: this.externalEndpoints,
      status: 'TRANSPASSED',
      timestamp: Date.now()
    };

    this.emit('transpass', result);
    return result;
  }

  addExternalEndpoint(endpoint) {
    this.externalEndpoints.push(endpoint);
    this.emit('endpoint_added', endpoint);
    return { added: true, endpoint };
  }

  getLinkStatus() {
    return {
      link_established: this.linkEstablished,
      locked_node: this.actuator.lockedNodeId,
      lock_hash: this.actuator.lockStateHash,
      transpass_count: this.transpassCount,
      compute_modules: Array.from(this.computeModules.keys()),
      external_endpoints: this.externalEndpoints,
      frequency_history: this.actuator.getFrequencyHistory()
    };
  }
}

class NodeRuntimeBypass {
  static createExternalLink(options) {
    return new ExternalComputeLink(options);
  }

  static bridgeSimulationToHardware(simulationLockHash, nodeId, hardwareInterface) {
    const link = new ExternalComputeLink();
    link.establishLink(simulationLockHash, nodeId);
    link.addExternalEndpoint({
      type: 'hardware_interface',
      interface: hardwareInterface,
      protocol: 'spectrum_hz',
      mode: 'bidirectional'
    });
    link.registerComputeModule('hardware_bypass', {
      type: 'actuation',
      interface: hardwareInterface,
      permission: 'full'
    });
    return link;
  }

  static generateTranspassPayload(simulationLockHash, nodeId) {
    const actuator = new SpectrumHzActuator();
    actuator.applyLockState(simulationLockHash, nodeId);
    return actuator.getActuationCommand();
  }
}

module.exports = {
  SpectrumHzActuator,
  ExternalComputeLink,
  NodeRuntimeBypass
};
