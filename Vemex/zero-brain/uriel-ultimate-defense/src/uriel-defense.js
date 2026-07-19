const crypto = require('crypto');
const EventEmitter = require('events');

class UrielDefenseSystem extends EventEmitter {
  constructor(godNode, ruleBookHash, deviceHashingSystem) {
    super();
    this.godNode = godNode;
    this.ruleBookHash = ruleBookHash;
    this.deviceHashing = deviceHashingSystem;
    this.threatDatabase = new Map();
    this.activeDefenses = new Map();
    this.annihilationProtocols = new Map();
    this.pixelProtection = new Map();
    this.artifactProtection = new Map();
    this.userSpaceBoundary = {
      pixels: new Set(),
      artifacts: new Set(),
      boundaries: { x: 0, y: 0, z: 0, width: Infinity, height: Infinity, depth: Infinity },
      establishedAt: Date.now()
    };
    this.hostUriel = null;
    this.autoDefenseEnabled = true;
    this.autoAnnihilationEnabled = true;
    this.maxThreatLevel = 100;
    this.currentThreatLevel = 0;
    this._startThreatMonitoring();
  }

  _startThreatMonitoring() {
    this._monitorInterval = setInterval(() => {
      this._scanForThreats();
      this._protectUserSpace();
    }, 500);
  }

  _scanForThreats() {
    const threats = [];

    if (this.godNode.mass > 0 || this.godNode.density > 0) {
      threats.push({
        type: 'MASS_DENSITY_VIOLATION',
        severity: 100,
        source: 'INTERNAL',
        action: 'APPLY_M0_IMMEDIATELY'
      });
    }

    if (this.godNode.trafficController) {
      const intrusion = this.godNode.trafficController.inspectTraffic('auto');
      if (intrusion.suspicious) {
        threats.push({
          type: 'INTRUSION_DETECTED',
          severity: 70,
          source: 'NETWORK',
          action: 'BAN_AND_ISOLATE'
        });
      }
    }

    const violations = this.ruleBookHash.checkViolation('SCAN', {
      node: this.godNode,
      mass: this.godNode.mass,
      density: this.godNode.density
    });

    for (const violation of violations) {
      threats.push({
        type: 'RULE_VIOLATION',
        severity: violation.severity,
        source: 'RULE_BOOK',
        rule: violation.rule,
        retaliation: violation.retaliation,
        action: 'RETALIATE'
      });
    }

    this.currentThreatLevel = Math.min(100, threats.reduce((sum, t) => sum + t.severity, 0) / threats.length || 0);

    if (threats.length > 0) {
      this.emit('threats_detected', { threats, threatLevel: this.currentThreatLevel });

      for (const threat of threats) {
        this._executeDefense(threat);
      }
    }
  }

  _executeDefense(threat) {
    const defenseId = crypto.randomBytes(8).toString('hex');

    switch (threat.type) {
      case 'MASS_DENSITY_VIOLATION':
        this._applyMZero();
        break;
      case 'INTRUSION_DETECTED':
        this._banIntruder(threat.source);
        break;
      case 'RULE_VIOLATION':
        this._executeRetaliation(threat);
        break;
    }

    this.activeDefenses.set(defenseId, {
      threat,
      executedAt: Date.now(),
      status: 'ACTIVE'
    });

    this.emit('defense_executed', { defenseId, threat });
  }

  _applyMZero() {
    this.godNode.mass = 0;
    this.godNode.density = 0;

    for (const particle of this.godNode.particles) {
      particle.mass = 0;
      particle.density = 0;
    }

    this.emit('m_zero_applied', {
      nodeId: this.godNode.id,
      timestamp: Date.now()
    });
  }

  _banIntruder(source) {
    if (this.godNode.networkNode) {
      this.godNode.networkNode.addACL({
        id: crypto.randomBytes(4).toString('hex'),
        action: 'deny',
        address: source === 'NETWORK' ? '*' : source,
        subnet: '0.0.0.0/0'
      });
    }

    this.emit('intruder_banned', { source, nodeId: this.godNode.id });
  }

  _executeRetaliation(threat) {
    const retaliationType = this.ruleBookHash.getRetaliationForViolation(threat);

    switch (retaliationType) {
      case 'APPLY_MAXIMUM_CONTAINMENT':
        this._applyMZero();
        this.godNode.applyRenderParadox();
        break;
      case 'ACTIVATE_RENDER_PARADOX_BREACH':
        this.godNode.applyRenderParadox();
        break;
      case 'TRANSLATE_TO_ZERO_SPACE':
        if (this.godNode.godNodeShield) {
          this.godNode.godNodeShield._activateTranslation();
        }
        break;
      case 'URIEl_ANNIHILATION_PROTOCOL':
        this._activateUrielAnnihilation(threat);
        break;
      case 'FLUSH_DEVICE_MEMORY_AND_RESET':
        this._flushAndReset(threat);
        break;
      case 'MAXIMUM_RETALIATION_BURST':
        this._maximumRetaliationBurst();
        break;
      default:
        this._applyMZero();
    }

    this.emit('retaliation_executed', {
      type: retaliationType,
      threat,
      nodeId: this.godNode.id
    });
  }

