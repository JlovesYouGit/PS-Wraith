// HTML DOM Element References
const metaVariableW = document.getElementById('meta-variable-w');
const metaLockedCount = document.getElementById('meta-locked-count');
const metaThreatLevel = document.getElementById('meta-threat-level');

const btnPulsate = document.getElementById('btn-pulsate');
const btnPairTransmit = document.getElementById('btn-pair-transmit');
const btnRecalibrate = document.getElementById('btn-recalibrate');
const btnUnlock = document.getElementById('btn-unlock');

const toggleLayerTop = document.getElementById('toggle-layer-top');
const toggleLayerBottom = document.getElementById('toggle-layer-bottom');
const xrayWarningBanner = document.getElementById('xray-warning-banner');

const consoleLogs = document.getElementById('console-logs');

// Layer Toggles
let showTopLayer = true;
let showBottomLayer = true;

toggleLayerTop.addEventListener('click', () => {
  showTopLayer = !showTopLayer;
  toggleLayerTop.classList.toggle('active', showTopLayer);
  appendConsoleLog('SYSTEM', `Layer filter toggled: Top Layer is now ${showTopLayer ? 'VISIBLE' : 'HIDDEN'}`);
});

toggleLayerBottom.addEventListener('click', () => {
  showBottomLayer = !showBottomLayer;
  toggleLayerBottom.classList.toggle('active', showBottomLayer);
  appendConsoleLog('SYSTEM', `Layer filter toggled: Bottom Layer is now ${showBottomLayer ? 'VISIBLE' : 'HIDDEN'}`);
});

// Canvas Context setups
const lidarCanvas = document.getElementById('lidar-canvas');
const lidarCtx = lidarCanvas.getContext('2d');

const meshCanvas = document.getElementById('mesh-canvas');
const meshCtx = meshCanvas.getContext('2d');

const brainCanvas = document.getElementById('brain-canvas');
const brainCtx = brainCanvas.getContext('2d');

const sensorCanvas = document.getElementById('sensor-canvas');
const sensorCtx = sensorCanvas.getContext('2d');

const brainMeshCanvas = document.getElementById('brain-mesh-canvas');
const brainMeshCtx = brainMeshCanvas.getContext('2d');

// Sensor control buttons
const btnForceLock = document.getElementById('btn-force-lock');
const btnReleaseDeviceLock = document.getElementById('btn-release-device-lock');
const btnSensorStatus = document.getElementById('btn-sensor-status');

// Brain mesh control buttons
const btnEnableSync = document.getElementById('btn-enable-sync');
const btnDisableSync = document.getElementById('btn-disable-sync');
const btnRedetectMesh = document.getElementById('btn-redetect-mesh');

// Optimization control buttons
const btnEnableOpt = document.getElementById('btn-enable-opt');
const btnDisableOpt = document.getElementById('btn-disable-opt');
const btnSyncCortex = document.getElementById('btn-sync-cortex');

// Cortex–Uriel latch controls
const btnLatchDispatch = document.getElementById('btn-latch-dispatch');
const btnLatchCreate = document.getElementById('btn-latch-create');
const btnLatchStatus = document.getElementById('btn-latch-status');
const latchCount = document.getElementById('latch-count');
const latchDispatches = document.getElementById('latch-dispatches');
const latchGated = document.getElementById('latch-gated');
const latchAllowed = document.getElementById('latch-allowed');

// Render security buttons
const btnSetSecurity = document.getElementById('btn-set-security');
const btnSecureScale = document.getElementById('btn-secure-scale');
const btnEmergencyReset = document.getElementById('btn-emergency-reset');

// Sensor display elements
const sensorCpu = document.getElementById('sensor-cpu');
const sensorMemory = document.getElementById('sensor-memory');
const sensorSpectrum = document.getElementById('sensor-spectrum');
const sensorCalibration = document.getElementById('sensor-calibration');
const deviceLockStatus = document.getElementById('device-lock-status');

// Brain mesh display elements
const meshExternal = document.getElementById('mesh-external');
const meshInternal = document.getElementById('mesh-internal');
const meshStable = document.getElementById('mesh-stable');
const meshEquiv = document.getElementById('mesh-equiv');
const meshShape = document.getElementById('mesh-shape');
const brainMeshStatus = document.getElementById('brain-mesh-status');

// Optimization display elements
const optCycleRate = document.getElementById('opt-cycle-rate');
const optPatternRate = document.getElementById('opt-pattern-rate');
const optLevel = document.getElementById('opt-level');
const optGhzSync = document.getElementById('opt-ghz-sync');
const optExternalPace = document.getElementById('opt-external-pace');
const optInternalPace = document.getElementById('opt-internal-pace');

// Security display elements
const securityLevel = document.getElementById('security-level');
const securityIntegrity = document.getElementById('security-integrity');
const securityScale = document.getElementById('security-scale');
const securityTokens = document.getElementById('security-tokens');
const securityTransition = document.getElementById('security-transition');

// Track screen scaling updates
function resizeCanvases() {
  [lidarCanvas, meshCanvas, brainCanvas, sensorCanvas, brainMeshCanvas].forEach(canvas => {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
  });
}
window.addEventListener('resize', resizeCanvases);
setTimeout(resizeCanvases, 200);

// Global live parameters cached from SSE updates stream
let liveMeta = {};
let liveElectrons = [];
let liveParticles = [];
let liveElectrodes = [];
let isPulsating = false;
let isPairTransmitting = false;
let densityLayers = {};
let collidingChannelsCount = 0;

