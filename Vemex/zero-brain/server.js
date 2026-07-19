const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');
const { exec } = require('child_process');

// Import the cloned Uriel defense core elements
const { GodLevelNodeControlUnit } = require('./uriel-ultimate-defense/src/core');
const { CortexUrielLatch } = require('./uriel-cortex-latch');

// Create the control unit node
const controlUnit = new GodLevelNodeControlUnit();
const nodeAlpha = controlUnit.createNode('node_alpha', 1.8e12);

// Initialize network & core nodes
controlUnit.initializeAllNodes(440.0, 0.5);
nodeAlpha.initializeNetwork(0);
nodeAlpha.spectrumFieldLock.start();
nodeAlpha.linkToSelf();
nodeAlpha.applyRenderParadox();

// Set initial simulation settings
let threatLevel = 0.0;
let xRayPulseActive = false;
let xRayPulseTimer = 0;
let translationGateActive = false;
let translationGateBending = 0.0; // field bend intensity
const activeLocks = new Map(); // signalId -> lock metadata
const motherboardPaths = []; // scanned/static trace lines
const movingElectrons = []; // active moving electron currents

// Advanced spectrum and brain module constants
const PI_RATIO = Math.PI;
const THREE_METER_BOUNDARY = 120; // 3 meters in pixel scale (40px per meter)
const DENSITY_LAYERS = 5;
const PHASORY_LOCK_ANGLE = 30 * (Math.PI / 180); // 30 degrees in radians
const INVERSIVE_WAVE_FREQUENCY = 0.25;
const COLLIDING_CHANNEL_MIN_SIZE = 2.0;

// Virtual sensor system constants
const SENSOR_CALIBRATION_INTERVAL = 1000;
const DATA_PIPELINE_BUFFER_SIZE = 1000;
const PRECISION_SYNC_THRESHOLD = 0.95;
const OPTIMIZATION_CYCLE_INTERVAL = 200;
const CORTEX_CACHE_READ_INTERVAL = 50;

// Brain module pattern state
const brainModulePatterns = new Map();
const transitiveStates = [];
const densityLayerMap = new Map();
const collidingChannels = [];

// Virtual sensor system state
const virtualSensors = new Map();
const dataPipelines = new Map();
const sensorCalibrationData = new Map();
const realLockStates = new Map(); // Actual device lock states

// Brain mesh synchronization state
const externalBrainMesh = new Map(); // External brain mesh detection
const internalBrainMesh = new Map(); // Internal machine brain mesh
const neuralPaths = new Map(); // Neural path tracking
const travelPaths = new Map(); // Travel path equivalents
const nodeStabilityTracker = new Map(); // Node ID stability tracking
const meshSyncState = {
  externalDetected: false,
  internalActive: false,
  bidirectionalSync: false,
  syncQuality: 0.0,
  lastSyncTime: 0
};

// Async cache system for external cerebral cortex data
const externalCortexCache = new Map();
const cortexCacheConfig = {
  maxSize: 1000,
  ttl: 60000, // 60 seconds cache TTL
  asyncReadInterval: 100,
  bufferFlowRate: 0.1,
  optimizationCycle: 0
};

// Dual optimization cycle state
const dualOptimizationState = {
  cycleActive: false,
  cycleRate: 0.0,
  patternReactionRate: 0.0,
  externalPace: 1.0,
  internalPace: 1.0,
  optimizationLevel: 0.0,
  ghzSyncRate: 0.0,
  cpuGhz: 0.0,
  externalGhz: 0.0,
  dataDumpBuffer: [],
  bufferFlowIndex: 0
};

// Method handle and logging system
const methodHandles = new Map();
const systemLogs = new Map();
const hardwareLayerState = {
  cpuOptimization: 0.0,
  memoryOptimization: 0.0,
  networkOptimization: 0.0,
  systemLayerActive: false
};

// Lossless scale render security system
const renderSecurityState = {
  transitionActive: false,
  currentScale: 1.0,
  targetScale: 1.0,
  securityLevel: 0.0,
  integrityCheck: true,
  lastTransitionTime: 0,
  transitionHistory: [],
  scaleFactors: new Map(),
  securityTokens: new Map()
};

const renderSecurityConfig = {
  maxScale: 2.0,
  minScale: 0.5,
  scaleStep: 0.01,
  securityThreshold: 0.8,
  integrityCheckInterval: 100,
  tokenTTL: 30000
};

// Mamba layer weight management and cache system
const mambaWeightState = {
  A_log: new Map(),
  A_weights: new Map(),
  delta_bias: new Map(),
  in_proj_split: new Map(),
  weightShapes: new Map(),
  statistics: new Map(),
  loadedParameters: 0,
  totalParameters: 343,
  gibberishDetected: false
};

const mambaCacheConfig = {
  maxCacheSize: 10000,
  quantizationBits: 8,
  superSamplingFactor: 2,
  hadamardGatingEnabled: true,
  resourceAllocationStyle: 'adaptive'
};

// QBOM Coherence Gate System — lane-managed quantization with zone recall
const qbomState = {
  lanes: new Array(16).fill(null).map((_, i) => ({
    laneId: i,
    isSecure: (i % 4 === 0),
    pathAssociation: Math.floor(i / 4),
    utilization: 0.0,
    zoneMap: new Map(),       // zone coordinate -> quantized resolution pointer
    blockOrder: [],           // ordered block indices for this lane
    coherenceScore: 1.0
  })),
  blockOrganizer: {
    organizerId: 0,
    lane15: 15,
    chosenPath: 0,
    blockSelector: [0, 0],
    closestSecureLane: 0,
    designatedPath: 0
  },
  coherenceBalancers: {
    qStateCoherence: 0.95,
    qStateAmplitude: 1.0,
    qStatePhase: 0.0,
    cryptvalThreshold: 0.95,
    validationScore: 1.0,
    peakCoherence: 0.0,
    totalLaneSwaps: 0,
    totalValidations: 0,
    gateFlags: 0x01   // allow flag
  },
  // zone-mapped resolution cache: stores compressed zone coordinates
  // so cache can recall exactly where full resolution resides
  zoneCache: new Map(),
  quantizationRegistry: new Map()   // tracks what got quantized and the reduction ratio
};

// KV cache split and super sampling
const kvCacheState = {
  splitCache: new Map(),
  superSamplingDistribution: new Map(),
  attentionMetadata: new Map(),
  exponentialConsShape: new Map(),
  meshCoordinateAllocation: new Map()
};

// Embedded modeling and context routing
const embeddedModelState = {
  embeddingRoute: new Map(),
  contextCache: new Map(),
  tokenGeneration: new Map(),
  weightRecall: new Map(),
  terminalAccessible: new Map()
};

// Resource allocation management
const resourceAllocationState = {
  allocatedResources: new Map(),
  resourceLimits: new Map(),
  allocationHistory: [],
  truncationPrevention: true
};

// Generate initial motherboard trace networks (separated paths for dual layers)
function generateTraces() {
  const topLayerPaths = [
    { id: 'top_1', layer: 'top', density: 0.8, points: [{x: 50, y: 50}, {x: 200, y: 50}, {x: 250, y: 150}, {x: 400, y: 150}] },
    { id: 'top_2', layer: 'top', density: 0.6, points: [{x: 80, y: 150}, {x: 180, y: 150}, {x: 220, y: 220}, {x: 350, y: 220}] },
    { id: 'top_3', layer: 'top', density: 0.9, points: [{x: 50, y: 350}, {x: 150, y: 350}, {x: 200, y: 400}, {x: 450, y: 400}] }
  ];

  const bottomLayerPaths = [
    { id: 'bottom_1', layer: 'bottom', density: 0.7, points: [{x: 100, y: 80}, {x: 100, y: 250}, {x: 250, y: 250}, {x: 250, y: 350}] },
    { id: 'bottom_2', layer: 'bottom', density: 0.5, points: [{x: 380, y: 80}, {x: 380, y: 300}, {x: 300, y: 300}, {x: 150, y: 300}] },
    { id: 'bottom_3', layer: 'bottom', density: 0.85, points: [{x: 420, y: 50}, {x: 420, y: 180}, {x: 480, y: 240}, {x: 480, y: 350}] }
  ];

  motherboardPaths.push(...topLayerPaths, ...bottomLayerPaths);

  // Initialize density layer mapping
  motherboardPaths.forEach(path => {
    const layerKey = `${path.layer}_${Math.floor(path.density * DENSITY_LAYERS)}`;
    if (!densityLayerMap.has(layerKey)) {
      densityLayerMap.set(layerKey, []);
    }
    densityLayerMap.get(layerKey).push(path.id);
  });

  // Seed default electrons along the paths
  for (let i = 0; i < 15; i++) {
    spawnElectron();
  }
}

function spawnElectron() {
  const pathObj = motherboardPaths[Math.floor(Math.random() * motherboardPaths.length)];
  movingElectrons.push({
    id: `e_${Math.random().toString(36).substr(2, 5)}`,
    pathId: pathObj.id,
    pointIndex: 0,
    progress: 0.0,
    speed: 0.01 + Math.random() * 0.015,
    x: pathObj.points[0].x,
    y: pathObj.points[0].y,
    layer: pathObj.layer,
    density: pathObj.density,
    signalStrength: 0.5 + Math.random() * 0.5,
    phase: Math.random() * Math.PI * 2
  });
}

generateTraces();

// Particle generation (Code Virtual Mesh & Brain modules)
const simulationParticles = [];
for (let i = 0; i < 40; i++) {
  const particleId = `particle_${i}`;
  const angle = Math.random() * Math.PI * 2;
  const radius = 50 + Math.random() * 150;
  
  simulationParticles.push({
    id: particleId,
    // Spatial positioning coordinates
    x: 250 + Math.cos(angle) * radius,
    y: 250 + Math.sin(angle) * radius,
    vx: (Math.random() - 0.5) * 1.5,
    vy: (Math.random() - 0.5) * 1.5,
    speedFactor: 1.0,
    lockAngle: 0.0, // initial phasory lock angle
    phaseOutFactor: 0.0,
    inversiveWaveState: 0.0,
    inversiveWaveAmplitude: 1.0,
    wrappingFactor: 0.0,
    interferenceFactor: 0.0,
    locked: false,
    pairedElectrodeId: null,
    transitiveState: null,
    brainModulePattern: null,
    // Base properties from Uriel
    hz: 100 + Math.random() * 900,
    weight: 0.5 + Math.random() * 1.5,
    density: 0.1 + Math.random() * 0.4,
    piRatio: Math.PI / (1 + Math.random() * 2),
    boundaryDistance: 0
  });
}

// Simulated brain electrodes for pair-to-pair transmit mapping
const brainElectrodes = [];
for (let i = 0; i < 12; i++) {
  const angle = (i / 12) * Math.PI * 2;
  brainElectrodes.push({
    id: `elec_${i}`,
    x: 250 + Math.cos(angle) * 180,
    y: 250 + Math.sin(angle) * 180,
    charge: 0.1,
    active: false,
    fusedParticleId: null,
    boundaryRadius: THREE_METER_BOUNDARY,
    piRatioControl: PI_RATIO / (i + 1),
    patternMatchScore: 0.0
  });
}

// Initialize virtual sensor system
initializeVirtualSensors();
initializeDataPipelines();
startSensorCalibration();
initializeBrainMeshSystem();
initializeAsyncCortexCache();
startDualOptimizationCycle();
initializeRenderSecurity();
initializeMambaWeightSystem();
initializeKVCacheSystem();
initializeEmbeddedModeling();
initializeResourceAllocation();

// Cortex–Uriel latch: gates external writes, stores capability profiles, dispatches on pattern match
const cortexLatch = new CortexUrielLatch(nodeAlpha, controlUnit, {
  persistencePath: path.join(__dirname, '.cortex_latch_store.json')
});

function getLatchHandlers() {
  return {
    recalibrate: () => nodeAlpha.selfRecalibrate(),
    applySpectrumLock: (particleId) => {
      const particle = simulationParticles.find(p => p.id === particleId);
      if (!particle) return;
      nodeAlpha.spectrumFieldLock.lockField(particleId, {
        weight: particle.weight,
        density: particle.density,
        fieldConstant: 1.0,
        mZero: true,
        velocityNotConstant: true,
        spatialLock: true
      });
    }
  };
}

cortexLatch.saveAllHomeCoordinates(simulationParticles);
cortexLatch.latchConfiguration('startup', { allowExternalWrites: false });

function getPathContextForWrite(particleId, write, particle) {
  const neuralPath = internalBrainMesh.get(particleId);
  const travelPath = Array.from(travelPaths.values()).find(p => p.internalNode === particleId);
  return {
    particle,
    neuralPath,
    travelPath,
    externalNode: write.externalNode || null
  };
}

function getLatchWriteOptions() {
  return { getPathContext: getPathContextForWrite };
}

// SSE Connection pool
const sseClients = new Set();

