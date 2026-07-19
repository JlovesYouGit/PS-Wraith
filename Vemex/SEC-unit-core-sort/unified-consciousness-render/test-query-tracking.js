const ConsciousnessExchange = require('./consciousness-exchange');

async function test() {
    try {
        const ex = new ConsciousnessExchange({ baseDir: __dirname });

        await ex.initialize();
        console.log('INIT OK');

        // Register layer with depth and importance
        ex.registerLayerLock('layer-1', 'seed-1', 0.6, 'pattern-1', { depth: 2, importance: 0.8 });
        ex.registerLayerLock('layer-2', 'seed-2', 0.7, 'pattern-2', { depth: 1, importance: 0.3 });
        ex.registerLayerLock('layer-3', 'seed-3', 0.5, 'pattern-3', { depth: 3, importance: 0.5 });

        // Record queries and extractions
        for (let i = 0; i < 60; i++) {
            ex.recordLayerQuery('layer-1');
            if (i % 5 === 0) ex.recordLayerExtraction('layer-1');
        }
        for (let i = 0; i < 10; i++) {
            ex.recordLayerQuery('layer-2');
        }
        for (let i = 0; i < 25; i++) {
            ex.recordLayerQuery('layer-3');
            if (i % 3 === 0) ex.recordLayerExtraction('layer-3');
        }

        // Test depth and importance setting
        ex.setLayerDepth('layer-2', 4);
        ex.setLayerImportance('layer-2', 0.9);

        // Get query counts
        console.log('Layer-1 queries:', ex.getLayerQueryCount('layer-1'));
        console.log('Layer-2 queries:', ex.getLayerQueryCount('layer-2'));
        console.log('Layer-3 queries:', ex.getLayerQueryCount('layer-3'));

        // Get depth stacks
        console.log('Layer-1 depth stack:', ex.getLayerDepthStack('layer-1'));
        console.log('Layer-2 depth stack:', ex.getLayerDepthStack('layer-2'));

        // Get max cache sizes
        console.log('Layer-1 max cache:', (ex.getLayerMaxCacheSize('layer-1') / 1024 / 1024).toFixed(1), 'MB');
        console.log('Layer-2 max cache:', (ex.getLayerMaxCacheSize('layer-2') / 1024 / 1024).toFixed(1), 'MB');

        // Get density map
        const densityMap = ex.getDensityMap();
        console.log('Density map:', densityMap.map(d => ({ layerId: d.layerId, density: d.density.toFixed(2), zone: d.attentionZone })));

        // Get attention zones
        const zones = ex.getAttentionZones();
        console.log('Attention zones:', { high: zones.high.length, medium: zones.medium.length, low: zones.low.length, unattended: zones.unattended.length });

        // Select layer by depth
        const selected = ex.selectLayerByDepth(0.7);
        console.log('Selected layer:', selected?.layerId, 'score:', selected?.score?.toFixed(2));

        // Get all query tracking
        const allTracking = ex.getAllQueryTracking();
        console.log('All tracking:', allTracking.length, 'layers');

        // Get status
        const status = ex.getStatus();
        console.log('Query tracking:', status.queryTracking);
        console.log('Density map entries:', status.densityMap.length);
        console.log('Attention zones:', Object.keys(status.attentionZones));

        process.exit(0);
    } catch (e) {
        console.error('FAIL:', e);
        process.exit(1);
    }
}

test();
