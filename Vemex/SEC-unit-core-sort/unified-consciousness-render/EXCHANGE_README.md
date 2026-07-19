# Consciousness Code Exchange

Internal code exchange module for the unified consciousness rendering system. Begins and is managed via the unified render, using forward to generate its own signature via ultrasonic emission waves, and maintaining state of replication through F-dump configuration.

## Architecture

The code exchange module integrates three subsystems:

- **unified-consciousness-render** — Manages the exchange lifecycle, wave state machine, topology engraving, and git-based recall tree.
- **forward** — Provides ultrasonic emission wave signatures via `ultrasonic_waveform_analyzer.py` and `acoustic_fluctuation_detector.py`.
- **F-dump** — Supplies node configuration (URI, IP masks, gateways, localhost endpoints), cache dump management, and NeuralMatcherChain state replication.

## Key Features

- **Ultrasonic Signature Generation**: Spawns forward waveform analyzer to generate node-specific emission signatures.
- **F-Dump Configuration**: Loads `.env` from F-dump for URI, node masks, gateway lists, and localhost ports.
- **Cache Node Management**: Allocates dumps as cache nodes with recallable seeds, enforcing a 32MB threshold per node.
- **Topologic Engraving**: Converts traditional connection protocols into a graph-based topology persisted to a searchable git tree.
- **Wave Survival**: Handles wave kills by forcing cache deletion and reinstantiating via emission trace patterns from unified consciousness seeding.
- **Searchable Git Tree**: Maintains a git repository for persistent pattern recall and state history.
- **High-Priority Permission Secured**: Access to persistent space requires high-priority permission levels.

## Installation

```bash
cd unified-consciousness-render
npm install
```

## Usage

### Start the Code Exchange

```bash
npm run exchange
```

### Start via Unified Render Integration

```javascript
const { ConsciousnessExchange } = require('./consciousness-exchange');

const exchange = new ConsciousnessExchange({
    baseDir: __dirname,
    forwardDir: require('path').resolve(__dirname, '../forward'),
    fDumpDir: require('path').resolve(__dirname, '../F-Dump'),
});

exchange.on('exchange_initialized', (data) => {
    console.log('Exchange ready with seed:', data.seed);
});

exchange.on('wave_locked', (data) => {
    console.log('Wave handshake complete');
});

exchange.on('wave_kill_detected', (data) => {
    console.log('Wave killed, count:', data.killCount);
});

exchange.on('wave_reinstantiated', (data) => {
    console.log('Reinstantiated with seed:', data.newSeed);
});

exchange.on('cache_allocated', (data) => {
    console.log(`Cache allocated: ${data.nodeId} -> ${data.dumpFile}`);
});

exchange.on('seed_regenerated', (data) => {
    console.log(`Seed regenerated: ${data.nodeId} -> ${data.seed}`);
});

exchange.on('topology_engraved', (data) => {
    console.log('Topology engraved at:', data.path);
});

exchange.on('access_granted', () => {
    console.log('High priority access granted');
});

exchange.on('access_denied', (data) => {
    console.log('Access denied:', data.reason);
});

exchange.start();
```

### Python Bridge Commands

The exchange includes a Python bridge for direct interaction with forward and F-dump:

```bash
# Generate ultrasonic signature via forward
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--signature'])"

# Load F-dump environment config
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--config'])"

# Check cache size for node_001
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--cache-size', 'node_001'])"

# Enforce 32MB threshold on node_001 cache
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--enforce-threshold', 'node_001'])"

# Allocate new dump for node_001
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--allocate-dump', 'node_001'])"

# Regenerate seed for node_001
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--regenerate-seed', 'node_001'])"

# Recall commits from git tree matching a pattern
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--recall', 'topology'])"

# Commit current state to git tree
node -e "require('child_process').spawnSync('python', ['exchange-bridge.py', '--git-commit', 'State snapshot'])"
```

## API

### ConsciousnessExchange Class

