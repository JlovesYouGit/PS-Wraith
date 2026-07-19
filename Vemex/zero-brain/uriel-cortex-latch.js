const fs = require('fs');
const crypto = require('crypto');
const { NodeRuntimeBypass } = require('./uriel-ultimate-defense/src/external-link');

const DEFAULT_HOME_RADIUS = 45;
const DEFAULT_EXTERNAL_RADIUS = 80;
const PATH_EQUIVALENCE_THRESHOLD = 0.35;

/**
 * Cortex–Uriel latch: gates external cortex writes through Uriel/rule-book,
 * stores capability profiles keyed by lock hash, and dispatches latched payloads
 * when cortex patterns match learned configurations.
 *
 * Coordinate permits: home (internal neural path) and external (cortex/mesh path)
 * are saved per particle; writes are allowed when path allocation matches a permit.
 */
class CortexUrielLatch {
  constructor(godNode, controlUnit, options = {}) {
    this.godNode = godNode;
    this.controlUnit = controlUnit;
    this.persistencePath = options.persistencePath || null;
    this.homeRadius = options.homeRadius ?? DEFAULT_HOME_RADIUS;
    this.externalRadius = options.externalRadius ?? DEFAULT_EXTERNAL_RADIUS;
    this.latches = new Map();
    this.patternIndex = new Map();
    this.coordinateRegistry = new Map(); // particleId -> CoordinateRecord
    this.dispatchLog = [];
    this.stats = {
      gatedWrites: 0,
      allowedWrites: 0,
      rejectedWrites: 0,
      homePermitWrites: 0,
      externalPermitWrites: 0,
      dispatches: 0,
      successfulDispatches: 0
    };
    this._load();
  }

  _load() {
    if (!this.persistencePath || !fs.existsSync(this.persistencePath)) return;
    try {
      const raw = JSON.parse(fs.readFileSync(this.persistencePath, 'utf8'));
      (raw.latches || []).forEach(([id, profile]) => this.latches.set(id, profile));
      (raw.patternIndex || []).forEach(([key, id]) => this.patternIndex.set(key, id));
      (raw.coordinateRegistry || []).forEach(([id, rec]) => this.coordinateRegistry.set(id, rec));
      if (raw.stats) this.stats = { ...this.stats, ...raw.stats };
    } catch (e) {
      console.log('[CORTEX LATCH] Persistence load skipped:', e.message);
    }
  }

  _save() {
    if (!this.persistencePath) return;
    try {
      fs.writeFileSync(this.persistencePath, JSON.stringify({
        latches: Array.from(this.latches.entries()),
        patternIndex: Array.from(this.patternIndex.entries()),
        coordinateRegistry: Array.from(this.coordinateRegistry.entries()),
        stats: this.stats,
        savedAt: Date.now()
      }, null, 2));
    } catch (e) {
      console.log('[CORTEX LATCH] Persistence save failed:', e.message);
    }
  }

