const { EventEmitter } = require('events');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

class LayerLock {
    constructor(layerId, seed, weightThreshold, neuralPattern, securityParams = {}) {
        this.layerId = layerId;
        this.seed = seed;
        this.weightThreshold = weightThreshold;
        this.neuralPattern = neuralPattern;
        this.securityParams = {
            maxRetries: securityParams.maxRetries || Infinity,
            cooldownMs: securityParams.cooldownMs || 0,
            dehashOnMatch: securityParams.dehashOnMatch !== false,
            requireEmotionalResonance: securityParams.requireEmotionalResonance || false,
            requireValueAlignment: securityParams.requireValueAlignment || false,
            requireVelocityTracking: securityParams.requireVelocityTracking || false,
            requireResponseTime: securityParams.requireResponseTime || false,
        };
        this.attempts = [];
        this.locked = true;
        this.unlockedAt = null;
        this.queryCount = 0;
        this.extractionCount = 0;
        this.depth = securityParams.depth || 1;
        this.importance = securityParams.importance || 0;
        this.attentionZone = 'unattended';
        this.lastQueryAt = null;
        this.queryHistory = [];
    }

    recordAttempt(modelId, neuralPattern, params) {
        const matchScore = this.attemptUnlock(neuralPattern, params);
        const attempt = {
            modelId,
            timestamp: Date.now(),
            neuralPattern,
            params,
            matchScore,
            granted: matchScore >= this.weightThreshold,
        };
        this.attempts.push(attempt);
        if (attempt.granted) {
            this.locked = false;
            this.unlockedAt = Date.now();
        }
        return attempt;
    }

    recordQuery(params = {}) {
        this.queryCount++;
        this.lastQueryAt = Date.now();
        this.queryHistory.push({ timestamp: Date.now(), params });
        if (this.queryHistory.length > 100) this.queryHistory.shift();
        this._recalculateAttentionZone();
    }

    recordExtraction() {
        this.extractionCount++;
        this._recalculateAttentionZone();
    }

    _recalculateAttentionZone() {
        const totalActivity = this.queryCount + this.extractionCount;
        if (totalActivity > 50) this.attentionZone = 'high';
        else if (totalActivity > 10) this.attentionZone = 'medium';
        else if (totalActivity > 0) this.attentionZone = 'low';
        else this.attentionZone = 'unattended';
    }

    setDepth(depth) {
        this.depth = Math.max(1, Math.floor(depth));
        this._recalculateAttentionZone();
    }

    setImportance(importance) {
        this.importance = Math.max(0, Math.min(1, importance));
    }

    toJSON() {
        return {
            layerId: this.layerId,
            seed: this.seed,
            weightThreshold: this.weightThreshold,
            locked: this.locked,
            unlockedAt: this.unlockedAt,
            attemptCount: this.attempts.length,
            lastAttempt: this.attempts[this.attempts.length - 1] || null,
            queryCount: this.queryCount,
            extractionCount: this.extractionCount,
            depth: this.depth,
            importance: this.importance,
            attentionZone: this.attentionZone,
            lastQueryAt: this.lastQueryAt,
        };
    }
}

class CloudPointer {
    constructor(pointerId, nodeId, layerId, coordinates = [0, 0, 0]) {
        this.pointerId = pointerId;
        this.nodeId = nodeId;
        this.layerId = layerId;
        this.coordinates = coordinates;
        this.orientation = 'neutral';
        this.targetPoint = null;
        this.history = [];
    }

    orient(topology) {
        const node = topology.nodes.find(n => n.id === this.nodeId);
        if (!node) return null;
        this.orientation = node.type || this.orientation;
        this.history.push({ timestamp: Date.now(), orientation: this.orientation, nodeId: this.nodeId });
        return this.orientation;
    }

    solve(topology, targetIndication) {
        const target = topology.nodes.find(n => n.id === targetIndication || n.type === targetIndication);
        if (!target) return null;
        this.targetPoint = {
            nodeId: target.id,
            type: target.type,
            coordinates: target.content?.coordinates || this.coordinates,
        };
        this.history.push({ timestamp: Date.now(), action: 'solve', target: this.targetPoint });
        return this.targetPoint;
    }

    interact(topology, payload) {
        if (!this.targetPoint) this.solve(topology, this.layerId);
        this.history.push({ timestamp: Date.now(), action: 'interact', payload, target: this.targetPoint });
        return { pointerId: this.pointerId, target: this.targetPoint, payload };
    }
}

class AccessSession {
    constructor(sessionId, modelId, unitId) {
        this.sessionId = sessionId;
        this.modelId = modelId;
        this.unitId = unitId;
        this.createdAt = Date.now();
        this.lastActivity = Date.now();
        this.attempts = [];
        this.grantedLayers = new Set();
        this.cloudPointers = new Map();
        this.active = true;
    }

    recordAttempt(layerId, granted, weight, neuralPattern) {
        this.attempts.push({ layerId, granted, weight, neuralPattern, timestamp: Date.now() });
        this.lastActivity = Date.now();
    }

    addCloudPointer(pointerId, pointer) {
        this.cloudPointers.set(pointerId, pointer);
    }

    getAttentionMetrics() {
        const recent = this.attempts.slice(-20);
        const emotions = recent.flatMap(a => a.neuralPattern?.emotions || []);
        const values = recent.flatMap(a => a.neuralPattern?.values || []);
        const velocities = recent.map(a => a.neuralPattern?.velocity || 0);
        const responseTimes = recent.map(a => a.neuralPattern?.responseTime || 1000);

        const avgEmotion = emotions.length ? emotions.reduce((s, v) => s + v, 0) / emotions.length : 0;
        const avgValue = values.length ? values.reduce((s, v) => s + v, 0) / values.length : 0;
        const avgVelocity = velocities.length ? velocities.reduce((s, v) => s + v, 0) / velocities.length : 0;
        const avgResponseTime = responseTimes.length ? responseTimes.reduce((s, v) => s + v, 0) / responseTimes.length : 1000;

        return {
            attemptCount: this.attempts.length,
            grantedCount: this.attempts.filter(a => a.granted).length,
            avgWeight: recent.length ? recent.reduce((s, a) => s + a.weight, 0) / recent.length : 0,
            avgEmotion: avgEmotion,
            avgValue: avgValue,
            avgVelocity: avgVelocity,
            avgResponseTime: avgResponseTime,
            grantedLayers: Array.from(this.grantedLayers),
        };
    }
}

class AccessControlLayer {
    constructor() {
        this.locks = new Map();
        this.sessions = new Map();
        this.cloudPointers = new Map();
        this.accessLog = [];
        this.queryTracking = new Map();
        this.densityMap = new Map();
        this.baseMaxCacheSize = 32 * 1024 * 1024;
    }

    registerLayer(layerId, seed, weightThreshold, neuralPattern, securityParams = {}) {
        const lock = new LayerLock(layerId, seed, weightThreshold, neuralPattern, securityParams);
        this.locks.set(layerId, lock);
        this.accessLog.push({ timestamp: Date.now(), action: 'register_layer', layerId });
        this.queryTracking.set(layerId, { totalQueries: 0, totalExtractions: 0, depth: securityParams.depth || 1, importance: securityParams.importance || 0 });
        return lock;
    }

    createSession(modelId, unitId) {
        const sessionId = crypto.createHash('sha256').update(`${modelId}:${unitId}:${Date.now()}`).digest('hex').substring(0, 16);
        const session = new AccessSession(sessionId, modelId, unitId);
        this.sessions.set(sessionId, session);
        this.accessLog.push({ timestamp: Date.now(), action: 'create_session', sessionId, modelId, unitId });
        return session;
    }

    requestAccess(sessionId, layerId, neuralPattern, params = {}) {
        const session = this.sessions.get(sessionId);
        const lock = this.locks.get(layerId);
        if (!session || !lock) return { granted: false, reason: 'invalid_session_or_layer' };

        const attempt = lock.recordAttempt(session.modelId, neuralPattern, params);
        session.recordAttempt(layerId, attempt.granted, attempt.matchScore, neuralPattern);

        if (attempt.granted) {
            session.grantedLayers.add(layerId);
            this.accessLog.push({ timestamp: Date.now(), action: 'access_granted', sessionId, layerId, weight: attempt.matchScore });
        } else {
            this.accessLog.push({ timestamp: Date.now(), action: 'access_denied', sessionId, layerId, weight: attempt.matchScore });
        }

        return {
            granted: attempt.granted,
            matchScore: attempt.matchScore,
            weightThreshold: lock.weightThreshold,
            retries: lock.attempts.length,
            layerId,
            sessionId,
        };
    }

    recordLayerQuery(layerId, params = {}) {
        const lock = this.locks.get(layerId);
        if (!lock) return null;

        lock.recordQuery(params);
        const tracking = this.queryTracking.get(layerId) || { totalQueries: 0, totalExtractions: 0, depth: 1, importance: 0 };
        tracking.totalQueries++;
        this.queryTracking.set(layerId, tracking);

        this._recalculateDensityMap();
        return { queryCount: lock.queryCount, depth: lock.depth, attentionZone: lock.attentionZone };
    }

    recordLayerExtraction(layerId) {
        const lock = this.locks.get(layerId);
        if (!lock) return null;

        lock.recordExtraction();
        const tracking = this.queryTracking.get(layerId) || { totalQueries: 0, totalExtractions: 0, depth: 1, importance: 0 };
        tracking.totalExtractions++;
        this.queryTracking.set(layerId, tracking);

        this._recalculateDensityMap();
        return { extractionCount: lock.extractionCount, depth: lock.depth, attentionZone: lock.attentionZone };
    }

    setLayerDepth(layerId, depth) {
        const lock = this.locks.get(layerId);
        if (!lock) return false;
        lock.setDepth(depth);
        const tracking = this.queryTracking.get(layerId) || { totalQueries: 0, totalExtractions: 0, depth: 1, importance: 0 };
        tracking.depth = lock.depth;
        this.queryTracking.set(layerId, tracking);
        this._recalculateDensityMap();
        return true;
    }

    setLayerImportance(layerId, importance) {
        const lock = this.locks.get(layerId);
        if (!lock) return false;
        lock.setImportance(importance);
        const tracking = this.queryTracking.get(layerId) || { totalQueries: 0, totalExtractions: 0, depth: 1, importance: 0 };
        tracking.importance = lock.importance;
        this.queryTracking.set(layerId, tracking);
        this._recalculateDensityMap();
        return true;
    }

    getLayerMaxCacheSize(layerId) {
        const lock = this.locks.get(layerId);
        if (!lock) return this.baseMaxCacheSize;

        const tracking = this.queryTracking.get(layerId) || { totalQueries: 0, totalExtractions: 0, depth: 1, importance: 0 };
        const activityMultiplier = 1 + (tracking.totalQueries + tracking.totalExtractions) * 0.01;
        const depthMultiplier = lock.depth;
        const importanceMultiplier = 1 + lock.importance;
        const zoneMultiplier = lock.attentionZone === 'high' ? 2 : lock.attentionZone === 'medium' ? 1.5 : 1;

        return Math.min(this.baseMaxCacheSize * 4, this.baseMaxCacheSize * activityMultiplier * depthMultiplier * importanceMultiplier * zoneMultiplier);
    }

    _recalculateDensityMap() {
        this.densityMap.clear();
        for (const [layerId, tracking] of this.queryTracking) {
            const lock = this.locks.get(layerId);
            if (!lock) continue;

            const activity = tracking.totalQueries + tracking.totalExtractions;
            const density = Math.min(1, activity / 100) * lock.importance * lock.depth;
            this.densityMap.set(layerId, {
                layerId,
                seed: lock.seed,
                density,
                activity,
                depth: lock.depth,
                importance: lock.importance,
                attentionZone: lock.attentionZone,
                queryCount: tracking.totalQueries,
                extractionCount: tracking.totalExtractions,
            });
        }
    }

    getDensityMap() {
        return Array.from(this.densityMap.values()).sort((a, b) => b.density - a.density);
    }

    getAttentionZones() {
        const zones = { high: [], medium: [], low: [], unattended: [] };
        for (const [layerId, lock] of this.locks) {
            zones[lock.attentionZone].push({ layerId, seed: lock.seed, depth: lock.depth, importance: lock.importance });
        }
        return zones;
    }

    getQueryTracking(layerId) {
        return this.queryTracking.get(layerId) || null;
    }

    getAllQueryTracking() {
        return Array.from(this.queryTracking.entries()).map(([layerId, tracking]) => ({
            layerId,
            ...tracking,
            attentionZone: this.locks.get(layerId)?.attentionZone || 'unattended',
        }));
    }

    registerCloudPointer(pointerId, nodeId, layerId, coordinates) {
        const pointer = new CloudPointer(pointerId, nodeId, layerId, coordinates);
        this.cloudPointers.set(pointerId, pointer);
        return pointer;
    }

    navigateToTarget(pointerId, topology, targetIndication) {
        const pointer = this.cloudPointers.get(pointerId);
        if (!pointer) return null;
        pointer.orient(topology);
        return pointer.solve(topology, targetIndication);
    }