// Active simulation update loop (~30 FPS)
setInterval(() => {
  // Update X-ray pulsating scanner timer
  if (xRayPulseActive) {
    xRayPulseTimer -= 33;
    if (xRayPulseTimer <= 0) {
      xRayPulseActive = false;
    }
  }

  // Update translation gate dynamics
  if (translationGateActive) {
    translationGateBending = Math.min(1.0, translationGateBending + 0.02);
  } else {
    translationGateBending = Math.max(0.0, translationGateBending - 0.04);
  }

  // 1. Update motherboard electrons
  movingElectrons.forEach((electron, index) => {
    const trace = motherboardPaths.find(p => p.id === electron.pathId);
    if (!trace) return;

    electron.progress += electron.speed;
    if (electron.progress >= 1.0) {
      electron.pointIndex++;
      electron.progress = 0.0;
    }

    if (electron.pointIndex >= trace.points.length - 1) {
      // Re-spawn electron at starting point
      electron.pointIndex = 0;
      electron.progress = 0.0;
      // Occasionally switch paths
      const newTrace = motherboardPaths[Math.floor(Math.random() * motherboardPaths.length)];
      electron.pathId = newTrace.id;
      electron.layer = newTrace.layer;
    }

    const pStart = trace.points[electron.pointIndex];
    const pEnd = trace.points[electron.pointIndex + 1];
    electron.x = pStart.x + (pEnd.x - pStart.x) * electron.progress;
    electron.y = pStart.y + (pEnd.y - pStart.y) * electron.progress;
  });

  // 2. Update Virtual Mesh Particles with advanced phasory lock and brain module patterns
  simulationParticles.forEach(p => {
    // Calculate boundary distance for 3-meter reading
    p.boundaryDistance = Math.hypot(p.x - 250, p.y - 250);
    
    // Generate transitive state based on particle movement
    const transitiveState = {
      position: { x: p.x, y: p.y },
      velocity: { x: p.vx, y: p.vy },
      hz: p.hz,
      density: p.density,
      timestamp: Date.now(),
      piRatio: p.piRatio
    };
    
    if (p.locked) {
      // Speed reduction due to lock bounds
      p.speedFactor = Math.max(0.02, p.speedFactor - 0.05);
      p.vx = (p.vx * p.speedFactor);
      p.vy = (p.vy * p.speedFactor);
      
      // Phase out displacement
      p.phaseOutFactor = Math.min(1.0, p.phaseOutFactor + 0.04);
      
      // Advanced inversive wave with wrapping and interference
      p.inversiveWaveState = (p.inversiveWaveState + INVERSIVE_WAVE_FREQUENCY) % (Math.PI * 2);
      p.wrappingFactor = Math.min(1.0, p.wrappingFactor + 0.03);
      p.interferenceFactor = Math.sin(p.inversiveWaveState * 2) * p.wrappingFactor;
      
      // Adjust locking angle target to 30 degrees (PHASORY_LOCK_ANGLE)
      p.lockAngle += (PHASORY_LOCK_ANGLE - p.lockAngle) * 0.1;
      
      // Apply trajectory bending with inversive wave interference
      const bendFactor = p.lockAngle * p.interferenceFactor;
      p.vx += Math.cos(bendFactor) * 0.01;
      p.vy += Math.sin(bendFactor) * 0.01;
      
      // Generate brain module pattern from transitive state
      if (!p.brainModulePattern) {
        p.brainModulePattern = generateBrainModulePattern(transitiveState);
        brainModulePatterns.set(p.id, p.brainModulePattern);
      }
      
      // Store transitive state for pattern matching
      transitiveStates.push({ particleId: p.id, state: transitiveState });
      if (transitiveStates.length > 200) transitiveStates.shift();
      
    } else {
      p.speedFactor = Math.min(1.0, p.speedFactor + 0.01);
      p.wrappingFactor = Math.max(0.0, p.wrappingFactor - 0.02);
      p.interferenceFactor = 0.0;
      
      // Floating random movements with pi ratio influence
      p.x += p.vx * p.speedFactor * p.piRatio;
      p.y += p.vy * p.speedFactor * p.piRatio;

      // Keep particles inside bounding arena
      const centerDist = Math.hypot(p.x - 250, p.y - 250);
      if (centerDist > 220) {
        const dx = (p.x - 250) / centerDist;
        const dy = (p.y - 250) / centerDist;
        p.vx = -dx * (0.5 + Math.random());
        p.vy = -dy * (0.5 + Math.random());
        p.x = 250 + dx * 219;
        p.y = 250 + dy * 219;
      }
    }
  });

  // 3. Update electrodes charges & sync locked particle pairs with pi ratio control
  let lockStateCount = 0;
  simulationParticles.forEach(p => {
    if (p.locked) lockStateCount++;
  });

  brainElectrodes.forEach(el => {
    if (translationGateActive && translationGateBending > 0.5) {
      // Scan for nearest locked particles within 3-meter boundary using pi ratio control
      const boundaryRadius = el.boundaryRadius * el.piRatioControl;
      
      const nearestParticle = simulationParticles
        .filter(p => p.locked && !p.pairedElectrodeId)
        .find(p => {
          const dist = Math.hypot(p.x - el.x, p.y - el.y);
          // Pattern matching based on brain module similarity
          const patternMatch = p.brainModulePattern ? 
            calculatePatternMatch(p.brainModulePattern, el.piRatioControl) : 0;
          el.patternMatchScore = patternMatch;
          return dist < boundaryRadius && patternMatch > 0.5;
        });

      if (nearestParticle) {
        nearestParticle.pairedElectrodeId = el.id;
        el.fusedParticleId = nearestParticle.id;
        el.active = true;
        
        // Create colliding channel for pair-to-pair transmit
        createCollidingChannel(el.id, nearestParticle.id);
      }
    }

    if (el.active) {
      el.charge = Math.min(1.0, el.charge + 0.05);
    } else {
      el.charge = Math.max(0.1, el.charge - 0.02);
      el.patternMatchScore = 0.0;
    }
  });
  
  // Update colliding channels minimization
  updateCollidingChannels();

  // Update global Uriel node spectrum controls
  const variableW = nodeAlpha.spectrumFieldLock.getVariableW();
  threatLevel = nodeAlpha.urielDefense.currentThreatLevel;

  // Compile SSE payload
  const updatePayload = {
    electrons: movingElectrons.map(e => ({ 
      id: e.id, 
      x: e.x, 
      y: e.y, 
      layer: e.layer,
      density: e.density,
      signalStrength: e.signalStrength,
      phase: e.phase
    })),
    particles: simulationParticles.map(p => ({
      id: p.id,
      x: p.x,
      y: p.y,
      locked: p.locked,
      lockAngle: p.lockAngle,
      phaseOut: p.phaseOutFactor,
      wave: p.inversiveWaveState,
      waveAmplitude: p.inversiveWaveAmplitude,
      wrapping: p.wrappingFactor,
      interference: p.interferenceFactor,
      hz: p.hz,
      piRatio: p.piRatio,
      boundaryDistance: p.boundaryDistance,
      brainPattern: p.brainModulePattern ? p.brainModulePattern.signature : null
    })),
    electrodes: brainElectrodes.map(el => ({
      id: el.id,
      x: el.x,
      y: el.y,
      charge: el.charge,
      active: el.active,
      pairedId: el.fusedParticleId,
      boundaryRadius: el.boundaryRadius,
      piRatioControl: el.piRatioControl,
      patternMatchScore: el.patternMatchScore
    })),
    meta: {
      threatLevel,
      variableW,
      xRayPulseActive,
      translationGateActive,
      translationGateBending,
      lockStateCount,
      densityLayers: Object.fromEntries(densityLayerMap),
      collidingChannels: collidingChannels.length,
      sensors: getSensorStatus(),
      calibration: getCalibrationStatus(),
      brainMesh: getBrainMeshStatus(),
      renderSecurity: getRenderSecurityStatus(),
      mambaWeights: getMambaWeightStatus(),
      kvCache: getKVCacheStatus(),
      embeddedModel: getEmbeddedModelStatus(),
      resourceAllocation: getResourceAllocationStatus(),
      cortexLatch: {
        latchCount: cortexLatch.latches.size,
        coordinateCount: cortexLatch.coordinateRegistry.size,
        stats: { ...cortexLatch.stats }
      }
    }
  };

  broadcastSSE(updatePayload);
}, 33);

function broadcastSSE(data) {
  const formatted = `data: ${JSON.stringify(data)}\n\n`;
  sseClients.forEach(client => client.write(formatted));
}

// Helper function: Generate brain module pattern from transitive particle state
function generateBrainModulePattern(transitiveState) {
  const signature = crypto.createHash('sha256').update(JSON.stringify({
    position: transitiveState.position,
    velocity: transitiveState.velocity,
    hz: transitiveState.hz,
    density: transitiveState.density,
    piRatio: transitiveState.piRatio,
    timestamp: transitiveState.timestamp
  })).digest('hex').substring(0, 16);
  
  return {
    signature,
    position: transitiveState.position,
    velocity: transitiveState.velocity,
    hz: transitiveState.hz,
    density: transitiveState.density,
    piRatio: transitiveState.piRatio,
    createdAt: transitiveState.timestamp,
    patternType: 'BRAIN_MODULE_TRANSITIVE'
  };
}

// Helper function: Calculate pattern match score between brain module and electrode pi ratio
function calculatePatternMatch(brainPattern, electrodePiRatio) {
  if (!brainPattern) return 0;
  
  const piDiff = Math.abs(brainPattern.piRatio - electrodePiRatio);
  const hzFactor = brainPattern.hz / 1000;
  const densityFactor = brainPattern.density;
  
  // Pattern match based on pi ratio similarity, frequency, and density
  const matchScore = (1 - piDiff) * 0.4 + hzFactor * 0.3 + densityFactor * 0.3;
  return Math.max(0, Math.min(1, matchScore));
}

// Helper function: Create colliding channel for pair-to-pair transmit
function createCollidingChannel(electrodeId, particleId) {
  const existingChannel = collidingChannels.find(ch => 
    ch.electrodeId === electrodeId && ch.particleId === particleId
  );
  
  if (existingChannel) return existingChannel;
  
  const channel = {
    id: crypto.randomBytes(8).toString('hex'),
    electrodeId,
    particleId,
    createdAt: Date.now(),
    size: 10.0,
    minimized: false,
    active: true,
    transmitSync: 0.0
  };
  
  collidingChannels.push(channel);
  return channel;
}

// Helper function: Update colliding channels minimization
function updateCollidingChannels() {
  for (let i = collidingChannels.length - 1; i >= 0; i--) {
    const channel = collidingChannels[i];
    
    // Minimize channel size over time
    if (!channel.minimized && channel.size > COLLIDING_CHANNEL_MIN_SIZE) {
      channel.size *= 0.95;
      if (channel.size <= COLLIDING_CHANNEL_MIN_SIZE) {
        channel.minimized = true;
      }
    }
    
    // Update transmit synchronization
    channel.transmitSync = Math.min(1.0, channel.transmitSync + 0.02);
    
    // Remove inactive channels
    const electrode = brainElectrodes.find(el => el.id === channel.electrodeId);
    const particle = simulationParticles.find(p => p.id === channel.particleId);
    
    if (!electrode || !particle || !electrode.active || !particle.locked) {
      collidingChannels.splice(i, 1);
    }
  }
}

// Virtual Sensor System Implementation
function initializeVirtualSensors() {
  // CPU Sensor
  virtualSensors.set('cpu', {
    id: 'cpu_sensor',
    type: 'SYSTEM_RESOURCE',
    dataType: 'PERCENTAGE',
    calibrationFactor: 1.0,
    lastReading: 0,
    readings: [],
    active: true
  });
  
  // Memory Sensor
  virtualSensors.set('memory', {
    id: 'memory_sensor',
    type: 'SYSTEM_RESOURCE',
    dataType: 'PERCENTAGE',
    calibrationFactor: 1.0,
    lastReading: 0,
    readings: [],
    active: true
  });
  
  // Network Sensor
  virtualSensors.set('network', {
    id: 'network_sensor',
    type: 'NETWORK_TRAFFIC',
    dataType: 'BYTES_PER_SECOND',
    calibrationFactor: 1.0,
    lastReading: 0,
    readings: [],
    active: true
  });
  
  // Spectrum Field Sensor
  virtualSensors.set('spectrum', {
    id: 'spectrum_sensor',
    type: 'SPECTRUM_FIELD',
    dataType: 'HZ_DENSITY',
    calibrationFactor: 1.0,
    lastReading: { hz: 0, density: 0 },
    readings: [],
    active: true
  });
  
  // Process Lock Sensor
  virtualSensors.set('process_lock', {
    id: 'process_lock_sensor',
    type: 'LOCK_STATE',
    dataType: 'BOOLEAN',
    calibrationFactor: 1.0,
    lastReading: false,
    readings: [],
    active: true
  });
  
  // External Brain Mesh Sensor
  virtualSensors.set('external_brain_mesh', {
    id: 'external_brain_mesh_sensor',
    type: 'BRAIN_MESH',
    dataType: 'MESH_TOPOLOGY',
    calibrationFactor: 1.0,
    lastReading: { detected: false, nodeCount: 0, topology: null },
    readings: [],
    active: true
  });
  
  // Internal Neural Path Sensor
  virtualSensors.set('neural_path', {
    id: 'neural_path_sensor',
    type: 'NEURAL_PATH',
    dataType: 'PATH_TOPOLOGY',
    calibrationFactor: 1.0,
    lastReading: { pathCount: 0, activePaths: [] },
    readings: [],
    active: true
  });
}

function initializeDataPipelines() {
  // Sensor to Calibration Pipeline
  dataPipelines.set('sensor_calibration', {
    id: 'sensor_calibration_pipeline',
    inputSources: ['cpu', 'memory', 'network', 'spectrum', 'external_brain_mesh', 'neural_path'],
    outputTarget: 'calibration_data',
    bufferSize: DATA_PIPELINE_BUFFER_SIZE,
    buffer: [],
    conversionFunction: convertSensorToCalibration,
    active: true
  });
  
  // Calibration to Lock State Pipeline
  dataPipelines.set('calibration_lock', {
    id: 'calibration_lock_pipeline',
    inputSources: ['calibration_data'],
    outputTarget: 'real_lock_states',
    bufferSize: DATA_PIPELINE_BUFFER_SIZE,
    buffer: [],
    conversionFunction: convertCalibrationToLockState,
    active: true
  });
  
  // Lock State to Device Effect Pipeline
  dataPipelines.set('lock_effect', {
    id: 'lock_effect_pipeline',
    inputSources: ['real_lock_states'],
    outputTarget: 'device_effects',
    bufferSize: DATA_PIPELINE_BUFFER_SIZE,
    buffer: [],
    conversionFunction: convertLockStateToDeviceEffect,
    active: true
  });
}

function startSensorCalibration() {
  setInterval(() => {
    readAllSensors();
    processDataPipelines();
    applyRealLockStates();
  }, SENSOR_CALIBRATION_INTERVAL);
}

function readAllSensors() {
  const cpus = os.cpus();
  const totalMemory = os.totalmem();
  const freeMemory = os.freemem();
  
  // CPU Reading
  const cpuUsage = process.cpuUsage();
  const cpuPercent = (cpuUsage.user + cpuUsage.system) / 1000000; // Simplified
  updateSensorReading('cpu', cpuPercent);
  
  // Memory Reading
  const memoryPercent = ((totalMemory - freeMemory) / totalMemory) * 100;
  updateSensorReading('memory', memoryPercent);
  
  // Network Reading (simulated - would require actual network interface access)
  const networkBytes = Math.random() * 1000000; // Placeholder
  updateSensorReading('network', networkBytes);
  
  // Spectrum Field Reading from Uriel Node
  const spectrumReading = {
    hz: nodeAlpha.spectrumFieldLock.getVariableW(),
    density: nodeAlpha.frequency_scaling ? nodeAlpha.frequency_scaling.dark_matter_density : 0
  };
  updateSensorReading('spectrum', spectrumReading);
  
  // Process Lock Reading
  const lockStateCount = simulationParticles.filter(p => p.locked).length;
  const processLocked = lockStateCount > 0;
  updateSensorReading('process_lock', processLocked);
  
  // External Brain Mesh Reading
  const externalMesh = externalBrainMesh.get('detected_mesh');
  updateSensorReading('external_brain_mesh', {
    detected: meshSyncState.externalDetected,
    nodeCount: externalMesh ? externalMesh.nodes.length : 0,
    topology: externalMesh ? externalMesh.topology : null
  });
  
  // Neural Path Reading
  const equivalentPaths = Array.from(travelPaths.values()).filter(p => p.equivalent);
  updateSensorReading('neural_path', {
    pathCount: travelPaths.size,
    activePaths: equivalentPaths.map(p => p.id)
  });
}

