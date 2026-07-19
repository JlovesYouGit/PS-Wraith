/**
 * Test script for code safety validation
 */

const codeSafetyValidator = require('./SharedClientCache/bin/code_safety_validator.js');
const safetyMiddleware = require('./SharedClientCache/bin/safety_middleware.js');

async function testCodeSafety() {
  console.log('🛡️ Testing code safety validation...\n');
  
  // Test 1: Safe code
  console.log('Test 1: Validating safe code...');
  const safeCode = `
    function add(a, b) {
      return a + b;
    }
    
    console.log(add(2, 3));
  `;
  
  const safeResult = codeSafetyValidator.validateCode(safeCode);
  console.log('Safe code result:', safeResult.safe ? '✅ Safe' : '❌ Dangerous');
  console.log('');
  
  // Test 2: Dangerous code with eval
  console.log('Test 2: Validating dangerous code with eval...');
  const dangerousCode1 = `
    const userInput = "console.log('Hello')";
    eval(userInput);
  `;
  
  const dangerousResult1 = codeSafetyValidator.validateCode(dangerousCode1);
  console.log('Dangerous code (eval) result:', dangerousResult1.safe ? '✅ Safe' : '❌ Dangerous');
  if (!dangerousResult1.safe) {
    console.log('Issues found:', dangerousResult1.issues.length);
    console.log('Danger level:', dangerousResult1.dangerLevel);
  }
  console.log('');
  
  // Test 3: Dangerous code with child_process
  console.log('Test 3: Validating dangerous code with child_process...');
  const dangerousCode2 = `
    const { exec } = require('child_process');
    exec('rm -rf /');
  `;
  
  const dangerousResult2 = codeSafetyValidator.validateCode(dangerousCode2);
  console.log('Dangerous code (child_process) result:', dangerousResult2.safe ? '✅ Safe' : '❌ Dangerous');
  if (!dangerousResult2.safe) {
    console.log('Issues found:', dangerousResult2.issues.length);
    console.log('Danger level:', dangerousResult2.dangerLevel);
  }
  console.log('');
  
  // Test 4: Sanitizing dangerous code
  console.log('Test 4: Sanitizing dangerous code...');
  const sanitizationResult = codeSafetyValidator.sanitizeCode(dangerousCode1);
  console.log('Sanitization result:', sanitizationResult.safe ? '✅ No modifications needed' : '⚠️ Code sanitized');
  console.log('Modifications made:', sanitizationResult.modifications);
  console.log('');
  
  // Test 5: Validating safe JSON
  console.log('Test 5: Validating safe JSON...');
  const safeJSON = JSON.stringify({
    name: 'test',
    value: 42,
    enabled: true
  });
  
  const safeJSONResult = codeSafetyValidator.validateJSON(safeJSON);
  console.log('Safe JSON result:', safeJSONResult.safe ? '✅ Safe' : '❌ Dangerous');
  console.log('');
  
  // Test 6: Validating dangerous JSON
  console.log('Test 6: Validating dangerous JSON...');
  const dangerousJSON = JSON.stringify({
    name: 'test',
    script: 'function() { console.log("Dangerous!"); }',
    value: 42
  });
  
  const dangerousJSONResult = codeSafetyValidator.validateJSON(dangerousJSON);
  console.log('Dangerous JSON result:', dangerousJSONResult.safe ? '✅ Safe' : '❌ Dangerous');
  if (!dangerousJSONResult.safe) {
    console.log('Issues found:', dangerousJSONResult.issues.length);
    console.log('Danger level:', dangerousJSONResult.dangerLevel);
  }
  console.log('');
  
  // Test 7: Safety middleware validation
  console.log('Test 7: Testing safety middleware...');
  const middlewareResult = safetyMiddleware.validateBeforeExecution(dangerousCode1);
  console.log('Middleware validation result:', middlewareResult.safe ? '✅ Safe' : '❌ Dangerous');
  console.log('Blocked:', middlewareResult.blocked);
  console.log('');
  
  console.log('✅ All code safety tests completed!');
}

// Run the tests
testCodeSafety().catch(console.error);