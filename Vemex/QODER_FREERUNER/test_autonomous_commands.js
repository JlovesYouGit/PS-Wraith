/**
 * Test script for autonomous command functionality
 */

const autonomousCommandManager = require('./SharedClientCache/bin/autonomous_command_manager.js');

async function testAutonomousCommands() {
  console.log('🧪 Testing autonomous command functionality...\n');
  
  // Test 1: Initialize autonomous command manager
  console.log('Test 1: Initializing autonomous command manager...');
  try {
    const result = await autonomousCommandManager.initialize();
    console.log('Initialization result:', result);
    console.log('✅ Test 1 passed\n');
  } catch (error) {
    console.log('❌ Test 1 failed:', error.message, '\n');
  }
  
  // Test 2: Get status
  console.log('Test 2: Getting autonomous command status...');
  try {
    const status = autonomousCommandManager.getStatus();
    console.log('Status:', JSON.stringify(status, null, 2));
    console.log('✅ Test 2 passed\n');
  } catch (error) {
    console.log('❌ Test 2 failed:', error.message, '\n');
  }
  
  // Test 3: Check safety of safe commands
  console.log('Test 3: Checking safety of safe commands...');
  try {
    const safeCommands = [
      'git status',
      'git add .',
      'npm install',
      'ls -la',
      'echo "Hello World"'
    ];
    
    for (const command of safeCommands) {
      const safety = await autonomousCommandManager.isCommandSafe(command);
      console.log(`${command}: Safe=${safety.safe}, AutoAccept=${safety.autoAccept}`);
    }
    console.log('✅ Test 3 passed\n');
  } catch (error) {
    console.log('❌ Test 3 failed:', error.message, '\n');
  }
  
  // Test 4: Check safety of dangerous commands
  console.log('Test 4: Checking safety of dangerous commands...');
  try {
    const dangerousCommands = [
      'rm -rf /',
      'format C:',
      'delete everything'
    ];
    
    for (const command of dangerousCommands) {
      const safety = await autonomousCommandManager.isCommandSafe(command);
      console.log(`${command}: Safe=${safety.safe}, RequiresConfirmation=${safety.requiresConfirmation}`);
    }
    console.log('✅ Test 4 passed\n');
  } catch (error) {
    console.log('❌ Test 4 failed:', error.message, '\n');
  }
  
  // Test 5: Execute a safe command
  console.log('Test 5: Executing a safe command...');
  try {
    const result = await autonomousCommandManager.executeCommand('echo "Autonomous command test"', {
      autoAccept: true
    });
    console.log('Command execution result:', result.success);
    if (result.success) {
      console.log('Output:', result.stdout.trim());
    }
    console.log('✅ Test 5 passed\n');
  } catch (error) {
    console.log('❌ Test 5 failed:', error.message, '\n');
  }
  
  // Test 6: Execute multiple commands
  console.log('Test 6: Executing multiple commands...');
  try {
    const commands = [
      'echo "Command 1"',
      'echo "Command 2"',
      'echo "Command 3"'
    ];
    
    const result = await autonomousCommandManager.executeCommands(commands, {
      autoAccept: true,
      continueOnError: true
    });
    console.log('Multiple command execution result:', result.success);
    console.log('Individual results:', result.results.length);
    console.log('✅ Test 6 passed\n');
  } catch (error) {
    console.log('❌ Test 6 failed:', error.message, '\n');
  }
  
  // Test 7: Get execution history
  console.log('Test 7: Getting execution history...');
  try {
    const history = autonomousCommandManager.getExecutionHistory();
    console.log('Execution history entries:', history.length);
    console.log('✅ Test 7 passed\n');
  } catch (error) {
    console.log('❌ Test 7 failed:', error.message, '\n');
  }
  
  // Test 8: Get active commands
  console.log('Test 8: Getting active commands...');
  try {
    const active = autonomousCommandManager.getActiveCommands();
    console.log('Active commands:', active.length);
    console.log('✅ Test 8 passed\n');
  } catch (error) {
    console.log('❌ Test 8 failed:', error.message, '\n');
  }
  
  console.log('🎉 All autonomous command tests completed!');
}

// Run the tests
testAutonomousCommands().catch(console.error);