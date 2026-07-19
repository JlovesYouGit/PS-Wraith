const EventEmitter = require('events');
const crypto = require('crypto');

class SpectrumFieldDetector extends EventEmitter {
  constructor(options = {}) {
    super();
    this.nodeId = options.nodeId || 'default';
    this.detectionRanges = options.detectionRanges || [
      { name: 'LOW', minMs: 0.5, maxMs: 120, minHz: 100, maxHz: Infinity, weight: 1.0 },
      { name: 'HIGH_PRECISION', minMs: 0.5, maxMs: 10, minHz: 100, maxHz: 2000, weight: 2.0 },
      { name: 'STANDARD', minMs: 10, maxMs: 120, minHz: 100, maxHz: 500, weight: 1.0 }
    ];
    this.variableW = 0;
    this.signalHistory = [];
    this.maxHistory = options.maxHistory || 50000;
    this.detectionInterval = options.detectionInterval || 10;
    this._monitoring = false;
    this._lastDetection = Date.now();
  }

  startMonitoring() {
    if (this._monitoring) return;
    this._monitoring = true;
    this._detectLoop();
    this.emit('monitoring_started', { nodeId: this.nodeId });
  }

  stopMonitoring() {
    this._monitoring = false;
    if (this._interval) clearInterval(this._interval);
  }

  _detectLoop() {
    this._interval = setInterval(() => {
      this._detectSignals();
      this._updateVariableW();
      this._enforceRanges();
    }, this.detectionInterval);
  }

  _detectSignals() {
    const now = Date.now();
    const elapsed = now - this._lastDetection;
    this._lastDetection = now;

    const rawSignal = {
      timestamp: now,
      elapsedMs: elapsed,
      hz: 100 + Math.random() * 1900,
      amplitude: Math.random(),
      phase: Math.random() * Math.PI * 2,
      weight: Math.random() * 2,
      density: Math.random() * 0.5
    };

    const matchedRanges = [];
    for (const range of this.detectionRanges) {
      if (rawSignal.elapsedMs >= range.minMs && rawSignal.elapsedMs <= range.maxMs &&
          rawSignal.hz >= range.minHz && rawSignal.hz <= range.maxHz) {
        matchedRanges.push(range);
      }
    }

    const detection = {
      ...rawSignal,
      matchedRanges,
      variableW: this.variableW,
      locked: matchedRanges.length > 0
    };

    this.signalHistory.push(detection);
    if (this.signalHistory.length > this.maxHistory) this.signalHistory.shift();

    this.emit('signal_detected', detection);
    return detection;
  }

  _updateVariableW() {
    if (this.signalHistory.length < 10) return;

    const recent = this.signalHistory.slice(-100);
    const avgHz = recent.reduce((s, r) => s + r.hz, 0) / recent.length;
    const avgWeight = recent.reduce((s, r) => s + r.weight, 0) / recent.length;
    const avgDensity = recent.reduce((s, r) => s + r.density, 0) / recent.length;

    const targetW = avgHz * avgWeight * avgDensity;
    this.variableW += (targetW - this.variableW) * 0.1;
  }

  _enforceRanges() {
    for (const range of this.detectionRanges) {
      this.emit('range_enforced', {
        nodeId: this.nodeId,
        range: range.name,
        minMs: range.minMs,
        maxMs: range.maxMs,
        minHz: range.minHz,
        maxHz: range.maxHz,
        variableW: this.variableW
      });
    }
  }

  getVariableW() {
    return this.variableW;
  }

  getRecentSignals(count = 100) {
    return this.signalHistory.slice(-count);
  }

  getStats() {
    const lockedCount = this.signalHistory.filter(s => s.locked).length;
    return {
      nodeId: this.nodeId,
      monitoring: this._monitoring,
      variableW: this.variableW,
      totalDetections: this.signalHistory.length,
      lockedDetections: lockedCount,
      detectionRate: this._monitoring ? (1000 / this.detectionInterval) : 0,
      ranges: this.detectionRanges.map(r => r.name)
    };
  }

  destroy() {
    this.stopMonitoring();
    this.signalHistory.length = 0;
    this.removeAllListeners();
  }
}

class ExternalFieldBandwidthController extends EventEmitter {
  constructor(options = {}) {
    super();
    this.nodeId = options.nodeId || 'default';
    this.bandwidthHz = options.bandwidthHz || 10000;
    this.currentUsage = 0;
    this.lockedSignals = new Map();
    this.fieldMappings = new Map();
    this.adjustmentSensitivity = options.adjustmentSensitivity || 0.1;
    this.autoAdjustEnabled = options.autoAdjustEnabled !== false;
    this._lastAdjustment = Date.now();
  }

  registerSignal(signalId, signalData) {
    const bandWidth = signalData.hz ? signalData.hz / 1000 : 0.1;
    this.currentUsage += bandWidth;

    if (this.currentUsage > this.bandwidthHz) {
      this._throttle();
    }

    this.fieldMappings.set(signalId, {
      signalData,
      registeredAt: Date.now(),
      locked: false,
      weight: signalData.weight || 1.0,
      density: signalData.density || 1.0,
      fieldAdjustment: 0
    });

    this.emit('signal_registered', { signalId, nodeId: this.nodeId, bandwidth: bandWidth });
    return signalId;
  }