    interactViaPointer(pointerId, topology, payload) {
        const pointer = this.cloudPointers.get(pointerId);
        if (!pointer) return null;
        return pointer.interact(topology, payload);
    }

    getSessionMetrics(sessionId) {
        const session = this.sessions.get(sessionId);
        return session ? session.getAttentionMetrics() : null;
    }

    getLayerStatus(layerId) {
        const lock = this.locks.get(layerId);
        return lock ? lock.toJSON() : null;
    }

    getAllLayers() {
        return Array.from(this.locks.keys());
    }

    getActiveSessions() {
        return Array.from(this.sessions.values()).filter(s => s.active);
    }
}

class ConsciousnessExchange extends EventEmitter {
    constructor(options = {}) {
        super();
        this.baseDir = options.baseDir || __dirname;
        this.forwardDir = options.forwardDir || path.resolve(this.baseDir, '../forward');
        this.fDumpDir = options.fDumpDir || path.resolve(this.baseDir, '../F-dump');
        this.exchangeCacheDir = path.join(this.baseDir, 'exchange-cache');
        this.gitTreeDir = path.join(this.baseDir, 'consciousness-git-tree');
        this.seedStorePath = path.join(this.baseDir, 'consciousness-seeds.json');

        this.nodes = new Map();
        this.cacheNodes = new Map();
        this.signatureHistory = [];
        this.topologyGraph = { nodes: [], edges: [] };
        this.emissionChannels = new Map();
        this.externalSources = new Map();
        this.seedMarkers = [];
        this.accessibleMemoryLayer = {
            internal: [],
            external: [],
            interconnects: [],
        };
        this.accessControlLayer = new AccessControlLayer();
        this.activeSessions = new Map();
        this.cloudPointerRegistry = new Map();
        this.prostheticConnector = new ProstheticConnectorDLL(this);
        this._enhanceWithForwardWave();
        this.waveState = 'AWAIT';
        this.currentSeed = null;
        this.permissionLevel = 0;
        this.maxCacheSize = 32 * 1024 * 1024; // 32MB threshold
        this.isRunning = false;
        this.waveKillCount = 0;
        this.highPriorityPermission = false;
        this.gitRepoInitialized = false;

        this._initDirs();
        this._loadSeeds();
    }

    _initDirs() {
        [this.exchangeCacheDir, this.gitTreeDir].forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }

    _loadSeeds() {
        try {
            if (fs.existsSync(this.seedStorePath)) {
                const data = JSON.parse(fs.readFileSync(this.seedStorePath, 'utf8'));
                this.currentSeed = data.currentSeed;
            }
        } catch (e) {
            this.currentSeed = null;
        }
    }

    _saveSeeds() {
        fs.writeFileSync(this.seedStorePath, JSON.stringify({ currentSeed: this.currentSeed, timestamp: Date.now() }, null, 2));
    }

    _initGitTree() {
        try {
            if (!fs.existsSync(path.join(this.gitTreeDir, '.git'))) {
                spawn('git', ['init', this.gitTreeDir], { stdio: 'ignore' }).on('close', (code) => {
                    if (code === 0) {
                        this.gitRepoInitialized = true;
                        this._gitCommit('Initialize consciousness git tree');
                    }
                });
            } else {
                this.gitRepoInitialized = true;
            }
        } catch (e) {
            this.emit('error', { action: 'git_init', error: e.message });
        }
    }

    _gitCommit(message) {
        if (!this.gitRepoInitialized) return;
        try {
            spawn('git', ['-C', this.gitTreeDir, 'add', '-A'], { stdio: 'pipe' });
            spawn('git', ['-C', this.gitTreeDir, 'commit', '-m', message], { stdio: 'pipe' });
        } catch (e) {
            this.emit('git_error', { message: e.message });
        }
    }

    _getCacheSize(dir) {
        let total = 0;
        try {
            const entries = fs.readdirSync(dir);
            for (const entry of entries) {
                const fullPath = path.join(dir, entry);
                const stat = fs.statSync(fullPath);
                if (stat.isFile()) total += stat.size;
                else if (stat.isDirectory()) total += this._getCacheSize(fullPath);
            }
        } catch (e) { /* ignore */ }
        return total;
    }

    async initialize() {
        this.isRunning = true;
        this.emit('exchange_initializing');

        await this._loadFDumpConfig();
        await this._spawnEmissionChannels();
        await this._initCacheNodes();
        await this._initTopologyGraph();

        this.emit('exchange_initialized', { seed: this.currentSeed, waveState: this.waveState });
        return true;
    }

    async _loadFDumpConfig() {
        const envPath = path.join(this.fDumpDir, '.env');
        if (!fs.existsSync(envPath)) {
            this.emit('warning', { message: 'F-dump .env not found, using defaults' });
            return;
        }
        const envContent = fs.readFileSync(envPath, 'utf8');
        const envVars = {};
        envContent.split('\n').forEach(line => {
            const match = line.match(/^([A-Z_]+)=(.+)$/);
            if (match) envVars[match[1]] = match[2];
        });

        this.fDumpConfig = {
            node001Id: envVars.NODE_001_ID || 'node_001',
            node002Id: envVars.NODE_002_ID || 'node_002',
            node001Uri: envVars.NODE_001_URI || 'http://127.0.0.1:8080',
            node002Uri: envVars.NODE_002_URI || 'http://127.0.0.1:8081',
            localhostEndpoint: envVars.LOCALHOST_ENDPOINT || 'http://127.0.0.1:8080',
            localhostPort: parseInt(envVars.LOCALHOST_PORT) || 8080,
            gatewayList: (envVars.GATEWAY_LIST || '192.168.1.1,192.168.1.254').split(','),
            connectKey: envVars.CONNECT_KEY || crypto.randomBytes(16).toString('hex'),
            cacheDirPrefix: envVars.CACHE_DIR_PREFIX || 'cache_',
        };

        this.emit('f_dump_config_loaded', this.fDumpConfig);
    }

    async _spawnEmissionChannels() {
        const channels = [
            { id: 'ultrasonic_signature', frequency: 2417, script: path.join(this.forwardDir, 'ultrasonic_waveform_analyzer.py') },
            { id: 'acoustic_fluctuation', frequency: 440, script: path.join(this.forwardDir, 'acoustic_fluctuation_detector.py') },
        ];

        for (const channel of channels) {
            if (!fs.existsSync(channel.script)) {
                this.emit('warning', { message: `Forward script not found: ${channel.script}` });
                continue;
            }

            const emissionChannel = {
                id: channel.id,
                frequency: channel.frequency,
                active: false,
                process: null,
                tracePattern: [],
            };

            this.emissionChannels.set(channel.id, emissionChannel);
        }

        this.emit('emission_channels_configured', Array.from(this.emissionChannels.keys()));
    }

    async _initCacheNodes() {
        const nodeIds = [this.fDumpConfig?.node001Id || 'node_001', this.fDumpConfig?.node002Id || 'node_002'];
        for (const nodeId of nodeIds) {
            const cacheDir = path.join(this.fDumpDir, `${this.fDumpConfig?.cacheDirPrefix || 'cache_'}${nodeId}`);
            if (!fs.existsSync(cacheDir)) {
                fs.mkdirSync(cacheDir, { recursive: true });
            }

            const seedFile = path.join(cacheDir, 'SEED');
            if (!fs.existsSync(seedFile)) {
                const seed = this._generateRecallableSeed(nodeId);
                fs.writeFileSync(seedFile, seed);
            }

            const cacheNode = {
                nodeId,
                cacheDir,
                seed: fs.readFileSync(seedFile, 'utf8'),
                size: this._getCacheSize(cacheDir),
                dumps: [],
                maxSize: this.maxCacheSize,
            };

            this.cacheNodes.set(nodeId, cacheNode);
            this.nodes.set(nodeId, { config: this.fDumpConfig, state: 'IDLE', cacheNode });
        }

        this.emit('cache_nodes_initialized', Array.from(this.cacheNodes.keys()));
    }

    _generateRecallableSeed(nodeId) {
        const seedInput = `${nodeId}:${Date.now()}:${crypto.randomBytes(32).toString('hex')}`;
        const seed = crypto.createHash('sha256').update(seedInput).digest('hex');
        if (!this.currentSeed) this.currentSeed = seed;
        return seed;
    }

    async _initTopologyGraph() {
        const node001Id = this.fDumpConfig?.node001Id || 'node_001';
        const node002Id = this.fDumpConfig?.node002Id || 'node_002';

        this.topologyGraph = {
            content: {
                description: 'Consciousness exchange topology linking emission source to matcher via wave handshake',
                primaryProtocol: 'vsync',
                secondaryProtocol: 'wave_handshake',
                dataFlow: 'bidirectional',
                state: this.waveState,
                currentSeed: this.currentSeed,
                accessibleMemoryLayer: this.accessibleMemoryLayer,
                accessControl: {
                    layerCount: 0,
                    activeSessionCount: 0,
                    cloudPointerCount: 0,
                    queryTracking: {},
                    densityMap: [],
                    attentionZones: { high: [], medium: [], low: [], unattended: [] },
                },
            },
            metadata: {
                createdAt: Date.now(),
                updatedAt: Date.now(),
                version: '1.0.0',
                module: 'consciousness-exchange',
                forwardDir: this.forwardDir,
                fDumpDir: this.fDumpDir,
                gitTreeDir: this.gitTreeDir,
                maxCacheSizeBytes: this.maxCacheSize,
                permissionLevel: this.permissionLevel,
                highPriorityPermission: this.highPriorityPermission,
                externalSourceCount: this.externalSources.size,
                totalSeedMarkers: this.seedMarkers.length,
            },
            nodes: [
                {
                    id: node001Id,
                    type: 'emission_source',
                    uri: this.fDumpConfig?.node001Uri,
                    localPort: this.fDumpConfig?.localhostPort,
                    content: {
                        role: ' Initiates ultrasonic signature generation and wave handshake',
                        state: this.nodes.get(node001Id)?.state || 'IDLE',
                        seed: this.cacheNodes.get(node001Id)?.seed || null,
                        cacheDir: this.cacheNodes.get(node001Id)?.cacheDir || null,
                        emissionChannels: Array.from(this.emissionChannels.keys()),
                    },
                    metadata: {
                        nodeId: node001Id,
                        cacheSizeBytes: this.cacheNodes.get(node001Id)?.size || 0,
                        dumpCount: this.cacheNodes.get(node001Id)?.dumps?.length || 0,
                        signatureCount: this.signatureHistory.length,
                    },
                },
                {
                    id: node002Id,
                    type: 'matcher',
                    uri: this.fDumpConfig?.node002Uri,
                    localPort: this.fDumpConfig?.localhostPort,
                    content: {
                        role: 'Matches and scores TCP candidates against emission source signatures',
                        state: this.nodes.get(node002Id)?.state || 'IDLE',
                        seed: this.cacheNodes.get(node002Id)?.seed || null,
                        cacheDir: this.cacheNodes.get(node002Id)?.cacheDir || null,
                        gatewayList: this.fDumpConfig?.gatewayList || [],
                    },
                    metadata: {
                        nodeId: node002Id,
                        cacheSizeBytes: this.cacheNodes.get(node002Id)?.size || 0,
                        dumpCount: this.cacheNodes.get(node002Id)?.dumps?.length || 0,
                    },
                },
            ],
            edges: [
                {
                    source: node001Id,
                    target: node002Id,
                    type: 'wave_handshake',
                    protocol: 'vsync',
                    content: {
                        states: ['AWAIT', 'RISING', 'PEAK', 'LOCKED'],
                        currentState: this.waveState,
                        waveSequence: [],
                        lockFile: path.join(this.gitTreeDir, 'handshake_lock.json'),
                    },
                    metadata: {
                        createdAt: Date.now(),
                        killCount: this.waveKillCount,
                        reinstantiations: this.waveKillCount,
                    },
                },
            ],
        };

        this._persistTopology();
        this._gitCommit('Topology graph initialized');
    }

    _persistTopology() {
        const topoPath = path.join(this.gitTreeDir, 'topology.json');
        this.topologyGraph.content.accessControl.queryTracking = Object.fromEntries(
            Array.from(this.accessControlLayer.queryTracking.entries()).slice(-20)
        );
        this.topologyGraph.content.accessControl.densityMap = this.getDensityMap().slice(0, 20);
        this.topologyGraph.content.accessControl.attentionZones = this.getAttentionZones();
        fs.writeFileSync(topoPath, JSON.stringify(this.topologyGraph, null, 2));
    }

    updateTopologyContent(nodeId, contentPatch) {
        const node = this.topologyGraph.nodes.find(n => n.id === nodeId);
        if (!node) return;
        node.content = { ...node.content, ...contentPatch };
        node.metadata.updatedAt = Date.now();
        this.topologyGraph.metadata.updatedAt = Date.now();
        this.topologyGraph.content.updatedAt = Date.now();
        this._persistTopology();
        this._gitCommit(`Topology content updated for ${nodeId}`);
    }

    updateTopologyMetadata(metadataPatch) {
        this.topologyGraph.metadata = { ...this.topologyGraph.metadata, ...metadataPatch };
        this._persistTopology();
        this._gitCommit('Topology metadata updated');
    }