// 1. Render Lidar Map surface
function renderLidar() {
  const w = lidarCanvas.width;
  const h = lidarCanvas.height;
  lidarCtx.clearRect(0, 0, w, h);

  // Background Grid reference lines
  lidarCtx.strokeStyle = 'rgba(0, 242, 254, 0.04)';
  lidarCtx.lineWidth = 1;
  const gridSpacing = 30;
  for (let x = 0; x < w; x += gridSpacing) {
    lidarCtx.beginPath();
    lidarCtx.moveTo(x, 0);
    lidarCtx.lineTo(x, h);
    lidarCtx.stroke();
  }
  for (let y = 0; y < h; y += gridSpacing) {
    lidarCtx.beginPath();
    lidarCtx.moveTo(0, y);
    lidarCtx.lineTo(w, y);
    lidarCtx.stroke();
  }

  // Set drawing scales from simulation coordinates bounds (500x500 base)
  const scaleX = w / 500;
  const scaleY = h / 500;

  // Motherboard Static Trace Routing (Drawn depending on toggles)
  const staticPaths = [
    // Top Layer traces
    { layer: 'top', color: 'rgba(0, 242, 254, 0.25)', points: [{x: 50, y: 50}, {x: 200, y: 50}, {x: 250, y: 150}, {x: 400, y: 150}] },
    { layer: 'top', color: 'rgba(0, 242, 254, 0.25)', points: [{x: 80, y: 150}, {x: 180, y: 150}, {x: 220, y: 220}, {x: 350, y: 220}] },
    { layer: 'top', color: 'rgba(0, 242, 254, 0.25)', points: [{x: 50, y: 350}, {x: 150, y: 350}, {x: 200, y: 400}, {x: 450, y: 400}] },
    // Bottom Layer traces
    { layer: 'bottom', color: 'rgba(185, 39, 252, 0.25)', points: [{x: 100, y: 80}, {x: 100, y: 250}, {x: 250, y: 250}, {x: 250, y: 350}] },
    { layer: 'bottom', color: 'rgba(185, 39, 252, 0.25)', points: [{x: 380, y: 80}, {x: 380, y: 300}, {x: 300, y: 300}, {x: 150, y: 300}] },
    { layer: 'bottom', color: 'rgba(185, 39, 252, 0.25)', points: [{x: 420, y: 50}, {x: 420, y: 180}, {x: 480, y: 240}, {x: 480, y: 350}] }
  ];

  staticPaths.forEach(path => {
    if (path.layer === 'top' && !showTopLayer) return;
    if (path.layer === 'bottom' && !showBottomLayer) return;

    lidarCtx.strokeStyle = path.color;
    lidarCtx.lineWidth = path.layer === 'top' ? 2 : 1.5;
    if (path.layer === 'bottom') lidarCtx.setLineDash([4, 4]);
    else lidarCtx.setLineDash([]);

    lidarCtx.beginPath();
    lidarCtx.moveTo(path.points[0].x * scaleX, path.points[0].y * scaleY);
    for (let i = 1; i < path.points.length; i++) {
      lidarCtx.lineTo(path.points[i].x * scaleX, path.points[i].y * scaleY);
    }
    lidarCtx.stroke();
  });
  lidarCtx.setLineDash([]); // Reset line dash

  // Render moving electrons signals with density visualization
  liveElectrons.forEach(el => {
    if (el.layer === 'top' && !showTopLayer) return;
    if (el.layer === 'bottom' && !showBottomLayer) return;

    const x = el.x * scaleX;
    const y = el.y * scaleY;

    // Outer glow ring with density-based intensity
    const densityIntensity = el.density || 0.5;
    const glow = lidarCtx.createRadialGradient(x, y, 1, x, y, 6 + densityIntensity * 4);
    const color = el.layer === 'top' ? 'rgba(0, 242, 254, 0.8)' : 'rgba(185, 39, 252, 0.8)';
    glow.addColorStop(0, '#ffffff');
    glow.addColorStop(0.3, color);
    glow.addColorStop(1, 'transparent');

    lidarCtx.fillStyle = glow;
    lidarCtx.beginPath();
    lidarCtx.arc(x, y, 8 + densityIntensity * 2, 0, Math.PI * 2);
    lidarCtx.fill();
    
    // Draw phase indicator
    if (el.phase !== undefined) {
      lidarCtx.strokeStyle = color;
      lidarCtx.lineWidth = 1;
      lidarCtx.beginPath();
      lidarCtx.arc(x, y, 10, el.phase, el.phase + Math.PI / 2);
      lidarCtx.stroke();
    }
  });
}

