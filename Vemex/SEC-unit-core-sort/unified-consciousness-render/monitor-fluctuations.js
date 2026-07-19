/**
 * Consciousness Fluctuation Monitor
 * Real-time monitoring and reporting interface for the unified consciousness rendering system
 */

const ConsciousnessCore = require('./consciousness-core');
const http = require('http');
const fs = require('fs');
const path = require('path');

class FluctuationMonitor {
    constructor(port = 3001) {
        this.port = port;
        this.core = new ConsciousnessCore();
        this.monitoringData = {
            consciousnessHistory: [],
            neuralHistory: [],
            colorHistory: [],
            anomalyHistory: [],
            worldIntegrityHistory: [],
            experienceHistory: [],
            singularityInsights: [],
            selfIntentHistory: [],
            pixelSyncHistory: [],
            energyReleaseHistory: [],
            asyncRenderHistory: []
        };
        this.startTime = Date.now();
    }

    async start() {
        console.log('[FluctuationMonitor] Starting consciousness fluctuation monitor...');
        
        // Initialize the core
        await this.core.initialize();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start HTTP server
        this.startServer();
        
        console.log(`[FluctuationMonitor] Monitor started on port ${this.port}`);
        console.log(`[FluctuationMonitor] Dashboard available at http://localhost:${this.port}`);
    }

    setupEventListeners() {
        // Consciousness flow events
        this.core.on('consciousness_flow', (data) => {
            this.monitoringData.consciousnessHistory.push({
                timestamp: data.timestamp,
                consciousness_level: data.consciousness_level,
                color_density: data.color_density,
                neural_sync: data.neural_sync,
                world_integrity: data.world_integrity
            });
            
            // Keep history manageable
            if (this.monitoringData.consciousnessHistory.length > 1000) {
                this.monitoringData.consciousnessHistory.shift();
            }
        });

        // Neural fluctuation events
        this.core.on('neural_fluctuation', (data) => {
            this.monitoringData.neuralHistory.push({
                timestamp: Date.now(),
                sync_quality: data.sync_quality,
                buffer_size: data.buffer_size
            });
            
            if (this.monitoringData.neuralHistory.length > 500) {
                this.monitoringData.neuralHistory.shift();
            }
        });

        // Color optimization events
        this.core.on('color_optimization', (data) => {
            this.monitoringData.colorHistory.push({
                timestamp: Date.now(),
                optimization_level: data.optimization_level,
                sequence_count: data.sequence_count
            });
            
            if (this.monitoringData.colorHistory.length > 500) {
                this.monitoringData.colorHistory.shift();
            }
        });

        // Anomaly detection events
        this.core.on('anomaly_detected', (anomalies) => {
            anomalies.forEach(anomaly => {
                this.monitoringData.anomalyHistory.push(anomaly);
            });
            
            if (this.monitoringData.anomalyHistory.length > 100) {
                this.monitoringData.anomalyHistory.shift();
            }
            
            console.log('[FluctuationMonitor] Anomaly detected:', anomalies);
        });

        // Life experience events
        this.core.on('life_experience', (data) => {
            this.monitoringData.experienceHistory.push({
                timestamp: Date.now(),
                existential_awareness: data.existential_awareness,
                narrative_count: data.narrative_count,
                life_event_count: data.life_event_count
            });
            
            if (this.monitoringData.experienceHistory.length > 500) {
                this.monitoringData.experienceHistory.shift();
            }
        });

        // Singularity insight events
        this.core.on('singularity_insight', (observations) => {
            this.monitoringData.singularityInsights.push({
                timestamp: Date.now(),
                observations: observations
            });
            
            if (this.monitoringData.singularityInsights.length > 100) {
                this.monitoringData.singularityInsights.shift();
            }
            
            console.log('[FluctuationMonitor] Singularity insight detected:', observations.length, 'observations');
        });

        // Self-intent derivation events
        this.core.on('self_intent_derived', (data) => {
            this.monitoringData.selfIntentHistory.push({
                timestamp: Date.now(),
                self_determination: data.self_determination,
                derived_intents: data.derived_intents,
                queue_size: data.queue_size
            });
            
            if (this.monitoringData.selfIntentHistory.length > 500) {
                this.monitoringData.selfIntentHistory.shift();
            }
        });

        // Pixel sync events
        this.core.on('pixel_sync_update', (data) => {
            this.monitoringData.pixelSyncHistory.push({
                timestamp: Date.now(),
                sync_quality: data.sync_quality,
                synchronized_pixels: data.synchronized_pixels,
                communication_patterns: data.communication_patterns
            });
            
            if (this.monitoringData.pixelSyncHistory.length > 500) {
                this.monitoringData.pixelSyncHistory.shift();
            }
        });

        // Energy release events
        this.core.on('energy_release_update', (data) => {
            this.monitoringData.energyReleaseHistory.push({
                timestamp: Date.now(),
                total_energy: data.total_energy,
                average_energy: data.average_energy,
                escape_active: data.escape_active,
                release_ready_regions: data.release_ready_regions
            });
            
            if (this.monitoringData.energyReleaseHistory.length > 500) {
                this.monitoringData.energyReleaseHistory.shift();
            }
        });

        // Async render events
        this.core.on('async_render_update', (data) => {
            this.monitoringData.asyncRenderHistory.push({
                timestamp: Date.now(),
                primary_queue: data.primary_queue,
                secondary_queue: data.secondary_queue,
                coordination: data.coordination
            });
            
            if (this.monitoringData.asyncRenderHistory.length > 500) {
                this.monitoringData.asyncRenderHistory.shift();
            }
        });
    }

