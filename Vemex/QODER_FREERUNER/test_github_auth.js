/**
 * Test script for GitHub authentication setup
 */

const githubAuthManager = require('./SharedClientCache/bin/github_auth_manager.js');

async function testGitHubAuth() {
  console.log('🧪 Testing GitHub authentication setup...\n');
  
  // Test 1: Initialize GitHub Auth Manager
  console.log('Test 1: Initializing GitHub Auth Manager...');
  try {
    const result = await githubAuthManager.initialize();
    console.log('Initialization result:', result);
    console.log('✅ Test 1 passed\n');
  } catch (error) {
    console.log('❌ Test 1 failed:', error.message, '\n');
  }
  
  // Test 2: Get token
  console.log('Test 2: Getting GitHub token...');
  try {
    const token = githubAuthManager.getToken();
    console.log('Token available:', !!token);
    if (token) {
      console.log('Token length:', token.length);
      console.log('Token starts with:', token.substring(0, 10) + '...');
    }
    console.log('✅ Test 2 passed\n');
  } catch (error) {
    console.log('❌ Test 2 failed:', error.message, '\n');
  }
  
  // Test 3: Get status
  console.log('Test 3: Getting GitHub auth status...');
  try {
    const status = githubAuthManager.getStatus();
    console.log('Status:', JSON.stringify(status, null, 2));
    console.log('✅ Test 3 passed\n');
  } catch (error) {
    console.log('❌ Test 3 failed:', error.message, '\n');
  }
  
  // Test 4: Check permissions
  console.log('Test 4: Checking GitHub permissions...');
  try {
    const hasRepoRead = githubAuthManager.hasPermission('repos', 'read');
    const hasIssueWrite = githubAuthManager.hasPermission('issues', 'write');
    console.log('Has repo read permission:', hasRepoRead);
    console.log('Has issue write permission:', hasIssueWrite);
    console.log('✅ Test 4 passed\n');
  } catch (error) {
    console.log('❌ Test 4 failed:', error.message, '\n');
  }
  
  // Test 5: Get MCP configuration
  console.log('Test 5: Getting MCP configuration...');
  try {
    const config = githubAuthManager.getMCPConfig();
    console.log('MCP config available:', !!config);
    if (config) {
      console.log('Config command:', config.command);
      console.log('Config args count:', config.args.length);
      console.log('Environment variables:', Object.keys(config.env).length);
    }
    console.log('✅ Test 5 passed\n');
  } catch (error) {
    console.log('❌ Test 5 failed:', error.message, '\n');
  }
  
  // Test 6: Audit token usage
  console.log('Test 6: Auditing token usage...');
  try {
    githubAuthManager.auditTokenUsage('test_action', { test: 'data' });
    console.log('Audit logged successfully');
    console.log('✅ Test 6 passed\n');
  } catch (error) {
    console.log('❌ Test 6 failed:', error.message, '\n');
  }
  
  console.log('🎉 All GitHub authentication tests completed!');
}

// Run the tests
testGitHubAuth().catch(console.error);