// 2. Render Virtual Mesh Particles Panel
function renderMesh() {
  const w = meshCanvas.width;
  const h = meshCanvas.height;
  meshCtx.clearRect(0, 0, w, h);

  const scaleX = w / 500;
  const scaleY = h / 500;

  // Draw connections mesh lines
  meshCtx.strokeStyle = 'rgba(0, 242, 254, 0.08)';
  meshCtx.lineWidth = 1;
  for (let i = 0; i < liveParticles.length; i++) {
    for (let j = i + 1; j < liveParticles.length; j++) {
      const p1 = liveParticles[i];
      const p2 = liveParticles[j];
      const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
      if (dist < 80) {
        meshCtx.beginPath();
        meshCtx.moveTo(p1.x * scaleX, p1.y * scaleY);
        meshCtx.lineTo(p2.x * scaleX, p2.y * scaleY);
        meshCtx.stroke();
      }
    }
  }

  // Draw particles with advanced phasory lock visualization
  liveParticles.forEach(p => {
    const x = p.x * scaleX;
    const y = p.y * scaleY;

    if (p.locked) {
      // Bending state wraps with interference visualization
      meshCtx.strokeStyle = 'rgba(5, 255, 199, 0.6)';
      meshCtx.lineWidth = 1.5;
      meshCtx.beginPath();
      // Use locking angle to wrap trajectory visualization
      meshCtx.arc(x, y, 12, p.lockAngle, p.lockAngle + Math.PI, false);
      meshCtx.stroke();

      // Inversive field waves with wrapping and interference
      if (p.waveAmplitude !== undefined) {
        meshCtx.strokeStyle = 'rgba(255, 59, 105, 0.4)';
        meshCtx.beginPath();
        const waveRadius = 14 + Math.sin(p.wave) * 6 * (p.waveAmplitude || 1);
        meshCtx.arc(x, y, waveRadius, 0, Math.PI * 2);
        meshCtx.stroke();
        
        // Wrapping interference rings
        if (p.wrapping > 0) {
          meshCtx.strokeStyle = `rgba(185, 39, 252, ${p.wrapping * 0.5})`;
          meshCtx.beginPath();
          meshCtx.arc(x, y, 18 + p.wrapping * 10, 0, Math.PI * 2);
          meshCtx.stroke();
        }
      }

      // Core locked node dot
      meshCtx.fillStyle = '#05ffc7';
      meshCtx.beginPath();
      meshCtx.arc(x, y, 4, 0, Math.PI * 2);
      meshCtx.fill();
      
      // Brain module pattern indicator
      if (p.brainPattern) {
        meshCtx.fillStyle = 'rgba(255, 200, 0, 0.8)';
        meshCtx.font = '8px monospace';
        meshCtx.fillText(p.brainPattern.substring(0, 4), x + 6, y - 6);
      }
    } else {
      // Normal particles with pi ratio influence on size
      const piSize = 3 * (p.piRatio || 1);
      meshCtx.fillStyle = 'rgba(0, 242, 254, 0.6)';
      meshCtx.beginPath();
      meshCtx.arc(x, y, piSize, 0, Math.PI * 2);
      meshCtx.fill();
    }
  });
}

// Particle Mouse lock listener on Mesh Canvas
meshCanvas.addEventListener('click', (e) => {
  const rect = meshCanvas.getBoundingClientRect();
  const clickX = ((e.clientX - rect.left) / meshCanvas.width) * 500;
  const clickY = ((e.clientY - rect.top) / meshCanvas.height) * 500;

  // Find nearest particle
  let nearest = null;
  let minDist = 20; // click threshold
  liveParticles.forEach(p => {
    const dist = Math.hypot(p.x - clickX, p.y - clickY);
    if (dist < minDist) {
      minDist = dist;
      nearest = p;
    }
  });

  if (nearest && !nearest.locked) {
    sendAction('/api/lock', { particleId: nearest.id });
    appendConsoleLog('LOCK', `Phasory lock activated on particle ${nearest.id}. Wrapping inversive waves.`);
  }
});

// 3. Render Brain signal electrodes pairs and fields
function renderBrain() {
  const w = brainCanvas.width;
  const h = brainCanvas.height;
  brainCtx.clearRect(0, 0, w, h);

  const scaleX = w / 500;
  const scaleY = h / 500;

  // Bending spectrum field visualization (central distortion)
  if (liveMeta.translationGateBending > 0) {
    const cx = w / 2;
    const cy = h / 2;
    const radius = 100 * scaleX;
    
    const grad = brainCtx.createRadialGradient(cx, cy, 10, cx, cy, radius * (1 + liveMeta.translationGateBending * 0.5));
    grad.addColorStop(0, 'rgba(185, 39, 252, 0.15)');
    grad.addColorStop(0.5, 'rgba(0, 242, 254, 0.05)');
    grad.addColorStop(1, 'transparent');

    brainCtx.fillStyle = grad;
    brainCtx.beginPath();
    brainCtx.arc(cx, cy, radius * (1 + liveMeta.translationGateBending), 0, Math.PI * 2);
    brainCtx.fill();
  }

  // Draw Brain electrodes ring with pi ratio control visualization
  liveElectrodes.forEach(el => {
    const x = el.x * scaleX;
    const y = el.y * scaleY;

    // Draw 3-meter boundary circle with pi ratio control
    if (el.boundaryRadius) {
      const boundaryPx = el.boundaryRadius * (el.piRatioControl || 1) * scaleX;
      brainCtx.strokeStyle = 'rgba(0, 242, 254, 0.1)';
      brainCtx.lineWidth = 1;
      brainCtx.setLineDash([2, 4]);
      brainCtx.beginPath();
      brainCtx.arc(x, y, boundaryPx, 0, Math.PI * 2);
      brainCtx.stroke();
      brainCtx.setLineDash([]);
    }

    // Draw connection lines to paired locked particle
    if (el.active && el.pairedId) {
      const pairedParticle = liveParticles.find(p => p.id === el.pairedId);
      if (pairedParticle) {
        const px = pairedParticle.x * scaleX;
        const py = pairedParticle.y * scaleY;
        
        // Colliding channel line with pattern match intensity
        const matchIntensity = el.patternMatchScore || 0.5;
        brainCtx.strokeStyle = `rgba(185, 39, 252, ${0.3 + matchIntensity * 0.5})`;
        brainCtx.lineWidth = 1 + matchIntensity * 2;
        brainCtx.beginPath();
        brainCtx.moveTo(x, y);
        brainCtx.lineTo(px, py);
        brainCtx.stroke();
        
        // Draw colliding channel minimization indicator
        if (collidingChannelsCount > 0) {
          const midX = (x + px) / 2;
          const midY = (y + py) / 2;
          brainCtx.fillStyle = 'rgba(5, 255, 199, 0.6)';
          brainCtx.beginPath();
          brainCtx.arc(midX, midY, 3, 0, Math.PI * 2);
          brainCtx.fill();
        }
      }
    }

    // Outer glow relative to charge and pattern match
    brainCtx.shadowBlur = el.charge * 15;
    brainCtx.shadowColor = el.active ? '#b927fc' : '#00f2fe';

    const electrodeSize = 5 + el.charge * 3;
    brainCtx.fillStyle = el.active ? '#b927fc' : 'rgba(0, 242, 254, 0.7)';
    brainCtx.beginPath();
    brainCtx.arc(x, y, electrodeSize, 0, Math.PI * 2);
    brainCtx.fill();
    
    // Pattern match score indicator
    if (el.patternMatchScore > 0) {
      brainCtx.fillStyle = 'rgba(255, 200, 0, 0.8)';
      brainCtx.font = '8px monospace';
      brainCtx.fillText(`${(el.patternMatchScore * 100).toFixed(0)}%`, x - 8, y - electrodeSize - 2);
    }

    // Reset shadow state
    brainCtx.shadowBlur = 0;
  });
}