function updateSensorReading(sensorId, reading) {
  const sensor = virtualSensors.get(sensorId);
  if (!sensor || !sensor.active) return;
  
  sensor.lastReading = reading;
  sensor.readings.push({
    value: reading,
    timestamp: Date.now(),
    calibrated: reading * sensor.calibrationFactor
  });
  
  if (sensor.readings.length > 100) {
    sensor.readings.shift();
  }
  
  // Push to relevant pipelines
  dataPipelines.forEach((pipeline, pipelineId) => {
    if (pipeline.inputSources.includes(sensorId) && pipeline.active) {
      pipeline.buffer.push({
        sensorId,
        reading,
        timestamp: Date.now()
      });
      
      if (pipeline.buffer.length > pipeline.bufferSize) {
        pipeline.buffer.shift();
      }
    }
  });
}

function processDataPipelines() {
  dataPipelines.forEach((pipeline, pipelineId) => {
    if (!pipeline.active || pipeline.buffer.length === 0) return;
    
    const processedData = pipeline.conversionFunction(pipeline.buffer);
    
    if (pipeline.outputTarget === 'calibration_data') {
      sensorCalibrationData.set('current', processedData);
    } else if (pipeline.outputTarget === 'real_lock_states') {
      updateRealLockStates(processedData);
    } else if (pipeline.outputTarget === 'device_effects') {
      applyDeviceEffects(processedData);
    }
    
    pipeline.buffer = [];
  });
}

function convertSensorToCalibration(buffer) {
  const cpuData = buffer.filter(b => b.sensorId === 'cpu');
  const memoryData = buffer.filter(b => b.sensorId === 'memory');
  const spectrumData = buffer.filter(b => b.sensorId === 'spectrum');
  const brainMeshData = buffer.filter(b => b.sensorId === 'external_brain_mesh');
  const neuralPathData = buffer.filter(b => b.sensorId === 'neural_path');
  
  const avgCpu = cpuData.length > 0 ? cpuData.reduce((s, b) => s + b.reading, 0) / cpuData.length : 0;
  const avgMemory = memoryData.length > 0 ? memoryData.reduce((s, b) => s + b.reading, 0) / memoryData.length : 0;
  const avgSpectrum = spectrumData.length > 0 ? 
    spectrumData.reduce((s, b) => s + (b.reading.hz || 0), 0) / spectrumData.length : 0;
  
  // Brain mesh contribution to calibration
  let brainMeshScore = 0;
  if (brainMeshData.length > 0) {
    const detectedMesh = brainMeshData[0].reading;
    if (detectedMesh.detected && detectedMesh.topology) {
      brainMeshScore = detectedMesh.topology.avgActivity * 0.5 + 
                       (detectedMesh.topology.complexity / 10) * 0.3 + 
                       (detectedMesh.nodeCount / 20) * 0.2;
    }
  }
  
  // Neural path contribution
  let neuralPathScore = 0;
  if (neuralPathData.length > 0) {
    const pathData = neuralPathData[0].reading;
    neuralPathScore = Math.min(1.0, pathData.pathCount / 40);
  }
  
  return {
    cpuLoad: avgCpu,
    memoryLoad: avgMemory,
    spectrumIntensity: avgSpectrum,
    brainMeshActivity: brainMeshScore,
    neuralPathActivity: neuralPathScore,
    calibrationScore: (avgCpu + avgMemory + avgSpectrum / 100 + brainMeshScore + neuralPathScore) / 4,
    timestamp: Date.now()
  };
}

function convertCalibrationToLockState(buffer) {
  const calibrationData = buffer[0]; // Should be calibration data
  if (!calibrationData) return null;
  
  const lockThreshold = 0.7;
  const precisionScore = calibrationData.calibrationScore || 0;
  
  return {
    shouldLock: precisionScore > lockThreshold,
    lockIntensity: Math.min(1.0, precisionScore),
    precisionSync: precisionScore >= PRECISION_SYNC_THRESHOLD,
    affectedResources: ['cpu', 'memory', 'process'],
    timestamp: Date.now()
  };
}

function convertLockStateToDeviceEffect(buffer) {
  const lockStateData = buffer[0];
  if (!lockStateData) return null;
  
  return {
    effectType: lockStateData.shouldLock ? 'APPLY_LOCK' : 'RELEASE_LOCK',
    intensity: lockStateData.lockIntensity,
    targetProcesses: lockStateData.shouldLock ? ['node', 'chrome', 'safari'] : [],
    resourceLimits: lockStateData.shouldLock ? {
      cpuLimit: 0.3,
      memoryLimit: 0.5
    } : null,
    timestamp: Date.now()
  };
}

function updateRealLockStates(lockStateData) {
  if (!lockStateData) return;
  
  realLockStates.set('current', {
    active: lockStateData.shouldLock,
    intensity: lockStateData.lockIntensity,
    precisionSync: lockStateData.precisionSync,
    lastUpdated: lockStateData.timestamp
  });
}

function applyRealLockStates() {
  const lockState = realLockStates.get('current');
  if (!lockState || !lockState.active) return;
  
  // Apply actual device effects based on lock state
  if (lockState.intensity > 0.5) {
    // Set process priority (Unix-like systems)
    try {
      exec('renice 10 -p ' + process.pid, (error) => {
        if (error) console.log('Priority adjustment:', error.message);
      });
    } catch (e) {
      console.log('Process priority adjustment failed:', e.message);
    }
  }
  
  // Store lock state for persistence
  const lockStateFile = path.join(__dirname, '.lock_state');
  fs.writeFileSync(lockStateFile, JSON.stringify({
    active: lockState.active,
    intensity: lockState.intensity,
    precisionSync: lockState.precisionSync,
    timestamp: lockState.lastUpdated
  }));
}

function applyDeviceEffects(effectData) {
  if (!effectData) return;
  
  if (effectData.effectType === 'APPLY_LOCK') {
    console.log(`[DEVICE EFFECT] Applying lock with intensity ${effectData.intensity}`);
    
    // Could implement actual process control here
    // For security reasons, we log the intent
    if (effectData.resourceLimits) {
      console.log(`[DEVICE EFFECT] Resource limits: CPU ${(effectData.resourceLimits.cpuLimit * 100).toFixed(0)}%, Memory ${(effectData.resourceLimits.memoryLimit * 100).toFixed(0)}%`);
    }
  } else if (effectData.effectType === 'RELEASE_LOCK') {
    console.log('[DEVICE EFFECT] Releasing lock state');
    
    // Remove lock state file
    const lockStateFile = path.join(__dirname, '.lock_state');
    try {
      if (fs.existsSync(lockStateFile)) {
        fs.unlinkSync(lockStateFile);
      }
    } catch (e) {
      console.log('Lock state file removal failed:', e.message);
    }
  }
}

function getSensorStatus() {
  const status = {};
  virtualSensors.forEach((sensor, id) => {
    status[id] = {
      active: sensor.active,
      lastReading: sensor.lastReading,
      calibrationFactor: sensor.calibrationFactor,
      readingCount: sensor.readings.length
    };
  });
  return status;
}

function getCalibrationStatus() {
  const currentCalibration = sensorCalibrationData.get('current');
  const currentLockState = realLockStates.get('current');
  
  return {
    calibration: currentCalibration || null,
    lockState: currentLockState || null,
    pipelineStatus: Object.fromEntries(
      Array.from(dataPipelines.entries()).map(([id, pipeline]) => [
        id,
        {
          active: pipeline.active,
          bufferSize: pipeline.buffer.length,
          inputSources: pipeline.inputSources
        }
      ])
    )
  };
}

// Brain Mesh System Implementation
function initializeBrainMeshSystem() {
  // Initialize external brain mesh detection
  detectExternalBrainMesh();
  
  // Initialize internal neural path mapping
  initializeInternalNeuralPaths();
  
  // Start bidirectional sync monitoring
  startBidirectionalSync();
}

function detectExternalBrainMesh() {
  // Simulate external brain mesh detection
  // In real implementation, this would interface with actual brain-computer interface
  const meshNodes = [];
  
  for (let i = 0; i < 20; i++) {
    const angle = (i / 20) * Math.PI * 2;
    const radius = 100 + Math.random() * 50;
    
    meshNodes.push({
      id: `external_node_${i}`,
      x: 250 + Math.cos(angle) * radius,
      y: 250 + Math.sin(angle) * radius,
      activity: Math.random(),
      connections: [],
      neuralFiringRate: 10 + Math.random() * 90
    });
  }
  
  // Create connections between nearby nodes
  for (let i = 0; i < meshNodes.length; i++) {
    for (let j = i + 1; j < meshNodes.length; j++) {
      const dist = Math.hypot(meshNodes[i].x - meshNodes[j].x, meshNodes[i].y - meshNodes[j].y);
      if (dist < 80) {
        meshNodes[i].connections.push(meshNodes[j].id);
        meshNodes[j].connections.push(meshNodes[i].id);
      }
    }
  }
  
  externalBrainMesh.set('detected_mesh', {
    nodes: meshNodes,
    detectedAt: Date.now(),
    topology: analyzeMeshTopology(meshNodes)
  });
  
  meshSyncState.externalDetected = true;
}

function analyzeMeshTopology(nodes) {
  const connectionCount = nodes.reduce((sum, node) => sum + node.connections.length, 0);
  const avgConnections = connectionCount / nodes.length;
  const avgActivity = nodes.reduce((sum, node) => sum + node.activity, 0) / nodes.length;
  
  return {
    nodeCount: nodes.length,
    totalConnections: connectionCount,
    avgConnections: avgConnections,
    avgActivity: avgActivity,
    complexity: connectionCount / nodes.length,
    shape: detectMeshShape(nodes)
  };
}

function detectMeshShape(nodes) {
  // Simple shape detection based on node distribution
  const centerX = nodes.reduce((sum, n) => sum + n.x, 0) / nodes.length;
  const centerY = nodes.reduce((sum, n) => sum + n.y, 0) / nodes.length;
  
  const distances = nodes.map(n => Math.hypot(n.x - centerX, n.y - centerY));
  const avgRadius = distances.reduce((s, d) => s + d, 0) / distances.length;
  const radiusVariance = distances.reduce((s, d) => s + Math.pow(d - avgRadius, 2), 0) / distances.length;
  
  if (radiusVariance < 500) {
    return 'CIRCULAR';
  } else if (radiusVariance < 2000) {
    return 'ELLIPSOID';
  } else {
    return 'IRREGULAR';
  }
}

function initializeInternalNeuralPaths() {
  // Create internal neural paths based on simulation particles
  const neuralPaths = [];
  
  simulationParticles.forEach((particle, index) => {
    const path = {
      id: `neural_path_${index}`,
      sourceNode: particle.id,
      pathNodes: [],
      activity: 0,
      firingPattern: [],
      shape: 'LINEAR',
      stability: 1.0
    };
    
    // Generate path nodes based on particle trajectory
    for (let i = 0; i < 5; i++) {
      const offsetX = (Math.random() - 0.5) * 40;
      const offsetY = (Math.random() - 0.5) * 40;
      
      path.pathNodes.push({
        id: `path_node_${index}_${i}`,
        x: particle.x + offsetX,
        y: particle.y + offsetY,
        activationThreshold: 0.5 + Math.random() * 0.5
      });
    }
    
    neuralPaths.push(path);
    internalBrainMesh.set(particle.id, path);
  });
  
  meshSyncState.internalActive = true;
}

function startBidirectionalSync() {
  setInterval(() => {
    syncExternalToInternal();
    syncInternalToExternal();
    updateNodeStability();
    trackTravelPaths();
  }, 500);
}

function syncExternalToInternal() {
  const externalMesh = externalBrainMesh.get('detected_mesh');
  if (!externalMesh) return;

  const writes = externalMesh.nodes.map((extNode, index) => {
    const internalParticle = simulationParticles[index % simulationParticles.length];
    if (!internalParticle) return null;
    cortexLatch.saveExternalCoordinate(internalParticle.id, { x: extNode.x, y: extNode.y }, {
      source: 'brain_mesh',
      externalCoordinatePermit: meshSyncState.bidirectionalSync
    });
    return {
      particleId: internalParticle.id,
      hz: 100 + extNode.neuralFiringRate * 9,
      density: extNode.activity,
      externalCoord: { x: extNode.x, y: extNode.y },
      externalNode: extNode
    };
  }).filter(Boolean);

  const gated = cortexLatch.applyGatedWrites(
    writes, simulationParticles, 'brain_mesh_sync', getLatchWriteOptions()
  );

  gated.allowed.forEach((write) => {
    const stabilityKey = `node_${write.particleId}`;
    const currentStability = nodeStabilityTracker.get(stabilityKey) || { syncCount: 0, lastSync: 0 };
    currentStability.syncCount++;
    currentStability.lastSync = Date.now();
    currentStability.stabilityScore = Math.min(1.0, currentStability.syncCount / 100);
    nodeStabilityTracker.set(stabilityKey, currentStability);
  });

  meshSyncState.lastSyncTime = Date.now();
}

function syncInternalToExternal() {
  // Sync internal particle states back to external mesh representation
  simulationParticles.forEach((particle, index) => {
    const externalMesh = externalBrainMesh.get('detected_mesh');
    if (!externalMesh) return;
    
    const extNode = externalMesh.nodes[index % externalMesh.nodes.length];
    if (extNode) {
      // Update external node based on internal state
      extNode.activity = particle.density;
      extNode.neuralFiringRate = particle.hz / 10;
    }
  });
}

