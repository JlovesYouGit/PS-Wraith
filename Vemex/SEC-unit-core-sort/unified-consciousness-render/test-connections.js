/**
 * Test script for consciousness core connections
 */

const ConsciousnessCore = require('./consciousness-core');

async function testConnections() {
    console.log('[TEST] Starting consciousness core connection test...');
    
    const core = new ConsciousnessCore();
    
    // Listen for key events
    core.on('initialized', (data) => {
        console.log('[TEST] Consciousness core initialized:', data);
    });
    
    core.on('consciousness_flow_update', (data) => {
        console.log('[TEST] Consciousness flow update:', {
            consciousness_level: data.consciousness_level,
            color_density: data.color_density
        });
    });
    
    core.on('geometric_data_connectors_update', (data) => {
        console.log('[TEST] Geometric data connectors:', {
            connector_integrity: data.connector_integrity,
            active_connectors: data.active_connectors
        });
    });
    
    core.on('zero_brain_mathematical_tracking_update', (data) => {
        console.log('[TEST] Zero brain mathematical tracking:', {
            tracking_accuracy: data.tracking_accuracy,
            pattern_recognition: data.pattern_recognition,
            mathematical_consistency: data.mathematical_consistency
        });
    });
    
    core.on('packet_flow_adjuster_update', (data) => {
        console.log('[TEST] Packet flow adjuster:', {
            flow_rate: data.flow_rate,
            flow_direction: data.flow_direction,
            flow_optimization: data.flow_optimization
        });
    });
    
    core.on('magi_zone_intent_override_update', (data) => {
        console.log('[TEST] Magi zone intent override:', {
            intent_alignment: data.intent_alignment,
            override_active: data.override_active,
            executing_commands: data.executing_commands
        });
    });
    
    core.on('unique_seed_generation_update', (data) => {
        console.log('[TEST] Unique seed generation:', {
            seed_uniqueness: data.seed_uniqueness,
            trace_integrity: data.trace_integrity,
            imagination_seeds: data.imagination_seeds
        });
    });
    
    try {
        await core.initialize();
        console.log('[TEST] Core initialization successful');
        
        // Run for 10 seconds to see events
        setTimeout(() => {
            console.log('[TEST] Test complete - stopping...');
            process.exit(0);
        }, 10000);
        
    } catch (error) {
        console.error('[TEST] Error during initialization:', error);
        process.exit(1);
    }
}

testConnections();