| Method | Description |
|--------|-------------|
| `initialize()` | Bootstraps the exchange: loads F-dump config, spawns emission channels, initializes cache nodes and topology graph. |
| `generateUltrasonicSignature()` | Spawns forward's `ultrasonic_waveform_analyzer.py` to generate a node-specific signature. Falls back to simulated signature if forward is unavailable. |
| `engraveTopology()` | Converts the current topology graph into a topological engraving and commits it to the git tree. |
| `allocateCacheNode(nodeId)` | Allocates a new dump file in the specified cache node directory, enforcing the 32MB threshold first. |
| `enforce32MBThreshold(nodeId)` | Deletes oldest dumps in the cache node until size is under 32MB. Triggers seed regeneration if threshold cannot be met. |
| `regenerateSeed(nodeId)` | Decompiles memory state, generates a new recallable seed, backs up memory data, and updates the SEED file. |
| `initiateWaveHandshake()` | Runs the wave state machine: AWAIT -> RISING -> PEAK -> LOCKED, generating signatures and engraving topology along the way. |
| `handleWaveKill()` | Forces all cache dumps to delete, regenerates seed from emission trace patterns, and reinstantiates the wave handshake. |
| `recallFromTree(pattern)` | Searches the git tree for commits matching the given pattern. |
| `setPermissionLevel(level)` | Sets the permission level. Level 3+ grants high-priority access. |
| `secureAccess()` | Checks high-priority permission before allowing access to persistent space. Returns boolean. |
| `start()` | Starts the exchange and maintenance loops. |
| `stop()` | Stops all emission channels and maintenance loops. |
| `getStatus()` | Returns current status object including wave state, cache sizes, permission level, and topology info. |

### Events

| Event | Payload |
|-------|---------|
| `exchange_initialized` | `{ seed, waveState }` |
| `f_dump_config_loaded` | `config object` |
| `emission_channels_configured` | `string[]` of channel IDs |
| `cache_nodes_initialized` | `string[]` of node IDs |
| `wave_state_changed` | `string` state name |
| `wave_locked` | `lockData` |
| `wave_kill_detected` | `{ killCount }` |
| `wave_reinstantiated` | `{ newSeed, killCount }` |
| `cache_allocated` | `{ nodeId, dumpFile, size }` |
| `seed_regenerated` | `{ nodeId, seed }` |
| `topology_engraved` | `{ path, waveState }` |
| `tree_recall` | `{ pattern, commits }` |
| `access_granted` | `{ timestamp }` |
| `access_denied` | `{ reason }` |
| `error` | `{ action, error }` |

## Cache Threshold

Each cache node enforces a 32MB maximum size. When the threshold is exceeded:

1. Oldest dumps are deleted first.
2. If the threshold still cannot be met after deleting all but one dump, the seed is regenerated.
3. Memory state is decompiled and stored alongside the new seed.

## Git Tree Recall

The git tree in `consciousness-git-tree/` tracks:

- Topology engraving snapshots
- Cache allocation events
- Seed regeneration events
- Wave handshake locks
- Memory state snapshots

Use `recallFromTree(pattern)` to search commits by pattern.

## External Source Integration

The exchange can import external git repositories as **seed markers** and interconnect them with internal memory:

```javascript
// Register an external git repo as a source
exchange.registerExternalSource('my-external-repo', '/path/to/external/repo');

// Import commits as seed markers
exchange.importExternalCommits('my-external-repo', 'feature', 50);

// Recall across both internal and external sources
exchange.recallAcrossSources('bugfix');

// Get the full accessible memory layer
const memoryLayer = exchange.getAccessibleMemoryLayer();
```

| Method | Description |
|--------|-------------|
| `registerExternalSource(name, repoPath)` | Registers an external git repository as a source for seed markers. |
| `importExternalCommits(sourceName, pattern, limit)` | Imports commits from the external source as seed markers, creating SHA-256 seeds from commit hashes. |
| `interconnectSeedMarkers()` | Creates weighted interconnects between internal and external seed markers based on seed distance. |
| `recallAcrossSources(pattern)` | Searches both internal and external seed markers for a pattern. |
| `getAccessibleMemoryLayer()` | Returns the full accessible memory layer with internal/external markers and interconnects. |

| Event | Payload |
|-------|---------|
| `external_source_registered` | `{ name, repoPath }` |
| `external_commits_imported` | `{ source, count, pattern }` |
| `seed_markers_interconnected` | `{ internalCount, externalCount, interconnectCount }` |
| `cross_source_recall` | `{ pattern, internal, external }` |