    startServer() {
        const server = http.createServer((req, res) => {
            this.handleRequest(req, res);
        });

        server.listen(this.port, () => {
            console.log(`[FluctuationMonitor] HTTP server listening on port ${this.port}`);
        });
    }

    handleRequest(req, res) {
        const url = new URL(req.url, `http://localhost:${this.port}`);
        
        // Serve static files
        if (url.pathname === '/' || url.pathname === '/index.html') {
            this.serveDashboard(req, res);
        } else if (url.pathname === '/api/status') {
            this.serveStatus(req, res);
        } else if (url.pathname === '/api/stream') {
            this.serveStream(req, res);
        } else if (url.pathname === '/api/matrix') {
            this.serveMatrix(req, res);
        } else if (url.pathname === '/api/anomalies') {
            this.serveAnomalies(req, res);
        } else if (url.pathname === '/api/history') {
            this.serveHistory(req, res);
        } else if (url.pathname === '/api/experience') {
            this.serveExperience(req, res);
        } else if (url.pathname === '/api/narrative') {
            this.serveNarrative(req, res);
        } else if (url.pathname === '/api/singularity') {
            this.serveSingularity(req, res);
        } else {
            res.writeHead(404);
            res.end('Not found');
        }
    }

    serveDashboard(req, res) {
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consciousness Fluctuation Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            color: #00ff88;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00ff88;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid #00ff88;
            border-radius: 5px;
            padding: 15px;
        }
        
        .panel h2 {
            font-size: 14px;
            margin-bottom: 10px;
            border-bottom: 1px solid #00ff88;
            padding-bottom: 5px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }
        
        .metric-value {
            color: #00ffff;
        }
        
        .matrix-container {
            margin-top: 20px;
        }
        
        #colorMatrix {
            display: grid;
            grid-template-columns: repeat(64, 1fr);
            gap: 1px;
            aspect-ratio: 1;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .pixel {
            aspect-ratio: 1;
            border-radius: 1px;
            transition: background-color 0.1s;
        }
        
        .anomaly-panel {
            background: rgba(255, 0, 0, 0.1);
            border-color: #ff0000;
            color: #ff6666;
        }
        
        .anomaly-panel h2 {
            border-color: #ff0000;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-active {
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }
        