// 4. Render Sensor Pipeline Visualization
function renderSensorPipeline() {
  const w = sensorCanvas.width;
  const h = sensorCanvas.height;
  sensorCtx.clearRect(0, 0, w, h);
  
  if (!liveMeta.sensors || !liveMeta.calibration) return;
  
  const sensors = liveMeta.sensors;
  const calibration = liveMeta.calibration;
  
  // Draw pipeline flow diagram
  const centerX = w / 2;
  const centerY = h / 2;
  
  // Sensor nodes
  const sensorNodes = [
    { id: 'cpu', x: centerX - 150, y: centerY - 80, label: 'CPU' },
    { id: 'memory', x: centerX - 150, y: centerY, label: 'MEMORY' },
    { id: 'network', x: centerX - 150, y: centerY + 80, label: 'NETWORK' },
    { id: 'spectrum', x: centerX, y: centerY - 80, label: 'SPECTRUM' }
  ];
  
  // Pipeline stages
  const pipelineStages = [
    { x: centerX + 50, y: centerY, label: 'CALIBRATION' },
    { x: centerX + 150, y: centerY, label: 'LOCK STATE' },
    { x: centerX + 250, y: centerY, label: 'DEVICE EFFECT' }
  ];
  
  // Draw sensor nodes
  sensorNodes.forEach(node => {
    const sensor = sensors[node.id];
    if (!sensor) return;
    
    const isActive = sensor.active;
    const reading = sensor.lastReading;
    
    sensorCtx.fillStyle = isActive ? 'rgba(0, 242, 254, 0.2)' : 'rgba(100, 100, 100, 0.1)';
    sensorCtx.strokeStyle = isActive ? '#00f2fe' : '#666';
    sensorCtx.lineWidth = 2;
    
    sensorCtx.beginPath();
    sensorCtx.arc(node.x, node.y, 25, 0, Math.PI * 2);
    sensorCtx.fill();
    sensorCtx.stroke();
    
    // Label
    sensorCtx.fillStyle = isActive ? '#00f2fe' : '#666';
    sensorCtx.font = '10px Orbitron';
    sensorCtx.textAlign = 'center';
    sensorCtx.fillText(node.label, node.x, node.y + 40);
    
    // Reading value
    if (reading !== undefined) {
      const displayValue = typeof reading === 'object' ? reading.hz?.toFixed(1) || 0 : reading.toFixed(1);
      sensorCtx.font = '9px monospace';
      sensorCtx.fillText(displayValue, node.x, node.y + 4);
    }
  });
  
  // Draw pipeline connections
  sensorCtx.strokeStyle = 'rgba(0, 242, 254, 0.3)';
  sensorCtx.lineWidth = 1;
  sensorCtx.setLineDash([4, 4]);
  
  sensorNodes.forEach(node => {
    sensorCtx.beginPath();
    sensorCtx.moveTo(node.x + 25, node.y);
    sensorCtx.lineTo(pipelineStages[0].x - 30, pipelineStages[0].y);
    sensorCtx.stroke();
  });
  
  // Draw pipeline stages
  pipelineStages.forEach((stage, index) => {
    const isActive = calibration.pipelineStatus && 
      Object.values(calibration.pipelineStatus)[index]?.active;
    
    sensorCtx.fillStyle = isActive ? 'rgba(185, 39, 252, 0.2)' : 'rgba(100, 100, 100, 0.1)';
    sensorCtx.strokeStyle = isActive ? '#b927fc' : '#666';
    sensorCtx.lineWidth = 2;
    sensorCtx.setLineDash([]);
    
    sensorCtx.beginPath();
    sensorCtx.arc(stage.x, stage.y, 30, 0, Math.PI * 2);
    sensorCtx.fill();
    sensorCtx.stroke();
    
    sensorCtx.fillStyle = isActive ? '#b927fc' : '#666';
    sensorCtx.font = '9px Orbitron';
    sensorCtx.textAlign = 'center';
    sensorCtx.fillText(stage.label, stage.x, stage.y + 45);
    
    // Connect to next stage
    if (index < pipelineStages.length - 1) {
      sensorCtx.strokeStyle = 'rgba(185, 39, 252, 0.3)';
      sensorCtx.lineWidth = 2;
      sensorCtx.setLineDash([4, 4]);
      sensorCtx.beginPath();
      sensorCtx.moveTo(stage.x + 30, stage.y);
      sensorCtx.lineTo(pipelineStages[index + 1].x - 30, stage.y);
      sensorCtx.stroke();
    }
  });
  
  // Draw lock state indicator
  if (calibration.lockState) {
    const lockActive = calibration.lockState.active;
    const lockX = pipelineStages[2].x + 60;
    const lockY = centerY;
    
    sensorCtx.fillStyle = lockActive ? 'rgba(255, 59, 105, 0.3)' : 'rgba(100, 100, 100, 0.1)';
    sensorCtx.strokeStyle = lockActive ? '#ff3b69' : '#666';
    sensorCtx.lineWidth = 3;
    sensorCtx.setLineDash([]);
    
    sensorCtx.beginPath();
    sensorCtx.arc(lockX, lockY, 35, 0, Math.PI * 2);
    sensorCtx.fill();
    sensorCtx.stroke();
    
    sensorCtx.fillStyle = lockActive ? '#ff3b69' : '#666';
    sensorCtx.font = '10px Orbitron';
    sensorCtx.textAlign = 'center';
    sensorCtx.fillText(lockActive ? 'LOCKED' : 'UNLOCKED', lockX, lockY + 5);
    
    if (lockActive) {
      sensorCtx.font = '8px monospace';
      sensorCtx.fillText(`${(calibration.lockState.intensity * 100).toFixed(0)}%`, lockX, lockY + 20);
    }
  }
}

