/**
 * Migration helper script to convert existing MCP configuration
 * to the bridge controller architecture
 */

const fs = require('fs');
const path = require('path');

// Path to the original configuration
const ORIGINAL_CONFIG_PATH = process.argv[2] || 'original_mcp.json';
// Path to the individual servers directory
const SERVERS_DIR = 'C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools\\individual_mcp_servers';

/**
 * Migrate the original configuration to individual server files
 */
function migrateConfiguration() {
  try {
    // Read the original configuration
    const originalConfig = JSON.parse(fs.readFileSync(ORIGINAL_CONFIG_PATH, 'utf8'));
    
    // Create individual server files
    const servers = originalConfig.mcpServers || {};
    const serverNames = Object.keys(servers);
    
    console.log(`Migrating ${serverNames.length} MCP servers...`);
    
    serverNames.forEach(serverName => {
      const serverConfig = servers[serverName];
      const filePath = path.join(SERVERS_DIR, `${serverName}.json`);
      
      try {
        fs.writeFileSync(filePath, JSON.stringify(serverConfig, null, 2));
        console.log(`✓ Migrated ${serverName} to ${filePath}`);
      } catch (error) {
        console.error(`✗ Failed to migrate ${serverName}: ${error.message}`);
      }
    });
    
    // Create the new bridge configuration
    const bridgeConfig = {
      mcpServers: {
        "mcp-bridge": {
          command: "node",
          args: [
            "C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools\\bridge_controller\\bridge_mcp_server.js"
          ]
        }
      }
    };
    
    const bridgeConfigPath = 'C:\\Users\\JJ\\AppData\\Local\\Programs\\Qoder\\tools\\mcp.json';
    fs.writeFileSync(bridgeConfigPath, JSON.stringify(bridgeConfig, null, 2));
    console.log(`✓ Created new bridge configuration at ${bridgeConfigPath}`);
    
    console.log('\nMigration completed successfully!');
    console.log('To use the new architecture:');
    console.log('1. Replace your original mcp.json with the new bridge configuration');
    console.log('2. Ensure all individual server files are in the individual_mcp_servers directory');
    console.log('3. Restart Qoder to use the bridge controller architecture');
    
  } catch (error) {
    console.error('Migration failed:', error.message);
    process.exit(1);
  }
}

// Run migration if this script is executed directly
if (require.main === module) {
  migrateConfiguration();
}