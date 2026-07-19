/**
 * Setup script for MCP Bridge Controller Architecture
 * This script helps users set up the bridge controller architecture
 */

const fs = require('fs');
const path = require('path');

// Configuration
const TOOLS_DIR = 'C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools';
const BRIDGE_DIR = path.join(TOOLS_DIR, 'bridge_controller');
const SERVERS_DIR = path.join(TOOLS_DIR, 'individual_mcp_servers');

console.log('Setting up MCP Bridge Controller Architecture');
console.log('==========================================');

// Check if required directories exist
if (!fs.existsSync(TOOLS_DIR)) {
  console.error('Error: Tools directory not found');
  process.exit(1);
}

if (!fs.existsSync(BRIDGE_DIR)) {
  console.error('Error: Bridge controller directory not found');
  console.error('Please run this script from the correct location');
  process.exit(1);
}

if (!fs.existsSync(SERVERS_DIR)) {
  console.error('Error: Individual MCP servers directory not found');
  process.exit(1);
}

// Verify that individual server files exist
const serverFiles = fs.readdirSync(SERVERS_DIR);
if (serverFiles.length === 0) {
  console.error('Error: No individual MCP server configurations found');
  process.exit(1);
}

console.log(`Found ${serverFiles.length} individual MCP server configurations:`);
serverFiles.forEach(file => console.log(`  - ${file}`));

// Check if bridge configuration exists
const bridgeConfigPath = path.join(TOOLS_DIR, 'mcp.json');
if (!fs.existsSync(bridgeConfigPath)) {
  console.error('Warning: Bridge configuration not found');
  console.error('You need to create or move the mcp.json file to the tools directory');
} else {
  console.log('✓ Bridge configuration found');
}

console.log('\nSetup verification completed successfully!');
console.log('\nTo use this architecture:');
console.log('1. Make sure the mcp.json file in your Qoder configuration directory');
console.log('   points to the bridge controller');
console.log('2. Restart Qoder to load the new configuration');
console.log('3. The bridge controller will make all individual MCP servers available');

console.log('\nArchitecture is ready to use!');