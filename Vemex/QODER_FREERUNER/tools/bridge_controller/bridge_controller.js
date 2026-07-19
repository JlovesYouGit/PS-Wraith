const fs = require('fs');
const path = require('path');

// Directory where individual MCP server configurations are stored
const MCP_SERVERS_DIR = path.join(__dirname, '..', 'individual_mcp_servers');

class BridgeController {
  constructor() {
    this.loadedServers = new Map();
  }

  /**
   * Get list of available MCP servers
   */
  getAvailableServers() {
    try {
      const files = fs.readdirSync(MCP_SERVERS_DIR);
      return files
        .filter(file => file.endsWith('.json'))
        .map(file => path.basename(file, '.json'));
    } catch (error) {
      console.error('Error reading MCP servers directory:', error);
      return [];
    }
  }

  /**
   * Load a specific MCP server configuration
   */
  loadServer(serverName) {
    if (this.loadedServers.has(serverName)) {
      return this.loadedServers.get(serverName);
    }

    try {
      const configPath = path.join(MCP_SERVERS_DIR, `${serverName}.json`);
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      this.loadedServers.set(serverName, config);
      return config;
    } catch (error) {
      console.error(`Error loading server ${serverName}:`, error);
      return null;
    }
  }

  /**
   * Get all loaded servers
   */
  getLoadedServers() {
    return Array.from(this.loadedServers.entries()).reduce((acc, [name, config]) => {
      acc[name] = config;
      return acc;
    }, {});
  }
}

module.exports = BridgeController;