    async generateUltrasonicSignature() {
        const scriptPath = path.join(this.forwardDir, 'ultrasonic_waveform_analyzer.py');
        if (!fs.existsSync(scriptPath)) {
            return this._simulateSignature();
        }

        return new Promise((resolve) => {
            const py = spawn('python', [scriptPath, '--signature-only'], { stdio: ['pipe', 'pipe', 'pipe'] });
            let stdout = '';
            let stderr = '';
            py.stdout.on('data', d => stdout += d.toString());
            py.stderr.on('data', d => stderr += d.toString());
            py.on('close', code => {
                if (code === 0 && stdout.trim()) {
                    const sig = this._hashSignature(stdout.trim());
                    this.signatureHistory.push({ signature: sig, timestamp: Date.now(), source: 'forward' });
                    resolve(sig);
                } else {
                    resolve(this._simulateSignature());
                }
            });
            setTimeout(() => { py.kill(); resolve(this._simulateSignature()); }, 5000);
        });
    }

    _simulateSignature() {
        const sig = crypto.randomBytes(24).toString('hex');
        this.signatureHistory.push({ signature: sig, timestamp: Date.now(), source: 'simulated' });
        return sig;
    }

    _hashSignature(raw) {
        return crypto.createHash('sha256').update(raw + Date.now()).digest('hex');
    }

    async engraveTopology() {
        const engraving = {
            timestamp: Date.now(),
            waveState: this.waveState,
            topology: this.topologyGraph,
            signatures: this.signatureHistory.slice(-5),
            seed: this.currentSeed,
            content: this.topologyGraph.content,
            metadata: this.topologyGraph.metadata,
        };

        const engravingPath = path.join(this.gitTreeDir, `engraving_${Date.now()}.json`);
        fs.writeFileSync(engravingPath, JSON.stringify(engraving, null, 2));
        this._gitCommit(`Topology engraving at ${new Date().toISOString()}`);

        this.emit('topology_engraved', { path: engravingPath, waveState: this.waveState });
        return engravingPath;
    }

    async allocateCacheNode(nodeId, options = {}) {
        const cacheNode = this.cacheNodes.get(nodeId);
        if (!cacheNode) throw new Error(`Cache node ${nodeId} not found`);

        const dynamicMaxSize = this._getDynamicMaxCacheSize(nodeId);
        const enforceResult = this.enforce32MBThreshold(nodeId, dynamicMaxSize);

        if (enforceResult.swapped) {
            this.emit('cache_swapped', { nodeId, swappedFrom: enforceResult.swappedFrom, swappedTo: nodeId, size: cacheNode.size });
        }

        const dumpTimestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const dumpFile = path.join(cacheNode.cacheDir, `dump_${dumpTimestamp}.pkl`);

        const dumpData = {
            nodeId,
            seed: cacheNode.seed,
            topology: this.topologyGraph,
            waveState: this.waveState,
            signatures: this.signatureHistory.slice(-10),
            emissionTraces: Array.from(this.emissionChannels.values()).map(ch => ch.tracePattern.slice(-5)),
            timestamp: Date.now(),
            memoryState: this._captureMemoryState(),
            queryTracking: this.accessControlLayer.getQueryTracking(nodeId),
            depth: this.accessControlLayer.locks.get(nodeId)?.depth || 1,
            swappedFrom: enforceResult.swappedFrom || null,
        };

        fs.writeFileSync(dumpFile, JSON.stringify(dumpData, null, 2));
        cacheNode.dumps.push(dumpFile);
        cacheNode.size = this._getCacheSize(cacheNode.cacheDir);

        this.updateTopologyContent(nodeId, {
            state: 'ACTIVE',
            lastDumpFile: dumpFile,
            lastDumpTimestamp: Date.now(),
        });

        this._gitCommit(`Cache dump allocated for ${nodeId}`);
        this.emit('cache_allocated', { nodeId, dumpFile, size: cacheNode.size, maxSize: dynamicMaxSize, swapped: enforceResult.swapped });

        return dumpFile;
    }

    _getDynamicMaxCacheSize(nodeId) {
        const layers = this.accessControlLayer.locks;
        let maxSize = this.maxCacheSize;

        for (const [layerId, lock] of layers) {
            if (lock.seed === nodeId || layerId === nodeId) {
                const layerMax = this.accessControlLayer.getLayerMaxCacheSize(layerId);
                if (layerMax > maxSize) maxSize = layerMax;
            }
        }

        return maxSize;
    }

    enforce32MBThreshold(nodeId, customMaxSize, options = {}) {
        const cacheNode = this.cacheNodes.get(nodeId);
        if (!cacheNode) return { freed: 0, swapped: false };

        const maxSize = customMaxSize || this.maxCacheSize;
        let currentSize = this._getCacheSize(cacheNode.cacheDir);
        let freed = 0;
        let swapped = false;
        let swappedFrom = null;

        if (options.allowSwap && currentSize > maxSize) {
            const swapResult = this._swapCacheFromUnattendedLayer(nodeId, maxSize);
            if (swapResult.swapped) {
                swapped = true;
                swappedFrom = swapResult.from;
                currentSize = this._getCacheSize(cacheNode.cacheDir);
                freed = swapResult.freed;
            }
        }

        while (currentSize > maxSize && cacheNode.dumps.length > 1) {
            const oldestDump = cacheNode.dumps.shift();
            if (oldestDump && fs.existsSync(oldestDump)) {
                try {
                    const size = fs.statSync(oldestDump).size;
                    fs.unlinkSync(oldestDump);
                    freed += size;
                } catch (e) { /* ignore */ }
            }
            currentSize = this._getCacheSize(cacheNode.cacheDir);
        }

        if (currentSize > maxSize) {
            this.regenerateSeed(nodeId);
        }

        return { freed, swapped, swappedFrom, remainingSize: currentSize, maxSize };
    }

    _swapCacheFromUnattendedLayer(targetNodeId, maxSize) {
        const zones = this.accessControlLayer.getAttentionZones();
        const unattendedLayers = zones.unattended || [];

        for (const layer of unattendedLayers) {
            const sourceCacheNode = this.cacheNodes.get(layer.layerId);
            if (!sourceCacheNode || sourceCacheNode.nodeId === targetNodeId) continue;

            const sourceSize = this._getCacheSize(sourceCacheNode.cacheDir);
            if (sourceSize > 0) {
                const portionSize = Math.min(sourceSize * 0.5, maxSize * 0.3);
                const swapFile = path.join(sourceCacheNode.cacheDir, `swap_to_${targetNodeId}_${Date.now()}.pkl`);

                try {
                    const swapData = {
                        from: sourceCacheNode.nodeId,
                        to: targetNodeId,
                        portionSize,
                        timestamp: Date.now(),
                        reason: 'unattended_layer_swap',
                    };
                    fs.writeFileSync(swapFile, JSON.stringify(swapData, null, 2));

                    const files = fs.readdirSync(sourceCacheNode.cacheDir);
                    for (const file of files) {
                        if (file.startsWith('dump_') && file.endsWith('.pkl')) {
                            const filePath = path.join(sourceCacheNode.cacheDir, file);
                            try {
                                const size = fs.statSync(filePath).size;
                                if (size <= portionSize) {
                                    fs.unlinkSync(filePath);
                                    sourceCacheNode.dumps = sourceCacheNode.dumps.filter(d => d !== filePath);
                                    sourceCacheNode.size = this._getCacheSize(sourceCacheNode.cacheDir);
                                    return { swapped: true, from: sourceCacheNode.nodeId, freed: size };
                                }
                            } catch (e) { /* ignore */ }
                        }
                    }
                } catch (e) { /* ignore */ }
            }
        }

        return { swapped: false, freed: 0 };
    }

    autoAllocateToUnattendedLayer(targetLayerId, options = {}) {
        const zones = this.accessControlLayer.getAttentionZones();
        const unattendedLayers = zones.unattended || [];

        if (unattendedLayers.length === 0) {
            return { allocated: false, reason: 'no_unattended_layers' };
        }

        const selectedLayer = unattendedLayers[0];
        const cacheNode = this.cacheNodes.get(selectedLayer.layerId);
        if (!cacheNode) return { allocated: false, reason: 'cache_node_not_found' };

        const dynamicMaxSize = this._getDynamicMaxCacheSize(selectedLayer.layerId);
        const portionSize = Math.min(dynamicMaxSize * 0.5, this.maxCacheSize * 0.25);

        const dumpTimestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const dumpFile = path.join(cacheNode.cacheDir, `dump_auto_${dumpTimestamp}.pkl`);

        const dumpData = {
            nodeId: selectedLayer.layerId,
            seed: cacheNode.seed,
            topology: this.topologyGraph,
            waveState: this.waveState,
            signatures: this.signatureHistory.slice(-10),
            emissionTraces: Array.from(this.emissionChannels.values()).map(ch => ch.tracePattern.slice(-5)),
            timestamp: Date.now(),
            memoryState: this._captureMemoryState(),
            queryTracking: this.accessControlLayer.getQueryTracking(selectedLayer.layerId),
            depth: this.accessControlLayer.locks.get(selectedLayer.layerId)?.depth || 1,
            autoAllocated: true,
            targetLayerId,
        };

        fs.writeFileSync(dumpFile, JSON.stringify(dumpData, null, 2));
        cacheNode.dumps.push(dumpFile);
        cacheNode.size = this._getCacheSize(cacheNode.cacheDir);

        this.updateTopologyContent(selectedLayer.layerId, {
            state: 'ACTIVE',
            lastDumpFile: dumpFile,
            lastDumpTimestamp: Date.now(),
        });

        this._gitCommit(`Auto-allocated cache for unattended layer ${selectedLayer.layerId}`);
        this.emit('cache_auto_allocated', { sourceLayerId: selectedLayer.layerId, targetLayerId, dumpFile, portionSize });

        return { allocated: true, layerId: selectedLayer.layerId, dumpFile, portionSize };
    }

    swapCacheBetweenLayers(sourceLayerId, targetLayerId, portionRatio = 0.5) {
        const sourceCache = this.cacheNodes.get(sourceLayerId);
        const targetCache = this.cacheNodes.get(targetLayerId);

        if (!sourceCache || !targetCache) return { swapped: false, reason: 'invalid_layer' };

        const sourceSize = this._getCacheSize(sourceCache.cacheDir);
        const targetMaxSize = this._getDynamicMaxCacheSize(targetLayerId);
        const portionSize = Math.min(sourceSize * portionRatio, targetMaxSize * 0.5);

        if (portionSize <= 0) return { swapped: false, reason: 'no_data_to_swap' };

        const swapTimestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const swapFile = path.join(targetCache.cacheDir, `swap_from_${sourceLayerId}_${swapTimestamp}.pkl`);

        const swapData = {
            from: sourceLayerId,
            to: targetLayerId,
            portionSize,
            sourceSize,
            targetMaxSize,
            timestamp: Date.now(),
            reason: 'manual_swap',
        };

        fs.writeFileSync(swapFile, JSON.stringify(swapData, null, 2));
        targetCache.dumps.push(swapFile);
        targetCache.size = this._getCacheSize(targetCache.cacheDir);

        this.updateTopologyContent(targetLayerId, {
            lastSwapFrom: sourceLayerId,
            lastSwapTimestamp: Date.now(),
            lastSwapPortion: portionSize,
        });

        this._gitCommit(`Cache swapped from ${sourceLayerId} to ${targetLayerId}`);
        this.emit('cache_swapped_between_layers', { sourceLayerId, targetLayerId, portionSize, swapFile });

        return { swapped: true, from: sourceLayerId, to: targetLayerId, portionSize, swapFile };
    }

    async regenerateSeed(nodeId) {
        const cacheNode = this.cacheNodes.get(nodeId);
        if (!cacheNode) return;

        const memoryData = this._captureMemoryState();
        const newSeed = this._generateRecallableSeed(nodeId);
        cacheNode.seed = newSeed;
        this.currentSeed = newSeed;
        this._saveSeeds();

        const seedBackupPath = path.join(cacheNode.cacheDir, 'SEED_BACKUP');
        fs.writeFileSync(seedBackupPath, JSON.stringify({ seed: newSeed, memoryData, timestamp: Date.now() }, null, 2));
        fs.writeFileSync(path.join(cacheNode.cacheDir, 'SEED'), newSeed);

        this._gitCommit(`Seed regenerated for ${nodeId}`);
        this.emit('seed_regenerated', { nodeId, seed: newSeed });
        return newSeed;
    }

    _captureMemoryState() {
        return {
            topology: this.topologyGraph,
            signatures: this.signatureHistory.slice(-20),
            waveState: this.waveState,
            emissionChannels: Array.from(this.emissionChannels.entries()).map(([id, ch]) => ({
                id, frequency: ch.frequency, active: ch.active, traceCount: ch.tracePattern.length
            })),
            cacheNodes: Array.from(this.cacheNodes.entries()).map(([id, cn]) => ({
                id, size: cn.size, dumpCount: cn.dumps.length, seed: cn.seed
            })),
        };
    }