  lockSignal(signalId, lockData = {}) {
    const entry = this.fieldMappings.get(signalId);
    if (!entry) return null;

    entry.locked = true;
    entry.lockedAt = Date.now();
    entry.lockData = {
      weight: lockData.weight || entry.weight,
      density: lockData.density || entry.density,
      fieldConstant: lockData.fieldConstant || 1.0,
      mZero: lockData.mZero !== false,
      velocityNotConstant: lockData.velocityNotConstant !== false,
      spatialLock: lockData.spatialLock || true,
      lockedBy: this.nodeId
    };

    this.lockedSignals.set(signalId, entry);
    this.emit('signal_locked', { signalId, nodeId: this.nodeId, lockData: entry.lockData });
    return entry;
  }

  releaseSignal(signalId) {
    const entry = this.fieldMappings.get(signalId);
    if (!entry) return false;
    entry.locked = false;
    this.lockedSignals.delete(signalId);
    this.emit('signal_released', { signalId, nodeId: this.nodeId });
    return true;
  }

  _throttle() {
    if (!this.autoAdjustEnabled) return;

    const now = Date.now();
    const elapsed = now - this._lastAdjustment;
    if (elapsed < 100) return;

    const overflow = this.currentUsage - this.bandwidthHz;
    const adjustment = overflow * this.adjustmentSensitivity;

    for (const [id, entry] of this.fieldMappings) {
      if (!entry.locked) {
        entry.fieldAdjustment -= adjustment;
        entry.density = Math.max(0.01, entry.density - adjustment * 0.01);
      }
    }

    this.emit('bandwidth_throttled', {
      nodeId: this.nodeId,
      overflow,
      adjustment,
      timestamp: now
    });

    this._lastAdjustment = now;
  }

  applyAutomaticAdjustment(signalId) {
    const entry = this.fieldMappings.get(signalId);
    if (!entry) return null;

    entry.fieldAdjustment += (1.0 - entry.fieldAdjustment) * this.adjustmentSensitivity;
    entry.density = Math.min(1.0, entry.density + this.adjustmentSensitivity);
    entry.weight = Math.min(2.0, entry.weight + this.adjustmentSensitivity * 0.5);

    if (!entry.locked) {
      this.lockSignal(signalId, {
        weight: entry.weight,
        density: entry.density,
        fieldConstant: 1.0 + entry.fieldAdjustment,
        mZero: true,
        velocityNotConstant: true,
        spatialLock: true
      });
    }

    this.emit('auto_adjustment_applied', {
      signalId,
      nodeId: this.nodeId,
      fieldAdjustment: entry.fieldAdjustment,
      density: entry.density,
      weight: entry.weight
    });

    return entry;
  }

  getLockedSignal(signalId) {
    return this.lockedSignals.get(signalId) || null;
  }

  getAllLockedSignals() {
    return Array.from(this.lockedSignals.values());
  }

  getStats() {
    return {
      nodeId: this.nodeId,
      bandwidthHz: this.bandwidthHz,
      currentUsage: this.currentUsage,
      utilizationPercent: (this.currentUsage / this.bandwidthHz * 100).toFixed(2),
      lockedSignals: this.lockedSignals.size,
      totalMappedSignals: this.fieldMappings.size,
      autoAdjustEnabled: this.autoAdjustEnabled,
      adjustmentSensitivity: this.adjustmentSensitivity
    };
  }

  destroy() {
    this.lockedSignals.clear();
    this.fieldMappings.clear();
    this.removeAllListeners();
  }
}

class SpectrumFieldLockEngine extends EventEmitter {
  constructor(options = {}) {
    super();
    this.nodeId = options.nodeId || 'default';
    this.detector = new SpectrumFieldDetector({ nodeId: this.nodeId, ...options });
    this.bandwidthController = new ExternalFieldBandwidthController({ nodeId: this.nodeId, ...options });
    this.lockedFields = new Map();
    this.fieldLockHistory = [];

    this.detector.on('signal_detected', (signal) => {
      if (signal.locked) {
        this.bandwidthController.registerSignal(signal.signalId || `${this.nodeId}_${signal.timestamp}`, signal);
      }
    });

    this.bandwidthController.on('signal_locked', (data) => {
      this.lockedFields.set(data.signalId, {
        lockedAt: Date.now(),
        nodeId: this.nodeId,
        lockData: data.lockData
      });
      this.fieldLockHistory.push({
        action: 'LOCK',
        signalId: data.signalId,
        timestamp: Date.now()
      });
      if (this.fieldLockHistory.length > 10000) this.fieldLockHistory.shift();
    });
  }

  start() {
    this.detector.startMonitoring();
    this.emit('started', { nodeId: this.nodeId });
  }

  stop() {
    this.detector.stopMonitoring();
  }

  lockField(signalId, lockData = {}) {
    return this.bandwidthController.lockSignal(signalId, lockData);
  }

  releaseField(signalId) {
    const released = this.bandwidthController.releaseSignal(signalId);
    if (released) {
      this.lockedFields.delete(signalId);
    }
    return released;
  }

  getVariableW() {
    return this.detector.getVariableW();
  }

  getLockedFields() {
    return Array.from(this.lockedFields.values());
  }

  getStats() {
    return {
      nodeId: this.nodeId,
      detector: this.detector.getStats(),
      bandwidth: this.bandwidthController.getStats(),
      lockedFields: this.lockedFields.size,
      variableW: this.detector.getVariableW()
    };
  }

  destroy() {
    this.detector.destroy();
    this.bandwidthController.destroy();
    this.lockedFields.clear();
    this.fieldLockHistory.length = 0;
    this.removeAllListeners();
  }
}

module.exports = { SpectrumFieldDetector, ExternalFieldBandwidthController, SpectrumFieldLockEngine };
