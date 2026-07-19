const { spawn } = require('child_process');
const path = require('path');
const BridgeController = require('./bridge_controller');

// Create bridge controller instance
const bridgeController = new BridgeController();

// Function to dynamically spawn an MCP server
function spawnMcpServer(serverName, config) {
  const { command, args = [], env = {} } = config;
  
  // Merge with current environment
  const mergedEnv = { ...process.env, ...env };
  
  // Spawn the MCP server process
  const child = spawn(command, args, {
    env: mergedEnv,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  return child;
}

// Handle requests to list available servers
function handleListServers() {
  const servers = bridgeController.getAvailableServers();
  console.log(JSON.stringify({
    type: 'response',
    method: 'list_servers',
    result: {
      servers: servers
    }
  }));
}

// Handle requests to load and start a specific server
function handleLoadServer(serverName) {
  const config = bridgeController.loadServer(serverName);
  
  if (!config) {
    console.log(JSON.stringify({
      type: 'error',
      message: `Failed to load server: ${serverName}`
    }));
    return;
  }
  
  // Spawn the actual MCP server
  const serverProcess = spawnMcpServer(serverName, config);
  
  // Forward stdout and stderr
  serverProcess.stdout.on('data', (data) => {
    process.stdout.write(data);
  });
  
  serverProcess.stderr.on('data', (data) => {
    process.stderr.write(data);
  });
  
  // Handle process exit
  serverProcess.on('exit', (code) => {
    console.log(JSON.stringify({
      type: 'server_exit',
      server: serverName,
      code: code
    }));
  });
  
  console.log(JSON.stringify({
    type: 'response',
    method: 'load_server',
    result: {
      server: serverName,
      status: 'started'
    }
  }));
}

// Main message handler
function handleMessage(data) {
  try {
    const message = JSON.parse(data);
    
    switch (message.method) {
      case 'list_servers':
        handleListServers();
        break;
      case 'load_server':
        handleLoadServer(message.params.serverName);
        break;
      default:
        console.log(JSON.stringify({
          type: 'error',
          message: `Unknown method: ${message.method}`
        }));
    }
  } catch (error) {
    console.log(JSON.stringify({
      type: 'error',
      message: `Failed to parse message: ${error.message}`
    }));
  }
}

// Listen for messages from Qoder
process.stdin.on('data', handleMessage);

// Initial handshake
console.log(JSON.stringify({
  type: 'ready',
  capabilities: ['list_servers', 'load_server']
}));