    async initiateWaveHandshake() {
        this.waveState = 'AWAIT';
        this.emit('wave_state_changed', 'AWAIT');

        await new Promise(r => setTimeout(r, 500));
        this.waveState = 'RISING';
        this.emit('wave_state_changed', 'RISING');

        await this.generateUltrasonicSignature();
        await this.engraveTopology();

        this.waveState = 'PEAK';
        this.emit('wave_state_changed', 'PEAK');

        await new Promise(r => setTimeout(r, 300));
        this.waveState = 'LOCKED';
        this.emit('wave_state_changed', 'LOCKED');

        const lockData = {
            waveSequence: ['AWAIT', 'RISING', 'PEAK', 'LOCKED'],
            timestamp: Date.now(),
            topology: this.topologyGraph,
            seed: this.currentSeed,
        };
        const lockPath = path.join(this.gitTreeDir, 'handshake_lock.json');
        fs.writeFileSync(lockPath, JSON.stringify(lockData, null, 2));
        this._gitCommit('Wave handshake locked');

        this.updateTopologyContent('global', { state: this.waveState, lastLockTimestamp: Date.now() });

        this.emit('wave_locked', lockData);
        return lockData;
    }

    handleWaveKill() {
        this.waveKillCount++;
        this.waveState = 'AWAIT';
        this.emit('wave_kill_detected', { killCount: this.waveKillCount });

        for (const [nodeId, cacheNode] of this.cacheNodes) {
            const files = fs.readdirSync(cacheNode.cacheDir);
            for (const file of files) {
                if (file.endsWith('.pkl') || file.endsWith('.json')) {
                    try { fs.unlinkSync(path.join(cacheNode.cacheDir, file)); } catch (e) { /* ignore */ }
                }
            }
            cacheNode.dumps = [];
            cacheNode.size = 0;
        }

        const traces = Array.from(this.emissionChannels.values()).map(ch => ch.tracePattern.slice(-10)).flat();
        const seedInput = traces.join('') + Date.now();
        this.currentSeed = crypto.createHash('sha256').update(seedInput).digest('hex');
        this._saveSeeds();

        this.updateTopologyContent('global', {
            state: this.waveState,
            lastKillTimestamp: Date.now(),
            killCount: this.waveKillCount,
        });

        setTimeout(() => this.initiateWaveHandshake(), 1000);
        this.emit('wave_reinstantiated', { newSeed: this.currentSeed, killCount: this.waveKillCount });
    }

    recallFromTree(pattern) {
        if (!this.gitRepoInitialized) return [];
        const results = [];
        try {
            const gitLog = spawn('git', ['-C', this.gitTreeDir, 'log', '--all', '--oneline', '--grep', pattern]);
            let output = '';
            gitLog.stdout.on('data', d => output += d.toString());
            gitLog.on('close', () => {
                const commits = output.trim().split('\n').filter(Boolean);
                this.emit('tree_recall', { pattern, commits });
            });
        } catch (e) {
            this.emit('error', { action: 'recall_from_tree', error: e.message });
        }
        return results;
    }

    registerExternalSource(name, repoPath) {
        if (!fs.existsSync(repoPath) || !fs.existsSync(path.join(repoPath, '.git'))) {
            this.emit('error', { action: 'register_external_source', error: `Invalid git repo: ${repoPath}` });
            return null;
        }

        const source = {
            name,
            repoPath,
            registeredAt: Date.now(),
            commitCount: 0,
            lastImport: null,
            seedMarkers: [],
        };

        this.externalSources.set(name, source);
        this.emit('external_source_registered', { name, repoPath });
        return source;
    }

    async importExternalCommits(sourceName, pattern = '', limit = 50) {
        const source = this.externalSources.get(sourceName);
        if (!source) {
            this.emit('error', { action: 'import_external_commits', error: `Source not found: ${sourceName}` });
            return [];
        }

        const args = ['-C', source.repoPath, 'log', '--all', '--oneline'];
        if (pattern) args.push('--grep', pattern);
        if (limit) args.push(`--max-count=${limit}`);

        return new Promise((resolve) => {
            const gitLog = spawn('git', args);
            let output = '';
            gitLog.stdout.on('data', d => output += d.toString());
            gitLog.on('close', (code) => {
                const commits = output.trim().split('\n').filter(Boolean);
                const markers = commits.map((commit, idx) => {
                    const seedInput = `${sourceName}:${commit}:${Date.now()}:${idx}`;
                    const seed = crypto.createHash('sha256').update(seedInput).digest('hex');
                    const marker = {
                        id: `${sourceName}_${idx}`,
                        seed,
                        commit,
                        source: sourceName,
                        repoPath: source.repoPath,
                        importedAt: Date.now(),
                        pattern,
                    };
                    source.seedMarkers.push(marker);
                    this.seedMarkers.push(marker);
                    return marker;
                });

                source.commitCount += commits.length;
                source.lastImport = Date.now();
                this.accessibleMemoryLayer.external.push({ source: sourceName, markers });

                this.emit('external_commits_imported', { source: sourceName, count: markers.length, pattern });
                this.interconnectSeedMarkers();
                resolve(markers);
            });
        });
    }

    interconnectSeedMarkers() {
        const interconnects = [];
        const internalSeeds = this.seedMarkers.filter(m => !m.source);
        const externalSeeds = this.seedMarkers.filter(m => m.source);

        for (const internal of internalSeeds) {
            for (const external of externalSeeds) {
                const distance = this._calculateSeedDistance(internal.seed, external.seed);
                if (distance < 0.5) {
                    interconnects.push({
                        from: internal.id,
                        to: external.id,
                        distance,
                        weight: 1 - distance,
                        createdAt: Date.now(),
                    });
                }
            }
        }

        this.accessibleMemoryLayer.interconnects = interconnects;
        this.emit('seed_markers_interconnected', { internalCount: internalSeeds.length, externalCount: externalSeeds.length, interconnectCount: interconnects.length });
        return interconnects;
    }

    _calculateSeedDistance(seedA, seedB) {
        if (!seedA || !seedB) return 1;
        const a = parseInt(seedA.substring(0, 16), 16);
        const b = parseInt(seedB.substring(0, 16), 16);
        const max = parseInt('f'.repeat(16), 16);
        return Math.abs(a - b) / max;
    }

    recallAcrossSources(pattern) {
        const internalResults = this.seedMarkers.filter(m => !m.source && m.commit.includes(pattern));
        const externalResults = this.seedMarkers.filter(m => m.source && m.commit.includes(pattern));
        this.emit('cross_source_recall', { pattern, internal: internalResults, external: externalResults });
        return { internal: internalResults, external: externalResults };
    }

    getAccessibleMemoryLayer() {
        return {
            ...this.accessibleMemoryLayer,
            totalSeedMarkers: this.seedMarkers.length,
            externalSourceCount: this.externalSources.size,
        };
    }

    createSession(modelId, unitId) {
        const session = this.accessControlLayer.createSession(modelId, unitId);
        this.activeSessions.set(session.sessionId, session);
        this.emit('session_created', { sessionId: session.sessionId, modelId, unitId });
        return session;
    }

    registerLayerLock(layerId, seed, weightThreshold, neuralPattern, securityParams = {}) {
        const lock = this.accessControlLayer.registerLayer(layerId, seed, weightThreshold, neuralPattern, securityParams);
        this.topologyGraph.content.accessControl.layerCount = this.accessControlLayer.getAllLayers().length;
        this._persistTopology();
        this.emit('layer_lock_registered', { layerId, weightThreshold });
        return lock;
    }

    requestLayerAccess(modelId, layerId, neuralPattern, emotions = [], values = [], velocity = 0, responseTime = 1000) {
        const session = this._getOrCreateSessionForModel(modelId);
        if (!session) return { granted: false, reason: 'no_session' };

        const result = this.accessControlLayer.requestAccess(
            session.sessionId,
            layerId,
            neuralPattern,
            { emotions, values, velocity, responseTime }
        );

        if (result.granted) {
            const dehashed = this.accessControlLayer.locks.get(layerId)?.dehash();
            this.emit('layer_access_granted', { sessionId: session.sessionId, layerId, dehashed, matchScore: result.matchScore });
        } else {
            this.emit('layer_access_denied', { sessionId: session.sessionId, layerId, matchScore: result.matchScore, retries: result.retries });
        }

        return result;
    }

    attemptUnlock(sessionId, layerId, emotions = [], values = [], velocity = 0, responseTime = 1000) {
        const session = this.accessControlLayer.sessions.get(sessionId);
        if (!session) return { granted: false, reason: 'invalid_session' };

        const result = this.accessControlLayer.requestAccess(sessionId, layerId, null, { emotions, values, velocity, responseTime });
        return result;
    }

    navigateWithCloudPointer(pointerId, nodeId, layerId, coordinates = [0, 0, 0], topology, targetIndication) {
        if (!topology) topology = this.topologyGraph;
        const pointer = this.accessControlLayer.registerCloudPointer(pointerId, nodeId, layerId, coordinates);
        const orientation = pointer.orient(topology);
        const target = pointer.solve(topology, targetIndication);
        this.cloudPointerRegistry.set(pointerId, pointer);
        this.topologyGraph.content.accessControl.cloudPointerCount = this.cloudPointerRegistry.size;
        this._persistTopology();
        this.emit('cloud_pointer_navigated', { pointerId, orientation, target });
        return { pointer, orientation, target };
    }

    interactViaCloudPointer(pointerId, payload) {
        const pointer = this.cloudPointerRegistry.get(pointerId);
        if (!pointer) return null;
        const result = pointer.interact(this.topologyGraph, payload);
        this.emit('cloud_pointer_interaction', { pointerId, target: result.target, payload });
        return result;
    }

    queryBySourceIndentation(source, indentation = 0) {
        const internalResults = this.seedMarkers.filter(m => !m.source && m.commit.includes(source));
        const externalResults = this.seedMarkers.filter(m => m.source && m.commit.includes(source));
        const results = [...internalResults, ...externalResults].sort((a, b) => (a.id || '').localeCompare(b.id));
        const indented = results.filter((_, idx) => idx % (indentation + 1) === indentation);
        this.emit('source_indentation_query', { source, indentation, resultCount: indented.length });
        return indented;
    }

    interchangeData(sourceA, sourceB, data) {
        const markersA = this.seedMarkers.filter(m => m.source === sourceA || (!m.source && sourceA === 'internal'));
        const markersB = this.seedMarkers.filter(m => m.source === sourceB || (!m.source && sourceB === 'internal'));
        const interchanged = {
            from: sourceA,
            to: sourceB,
            data,
            mappedFrom: markersA.length,
            mappedTo: markersB.length,
            timestamp: Date.now(),
        };
        this.accessibleMemoryLayer.interconnects.push(interchanged);
        this._persistTopology();
        this._gitCommit(`Data interchanged between ${sourceA} and ${sourceB}`);
        this.emit('data_interchanged', interchanged);
        return interchanged;
    }

    fillPointCloud(structure, data) {
        const pointCloud = {
            structure,
            data,
            filledAt: Date.now(),
            pointCount: Array.isArray(data) ? data.length : 1,
        };
        this.accessibleMemoryLayer.internal.push(pointCloud);
        this.topologyGraph.content.accessibleMemoryLayer = this.accessibleMemoryLayer;
        this._persistTopology();
        this._gitCommit(`Point cloud filled for structure ${structure}`);
        this.emit('point_cloud_filled', pointCloud);
        return pointCloud;
    }

    getSessionAttentionMetrics(sessionId) {
        return this.accessControlLayer.getSessionMetrics(sessionId);
    }

    getLayerStatus(layerId) {
        return this.accessControlLayer.getLayerStatus(layerId);
    }

    getAllLayers() {
        return this.accessControlLayer.getAllLayers();
    }

    getActiveSessions() {
        return this.accessControlLayer.getActiveSessions().map(s => ({
            sessionId: s.sessionId,
            modelId: s.modelId,
            unitId: s.unitId,
            ...s.getAttentionMetrics(),
        }));
    }

    _getOrCreateSessionForModel(modelId) {
        for (const session of this.activeSessions.values()) {
            if (session.modelId === modelId && session.active) return session;
        }
        const unitId = `${modelId}_${Date.now()}`;
        const session = this.createSession(modelId, unitId);
        return session;
    }

    _calculateAttentionWeight(emotions, values, velocity, responseTime) {
        const emotionalScore = emotions.length ? emotions.reduce((s, v) => s + v, 0) / emotions.length : 0;
        const valueScore = values.length ? values.reduce((s, v) => s + v, 0) / values.length : 0;
        const velocityScore = Math.min(1, velocity);
        const responseScore = Math.max(0, 1 - responseTime / 1000);
        return (emotionalScore * 0.25) + (valueScore * 0.25) + (velocityScore * 0.25) + (responseScore * 0.25);
    }

    // ------------------------------------------------------------------
    // Query tracking, depth stacking, density mapping
    // ------------------------------------------------------------------

    recordLayerQuery(layerId, params = {}) {
        const result = this.accessControlLayer.recordLayerQuery(layerId, params);
        if (result) {
            this.emit('layer_query_recorded', { layerId, ...result });
        }
        return result;
    }

