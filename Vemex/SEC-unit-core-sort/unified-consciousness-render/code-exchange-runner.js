const ConsciousnessExchange = require('./consciousness-exchange');

const exchange = new ConsciousnessExchange({
    baseDir: __dirname,
    forwardDir: require('path').resolve(__dirname, '../forward'),
    fDumpDir: require('path').resolve(__dirname, '../F-dump'),
});

process.on('SIGINT', () => {
    console.log('\n[Exchange] Stopping consciousness exchange...');
    exchange.stop();
    process.exit(0);
});

process.on('SIGTERM', () => {
    exchange.stop();
    process.exit(0);
});

exchange.on('exchange_initialized', (data) => {
    console.log('[Exchange] Initialized with seed:', data.seed);
    console.log('[Exchange] Wave state:', data.waveState);
});

exchange.on('wave_state_changed', (state) => {
    console.log(`[Exchange] Wave state: ${state}`);
});

exchange.on('wave_locked', (data) => {
    console.log('[Exchange] Wave handshake locked');
});

exchange.on('wave_kill_detected', (data) => {
    console.log('[Exchange] Wave kill detected! Count:', data.killCount);
});

exchange.on('wave_reinstantiated', (data) => {
    console.log('[Exchange] Wave reinstantiated with new seed:', data.newSeed);
});

exchange.on('cache_allocated', (data) => {
    console.log(`[Exchange] Cache allocated for ${data.nodeId}: ${data.dumpFile} (${(data.size / 1024).toFixed(1)} KB)`);
});

exchange.on('seed_regenerated', (data) => {
    console.log(`[Exchange] Seed regenerated for ${data.nodeId}: ${data.seed}`);
});

exchange.on('topology_engraved', (data) => {
    console.log('[Exchange] Topology engraved:', data.path);
});

exchange.on('tree_recall', (data) => {
    console.log(`[Exchange] Tree recall for "${data.pattern}": ${data.commits.length} commits found`);
});

exchange.on('access_denied', (data) => {
    console.log('[Exchange] Access denied:', data.reason);
});

exchange.on('access_granted', () => {
    console.log('[Exchange] High priority access granted');
});

exchange.on('access_denied', (data) => {
    console.log('[Exchange] Access denied:', data.reason);
});

exchange.on('external_source_registered', (data) => {
    console.log('[Exchange] External source registered:', data.name);
});

exchange.on('external_commits_imported', (data) => {
    console.log(`[Exchange] Imported ${data.count} commits from ${data.source}`);
});

exchange.on('seed_markers_interconnected', (data) => {
    console.log(`[Exchange] Seed markers interconnected: ${data.internalCount} internal, ${data.externalCount} external, ${data.interconnectCount} links`);
});

exchange.on('cross_source_recall', (data) => {
    console.log(`[Exchange] Cross-source recall for "${data.pattern}": ${data.internal.length} internal, ${data.external.length} external`);
});

exchange.on('session_created', (data) => {
    console.log('[Exchange] Session created:', data.sessionId, 'for model:', data.modelId);
});

exchange.on('layer_lock_registered', (data) => {
    console.log('[Exchange] Layer lock registered:', data.layerId, 'threshold:', data.weightThreshold);
});

exchange.on('layer_access_granted', (data) => {
    console.log('[Exchange] Layer access granted:', data.layerId, 'score:', data.matchScore, 'dehashed:', data.dehashed ? 'yes' : 'no');
});

exchange.on('layer_access_denied', (data) => {
    console.log('[Exchange] Layer access denied:', data.layerId, 'score:', data.matchScore, 'retries:', data.retries);
});

exchange.on('cloud_pointer_navigated', (data) => {
    console.log('[Exchange] Cloud pointer navigated:', data.pointerId, 'orientation:', data.orientation, 'target:', data.target);
});

exchange.on('cloud_pointer_interaction', (data) => {
    console.log('[Exchange] Cloud pointer interaction:', data.pointerId, 'target:', data.target);
});

exchange.on('source_indentation_query', (data) => {
    console.log(`[Exchange] Source query "${data.source}" indentation ${data.indentation}: ${data.resultCount} results`);
});

exchange.on('data_interchanged', (data) => {
    console.log(`[Exchange] Data interchanged: ${data.from} -> ${data.to}`);
});

