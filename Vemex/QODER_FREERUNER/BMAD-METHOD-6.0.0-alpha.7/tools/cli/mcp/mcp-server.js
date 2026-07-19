/**
 * BMAD MCP Server
 *
 * Modular Capability Platform server for BMAD integration
 * Provides enhanced capabilities through modular tools and services
 */

const http = require('node:http');
const chalk = require('chalk');
const { executeMcpTool } = require('../../../src/core/mcp/mcp-integration.js');

// Default port
const PORT = process.env.BMAD_MCP_PORT || 3174;

// Tools registry
const tools = new Map();

/**
 * Register a tool with the MCP server
 * @param {string} name - Tool name
 * @param {Object} tool - Tool definition
 */
function registerTool(name, tool) {
  tools.set(name, tool);
  console.log(chalk.green(`Registered tool: ${name}`));
}

/**
 * Get list of available tools
 * @returns {Array} List of tool names
 */
function getToolList() {
  return [...tools.keys()];
}

/**
 * Handle HTTP requests
 * @param {Object} req - HTTP request
 * @param {Object} res - HTTP response
 */
async function handleRequest(req, res) {
  try {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight requests
    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Parse URL
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathname = url.pathname;

    // Route handling
    if (pathname === '/' && req.method === 'GET') {
      // Health check endpoint
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(
        JSON.stringify(
          {
            status: 'ok',
            version: '1.0.0',
            name: 'BMAD MCP Server',
            tools: getToolList(),
          },
          null,
          2,
        ),
      );
    } else if (pathname === '/tools' && req.method === 'GET') {
      // Get list of available tools
      const toolList = getToolList();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ tools: toolList }, null, 2));
    } else if (pathname === '/tools/:name' && req.method === 'GET') {
      // Get tool information
      const toolName = pathname.split('/')[2];
      const tool = tools.get(toolName);

      if (tool) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(tool, null, 2));
      } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Tool not found' }, null, 2));
      }
    } else if (pathname === '/execute' && req.method === 'POST') {
      // Execute a tool
      let body = '';
      req.on('data', (chunk) => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        try {
          const params = JSON.parse(body);
          const { toolName, projectName, toolParams } = params;

          if (!toolName) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Missing toolName parameter' }, null, 2));
            return;
          }

          // Execute the tool
          const result = await executeMcpTool(projectName, toolName, toolParams);

          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(result, null, 2));
        } catch {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid JSON in request body' }, null, 2));
        }
      });
    } else {
      // 404 Not Found
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Endpoint not found' }, null, 2));
    }
  } catch (error) {
    console.error(chalk.red('Error handling request:'), error.message);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Internal server error' }, null, 2));
  }
}

/**
 * Start the MCP server
 */
function startServer() {
  const server = http.createServer(handleRequest);

  server.listen(PORT, () => {
    console.log(chalk.green(`BMAD MCP Server running on port ${PORT}`));
    console.log(chalk.dim(`Health check: http://localhost:${PORT}/`));
    console.log(chalk.dim(`Tools list: http://localhost:${PORT}/tools`));
  });

  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log(chalk.yellow('\nShutting down MCP server...'));
    server.close(() => {
      console.log(chalk.green('MCP server stopped'));
      process.exit(0);
    });
  });

  return server;
}

/**
 * Register built-in tools
 */
async function registerBuiltInTools() {
  // Get available tools from BMAD
  try {
    // In a real implementation, we would dynamically load tools
    // For now, we'll register some example tools

    registerTool('bmad-agent-executor', {
      name: 'bmad-agent-executor',
      description: 'Execute BMAD agents with full context',
      parameters: {
        type: 'object',
        properties: {
          agentModule: { type: 'string', description: 'Module containing the agent' },
          agentName: { type: 'string', description: 'Name of the agent to execute' },
          userInput: { type: 'string', description: 'User input to pass to the agent' },
        },
        required: ['agentModule', 'agentName'],
      },
    });

    registerTool('bmad-workflow-runner', {
      name: 'bmad-workflow-runner',
      description: 'Run BMAD workflows with guided execution',
      parameters: {
        type: 'object',
        properties: {
          workflowModule: { type: 'string', description: 'Module containing the workflow' },
          workflowName: { type: 'string', description: 'Name of the workflow to run' },
        },
        required: ['workflowModule', 'workflowName'],
      },
    });

    registerTool('bmad-document-generator', {
      name: 'bmad-document-generator',
      description: 'Generate documents using BMAD templates',
      parameters: {
        type: 'object',
        properties: {
          templatePath: { type: 'string', description: 'Path to the document template' },
          variables: { type: 'object', description: 'Variables to populate in the template' },
        },
        required: ['templatePath'],
      },
    });

    console.log(chalk.green('✓ Registered built-in MCP tools'));
  } catch (error) {
    console.error(chalk.red('Failed to register built-in tools:'), error.message);
  }
}

// If run directly, start the server
if (require.main === module) {
  console.log(chalk.blue('Starting BMAD MCP Server...'));

  // Register built-in tools
  registerBuiltInTools().then(() => {
    // Start the server
    startServer();
  });
}

module.exports = {
  startServer,
  registerTool,
  getToolList,
};