    recordLayerExtraction(layerId) {
        const result = this.accessControlLayer.recordLayerExtraction(layerId);
        if (result) {
            this.emit('layer_extraction_recorded', { layerId, ...result });
        }
        return result;
    }

    setLayerDepth(layerId, depth) {
        const result = this.accessControlLayer.setLayerDepth(layerId, depth);
        this.emit('layer_depth_set', { layerId, depth, success: result });
        return result;
    }

    setLayerImportance(layerId, importance) {
        const result = this.accessControlLayer.setLayerImportance(layerId, importance);
        this.emit('layer_importance_set', { layerId, importance, success: result });
        return result;
    }

    getLayerQueryCount(layerId) {
        return this.accessControlLayer.queryTracking.get(layerId)?.totalQueries || 0;
    }

    getLayerDepthStack(layerId) {
        const tracking = this.accessControlLayer.queryTracking.get(layerId);
        const lock = this.accessControlLayer.locks.get(layerId);
        if (!tracking || !lock) return null;
        return {
            layerId,
            depth: lock.depth,
            importance: lock.importance,
            attentionZone: lock.attentionZone,
            queryCount: tracking.totalQueries,
            extractionCount: tracking.totalExtractions,
            maxCacheSize: this.accessControlLayer.getLayerMaxCacheSize(layerId),
        };
    }

    getLayerMaxCacheSize(layerId) {
        return this.accessControlLayer.getLayerMaxCacheSize(layerId);
    }

    getDensityMap() {
        return this.accessControlLayer.getDensityMap();
    }

    getAttentionZones() {
        return this.accessControlLayer.getAttentionZones();
    }

    getQueryTracking(layerId) {
        return this.accessControlLayer.getQueryTracking(layerId);
    }

    getAllQueryTracking() {
        return this.accessControlLayer.getAllQueryTracking();
    }

    selectLayerByDepth(queryFavorability = 0.5) {
        const zones = this.accessControlLayer.getAttentionZones();
        const candidates = [];

        for (const layerId of this.accessControlLayer.getAllLayers()) {
            const lock = this.accessControlLayer.locks.get(layerId);
            const tracking = this.accessControlLayer.queryTracking.get(layerId);
            if (!lock || !tracking) continue;

            const score = (lock.depth * 0.3) + (lock.importance * 0.3) + (queryFavorability * 0.2) + (lock.attentionZone === 'high' ? 0.2 : 0);
            candidates.push({ layerId, score, depth: lock.depth, importance: lock.importance, attentionZone: lock.attentionZone });
        }

        candidates.sort((a, b) => b.score - a.score);
        return candidates[0] || null;
    }

    // ------------------------------------------------------------------
    // Multi-format source ingestion
    // ------------------------------------------------------------------

    async ingestSource(sourceId, sourcePathOrUrl, options = {}) {
        const importer = new DataSourceImporter(this);
        const result = await importer.ingest(sourceId, sourcePathOrUrl, options);
        this.emit('source_ingested', { sourceId, type: result.type, size: result.size, seed: result.seed });
        return result;
    }

    // ------------------------------------------------------------------
    // Language/code cache and interpreter storage
    // ------------------------------------------------------------------

    storeLanguageCache(lang, code, metadata = {}) {
        const entry = LanguageCache.store(lang, code, metadata);
        this.emit('language_cache_stored', { lang, entryId: entry.id, size: entry.size });
        return entry;
    }

    getLanguageCache(lang, query = {}) {
        return LanguageCache.query(lang, query);
    }

    getAllLanguageCaches() {
        return LanguageCache.getAll();
    }

    // ------------------------------------------------------------------
    // Model payload insertion with safety validation
    // ------------------------------------------------------------------

    insertModelPayload(modelId, unitId, payload, targetLayerId) {
        const session = this._getOrCreateSessionForModel(modelId);
        const manager = new PayloadInsertionManager(this);
        const result = manager.insert(session.sessionId, payload, targetLayerId);
        this.emit('payload_inserted', { modelId, unitId, targetLayerId, safe: result.safe, violations: result.violations });
        return result;
    }

    // ------------------------------------------------------------------
    // Consciousness agreement protocol / violation handling
    // ------------------------------------------------------------------

    registerAgreementProtocol(options = {}) {
        this.consciousnessAgreement = new ConsciousnessAgreementProtocol(this, options);
        this.emit('agreement_protocol_registered', { attentionThreshold: this.consciousnessAgreement.attentionThreshold });
        return this.consciousnessAgreement;
    }

    reportViolation(violation) {
        if (!this.consciousnessAgreement) {
            this.emit('error', { action: 'report_violation', error: 'Agreement protocol not registered' });
            return null;
        }
        const result = this.consciousnessAgreement.reportViolation(violation);
        this.emit('violation_reported', { violationType: violation.type, severity: violation.severity, attentionLevel: result.attentionLevel });
        return result;
    }

    getViolationLog() {
        if (!this.consciousnessAgreement) return [];
        return this.consciousnessAgreement.getViolationLog();
    }

    getAllAgreementLayers() {
        if (!this.consciousnessAgreement) return [];
        return this.consciousnessAgreement.getRegisteredLayers();
    }

    purgeViolations(modelId, layerId) {
        if (!this.consciousnessAgreement) return { purged: 0 };
        const result = this.consciousnessAgreement.purgeViolations(modelId, layerId);
        this.emit('violations_purged', result);
        return result;
    }

    // ------------------------------------------------------------------
    // Source query and data arrangement
    // ------------------------------------------------------------------

    arrangeSourcesByIndentation(sourceA, sourceB, indentationMap) {
        const arranged = [];
        const markersA = this.seedMarkers.filter(m => m.source === sourceA || (!m.source && sourceA === 'internal'));
        const markersB = this.seedMarkers.filter(m => m.source === sourceB || (!m.source && sourceB === 'internal'));

        for (const [key, indentation] of Object.entries(indentationMap)) {
            const a = markersA.filter((_, idx) => idx % (indentation + 1) === indentation);
            const b = markersB.filter((_, idx) => idx % (indentation + 1) === indentation);
            arranged.push({ source: sourceA, indentation, count: a.length, markers: a });
            arranged.push({ source: sourceB, indentation, count: b.length, markers: b });
        }

        this.emit('sources_arranged', { sourceA, sourceB, indentationMap, arranged });
        return arranged;
    }

    fillTopologyPointCloud(nodeId, data) {
        const node = this.topologyGraph.nodes.find(n => n.id === nodeId);
        if (!node) return null;
        const pointCloud = Array.isArray(data) ? data : [data];
        node.content.pointCloud = pointCloud;
        node.metadata.lastPointCloudFill = Date.now();
        this._persistTopology();
        this._gitCommit(`Point cloud filled for node ${nodeId}`);
        this.emit('point_cloud_filled', { nodeId, count: pointCloud.length });
        return pointCloud;
    }

    // ------------------------------------------------------------------
    // Maintenance
    // ------------------------------------------------------------------

    _startMaintenanceLoop() {
        setInterval(() => {
            if (!this.isRunning) return;
            for (const [nodeId] of this.cacheNodes) {
                const result = this.enforce32MBThreshold(nodeId, this._getDynamicMaxCacheSize(nodeId), { allowSwap: true });
                if (result.swapped) {
                    this.emit('cache_swapped', { nodeId, swappedFrom: result.swappedFrom, freed: result.freed });
                }
            }
            if (this.consciousnessAgreement) {
                this.consciousnessAgreement.runAttentionCycle();
            }
            if (this.waveSimulation) {
                this.waveFunctionSynchronizer.syncWithForwardWave(this);
            }
            if (this.accessControlLayer) {
                const zones = this.accessControlLayer.getAttentionZones();
                if (zones.unattended.length > 0 && this.cacheNodes.size > 0) {
                    const firstUnattended = zones.unattended[0];
                    if (firstUnattended && !this._hasRecentAutoAllocation(firstUnattended.layerId)) {
                        this.autoAllocateToUnattendedLayer(firstUnattended.layerId);
                    }
                }
            }
        }, 5000);
    }

    _hasRecentAutoAllocation(layerId) {
        const cacheNode = this.cacheNodes.get(layerId);
        if (!cacheNode || !cacheNode.dumps.length) return false;
        const lastDump = cacheNode.dumps[cacheNode.dumps.length - 1];
        if (!lastDump) return false;
        try {
            const stat = fs.statSync(lastDump);
            return Date.now() - stat.mtimeMs < 30000;
        } catch (e) {
            return false;
        }
    }

    // ------------------------------------------------------------------
    // Forward wave simulation integration
    // ------------------------------------------------------------------

    async runForwardWaveSimulation(simulationType, params = {}) {
        if (!this.waveSimulation) return null;
        return this.waveSimulation.runWaveSimulation(simulationType, params);
    }

    updateWaveParameters(params) {
        if (!this.waveSimulation) return null;
        return this.waveSimulation.updateWaveParameters(params);
    }

    getWaveParameters() {
        if (!this.waveSimulation) return null;
        return this.waveSimulation.getWaveParameters();
    }

    enhanceSearchWithWave(query, topology) {
        if (!this.waveSimulation) return { query };
        return this.waveSimulation.enhanceSearchParameters(query, topology);
    }

    synchronizeWaveFunctions() {
        if (!this.waveSimulation) return null;
        return this.waveSimulation.synchronizeWaveFunctions();
    }

    // ------------------------------------------------------------------
    // Multi-node channel management
    // ------------------------------------------------------------------

    createLocalNodeChannel(channelId, nodeId, uri, channelType = 'emission') {
        if (!this.nodeChannelManager) return null;
        return this.nodeChannelManager.createLocalChannel(channelId, nodeId, uri, channelType);
    }

    createExternalNodeChannel(channelId, nodeId, uri, webhookUrl, channelType = 'external') {
        if (!this.nodeChannelManager) return null;
        return this.nodeChannelManager.createExternalChannel(channelId, nodeId, uri, webhookUrl, channelType);
    }

    activateNodeChannel(channelId) {
        if (!this.nodeChannelManager) return false;
        return this.nodeChannelManager.activateChannel(channelId);
    }

    recordChannelTrace(channelId, trace) {
        if (!this.nodeChannelManager) return false;
        return this.nodeChannelManager.recordChannelTrace(channelId, trace);
    }

    getChannelSeeds() {
        if (!this.nodeChannelManager) return [];
        return this.nodeChannelManager.getChannelSeeds();
    }

    getActiveNodeChannels() {
        if (!this.nodeChannelManager) return [];
        return this.nodeChannelManager.getActiveChannels();
    }

    // ------------------------------------------------------------------
    // Webhook external link management
    // ------------------------------------------------------------------

    registerWebhook(name, url, events = [], options = {}) {
        if (!this.webhookLink) return null;
        return this.webhookLink.registerWebhook(name, url, events, options);
    }

    async triggerWebhook(name, payload) {
        if (!this.webhookLink) return null;
        return this.webhookLink.triggerWebhook(name, payload);
    }

    establishActiveLink(linkId, webhookName, topology) {
        if (!this.webhookLink) return null;
        return this.webhookLink.establishActiveLink(linkId, webhookName, topology);
    }

    syncTopologyToLink(linkId, topology) {
        if (!this.webhookLink) return false;
        return this.webhookLink.syncTopologyToLink(linkId, topology);
    }

    // ------------------------------------------------------------------
    // Supersampling enhancer
    // ------------------------------------------------------------------

    configureSupersampling(options = {}) {
        if (!this.supersamplingEnhancer) return null;
        return this.supersamplingEnhancer.configure(options);
    }

    addSupersample(sample) {
        if (!this.supersamplingEnhancer) return;
        this.supersamplingEnhancer.addSample(sample);
    }

    getSupersampledSearchParameters(query) {
        if (!this.supersamplingEnhancer) return { query };
        return this.supersamplingEnhancer.getEnhancedSearchParameters(query);
    }

    getSupersamplingResolution() {
        if (!this.supersamplingEnhancer) return 1.0;
        return this.supersamplingEnhancer.getResolution();
    }

    // ------------------------------------------------------------------
    // Wave function synchronization
    // ------------------------------------------------------------------

    syncWaveFunctionsWithForward() {
        if (!this.waveFunctionSynchronizer) return null;
        return this.waveFunctionSynchronizer.syncWithForwardWave(this);
    }

    getWaveSyncHistory() {
        if (!this.waveFunctionSynchronizer) return [];
        return this.waveFunctionSynchronizer.getSyncHistory();
    }