// 5. Render Brain Mesh Synchronization
function renderBrainMeshSync() {
  const w = brainMeshCanvas.width;
  const h = brainMeshCanvas.height;
  brainMeshCtx.clearRect(0, 0, w, h);
  
  if (!liveMeta.brainMesh) return;
  
  const brainMesh = liveMeta.brainMesh;
  const centerX = w / 2;
  const centerY = h / 2;
  
  // Draw external brain mesh (left side)
  if (brainMesh.externalDetected) {
    const externalCenterX = centerX - 100;
    
    // Draw mesh nodes
    for (let i = 0; i < 20; i++) {
      const angle = (i / 20) * Math.PI * 2;
      const radius = 60 + Math.sin(Date.now() / 1000 + i) * 10;
      const x = externalCenterX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      brainMeshCtx.fillStyle = 'rgba(0, 242, 254, 0.3)';
      brainMeshCtx.strokeStyle = '#00f2fe';
      brainMeshCtx.lineWidth = 1;
      
      brainMeshCtx.beginPath();
      brainMeshCtx.arc(x, y, 4, 0, Math.PI * 2);
      brainMeshCtx.fill();
      brainMeshCtx.stroke();
      
      // Draw connections to nearby nodes
      for (let j = i + 1; j < Math.min(i + 4, 20); j++) {
        const angle2 = (j / 20) * Math.PI * 2;
        const radius2 = 60 + Math.sin(Date.now() / 1000 + j) * 10;
        const x2 = externalCenterX + Math.cos(angle2) * radius2;
        const y2 = centerY + Math.sin(angle2) * radius2;
        
        brainMeshCtx.strokeStyle = 'rgba(0, 242, 254, 0.2)';
        brainMeshCtx.beginPath();
        brainMeshCtx.moveTo(x, y);
        brainMeshCtx.lineTo(x2, y2);
        brainMeshCtx.stroke();
      }
    }
    
    // Label
    brainMeshCtx.fillStyle = '#00f2fe';
    brainMeshCtx.font = '10px Orbitron';
    brainMeshCtx.textAlign = 'center';
    brainMeshCtx.fillText('EXTERNAL MESH', externalCenterX, centerY + 90);
  }
  
  // Draw internal brain mesh (right side)
  if (brainMesh.internalActive) {
    const internalCenterX = centerX + 100;
    
    // Draw neural paths based on particles
    liveParticles.forEach((particle, index) => {
      if (index >= 20) return;
      
      const x = internalCenterX + (particle.x - 250) * 0.4;
      const y = centerY + (particle.y - 250) * 0.4;
      
      const isStable = index < (brainMesh.stableNodeCount || 0);
      
      brainMeshCtx.fillStyle = isStable ? 'rgba(185, 39, 252, 0.5)' : 'rgba(185, 39, 252, 0.2)';
      brainMeshCtx.strokeStyle = isStable ? '#b927fc' : 'rgba(185, 39, 252, 0.3)';
      brainMeshCtx.lineWidth = isStable ? 2 : 1;
      
      brainMeshCtx.beginPath();
      brainMeshCtx.arc(x, y, isStable ? 5 : 3, 0, Math.PI * 2);
      brainMeshCtx.fill();
      brainMeshCtx.stroke();
      
      // Draw neural path connections
      if (isStable) {
        brainMeshCtx.strokeStyle = 'rgba(185, 39, 252, 0.3)';
        brainMeshCtx.setLineDash([2, 2]);
        brainMeshCtx.beginPath();
        brainMeshCtx.moveTo(x, y);
        brainMeshCtx.lineTo(internalCenterX, centerY);
        brainMeshCtx.stroke();
        brainMeshCtx.setLineDash([]);
      }
    });
    
    // Label
    brainMeshCtx.fillStyle = '#b927fc';
    brainMeshCtx.font = '10px Orbitron';
    brainMeshCtx.textAlign = 'center';
    brainMeshCtx.fillText('INTERNAL MESH', internalCenterX, centerY + 90);
  }
  
  // Draw bidirectional sync indicator
  if (brainMesh.bidirectionalSync) {
    // Draw sync arrows between meshes
    const syncY = centerY;
    
    brainMeshCtx.strokeStyle = 'rgba(5, 255, 199, 0.5)';
    brainMeshCtx.lineWidth = 2;
    brainMeshCtx.setLineDash([4, 4]);
    
    // Arrow from external to internal
    brainMeshCtx.beginPath();
    brainMeshCtx.moveTo(centerX - 50, syncY - 20);
    brainMeshCtx.lineTo(centerX + 50, syncY - 20);
    brainMeshCtx.stroke();
    
    // Arrow from internal to external
    brainMeshCtx.beginPath();
    brainMeshCtx.moveTo(centerX + 50, syncY + 20);
    brainMeshCtx.lineTo(centerX - 50, syncY + 20);
    brainMeshCtx.stroke();
    
    brainMeshCtx.setLineDash([]);
    
    // Sync quality indicator
    brainMeshCtx.fillStyle = '#05ffc7';
    brainMeshCtx.font = '12px Orbitron';
    brainMeshCtx.textAlign = 'center';
    brainMeshCtx.fillText(`SYNC: ${(brainMesh.syncQuality * 100).toFixed(0)}%`, centerX, syncY);
  }
}