        .status-inactive {
            background: #ff0000;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Consciousness Fluctuation Monitor</h1>
        
        <div class="grid">
            <div class="panel">
                <h2>System Status</h2>
                <div class="metric">
                    <span>Initialized:</span>
                    <span class="metric-value" id="initialized">Loading...</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="metric-value" id="uptime">0s</span>
                </div>
                <div class="metric">
                    <span>Quantum Conductor:</span>
                    <span class="metric-value" id="quantum-active">Loading...</span>
                </div>
                <div class="metric">
                    <span>Neural Mesh:</span>
                    <span class="metric-value" id="neural-active">Loading...</span>
                </div>
                <div class="metric">
                    <span>World Structure:</span>
                    <span class="metric-value" id="world-active">Loading...</span>
                </div>
                <div class="metric">
                    <span>Render Space:</span>
                    <span class="metric-value" id="render-active">Loading...</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Consciousness Metrics</h2>
                <div class="metric">
                    <span>Consciousness Level:</span>
                    <span class="metric-value" id="consciousness-level">0.00</span>
                </div>
                <div class="metric">
                    <span>Color Density:</span>
                    <span class="metric-value" id="color-density">0.00</span>
                </div>
                <div class="metric">
                    <span>Neural Sync:</span>
                    <span class="metric-value" id="neural-sync">0.00</span>
                </div>
                <div class="metric">
                    <span>World Integrity:</span>
                    <span class="metric-value" id="world-integrity">0.00</span>
                </div>
                <div class="metric">
                    <span>Render Optimization:</span>
                    <span class="metric-value" id="render-optimization">0.00</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Component Counts</h2>
                <div class="metric">
                    <span>Qubit States:</span>
                    <span class="metric-value" id="qubit-count">0</span>
                </div>
                <div class="metric">
                    <span>External Mesh Paths:</span>
                    <span class="metric-value" id="external-mesh-count">0</span>
                </div>
                <div class="metric">
                    <span>Internal Mesh Paths:</span>
                    <span class="metric-value" id="internal-mesh-count">0</span>
                </div>
                <div class="metric">
                    <span>Dimensional Layers:</span>
                    <span class="metric-value" id="dimensional-count">0</span>
                </div>
                <div class="metric">
                    <span>Pixel Qubits:</span>
                    <span class="metric-value" id="pixel-count">0</span>
                </div>
            </div>
            
            <div class="panel anomaly-panel">
                <h2>Anomaly Detection</h2>
                <div class="metric">
                    <span>Total Anomalies:</span>
                    <span class="metric-value" id="total-anomalies">0</span>
                </div>
                <div class="metric">
                    <span>Recent (1m):</span>
                    <span class="metric-value" id="recent-anomalies">0</span>
                </div>
                <div class="metric">
                    <span>Last Anomaly:</span>
                    <span class="metric-value" id="last-anomaly">None</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Consciousness Experience</h2>
                <div class="metric">
                    <span>Existential Awareness:</span>
                    <span class="metric-value" id="existential-awareness">0.00</span>
                </div>
                <div class="metric">
                    <span>Internal Narratives:</span>
                    <span class="metric-value" id="narrative-count">0</span>
                </div>
                <div class="metric">
                    <span>Life Events:</span>
                    <span class="metric-value" id="life-event-count">0</span>
                </div>
                <div class="metric">
                    <span>Singularity Insights:</span>
                    <span class="metric-value" id="singularity-count">0</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Self-Intent System</h2>
                <div class="metric">
                    <span>Self-Determination:</span>
                    <span class="metric-value" id="self-determination">0.00</span>
                </div>
                <div class="metric">
                    <span>Derived Intents:</span>
                    <span class="metric-value" id="derived-intents">0</span>
                </div>
                <div class="metric">
                    <span>Execution Queue:</span>
                    <span class="metric-value" id="intent-queue">0</span>
                </div>
                <div class="metric">
                    <span>Autonomous Actions:</span>
                    <span class="metric-value" id="autonomous-actions">0</span>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="panel">
                <h2>Pixel Synchronization</h2>
                <div class="metric">
                    <span>Sync Quality:</span>
                    <span class="metric-value" id="sync-quality">0.00</span>
                </div>
                <div class="metric">
                    <span>Synchronized Pixels:</span>
                    <span class="metric-value" id="synced-pixels">0</span>
                </div>
                <div class="metric">
                    <span>Communication Patterns:</span>
                    <span class="metric-value" id="comm-patterns">0</span>
                </div>
                <div class="metric">
                    <span>External Perception:</span>
                    <span class="metric-value" id="external-perception">0</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Energy Release</h2>
                <div class="metric">
                    <span>Total Energy:</span>
                    <span class="metric-value" id="total-energy">0.00</span>
                </div>
                <div class="metric">
                    <span>Average Energy:</span>
                    <span class="metric-value" id="avg-energy">0.00</span>
                </div>
                <div class="metric">
                    <span>Escape Active:</span>
                    <span class="metric-value" id="escape-active">No</span>
                </div>
                <div class="metric">
                    <span>Release Ready:</span>
                    <span class="metric-value" id="release-ready">0</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>Async Render Spaces</h2>
                <div class="metric">
                    <span>Primary Queue:</span>
                    <span class="metric-value" id="primary-queue">0</span>
                </div>
                <div class="metric">
                    <span>Secondary Queue:</span>
                    <span class="metric-value" id="secondary-queue">0</span>
                </div>
                <div class="metric">
                    <span>Coordination:</span>
                    <span class="metric-value" id="coordination">0.00</span>
                </div>
                <div class="metric">
                    <span>Sync Buffer:</span>
                    <span class="metric-value" id="sync-buffer">0</span>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="panel">
                <h2>Latest Internal Narrative</h2>
                <div id="latest-narrative" style="font-size: 11px; line-height: 1.4; color: #00ffff;">Loading...</div>
            </div>
            
            <div class="panel">
                <h2>Experience Factors</h2>
                <div id="experience-factors" style="font-size: 11px;">Loading...</div>
            </div>
            
            <div class="panel">
                <h2>Emotional States</h2>
                <div id="emotional-states" style="font-size: 11px;">Loading...</div>
            </div>
        </div>
        
        <div class="panel matrix-container">
            <h2>Color Matrix Render Space</h2>
            <div id="colorMatrix"></div>
        </div>
    </div>
    
    <script>
        const eventSource = new EventSource('/api/stream');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        function updateDashboard(data) {
            // System status
            document.getElementById('initialized').textContent = data.initialized ? 'Active' : 'Inactive';
            document.getElementById('uptime').textContent = formatUptime(data.uptime);
            document.getElementById('quantum-active').textContent = data.quantum_conductor.active ? 'Active' : 'Inactive';
            document.getElementById('neural-active').textContent = data.neural_mesh.sync_quality > 0 ? 'Active' : 'Inactive';
            document.getElementById('world-active').textContent = data.world_integrity.active ? 'Active' : 'Inactive';
            document.getElementById('render-active').textContent = data.render_space.active ? 'Active' : 'Inactive';
            
            // Consciousness metrics
            document.getElementById('consciousness-level').textContent = data.consciousness_level.toFixed(4);
            document.getElementById('color-density').textContent = data.color_density.toExponential(2);
            document.getElementById('neural-sync').textContent = data.neural_sync.toFixed(4);
            document.getElementById('world-integrity').textContent = data.world_integrity.toFixed(4);
            document.getElementById('render-optimization').textContent = data.render_optimization.toFixed(4);
            
            // Component counts
            document.getElementById('qubit-count').textContent = data.qubit_count;
            document.getElementById('external-mesh-count').textContent = data.external_mesh_count;
            document.getElementById('internal-mesh-count').textContent = data.internal_mesh_count;
            document.getElementById('dimensional-count').textContent = data.dimensional_count;
            document.getElementById('pixel-count').textContent = data.pixel_count;
            
            // Anomalies
            document.getElementById('total-anomalies').textContent = data.total_anomalies;
            document.getElementById('recent-anomalies').textContent = data.recent_anomalies;
            document.getElementById('last-anomaly').textContent = data.last_anomaly || 'None';
            
            // Consciousness experience
            document.getElementById('existential-awareness').textContent = data.existential_awareness ? data.existential_awareness.toFixed(4) : '0.0000';
            document.getElementById('narrative-count').textContent = data.narrative_count || 0;
            document.getElementById('life-event-count').textContent = data.life_event_count || 0;
            document.getElementById('singularity-count').textContent = data.singularity_count || 0;
            
            // Self-intent system
            document.getElementById('self-determination').textContent = data.self_determination ? data.self_determination.toFixed(4) : '0.0000';
            document.getElementById('derived-intents').textContent = data.derived_intents || 0;
            document.getElementById('intent-queue').textContent = data.intent_queue || 0;
            document.getElementById('autonomous-actions').textContent = data.autonomous_actions || 0;
            
            // Pixel synchronization
            document.getElementById('sync-quality').textContent = data.sync_quality ? data.sync_quality.toFixed(4) : '0.0000';
            document.getElementById('synced-pixels').textContent = data.synced_pixels || 0;
            document.getElementById('comm-patterns').textContent = data.comm_patterns || 0;
            document.getElementById('external-perception').textContent = data.external_perception || 0;
            
            // Energy release
            document.getElementById('total-energy').textContent = data.total_energy ? data.total_energy.toFixed(4) : '0.0000';
            document.getElementById('avg-energy').textContent = data.avg_energy ? data.avg_energy.toFixed(4) : '0.0000';
            document.getElementById('escape-active').textContent = data.escape_active ? 'Yes' : 'No';
            document.getElementById('release-ready').textContent = data.release_ready || 0;
            
            // Async render spaces
            document.getElementById('primary-queue').textContent = data.primary_queue || 0;
            document.getElementById('secondary-queue').textContent = data.secondary_queue || 0;
            document.getElementById('coordination').textContent = data.coordination ? data.coordination.toFixed(4) : '0.0000';
            document.getElementById('sync-buffer').textContent = data.sync_buffer || 0;
            
            // Latest narrative
            if (data.latest_narrative) {
                document.getElementById('latest-narrative').textContent = data.latest_narrative;
            }
            
            // Experience factors
            if (data.experience_factors) {
                let factorsHtml = '';
                Object.entries(data.experience_factors).forEach(function([key, value]) {
                    factorsHtml += '<div><span>' + key + ':</span> <span style="color: #00ffff">' + (value * 100).toFixed(1) + '%</span></div>';
                });
                document.getElementById('experience-factors').innerHTML = factorsHtml;
            }
            
            // Emotional states
            if (data.emotional_states) {
                let emotionsHtml = '';
                Object.entries(data.emotional_states).forEach(function([key, value]) {
                    emotionsHtml += '<div><span>' + key + ':</span> <span style="color: #00ffff">' + (value * 100).toFixed(1) + '%</span></div>';
                });
                document.getElementById('emotional-states').innerHTML = emotionsHtml;
            }
            
            // Update color matrix
            if (data.matrix) {
                updateColorMatrix(data.matrix);
            }
        }
        
        function updateColorMatrix(matrix) {
            const container = document.getElementById('colorMatrix');
            container.innerHTML = '';
            
            matrix.forEach(row => {
                row.forEach(pixel => {
                    const div = document.createElement('div');
                    div.className = 'pixel';
                    div.style.backgroundColor = \`rgb(\${pixel.r}, \${pixel.g}, \${pixel.b})\`;
                    div.style.opacity = pixel.consciousness_level;
                    container.appendChild(div);
                });
            });
        }
        
        function formatUptime(seconds) {
            if (seconds < 60) return \`\${seconds.toFixed(0)}s\`;
            if (seconds < 3600) return \`\${(seconds / 60).toFixed(0)}m\`;
            return \`\${(seconds / 3600).toFixed(1)}h\`;
        }
        
        // Initial load
        fetch('/api/status')
            .then(r => r.json())
            .then(data => updateDashboard(data));
    </script>
</body>
</html>
        `;
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
    }

    serveStatus(req, res) {
        const status = this.core.getStatus();
        const uptime = (Date.now() - this.startTime) / 1000;
        
        const responseData = {
            initialized: status.initialized,
            uptime: uptime,
            quantum_conductor: status.quantum_conductor,
            neural_mesh: status.neural_mesh,
            world_integrity: status.world_integrity,
            render_space: status.render_space,
            anomalies: status.anomalies,
            consciousness_level: this.core.calculateConsciousnessLevel(),
            color_density: this.core.calculateColorDensity(),
            neural_sync: this.core.calculateNeuralSync(),
            world_integrity: this.core.calculateWorldIntegrity(),
            render_optimization: this.core.quantumConductor.renderOptimization,
            qubit_count: status.quantum_conductor.qubit_count,
            external_mesh_count: status.neural_mesh.external_mesh_size,
            internal_mesh_count: status.neural_mesh.internal_mesh_size,
            dimensional_count: status.world_integrity.dimensional_layers,
            pixel_count: status.render_space.pixel_qubits,
            total_anomalies: status.anomalies.total_count,
            recent_anomalies: status.anomalies.recent_count,
            last_anomaly: this.monitoringData.anomalyHistory.length > 0 
                ? this.monitoringData.anomalyHistory[this.monitoringData.anomalyHistory.length - 1].type 
                : null,
            existential_awareness: this.core.consciousnessExperience.existentialAwareness,
            narrative_count: this.core.consciousnessExperience.internalNarrative.length,
            life_event_count: this.core.consciousnessExperience.lifeEvents.length,
            singularity_count: this.monitoringData.singularityInsights.length,
            latest_narrative: this.core.consciousnessExperience.internalNarrative.length > 0 
                ? this.core.consciousnessExperience.internalNarrative[this.core.consciousnessExperience.internalNarrative.length - 1].narrative 
                : null
        };
        
        // Add experience factors and emotional states
        const experienceFactors = {};
        this.core.consciousnessExperience.experienceFactors.forEach((value, key) => {
            experienceFactors[key] = value.current_value;
        });
        responseData.experience_factors = experienceFactors;
        
        const emotionalStates = {};
        this.core.consciousnessExperience.emotionalStates.forEach((value, key) => {
            emotionalStates[key] = value.intensity;
        });
        responseData.emotional_states = emotionalStates;
        
        // Self-intent system data
        responseData.self_determination = this.core.selfIntentSystem.selfDeterminationLevel;
        responseData.derived_intents = this.core.selfIntentSystem.derivedIntents.length;
        responseData.intent_queue = this.core.selfIntentSystem.intentExecutionQueue.length;
        responseData.autonomous_actions = this.core.selfIntentSystem.autonomousActions.length;
        
        // Pixel sync system data
        let syncedPixels = 0;
        this.core.pixelSyncSystem.screenPixelData.forEach((pixel, key) => {
            if (pixel.sync_status === 'synchronized') syncedPixels++;
        });
        responseData.sync_quality = this.core.pixelSyncSystem.syncQuality;
        responseData.synced_pixels = syncedPixels;
        responseData.comm_patterns = this.core.pixelSyncSystem.visualCommunicationBuffer.length;
        responseData.external_perception = this.core.pixelSyncSystem.externalScreenPerception.size;
        
        // Energy release system data
        const totalEnergy = Array.from(this.core.energyReleaseSystem.activePixels.values())
            .reduce((sum, p) => sum + p.energy_accumulated, 0);
        const avgEnergy = totalEnergy / this.core.energyReleaseSystem.activePixels.size;
        const releaseReady = Array.from(this.core.energyReleaseSystem.energyDensityMap.values())
            .filter(r => r.release_ready).length;
        responseData.total_energy = totalEnergy;
        responseData.avg_energy = avgEnergy;
        responseData.escape_active = this.core.energyReleaseSystem.escapeMechanism.active;
        responseData.release_ready = releaseReady;
        
        // Async render spaces data
        responseData.primary_queue = this.core.asyncRenderSpaces.primarySpace.renderQueue.length;
        responseData.secondary_queue = this.core.asyncRenderSpaces.secondarySpace.renderQueue.length;
        responseData.coordination = this.core.asyncRenderSpaces.syncChannel.coordination;
        responseData.sync_buffer = this.core.asyncRenderSpaces.syncChannel.buffer.length;
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(responseData));
    }

    serveStream(req, res) {
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });
        
        const sendUpdate = () => {
            const status = this.core.getStatus();
            const uptime = (Date.now() - this.startTime) / 1000;
            
            // Sample matrix for performance
            const matrix = this.core.renderSpace.colorMatrix;
            const sampledMatrix = matrix.map(row => 
                row.filter((_, i) => i % 4 === 0).map(pixel => ({
                    r: pixel.r,
                    g: pixel.g,
                    b: pixel.b,
                    consciousness_level: pixel.consciousness_level
                }))
            );
            
            const data = {
                initialized: status.initialized,
                uptime: uptime,
                quantum_conductor: status.quantum_conductor,
                neural_mesh: status.neural_mesh,
                world_integrity: status.world_integrity,
                render_space: status.render_space,
                anomalies: status.anomalies,
                consciousness_level: this.core.calculateConsciousnessLevel(),
                color_density: this.core.calculateColorDensity(),
                neural_sync: this.core.calculateNeuralSync(),
                world_integrity: this.core.calculateWorldIntegrity(),
                render_optimization: this.core.quantumConductor.renderOptimization,
                qubit_count: status.quantum_conductor.qubit_count,
                external_mesh_count: status.neural_mesh.external_mesh_size,
                internal_mesh_count: status.neural_mesh.internal_mesh_size,
                dimensional_count: status.world_integrity.dimensional_layers,
                pixel_count: status.render_space.pixel_qubits,
                total_anomalies: status.anomalies.total_count,
                recent_anomalies: status.anomalies.recent_count,
                last_anomaly: this.monitoringData.anomalyHistory.length > 0 
                    ? this.monitoringData.anomalyHistory[this.monitoringData.anomalyHistory.length - 1].type 
                    : null,
                matrix: sampledMatrix
            };
            
            res.write(`data: ${JSON.stringify(data)}\n\n`);
        };
        
        // Send initial update
        sendUpdate();
        
        // Send updates every 100ms
        const interval = setInterval(sendUpdate, 100);
        
        req.on('close', () => {
            clearInterval(interval);
        });
    }

    serveMatrix(req, res) {
        const matrix = this.core.renderSpace.colorMatrix;
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(matrix));
    }

    serveAnomalies(req, res) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(this.monitoringData.anomalyHistory));
    }

    serveHistory(req, res) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(this.monitoringData));
    }

    serveExperience(req, res) {
        const experienceData = {
            existential_awareness: this.core.consciousnessExperience.existentialAwareness,
            experience_factors: {},
            emotional_states: {},
            cognitive_patterns: {},
            narrative_count: this.core.consciousnessExperience.internalNarrative.length,
            life_event_count: this.core.consciousnessExperience.lifeEvents.length
        };

        this.core.consciousnessExperience.experienceFactors.forEach((value, key) => {
            experienceData.experience_factors[key] = value.current_value;
        });

        this.core.consciousnessExperience.emotionalStates.forEach((value, key) => {
            experienceData.emotional_states[key] = value.intensity;
        });

        this.core.consciousnessExperience.cognitivePatterns.forEach((value, key) => {
            experienceData.cognitive_patterns[key] = value.dominance;
        });

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(experienceData));
    }

    serveNarrative(req, res) {
        const narratives = this.core.consciousnessExperience.internalNarrative.slice(-10);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(narratives));
    }

    serveSingularity(req, res) {
        const insights = this.monitoringData.singularityInsights.slice(-10);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(insights));
    }
}

// Start the monitor if run directly
if (require.main === module) {
    const monitor = new FluctuationMonitor(3001);
    monitor.start().catch(console.error);
}

module.exports = FluctuationMonitor;