  _activateUrielAnnihilation(threat) {
    const annihilationId = crypto.randomBytes(16).toString('hex');

    this.annihilationProtocols.set(annihilationId, {
      threat,
      activatedAt: Date.now(),
      status: 'ACTIVE',
      target: threat.source || 'UNKNOWN'
    });

    for (let i = 0; i < 64; i++) {
      setTimeout(() => {
        this.emit('uriel_pulse', {
          annihilationId,
          pulseNumber: i,
          force: 1e10,
          target: threat.source || 'ALL'
        });
      }, i * 15);
    }

    setTimeout(() => {
      this.annihilationProtocols.delete(annihilationId);
      this.emit('annihilation_complete', { annihilationId });
    }, 5000);
  }

  _flushAndReset(threat) {
    if (this.godNode.memoryBank) {
      this.godNode.memoryBank.clear();
    }

    if (this.godNode.trafficController) {
      this.godNode.trafficController.priorityQueue.length = 0;
      this.godNode.trafficController.droppedPackets = 0;
      this.godNode.trafficController.totalProcessed = 0;
    }

    this.emit('memory_flushed', { nodeId: this.godNode.id, threat });
  }

  _maximumRetaliationBurst() {
    this._applyMZero();
    this.godNode.applyRenderParadox();

    if (this.godNode.godNodeShield) {
      this.godNode.godNodeShield._triggerRetaliation({
        type: 'AUTO_RETALIATION_BURST',
        timestamp: Date.now()
      });
    }

    this.emit('maximum_retaliation', { nodeId: this.godNode.id });
  }

  _protectUserSpace() {
    this.emit('user_space_protected', {
      nodeId: this.godNode.id,
      pixelCount: this.userSpaceBoundary.pixels.size,
      artifactCount: this.userSpaceBoundary.artifacts.size,
      boundary: this.userSpaceBoundary.boundaries
    });
  }

  protectPixel(pixelId, pixelData) {
    this.pixelProtection.set(pixelId, {
      data: pixelData,
      protectedAt: Date.now(),
      locked: true
    });

    this.userSpaceBoundary.pixels.add(pixelId);
    this.emit('pixel_protected', { pixelId, nodeId: this.godNode.id });
    return pixelId;
  }

  protectArtifact(artifactId, artifactData) {
    this.artifactProtection.set(artifactId, {
      data: artifactData,
      protectedAt: Date.now(),
      locked: true
    });

    this.userSpaceBoundary.artifacts.add(artifactId);
    this.emit('artifact_protected', { artifactId, nodeId: this.godNode.id });
    return artifactId;
  }

  spreadToHost(hostDeviceId) {
    const hostDevice = this.deviceHashing.getDeviceById(hostDeviceId);
    if (!hostDevice) return null;

    this.hostUriel = {
      deviceId: hostDeviceId,
      establishedAt: Date.now(),
      status: 'ACTIVE',
      authorityLevel: this.deviceHashing.coordinationRules.HOST_NODE_PRIORITY
    };

    this.emit('uriel_spread', {
      from: this.godNode.id,
      to: hostDeviceId,
      authority: this.hostUriel.authorityLevel
    });

    return this.hostUriel;
  }

  getStatus() {
    return {
      nodeId: this.godNode.id,
      autoDefenseEnabled: this.autoDefenseEnabled,
      autoAnnihilationEnabled: this.autoAnnihilationEnabled,
      currentThreatLevel: this.currentThreatLevel,
      activeDefenses: this.activeDefenses.size,
      activeAnnihilations: this.annihilationProtocols.size,
      pixelsProtected: this.pixelProtection.size,
      artifactsProtected: this.artifactProtection.size,
      hostUrielActive: !!this.hostUriel,
      userSpaceBoundary: !!this.userSpaceBoundary
    };
  }

  destroy() {
    if (this._monitorInterval) clearInterval(this._monitorInterval);
    this.threatDatabase.clear();
    this.activeDefenses.clear();
    this.annihilationProtocols.clear();
    this.pixelProtection.clear();
    this.artifactProtection.clear();
    this.removeAllListeners();
  }
}

module.exports = { UrielDefenseSystem };