exchange.on('point_cloud_filled', (data) => {
    console.log('[Exchange] Point cloud filled for:', data.structure, 'points:', data.pointCount);
});

exchange.on('wave_simulation_started', (data) => {
    console.log('[Exchange] Wave simulation started:', data.type, 'id:', data.id);
});

exchange.on('wave_simulation_completed', (data) => {
    console.log('[Exchange] Wave simulation completed:', data.type, 'status:', data.status, 'signature:', data.result?.signature ? 'yes' : 'no');
});

exchange.on('wave_parameters_updated', (params) => {
    console.log('[Exchange] Wave parameters updated:', Object.keys(params).length, 'parameters');
});

exchange.on('search_parameters_enhanced', (data) => {
    console.log('[Exchange] Search parameters enhanced for:', data.query, 'amplitude boost:', data.enhanced.amplitudeBoost?.toFixed(2));
});

exchange.on('wave_functions_synchronized', (data) => {
    console.log('[Exchange] Wave functions synchronized');
});

exchange.on('local_channel_created', (data) => {
    console.log('[Exchange] Local channel created:', data.channelId, 'node:', data.nodeId);
});

exchange.on('external_channel_created', (data) => {
    console.log('[Exchange] External channel created:', data.channelId, 'webhook:', data.webhookUrl);
});

exchange.on('channel_activated', (data) => {
    console.log('[Exchange] Channel activated:', data.channelId);
});

exchange.on('webhook_registered', (data) => {
    console.log('[Exchange] Webhook registered:', data.name, 'url:', data.url);
});

exchange.on('webhook_triggered', (data) => {
    console.log('[Exchange] Webhook triggered:', data.name, 'status:', data.status);
});

exchange.on('webhook_failed', (data) => {
    console.log('[Exchange] Webhook failed:', data.name, 'error:', data.error);
});

exchange.on('active_link_established', (data) => {
    console.log('[Exchange] Active link established:', data.linkId, 'webhook:', data.webhookName);
});

exchange.on('topology_synced_to_link', (data) => {
    console.log('[Exchange] Topology synced to link:', data.linkId, 'sync count:', data.syncCount);
});

exchange.on('supersampling_configured', (data) => {
    console.log('[Exchange] Supersampling configured:', 'resolution:', data.resolution?.toFixed(1));
});

exchange.on('search_parameters_supersampled', (data) => {
    console.log('[Exchange] Search parameters supersampled for:', data.query, 'confidence:', data.enhanced.confidence?.toFixed(2));
});

exchange.on('wave_functions_synced_with_forward', (data) => {
    console.log('[Exchange] Wave functions synced with forward:', data.timestamp);
});

exchange.on('layer_query_recorded', (data) => {
    console.log('[Exchange] Layer query recorded:', data.layerId, 'count:', data.queryCount, 'zone:', data.attentionZone);
});

exchange.on('layer_extraction_recorded', (data) => {
    console.log('[Exchange] Layer extraction recorded:', data.layerId, 'count:', data.extractionCount, 'zone:', data.attentionZone);
});

exchange.on('layer_depth_set', (data) => {
    console.log('[Exchange] Layer depth set:', data.layerId, 'depth:', data.depth);
});

exchange.on('layer_importance_set', (data) => {
    console.log('[Exchange] Layer importance set:', data.layerId, 'importance:', data.importance);
});

exchange.on('cache_swapped', (data) => {
    console.log('[Exchange] Cache swapped:', data.nodeId, 'from:', data.swappedFrom, 'freed:', (data.freed / 1024).toFixed(1), 'KB');
});

exchange.on('cache_auto_allocated', (data) => {
    console.log('[Exchange] Cache auto-allocated:', data.sourceLayerId, '->', data.targetLayerId, 'portion:', (data.portionSize / 1024).toFixed(1), 'KB');
});

exchange.on('cache_swapped_between_layers', (data) => {
    console.log('[Exchange] Cache swapped between layers:', data.sourceLayerId, '->', data.targetLayerId, 'portion:', (data.portionSize / 1024).toFixed(1), 'KB');
});

exchange.on('error', (err) => {
    console.error('[Exchange] Error:', err);
});

if (require.main === module) {
    exchange.start();
    console.log('[Exchange] Consciousness Exchange started');
    console.log('[Exchange] Press Ctrl+C to stop');
}

module.exports = { ConsciousnessExchange, exchange };
