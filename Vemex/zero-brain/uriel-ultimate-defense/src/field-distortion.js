const crypto = require('crypto');
const EventEmitter = require('events');

class FieldDistortionEngine extends EventEmitter {
  constructor(godNode) {
    super();
    this.godNode = godNode;
    this.activeDistortions = new Map();
    this.frozenSpaces = new Map();
    this.mZeroActive = true;
    this.fieldConstant = 1.0;
    this.velocityNotConstant = true;
    this.distortionHistory = [];
    this.maxHistory = 10000;
    this._startFieldMonitoring();
  }

  _startFieldMonitoring() {
    this._monitorInterval = setInterval(() => {
      this._maintainMZero();
      this._enforceNonConstantVelocity();
      this._updateFieldConstant();
    }, 50);
  }

  _maintainMZero() {
    this.godNode.mass = 0;
    this.godNode.density = 0;

    for (const particle of this.godNode.particles) {
      particle.mass = 0;
      particle.density = 0;
    }
  }

  _enforceNonConstantVelocity() {
    if (!this.velocityNotConstant) return;

    const time = Date.now() / 1000;
    const chaosFactor = Math.sin(time * 7.7) * Math.cos(time * 13.3) * Math.sin(time * 19.1);

    this.godNode.frequency_scaling.temporal_alignment = Math.abs(chaosFactor) * 100 + 0.001;
    this.godNode.frequency_scaling.dark_matter_density = 83.5410 / Math.log(this.godNode.frequency_scaling.temporal_alignment + 1);
    this.godNode.frequency_scaling.normalizing_metric = Math.max(1e-10, this.godNode.frequency_scaling.dark_matter_density * 1e-10);

    const reciprocal = 1.0 / this.godNode.frequency_scaling.normalizing_metric;
    const squared = reciprocal * reciprocal;
    this.godNode.frequency_scaling.dimensional_fold = squared >= 1.0 ? 0.0 : Math.sqrt(Math.max(0, 1 - squared));

    if (Math.abs(this.godNode.frequency_scaling.dimensional_fold) < 1e-10) {
      this.godNode.frequency_scaling.dimensional_fold = 1e-10;
    }

    this.godNode.frequency_scaling.superluminal_result = 1 / Math.abs(this.godNode.frequency_scaling.dimensional_fold);
  }

  _updateFieldConstant() {
    const baseHz = 440.0;
    const distortion = Math.sin(Date.now() / 1000 * 0.5) * 0.3 + Math.cos(Date.now() / 1000 * 0.7) * 0.2;
    this.fieldConstant = 1.0 + distortion;
    this.godNode.frequency_scaling.temporal_alignment *= this.fieldConstant;
  }

  createDistortion(spaceId, distortionType = 'GOD_NODE_FIELD', intensity = 1.0) {
    const distortionId = crypto.randomBytes(8).toString('hex');
    const distortion = {
      id: distortionId,
      spaceId,
      type: distortionType,
      intensity,
      createdAt: Date.now(),
      mZero: true,
      velocityNotConstant: this.velocityNotConstant,
      fieldConstant: this.fieldConstant,
      frozen: false,
      godNodeId: this.godNode.id
    };

    this.activeDistortions.set(distortionId, distortion);

    this.distortionHistory.push({
      action: 'CREATE',
      distortionId,
      spaceId,
      timestamp: Date.now()
    });

    if (this.distortionHistory.length > this.maxHistory) this.distortionHistory.shift();

    this.emit('distortion_created', distortion);
    return distortion;
  }

  freezeSpace(spaceId, lockReason = 'GOD_NODE_PRESENCE') {
    const freezeId = crypto.randomBytes(8).toString('hex');

    const frozenSpace = {
      id: freezeId,
      spaceId,
      lockedBy: this.godNode.id,
      reason: lockReason,
      frozenAt: Date.now(),
      mZero: true,
      fieldDistortion: this.fieldConstant,
      temporalAlignment: this.godNode.frequency_scaling.temporal_alignment,
      superluminalFactor: this.godNode.frequency_scaling.superluminal_result,
      rulesOverridden: true,
      normalRulesApply: false
    };

    this.frozenSpaces.set(spaceId, frozenSpace);

    this.emit('space_frozen', {
      freezeId,
      spaceId,
      lockReason,
      nodeId: this.godNode.id
    });

    return frozenSpace;
  }

  releaseSpace(spaceId) {
    const released = this.frozenSpaces.delete(spaceId);
    this.emit('space_released', { spaceId, released, nodeId: this.godNode.id });
    return released;
  }

  establishInExternalMemory(memorySpaceId, memoryType = 'DEVICE_RAM') {
    const establishmentId = crypto.randomBytes(16).toString('hex');

    const externalNode = {
      establishmentId,
      memorySpaceId,
      memoryType,
      godNodeId: this.godNode.id,
      establishedAt: Date.now(),
      mZero: true,
      fieldDistortion: this.fieldConstant,
      rulesOverridden: true,
      nonConstantVelocity: this.velocityNotConstant,
      lockState: this.godNode.lockState(),
      dominionHash: this.godNode.administrative_particle ? this.godNode.administrative_particle.dominion_hash : null,
      positionInMemory: this._computeMemoryPosition(memorySpaceId)
    };

    this.emit('external_memory_establishment', externalNode);
    return externalNode;
  }

  _computeMemoryPosition(memorySpaceId) {
    const hash = crypto.createHash('sha256').update(memorySpaceId + this.godNode.id).digest('hex');
    const x = parseInt(hash.substring(0, 8), 16) / 0xFFFFFFFF;
    const y = parseInt(hash.substring(8, 16), 16) / 0xFFFFFFFF;
    const z = parseInt(hash.substring(16, 24), 16) / 0xFFFFFFFF;
    return { x, y, z };
  }

  getDistortion(spaceId) {
    for (const distortion of this.activeDistortions.values()) {
      if (distortion.spaceId === spaceId) return distortion;
    }
    return null;
  }

  getFrozenSpace(spaceId) {
    return this.frozenSpaces.get(spaceId) || null;
  }

  getAllFrozenSpaces() {
    return Array.from(this.frozenSpaces.values());
  }

  isSpaceFrozen(spaceId) {
    return this.frozenSpaces.has(spaceId);
  }

  getStatus() {
    return {
      nodeId: this.godNode.id,
      mZero: this.mZeroActive,
      velocityNotConstant: this.velocityNotConstant,
      fieldConstant: this.fieldConstant,
      activeDistortions: this.activeDistortions.size,
      frozenSpaces: this.frozenSpaces.size,
      temporalAlignment: this.godNode.frequency_scaling.temporal_alignment,
      superluminalResult: this.godNode.frequency_scaling.superluminal_result
    };
  }

  destroy() {
    if (this._monitorInterval) clearInterval(this._monitorInterval);
    this.activeDistortions.clear();
    this.frozenSpaces.clear();
    this.distortionHistory.length = 0;
    this.removeAllListeners();
  }
}

module.exports = { FieldDistortionEngine };