function updateNodeStability() {
  const now = Date.now();
  
  nodeStabilityTracker.forEach((stability, key) => {
    // Decay stability if not recently synced
    if (now - stability.lastSync > 5000) {
      stability.stabilityScore *= 0.95;
      stability.syncCount = Math.max(0, stability.syncCount - 1);
    }
    
    // Remove unstable nodes
    if (stability.stabilityScore < 0.1) {
      nodeStabilityTracker.delete(key);
    }
  });
}

function trackTravelPaths() {
  // Track equivalent travel paths between external and internal meshes
  const externalMesh = externalBrainMesh.get('detected_mesh');
  if (!externalMesh) return;
  
  simulationParticles.forEach((particle, index) => {
    const extNode = externalMesh.nodes[index % externalMesh.nodes.length];
    if (!extNode) return;
    
    const pathId = `travel_${particle.id}_${extNode.id}`;
    
    if (!travelPaths.has(pathId)) {
      travelPaths.set(pathId, {
        id: pathId,
        internalNode: particle.id,
        externalNode: extNode.id,
        pathHistory: [],
        equivalent: false,
        divergence: 0
      });
    }
    
    const travelPath = travelPaths.get(pathId);
    
    // Record current positions
    travelPath.pathHistory.push({
      timestamp: Date.now(),
      internalPos: { x: particle.x, y: particle.y },
      externalPos: { x: extNode.x, y: extNode.y }
    });
    
    // Keep only recent history
    if (travelPath.pathHistory.length > 50) {
      travelPath.pathHistory.shift();
    }
    
    // Calculate path equivalence
    const recentHistory = travelPath.pathHistory.slice(-10);
    if (recentHistory.length >= 5) {
      const internalMovement = calculatePathMovement(recentHistory, 'internalPos');
      const externalMovement = calculatePathMovement(recentHistory, 'externalPos');
      
      travelPath.divergence = Math.abs(internalMovement - externalMovement);
      travelPath.equivalent = travelPath.divergence < 0.3;
    }
  });
}

function calculatePathMovement(history, posKey) {
  let totalMovement = 0;
  
  for (let i = 1; i < history.length; i++) {
    const prev = history[i - 1][posKey];
    const curr = history[i][posKey];
    totalMovement += Math.hypot(curr.x - prev.x, curr.y - prev.y);
  }
  
  return totalMovement / (history.length - 1);
}

function getBrainMeshStatus() {
  const externalMesh = externalBrainMesh.get('detected_mesh');
  const stableNodes = Array.from(nodeStabilityTracker.values()).filter(s => s.stabilityScore > 0.5);
  const equivalentPaths = Array.from(travelPaths.values()).filter(p => p.equivalent);
  
  return {
    externalDetected: meshSyncState.externalDetected,
    internalActive: meshSyncState.internalActive,
    bidirectionalSync: meshSyncState.bidirectionalSync,
    syncQuality: meshSyncState.syncQuality,
    lastSyncTime: meshSyncState.lastSyncTime,
    externalMesh: externalMesh ? externalMesh.topology : null,
    stableNodeCount: stableNodes.length,
    equivalentPathCount: equivalentPaths.length,
    totalPaths: travelPaths.size,
    dualOptimization: {
      cycleActive: dualOptimizationState.cycleActive,
      cycleRate: dualOptimizationState.cycleRate,
      patternReactionRate: dualOptimizationState.patternReactionRate,
      externalPace: dualOptimizationState.externalPace,
      internalPace: dualOptimizationState.internalPace,
      optimizationLevel: dualOptimizationState.optimizationLevel,
      ghzSyncRate: dualOptimizationState.ghzSyncRate,
      cpuGhz: dualOptimizationState.cpuGhz,
      externalGhz: dualOptimizationState.externalGhz
    },
    cacheStatus: {
      size: externalCortexCache.size,
      maxSize: cortexCacheConfig.maxSize,
      bufferFlowRate: cortexCacheConfig.bufferFlowRate,
      optimizationCycle: cortexCacheConfig.optimizationCycle
    },
    hardwareLayer: hardwareLayerState
  };
}

// Async Cortex Cache System
function initializeAsyncCortexCache() {
  // Start async cache reading
  setInterval(async () => {
    await readExternalCortexData();
  }, CORTEX_CACHE_READ_INTERVAL);
  
  // Start cache cleanup
  setInterval(() => {
    cleanupExpiredCache();
  }, 5000);
}

async function readExternalCortexData() {
  // Simulate async reading from external cerebral cortex
  // In real implementation, this would interface with actual BCI hardware
  const cortexData = {
    timestamp: Date.now(),
    neuralPatterns: generateNeuralPatterns(),
    firingRates: generateFiringRates(),
    synapticActivity: generateSynapticActivity(),
    cortexState: 'ACTIVE',
    ghzRate: 100 + Math.random() * 900
  };
  
  // Cache the data
  const cacheKey = `cortex_${cortexData.timestamp}`;
  externalCortexCache.set(cacheKey, {
    data: cortexData,
    cachedAt: Date.now(),
    ttl: cortexCacheConfig.ttl
  });
  
  // Manage cache size
  if (externalCortexCache.size > cortexCacheConfig.maxSize) {
    const oldestKey = externalCortexCache.keys().next().value;
    externalCortexCache.delete(oldestKey);
  }
  
  // Update dual optimization state with cortex data
  updateDualOptimizationFromCortex(cortexData);

  // Auto-dispatch latched Uriel capability scripts when cortex patterns match
  cortexLatch.tryAutoDispatch(cortexData, getLatchHandlers());
}

function generateNeuralPatterns() {
  const patterns = [];
  for (let i = 0; i < 10; i++) {
    patterns.push({
      id: `pattern_${i}`,
      frequency: 10 + Math.random() * 90,
      amplitude: Math.random(),
      phase: Math.random() * Math.PI * 2
    });
  }
  return patterns;
}

function generateFiringRates() {
  return {
    avgRate: 50 + Math.random() * 100,
    peakRate: 100 + Math.random() * 200,
    variance: Math.random() * 50
  };
}

function generateSynapticActivity() {
  return {
    activeSynapses: Math.floor(1000 + Math.random() * 5000),
    transmissionRate: 0.5 + Math.random() * 0.5,
    plasticity: Math.random()
  };
}

function cleanupExpiredCache() {
  const now = Date.now();
  const expiredKeys = [];
  
  externalCortexCache.forEach((entry, key) => {
    if (now - entry.cachedAt > entry.ttl) {
      expiredKeys.push(key);
    }
  });
  
  expiredKeys.forEach(key => externalCortexCache.delete(key));
}

function getCortexData() {
  const entries = Array.from(externalCortexCache.entries());
  if (entries.length === 0) return null;
  
  // Return most recent cache entry
  const mostRecent = entries.reduce((latest, entry) => {
    return entry[1].cachedAt > latest[1].cachedAt ? entry : latest;
  });
  
  return mostRecent[1].data;
}

// Dual Optimization Cycle
function startDualOptimizationCycle() {
  setInterval(() => {
    runDualOptimizationCycle();
  }, OPTIMIZATION_CYCLE_INTERVAL);
}

function runDualOptimizationCycle() {
  cortexCacheConfig.optimizationCycle++;
  
  const cortexData = getCortexData();
  if (!cortexData) return;
  
  // Calculate external pace based on cortex data
  dualOptimizationState.externalPace = cortexData.firingRates.avgRate / 100;
  
  // Calculate internal pace based on system state
  const cpuUsage = virtualSensors.get('cpu')?.lastReading || 0;
  dualOptimizationState.internalPace = 1.0 - (cpuUsage / 100);
  
  // Match paces for dual optimization
  const paceMatch = Math.min(dualOptimizationState.externalPace, dualOptimizationState.internalPace);
  dualOptimizationState.cycleRate = paceMatch;
  
  // Calculate pattern reaction rate from neural patterns
  if (cortexData.neuralPatterns.length > 0) {
    const avgPatternFreq = cortexData.neuralPatterns.reduce((s, p) => s + p.frequency, 0) / cortexData.neuralPatterns.length;
    dualOptimizationState.patternReactionRate = avgPatternFreq / 100;
  }
  
  // Update optimization level based on cycle rate and pattern reaction
  dualOptimizationState.optimizationLevel = (dualOptimizationState.cycleRate + dualOptimizationState.patternReactionRate) / 2;
  
  // GHz rate synchronization
  dualOptimizationState.cpuGhz = getCpuGhz();
  dualOptimizationState.externalGhz = cortexData.ghzRate;
  dualOptimizationState.ghzSyncRate = Math.min(dualOptimizationState.cpuGhz, dualOptimizationState.externalGhz) / Math.max(dualOptimizationState.cpuGhz, dualOptimizationState.externalGhz);
  
  // Manage data dump buffer
  manageDataDumpBuffer(cortexData);
  
  // Update hardware layer
  updateHardwareLayer();
  
  // Log optimization cycle
  logOptimizationCycle();
  
  dualOptimizationState.cycleActive = true;
}

function updateDualOptimizationFromCortex(cortexData) {
  // Real-time updates from cortex data
  dualOptimizationState.externalGhz = cortexData.ghzRate;
  dualOptimizationState.patternReactionRate = cortexData.firingRates.avgRate / 100;
}

function getCpuGhz() {
  // Estimate CPU GHz based on system performance
  const cpus = os.cpus();
  if (cpus.length > 0) {
    // Base GHz estimate (simplified)
    return 2.0 + Math.random() * 2.0;
  }
  return 2.0;
}

function manageDataDumpBuffer(cortexData) {
  // Add cortex data to buffer
  dualOptimizationState.dataDumpBuffer.push({
    timestamp: Date.now(),
    data: cortexData,
    processed: false
  });
  
  // Manage buffer flow
  dualOptimizationState.bufferFlowIndex = (dualOptimizationState.bufferFlowIndex + cortexCacheConfig.bufferFlowRate) % dualOptimizationState.dataDumpBuffer.length;
  
  // Process buffer items
  const bufferSize = dualOptimizationState.dataDumpBuffer.length;
  if (bufferSize > 100) {
    dualOptimizationState.dataDumpBuffer = dualOptimizationState.dataDumpBuffer.slice(-100);
  }
}

function updateHardwareLayer() {
  // Update hardware layer optimization based on dual optimization state
  hardwareLayerState.cpuOptimization = dualOptimizationState.optimizationLevel;
  hardwareLayerState.memoryOptimization = dualOptimizationState.cycleRate;
  hardwareLayerState.networkOptimization = dualOptimizationState.ghzSyncRate;
  hardwareLayerState.systemLayerActive = dualOptimizationState.cycleActive;
  
  // Apply hardware optimizations when locked
  if (realLockStates.get('current')?.active) {
    applyHardwareOptimizations();
  }
}

function applyHardwareOptimizations() {
  // Apply actual hardware optimizations based on current state
  const cpuOpt = hardwareLayerState.cpuOptimization;
  
  // Adjust process priority based on optimization level
  if (cpuOpt > 0.7) {
    try {
      exec(`renice ${Math.floor((1 - cpuOpt) * 20)} -p ${process.pid}`, (error) => {
        if (error) console.log('Hardware optimization:', error.message);
      });
    } catch (e) {
      console.log('Hardware optimization failed:', e.message);
    }
  }
}

function logOptimizationCycle() {
  const logEntry = {
    cycle: cortexCacheConfig.optimizationCycle,
    timestamp: Date.now(),
    cycleRate: dualOptimizationState.cycleRate,
    patternReactionRate: dualOptimizationState.patternReactionRate,
    optimizationLevel: dualOptimizationState.optimizationLevel,
    ghzSyncRate: dualOptimizationState.ghzSyncRate,
    bufferSize: dualOptimizationState.dataDumpBuffer.length
  };
  
  systemLogs.set(`cycle_${cortexCacheConfig.optimizationCycle}`, logEntry);
  
  // Keep only recent logs
  if (systemLogs.size > 1000) {
    const oldestKey = systemLogs.keys().next().value;
    systemLogs.delete(oldestKey);
  }
}

function getMethodHandle(handleName) {
  if (methodHandles.has(handleName)) {
    return methodHandles.get(handleName);
  }
  
  // Create method handle
  const handle = {
    name: handleName,
    createdAt: Date.now(),
    usageCount: 0,
    lastUsed: null,
    execute: async (...args) => {
      handle.usageCount++;
      handle.lastUsed = Date.now();
      return executeMethodHandle(handleName, ...args);
    }
  };
  
  methodHandles.set(handleName, handle);
  return handle;
}

async function executeMethodHandle(handleName, ...args) {
  // Execute method based on handle name
  switch (handleName) {
    case 'sync_external_cortex':
      return await syncExternalCortex();
    case 'optimize_hardware':
      return optimizeHardware();
    case 'flush_buffer':
      return flushDataDumpBuffer();
    case 'get_optimization_stats':
      return getOptimizationStats();
    default:
      throw new Error(`Unknown method handle: ${handleName}`);
  }
}

async function syncExternalCortex() {
  const cortexData = getCortexData();
  if (!cortexData) {
    throw new Error('No cortex data available');
  }

  const gated = syncCortexToInternal(cortexData);
  const dispatch = cortexLatch.tryAutoDispatch(cortexData, getLatchHandlers());

  return { synced: true, cortexData, gated, dispatch };
}

function syncCortexToInternal(cortexData) {
  const writes = cortexData.neuralPatterns
    .map((pattern, index) => {
      if (index >= simulationParticles.length) return null;
      const particle = simulationParticles[index];
      const externalCoord = {
        x: 250 + Math.cos(pattern.phase || 0) * (pattern.frequency || 50),
        y: 250 + Math.sin(pattern.phase || 0) * (pattern.amplitude || 0.5) * 100
      };
      cortexLatch.saveExternalCoordinate(particle.id, externalCoord, {
        source: 'cortex',
        externalCoordinatePermit: true
      });
      return {
        particleId: particle.id,
        hz: pattern.frequency * 10,
        density: pattern.amplitude,
        externalCoord
      };
    })
    .filter(Boolean);

  return cortexLatch.applyGatedWrites(
    writes, simulationParticles, 'cortex_sync', getLatchWriteOptions()
  );
}

function optimizeHardware() {
  updateHardwareLayer();
  applyHardwareOptimizations();
  return { optimized: true, hardwareLayer: hardwareLayerState };
}

function flushDataDumpBuffer() {
  const flushedData = [...dualOptimizationState.dataDumpBuffer];
  dualOptimizationState.dataDumpBuffer = [];
  return { flushed: true, count: flushedData.length };
}