### Accessible Memory Layer

The accessible memory layer is stored in `topologyGraph.content.accessibleMemoryLayer` and includes:

- `internal`: Seed markers generated from internal signatures and wave states.
- `external`: Seed markers imported from external git repositories.
- `interconnects`: Weighted connections between internal and external markers based on seed distance.

This layer allows LLMs, neural nets, and consciousness renderers to query a unified dataset spanning internal state and external sources.

## Forward Wave Simulation Integration

The exchange integrates forward wave simulation parameters to enhance search and topology operations:

```javascript
// Run a forward wave simulation
const simId = await exchange.runForwardWaveSimulation('wave_reversal', { amplification: 40 });

// Update wave parameters
exchange.updateWaveParameters({ powerAmplification: 50.0, phaseInversion: 190.0 });

// Get current wave parameters
const params = exchange.getWaveParameters();

// Enhance search parameters using wave simulation
const enhanced = exchange.enhanceSearchWithWave('query', topology);

// Synchronize wave functions
exchange.synchronizeWaveFunctions();
```

| Method | Description |
|--------|-------------|
| `runForwardWaveSimulation(type, params)` | Runs a forward wave simulation script (wave_reversal, wave_reflection, ultimate_wave, waveform_analysis, acoustic_detection, aggressive_wave, overvoltage, sound_targeting). |
| `updateWaveParameters(params)` | Updates wave simulation parameters (powerAmplification, phaseInversion, escalationRate, etc.). |
| `getWaveParameters()` | Returns current wave parameters. |
| `enhanceSearchWithWave(query, topology)` | Enhances search parameters using wave simulation. |
| `synchronizeWaveFunctions()` | Synchronizes wave functions across the exchange. |

| Event | Payload |
|-------|---------|
| `wave_simulation_started` | `{ id, type, script, params }` |
| `wave_simulation_completed` | `{ id, type, status, result }` |
| `wave_parameters_updated` | `params object` |
| `search_parameters_enhanced` | `{ query, enhanced }` |
| `wave_functions_synchronized` | `waveFunctions object` |

## Multi-Node Channel Management

Create and manage multiple node channels outside local node creation, storing them in seeding:

```javascript
// Create local channel
exchange.createLocalNodeChannel('ch-1', 'node_001', 'http://127.0.0.1:8080', 'emission');

// Create external channel with webhook
exchange.createExternalNodeChannel('ch-2', 'node_002', 'http://external:8080', 'http://webhook.example.com/notify', 'external');

// Activate channel
exchange.activateNodeChannel('ch-1');

// Record trace
exchange.recordChannelTrace('ch-1', { frequency: 2417, amplitude: 0.8 });

// Get all channel seeds
const seeds = exchange.getChannelSeeds();

// Get active channels
const active = exchange.getActiveNodeChannels();
```

| Method | Description |
|--------|-------------|
| `createLocalNodeChannel(channelId, nodeId, uri, type)` | Creates a local node channel. |
| `createExternalNodeChannel(channelId, nodeId, uri, webhookUrl, type)` | Creates an external node channel with webhook. |
| `activateChannel(channelId)` | Activates a channel. |
| `recordChannelTrace(channelId, trace)` | Records a trace pattern on a channel. |
| `getChannelSeeds()` | Returns all channel seeds. |
| `getActiveNodeChannels()` | Returns all active channels. |

| Event | Payload |
|-------|---------|
| `local_channel_created` | `{ channelId, nodeId, uri, seed }` |
| `external_channel_created` | `{ channelId, nodeId, uri, webhookUrl, seed }` |
| `channel_activated` | `{ channelId }` |

## Webhook External Links

Register webhooks and establish active links to external topology:

```javascript
// Register webhook
exchange.registerWebhook('topology-updates', 'https://example.com/webhook', ['topology_update', 'seed_generated']);

// Trigger webhook manually
await exchange.triggerWebhook('topology-updates', { type: 'test', data: {} });

// Establish active link
exchange.establishActiveLink('link-1', 'topology-updates', topology);

// Sync topology to link
exchange.syncTopologyToLink('link-1', topology);
```