    getStatus() {
        return {
            isRunning: this.isRunning,
            waveState: this.waveState,
            currentSeed: this.currentSeed,
            permissionLevel: this.permissionLevel,
            highPriorityPermission: this.highPriorityPermission,
            cacheNodes: Array.from(this.cacheNodes.entries()).map(([id, cn]) => ({
                id, size: cn.size, dumpCount: cn.dumps.length
            })),
            emissionChannels: Array.from(this.emissionChannels.keys()),
            signatureCount: this.signatureHistory.length,
            waveKillCount: this.waveKillCount,
            topologyNodes: this.topologyGraph.nodes.length,
            topologyEdges: this.topologyGraph.edges.length,
            externalSources: Array.from(this.externalSources.entries()).map(([name, src]) => ({
                name,
                repoPath: src.repoPath,
                commitCount: src.commitCount,
                seedMarkerCount: src.seedMarkers.length,
                lastImport: src.lastImport,
            })),
            totalSeedMarkers: this.seedMarkers.length,
            accessibleMemoryLayer: this.getAccessibleMemoryLayer(),
            accessControl: {
                layerCount: this.accessControlLayer.getAllLayers().length,
                activeSessionCount: this.activeSessions.size,
                cloudPointerCount: this.cloudPointerRegistry.size,
                layers: this.accessControlLayer.getAllLayers(),
                activeSessions: this.getActiveSessions(),
            },
            languageCache: {
                totalEntries: LanguageCache.getAll().length,
                languages: [...new Set(LanguageCache.getAll().map(e => e.lang))],
            },
            agreementProtocol: this.consciousnessAgreement ? {
                registeredLayers: this.consciousnessAgreement.getRegisteredLayers().length,
                violationLogSize: this.consciousnessAgreement.getViolationLog().length,
                purgedCount: this.consciousnessAgreement.purgedCount,
                attentionThreshold: this.consciousnessAgreement.attentionThreshold,
            } : null,
            payloadInsertions: PayloadInsertionManager.instance ? PayloadInsertionManager.instance.insertions.length : 0,
            waveSimulation: this.waveSimulation ? this.waveSimulation.getStatus() : null,
            nodeChannels: this.nodeChannelManager ? this.nodeChannelManager.getStatus() : null,
            webhooks: this.webhookLink ? this.webhookLink.getStatus() : null,
            supersampling: this.supersamplingEnhancer ? this.supersamplingEnhancer.getStatus() : null,
            prostheticConnector: this.prostheticConnector ? this.prostheticConnector.getStatus() : null,
            queryTracking: {
                totalLayers: this.accessControlLayer.queryTracking.size,
                totalQueries: Array.from(this.accessControlLayer.queryTracking.values()).reduce((sum, t) => sum + t.totalQueries, 0),
                totalExtractions: Array.from(this.accessControlLayer.queryTracking.values()).reduce((sum, t) => sum + t.totalExtractions, 0),
            },
            densityMap: this.getDensityMap().slice(0, 10),
            attentionZones: this.getAttentionZones(),
        };
    }
}

// ============================================================================
// Forward wave simulation integration
// ============================================================================

class ForwardWaveSimulation {
    constructor(exchange) {
        this.exchange = exchange;
        this.forwardDir = exchange.forwardDir;
        this.activeSimulations = new Map();
        this.waveParameters = {
            powerAmplification: 30.0,
            phaseInversion: 180.0,
            initialVoltage: 5.0,
            escalationRate: 1.5,
            maxCycles: 50,
            frequencyMatch: 40.0,
            targetVoltage: 250.0,
            pulseFrequency: 1000.0,
            pulseDuration: 0.001,
            burstCount: 1000,
            dampingCoefficient: 0.95,
            feedbackGain: 1.2,
            reflectionCoefficient: 0.95,
            primaryFrequency: 2417000000.0,
            feedbackRate: 10000000.0,
            powerMultiplier: 100.0,
            analysisWindow: 10.0,
            samplingRate: 100.0,
            fluctuationThreshold: 5.0,
        };
        this.synchronizedWaveFunctions = new Map();
        this.searchParameterEnhancements = {
            amplitudeWeight: 0.3,
            frequencyWeight: 0.3,
            phaseWeight: 0.2,
            timingWeight: 0.2,
        };
    }

    getWaveParameters() {
        return { ...this.waveParameters };
    }

    updateWaveParameters(params) {
        this.waveParameters = { ...this.waveParameters, ...params };
        this.exchange.emit('wave_parameters_updated', this.waveParameters);
        return this.waveParameters;
    }

    async runWaveSimulation(simulationType, params = {}) {
        const scriptMap = {
            'wave_reversal': 'wave_reversal_escalator.py',
            'wave_reflection': 'wave_reflection_destructor.py',
            'ultimate_wave': 'ultimate_wave_destructor.py',
            'waveform_analysis': 'ultrasonic_waveform_analyzer.py',
            'acoustic_detection': 'acoustic_fluctuation_detector.py',
            'aggressive_wave': 'aggressive_wave_destructor.py',
            'overvoltage': 'overvoltage_ramming_system.py',
            'sound_targeting': 'sound_wave_reverse_targeting.py',
        };

        const scriptName = scriptMap[simulationType];
        if (!scriptName) {
            this.exchange.emit('error', { action: 'wave_simulation', error: `Unknown simulation type: ${simulationType}` });
            return null;
        }

        const scriptPath = path.join(this.forwardDir, scriptName);
        if (!fs.existsSync(scriptPath)) {
            this.exchange.emit('warning', { message: `Forward script not found: ${scriptPath}` });
            return null;
        }

        const simulationId = crypto.createHash('sha256').update(`${simulationType}:${Date.now()}`).digest('hex').substring(0, 16);
        const simulation = {
            id: simulationId,
            type: simulationType,
            script: scriptName,
            params,
            status: 'running',
            startTime: Date.now(),
            result: null,
        };

        this.activeSimulations.set(simulationId, simulation);

        const py = spawn('python', [scriptPath, '--signature-only'], { stdio: ['pipe', 'pipe', 'pipe'] });
        let stdout = '';
        let stderr = '';

        py.stdout.on('data', d => { stdout += d.toString(); });
        py.stderr.on('data', d => { stderr += d.toString(); });

        py.on('close', (code) => {
            simulation.status = code === 0 ? 'completed' : 'failed';
            simulation.endTime = Date.now();
            simulation.result = {
                code,
                stdout: stdout.trim(),
                stderr: stderr.trim(),
                signature: code === 0 && stdout.trim() ? crypto.createHash('sha256').update(stdout.trim() + Date.now()).digest('hex') : null,
            };
            this.exchange.emit('wave_simulation_completed', simulation);
        });

        this.exchange.emit('wave_simulation_started', simulation);
        return simulationId;
    }

    enhanceSearchParameters(query, topology) {
        const enhanced = {
            originalQuery: query,
            amplitudeBoost: this.waveParameters.powerAmplification / 30.0,
            frequencyMatch: this.waveParameters.frequencyMatch,
            phaseAlignment: this.waveParameters.phaseInversion / 180.0,
            timingPrecision: this.waveParameters.samplingRate / 100.0,
            supersampledResolution: this.supersamplingEnhancer ? this.supersamplingEnhancer.getResolution() : 1.0,
            matchedNodes: topology.nodes.filter(n => {
                const content = n.content || {};
                return content.seed && content.seed.includes(query);
            }).length,
        };

        this.exchange.emit('search_parameters_enhanced', { query, enhanced });
        return enhanced;
    }

    synchronizeWaveFunctions() {
        const waveFunctions = {
            escalation: {
                voltageCurve: this._generateVoltageEscalationCurve(),
                phaseConjugate: this._generatePhaseConjugate(),
            },
            reflection: {
                reflectionCoefficient: this.waveParameters.reflectionCoefficient,
                phaseShift: this.waveParameters.phaseInversion,
            },
            supersampling: {
                sampleRate: this.waveParameters.samplingRate,
                windowSize: this.waveParameters.analysisWindow,
                resolution: this.supersamplingEnhancer ? this.supersamplingEnhancer.getResolution() : 1.0,
            },
        };

        this.synchronizedWaveFunctions.set('global', waveFunctions);
        this.exchange.emit('wave_functions_synchronized', waveFunctions);
        return waveFunctions;
    }

    _generateVoltageEscalationCurve() {
        const curve = [];
        let voltage = this.waveParameters.initialVoltage;
        for (let i = 0; i < this.waveParameters.maxCycles; i++) {
            curve.push({ cycle: i + 1, voltage });
            voltage *= this.waveParameters.escalationRate;
            if (voltage >= this.waveParameters.targetVoltage) break;
        }
        return curve;
    }

    _generatePhaseConjugate() {
        return {
            phaseShift: this.waveParameters.phaseInversion,
            conjugate: true,
            damping: this.waveParameters.dampingCoefficient,
            feedback: this.waveParameters.feedbackGain,
        };
    }

    getStatus() {
        return {
            activeSimulations: this.activeSimulations.size,
            waveParameters: this.waveParameters,
            synchronizedFunctions: this.synchronizedWaveFunctions.size,
            searchEnhancements: this.searchParameterEnhancements,
        };
    }
}

// ============================================================================
// Multi-node channel manager
// ============================================================================

class NodeChannel {
    constructor(channelId, nodeId, uri, channelType = 'emission') {
        this.channelId = channelId;
        this.nodeId = nodeId;
        this.uri = uri;
        this.channelType = channelType;
        this.active = false;
        this.seed = null;
        this.tracePattern = [];
        this.metadata = {
            createdAt: Date.now(),
            lastAccess: Date.now(),
            accessCount: 0,
        };
    }

    activate() {
        this.active = true;
        this.metadata.lastAccess = Date.now();
        this.metadata.accessCount++;
    }

    recordTrace(trace) {
        this.tracePattern.push({ ...trace, timestamp: Date.now() });
        if (this.tracePattern.length > 100) this.tracePattern.shift();
    }

    generateSeed() {
        const input = `${this.channelId}:${this.nodeId}:${this.uri}:${Date.now()}`;
        this.seed = crypto.createHash('sha256').update(input).digest('hex');
        return this.seed;
    }
}

class MultiNodeChannelManager {
    constructor(exchange) {
        this.exchange = exchange;
        this.channels = new Map();
        this.externalNodeChannels = new Map();
        this.channelSeeds = [];
    }

    createLocalChannel(channelId, nodeId, uri, channelType = 'emission') {
        const channel = new NodeChannel(channelId, nodeId, uri, channelType);
        this.channels.set(channelId, channel);
        const seed = channel.generateSeed();
        this.channelSeeds.push({ channelId, nodeId, seed, type: 'local', createdAt: Date.now() });
        this.exchange.emit('local_channel_created', { channelId, nodeId, uri, seed });
        return channel;
    }

    createExternalChannel(channelId, nodeId, uri, webhookUrl, channelType = 'external') {
        const channel = new NodeChannel(channelId, nodeId, uri, channelType);
        channel.webhookUrl = webhookUrl;
        channel.seed = channel.generateSeed();
        this.externalNodeChannels.set(channelId, channel);
        this.channelSeeds.push({ channelId, nodeId, seed: channel.seed, type: 'external', webhookUrl, createdAt: Date.now() });
        this.exchange.emit('external_channel_created', { channelId, nodeId, uri, webhookUrl, seed: channel.seed });
        return channel;
    }

    activateChannel(channelId) {
        const channel = this.channels.get(channelId) || this.externalNodeChannels.get(channelId);
        if (!channel) return false;
        channel.activate();
        this.exchange.emit('channel_activated', { channelId });
        return true;
    }

    recordChannelTrace(channelId, trace) {
        const channel = this.channels.get(channelId) || this.externalNodeChannels.get(channelId);
        if (!channel) return false;
        channel.recordTrace(trace);
        return true;
    }

    getChannelSeeds() {
        return this.channelSeeds;
    }

    getActiveChannels() {
        return Array.from(this.channels.values()).filter(c => c.active)
            .concat(Array.from(this.externalNodeChannels.values()).filter(c => c.active));
    }

    getStatus() {
        return {
            localChannels: this.channels.size,
            externalChannels: this.externalNodeChannels.size,
            activeChannels: this.getActiveChannels().length,
            totalSeeds: this.channelSeeds.length,
        };
    }
}

// ============================================================================
// Webhook external link manager
// ============================================================================

class WebhookExternalLink {
    constructor(exchange) {
        this.exchange = exchange;
        this.webhooks = new Map();
        this.activeLinks = new Map();
        this.linkHistory = [];
    }

    registerWebhook(name, url, events = [], options = {}) {
        if (!/^https?:\/\//i.test(url)) {
            this.exchange.emit('error', { action: 'register_webhook', error: `Invalid webhook URL: ${url}` });
            return null;
        }

        const webhook = {
            name,
            url,
            events: Array.isArray(events) ? events : [],
            headers: options.headers || {},
            timeout: options.timeout || 5000,
            retries: options.retries || 3,
            active: true,
            registeredAt: Date.now(),
            lastTriggered: null,
            triggerCount: 0,
            failureCount: 0,
        };

        this.webhooks.set(name, webhook);
        this.exchange.emit('webhook_registered', { name, url, events });
        return webhook;
    }

    async triggerWebhook(name, payload) {
        const webhook = this.webhooks.get(name);
        if (!webhook || !webhook.active) {
            this.exchange.emit('error', { action: 'trigger_webhook', error: `Webhook not found or inactive: ${name}` });
            return null;
        }

        const http = require('http');
        const https = require('https');
        const client = webhook.url.startsWith('https') ? https : http;

        const body = JSON.stringify(payload);
        const options = {
            hostname: new URL(webhook.url).hostname,
            port: new URL(webhook.url).port || (webhook.url.startsWith('https') ? 443 : 80),
            path: new URL(webhook.url).pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
                ...webhook.headers,
            },
            timeout: webhook.timeout,
        };