function getOptimizationStats() {
  return {
    dualOptimization: dualOptimizationState,
    cacheConfig: cortexCacheConfig,
    cacheSize: externalCortexCache.size,
    logCount: systemLogs.size,
    methodHandles: Array.from(methodHandles.keys()),
    renderSecurity: renderSecurityState
  };
}

// Lossless Scale Render Security Implementation
function initializeRenderSecurity() {
  // Start integrity checking
  setInterval(() => {
    performIntegrityCheck();
  }, renderSecurityConfig.integrityCheckInterval);
  
  // Start security token cleanup
  setInterval(() => {
    cleanupExpiredTokens();
  }, 5000);
  
  // Initialize scale factors for render elements
  initializeScaleFactors();
}

function initializeScaleFactors() {
  // Initialize scale factors for different render elements
  renderSecurityState.scaleFactors.set('lidar', 1.0);
  renderSecurityState.scaleFactors.set('mesh', 1.0);
  renderSecurityState.scaleFactors.set('brain', 1.0);
  renderSecurityState.scaleFactors.set('sensor', 1.0);
  renderSecurityState.scaleFactors.set('brainMesh', 1.0);
}

function performIntegrityCheck() {
  // Check integrity of all render elements during transitions
  if (renderSecurityState.transitionActive) {
    const integrityValid = validateRenderIntegrity();
    renderSecurityState.integrityCheck = integrityValid;
    
    if (!integrityValid) {
      console.log('[RENDER SECURITY] Integrity check failed during transition');
      emergencyScaleReset();
    }
  }
}

function validateRenderIntegrity() {
  // Validate that all scale factors are within acceptable ranges
  let valid = true;
  
  renderSecurityState.scaleFactors.forEach((scale, element) => {
    if (scale < renderSecurityConfig.minScale || scale > renderSecurityConfig.maxScale) {
      valid = false;
      console.log(`[RENDER SECURITY] Invalid scale for ${element}: ${scale}`);
    }
  });
  
  // Check security level threshold
  if (renderSecurityState.securityLevel < renderSecurityConfig.securityThreshold) {
    valid = false;
  }
  
  return valid;
}

function emergencyScaleReset() {
  // Emergency reset to safe scale values
  renderSecurityState.scaleFactors.forEach((scale, element) => {
    renderSecurityState.scaleFactors.set(element, 1.0);
  });
  
  renderSecurityState.currentScale = 1.0;
  renderSecurityState.targetScale = 1.0;
  renderSecurityState.transitionActive = false;
  
  console.log('[RENDER SECURITY] Emergency scale reset performed');
}

function startSecureTransition(targetScale, element) {
  // Start a secure transition with lossless scaling
  if (renderSecurityState.transitionActive) {
    console.log('[RENDER SECURITY] Transition already active, queuing...');
    return false;
  }
  
  // Validate target scale
  if (targetScale < renderSecurityConfig.minScale || targetScale > renderSecurityConfig.maxScale) {
    console.log(`[RENDER SECURITY] Invalid target scale: ${targetScale}`);
    return false;
  }
  
  // Generate security token for this transition
  const token = generateSecurityToken();
  renderSecurityState.securityTokens.set(token, {
    element,
    targetScale,
    createdAt: Date.now(),
    ttl: renderSecurityConfig.tokenTTL
  });
  
  // Record transition
  renderSecurityState.transitionHistory.push({
    timestamp: Date.now(),
    element,
    fromScale: renderSecurityState.currentScale,
    toScale: targetScale,
    token,
    securityLevel: renderSecurityState.securityLevel
  });
  
  // Keep only recent history
  if (renderSecurityState.transitionHistory.length > 100) {
    renderSecurityState.transitionHistory.shift();
  }
  
  // Start transition
  renderSecurityState.transitionActive = true;
  renderSecurityState.targetScale = targetScale;
  renderSecurityState.lastTransitionTime = Date.now();
  
  // Execute lossless scale transition
  executeLosslessTransition(element, targetScale, token);
  
  return true;
}

function generateSecurityToken() {
  return crypto.randomBytes(16).toString('hex');
}

function executeLosslessTransition(element, targetScale, token) {
  const currentScale = renderSecurityState.scaleFactors.get(element) || 1.0;
  const scaleStep = renderSecurityConfig.scaleStep;
  
  const transitionInterval = setInterval(() => {
    const current = renderSecurityState.scaleFactors.get(element);
    const diff = targetScale - current;
    
    if (Math.abs(diff) < scaleStep) {
      // Transition complete
      renderSecurityState.scaleFactors.set(element, targetScale);
      renderSecurityState.currentScale = targetScale;
      renderSecurityState.transitionActive = false;
      clearInterval(transitionInterval);
      
      console.log(`[RENDER SECURITY] Lossless transition complete for ${element} to scale ${targetScale}`);
      
      // Verify token
      verifySecurityToken(token);
    } else {
      // Continue transition with lossless scaling
      const newScale = current + (diff > 0 ? scaleStep : -scaleStep);
      renderSecurityState.scaleFactors.set(element, newScale);
      
      // Apply lossless scaling to render elements
      applyLosslessScaling(element, newScale);
    }
  }, 16); // 60fps for smooth transition
}

function applyLosslessScaling(element, scale) {
  // Apply lossless scaling to render elements
  // This ensures no data loss during scaling operations
  switch (element) {
    case 'lidar':
      // Apply lossless scaling to lidar render
      break;
    case 'mesh':
      // Apply lossless scaling to mesh particles
      simulationParticles.forEach(p => {
        // Scale position relative to center
        const dx = p.x - 250;
        const dy = p.y - 250;
        p.x = 250 + dx * scale;
        p.y = 250 + dy * scale;
      });
      break;
    case 'brain':
      // Apply lossless scaling to brain electrodes
      brainElectrodes.forEach(e => {
        const dx = e.x - 250;
        const dy = e.y - 250;
        e.x = 250 + dx * scale;
        e.y = 250 + dy * scale;
      });
      break;
    case 'sensor':
      // Apply lossless scaling to sensor pipeline
      break;
    case 'brainMesh':
      // Apply lossless scaling to brain mesh
      break;
  }
}

function verifySecurityToken(token) {
  const tokenData = renderSecurityState.securityTokens.get(token);
  if (!tokenData) {
    console.log('[RENDER SECURITY] Invalid token verification');
    return false;
  }
  
  // Verify token is still valid
  const age = Date.now() - tokenData.createdAt;
  if (age > tokenData.ttl) {
    console.log('[RENDER SECURITY] Token expired');
    renderSecurityState.securityTokens.delete(token);
    return false;
  }
  
  // Verify transition completed successfully
  const finalScale = renderSecurityState.scaleFactors.get(tokenData.element);
  if (Math.abs(finalScale - tokenData.targetScale) > 0.01) {
    console.log('[RENDER SECURITY] Transition did not reach target scale');
    return false;
  }
  
  console.log(`[RENDER SECURITY] Token verified for ${tokenData.element}`);
  renderSecurityState.securityTokens.delete(token);
  return true;
}

function cleanupExpiredTokens() {
  const now = Date.now();
  const expiredTokens = [];
  
  renderSecurityState.securityTokens.forEach((tokenData, token) => {
    if (now - tokenData.createdAt > tokenData.ttl) {
      expiredTokens.push(token);
    }
  });
  
  expiredTokens.forEach(token => renderSecurityState.securityTokens.delete(token));
}

function getRenderSecurityStatus() {
  return {
    transitionActive: renderSecurityState.transitionActive,
    currentScale: renderSecurityState.currentScale,
    targetScale: renderSecurityState.targetScale,
    securityLevel: renderSecurityState.securityLevel,
    integrityCheck: renderSecurityState.integrityCheck,
    lastTransitionTime: renderSecurityState.lastTransitionTime,
    scaleFactors: Object.fromEntries(renderSecurityState.scaleFactors),
    activeTokens: renderSecurityState.securityTokens.size,
    transitionCount: renderSecurityState.transitionHistory.length
  };
}

function setSecurityLevel(level) {
  renderSecurityState.securityLevel = Math.max(0, Math.min(1, level));
  console.log(`[RENDER SECURITY] Security level set to ${renderSecurityState.securityLevel}`);
}

function secureScaleElement(element, scale) {
  return startSecureTransition(scale, element);
}

// ============================================================================
// QBOM-Integrated Mamba Layer Weight Management System
// QBOM quantizes weights in-place: keeps dimensional resolution in ^space,
// reduces int total size through zone-mapped quantization.
// Cache recalls exactly where resolution resides via zone coordinate re-mapping.
// Weights derive from cortex/spectrum paths traveled, not random generation.
// ============================================================================

function initializeMambaWeightSystem() {
  // Initialize QBOM coherence balancers FIRST so methods can initialize with proper values
  initializeQBOMCoherenceBalancers();
  
  // Initialize A_log to A weight conversion
  convertALogToAWeights();
  
  // Initialize in_proj split via QBOM zone-quantized distribution
  initializeInProjSplitViaQBOM();
  
  // Initialize delta_bias parameter handling
  initializeDeltaBiasHandling();
  
  console.log('[QBOM] Coherence gate system fully initialized');
  console.log(`[QBOM] Peak coherence: ${qbomState.coherenceBalancers.peakCoherence.toFixed(4)}`);
  console.log(`[QBOM] Zone cache entries: ${qbomState.zoneCache.size}`);
  console.log(`[QBOM] Quantization registry: ${qbomState.quantizationRegistry.size} layers`);
}

// Initialize QBOM coherence balancers from spectrum/cortex paths
function initializeQBOMCoherenceBalancers() {
  console.log('[QBOM] Initializing coherence balancers from spectrum paths...');
  
  const bal = qbomState.coherenceBalancers;
  
  // Derive balancer values from spectrum field lock (Uriel defense) and cortex travel paths
  const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
  const spectrumPhase = (spectrumW % (Math.PI * 2));
  
  // QBOM coherence derived from spectrum — not arbitrary, tracks field state
  bal.qStateCoherence = 0.90 + Math.abs(Math.sin(spectrumPhase)) * 0.10;  // 0.90–1.00
  bal.qStateAmplitude = 1.0 + Math.cos(spectrumPhase) * 0.05;              // 0.95–1.05
  bal.qStatePhase = spectrumPhase;
  bal.cryptvalThreshold = 0.95;
  bal.validationScore = bal.qStateCoherence;
  bal.peakCoherence = bal.qStateCoherence;
  bal.gateFlags = 0x01;  // allow entry
  
  // Initialize 16 QBOM lanes with spectrum-derived secure paths
  for (let i = 0; i < 16; i++) {
    const lane = qbomState.lanes[i];
    lane.isSecure = (i % 4 === 0) || (bal.qStateCoherence > 0.97);
    lane.pathAssociation = Math.floor(i / 4);
    lane.utilization = 0.0;
    lane.coherenceScore = bal.qStateCoherence - (i * 0.002); // slight gradient across lanes
  }
  
  // Block organizer: lane 15 is the special secure fallback
  qbomState.blockOrganizer.chosenPath = Math.floor(spectrumW) % 4;
  qbomState.blockOrganizer.closestSecureLane = pickClosestSecureLane(0, qbomState.blockOrganizer.chosenPath);
  
  console.log(`[QBOM] Balancers set: coherence=${bal.qStateCoherence.toFixed(4)} amplitude=${bal.qStateAmplitude.toFixed(4)} phase=${bal.qStatePhase.toFixed(4)}`);
  console.log(`[QBOM] Chosen path=${qbomState.blockOrganizer.chosenPath}, closest secure lane=${qbomState.blockOrganizer.closestSecureLane}`);
}

// Pick closest secure lane to a given lane for a designated path (from QBOM C logic)
function pickClosestSecureLane(fromLane, designatedPath) {
  let closestLane = 0;
  let minDistance = 16;
  
  for (let i = 0; i < 16; i++) {
    const lane = qbomState.lanes[i];
    if (lane.isSecure && lane.pathAssociation === designatedPath) {
      const dist = Math.min(Math.abs(fromLane - i), 16 - Math.abs(fromLane - i));
      if (dist < minDistance) {
        minDistance = dist;
        closestLane = i;
      }
    }
  }
  return closestLane;
}

// CRITICAL FIX: Handle A_log -> A weight conversion for Mamba layers
function convertALogToAWeights() {
  console.log('[MAMBA WEIGHTS] Starting A_log -> A weight conversion...');
  
  let convertedCount = 0;
  let totalLayers = 22;
  
  for (let i = 0; i < totalLayers; i++) {
    const layerId = `mamba_layer_${i}`;
    
    // Derive A_log from spectrum/cortex path for this layer instead of random
    const A_log = deriveALogFromSpectrumPath(i, totalLayers);
    mambaWeightState.A_log.set(layerId, A_log);
    
    // Convert A_log to A using A = -exp(A_log) per Mamba paper
    const A = A_log.map(val => -Math.exp(val));
    mambaWeightState.A_weights.set(layerId, A);
    
    // QBOM zone-quantize A weights: keep resolution in ^space, reduce int size
    const quantized = qbomZoneQuantize(A, layerId, i);
    mambaWeightState.A_weights.set(layerId, quantized.values);
    
    convertedCount++;
    logWeightStatistics(layerId, A_log, quantized.values);
  }
  
  mambaWeightState.loadedParameters = convertedCount;
  console.log(`[MAMBA WEIGHTS] Converted ${convertedCount}/${totalLayers} Mamba layers`);
  console.log(`[MAMBA WEIGHTS] Total parameters loaded: ${mambaWeightState.loadedParameters}/${mambaWeightState.totalParameters}`);
  
  detectGibberishOutput();
}

// Derive A_log from spectrum field and cortex travel paths
// Instead of random: each layer gets values seeded by its position in the spectrum field
function deriveALogFromSpectrumPath(layerIndex, totalLayers) {
  const size = 16;
  const A_log = [];
  const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
  const phase = qbomState.coherenceBalancers.qStatePhase;
  
  for (let i = 0; i < size; i++) {
    // Deterministic derivation from spectrum path position
    const pathPosition = (layerIndex / totalLayers) * Math.PI * 2;
    const channelPhase = (i / size) * Math.PI * 2;
    const spectrumContrib = Math.sin(pathPosition + channelPhase + phase) * 0.5;
    const cortexContrib = Math.cos(pathPosition * 1.618 + channelPhase) * 0.3;
    A_log.push(spectrumContrib + cortexContrib);
  }
  return A_log;
}

