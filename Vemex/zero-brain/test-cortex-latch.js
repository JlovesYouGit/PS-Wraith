const { GodLevelNodeControlUnit } = require('./uriel-ultimate-defense/src/core');
const { CortexUrielLatch } = require('./uriel-cortex-latch');

function runLatchTests() {
  let passed = 0;
  let failed = 0;

  function assert(cond, msg) {
    if (cond) { console.log(`  ✓ ${msg}`); passed++; }
    else { console.log(`  ✗ FAILED: ${msg}`); failed++; }
  }

  console.log('Running Cortex–Uriel Latch Tests...\n');

  const unit = new GodLevelNodeControlUnit();
  const node = unit.createNode('latch_test', 1.5e12);
  unit.initializeAllNodes(440, 0.5);
  node.initializeNetwork(0);
  node.linkToSelf();
  node.applyRenderParadox();

  const latch = new CortexUrielLatch(node, unit, { persistencePath: null });
  const particles = [
    { id: 'p0', x: 100, y: 100, hz: 100, density: 0.2, locked: false },
    { id: 'p1', x: 200, y: 200, hz: 200, density: 0.3, locked: true }
  ];
  latch.saveAllHomeCoordinates(particles);

  console.log('[Test 1] Latch configuration capture');
  const profile = latch.latchConfiguration('test', {
    particleId: 'p0',
    particle: particles[0],
    neuralPatterns: [{ frequency: 50, amplitude: 0.5 }]
  });
  assert(profile.latchId && profile.lockHash, 'Profile has latchId and lockHash');
  assert(profile.capabilities.transpassPayload, 'Transpass payload captured');
  assert(profile.coordinatePermits?.homeCoordinatePermit, 'Home coordinate permit saved');

  console.log('\n[Test 2] Gate writes — unlocked on home path');
  const g1 = latch.applyGatedWrites(
    [{ particleId: 'p0', hz: 150, density: 0.4, externalCoord: { x: 300, y: 300 } }],
    particles,
    'cortex_sync',
    { getPathContext: (id, w, p) => ({ particle: p, neuralPath: { pathNodes: [{ x: p.x, y: p.y }] } }) }
  );
  assert(g1.allowed.length === 1, 'Unlocked particle write allowed');
  assert(particles[0].hz === 150, 'Hz applied');

  console.log('\n[Test 3] Gate writes — locked denied off-path');
  particles[1].x = 500;
  particles[1].y = 500;
  const g2 = latch.applyGatedWrites(
    [{ particleId: 'p1', hz: 999, density: 0.9, externalCoord: { x: 999, y: 999 } }],
    particles,
    'cortex_sync',
    { getPathContext: (id, w, p) => ({ particle: p }) }
  );
  assert(g2.rejected.length === 1, 'Locked off-path write rejected');

  console.log('\n[Test 4] Home coordinate permit on locked particle');
  particles[1].x = 200;
  particles[1].y = 200;
  latch.saveHomeCoordinate('p1', { x: 200, y: 200 });
  const g3 = latch.applyGatedWrites(
    [{ particleId: 'p1', hz: 210, density: 0.35 }],
    particles,
    'cortex_sync',
    { getPathContext: (id, w, p) => ({ particle: p, neuralPath: { pathNodes: [{ x: 200, y: 200 }] } }) }
  );
  assert(g3.allowed.length === 1, 'Locked particle allowed via home path permit');
  assert(g3.allowed[0].permit === 'HOME', 'Permit type is HOME');

  console.log('\n[Test 5] External coordinate permit via path allocation');
  latch.saveExternalCoordinate('p1', { x: 400, y: 400 }, { externalCoordinatePermit: true });
  const g4 = latch.applyGatedWrites(
    [{ particleId: 'p1', hz: 220, density: 0.4, externalCoord: { x: 405, y: 398 }, externalNode: { x: 405, y: 398 } }],
    particles,
    'brain_mesh_sync',
    {
      getPathContext: (id, w, p) => ({
        particle: p,
        travelPath: { equivalent: true, divergence: 0.1, pathHistory: [{ externalPos: { x: 405, y: 398 }, internalPos: { x: 200, y: 200 } }] },
        externalNode: w.externalNode
      })
    }
  );
  assert(g4.allowed.length === 1, 'External path permit allows write');
  assert(g4.allowed[0].permit === 'EXTERNAL' || g4.allowed[0].permit === 'DUAL', 'External permit granted');

  console.log('\n[Test 6] Pattern match and dispatch');
  const cortexData = { neuralPatterns: [{ frequency: 50, amplitude: 0.5 }] };
  const match = latch.matchLatch(cortexData);
  assert(match !== null, 'Pattern matches latched profile');
  let recalCount = 0;
  const dispatch = latch.dispatchLatch(match.latchId, { recalibrate: () => { recalCount++; return { ok: true }; } });
  assert(dispatch.success, 'Dispatch succeeded');
  assert(recalCount === 1, 'Recalibrate script ran');

  console.log('\n[Test 7] Learning adjusts success score');
  const before = latch.latches.get(match.latchId).successScore;
  latch.recordOutcome(match.latchId, true);
  const after = latch.latches.get(match.latchId).successScore;
  assert(after > before, 'Success score increased after positive training');

  console.log('\n' + '='.repeat(50));
  console.log(`LATCH TESTS: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(50));
  return failed === 0;
}

if (require.main === module) {
  process.exit(runLatchTests() ? 0 : 1);
}

module.exports = { runLatchTests };