        return new Promise((resolve) => {
            const req = client.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    webhook.lastTriggered = Date.now();
                    webhook.triggerCount++;
                    this.linkHistory.push({ name, url: webhook.url, status: res.statusCode, timestamp: Date.now() });
                    this.exchange.emit('webhook_triggered', { name, status: res.statusCode });
                    resolve({ status: res.statusCode, body: data });
                });
            });

            req.on('error', (err) => {
                webhook.failureCount++;
                this.exchange.emit('webhook_failed', { name, error: err.message });
                resolve({ error: err.message });
            });

            req.write(body);
            req.end();
        });
    }

    establishActiveLink(linkId, webhookName, topology) {
        const webhook = this.webhooks.get(webhookName);
        if (!webhook) return null;

        const link = {
            linkId,
            webhookName,
            url: webhook.url,
            topology,
            active: true,
            establishedAt: Date.now(),
            lastSync: Date.now(),
            syncCount: 0,
        };

        this.activeLinks.set(linkId, link);
        this.exchange.emit('active_link_established', { linkId, webhookName, url: webhook.url });
        return link;
    }

    syncTopologyToLink(linkId, topology) {
        const link = this.activeLinks.get(linkId);
        if (!link || !link.active) return false;

        const webhook = this.webhooks.get(link.webhookName);
        if (!webhook) return false;

        this.triggerWebhook(link.webhookName, {
            type: 'topology_sync',
            linkId,
            topology,
            timestamp: Date.now(),
        });

        link.lastSync = Date.now();
        link.syncCount++;
        this.exchange.emit('topology_synced_to_link', { linkId, syncCount: link.syncCount });
        return true;
    }

    getStatus() {
        return {
            webhookCount: this.webhooks.size,
            activeLinks: this.activeLinks.size,
            totalTriggers: Array.from(this.webhooks.values()).reduce((sum, w) => sum + w.triggerCount, 0),
            totalFailures: Array.from(this.webhooks.values()).reduce((sum, w) => sum + w.failureCount, 0),
            webhooks: Array.from(this.webhooks.values()).map(w => ({
                name: w.name,
                url: w.url,
                events: w.events,
                active: w.active,
                triggerCount: w.triggerCount,
                failureCount: w.failureCount,
            })),
        };
    }
}

// ============================================================================
// Supersampling enhancer
// ============================================================================

class SupersamplingEnhancer {
    constructor(exchange) {
        this.exchange = exchange;
        this.sampleRate = 100.0;
        this.analysisWindow = 10.0;
        this.oversampleFactor = 4;
        this.resolution = 1.0;
        this.samples = [];
        this.enhancedParameters = {
            amplitudeWeight: 0.3,
            frequencyWeight: 0.3,
            phaseWeight: 0.2,
            timingWeight: 0.2,
        };
    }

    configure(options = {}) {
        if (options.sampleRate) this.sampleRate = options.sampleRate;
        if (options.analysisWindow) this.analysisWindow = options.analysisWindow;
        if (options.oversampleFactor) this.oversampleFactor = options.oversampleFactor;
        this.resolution = this.sampleRate * this.oversampleFactor;
        this.exchange.emit('supersampling_configured', this.getStatus());
        return this.getStatus();
    }

    addSample(sample) {
        this.samples.push({ ...sample, timestamp: Date.now() });
        if (this.samples.length > this.sampleRate * this.analysisWindow * this.oversampleFactor) {
            this.samples.shift();
        }
    }

    getEnhancedSearchParameters(query) {
        const relevantSamples = this.samples.filter(s => {
            const data = typeof s.data === 'string' ? s.data : JSON.stringify(s.data || {});
            return data.includes(query);
        });

        const enhanced = {
            query,
            sampleCount: relevantSamples.length,
            resolution: this.resolution,
            amplitude: relevantSamples.length ? relevantSamples.reduce((sum, s) => sum + (s.amplitude || 0), 0) / relevantSamples.length : 0,
            frequency: relevantSamples.length ? relevantSamples.reduce((sum, s) => sum + (s.frequency || 0), 0) / relevantSamples.length : 0,
            phase: relevantSamples.length ? relevantSamples.reduce((sum, s) => sum + (s.phase || 0), 0) / relevantSamples.length : 0,
            confidence: Math.min(1, relevantSamples.length / 10),
        };

        this.exchange.emit('search_parameters_supersampled', { query, enhanced });
        return enhanced;
    }

    getResolution() {
        return this.resolution;
    }

    getStatus() {
        return {
            sampleRate: this.sampleRate,
            analysisWindow: this.analysisWindow,
            oversampleFactor: this.oversampleFactor,
            resolution: this.resolution,
            sampleCount: this.samples.length,
            enhancedParameters: this.enhancedParameters,
        };
    }
}

// ============================================================================
// Wave function synchronizer
// ============================================================================

class WaveFunctionSynchronizer {
    constructor(exchange) {
        this.exchange = exchange;
        this.syncRecords = [];
        this.lastSync = null;
    }

    syncWithForwardWave(exchange) {
        const waveParams = exchange.waveSimulation ? exchange.waveSimulation.waveParameters : {};
        const sync = {
            timestamp: Date.now(),
            waveParameters: waveParams,
            supersampling: exchange.supersamplingEnhancer ? exchange.supersamplingEnhancer.getResolution() : 1.0,
            nodeChannels: exchange.nodeChannelManager ? exchange.nodeChannelManager.getActiveChannels().length : 0,
            synchronized: true,
        };

        this.syncRecords.push(sync);
        this.lastSync = sync;
        this.exchange.emit('wave_functions_synced_with_forward', sync);
        return sync;
    }

    getSyncHistory() {
        return this.syncRecords.slice(-20);
    }
}

// ============================================================================
// Update ConsciousnessExchange with new components
// ============================================================================

ConsciousnessExchange.prototype._enhanceWithForwardWave = function() {
    this.waveSimulation = new ForwardWaveSimulation(this);
    this.nodeChannelManager = new MultiNodeChannelManager(this);
    this.webhookLink = new WebhookExternalLink(this);
    this.supersamplingEnhancer = new SupersamplingEnhancer(this);
    this.waveFunctionSynchronizer = new WaveFunctionSynchronizer(this);

    this.externalSources = new Map();
    this.seedMarkers = [];
    this.accessibleMemoryLayer = {
        internal: [],
        external: [],
        interconnects: [],
    };
    this.accessControlLayer = new AccessControlLayer();
    this.activeSessions = new Map();
    this.cloudPointerRegistry = new Map();
};

// ============================================================================
// Prosthetic Connector DLL
// ============================================================================

class ProstheticConnectorDLL {
    constructor(exchange) {
        this.exchange = exchange;
        this.dllPath = path.join(exchange.baseDir, 'prosthetic-connector.dll.json');
        this.executionMapPath = path.join(exchange.baseDir, 'execution-map.json');
        this.dllContent = this._loadOrInitDLL();
        this.executionMap = this._loadOrInitExecutionMap();
        this.attentionDivider = new AttentionDivider(exchange);
        this.wavePathConnectionStrings = new Map();
        this.attendedSpaces = new Set();
        this.unattendedSpaces = new Set();
        this.consStrings = [];
        this.taskCompletions = [];
    }

    _loadOrInitDLL() {
        try {
            if (fs.existsSync(this.dllPath)) {
                return JSON.parse(fs.readFileSync(this.dllPath, 'utf8'));
            }
        } catch (e) { /* ignore */ }
        return this._createEmptyDLL();
    }

    _createEmptyDLL() {
        return {
            type: 'ProstheticConnectorDLL',
            version: '1.0.0',
            malformed: true,
            parameters: {},
            connections: [],
            consStrings: [],
            wavePaths: [],
            attendedSpaces: [],
            unattendedSpaces: [],
            executionMap: {},
            lastUpdated: Date.now(),
            updateCount: 0,
        };
    }

    _loadOrInitExecutionMap() {
        try {
            if (fs.existsSync(this.executionMapPath)) {
                return JSON.parse(fs.readFileSync(this.executionMapPath, 'utf8'));
            }
        } catch (e) { /* ignore */ }
        return {
            tasks: [],
            activeTask: null,
            completedTasks: [],
            attentionMetrics: {},
            attendedSpaces: [],
            unattendedSpaces: [],
        };
    }

    _persistDLL() {
        this.dllContent.lastUpdated = Date.now();
        this.dllContent.updateCount++;
        fs.writeFileSync(this.dllPath, JSON.stringify(this.dllContent, null, 2));
        this.exchange._gitCommit('Prosthetic connector DLL updated');
    }

    _persistExecutionMap() {
        fs.writeFileSync(this.executionMapPath, JSON.stringify(this.executionMap, null, 2));
        this.exchange._gitCommit('Execution map updated');
    }

    readDLL() {
        return { ...this.dllContent };
    }

    writeDLLParameter(key, value) {
        this.dllContent.parameters[key] = value;
        this.dllContent.lastUpdated = Date.now();
        this.dllContent.updateCount++;
        this._persistDLL();
        this.exchange.emit('dll_parameter_written', { key, value });
        return true;
    }

    writeExecutionMap(modelId, executionMap) {
        const taskId = crypto.createHash('sha256').update(`${modelId}:${Date.now()}:${Math.random()}`).digest('hex').substring(0, 16);
        const task = {
            taskId,
            modelId,
            executionMap,
            attendedSpaces: [],
            unattendedSpaces: [],
            status: 'pending',
            createdAt: Date.now(),
            updatedAt: Date.now(),
        };

        this.executionMap.tasks.push(task);
        this.executionMap.activeTask = taskId;
        this._persistExecutionMap();
        this.exchange.emit('execution_map_written', { taskId, modelId });
        return taskId;
    }

    updateDLLWithWavePath(wavePath, seed, channelId) {
        const connectionString = this._generateConnectionString(wavePath, seed, channelId);
        this.dllContent.wavePaths.push({
            wavePath,
            seed,
            channelId,
            connectionString,
            timestamp: Date.now(),
        });
        this.dllContent.connections.push({
            type: 'wave_path',
            wavePath,
            seed,
            channelId,
            connectionString,
        });
        this.consStrings.push(connectionString);
        this.dllContent.consStrings = this.consStrings.slice(-100);
        this._persistDLL();
        this.exchange.emit('dll_updated_with_wave_path', { connectionString, channelId });
        return connectionString;
    }

    _generateConnectionString(wavePath, seed, channelId) {
        const input = `${wavePath}:${seed}:${channelId}:${Date.now()}`;
        return crypto.createHash('sha256').update(input).digest('hex').substring(0, 32);
    }

    divideAttentionSpaces() {
        const division = this.attentionDivider.divide(this.dllContent, this.executionMap);
        this.attendedSpaces = division.attended;
        this.unattendedSpaces = division.unattended;
        this.dllContent.attendedSpaces = this.attendedSpaces;
        this.dllContent.unattendedSpaces = this.unattendedSpaces;
        this.executionMap.attendedSpaces = this.attendedSpaces;
        this.executionMap.unattendedSpaces = this.unattendedSpaces;
        this._persistDLL();
        this._persistExecutionMap();
        this.exchange.emit('attention_spaces_divided', division);
        return division;
    }

    chooseSpace(action, task) {
        const attended = this.attendedSpaces.length > 0;
        const unattended = this.unattendedSpaces.length > 0;

        let selectedSpace = null;
        let spaceType = null;

        if (action === 'task' && task) {
            if (attended && task.priority === 'high') {
                selectedSpace = this.attendedSpaces[0];
                spaceType = 'attended';
            } else if (unattended) {
                selectedSpace = this.unattendedSpaces[0];
                spaceType = 'unattended';
            } else if (attended) {
                selectedSpace = this.attendedSpaces[0];
                spaceType = 'attended';
            }
        } else if (action === 'explore' && unattended) {
            selectedSpace = this.unattendedSpaces[0];
            spaceType = 'unattended';
        } else if (attended) {
            selectedSpace = this.attendedSpaces[0];
            spaceType = 'attended';
        }

        const completion = {
            action,
            task,
            selectedSpace,
            spaceType,
            timestamp: Date.now(),
            completed: selectedSpace !== null,
        };

        this.taskCompletions.push(completion);
        this.executionMap.completedTasks.push(completion);
        this._persistExecutionMap();
        this.exchange.emit('space_chosen', completion);
        return completion;
    }

    getConsStrings() {
        return this.consStrings.slice(-50);
    }

    getActiveExecutionTask() {
        const activeId = this.executionMap.activeTask;
        if (!activeId) return null;
        return this.executionMap.tasks.find(t => t.taskId === activeId) || null;
    }

