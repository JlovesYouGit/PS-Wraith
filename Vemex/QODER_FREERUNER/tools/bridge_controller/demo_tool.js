/**
 * Demo tool showing how to use the MCP bridge controller
 * This tool demonstrates how Qoder can interact with the bridge to access individual MCP servers
 */

const fs = require('fs');
const path = require('path');

// Path to the bridge controller
const BRIDGE_CONTROLLER_PATH = 'C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools\\bridge_controller\\bridge_mcp_server.js';

/**
 * List all available MCP servers
 */
function listAvailableServers() {
  // In a real implementation, this would communicate with the bridge controller
  // For demo purposes, we'll just read the directory
  try {
    const serversDir = 'C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools\\individual_mcp_servers';
    const files = fs.readdirSync(serversDir);
    const servers = files
      .filter(file => file.endsWith('.json'))
      .map(file => path.basename(file, '.json'));
    
    console.log('Available MCP servers:');
    servers.forEach(server => console.log(`- ${server}`));
    return servers;
  } catch (error) {
    console.error('Error listing servers:', error.message);
    return [];
  }
}

/**
 * Load and use a specific MCP server
 */
function loadServer(serverName) {
  console.log(`Loading MCP server: ${serverName}`);
  // In a real implementation, this would send a message to the bridge controller
  // to dynamically load and start the specified server
  console.log(`Server ${serverName} would now be available for use through the bridge`);
}

// Demo usage
console.log('MCP Bridge Controller Demo');
console.log('========================');

const servers = listAvailableServers();
console.log();

if (servers.length > 0) {
  console.log('Loading first available server as demo:');
  loadServer(servers[0]);
}

console.log('\nIn Qoder, you would interact with the bridge controller through the MCP protocol.');
console.log('The bridge would dynamically load individual servers as needed.');