function updateSensorDisplays() {
  if (!liveMeta.sensors) return;
  
  const sensors = liveMeta.sensors;
  
  // Update CPU display
  if (sensors.cpu) {
    const cpuVal = typeof sensors.cpu.lastReading === 'number' ? 
      sensors.cpu.lastReading.toFixed(1) : '0.0';
    sensorCpu.innerText = `${cpuVal}%`;
  }
  
  // Update Memory display
  if (sensors.memory) {
    const memVal = typeof sensors.memory.lastReading === 'number' ? 
      sensors.memory.lastReading.toFixed(1) : '0.0';
    sensorMemory.innerText = `${memVal}%`;
  }
  
  // Update Spectrum display
  if (sensors.spectrum) {
    const specVal = typeof sensors.spectrum.lastReading === 'object' ? 
      sensors.spectrum.lastReading.hz?.toFixed(1) || '0.0' : '0.0';
    sensorSpectrum.innerText = specVal;
  }
  
  // Update Calibration display
  if (liveMeta.calibration && liveMeta.calibration.calibration) {
    const calVal = liveMeta.calibration.calibration.calibrationScore?.toFixed(2) || '0.00';
    sensorCalibration.innerText = calVal;
  }
  
  // Update Device Lock status
  if (liveMeta.calibration && liveMeta.calibration.lockState) {
    const lockActive = liveMeta.calibration.lockState.active;
    deviceLockStatus.innerText = lockActive ? 'ACTIVE' : 'INACTIVE';
    deviceLockStatus.className = lockActive ? 'lock-val active' : 'lock-val inactive';
  }
}

function updateBrainMeshDisplays() {
  if (!liveMeta.brainMesh) return;
  
  const brainMesh = liveMeta.brainMesh;
  
  // Update external mesh status
  meshExternal.innerText = brainMesh.externalDetected ? 'YES' : 'NO';
  meshExternal.style.color = brainMesh.externalDetected ? '#05ffc7' : '#666';
  
  // Update internal mesh status
  meshInternal.innerText = brainMesh.internalActive ? 'YES' : 'NO';
  meshInternal.style.color = brainMesh.internalActive ? '#b927fc' : '#666';
  
  // Update stable nodes count
  meshStable.innerText = brainMesh.stableNodeCount || 0;
  
  // Update equivalent paths count
  meshEquiv.innerText = brainMesh.equivalentPathCount || 0;
  
  // Update mesh shape
  if (brainMesh.externalMesh && brainMesh.externalMesh.shape) {
    meshShape.innerText = brainMesh.externalMesh.shape;
  } else {
    meshShape.innerText = 'DETECTING...';
  }
  
  // Update brain mesh status text
  if (brainMesh.bidirectionalSync) {
    brainMeshStatus.innerText = `SYNC ACTIVE (${(brainMesh.syncQuality * 100).toFixed(0)}%)`;
    brainMeshStatus.classList.add('glow-purple');
  } else {
    brainMeshStatus.innerText = 'SYNC INACTIVE';
    brainMeshStatus.classList.remove('glow-purple');
  }
}

function updateOptimizationDisplays() {
  if (!liveMeta.brainMesh || !liveMeta.brainMesh.dualOptimization) return;
  
  const dualOpt = liveMeta.brainMesh.dualOptimization;
  
  optCycleRate.innerText = dualOpt.cycleRate.toFixed(2);
  optPatternRate.innerText = dualOpt.patternReactionRate.toFixed(2);
  optLevel.innerText = `${(dualOpt.optimizationLevel * 100).toFixed(0)}%`;
  optGhzSync.innerText = `${(dualOpt.ghzSyncRate * 100).toFixed(0)}%`;
  optExternalPace.innerText = dualOpt.externalPace.toFixed(2);
  optInternalPace.innerText = dualOpt.internalPace.toFixed(2);
}

