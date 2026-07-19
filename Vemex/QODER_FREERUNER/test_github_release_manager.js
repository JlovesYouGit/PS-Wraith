/**
 * Test script for GitHub Release Manager functionality
 */

const { Client } = require('@modelcontextprotocol/sdk');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk');
const path = require('path');

async function testGitHubReleaseManager() {
  console.log('🧪 Testing GitHub Release Manager functionality...\n');
  
  let client;
  let transport;
  
  try {
    // Create MCP client
    client = new Client({
      name: "GitHub Release Manager Test Client",
      version: "1.0.0"
    });
    
    // Connect to GitHub Release Manager server
    const serverPath = path.join(__dirname, 'SharedClientCache', 'individual_mcp_servers', 'github_release_manager.js');
    transport = new StdioClientTransport({
      command: "node",
      args: [serverPath]
    });
    
    await client.connect(transport);
    console.log('✅ Connected to GitHub Release Manager\n');
    
    // Test 1: List available tools
    console.log('Test 1: Listing available tools...');
    try {
      const tools = await client.request({method: "tools/list"});
      console.log('Available tools:');
      tools.tools.forEach(tool => {
        console.log(`  - ${tool.name}: ${tool.description}`);
      });
      console.log('✅ Test 1 passed\n');
    } catch (error) {
      console.log('❌ Test 1 failed:', error.message, '\n');
    }
    
    // Test 2: List releases (using a real repository)
    console.log('Test 2: Listing releases...');
    try {
      const result = await client.request({
        method: "tools/call",
        params: {
          name: "github_list_releases",
          arguments: {
            owner: "JlovesYouGit",
            repo: "test-repo"
          }
        }
      });
      console.log('Releases listing result:', JSON.stringify(result, null, 2));
      console.log('✅ Test 2 passed\n');
    } catch (error) {
      console.log('❌ Test 2 failed:', error.message, '\n');
    }
    
    // Test 3: Generate release notes
    console.log('Test 3: Generating release notes...');
    try {
      const result = await client.request({
        method: "tools/call",
        params: {
          name: "github_generate_release_notes",
          arguments: {
            owner: "JlovesYouGit",
            repo: "test-repo",
            tag_name: "v1.0.0"
          }
        }
      });
      console.log('Release notes generation result:', JSON.stringify(result, null, 2));
      console.log('✅ Test 3 passed\n');
    } catch (error) {
      console.log('❌ Test 3 failed:', error.message, '\n');
    }
    
    console.log('🎉 GitHub Release Manager tests completed!');
    
  } catch (error) {
    console.error('💥 GitHub Release Manager test failed:', error);
  } finally {
    if (transport) {
      await transport.close();
    }
  }
}

// Run the tests
testGitHubReleaseManager().catch(console.error);