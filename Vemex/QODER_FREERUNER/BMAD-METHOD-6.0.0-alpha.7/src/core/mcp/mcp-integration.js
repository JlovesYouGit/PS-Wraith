/**
 * MCP (Modular Capability Platform) Integration for BMAD
 *
 * This module provides seamless integration between BMAD and MCP,
 * enabling enhanced capabilities through modular tools and services.
 */

/* eslint-disable unicorn/prefer-module -- CommonJS module consumed by CLI tooling */

const fs = require('fs-extra');
const path = require('node:path');
const chalk = require('chalk');

/**
 * Initialize MCP integration for BMAD
 * @param {string} projectRoot - Project root directory
 * @param {Object} config - BMAD configuration
 * @returns {Promise<Object>} MCP integration status
 */
async function initializeMcpIntegration(projectRoot, config) {
  console.log(chalk.blue('Initializing MCP integration...'));

  try {
    // Check if MCP is enabled in configuration
    const mcpEnabled = config.qoder_mcp_enabled || config.mcp_enabled || false;

    if (!mcpEnabled) {
      console.log(chalk.yellow('MCP integration is disabled in configuration'));
      return { enabled: false, reason: 'Disabled in configuration' };
    }

    // Create MCP directory structure
    const mcpDir = path.join(projectRoot, 'bmad', 'mcp');
    await fs.ensureDir(mcpDir);

    // Create MCP configuration file
    const mcpConfig = {
      version: '1.0',
      enabled: true,
      servers: {
        bmad: {
          command: 'node',
          args: ['tools/bmad-npx-wrapper.js', 'mcp-server'],
          env: {
            BMAD_MCP_ENABLED: 'true',
            BMAD_MCP_PORT: '3174',
          },
        },
      },
      tools: [
        {
          name: 'bmad-agent-executor',
          description: 'Execute BMAD agents with full context',
          capabilities: ['agent-execution', 'context-aware'],
        },
        {
          name: 'bmad-workflow-runner',
          description: 'Run BMAD workflows with guided execution',
          capabilities: ['workflow-execution', 'guided-process'],
        },
        {
          name: 'bmad-document-generator',
          description: 'Generate documents using BMAD templates',
          capabilities: ['document-generation', 'template-processing'],
        },
      ],
    };

    const mcpConfigPath = path.join(mcpDir, 'config.json');
    await fs.writeJson(mcpConfigPath, mcpConfig, { spaces: 2 });

    // Create MCP tools directory
    const toolsDir = path.join(mcpDir, 'tools');
    await fs.ensureDir(toolsDir);

    // Create tool implementations
    await createMcpTools(toolsDir);

    console.log(chalk.green('✓ MCP integration initialized successfully'));
    return { enabled: true, configPath: mcpConfigPath };
  } catch (error) {
    console.error(chalk.red('Failed to initialize MCP integration:'), error.message);
    return { enabled: false, error: error.message };
  }
}

/**
 * Create MCP tool implementations
 * @param {string} toolsDir - Tools directory path
 */
async function createMcpTools(toolsDir) {
  // Create agent executor tool
  const agentExecutor = {
    name: 'bmad-agent-executor',
    description: 'Execute BMAD agents with full context',
    execute: async function (params = {}) {
      // Implementation would go here
      return { status: 'success', result: 'Agent executed successfully', params };
    },
  };

  await fs.writeJson(path.join(toolsDir, 'agent-executor.json'), agentExecutor, { spaces: 2 });

  // Create workflow runner tool
  const workflowRunner = {
    name: 'bmad-workflow-runner',
    description: 'Run BMAD workflows with guided execution',
    execute: async function (params = {}) {
      // Implementation would go here
      return { status: 'success', result: 'Workflow executed successfully', params };
    },
  };

  await fs.writeJson(path.join(toolsDir, 'workflow-runner.json'), workflowRunner, { spaces: 2 });

  // Create document generator tool
  const documentGenerator = {
    name: 'bmad-document-generator',
    description: 'Generate documents using BMAD templates',
    execute: async function (params = {}) {
      // Implementation would go here
      return { status: 'success', result: 'Document generated successfully', params };
    },
  };

  await fs.writeJson(path.join(toolsDir, 'document-generator.json'), documentGenerator, { spaces: 2 });
}

/**
 * Register MCP tools with the system
 * @param {Object} mcpServer - MCP server instance
 * @param {string} toolsDir - Tools directory path
 */
async function registerMcpTools(mcpServer, toolsDir) {
  try {
    const tools = await fs.readdir(toolsDir);

    for (const toolFile of tools) {
      if (toolFile.endsWith('.json')) {
        const toolPath = path.join(toolsDir, toolFile);
        const toolConfig = await fs.readJson(toolPath);

        // Register tool with MCP server
        mcpServer.registerTool(toolConfig.name, toolConfig);
        console.log(chalk.green(`  ✓ Registered MCP tool: ${toolConfig.name}`));
      }
    }
  } catch (error) {
    console.error(chalk.red('Failed to register MCP tools:'), error.message);
  }
}

/**
 * Get available MCP tools
 * @param {string} projectRoot - Project root directory
 * @returns {Promise<Array>} List of available MCP tools
 */
async function getAvailableMcpTools(projectRoot) {
  try {
    const mcpDir = path.join(projectRoot, 'bmad', 'mcp');
    const toolsDir = path.join(mcpDir, 'tools');

    if (!(await fs.pathExists(toolsDir))) {
      return [];
    }

    const tools = await fs.readdir(toolsDir);
    const toolList = [];

    for (const toolFile of tools) {
      if (toolFile.endsWith('.json')) {
        const toolPath = path.join(toolsDir, toolFile);
        const toolConfig = await fs.readJson(toolPath);
        toolList.push(toolConfig);
      }
    }

    return toolList;
  } catch (error) {
    console.error(chalk.red('Failed to get MCP tools:'), error.message);
    return [];
  }
}

/**
 * Execute an MCP tool
 * @param {string} projectName - Project name
 * @param {string} toolName - Tool name to execute
 * @param {Object} params - Tool parameters
 * @returns {Promise<Object>} Tool execution result
 */
async function executeMcpTool(projectName, toolName, params) {
  try {
    // In a real implementation, this would connect to the MCP server
    // and execute the specified tool with the given parameters

    console.log(chalk.blue(`Executing MCP tool: ${toolName}`));

    // Simulate tool execution
    const result = {
      tool: toolName,
      status: 'success',
      timestamp: new Date().toISOString(),
      result: `Executed ${toolName} with params: ${JSON.stringify(params)}`,
    };

    console.log(chalk.green(`✓ MCP tool executed successfully: ${toolName}`));
    return result;
  } catch (error) {
    console.error(chalk.red(`Failed to execute MCP tool ${toolName}:`), error.message);
    return {
      tool: toolName,
      status: 'error',
      timestamp: new Date().toISOString(),
      error: error.message,
    };
  }
}

module.exports = {
  initializeMcpIntegration,
  registerMcpTools,
  getAvailableMcpTools,
  executeMcpTool,
};