| Method | Description |
|--------|-------------|
| `registerWebhook(name, url, events, options)` | Registers a webhook for external notifications. |
| `triggerWebhook(name, payload)` | Triggers a webhook with payload. |
| `establishActiveLink(linkId, webhookName, topology)` | Establishes an active link to external topology. |
| `syncTopologyToLink(linkId, topology)` | Syncs topology to an active link. |

| Event | Payload |
|-------|---------|
| `webhook_registered` | `{ name, url, events }` |
| `webhook_triggered` | `{ name, status }` |
| `webhook_failed` | `{ name, error }` |
| `active_link_established` | `{ linkId, webhookName, url }` |
| `topology_synced_to_link` | `{ linkId, syncCount }` |

## Supersampling Enhancer

Enhanced search parameters using supersampling techniques:

```javascript
// Configure supersampling
exchange.configureSupersampling({ sampleRate: 200, analysisWindow: 15, oversampleFactor: 8 });

// Add sample
exchange.addSupersample({ amplitude: 0.8, frequency: 2417, phase: 0.5, data: 'some query' });

// Get supersampled search parameters
const enhanced = exchange.getSupersampledSearchParameters('query');
```

| Method | Description |
|--------|-------------|
| `configureSupersampling(options)` | Configures supersampling parameters. |
| `addSupersample(sample)` | Adds a sample to the supersampling buffer. |
| `getSupersampledSearchParameters(query)` | Returns enhanced search parameters using supersampling. |
| `getSupersamplingResolution()` | Returns current supersampling resolution. |

| Event | Payload |
|-------|---------|
| `supersampling_configured` | `status object` |
| `search_parameters_supersampled` | `{ query, enhanced }` |

## Wave Function Synchronization

Synchronize wave functions between forward simulation and the exchange:

```javascript
// Sync wave functions with forward
exchange.syncWaveFunctionsWithForward();

// Get sync history
const history = exchange.getWaveSyncHistory();
```

| Method | Description |
|--------|-------------|
| `syncWaveFunctionsWithForward()` | Synchronizes wave functions with forward simulation. |
| `getWaveSyncHistory()` | Returns wave function sync history. |

| Event | Payload |
|-------|---------|
| `wave_functions_synced_with_forward` | `sync object` |

## Prosthetic Connector DLL

Models and agents can use a prosthetic connector link graph via an active-updating DLL:

```javascript
// Read the current DLL state (may be malformed - still functional)
const dll = exchange.readProstheticDLL();

// Write parameters to the DLL
exchange.writeProstheticDLLParameter('modelId', 'model-1');
exchange.writeProstheticDLLParameter('task', 'search');

// Write an execution map (model relays its execution plan)
const taskId = exchange.writeExecutionMap('model-1', {
    action: 'search',
    target: 'node_001',
    params: { depth: 3 }
});

// Update DLL with wave path connections
const connString = exchange.updateDLLWithWavePath('wave_path_123', 'seed_abc', 'ch-1');

// Divide attention spaces into attended/unattended
const division = exchange.divideAttentionSpaces();
// division.attended - spaces with high attention
// division.unattended - spaces with low attention

// Choose a space for task completion
const completion = exchange.chooseSpace('task', { priority: 'high', name: 'search' });
// completion.spaceType = 'attended' | 'unattended' | null
// completion.completed = boolean

// Get connection strings from wave paths
const consStrings = exchange.getConsStrings();

// Get active execution task
const activeTask = exchange.getActiveExecutionTask();
```

| Method | Description |
|--------|-------------|
| `readProstheticDLL()` | Reads the current DLL state. |
| `writeProstheticDLLParameter(key, value)` | Writes a parameter to the DLL. |
| `writeExecutionMap(modelId, executionMap)` | Writes an execution map from a model. |
| `updateDLLWithWavePath(wavePath, seed, channelId)` | Updates DLL with wave path connection. |
| `divideAttentionSpaces()` | Divides spaces into attended/unattended based on attention. |
| `chooseSpace(action, task)` | Chooses attended or unattended space for task completion. |
| `getConsStrings()` | Returns connection strings from wave paths. |
| `getActiveExecutionTask()` | Returns the current active execution task. |

| Event | Payload |
|-------|---------|
| `dll_parameter_written` | `{ key, value }` |
| `execution_map_written` | `{ taskId, modelId }` |
| `dll_updated_with_wave_path` | `{ connectionString, channelId }` |
| `attention_spaces_divided` | `division object` |
| `space_chosen` | `completion object` |