  _dist(a, b) {
    if (!a || !b || a.x === undefined || b.x === undefined) return Infinity;
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  /**
   * Save home (internal) coordinate for a particle — anchor for homeCoordinatePermit.
   */
  saveHomeCoordinate(particleId, coord, metadata = {}) {
    const existing = this.coordinateRegistry.get(particleId) || this._blankCoordinateRecord(particleId);
    existing.home = {
      x: coord.x,
      y: coord.y,
      savedAt: Date.now(),
      source: metadata.source || 'internal'
    };
    existing.permits.homeCoordinatePermit = metadata.homeCoordinatePermit !== false;
    existing.pathAllocation = existing.permits.externalCoordinatePermit ? 'dual' : 'home';
    this.coordinateRegistry.set(particleId, existing);
    this._save();
    return existing;
  }

  /**
   * Save external (cortex/mesh) coordinate — anchor for externalCoordinatePermit.
   */
  saveExternalCoordinate(particleId, coord, metadata = {}) {
    const existing = this.coordinateRegistry.get(particleId) || this._blankCoordinateRecord(particleId);
    existing.external = {
      x: coord.x,
      y: coord.y,
      savedAt: Date.now(),
      source: metadata.source || 'cortex'
    };
    existing.permits.externalCoordinatePermit = metadata.externalCoordinatePermit !== false;
    existing.pathAllocation = existing.permits.homeCoordinatePermit ? 'dual' : 'external';
    this.coordinateRegistry.set(particleId, existing);
    this._save();
    return existing;
  }

  saveAllHomeCoordinates(particles) {
    particles.forEach((p) => {
      this.saveHomeCoordinate(p.id, { x: p.x, y: p.y }, { source: 'particle_init' });
    });
  }

  _blankCoordinateRecord(particleId) {
    return {
      particleId,
      home: null,
      external: null,
      permits: {
        homeCoordinatePermit: true,
        externalCoordinatePermit: false
      },
      pathAllocation: 'home',
      homeRadius: this.homeRadius,
      externalRadius: this.externalRadius
    };
  }

  /**
   * Allocate write permit via pathing: home neural path, external travel path, or dual.
   */
  allocatePermitViaPathing(particle, write, source, pathContext = {}) {
    const record = this.coordinateRegistry.get(particle.id);
    if (!record) {
      return { allowed: !particle.locked, permit: particle.locked ? 'NONE' : 'OPEN', reason: 'NO_COORDINATE_RECORD' };
    }

    const homeRadius = record.homeRadius ?? this.homeRadius;
    const externalRadius = record.externalRadius ?? this.externalRadius;
    const currentPos = { x: particle.x, y: particle.y };
    const writeExternal = write.externalCoord || write.coord || null;

    const onHomePath = this._isOnHomePath(currentPos, record, pathContext, homeRadius);
    const onExternalPath = this._isOnExternalPath(writeExternal, currentPos, record, pathContext, externalRadius);

    const homeAllowed = record.permits.homeCoordinatePermit && onHomePath;
    const externalAllowed = record.permits.externalCoordinatePermit && onExternalPath;

    if (homeAllowed && externalAllowed) {
      return { allowed: true, permit: 'DUAL', pathAllocation: 'dual', onHomePath, onExternalPath };
    }
    if (homeAllowed) {
      return { allowed: true, permit: 'HOME', pathAllocation: 'home', onHomePath, onExternalPath };
    }
    if (externalAllowed) {
      return { allowed: true, permit: 'EXTERNAL', pathAllocation: 'external', onHomePath, onExternalPath };
    }

    if (!particle.locked) {
      return { allowed: true, permit: 'OPEN', pathAllocation: record.pathAllocation, onHomePath, onExternalPath };
    }

    return {
      allowed: false,
      permit: 'NONE',
      reason: 'COORDINATE_PERMIT_DENIED',
      onHomePath,
      onExternalPath,
      source
    };
  }

  _isOnHomePath(currentPos, record, pathContext, radius) {
    if (!record.home) return false;

    if (this._dist(currentPos, record.home) <= radius) return true;

    const neuralPath = pathContext.neuralPath;
    if (neuralPath?.pathNodes?.length) {
      const nearPathNode = neuralPath.pathNodes.some((node) => this._dist(currentPos, node) <= radius * 0.75);
      if (nearPathNode) return true;
    }

    const travelPath = pathContext.travelPath;
    if (travelPath?.pathHistory?.length >= 3) {
      const recent = travelPath.pathHistory.slice(-5);
      const nearInternal = recent.some((h) => this._dist(h.internalPos, record.home) <= radius);
      if (nearInternal && travelPath.divergence < PATH_EQUIVALENCE_THRESHOLD * 2) return true;
    }

    return false;
  }

  _isOnExternalPath(writeExternal, currentPos, record, pathContext, radius) {
    const extAnchor = writeExternal || record.external;
    if (!extAnchor) return false;

    if (writeExternal && record.external && this._dist(writeExternal, record.external) <= radius) return true;
    if (writeExternal && this._dist(writeExternal, currentPos) <= radius * 1.25) return true;

    const travelPath = pathContext.travelPath;
    if (travelPath) {
      if (travelPath.equivalent) return true;
      if (travelPath.divergence < PATH_EQUIVALENCE_THRESHOLD) return true;
      if (travelPath.pathHistory?.length >= 3) {
        const recent = travelPath.pathHistory.slice(-5);
        const aligned = recent.some((h) => this._dist(h.externalPos, extAnchor) <= radius);
        if (aligned) return true;
      }
    }

    const externalMesh = pathContext.externalNode;
    if (externalMesh && this._dist({ x: externalMesh.x, y: externalMesh.y }, extAnchor) <= radius) return true;

    return false;
  }

  _fingerprintPatterns(neuralPatterns) {
    if (!neuralPatterns || neuralPatterns.length === 0) return 'empty';
    const summary = neuralPatterns.slice(0, 10).map(p => ({
      f: Math.round((p.frequency || 0) * 10) / 10,
      a: Math.round((p.amplitude || 0) * 100) / 100
    }));
    return crypto.createHash('sha256').update(JSON.stringify(summary)).digest('hex').substring(0, 16);
  }

  _validateWrite(particle, write, source, pathContext = {}) {
    const proposedHz = write.hz;
    const proposedDensity = write.density;

    if (proposedHz < 0 || proposedHz > 10000 || proposedDensity < 0 || proposedDensity > 1.0) {
      return { allowed: false, reason: 'OUT_OF_BOUNDS' };
    }

    const adversaryViolations = this.godNode.ruleBookHash.checkViolation('CORTEX_WRITE', {
      type: source === 'adversary' ? 'ADVERSARY' : 'INGEST',
      constraint_attempted: source === 'adversary'
    });
    if (adversaryViolations.length > 0) {
      return { allowed: false, reason: 'RULE_VIOLATION', violations: adversaryViolations };
    }

    const pathPermit = this.allocatePermitViaPathing(particle, write, source, pathContext);
    if (!pathPermit.allowed) {
      return { allowed: false, ...pathPermit };
    }

    if (this.godNode.urielDefense.currentThreatLevel > 80 && pathPermit.permit === 'EXTERNAL') {
      return { allowed: false, reason: 'THREAT_LEVEL_HIGH', threatLevel: this.godNode.urielDefense.currentThreatLevel };
    }

    return { allowed: true, ...pathPermit };
  }

  _findLatchForParticle(particleId) {
    for (const profile of this.latches.values()) {
      if (profile.particleId === particleId) return profile;
    }
    return null;
  }

  gateWrites(source, writes, particlesById, pathContextResolver = null) {
    const results = { allowed: [], rejected: [] };

    for (const write of writes) {
      const particle = particlesById.get(write.particleId);
      if (!particle) {
        results.rejected.push({ ...write, reason: 'PARTICLE_NOT_FOUND' });
        this.stats.rejectedWrites++;
        continue;
      }

      const pathContext = pathContextResolver
        ? pathContextResolver(write.particleId, write, particle)
        : {};

      const check = this._validateWrite(particle, write, source, pathContext);
      if (check.allowed) {
        results.allowed.push({ ...write, permit: check.permit, pathAllocation: check.pathAllocation });
        this.stats.allowedWrites++;
        if (check.permit === 'HOME' || check.permit === 'DUAL') this.stats.homePermitWrites++;
        if (check.permit === 'EXTERNAL' || check.permit === 'DUAL') this.stats.externalPermitWrites++;
      } else {
        results.rejected.push({ ...write, ...check });
        this.stats.rejectedWrites++;
        this.stats.gatedWrites++;
      }
    }

    return results;
  }

  applyGatedWrites(writes, particles, source = 'cortex_sync', options = {}) {
    const byId = new Map(particles.map(p => [p.id, p]));
    const gated = this.gateWrites(source, writes, byId, options.getPathContext || null);
    for (const write of gated.allowed) {
      const p = byId.get(write.particleId);
      if (!p) continue;
      if (write.hz !== undefined) p.hz = write.hz;
      if (write.density !== undefined) p.density = write.density;
    }
    return gated;
  }

  latchConfiguration(trigger, metadata = {}) {
    const lockHash = this.godNode.lockState();
    const lockState = this.controlUnit.exportLockStateForExternalLink(this.godNode.id);
    let transpassPayload = null;
    try {
      transpassPayload = NodeRuntimeBypass.generateTranspassPayload(lockHash, this.godNode.id);
    } catch (e) {
      transpassPayload = { error: e.message };
    }

    const patternKey = metadata.patternKey || this._fingerprintPatterns(metadata.neuralPatterns);
    const latchId = crypto.createHash('sha256')
      .update(`${lockHash}:${trigger}:${patternKey}`)
      .digest('hex')
      .substring(0, 24);

    if (metadata.particleId && metadata.particle) {
      this.saveHomeCoordinate(metadata.particleId, { x: metadata.particle.x, y: metadata.particle.y }, {
        homeCoordinatePermit: true,
        source: trigger
      });
      if (metadata.externalCoord) {
        this.saveExternalCoordinate(metadata.particleId, metadata.externalCoord, {
          externalCoordinatePermit: metadata.allowExternalWrites === true,
          source: metadata.externalSource || 'latch'
        });
      } else if (metadata.allowExternalWrites) {
        const rec = this.coordinateRegistry.get(metadata.particleId);
        if (rec) {
          rec.permits.externalCoordinatePermit = true;
          rec.pathAllocation = 'dual';
        }
      }
    }

    const profile = {
      latchId,
      lockHash,
      trigger,
      patternKey,
      particleId: metadata.particleId || null,
      allowExternalWrites: metadata.allowExternalWrites === true,
      coordinatePermits: metadata.particleId
        ? this.coordinateRegistry.get(metadata.particleId)?.permits
        : null,
      createdAt: Date.now(),
      lastUsed: null,
      invocationCount: 0,
      successScore: 0.5,
      capabilities: {
        transpassPayload,
        lockState: {
          lock_hash: lockState.lock_hash,
          breach_active: lockState.breach_active,
          external_link_ready: lockState.external_link_ready
        },
        spectrum: {
          variableW: this.godNode.spectrumFieldLock.getVariableW(),
          lockedFields: this.godNode.spectrumFieldLock.getLockedFields().length
        },
        renderParadox: {
          breach_active: this.godNode.breach_active,
          self_linked: this.godNode.self_linked,
          state: this.godNode.state
        },
        uriel: this.godNode.urielDefense.getStatus()
      },
      scripts: {
        sync_cortex: 'sync_external_cortex',
        recalibrate: 'self_recalibrate',
        spectrum_lock: 'spectrum_field_lock'
      }
    };

    this.latches.set(latchId, profile);
    this.patternIndex.set(patternKey, latchId);
    this._save();
    return profile;
  }

  matchLatch(cortexData) {
    const patternKey = this._fingerprintPatterns(cortexData.neuralPatterns);
    const directId = this.patternIndex.get(patternKey);
    if (directId && this.latches.has(directId)) {
      return this.latches.get(directId);
    }

    let best = null;
    let bestScore = -1;

    this.latches.forEach((profile) => {
      const score = this._patternSimilarity(cortexData, profile);
      const weighted = score * (0.5 + profile.successScore);
      if (weighted > bestScore && weighted > 0.35) {
        bestScore = weighted;
        best = profile;
      }
    });

    return best;
  }

  _patternSimilarity(cortexData, profile) {
    if (!cortexData.neuralPatterns || cortexData.neuralPatterns.length === 0) return 0;
    const avgFreq = cortexData.neuralPatterns.reduce((s, p) => s + p.frequency, 0) / cortexData.neuralPatterns.length;
    const avgAmp = cortexData.neuralPatterns.reduce((s, p) => s + p.amplitude, 0) / cortexData.neuralPatterns.length;
    const capFreq = (profile.capabilities.transpassPayload?.derived_hz || 440) / 10;
    const freqDiff = Math.abs(avgFreq - capFreq) / 100;
    const ampDiff = Math.abs(avgAmp - 0.5);
    return Math.max(0, 1 - (freqDiff + ampDiff) / 2);
  }

  dispatchLatch(latchId, handlers = {}) {
    const profile = this.latches.get(latchId);
    if (!profile) {
      return { success: false, error: 'LATCH_NOT_FOUND' };
    }

    profile.invocationCount++;
    profile.lastUsed = Date.now();
    const results = { latchId, scriptsRun: [], errors: [] };

    try {
      if (handlers.recalibrate) {
        const recal = handlers.recalibrate();
        results.scriptsRun.push({ script: 'recalibrate', result: recal });
      }
      if (handlers.applySpectrumLock && profile.particleId) {
        handlers.applySpectrumLock(profile.particleId, profile.capabilities.spectrum);
        results.scriptsRun.push({ script: 'spectrum_lock', particleId: profile.particleId });
      }
      results.transpassPayload = profile.capabilities.transpassPayload;
      results.lockState = profile.capabilities.lockState;

      this.stats.dispatches++;
      this.recordOutcome(latchId, true);
      this._save();

      this.dispatchLog.push({ latchId, at: Date.now(), success: true });
      if (this.dispatchLog.length > 200) this.dispatchLog.shift();

      return { success: true, ...results };
    } catch (e) {
      results.errors.push(e.message);
      this.recordOutcome(latchId, false);
      return { success: false, ...results };
    }
  }

  tryAutoDispatch(cortexData, handlers = {}) {
    const match = this.matchLatch(cortexData);
    if (!match) return { dispatched: false, reason: 'NO_MATCH' };
    const result = this.dispatchLatch(match.latchId, handlers);
    return { dispatched: result.success, latchId: match.latchId, result };
  }

  recordOutcome(latchId, success) {
    const profile = this.latches.get(latchId);
    if (!profile) return;
    const delta = success ? 0.08 : -0.05;
    profile.successScore = Math.max(0, Math.min(1, profile.successScore + delta));
    if (success) this.stats.successfulDispatches++;
    this._save();
  }

  getCoordinateStatus(particleId = null) {
    if (particleId) {
      return this.coordinateRegistry.get(particleId) || null;
    }
    return Array.from(this.coordinateRegistry.values());
  }

  persist() {
    this._save();
  }

  getStatus() {
    return {
      latchCount: this.latches.size,
      patternIndexSize: this.patternIndex.size,
      coordinateCount: this.coordinateRegistry.size,
      stats: { ...this.stats },
      recentDispatches: this.dispatchLog.slice(-5),
      coordinates: Array.from(this.coordinateRegistry.values()).slice(0, 10).map(c => ({
        particleId: c.particleId,
        pathAllocation: c.pathAllocation,
        permits: c.permits,
        home: c.home ? { x: Math.round(c.home.x), y: Math.round(c.home.y) } : null,
        external: c.external ? { x: Math.round(c.external.x), y: Math.round(c.external.y) } : null
      })),
      latches: Array.from(this.latches.values()).map(p => ({
        latchId: p.latchId,
        trigger: p.trigger,
        patternKey: p.patternKey,
        particleId: p.particleId,
        coordinatePermits: p.coordinatePermits,
        successScore: p.successScore,
        invocationCount: p.invocationCount,
        lastUsed: p.lastUsed,
        lockHash: p.lockHash.substring(0, 16) + '...'
      }))
    };
  }
}

module.exports = { CortexUrielLatch };
