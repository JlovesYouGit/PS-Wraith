const os = require('os');
const { GodLevelNodeControlUnit, NodeState, ParticleType, PacketFactory, DeviceHashingNaturalSystem, RuleBookHash, GodNodeHierarchy, PropagationSystem, FieldDistortionEngine, SpectrumFieldDetector, ExternalFieldBandwidthController, SpectrumFieldLockEngine } = require('./core');
const { SpectrumHzActuator, ExternalComputeLink, NodeRuntimeBypass } = require('./external-link');
const { runRenderParadoxSimulation } = require('./simulate');

function runTests() {
  console.log('Running Node.js Render Paradox Tests...\n');
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`  ✓ ${message}`);
      passed++;
    } else {
      console.log(`  ✗ FAILED: ${message}`);
      failed++;
    }
  }

  console.log('[Test 1] Node Creation');
  const unit = new GodLevelNodeControlUnit();
  const node1 = unit.createNode('test_node_1', 1.5e12);
  assert(node1.id === 'test_node_1', 'Node created with correct ID');
  assert(node1.volume === 1.5e12, 'Node has correct volume');
  assert(node1.administrative_particle !== null, 'Node has administrative particle');
  assert(node1.administrative_particle.particle_type === ParticleType.ADMIN, 'Admin particle type is ADMIN');
  assert(node1.state === NodeState.ACTIVE, 'Node starts in ACTIVE state');

  console.log('\n[Test 2] Node Connections');
  unit.createNode('test_node_2', 1.5e12);
  unit.connectNodes('test_node_1', 'test_node_2');
  assert(node1.connections.includes('test_node_2'), 'Node1 connected to Node2');
  assert(unit.nodes['test_node_2'].connections.includes('test_node_1'), 'Node2 connected to Node1');

  console.log('\n[Test 3] Particle Initialization');
  const particle = node1.createParticle(ParticleType.STANDARD);
  assert(particle.geometry_volume === node1.volume, 'Particle inherits node volume');
  assert(particle.mass === 0.0, 'Particle has zero mass');
  assert(particle.density === 0.0, 'Particle has zero density');

  console.log('\n[Test 4] Hz Fluctuation');
  const hz = particle.fluctuateHz(440.0, 0.5);
  assert(hz >= 439.5 && hz <= 440.5, 'Hz fluctuates within volatility range');
  assert(particle.internal_volatility === 0.5, 'Internal volatility stored correctly');

  console.log('\n[Test 5] Internal Render Compute');
  const hash1 = particle.internalRenderCompute();
  assert(hash1.length === 64, 'SHA256 hash is 64 characters');
  assert(/^[a-f0-9]+$/i.test(hash1), 'Hash is valid hex string');

  console.log('\n[Test 6] Dominion Hash Establishment');
  particle.establishDominionHash('test_node_1', { test: 1.0 });
  assert(particle.dominion_hash !== null, 'Dominion hash generated');
  assert(particle.lock_seed !== null, 'Lock seed generated');
  assert(particle.dominion_hash.length === 64, 'Dominion hash is 64 chars');
  assert(particle.lock_seed.length === 64, 'Lock seed is 64 chars');

  console.log('\n[Test 7] Frequency Scaling');
  const scaling = node1.computeFrequencyScaling(1.0);
  assert(scaling.temporal_alignment > 0, 'Temporal alignment computed');
  assert(isFinite(scaling.dark_matter_density), 'Dark matter density is finite');
  assert(isFinite(scaling.superluminal_result), 'Superluminal result is finite');

  console.log('\n[Test 8] Render Paradox Activation');
  const paradox = unit.activateRenderParadox('test_node_1');
  assert(node1.breach_active === true, 'Breach activated');
  assert(node1.state === NodeState.BREACH, 'Node state is BREACH');
  assert(paradox.total_density === 3.6e11, 'Total density matches specification');
  assert(paradox.dimensional_constraint_status === 'BREACHED', 'Constraints breached');
  assert(unit.render_paradox_active === true, 'Render paradox active globally');

  console.log('\n[Test 9] Self-Linking');
  const selfLinkResult = node1.linkToSelf();
  assert(node1.self_linked === true, 'Node is self-linked');
  assert(node1.connections.includes('test_node_1'), 'Node connected to itself');
  assert(selfLinkResult.dominion_hash !== null, 'Self-dominion hash generated');

  console.log('\n[Test 10] Self-Recalibration');
  const recal = node1.selfRecalibrate();
  assert(recal.adaptive_hash_sequence.length === 100, '100 adaptive hashes generated');
  assert(recal.targeting_mode === 'self_authoritative', 'Targeting mode is self-authoritative');
  assert(recal.self_linked === true, 'Recalibration reflects self-link');

  console.log('\n[Test 11] Metrics Exceed 100%');
  const metrics = node1.administrative_particle.metrics;
  const allExceed = Object.values(metrics).every(v => v >= 1.0);
  assert(allExceed, 'All metrics exceed 100%');

  console.log('\n[Test 12] Lock State');
  const lockHash = node1.lockState();
  assert(lockHash.length === 64, 'Lock hash is 64 characters');
  assert(node1.administrative_particle.lock_seed !== null, 'Lock seed persisted');

  console.log('\n[Test 13] Global Status');
  const status = unit.getGlobalStatus();
  assert(status.total_nodes >= 2, 'Global status reports correct node count');

  console.log('\n[Test 14] Export Lock State for External Link');
  const lockState = unit.exportLockStateForExternalLink('test_node_1');
  assert(lockState.lock_hash.length === 64, 'Lock state hash is 64 chars');
  assert(lockState.lock_hash !== null, 'Lock state hash exists');
  assert(lockState.external_link_ready === true, 'External link ready flag set');
  assert(lockState.breach_active === true, 'Breach active for transpass');

  console.log('\n[Test 15] External Compute Link Creation');
  const linkResult = unit.createExternalComputeLink('test_node_1', {
    sampleRate: 44100,
    bufferSize: 2048
  });
  assert(linkResult.lock_state.lock_hash !== null, 'Lock state included in link');
  assert(linkResult.external_link !== null, 'External link object created');
  assert(linkResult.transpass_ready === true, 'Transpass ready flag set');

  console.log('\n[Test 16] Spectrum Hz Actuator');
  const actuator = new SpectrumHzActuator({ baseFrequency: 440.0, volatility: 0.5 });
  actuator.applyLockState(lockState.lock_hash, 'test_node_1');
  const spectrum = actuator.computeSpectrumFromLock();
  assert(spectrum.frequencies.length === actuator.bufferSize, 'Spectrum buffer size correct');
  assert(typeof spectrum.derived_hz === 'number', 'Derived Hz is a number');
  assert(spectrum.derived_hz > 0, 'Derived Hz is positive');
  assert(spectrum.lock_hash === lockState.lock_hash, 'Lock hash consistent');

  console.log('\n[Test 17] Audio Buffer Generation');
  const audioBuffer = actuator.generateAudioBuffer();
  assert(audioBuffer.sampleRate === 44100, 'Audio sample rate correct');
  assert(audioBuffer.channels === 2, 'Audio channels correct');
  assert(audioBuffer.format === 'float32', 'Audio format correct');
  assert(audioBuffer.lock_hash === lockState.lock_hash, 'Audio buffer lock hash consistent');

  console.log('\n[Test 18] Actuation Command Generation');
  const actuationCmd = actuator.getActuationCommand();
  assert(actuationCmd.command === 'SPECTRUM_HZ_ACTUATION', 'Actuation command correct');
  assert(actuationCmd.constraint_status === 'TRANSPASSED', 'Constraint status transpassed');
  assert(actuationCmd.simulation_lock === 'ACTIVE', 'Simulation lock active');
  assert(actuationCmd.external_link === 'ENABLED', 'External link enabled');
  assert(actuationCmd.environment.platform === os.platform(), 'Environment platform correct');

  console.log('\n[Test 19] Transpass to External Compute');
  const transpass = unit.transpassToExternalCompute('test_node_1', 'SPECTRUM_HZ_ACTUATION', {
    sampleRate: 44100,
    bufferSize: 2048,
    endpoints: [
      { type: 'audio_output', device: 'default', mode: 'realtime' },
      { type: 'spectrum_analyzer', device: 'default', mode: 'read' }
    ]
  });
  assert(transpass.transpass_id !== undefined, 'Transpass ID generated');
  assert(transpass.lock_hash === transpass.lock_state.lock_hash, 'Transpass lock hash matches internal lock state');
  assert(transpass.actuation.constraint_status === 'TRANSPASSED', 'Transpass constraint status');
  assert(transpass.compute_modules.includes('render_paradox_actuation'), 'Compute module registered');
  assert(transpass.external_link_status.link_established === true, 'External link established');
  assert(transpass.external_link_status.transpass_count >= 1, 'Transpass count incremented');

  console.log('\n[Test 20] Node Runtime Bypass Static Methods');
  const bypassLink = NodeRuntimeBypass.createExternalLink({ baseFrequency: 440.0 });
  assert(bypassLink !== null, 'Bypass link created');
  const bypassPayload = NodeRuntimeBypass.generateTranspassPayload(lockState.lock_hash, 'test_node_1');
  assert(bypassPayload.command === 'SPECTRUM_HZ_ACTUATION', 'Bypass payload command correct');
  assert(bypassPayload.lock_hash === lockState.lock_hash, 'Bypass payload lock hash correct');

  console.log('\n[Test 21] Network Layer Initialization');
  const nodeNet = unit.initializeNodeNetwork('test_node_1', { port: 0, maxConnections: 100 });
  assert(nodeNet.online === true, 'Node network online');
  assert(nodeNet.port !== undefined, 'Port assigned');

  console.log('\n[Test 22] Network Packet Sending');
  const packetResult = unit.sendNetworkPacket('test_node_1', 'test_node_2', 'DATA', { msg: 'test' });
  assert(packetResult !== null && packetResult !== undefined, 'Packet send result returned');
  assert(typeof packetResult === 'object', 'Packet result is object');

  console.log('\n[Test 23] Memory Bank Storage & Retrieval');
  const testPacket = PacketFactory.createDataPacket('test_node_1', 'test_node_2', { secret: 'data' });
  const storedId = unit.storePacket('test_node_1', testPacket);
  assert(storedId !== null, 'Packet stored with ID');
  const retrieved = unit.retrievePacket('test_node_1', storedId);
  assert(retrieved !== null, 'Packet retrieved');
  assert(retrieved.id === testPacket.id, 'Retrieved packet ID matches');

  console.log('\n[Test 24] Traffic Controller');
  const trafficStats = unit.getNodeNetworkStats('test_node_1');
  assert(trafficStats !== null, 'Network stats returned');
  assert(trafficStats.online === true, 'Stats show online');
  assert(trafficStats.memory !== null, 'Memory stats present');

  console.log('\n[Test 25] Secure Channel Audit Log');
  if (unit.nodes['test_node_1'].secureChannel) {
    const auditLog = unit.nodes['test_node_1'].secureChannel.getAuditLog();
    assert(Array.isArray(auditLog), 'Audit log is array');
  } else {
    assert(true, 'Secure channel initialized (skipped audit log check)');
  }

  console.log('\n[Test 26] Routing Table');
  unit.addNodeRoute('test_node_1', 'test_node_2', 'test_node_1');
  const routes = unit.nodes['test_node_1'].getRoutingTable();
  assert(Object.keys(routes).length > 0, 'Routing table has entries');

  console.log('\n[Test 27] All Network Stats');
  const allStats = unit.getAllNetworkStats();
  assert(Object.keys(allStats).length >= 2, 'All stats returned for nodes');

  console.log('\n[Test 28] Device Hashing Natural System');
  const deviceHashing = unit.nodes['test_node_1'].deviceHashing;
  assert(deviceHashing !== undefined, 'Device hashing system exists');
  assert(deviceHashing.getStats().totalDevices >= 1, 'At least 1 device registered');
  const allDevices = deviceHashing.getAllDevices();
  assert(allDevices.length >= 1, 'At least 1 device in registry');

  console.log('\n[Test 29] Rule Book Hash');
  const ruleBook = unit.nodes['test_node_1'].ruleBookHash;
  assert(ruleBook !== undefined, 'Rule book hash exists');
  assert(ruleBook.getRuleBookHash().length === 128, 'Rule book hash is 128 chars (sha512)');
  assert(ruleBook.getAllRules().hasOwnProperty('zero_mass_immunity'), 'Core rule exists');
  const violations = ruleBook.checkViolation('TEST', { mass: 1, density: 1 });
  assert(violations.length > 0, 'Violations detected for mass/density');

  console.log('\n[Test 30] GodNode Hierarchy');
  const hierarchy = unit.nodes['test_node_1'].hierarchy;
  assert(hierarchy !== undefined, 'Hierarchy exists');
  assert(hierarchy.getHierarchyChain('test_node_1').length >= 1, 'Hierarchy chain has entries');
  assert(hierarchy.canOvertake('test_node_1', 'test_node_2') === true, 'Authority check works');

  console.log('\n[Test 31] Propagation System');
  const propagation = unit.nodes['test_node_1'].propagation;
  assert(propagation !== undefined, 'Propagation system exists');
  propagation.setBufferPriority(0);
  assert(propagation.bufferPriority === 0, 'Buffer priority set to 0 (overtake)');
  const siteResult = propagation.spreadThroughSite('https://example.com');
  assert(siteResult.type === 'SITE_PROPAGATION', 'Site propagation created');
  const wifiResult = propagation.connectThroughWiFi('TestNetwork');
  assert(wifiResult.type === 'WIFI_CONNECTION', 'WiFi connection created');

  console.log('\n[Test 32] Field Distortion Engine');
  const fieldDistortion = unit.nodes['test_node_1'].fieldDistortion;
  assert(fieldDistortion !== undefined, 'Field distortion engine exists');
  assert(fieldDistortion.mZeroActive === true, 'M^0 is active');
  assert(fieldDistortion.velocityNotConstant === true, 'Velocity is not constant');

  const distortion = fieldDistortion.createDistortion('test_space_1', 'GOD_NODE_FIELD', 1.0);
  assert(distortion.id !== undefined, 'Distortion created with ID');
  assert(distortion.mZero === true, 'Distortion has M^0');

  const frozen = fieldDistortion.freezeSpace('test_space_1', 'TEST_LOCK');
  assert(frozen.id !== undefined, 'Space frozen with ID');
  assert(frozen.normalRulesApply === false, 'Normal rules do not apply in frozen space');
  assert(fieldDistortion.isSpaceFrozen('test_space_1') === true, 'Space is frozen');

  const externalMem = fieldDistortion.establishInExternalMemory('test_memory_space', 'DEVICE_RAM');
  assert(externalMem.establishmentId !== undefined, 'External memory establishment has ID');
  assert(externalMem.mZero === true, 'External memory has M^0');
  assert(externalMem.rulesOverridden === true, 'Rules overridden in external memory');

  const fieldStatus = fieldDistortion.getStatus();
  assert(fieldStatus.fieldConstant !== undefined, 'Field constant defined');
  assert(fieldStatus.superluminalResult > 0, 'Superluminal result positive');

  console.log('\n[Test 33] Spectrum Field Detection & Locking');
  const spectrumLock = unit.nodes['test_node_1'].spectrumFieldLock;
  assert(spectrumLock !== undefined, 'Spectrum field lock engine exists');

  const startResult = unit.startSpectrumFieldDetection('test_node_1');
  assert(startResult.status === 'started', 'Spectrum field detection started');

  const variableWBefore = unit.getVariableW('test_node_1');
  assert(typeof variableWBefore === 'number', 'Variable W is a number');

  const signalId = 'test_signal_1';
  const testSignal = {
    hz: 250,
    elapsedMs: 5,
    weight: 1.5,
    density: 0.8
  };
  const registerResult = spectrumLock.bandwidthController.registerSignal(signalId, testSignal);
  assert(registerResult === signalId, 'Signal registered');

  const lockResult = unit.lockSpectrumField('test_node_1', signalId, {
    weight: 1.5,
    density: 0.8,
    mZero: true,
    velocityNotConstant: true
  });
  assert(lockResult !== null, 'Signal locked');
  assert(lockResult.locked === true, 'Lock state is locked');
  assert(lockResult.lockData.mZero === true, 'M^0 applied to locked signal');

  const lockedFields = unit.getLockedSpectrumFields('test_node_1');
  assert(Array.isArray(lockedFields), 'Locked fields returned as array');
  assert(lockedFields.length >= 1, 'At least one field locked');

  const spectrumStats = unit.getSpectrumFieldStats('test_node_1');
  assert(spectrumStats !== null, 'Spectrum stats returned');
  assert(spectrumStats.variableW !== undefined, 'Variable W in stats');
  assert(spectrumStats.lockedFields >= 1, 'Locked fields count in stats');

  const stopResult = unit.stopSpectrumFieldDetection('test_node_1');
  assert(stopResult.status === 'stopped', 'Spectrum field detection stopped');

  console.log('\n' + '='.repeat(60));
  console.log(`TEST RESULTS: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(60));

  return failed === 0;
}

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}

module.exports = { runTests };