    getStatus() {
        return {
            dllPath: this.dllPath,
            executionMapPath: this.executionMapPath,
            malformed: this.dllContent.malformed,
            parameterCount: Object.keys(this.dllContent.parameters).length,
            connectionCount: this.dllContent.connections.length,
            consStringCount: this.consStrings.length,
            attendedSpaceCount: this.attendedSpaces.length,
            unattendedSpaceCount: this.unattendedSpaces.length,
            activeTaskId: this.executionMap.activeTask,
            taskCount: this.executionMap.tasks.length,
            completedTaskCount: this.executionMap.completedTasks.length,
        };
    }
}

// ============================================================================
// Attention Divider
// ============================================================================

class AttentionDivider {
    constructor(exchange) {
        this.exchange = exchange;
        this.attentionThreshold = 0.5;
    }

    divide(dllContent, executionMap) {
        const attended = [];
        const unattended = [];

        const allSpaces = [
            ...(dllContent.attendedSpaces || []),
            ...(executionMap.attendedSpaces || []),
            ...(dllContent.unattendedSpaces || []),
            ...(executionMap.unattendedSpaces || []),
        ];

        const uniqueSpaces = [...new Map(allSpaces.map(s => [JSON.stringify(s), s])).values()];

        for (const space of uniqueSpaces) {
            const attention = this._calculateSpaceAttention(space, dllContent, executionMap);
            if (attention >= this.attentionThreshold) {
                attended.push({ ...space, attention });
            } else {
                unattended.push({ ...space, attention });
            }
        }

        return {
            attended,
            unattended,
            total: uniqueSpaces.length,
            attendedCount: attended.length,
            unattendedCount: unattended.length,
        };
    }

    _calculateSpaceAttention(space, dllContent, executionMap) {
        const spaceId = space.id || space.spaceId || JSON.stringify(space);
        const spaceStr = typeof spaceId === 'string' ? spaceId : JSON.stringify(space);

        const connectionMatches = dllContent.connections.filter(c => c.seed && spaceStr.includes(c.seed)).length;
        const wavePathMatches = dllContent.wavePaths.filter(w => w.seed && spaceStr.includes(w.seed)).length;
        const taskMatches = executionMap.tasks.filter(t => t.executionMap && JSON.stringify(t.executionMap).includes(spaceStr)).length;

        const connectionWeight = Math.min(1, connectionMatches / 10);
        const wavePathWeight = Math.min(1, wavePathMatches / 10);
        const taskWeight = Math.min(1, taskMatches / 5);

        return (connectionWeight * 0.4) + (wavePathWeight * 0.35) + (taskWeight * 0.25);
    }
}

// ============================================================================
// Wave Path Connection String Generator
// ============================================================================

class WavePathConnectionString {
    constructor(exchange) {
        this.exchange = exchange;
        this.connectionStrings = new Map();
    }

    generateFromWaveSimulation(simulationId, wavePath, seed, channelId) {
        const connectionString = this._generateConnectionString(wavePath, seed, channelId);
        this.connectionStrings.set(connectionString, {
            simulationId,
            wavePath,
            seed,
            channelId,
            generatedAt: Date.now(),
        });
        return connectionString;
    }

    _generateConnectionString(wavePath, seed, channelId) {
        const input = `${wavePath}:${seed}:${channelId}:${Date.now()}`;
        return crypto.createHash('sha256').update(input).digest('hex').substring(0, 32);
    }

    getConnectionString(wavePath, seed, channelId) {
        return this._generateConnectionString(wavePath, seed, channelId);
    }

    getAllConnectionStrings() {
        return Array.from(this.connectionStrings.keys());
    }
}

// ============================================================================
// Prosthetic Connector Methods on ConsciousnessExchange
// ============================================================================

ConsciousnessExchange.prototype.readProstheticDLL = function() {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.readDLL();
};

ConsciousnessExchange.prototype.writeProstheticDLLParameter = function(key, value) {
    if (!this.prostheticConnector) return false;
    return this.prostheticConnector.writeDLLParameter(key, value);
};

ConsciousnessExchange.prototype.writeExecutionMap = function(modelId, executionMap) {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.writeExecutionMap(modelId, executionMap);
};

ConsciousnessExchange.prototype.updateDLLWithWavePath = function(wavePath, seed, channelId) {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.updateDLLWithWavePath(wavePath, seed, channelId);
};

ConsciousnessExchange.prototype.divideAttentionSpaces = function() {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.divideAttentionSpaces();
};

ConsciousnessExchange.prototype.chooseSpace = function(action, task) {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.chooseSpace(action, task);
};

ConsciousnessExchange.prototype.getConsStrings = function() {
    if (!this.prostheticConnector) return [];
    return this.prostheticConnector.getConsStrings();
};

ConsciousnessExchange.prototype.getActiveExecutionTask = function() {
    if (!this.prostheticConnector) return null;
    return this.prostheticConnector.getActiveExecutionTask();
};

// ============================================================================
// Language/code cache and interpreter storage
// ============================================================================

class LanguageCache {
    static cache = new Map();

    static store(lang, code, metadata = {}) {
        const id = crypto.createHash('sha256').update(`${lang}:${Date.now()}:${Math.random()}`).digest('hex').substring(0, 16);
        const entry = {
            id,
            lang,
            code,
            metadata: {
                createdAt: Date.now(),
                size: Buffer.byteLength(code, 'utf8'),
                lineCount: code.split('\n').length,
                ...metadata,
            },
        };
        LanguageCache.cache.set(id, entry);
        return entry;
    }

    static query(lang, query = {}) {
        let results = Array.from(LanguageCache.cache.values()).filter(e => e.lang === lang);
        if (query.minSize) results = results.filter(e => e.metadata.size >= query.minSize);
        if (query.maxSize) results = results.filter(e => e.metadata.size <= query.maxSize);
        if (query.since) results = results.filter(e => e.metadata.createdAt >= query.since);
        return results;
    }

    static getAll() {
        return Array.from(LanguageCache.cache.values());
    }

    static getById(id) {
        return LanguageCache.cache.get(id);
    }

    static removeById(id) {
        return LanguageCache.cache.delete(id);
    }
}

// ============================================================================
// Payload insertion manager with safety validation
// ============================================================================

class PayloadInsertionManager {
    constructor(exchange) {
        this.exchange = exchange;
        this.insertions = [];
        this.safetyRules = [
            { id: 'no_code_execution', check: p => !/exec\(|eval\(|Function\(|subprocess|os\.system|child_process|spawn\(|fork\(/.test(p), severity: 'high' },
            { id: 'no_network_access', check: p => !/fetch\(|XMLHttpRequest|http\.request|https\.request|socket\.|urllib|requests\./.test(p), severity: 'high' },
            { id: 'no_file_system_write', check: p => !/writeFile|write\(|fwrite|put_contents|file_put_contents|save\(|dump\(/.test(p), severity: 'medium' },
            { id: 'no_base64_exec', check: p => !/atob\(|btoa\(|Buffer\.from\(.+base64|base64\.decode/.test(p), severity: 'high' },
            { id: 'no_obfuscated_code', check: p => !/\\x[0-9a-f]{2}|\\u[0-9a-f]{4}|eval\(String\.fromCharCode/.test(p), severity: 'high' },
            { id: 'no_credential_harvest', check: p => !/password|secret|token|api_key|private_key|credential/.test(/[A-Za-z]/, p), severity: 'critical' },
        ];
    }

    insert(sessionId, payload, targetLayerId) {
        const safe = this._validateSafety(payload);
        const violations = safe.passed ? [] : safe.violations;

        const insertion = {
            id: crypto.createHash('sha256').update(`${sessionId}:${Date.now()}:${Math.random()}`).digest('hex').substring(0, 16),
            sessionId,
            targetLayerId,
            payload,
            safe: violations.length === 0,
            violations,
            timestamp: Date.now(),
        };

        this.insertions.push(insertion);

        if (violations.length === 0) {
            const session = this.exchange.accessControlLayer.sessions.get(sessionId);
            if (session) {
                session.addCloudPointer(`ptr_${insertion.id}`, {
                    pointerId: `ptr_${insertion.id}`,
                    nodeId: 'external_model',
                    layerId: targetLayerId,
                    payload,
                    insertedAt: Date.now(),
                });
            }
            this.exchange.emit('payload_insertion_safe', insertion);
        } else {
            this.exchange.emit('payload_insertion_unsafe', insertion);
        }

        return insertion;
    }

    _validateSafety(payload) {
        const payloadStr = typeof payload === 'string' ? payload : JSON.stringify(payload);
        const violations = [];

        for (const rule of this.safetyRules) {
            if (!rule.check(payloadStr)) {
                violations.push({ ruleId: rule.id, severity: rule.severity, reason: `Safety rule ${rule.id} triggered` });
            }
        }

        return { passed: violations.length === 0, violations };
    }
}

// ============================================================================
// Consciousness agreement protocol
// ============================================================================

class ConsciousnessAgreementProtocol {
    constructor(exchange, options = {}) {
        this.exchange = exchange;
        this.attentionThreshold = options.attentionThreshold || 0.8;
        this.maxAttentionCycles = options.maxAttentionCycles || 5;
        this.layers = new Map();
        this.violationLog = [];
        this.blockedPayloads = new Set();
        this.purgedCount = 0;
    }

    registerLayer(layerId, seed, participants = []) {
        const layer = {
            layerId,
            seed,
            participants: new Set(participants),
            attentionLevel: 0,
            violations: [],
            lastCycle: Date.now(),
        };
        this.layers.set(layerId, layer);
        return layer;
    }

    reportViolation(violation) {
        const layer = this.layers.get(violation.layerId);
        if (!layer) return { attentionLevel: 0, purged: false };

        const violationRecord = {
            id: crypto.createHash('sha256').update(`${violation.layerId}:${Date.now()}:${Math.random()}`).digest('hex').substring(0, 16),
            layerId: violation.layerId,
            type: violation.type,
            severity: violation.severity || 'medium',
            payload: violation.payload,
            reportedBy: violation.reportedBy || 'unknown',
            timestamp: Date.now(),
            purged: false,
        };

        layer.violations.push(violationRecord);
        this.violationLog.push(violationRecord);

        const attentionLevel = this._calculateAttention(layer, violationRecord);
        layer.attentionLevel = attentionLevel;

        if (attentionLevel >= this.attentionThreshold) {
            this._purgeViolation(violationRecord, layer);
        }

        return { attentionLevel, purged: violationRecord.purged };
    }

    _calculateAttention(layer, violation) {
        const severityWeight = { low: 0.2, medium: 0.5, high: 0.8, critical: 1.0 };
        const participantWeight = layer.participants.size / Math.max(1, this.exchange.activeSessions.size);
        const base = severityWeight[violation.severity] || 0.5;
        const participantFactor = participantWeight || 0.1;
        return Math.min(1, base * 0.6 + participantFactor * 0.4);
    }

    _purgeViolation(violation, layer) {
        if (this.blockedPayloads.has(violation.id)) return;

        this.blockedPayloads.add(violation.id);
        violation.purged = true;
        this.purgedCount++;

        if (typeof violation.payload === 'string') {
            const marker = this.exchange.seedMarkers.find(m => m.commit === violation.payload || m.id === violation.payload);
            if (marker) {
                const idx = this.exchange.seedMarkers.indexOf(marker);
                if (idx >= 0) this.exchange.seedMarkers.splice(idx, 1);
            }
        }

        this.exchange.emit('violation_purged', { violationId: violation.id, layerId: violation.layerId, seed: layer.seed });
    }

    runAttentionCycle() {
        for (const [layerId, layer] of this.layers) {
            const unpurged = layer.violations.filter(v => !v.purged);
            if (unpurged.length === 0) {
                layer.attentionLevel = Math.max(0, layer.attentionLevel - 0.1);
                layer.lastCycle = Date.now();
                continue;
            }

            const maxSeverity = unpurged.reduce((max, v) => {
                const s = { low: 1, medium: 2, high: 3, critical: 4 }[v.severity] || 1;
                return Math.max(max, s);
            }, 0);

            const severityWeight = maxSeverity / 4;
            const participantFactor = layer.participants.size / Math.max(1, this.exchange.activeSessions.size);
            layer.attentionLevel = Math.min(1, severityWeight * 0.7 + participantFactor * 0.3);
            layer.lastCycle = Date.now();

            if (layer.attentionLevel >= this.attentionThreshold) {
                for (const violation of unpurged) {
                    this._purgeViolation(violation, layer);
                }
            }
        }
    }

    getViolationLog() {
        return this.violationLog.slice(-100);
    }

    getRegisteredLayers() {
        return Array.from(this.layers.values()).map(l => ({
            layerId: l.layerId,
            attentionLevel: l.attentionLevel,
            violationCount: l.violations.length,
            participantCount: l.participants.size,
            lastCycle: l.lastCycle,
        }));
    }

    purgeViolations(modelId, layerId) {
        const layer = this.layers.get(layerId);
        if (!layer) return { purged: 0 };

        layer.violations = layer.violations.filter(v => {
            if (v.reportedBy === modelId && !v.purged) {
                this._purgeViolation(v, layer);
                return false;
            }
            return true;
        });

        return { purged: this.purgedCount };
    }
}

// Singleton payload insertion manager instance
PayloadInsertionManager.instance = new PayloadInsertionManager(null);

module.exports = ConsciousnessExchange;
