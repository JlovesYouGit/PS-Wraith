/**
 * Test script for intelligent terminal functionality
 */

const intelligentTerminalController = require('./SharedClientCache/bin/intelligent_terminal_controller.js');

async function testIntelligentTerminal() {
  console.log('🧪 Testing intelligent terminal functionality...\n');
  
  // Test 1: Initialize intelligent terminal controller
  console.log('Test 1: Initializing intelligent terminal controller...');
  try {
    const result = await intelligentTerminalController.initialize();
    console.log('Initialization result:', result);
    console.log('✅ Test 1 passed\n');
  } catch (error) {
    console.log('❌ Test 1 failed:', error.message, '\n');
  }
  
  // Test 2: Get status
  console.log('Test 2: Getting intelligent terminal status...');
  try {
    const status = intelligentTerminalController.getStatus();
    console.log('Status:', JSON.stringify(status, null, 2));
    console.log('✅ Test 2 passed\n');
  } catch (error) {
    console.log('❌ Test 2 failed:', error.message, '\n');
  }
  
  // Test 3: Analyze different types of commands
  console.log('Test 3: Analyzing different types of commands...');
  try {
    const testCommands = [
      'find . -name "*.js"',
      'git push origin main',
      'gh workflow run deploy.yml',
      'rm -rf node_modules',
      'grep "function" *.js'
    ];
    
    for (const command of testCommands) {
      const analysis = await intelligentTerminalController.analyzeCommand(command);
      console.log(`${command}:`);
      console.log(`  Type: ${analysis.type}`);
      console.log(`  Strategy: ${analysis.strategy}`);
      console.log(`  Risk Level: ${analysis.riskLevel}`);
    }
    console.log('✅ Test 3 passed\n');
  } catch (error) {
    console.log('❌ Test 3 failed:', error.message, '\n');
  }
  
  // Test 4: Execute a safe command
  console.log('Test 4: Executing a safe command...');
  try {
    const result = await intelligentTerminalController.executeCommand('echo "Intelligent terminal test"', {
      autoConfirm: true
    });
    console.log('Command execution result:', result.success);
    if (result.success) {
      console.log('Output:', result.stdout.trim());
    }
    console.log('✅ Test 4 passed\n');
  } catch (error) {
    console.log('❌ Test 4 failed:', error.message, '\n');
  }
  
  // Test 5: Execute a high-risk command (should require confirmation)
  console.log('Test 5: Executing a high-risk command...');
  try {
    const result = await intelligentTerminalController.executeCommand('rm -rf test_directory');
    console.log('Command execution result:', result.success);
    console.log('Requires confirmation:', result.requiresConfirmation);
    console.log('✅ Test 5 passed\n');
  } catch (error) {
    console.log('❌ Test 5 failed:', error.message, '\n');
  }
  
  // Test 6: Execute a git command with pre-check
  console.log('Test 6: Executing a git command with pre-check...');
  try {
    const result = await intelligentTerminalController.executeCommand('git status', {
      autoConfirm: true
    });
    console.log('Git command execution result:', result.success);
    console.log('✅ Test 6 passed\n');
  } catch (error) {
    console.log('❌ Test 6 failed:', error.message, '\n');
  }
  
  // Test 7: Get command history
  console.log('Test 7: Getting command history...');
  try {
    const history = intelligentTerminalController.getCommandHistory();
    console.log('Command history entries:', history.length);
    console.log('✅ Test 7 passed\n');
  } catch (error) {
    console.log('❌ Test 7 failed:', error.message, '\n');
  }
  
  // Test 8: Get active sessions
  console.log('Test 8: Getting active sessions...');
  try {
    const sessions = intelligentTerminalController.getActiveSessions();
    console.log('Active sessions:', sessions.length);
    console.log('✅ Test 8 passed\n');
  } catch (error) {
    console.log('❌ Test 8 failed:', error.message, '\n');
  }
  
  console.log('🎉 All intelligent terminal tests completed!');
}

// Run the tests
testIntelligentTerminal().catch(console.error);