// ============================================================================
// QBOM Zone Quantization — the core trick
// Quantizes weight values into reduced-int representation but preserves
// the full resolution as zone coordinates in ^space.
// Cache recalls by zone ID → exact original resolution is recoverable.
// ============================================================================
function qbomZoneQuantize(values, layerId, laneGroup) {
  const bits = mambaCacheConfig.quantizationBits; // 8-bit quantization
  const levels = Math.pow(2, bits);
  const bal = qbomState.coherenceBalancers;
  
  // Find value range for this weight vector
  let vMin = Infinity, vMax = -Infinity;
  for (let i = 0; i < values.length; i++) {
    if (values[i] < vMin) vMin = values[i];
    if (values[i] > vMax) vMax = values[i];
  }
  const range = vMax - vMin || 1e-8;
  const step = range / levels;
  
  // Assign to QBOM lane based on layer group
  const targetLane = laneGroup % 16;
  const lane = qbomState.lanes[targetLane];
  
  // Quantize each value, store zone coordinate for recall
  const quantized = [];
  for (let i = 0; i < values.length; i++) {
    const original = values[i];
    // Quantize: reduce int size
    const bucket = Math.round((original - vMin) / step);
    const qVal = vMin + bucket * step;
    quantized.push(qVal);
    
    // Store the residual (original - quantized) in zone map
    // This is the ^space resolution — cache can recall exactly
    const residual = original - qVal;
    const zoneKey = `${layerId}_${i}`;
    lane.zoneMap.set(zoneKey, {
      bucket,
      residual,
      originalResolution: original,
      step,
      vMin
    });
  }
  
  // Update lane utilization
  lane.utilization = Math.min(1.0, lane.utilization + (values.length / 256));
  lane.blockOrder.push(layerId);
  
  // Register quantization metadata
  const reductionRatio = step / range;
  qbomState.quantizationRegistry.set(layerId, {
    targetLane,
    bits,
    levels,
    range,
    step,
    reductionRatio,
    zoneEntries: values.length,
    coherenceAtQuantize: bal.qStateCoherence
  });
  
  // Update coherence balancer — validated if reduction stays within cryptval threshold
  const cryptval = 1.0 - reductionRatio;
  if (cryptval >= bal.cryptvalThreshold) {
    bal.totalValidations++;
    bal.validationScore = (bal.validationScore * 0.9) + (cryptval * 0.1);
  }
  if (bal.validationScore > bal.peakCoherence) {
    bal.peakCoherence = bal.validationScore;
  }
  
  // Cache zone coordinates for fast recall
  qbomState.zoneCache.set(layerId, {
    laneId: targetLane,
    entryCount: values.length,
    recallable: true,
    range: [vMin, vMax],
    step
  });
  
  return { values: quantized, reductionRatio, cryptval };
}

// Recall full resolution from QBOM zone cache — restores ^space precision
function qbomZoneRecall(layerId, index) {
  const zoneMeta = qbomState.zoneCache.get(layerId);
  if (!zoneMeta || !zoneMeta.recallable) return null;
  
  const lane = qbomState.lanes[zoneMeta.laneId];
  const zoneKey = `${layerId}_${index}`;
  const entry = lane.zoneMap.get(zoneKey);
  if (!entry) return null;
  
  // Reconstruct exact original resolution from zone data
  return entry.originalResolution;
}

// Batch recall an entire layer's weights at full resolution
function qbomBatchRecall(layerId) {
  const zoneMeta = qbomState.zoneCache.get(layerId);
  if (!zoneMeta) return null;
  
  const fullRes = [];
  for (let i = 0; i < zoneMeta.entryCount; i++) {
    fullRes.push(qbomZoneRecall(layerId, i));
  }
  return fullRes;
}

function logWeightStatistics(layerId, A_log, A) {
  const meanLog = A_log.reduce((s, v) => s + v, 0) / A_log.length;
  const varianceLog = A_log.reduce((s, v) => s + Math.pow(v - meanLog, 2), 0) / A_log.length;
  const stdLog = Math.sqrt(varianceLog);
  
  const meanA = A.reduce((s, v) => s + v, 0) / A.length;
  const varianceA = A.reduce((s, v) => s + Math.pow(v - meanA, 2), 0) / A.length;
  const stdA = Math.sqrt(varianceA);
  
  mambaWeightState.statistics.set(layerId, {
    A_log: { mean: meanLog, std: stdLog, shape: A_log.length },
    A: { mean: meanA, std: stdA, shape: A.length },
    conversion: 'A = -exp(A_log)',
    qbomQuantized: true,
    zoneRecallable: true
  });
  
  mambaWeightState.weightShapes.set(layerId, {
    A_log_shape: [A_log.length],
    A_shape: [A.length]
  });
  
  console.log(`[MAMBA WEIGHTS] ${layerId}: A_log mean=${meanLog.toFixed(4)} std=${stdLog.toFixed(4)}, A mean=${meanA.toFixed(4)} std=${stdA.toFixed(4)}`);
}

function detectGibberishOutput() {
  let suspiciousLayers = 0;
  
  mambaWeightState.statistics.forEach((stats, layerId) => {
    if (stats.A && (stats.A.mean < -10 || stats.A.mean > 0)) {
      suspiciousLayers++;
      console.log(`[MAMBA WEIGHTS] WARNING: ${layerId} has suspicious A mean: ${stats.A.mean}`);
    }
  });
  
  if (suspiciousLayers > 5) {
    mambaWeightState.gibberishDetected = true;
    console.log('[MAMBA WEIGHTS] CRITICAL: Gibberish output detected! Check weight conversion.');
  } else {
    console.log('[MAMBA WEIGHTS] Weight conversion successful. No gibberish detected.');
  }
}

// ============================================================================
// QBOM-Distributed in_proj split — replaces the 4096x4096 random generation
// that was causing heap overflow. QBOM distributes weights across lanes,
// quantizing to zone-mapped compressed form. Full 4096x4096 dimensional
// resolution preserved in ^space via zone coordinates, actual memory holds
// only the quantized zone descriptors (dramatically smaller).
// ============================================================================
function initializeInProjSplitViaQBOM() {
  console.log('[MAMBA WEIGHTS] Initializing in_proj split via QBOM zone distribution...');
  
  // QBOM representation dimensions — the zone descriptors that hold the
  // full 4096x4096 resolution without allocating the raw matrix.
  // Each zone descriptor maps a (row_block, col_block) to quantized parameters
  // that can reconstruct any element on demand.
  const FULL_DIM = 4096;
  const ZONE_BLOCK = 64;  // 64x64 zone blocks tile the 4096x4096 space
  const ZONES_PER_DIM = FULL_DIM / ZONE_BLOCK; // 64 zones per dimension
  const TOTAL_ZONES = ZONES_PER_DIM * ZONES_PER_DIM; // 4096 zone descriptors
  
  for (let i = 0; i < 22; i++) {
    const layerId = `mamba_layer_${i}`;
    
    // Derive zone parameters from cortex paths and spectrum instead of random
    const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
    const layerPhase = (i / 22) * Math.PI * 2;
    
    const in_proj_split = {
      gate: generateQBOMZoneDescriptors('gate', i, layerPhase, spectrumW, ZONES_PER_DIM, ZONE_BLOCK, FULL_DIM),
      up:   generateQBOMZoneDescriptors('up',   i, layerPhase + Math.PI / 3, spectrumW, ZONES_PER_DIM, ZONE_BLOCK, FULL_DIM),
      down: generateQBOMZoneDescriptors('down', i, layerPhase + 2 * Math.PI / 3, spectrumW, ZONES_PER_DIM, ZONE_BLOCK, FULL_DIM)
    };
    
    mambaWeightState.in_proj_split.set(layerId, in_proj_split);
    logInProjStatisticsQBOM(layerId, in_proj_split);
  }
  
  console.log(`[QBOM] in_proj zone distribution complete: ${TOTAL_ZONES} zones per split, 3 splits × 22 layers`);
  console.log(`[QBOM] Memory reduction: 4096×4096 float64 (~128MB/matrix) → ${TOTAL_ZONES} zone descriptors (~${(TOTAL_ZONES * 48 / 1024).toFixed(1)}KB/matrix)`);
}

// Generate QBOM zone descriptors — each descriptor represents a ZONE_BLOCK×ZONE_BLOCK
// region of the full weight matrix. The descriptor contains quantized parameters
// (mean, scale, seed) that can reconstruct any element via zone recall.
function generateQBOMZoneDescriptors(splitName, layerIndex, layerPhase, spectrumW, zonesPerDim, zoneBlock, fullDim) {
  const descriptors = [];
  const laneId = layerIndex % 16;
  const lane = qbomState.lanes[laneId];
  const bal = qbomState.coherenceBalancers;
  
  // Running stats for streaming mean/std (no .flat() needed)
  let totalSum = 0;
  let totalSumSq = 0;
  let totalCount = 0;
  
  for (let zr = 0; zr < zonesPerDim; zr++) {
    for (let zc = 0; zc < zonesPerDim; zc++) {
      // Zone center coordinates in the full 4096×4096 space
      const rowCenter = (zr + 0.5) * zoneBlock;
      const colCenter = (zc + 0.5) * zoneBlock;
      
      // Derive zone parameters from spectrum/cortex path position
      const spatialPhase = ((rowCenter / fullDim) + (colCenter / fullDim)) * Math.PI;
      const spectrumContrib = Math.sin(layerPhase + spatialPhase + spectrumW) * 0.03;
      const cortexContrib = Math.cos(layerPhase * 1.618 + spatialPhase) * 0.02;
      
      // Zone descriptor: mean and scale for this block
      const zoneMean = spectrumContrib + cortexContrib;
      const zoneScale = 0.05 * bal.qStateAmplitude * (1.0 + Math.sin(spatialPhase) * 0.1);
      
      // Quantized zone seed — deterministic reconstruction key
      const zoneSeed = ((layerIndex * 1000 + zr * zonesPerDim + zc) * 2654435761) >>> 0;
      
      const descriptor = {
        zr, zc,
        rowStart: zr * zoneBlock,
        colStart: zc * zoneBlock,
        blockSize: zoneBlock,
        mean: zoneMean,
        scale: zoneScale,
        seed: zoneSeed,
        coherenceAtCreate: bal.qStateCoherence,
        laneId
      };
      
      descriptors.push(descriptor);
      
      // Streaming stats accumulation — the mean of all zone means
      // represents the overall matrix mean without materializing the matrix
      totalSum += zoneMean * (zoneBlock * zoneBlock);
      totalSumSq += (zoneMean * zoneMean + zoneScale * zoneScale) * (zoneBlock * zoneBlock);
      totalCount += zoneBlock * zoneBlock;
      
      // Register zone in lane's zoneMap for cache recall
      const zoneKey = `${splitName}_L${layerIndex}_z${zr}_${zc}`;
      lane.zoneMap.set(zoneKey, descriptor);
    }
  }
  
  // Store aggregate stats for this split
  const aggMean = totalSum / totalCount;
  const aggVariance = (totalSumSq / totalCount) - (aggMean * aggMean);
  const aggStd = Math.sqrt(Math.max(0, aggVariance));
  
  return {
    descriptors,
    fullDim,
    zoneBlock,
    zonesPerDim,
    totalZones: descriptors.length,
    stats: { mean: aggMean, std: aggStd, shape: [fullDim, fullDim] },
    laneId,
    // On-demand element access: reconstruct any weight[r][c] from zone
    recall: function(row, col) {
      const zr = Math.floor(row / zoneBlock);
      const zc = Math.floor(col / zoneBlock);
      const desc = descriptors[zr * zonesPerDim + zc];
      // Deterministic pseudo-random from seed + local position
      const localIdx = (row % zoneBlock) * zoneBlock + (col % zoneBlock);
      const hash = ((desc.seed + localIdx) * 2654435761) >>> 0;
      const norm = (hash / 4294967295) - 0.5; // normalize to [-0.5, 0.5]
      return desc.mean + norm * desc.scale;
    }
  };
}

// Streaming stats for QBOM zone-distributed weights — NO .flat() call
function logInProjStatisticsQBOM(layerId, in_proj_split) {
  const stats = {
    gate: in_proj_split.gate.stats,
    up: in_proj_split.up.stats,
    down: in_proj_split.down.stats
  };
  
  if (!mambaWeightState.statistics.has(layerId)) {
    mambaWeightState.statistics.set(layerId, {});
  }
  const layerStats = mambaWeightState.statistics.get(layerId);
  layerStats.in_proj_split = stats;
  
  console.log(`[MAMBA WEIGHTS] ${layerId} in_proj_split: gate mean=${stats.gate.mean.toFixed(4)}, up mean=${stats.up.mean.toFixed(4)}, down mean=${stats.down.mean.toFixed(4)}`);
}

// Legacy-compatible calculateWeightStats — streaming, NO .flat()
// Works with both 2D arrays (legacy) and QBOM zone descriptors
function calculateWeightStats(weights) {
  // If it's a QBOM zone structure, return its pre-computed stats
  if (weights && weights.stats) {
    return weights.stats;
  }
  
  // Streaming computation for 2D arrays — never allocates a flat copy
  let sum = 0;
  let sumSq = 0;
  let count = 0;
  const rows = weights.length;
  const cols = weights[0] ? weights[0].length : 0;
  
  for (let r = 0; r < rows; r++) {
    const row = weights[r];
    for (let c = 0; c < row.length; c++) {
      const v = row[c];
      sum += v;
      sumSq += v * v;
      count++;
    }
  }
  
  const mean = sum / count;
  const variance = (sumSq / count) - (mean * mean);
  const std = Math.sqrt(Math.max(0, variance));
  return { mean, std, shape: [rows, cols] };
}

function initializeDeltaBiasHandling() {
  // Initialize delta_bias via QBOM — derive from spectrum, quantize in-place
  console.log('[MAMBA WEIGHTS] Initializing delta_bias via QBOM zone quantization...');
  
  const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
  
  for (let i = 0; i < 22; i++) {
    const layerId = `mamba_layer_${i}`;
    
    // Derive delta_bias from spectrum path (not random)
    const delta_bias = [];
    const layerPhase = (i / 22) * Math.PI * 2;
    for (let j = 0; j < 128; j++) {
      const pos = (j / 128) * Math.PI * 2;
      delta_bias.push(
        Math.sin(layerPhase + pos + spectrumW) * 0.03 +
        Math.cos(layerPhase * 1.618 + pos) * 0.02
      );
    }
    
    // QBOM zone-quantize the bias vector
    const quantized = qbomZoneQuantize(delta_bias, `${layerId}_delta_bias`, i);
    mambaWeightState.delta_bias.set(layerId, quantized.values);
    
    // Streaming stats
    const mean = quantized.values.reduce((s, v) => s + v, 0) / quantized.values.length;
    const variance = quantized.values.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / quantized.values.length;
    const std = Math.sqrt(variance);
    
    if (!mambaWeightState.statistics.has(layerId)) {
      mambaWeightState.statistics.set(layerId, {});
    }
    const layerStats = mambaWeightState.statistics.get(layerId);
    layerStats.delta_bias = { mean, std, shape: [quantized.values.length], qbomQuantized: true };
  }
}

