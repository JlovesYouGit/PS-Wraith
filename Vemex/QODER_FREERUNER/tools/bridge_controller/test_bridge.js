/**
 * Test script for the MCP bridge controller
 * This script demonstrates how the bridge controller would handle communication
 */

const BridgeController = require('./bridge_controller');

// Create bridge controller instance
const controller = new BridgeController();

console.log('Testing MCP Bridge Controller');
console.log('============================');

// Test listing available servers
console.log('1. Listing available MCP servers:');
const availableServers = controller.getAvailableServers();
console.log(availableServers);

// Test loading a server
console.log('\n2. Loading github server:');
const githubConfig = controller.loadServer('github');
console.log('GitHub server config loaded:', !!githubConfig);

// Test loading another server
console.log('\n3. Loading web-search server:');
const webSearchConfig = controller.loadServer('web-search');
console.log('Web-search server config loaded:', !!webSearchConfig);

// Show all loaded servers
console.log('\n4. All loaded servers:');
const loadedServers = controller.getLoadedServers();
console.log(Object.keys(loadedServers));

console.log('\nTest completed successfully!');