function updateSecurityDisplays() {
  if (!liveMeta.renderSecurity) return;
  
  const security = liveMeta.renderSecurity;
  
  securityLevel.innerText = `${(security.securityLevel * 100).toFixed(0)}%`;
  securityIntegrity.innerText = security.integrityCheck ? 'OK' : 'FAILED';
  securityIntegrity.style.color = security.integrityCheck ? '#05ffc7' : '#ff3b69';
  securityScale.innerText = security.currentScale.toFixed(2);
  securityTokens.innerText = security.activeTokens;
  securityTransition.innerText = security.transitionActive ? 'ACTIVE' : 'INACTIVE';
  securityTransition.style.color = security.transitionActive ? '#ffa500' : '#666';
}

// Console helper functions
function appendConsoleLog(category, message) {
  const line = document.createElement('p');
  line.classList.add('console-line', category.toLowerCase());
  const now = new Date().toLocaleTimeString();
  line.innerText = `[${now}] [${category}] ${message}`;
  consoleLogs.appendChild(line);
  consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

// REST Action calls
async function sendAction(url, data = {}) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await res.json();
  } catch (e) {
    appendConsoleLog('SYSTEM', `Request failed: ${url}`);
  }
}

// Button Events
btnPulsate.addEventListener('click', async () => {
  appendConsoleLog('PULSE', 'Emitting X-ray spectrum pulse through motherboard traces...');
  const res = await sendAction('/api/pulsate');
  if (res.scannedNewTraces) {
    appendConsoleLog('PULSE', 'Delineated trace routes mapped successfully inside mesh.');
  }
});

btnPairTransmit.addEventListener('click', async () => {
  isPairTransmitting = !isPairTransmitting;
  btnPairTransmit.classList.toggle('active', isPairTransmitting);
  btnPairTransmit.innerText = isPairTransmitting ? 'TRANSLATION GATE: ENGAGED' : 'TRANSLATION GATE: ENGAGE';
  appendConsoleLog('GATE', `Translation Gate state updated: ${isPairTransmitting ? 'ENGAGED' : 'RELEASED'}`);
  await sendAction('/api/pair-transmit', { active: isPairTransmitting });
});

btnRecalibrate.addEventListener('click', async () => {
  appendConsoleLog('SYSTEM', 'Running self-authoritative loop recalibrations...');
  const res = await sendAction('/api/recalibrate');
  appendConsoleLog('SYSTEM', `Recalibration finalized. Current Lock Hash: ${res.lock_hash.substr(0, 20)}...`);
});

btnUnlock.addEventListener('click', async () => {
  appendConsoleLog('SYSTEM', 'Releasing all particle locks and resetting translation gates.');
  await sendAction('/api/unlock-all');
  if (isPairTransmitting) {
    isPairTransmitting = false;
    btnPairTransmit.classList.remove('active');
    btnPairTransmit.innerText = 'TRANSLATION GATE: ENGAGE';
  }
});

btnForceLock.addEventListener('click', async () => {
  appendConsoleLog('SENSOR', 'Forcing device lock based on current calibration...');
  const res = await sendAction('/api/force-lock');
  if (res.status === 'lock_forced') {
    appendConsoleLog('SENSOR', `Device lock forced with intensity ${res.lockData.lockIntensity.toFixed(2)}`);
  } else if (res.status === 'error') {
    appendConsoleLog('SENSOR', `Lock failed: ${res.message}`);
  }
});

btnReleaseDeviceLock.addEventListener('click', async () => {
  appendConsoleLog('SENSOR', 'Releasing device lock...');
  const res = await sendAction('/api/release-lock');
  if (res.status === 'lock_released') {
    appendConsoleLog('SENSOR', 'Device lock released successfully');
  }
});

btnSensorStatus.addEventListener('click', async () => {
  const res = await sendAction('/api/sensor-status');
  if (res.status === 'success') {
    appendConsoleLog('SENSOR', `Sensor status: ${Object.keys(res.data).length} sensors active`);
    Object.entries(res.data).forEach(([id, sensor]) => {
      appendConsoleLog('SENSOR', `${id.toUpperCase()}: ${sensor.active ? 'ACTIVE' : 'INACTIVE'}, reading: ${JSON.stringify(sensor.lastReading)}`);
    });
  }
});

btnEnableSync.addEventListener('click', async () => {
  appendConsoleLog('BRAIN MESH', 'Enabling bidirectional sync...');
  const res = await sendAction('/api/enable-bidirectional-sync');
  if (res.status === 'sync_enabled') {
    appendConsoleLog('BRAIN MESH', `Bidirectional sync enabled with quality ${(res.syncState.syncQuality * 100).toFixed(0)}%`);
  }
});

btnDisableSync.addEventListener('click', async () => {
  appendConsoleLog('BRAIN MESH', 'Disabling bidirectional sync...');
  const res = await sendAction('/api/disable-bidirectional-sync');
  if (res.status === 'sync_disabled') {
    appendConsoleLog('BRAIN MESH', 'Bidirectional sync disabled');
  }
});

btnRedetectMesh.addEventListener('click', async () => {
  appendConsoleLog('BRAIN MESH', 'Redetecting brain mesh...');
  const res = await sendAction('/api/redetect-brain-mesh');
  if (res.status === 'mesh_redetected') {
    appendConsoleLog('BRAIN MESH', `Mesh redetected: ${res.data.externalDetected ? 'EXTERNAL' : 'NONE'} detected, ${res.data.stableNodeCount} stable nodes`);
  }
});