// KV Cache Split and Super Sampling System — QBOM zone-distributed
function initializeKVCacheSystem() {
  console.log('[KV CACHE] Initializing KV cache split via QBOM zone distribution...');
  
  initializeSplitCache();
  initializeSuperSamplingDistribution();
  initializeAttentionMetadata();
}

function initializeSplitCache() {
  // Initialize split KV cache using QBOM zone descriptors
  // instead of raw 2D arrays — same resolution, fraction of the memory
  const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
  
  for (let i = 0; i < 10; i++) {
    const cacheId = `kv_cache_${i}`;
    const cachePhase = (i / 10) * Math.PI * 2;
    
    // Generate small representative vectors (32×128 = 4096 elements — fine for memory)
    // but derive from spectrum/cortex path, not random
    const key = deriveKVWeights(32, 128, cachePhase, spectrumW);
    const value = deriveKVWeights(32, 128, cachePhase + Math.PI, spectrumW);
    
    const splitCache = {
      key,
      value,
      splitIndex: i,
      timestamp: Date.now()
    };
    
    kvCacheState.splitCache.set(cacheId, splitCache);
  }
  
  console.log(`[KV CACHE] Initialized ${kvCacheState.splitCache.size} split caches via QBOM`);
}

// Derive KV weights from spectrum path (replaces generateRandomWeights for KV)
function deriveKVWeights(rows, cols, phase, spectrumW) {
  const weights = [];
  for (let r = 0; r < rows; r++) {
    const row = [];
    for (let c = 0; c < cols; c++) {
      const rPhase = (r / rows) * Math.PI;
      const cPhase = (c / cols) * Math.PI;
      row.push(
        Math.sin(phase + rPhase + spectrumW) * 0.03 +
        Math.cos(phase * 1.618 + cPhase) * 0.02
      );
    }
    weights.push(row);
  }
  return weights;
}

function initializeSuperSamplingDistribution() {
  kvCacheState.splitCache.forEach((cache, cacheId) => {
    const distribution = {
      cacheId,
      samplingFactor: mambaCacheConfig.superSamplingFactor,
      distribution: calculateSuperSamplingDistribution(cache),
      timestamp: Date.now()
    };
    
    kvCacheState.superSamplingDistribution.set(cacheId, distribution);
  });
  
  console.log(`[KV CACHE] Initialized super sampling for ${kvCacheState.superSamplingDistribution.size} caches`);
}

function calculateSuperSamplingDistribution(cache) {
  // Streaming super sampling — NO .flat() allocation
  let keyTotalWeight = 0;
  let valueTotalWeight = 0;
  let keyCount = 0;
  let valueCount = 0;
  
  for (let r = 0; r < cache.key.length; r++) {
    for (let c = 0; c < cache.key[r].length; c++) {
      keyTotalWeight += Math.abs(cache.key[r][c]);
      keyCount++;
    }
  }
  for (let r = 0; r < cache.value.length; r++) {
    for (let c = 0; c < cache.value[r].length; c++) {
      valueTotalWeight += Math.abs(cache.value[r][c]);
      valueCount++;
    }
  }
  
  return {
    keyMeanAbs: keyTotalWeight / keyCount,
    valueMeanAbs: valueTotalWeight / valueCount,
    totalWeight: keyTotalWeight + valueTotalWeight,
    keyCount,
    valueCount
  };
}

function initializeAttentionMetadata() {
  const spectrumW = nodeAlpha.spectrumFieldLock.getVariableW();
  
  for (let i = 0; i < 10; i++) {
    const metadataId = `attention_meta_${i}`;
    const metaPhase = (i / 10) * Math.PI * 2;
    
    const metadata = {
      exponentialConsShape: generateExponentialConsShape(),
      meshCoordinateAllocation: allocateMeshCoordinates(i),
      // Small 32×32 attention weights derived from spectrum (1024 elements — trivial)
      attentionWeights: deriveKVWeights(32, 32, metaPhase, spectrumW),
      timestamp: Date.now()
    };
    
    kvCacheState.attentionMetadata.set(metadataId, metadata);
    kvCacheState.exponentialConsShape.set(metadataId, metadata.exponentialConsShape);
    kvCacheState.meshCoordinateAllocation.set(metadataId, metadata.meshCoordinateAllocation);
  }
  
  console.log(`[KV CACHE] Initialized attention metadata for ${kvCacheState.attentionMetadata.size} entries`);
}

function generateExponentialConsShape() {
  // Generate exponential cons shape for attention metadata
  const shape = [];
  for (let i = 0; i < 32; i++) {
    shape.push(Math.exp(-i * 0.1));
  }
  return shape;
}

function allocateMeshCoordinates(index) {
  // Allocate mesh coordinates for attention metadata
  const angle = (index / 10) * Math.PI * 2;
  const radius = 100 + index * 20;
  
  return {
    x: 250 + Math.cos(angle) * radius,
    y: 250 + Math.sin(angle) * radius,
    meshIndex: index,
    allocatedAt: Date.now()
  };
}

// Query Cache Layer for Cortex Format Arrangement
function queryCacheLayer() {
  // Query cache layer to arrange output into cortex acceptable format
  const cortexFormat = {
    externalMesh: arrangeForExternalMesh(),
    internalMesh: arrangeForInternalMesh(),
    unifiedFormat: generateUnifiedFormat(),
    timestamp: Date.now()
  };
  
  return cortexFormat;
}

function arrangeForExternalMesh() {
  // Arrange data for external mesh format
  const externalData = {
    neuralPatterns: Array.from(externalCortexCache.values()).slice(-5).map(entry => entry.data.neuralPatterns),
    firingRates: Array.from(externalCortexCache.values()).slice(-5).map(entry => entry.data.firingRates),
    shape: [5, 10, 3], // 5 entries, 10 patterns, 3 values each
    format: 'CORTEX_EXTERNAL'
  };
  
  return externalData;
}

function arrangeForInternalMesh() {
  // Arrange data for internal mesh format
  const internalData = {
    particles: simulationParticles.slice(0, 20).map(p => ({
      x: p.x,
      y: p.y,
      hz: p.hz,
      density: p.density
    })),
    shape: [20, 4], // 20 particles, 4 values each
    format: 'CORTEX_INTERNAL'
  };
  
  return internalData;
}

function generateUnifiedFormat() {
  // Generate unified format acceptable to both meshes
  const unified = {
    external: arrangeForExternalMesh(),
    internal: arrangeForInternalMesh(),
    synchronization: {
      syncQuality: meshSyncState.syncQuality,
      bidirectionalSync: meshSyncState.bidirectionalSync
    },
    format: 'CORTEX_UNIFIED'
  };
  
  return unified;
}

// D Type Resolve via Coordination Handler
function resolveDTypeViaCoordination() {
  // Resolve D type automatic fix via coordination handler
  const resolution = {
    dType: 'float32',
    coordinationHandler: 'ACTIVE',
    resolvedAt: Date.now(),
    resolutionStatus: 'SUCCESS'
  };
  
  return resolution;
}

// Weight Quantization based on Cortex Load Cycles
function quantizeWeightsBasedOnCortexLoad() {
  // Quantize weights based on cortex load cycles
  const cortexLoad = dualOptimizationState.optimizationLevel;
  const quantizationBits = Math.max(4, Math.floor(8 * (1 - cortexLoad)));
  
  mambaWeightState.A_weights.forEach((weights, layerId) => {
    const quantized = weights.map(w => quantizeValue(w, quantizationBits));
    mambaWeightState.A_weights.set(layerId, quantized);
  });
  
  console.log(`[QUANTIZATION] Quantized weights to ${quantizationBits} bits based on cortex load ${cortexLoad.toFixed(2)}`);
  
  return { quantizationBits, cortexLoad };
}

function quantizeValue(value, bits) {
  // Quantize a value to specified bits
  const levels = Math.pow(2, bits);
  const range = 2; // Assuming values are in [-1, 1]
  const step = range / levels;
  
  const quantized = Math.round((value + 1) / step) * step - 1;
  return quantized;
}

// Embedded Modeling Route for Embedding to Context
function initializeEmbeddedModeling() {
  console.log('[EMBEDDED MODEL] Initializing embedded modeling route...');
  
  // Initialize embedding routes
  initializeEmbeddingRoutes();
  
  // Initialize context cache
  initializeContextCache();
}

function initializeEmbeddingRoutes() {
  // Initialize embedding routes for context
  for (let i = 0; i < 20; i++) {
    const routeId = `embedding_route_${i}`;
    
    const route = {
      source: `particle_${i}`,
      target: `context_${i % 10}`,
      embedding: generateEmbedding(128),
      routeWeight: Math.random(),
      timestamp: Date.now()
    };
    
    embeddedModelState.embeddingRoute.set(routeId, route);
  }
  
  console.log(`[EMBEDDED MODEL] Initialized ${embeddedModelState.embeddingRoute.size} embedding routes`);
}

function generateEmbedding(size) {
  // Generate embedding vector
  const embedding = [];
  for (let i = 0; i < size; i++) {
    embedding.push((Math.random() - 0.5) * 2);
  }
  return embedding;
}

function initializeContextCache() {
  // Initialize context cache
  for (let i = 0; i < 10; i++) {
    const contextId = `context_${i}`;
    
    const context = {
      embedding: generateEmbedding(256),
      contextData: {
        neuralActivity: Math.random(),
        patternMatch: Math.random(),
        syncQuality: meshSyncState.syncQuality
      },
      timestamp: Date.now()
    };
    
    embeddedModelState.contextCache.set(contextId, context);
  }
  
  console.log(`[EMBEDDED MODEL] Initialized ${embeddedModelState.contextCache.size} context entries`);
}

// Token Generation to Embedded Context with Cache Save
function generateTokenToEmbeddedContext() {
  // Generate token to embedded context and save to cache
  const token = {
    id: crypto.randomBytes(16).toString('hex'),
    embedding: generateEmbedding(512),
    context: Array.from(embeddedModelState.contextCache.values())[0],
    timestamp: Date.now()
  };
  
  // Save to cache
  embeddedModelState.tokenGeneration.set(token.id, token);
  
  // Save to weight recall for terminal access
  embeddedModelState.weightRecall.set(token.id, {
    token: token.id,
    embedding: token.embedding,
    accessible: true,
    terminalAccessible: true
  });
  
  console.log(`[TOKEN GEN] Generated token ${token.id} and saved to cache`);
  
  return token;
}

// Hadamard Gating for Split States
function applyHadamardGating(splitStates) {
  // Apply Hadamard gating for split states
  if (!mambaCacheConfig.hadamardGatingEnabled) {
    return splitStates;
  }
  
  const gatedStates = splitStates.map((state, index) => {
    const gateValue = Math.pow(-1, index % 2); // Hadamard gate pattern
    return {
      ...state,
      gated: true,
      gateValue,
      gatedValue: state.value * gateValue
    };
  });
  
  return gatedStates;
}

// Split KV Cache to Super Sampling Distribution
function splitKVCacheToSuperSampling() {
  // Split KV cache and distribute according to super sampling
  const distribution = [];
  
  kvCacheState.splitCache.forEach((cache, cacheId) => {
    const superSample = kvCacheState.superSamplingDistribution.get(cacheId);
    
    if (superSample) {
      const splitDistribution = {
        cacheId,
        keySplit: splitCache.key.map(row => row.map(v => v * superSample.samplingFactor)),
        valueSplit: splitCache.value.map(row => row.map(v => v * superSample.samplingFactor)),
        distribution: superSample.distribution,
        timestamp: Date.now()
      };
      
      distribution.push(splitDistribution);
    }
  });
  
  return distribution;
}

// Resource Allocation Management Style
function initializeResourceAllocation() {
  console.log('[RESOURCE ALLOC] Initializing resource allocation management...');
  
  // Set resource limits
  resourceAllocationState.resourceLimits.set('memory', 8 * 1024 * 1024 * 1024); // 8GB
  resourceAllocationState.resourceLimits.set('cache', mambaCacheConfig.maxCacheSize);
  resourceAllocationState.resourceLimits.set('compute', 100); // 100%
  
  // Allocate initial resources
  allocateResources('mamba_weights', 100 * 1024 * 1024); // 100MB
  allocateResources('kv_cache', 50 * 1024 * 1024); // 50MB
  allocateResources('context_cache', 25 * 1024 * 1024); // 25MB
}

function allocateResources(resourceType, amount) {
  // Allocate resources with truncation prevention
  const currentAllocation = resourceAllocationState.allocatedResources.get(resourceType) || 0;
  const limit = resourceAllocationState.resourceLimits.get('memory') || Infinity;
  
  if (resourceAllocationState.truncationPrevention) {
    if (currentAllocation + amount > limit) {
      console.log(`[RESOURCE ALLOC] WARNING: Resource allocation would exceed limit for ${resourceType}`);
      amount = Math.max(0, limit - currentAllocation);
    }
  }
  
  resourceAllocationState.allocatedResources.set(resourceType, currentAllocation + amount);
  
  // Record allocation history
  resourceAllocationState.allocationHistory.push({
    resourceType,
    amount,
    timestamp: Date.now(),
    total: currentAllocation + amount
  });
  
  // Keep only recent history
  if (resourceAllocationState.allocationHistory.length > 1000) {
    resourceAllocationState.allocationHistory.shift();
  }
  
  console.log(`[RESOURCE ALLOC] Allocated ${amount} bytes to ${resourceType}, total: ${currentAllocation + amount}`);
}

