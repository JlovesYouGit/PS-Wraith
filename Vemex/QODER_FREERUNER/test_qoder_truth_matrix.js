/**
 * Test script for Qoder Truth Matrix functionality
 */

const qoderTruthMatrix = require('./SharedClientCache/bin/qoder_truth_matrix.js');

async function testQoderTruthMatrix() {
  console.log('🔮 Testing Qoder Truth Matrix functionality...\n');
  
  // Test 1: Process terminal warning
  console.log('Test 1: Processing terminal warning...');
  try {
    const warning = "Error: Cannot find module 'express' or its corresponding type declarations.";
    const context = {
      terminalType: 'powershell',
      platform: 'windows'
    };
    
    const result = qoderTruthMatrix.processTerminalWarning(warning, context);
    
    console.log('Warning processing result:');
    console.log('- Warning:', result.warning);
    console.log('- Pattern type:', result.analysis.patternType);
    console.log('- Indicates impossibility:', result.analysis.indicatesImpossibility);
    console.log('- Certainty tokens generated:', result.tokens.length);
    console.log('- Solution provided:', result.solution ? 'Yes' : 'No');
    if (result.solution) {
      console.log('- Solution action:', result.solution.action);
      console.log('- Solution certainty:', result.solution.certainty.toFixed(2));
    }
    console.log('✅ Test 1 passed\n');
  } catch (error) {
    console.log('❌ Test 1 failed:', error.message, '\n');
  }
  
  // Test 2: Process permission denied warning
  console.log('Test 2: Processing permission denied warning...');
  try {
    const warning = "Permission denied: Unable to write to file C:\\Program Files\\MyApp\\config.json";
    const context = {
      terminalType: 'cmd',
      platform: 'windows'
    };
    
    const result = qoderTruthMatrix.processTerminalWarning(warning, context);
    
    console.log('Warning processing result:');
    console.log('- Warning:', result.warning);
    console.log('- Pattern type:', result.analysis.patternType);
    console.log('- Indicates impossibility:', result.analysis.indicatesImpossibility);
    console.log('- Certainty tokens generated:', result.tokens.length);
    console.log('- Solution provided:', result.solution ? 'Yes' : 'No');
    if (result.solution) {
      console.log('- Solution action:', result.solution.action);
      console.log('- Solution certainty:', result.solution.certainty.toFixed(2));
    }
    console.log('✅ Test 2 passed\n');
  } catch (error) {
    console.log('❌ Test 2 failed:', error.message, '\n');
  }
  
  // Test 3: Process version mismatch warning
  console.log('Test 3: Processing version mismatch warning...');
  try {
    const warning = "Error: Package @types/node@14.18.36 is not compatible with typescript@5.0.0";
    const context = {
      terminalType: 'bash',
      platform: 'linux'
    };
    
    const result = qoderTruthMatrix.processTerminalWarning(warning, context);
    
    console.log('Warning processing result:');
    console.log('- Warning:', result.warning);
    console.log('- Pattern type:', result.analysis.patternType);
    console.log('- Indicates impossibility:', result.analysis.indicatesImpossibility);
    console.log('- Certainty tokens generated:', result.tokens.length);
    console.log('- Solution provided:', result.solution ? 'Yes' : 'No');
    if (result.solution) {
      console.log('- Solution action:', result.solution.action);
      console.log('- Solution certainty:', result.solution.certainty.toFixed(2));
    }
    console.log('✅ Test 3 passed\n');
  } catch (error) {
    console.log('❌ Test 3 failed:', error.message, '\n');
  }
  
  // Test 4: Process complex impossibility warning
  console.log('Test 4: Processing complex impossibility warning...');
  try {
    const warning = "FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory";
    const context = {
      terminalType: 'wsl',
      platform: 'linux'
    };
    
    const result = qoderTruthMatrix.processTerminalWarning(warning, context);
    
    console.log('Warning processing result:');
    console.log('- Warning:', result.warning);
    console.log('- Pattern type:', result.analysis.patternType);
    console.log('- Indicates impossibility:', result.analysis.indicatesImpossibility);
    console.log('- Certainty tokens generated:', result.tokens.length);
    console.log('- Solution provided:', result.solution ? 'Yes' : 'No');
    if (result.solution) {
      console.log('- Solution action:', result.solution.action);
      console.log('- Solution certainty:', result.solution.certainty.toFixed(2));
      console.log('- Solution type:', result.solution.type);
    }
    console.log('✅ Test 4 passed\n');
  } catch (error) {
    console.log('❌ Test 4 failed:', error.message, '\n');
  }
  
  // Test 5: Get status
  console.log('Test 5: Getting truth matrix status...');
  try {
    const status = qoderTruthMatrix.getStatus();
    
    console.log('Truth matrix status:');
    console.log('- Initialized:', status.initialized);
    console.log('- Patterns:', status.patterns);
    console.log('- Tokens:', status.tokens);
    console.log('- History:', status.history);
    console.log('- Certainty threshold:', status.certaintyThreshold);
    console.log('✅ Test 5 passed\n');
  } catch (error) {
    console.log('❌ Test 5 failed:', error.message, '\n');
  }
  
  // Test 6: Set certainty threshold
  console.log('Test 6: Setting certainty threshold...');
  try {
    qoderTruthMatrix.setCertaintyThreshold(0.9);
    
    const status = qoderTruthMatrix.getStatus();
    console.log('Certainty threshold set to:', status.certaintyThreshold);
    console.log('✅ Test 6 passed\n');
  } catch (error) {
    console.log('❌ Test 6 failed:', error.message, '\n');
  }
  
  // Test 7: Learn from solution
  console.log('Test 7: Learning from solution...');
  try {
    const warning = "Error: Cannot find module 'lodash'";
    const solution = {
      action: 'install_package',
      certainty: 0.95
    };
    
    qoderTruthMatrix.learnFromSolution(warning, solution, true);
    
    console.log('Learned from successful solution');
    console.log('✅ Test 7 passed\n');
  } catch (error) {
    console.log('❌ Test 7 failed:', error.message, '\n');
  }
  
  console.log('✅ All Qoder Truth Matrix tests completed!');
}

// Run the tests
testQoderTruthMatrix().catch(console.error);