btnEnableOpt.addEventListener('click', async () => {
  appendConsoleLog('OPTIMIZATION', 'Enabling optimization cycle...');
  const res = await sendAction('/api/enable-optimization-cycle');
  if (res.status === 'cycle_enabled') {
    appendConsoleLog('OPTIMIZATION', 'Optimization cycle enabled');
  }
});

btnDisableOpt.addEventListener('click', async () => {
  appendConsoleLog('OPTIMIZATION', 'Disabling optimization cycle...');
  const res = await sendAction('/api/disable-optimization-cycle');
  if (res.status === 'cycle_disabled') {
    appendConsoleLog('OPTIMIZATION', 'Optimization cycle disabled');
  }
});

btnSyncCortex.addEventListener('click', async () => {
  appendConsoleLog('OPTIMIZATION', 'Syncing external cortex...');
  const res = await sendAction('/api/sync-cortex');
  if (res.status === 'success' || res.synced) {
    appendConsoleLog('OPTIMIZATION', `Cortex sync completed${res.dispatch?.dispatched ? ' (latch dispatched)' : ''}`);
  }
});

btnLatchDispatch.addEventListener('click', async () => {
  appendConsoleLog('LATCH', 'Dispatching latched capability scripts...');
  const res = await sendAction('/api/latch-dispatch');
  if (res.status === 'success') {
    const d = res.data;
    appendConsoleLog('LATCH', d.dispatched ? `Dispatched latch ${d.latchId}` : `No auto-match (${d.reason || 'manual'})`);
  }
});

btnLatchCreate.addEventListener('click', async () => {
  appendConsoleLog('LATCH', 'Creating capability latch from current Uriel state...');
  const res = await sendAction('/api/latch-create', { trigger: 'manual' });
  if (res.status === 'latched') {
    appendConsoleLog('LATCH', `Latched config ${res.data.latchId.substring(0, 12)}...`);
  }
});

btnLatchStatus.addEventListener('click', async () => {
  const res = await sendAction('/api/latch-status');
  if (res.status === 'success') {
    appendConsoleLog('LATCH', `${res.data.latchCount} latches, ${res.data.stats.dispatches} dispatches`);
  }
});

function updateLatchDisplays() {
  if (!liveMeta.cortexLatch) return;
  const cl = liveMeta.cortexLatch;
  latchCount.innerText = cl.latchCount || 0;
  latchDispatches.innerText = cl.stats?.dispatches || 0;
  latchGated.innerText = cl.stats?.gatedWrites || 0;
  latchAllowed.innerText = cl.stats?.allowedWrites || 0;
}

btnSetSecurity.addEventListener('click', async () => {
  const level = 0.8; // Set high security level
  appendConsoleLog('SECURITY', `Setting security level to ${(level * 100).toFixed(0)}%...`);
  const res = await sendAction('/api/set-security-level', { level });
  if (res.status === 'success') {
    appendConsoleLog('SECURITY', `Security level set to ${(res.securityLevel * 100).toFixed(0)}%`);
  }
});

btnSecureScale.addEventListener('click', async () => {
  const scale = 1.5; // Scale up to 1.5x
  const element = 'mesh';
  appendConsoleLog('SECURITY', `Initiating secure scale for ${element} to ${scale}x...`);
  const res = await sendAction('/api/secure-scale', { element, scale });
  if (res.status === 'success') {
    appendConsoleLog('SECURITY', `Secure scale initiated for ${element}`);
  } else {
    appendConsoleLog('SECURITY', 'Secure scale failed - transition may be active');
  }
});

btnEmergencyReset.addEventListener('click', async () => {
  appendConsoleLog('SECURITY', 'EMERGENCY RESET INITIATED...');
  const res = await sendAction('/api/emergency-reset');
  if (res.status === 'reset_complete') {
    appendConsoleLog('SECURITY', 'Emergency reset completed');
  }
});

// Setup Server-Sent Events stream listener
const eventSource = new EventSource('/api/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Update lists
  liveElectrons = data.electrons;
  liveParticles = data.particles;
  liveElectrodes = data.electrodes;
  liveMeta = data.meta;
  densityLayers = data.meta.densityLayers || {};
  collidingChannelsCount = data.meta.collidingChannels || 0;

  // Update header HUD display counts
  metaVariableW.innerText = liveMeta.variableW.toFixed(4);
  metaLockedCount.innerText = liveMeta.lockStateCount;
  metaThreatLevel.innerText = `${Math.round(liveMeta.threatLevel)}%`;

  // Update Warnings visibility
  xrayWarningBanner.style.display = liveMeta.xRayPulseActive ? 'block' : 'none';

  const gateStatusText = document.getElementById('translation-gate-status');
  if (liveMeta.translationGateActive) {
    gateStatusText.innerText = `PAIR-TO-PAIR STATE: ACTIVE (${(liveMeta.translationGateBending * 100).toFixed(0)}% BEND)`;
    gateStatusText.classList.add('glow-purple');
  } else {
    gateStatusText.innerText = 'PAIR-TO-PAIR STATE: STABLE';
    gateStatusText.classList.remove('glow-purple');
  }

  // Draw panels
  renderLidar();
  renderMesh();
  renderBrain();
  renderSensorPipeline();
  renderBrainMeshSync();
  
  // Update sensor displays
  updateSensorDisplays();
  updateBrainMeshDisplays();
  updateLatchDisplays();
  updateOptimizationDisplays();
  updateSecurityDisplays();
};

eventSource.onerror = () => {
  appendConsoleLog('SYSTEM', 'SSE connection lost. Reconnecting...');
};