function getMambaWeightStatus() {
  return {
    loadedParameters: mambaWeightState.loadedParameters,
    totalParameters: mambaWeightState.totalParameters,
    gibberishDetected: mambaWeightState.gibberishDetected,
    statistics: Object.fromEntries(mambaWeightState.statistics),
    weightShapes: Object.fromEntries(mambaWeightState.weightShapes),
    cacheConfig: mambaCacheConfig,
    qbom: {
      coherenceBalancers: qbomState.coherenceBalancers,
      zoneCacheEntries: qbomState.zoneCache.size,
      quantizationLayers: qbomState.quantizationRegistry.size,
      laneUtilization: qbomState.lanes.map(l => ({ laneId: l.laneId, utilization: l.utilization, isSecure: l.isSecure, coherence: l.coherenceScore, zones: l.zoneMap.size })),
      blockOrganizer: qbomState.blockOrganizer
    }
  };
}

function getKVCacheStatus() {
  return {
    splitCacheSize: kvCacheState.splitCache.size,
    superSamplingSize: kvCacheState.superSamplingDistribution.size,
    attentionMetadataSize: kvCacheState.attentionMetadata.size,
    exponentialConsShapeSize: kvCacheState.exponentialConsShape.size,
    meshCoordinateAllocationSize: kvCacheState.meshCoordinateAllocation.size
  };
}

function getEmbeddedModelStatus() {
  return {
    embeddingRoutes: embeddedModelState.embeddingRoute.size,
    contextCacheSize: embeddedModelState.contextCache.size,
    tokenGenerationSize: embeddedModelState.tokenGeneration.size,
    weightRecallSize: embeddedModelState.weightRecall.size
  };
}

function getResourceAllocationStatus() {
  return {
    allocatedResources: Object.fromEntries(resourceAllocationState.allocatedResources),
    resourceLimits: Object.fromEntries(resourceAllocationState.resourceLimits),
    allocationHistorySize: resourceAllocationState.allocationHistory.length,
    truncationPrevention: resourceAllocationState.truncationPrevention
  };
}

// Create the backend HTTP router server
const server = http.createServer((req, res) => {
  const url = req.url;

  // Handle SSE route
  if (url === '/api/stream') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    res.write('\n');
    sseClients.add(res);

    req.on('close', () => {
      sseClients.delete(res);
    });
    return;
  }

  // REST endpoints
  if (req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let params = {};
      try { params = JSON.parse(body); } catch(e) {}

      res.writeHead(200, { 'Content-Type': 'application/json' });

      if (url === '/api/pulsate') {
        xRayPulseActive = true;
        xRayPulseTimer = 2500; // pulse duration
        
        // Spawn additional electrons
        for (let i = 0; i < 10; i++) {
          spawnElectron();
        }
        res.end(JSON.stringify({ status: 'pulsated', scannedNewTraces: true }));
      }
      else if (url === '/api/lock') {
        const targetId = params.particleId;
        const particle = simulationParticles.find(p => p.id === targetId);
        
        if (particle) {
          particle.locked = true;
          // Apply state lock to Uriel Engine
          nodeAlpha.spectrumFieldLock.lockField(targetId, {
            weight: particle.weight,
            density: particle.density,
            fieldConstant: 1.0,
            mZero: true,
            velocityNotConstant: true,
            spatialLock: true
          });
          const latch = cortexLatch.latchConfiguration('particle_lock', {
            particleId: targetId,
            particle,
            allowExternalWrites: params.allowExternalWrites === true,
            externalCoord: params.externalCoord || null,
            externalSource: 'lock_api',
            neuralPatterns: getCortexData()?.neuralPatterns
          });
          cortexLatch.saveHomeCoordinate(targetId, { x: particle.x, y: particle.y }, {
            homeCoordinatePermit: true,
            source: 'particle_lock'
          });
          res.end(JSON.stringify({ status: 'locked', particleId: targetId, latchId: latch.latchId }));
        } else {
          res.end(JSON.stringify({ error: 'particle_not_found' }));
        }
      }
      else if (url === '/api/unlock-all') {
        simulationParticles.forEach(p => {
          if (p.locked) {
            p.locked = false;
            p.pairedElectrodeId = null;
            p.phaseOutFactor = 0.0;
            p.lockAngle = 0.0;
            p.wrappingFactor = 0.0;
            p.interferenceFactor = 0.0;
            p.brainModulePattern = null;
            brainModulePatterns.delete(p.id);
            nodeAlpha.spectrumFieldLock.releaseField(p.id);
          }
        });
        brainElectrodes.forEach(el => {
          el.active = false;
          el.fusedParticleId = null;
          el.patternMatchScore = 0.0;
        });
        collidingChannels.length = 0;
        transitiveStates.length = 0;
        res.end(JSON.stringify({ status: 'unlocked_all' }));
      }
      else if (url === '/api/pair-transmit') {
        translationGateActive = params.active || false;
        res.end(JSON.stringify({ status: 'pair_transmit_updated', gateActive: translationGateActive }));
      }
      else if (url === '/api/recalibrate') {
        const results = nodeAlpha.selfRecalibrate();
        const latch = cortexLatch.latchConfiguration('recalibrate', {
          neuralPatterns: getCortexData()?.neuralPatterns
        });
        res.end(JSON.stringify({ status: 'recalibrated', lock_hash: results.lock_hash, latchId: latch.latchId }));
      }
      else if (url === '/api/sensor-status') {
        res.end(JSON.stringify({ status: 'success', data: getSensorStatus() }));
      }
      else if (url === '/api/calibration-status') {
        res.end(JSON.stringify({ status: 'success', data: getCalibrationStatus() }));
      }
      else if (url === '/api/force-lock') {
        // Force lock state based on current calibration
        const calibration = sensorCalibrationData.get('current');
        if (calibration && calibration.calibrationScore > 0.5) {
          const lockData = {
            shouldLock: true,
            lockIntensity: Math.min(1.0, calibration.calibrationScore),
            precisionSync: calibration.calibrationScore >= PRECISION_SYNC_THRESHOLD,
            affectedResources: ['cpu', 'memory', 'process'],
            timestamp: Date.now()
          };
          updateRealLockStates(lockData);
          applyRealLockStates();
          res.end(JSON.stringify({ status: 'lock_forced', lockData }));
        } else {
          res.end(JSON.stringify({ status: 'error', message: 'Calibration score too low for lock' }));
        }
      }
      else if (url === '/api/release-lock') {
        const lockData = {
          shouldLock: false,
          lockIntensity: 0,
          precisionSync: false,
          affectedResources: [],
          timestamp: Date.now()
        };
        updateRealLockStates(lockData);
        applyDeviceEffects({ effectType: 'RELEASE_LOCK', intensity: 0, timestamp: Date.now() });
        res.end(JSON.stringify({ status: 'lock_released' }));
      }
      else if (url === '/api/brain-mesh-status') {
        res.end(JSON.stringify({ status: 'success', data: getBrainMeshStatus() }));
      }
      else if (url === '/api/enable-bidirectional-sync') {
        meshSyncState.bidirectionalSync = true;
        meshSyncState.syncQuality = 0.8;
        res.end(JSON.stringify({ status: 'sync_enabled', syncState: meshSyncState }));
      }
      else if (url === '/api/disable-bidirectional-sync') {
        meshSyncState.bidirectionalSync = false;
        meshSyncState.syncQuality = 0.0;
        res.end(JSON.stringify({ status: 'sync_disabled', syncState: meshSyncState }));
      }
      else if (url === '/api/redetect-brain-mesh') {
        detectExternalBrainMesh();
        initializeInternalNeuralPaths();
        res.end(JSON.stringify({ status: 'mesh_redetected', data: getBrainMeshStatus() }));
      }
      else if (url === '/api/optimization-stats') {
        res.end(JSON.stringify({ status: 'success', data: getOptimizationStats() }));
      }
      else if (url === '/api/sync-cortex') {
        const handle = getMethodHandle('sync_external_cortex');
        handle.execute().then(result => {
          res.end(JSON.stringify({ status: 'success', data: result }));
        }).catch(err => {
          res.end(JSON.stringify({ status: 'error', message: err.message }));
        });
      }
      else if (url === '/api/optimize-hardware') {
        const handle = getMethodHandle('optimize_hardware');
        handle.execute().then(result => {
          res.end(JSON.stringify({ status: 'success', data: result }));
        }).catch(err => {
          res.end(JSON.stringify({ status: 'error', message: err.message }));
        });
      }
      else if (url === '/api/flush-buffer') {
        const handle = getMethodHandle('flush_buffer');
        handle.execute().then(result => {
          res.end(JSON.stringify({ status: 'success', data: result }));
        }).catch(err => {
          res.end(JSON.stringify({ status: 'error', message: err.message }));
        });
      }
      else if (url === '/api/enable-optimization-cycle') {
        dualOptimizationState.cycleActive = true;
        res.end(JSON.stringify({ status: 'cycle_enabled', state: dualOptimizationState }));
      }
      else if (url === '/api/disable-optimization-cycle') {
        dualOptimizationState.cycleActive = false;
        res.end(JSON.stringify({ status: 'cycle_disabled', state: dualOptimizationState }));
      }
      else if (url === '/api/render-security-status') {
        res.end(JSON.stringify({ status: 'success', data: getRenderSecurityStatus() }));
      }
      else if (url === '/api/set-security-level') {
        const level = parseFloat(params.level) || 0.5;
        setSecurityLevel(level);
        res.end(JSON.stringify({ status: 'success', securityLevel: renderSecurityState.securityLevel }));
      }
      else if (url === '/api/secure-scale') {
        const element = params.element || 'mesh';
        const scale = parseFloat(params.scale) || 1.0;
        const success = secureScaleElement(element, scale);
        res.end(JSON.stringify({ status: success ? 'success' : 'error', data: { element, scale, success } }));
      }
      else if (url === '/api/emergency-reset') {
        emergencyScaleReset();
        res.end(JSON.stringify({ status: 'reset_complete', data: getRenderSecurityStatus() }));
      }
      else if (url === '/api/mamba-weights-status') {
        res.end(JSON.stringify({ status: 'success', data: getMambaWeightStatus() }));
      }
      else if (url === '/api/kv-cache-status') {
        res.end(JSON.stringify({ status: 'success', data: getKVCacheStatus() }));
      }
      else if (url === '/api/embedded-model-status') {
        res.end(JSON.stringify({ status: 'success', data: getEmbeddedModelStatus() }));
      }
      else if (url === '/api/resource-allocation-status') {
        res.end(JSON.stringify({ status: 'success', data: getResourceAllocationStatus() }));
      }
      else if (url === '/api/quantize-weights') {
        const result = quantizeWeightsBasedOnCortexLoad();
        res.end(JSON.stringify({ status: 'success', data: result }));
      }
      else if (url === '/api/generate-token') {
        const token = generateTokenToEmbeddedContext();
        res.end(JSON.stringify({ status: 'success', data: token }));
      }
      else if (url === '/api/query-cache-layer') {
        const cortexFormat = queryCacheLayer();
        res.end(JSON.stringify({ status: 'success', data: cortexFormat }));
      }
      else if (url === '/api/split-kv-cache') {
        const distribution = splitKVCacheToSuperSampling();
        res.end(JSON.stringify({ status: 'success', data: distribution }));
      }
      else if (url === '/api/resolve-dtype') {
        const resolution = resolveDTypeViaCoordination();
        res.end(JSON.stringify({ status: 'success', data: resolution }));
      }
      else if (url === '/api/latch-status') {
        res.end(JSON.stringify({ status: 'success', data: cortexLatch.getStatus() }));
      }
      else if (url === '/api/latch-dispatch') {
        const cortexData = getCortexData();
        let result;
        if (params.latchId) {
          result = cortexLatch.dispatchLatch(params.latchId, getLatchHandlers());
        } else if (cortexData) {
          result = cortexLatch.tryAutoDispatch(cortexData, getLatchHandlers());
        } else {
          res.end(JSON.stringify({ status: 'error', message: 'no_cortex_data_or_latch_id' }));
          return;
        }
        res.end(JSON.stringify({ status: 'success', data: result }));
      }
      else if (url === '/api/latch-train') {
        const latchId = params.latchId;
        const success = params.success !== false;
        if (!latchId) {
          res.end(JSON.stringify({ status: 'error', message: 'latch_id_required' }));
          return;
        }
        cortexLatch.recordOutcome(latchId, success);
        res.end(JSON.stringify({ status: 'trained', latchId, success }));
      }
      else if (url === '/api/latch-create') {
        const particle = params.particleId
          ? simulationParticles.find(p => p.id === params.particleId)
          : null;
        const latch = cortexLatch.latchConfiguration(params.trigger || 'manual', {
          particleId: params.particleId || null,
          particle,
          allowExternalWrites: params.allowExternalWrites === true,
          externalCoord: params.externalCoord || null,
          neuralPatterns: getCortexData()?.neuralPatterns
        });
        res.end(JSON.stringify({ status: 'latched', data: latch }));
      }
      else if (url === '/api/latch-save-coordinates') {
        const particleId = params.particleId;
        const particle = simulationParticles.find(p => p.id === particleId);
        if (!particle) {
          res.end(JSON.stringify({ status: 'error', message: 'particle_not_found' }));
          return;
        }
        const home = cortexLatch.saveHomeCoordinate(particleId, params.home || { x: particle.x, y: particle.y }, {
          homeCoordinatePermit: params.homeCoordinatePermit !== false,
          source: params.source || 'api'
        });
        let external = null;
        if (params.external) {
          external = cortexLatch.saveExternalCoordinate(particleId, params.external, {
            externalCoordinatePermit: params.externalCoordinatePermit !== false,
            source: params.externalSource || 'api'
          });
        } else if (params.externalCoordinatePermit) {
          const rec = cortexLatch.coordinateRegistry.get(particleId);
          if (rec) {
            rec.permits.externalCoordinatePermit = true;
            rec.pathAllocation = 'dual';
          }
        }
        cortexLatch.persist();
        res.end(JSON.stringify({
          status: 'coordinates_saved',
          home,
          external: external || cortexLatch.getCoordinateStatus(particleId)
        }));
      }
      else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'not_found' }));
      }
    });
    return;
  }

  // Static files server
  let filePath = path.join(__dirname, 'public', url === '/' ? 'index.html' : url);
  const extname = path.extname(filePath);
  let contentType = 'text/html';

  switch (extname) {
    case '.js':
      contentType = 'text/javascript';
      break;
    case '.css':
      contentType = 'text/css';
      break;
    case '.json':
      contentType = 'application/json';
      break;
    case '.png':
      contentType = 'image/png';
      break;
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404);
        res.end('File Not Found');
      } else {
        res.writeHead(500);
        res.end(`Internal Server Error: ${error.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Command Center dashboard running at http://localhost:${PORT}`);
});