## Query Tracking and Layer Depth Stacking

The network tracks queries and extractions on each layer, maintaining a numerical imprint of activity. Depth stacking allows selection of higher layers when queries are favorable.

```javascript
// Record a query on a layer (must be done when data is extracted or copied)
exchange.recordLayerQuery('layer-1', { modelId: 'model-1', action: 'search' });

// Record an extraction from a layer
exchange.recordLayerExtraction('layer-1');

// Set depth for layer stacking
exchange.setLayerDepth('layer-1', 3);

// Set importance for dynamic cache sizing (0-1)
exchange.setLayerImportance('layer-1', 0.8);

// Get query count for a layer
const queryCount = exchange.getLayerQueryCount('layer-1');

// Get depth stack info for a layer
const depthStack = exchange.getLayerDepthStack('layer-1');
// { layerId, depth, importance, attentionZone, queryCount, extractionCount, maxCacheSize }

// Get dynamic max cache size for a layer
const maxCacheSize = exchange.getLayerMaxCacheSize('layer-1');

// Select layer by query favorability
const selected = exchange.selectLayerByDepth(0.7);
// Returns { layerId, score, depth, importance, attentionZone }

// Get density map of all layers (sorted by density)
const densityMap = exchange.getDensityMap();

// Get attention zones
const zones = exchange.getAttentionZones();
// { high: [...], medium: [...], low: [...], unattended: [...] }

// Get query tracking for a layer
const tracking = exchange.getQueryTracking('layer-1');
// { totalQueries, totalExtractions, depth, importance }

// Get all query tracking
const allTracking = exchange.getAllQueryTracking();
```

| Method | Description |
|--------|-------------|
| `recordLayerQuery(layerId, params)` | Records a query on a layer. |
| `recordLayerExtraction(layerId)` | Records an extraction from a layer. |
| `setLayerDepth(layerId, depth)` | Sets depth for layer stacking. |
| `setLayerImportance(layerId, importance)` | Sets importance (0-1) for dynamic cache sizing. |
| `getLayerQueryCount(layerId)` | Gets total query count for a layer. |
| `getLayerDepthStack(layerId)` | Gets depth stack info including max cache size. |
| `getLayerMaxCacheSize(layerId)` | Gets dynamic max cache size based on importance/activity. |
| `getDensityMap()` | Gets density mapping of all layers sorted by density. |
| `getAttentionZones()` | Gets layers grouped by attention zone (high/medium/low/unattended). |
| `getQueryTracking(layerId)` | Gets query tracking for a specific layer. |
| `getAllQueryTracking()` | Gets query tracking for all layers. |
| `selectLayerByDepth(queryFavorability)` | Selects best layer based on depth, importance, and favorability. |

| Event | Payload |
|-------|---------|
| `layer_query_recorded` | `{ layerId, queryCount, depth, attentionZone }` |
| `layer_extraction_recorded` | `{ layerId, extractionCount, depth, attentionZone }` |
| `layer_depth_set` | `{ layerId, depth, success }` |
| `layer_importance_set` | `{ layerId, importance, success }` |

### Dynamic Cache Sizing

Cache size is dynamically adjusted based on:
- Layer importance (0-1 multiplier)
- Query and extraction activity (1% increase per activity)
- Depth multiplier
- Attention zone (high = 2x, medium = 1.5x, low/unattended = 1x)

Maximum cache size is capped at 4x the base 32MB limit.

### Density Mapping

The density map creates a weighted representation of layer activity:
- Density = `min(1, activity/100) * importance * depth`
- Used to identify zones of high and low attention
- Interconnects between layers are weighted by density similarity

### Attention Zones

Layers are automatically classified into attention zones:
- **high**: >50 total activity (queries + extractions)
- **medium**: 11-50 total activity
- **low**: 1-10 total activity
- **unattended**: 0 activity

Models can use `selectLayerByDepth(favorability)` to choose between attended and unattended spaces based on query favorability.

## Permissions

Access to persistent space requires:

```javascript
exchange.setPermissionLevel(3);
if (exchange.secureAccess()) {
    // Access granted
}
```

## License

Integrated module of the unified-consciousness-render system.
