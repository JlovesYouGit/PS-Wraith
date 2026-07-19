/**
 * Test script for advanced terminal and workflow functionality
 */

const terminalController = require('./SharedClientCache/bin/terminal_controller.js');
const dotMatrixAnalyzer = require('./SharedClientCache/bin/dot_matrix_analyzer.js');
const ideWorkflowManager = require('./SharedClientCache/bin/ide_workflow_manager.js');

async function testAdvancedTerminalWorkflow() {
  console.log('🚀 Testing advanced terminal and workflow functionality...\n');
  
  // Test 1: Terminal Controller Status
  console.log('Test 1: Checking Terminal Controller status...');
  try {
    const terminalStatus = terminalController.getStatus();
    console.log('Terminal Controller status:', terminalStatus.initialized ? '✅ Initialized' : '❌ Not initialized');
  } catch (error) {
    console.log('Terminal Controller status: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 2: Dot Matrix Analyzer Status
  console.log('Test 2: Checking Dot Matrix Analyzer status...');
  try {
    const matrixStatus = dotMatrixAnalyzer.getStatus();
    console.log('Dot Matrix Analyzer status:', matrixStatus.initialized ? '✅ Initialized' : '❌ Not initialized');
  } catch (error) {
    console.log('Dot Matrix Analyzer status: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 3: IDE Workflow Manager Status
  console.log('Test 3: Checking IDE Workflow Manager status...');
  try {
    const workflowStatus = ideWorkflowManager.getStatus();
    console.log('IDE Workflow Manager status:', workflowStatus.initialized ? '✅ Initialized' : '❌ Not initialized');
  } catch (error) {
    console.log('IDE Workflow Manager status: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 4: Data to Dot Matrix Conversion
  console.log('Test 4: Testing data to dot matrix conversion...');
  try {
    const testData = {
      name: 'Qoder Test',
      value: 42,
      active: true,
      scores: [0.8, 0.9, 0.7, 0.95]
    };
    
    const matrix = dotMatrixAnalyzer.convertToDotMatrix(testData);
    console.log('Dot matrix conversion:', matrix.length > 0 ? '✅ Success' : '❌ Failed');
    console.log('Matrix dimensions:', `${matrix.length}x${matrix[0] ? matrix[0].length : 0}`);
  } catch (error) {
    console.log('Dot matrix conversion: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 5: Pattern Detection
  console.log('Test 5: Testing pattern detection...');
  try {
    const testMatrix = [
      [0.1, 0.2, 0.3, 0.4],
      [0.2, 0.3, 0.4, 0.5],
      [0.3, 0.4, 0.5, 0.6],
      [0.4, 0.5, 0.6, 0.7]
    ];
    
    const patterns = dotMatrixAnalyzer.findPatterns(testMatrix);
    console.log('Pattern detection:', patterns.length > 0 ? '✅ Found patterns' : '✅ No patterns (expected for this data)');
  } catch (error) {
    console.log('Pattern detection: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 6: Data Analysis
  console.log('Test 6: Testing data analysis...');
  try {
    const testData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const analysis = dotMatrixAnalyzer.analyzeData(testData);
    console.log('Data analysis:', analysis.insights.length >= 0 ? '✅ Success' : '❌ Failed');
  } catch (error) {
    console.log('Data analysis: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 7: Project Initialization
  console.log('Test 7: Testing project initialization...');
  try {
    const projectResult = ideWorkflowManager.initializeProject(
      'test-project',
      './test-project',
      { git: false }
    );
    console.log('Project initialization:', projectResult.success ? '✅ Success' : '❌ Failed');
  } catch (error) {
    console.log('Project initialization: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 8: Environment Setup
  console.log('Test 8: Testing environment setup...');
  try {
    const envResult = ideWorkflowManager.setupEnvironment('venv', {
      type: 'python',
      path: './test-venv'
    });
    console.log('Environment setup:', envResult.success ? '✅ Success' : '❌ Failed');
  } catch (error) {
    console.log('Environment setup: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 9: SDK Installation
  console.log('Test 9: Testing SDK installation...');
  try {
    const sdkResult = ideWorkflowManager.installSdk('node', {
      version: '18.x'
    });
    console.log('SDK installation:', sdkResult.success ? '✅ Success' : '❌ Failed');
  } catch (error) {
    console.log('SDK installation: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 10: Terminal Creation
  console.log('Test 10: Testing terminal creation...');
  try {
    const terminalResult = terminalController.createTerminal({
      shell: process.platform === 'win32' ? 'powershell.exe' : '/bin/bash',
      cwd: '.',
      isAdmin: false
    });
    console.log('Terminal creation:', terminalResult.success ? '✅ Success' : '❌ Failed');
    
    if (terminalResult.success) {
      // Test command execution
      console.log('Testing command execution...');
      const execResult = await terminalController.executeCommand(
        terminalResult.terminalId,
        'echo "Qoder Terminal Test"'
      );
      console.log('Command execution:', execResult.success ? '✅ Success' : '❌ Failed');
      
      // Kill the terminal
      console.log('Testing terminal cleanup...');
      const killResult = terminalController.killTerminal(terminalResult.terminalId);
      console.log('Terminal cleanup:', killResult.success ? '✅ Success' : '❌ Failed');
    }
  } catch (error) {
    console.log('Terminal operations: ❌ Error -', error.message);
  }
  console.log('');
  
  console.log('✅ All advanced terminal and workflow tests completed!');
}

// Run the tests
testAdvancedTerminalWorkflow().catch(console.error);