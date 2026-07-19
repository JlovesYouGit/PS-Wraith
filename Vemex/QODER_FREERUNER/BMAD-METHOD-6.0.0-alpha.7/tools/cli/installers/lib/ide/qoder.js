const path = require('node:path');
const { BaseIdeSetup } = require('./_base-ide');
const chalk = require('chalk');
const inquirer = require('inquirer');
const { getAgentsFromBmad, getTasksFromBmad } = require('./shared/bmad-artifacts');

/**
 * Qoder IDE setup handler
 * Creates MCP-enabled configuration for Qoder IDE with seamless integration
 */
class QoderSetup extends BaseIdeSetup {
  constructor() {
    super('qoder', 'Qoder IDE', true); // preferred IDE
    this.configDir = '.qoder';
    this.commandsDir = 'commands';
    this.bmadDir = 'bmad';
    this.mcpDir = 'mcp';
  }

  /**
   * Collect configuration choices before installation
   * @param {Object} options - Configuration options
   * @returns {Object} Collected configuration
   */
  async collectConfiguration(options = {}) {
    const config = {};

    console.log('\n' + chalk.blue('  🔧 Qoder IDE Configuration'));
    console.log(chalk.dim('  Configure MCP integration and advanced settings\n'));

    const response = await inquirer.prompt([
      {
        type: 'list',
        name: 'mcpConfig',
        message: 'How would you like to configure MCP integration?',
        choices: [
          { name: 'Enable full MCP capabilities (recommended)', value: 'full' },
          { name: 'Enable basic MCP tools only', value: 'basic' },
          { name: 'Disable MCP integration', value: 'disabled' },
        ],
        default: 'full',
      },
      {
        type: 'confirm',
        name: 'enableAdvancedFeatures',
        message: 'Enable advanced Qoder features (MCP-based workflows, enhanced tools)?',
        default: true,
      },
    ]);

    config.mcpConfig = response.mcpConfig;
    config.enableAdvancedFeatures = response.enableAdvancedFeatures;

    return config;
  }

  /**
   * Setup Qoder IDE configuration with MCP integration
   * @param {string} projectDir - Project directory
   * @param {string} bmadDir - BMAD installation directory
   * @param {Object} options - Setup options
   */
  async setup(projectDir, bmadDir, options = {}) {
    console.log(chalk.cyan(`Setting up ${this.name} with MCP integration...`));

    // Create .qoder directory structure
    const qoderDir = path.join(projectDir, this.configDir);
    const commandsDir = path.join(qoderDir, this.commandsDir);
    const bmadCommandsDir = path.join(commandsDir, this.bmadDir);
    const mcpDir = path.join(qoderDir, this.mcpDir);

    await this.ensureDir(bmadCommandsDir);
    await this.ensureDir(mcpDir);

    // Configure MCP settings using pre-collected config if available
    const config = options.preCollectedConfig || {};
    await this.configureMcpSettings(qoderDir, { ...options, ...config });

    // Clean up any existing BMAD files before reinstalling
    await this.cleanup(projectDir);

    // Get agents, tasks, tools, and workflows (standalone only for tools/workflows)
    const agents = await getAgentsFromBmad(bmadDir, options.selectedModules || []);
    const tasks = await getTasksFromBmad(bmadDir, options.selectedModules || []);
    const tools = await this.getTools(bmadDir, true);
    const workflows = await this.getWorkflows(bmadDir, true);

    // Create directories for each module (including standalone)
    const modules = new Set();
    for (const item of [...agents, ...tasks, ...tools, ...workflows]) modules.add(item.module);

    for (const module of modules) {
      await this.ensureDir(path.join(bmadCommandsDir, module));
      await this.ensureDir(path.join(bmadCommandsDir, module, 'agents'));
      await this.ensureDir(path.join(bmadCommandsDir, module, 'tasks'));
      await this.ensureDir(path.join(bmadCommandsDir, module, 'tools'));
      await this.ensureDir(path.join(bmadCommandsDir, module, 'workflows'));
    }

    // Create command files for each agent
    let agentCount = 0;
    for (const agent of agents) {
      const content = await this.readAndProcess(agent.path, {
        module: agent.module,
        name: agent.name,
      });

      const targetPath = path.join(bmadCommandsDir, agent.module, 'agents', `${agent.name}.json`);

      await this.writeFile(targetPath, content);

      agentCount++;
      console.log(chalk.green(`  ✓ Added agent: /bmad:${agent.module}:agents:${agent.name}`));
    }

    // Create command files for each task
    let taskCount = 0;
    for (const task of tasks) {
      const content = await this.readAndProcess(task.path, {
        module: task.module,
        name: task.name,
      });

      const targetPath = path.join(bmadCommandsDir, task.module, 'tasks', `${task.name}.json`);

      await this.writeFile(targetPath, content);

      taskCount++;
      console.log(chalk.green(`  ✓ Added task: /bmad:${task.module}:tasks:${task.name}`));
    }

    // Create command files for each tool
    let toolCount = 0;
    for (const tool of tools) {
      const content = await this.readAndProcess(tool.path, {
        module: tool.module,
        name: tool.name,
      });

      const targetPath = path.join(bmadCommandsDir, tool.module, 'tools', `${tool.name}.json`);

      await this.writeFile(targetPath, content);

      toolCount++;
      console.log(chalk.green(`  ✓ Added tool: /bmad:${agent.module}:tools:${tool.name}`));
    }

    // Create command files for each workflow
    let workflowCount = 0;
    for (const workflow of workflows) {
      const content = await this.readAndProcess(workflow.path, {
        module: workflow.module,
        name: workflow.name,
      });

      const targetPath = path.join(bmadCommandsDir, workflow.module, 'workflows', `${workflow.name}.json`);

      await this.writeFile(targetPath, content);

      workflowCount++;
      console.log(chalk.green(`  ✓ Added workflow: /bmad:${workflow.module}:workflows:${workflow.name}`));
    }

    // Create MCP configuration files if enabled
    if (config.mcpConfig !== 'disabled') {
      await this.createMcpConfigurations(mcpDir, bmadDir, options);
    }

    console.log(chalk.green(`✓ ${this.name} configured with MCP integration:`));
    console.log(chalk.dim(`  - ${agentCount} agents configured`));
    console.log(chalk.dim(`  - ${taskCount} tasks configured`));
    console.log(chalk.dim(`  - ${toolCount} tools configured`));
    console.log(chalk.dim(`  - ${workflowCount} workflows configured`));
    if (config.mcpConfig !== 'disabled') {
      console.log(chalk.dim(`  - MCP integration enabled`));
    }
    console.log(chalk.dim(`  - Commands directory: ${path.relative(projectDir, bmadCommandsDir)}`));

    return {
      success: true,
      agents: agentCount,
      tasks: taskCount,
      tools: toolCount,
      workflows: workflowCount,
      mcpEnabled: config.mcpConfig !== 'disabled',
    };
  }

  /**
   * Configure MCP settings for Qoder
   */
  async configureMcpSettings(qoderDir, options) {
    const fs = require('fs-extra');
    const settingsPath = path.join(qoderDir, 'settings.json');

    await this.ensureDir(qoderDir);

    // Read existing settings
    let existingSettings = {};
    if (await fs.pathExists(settingsPath)) {
      try {
        const content = await fs.readFile(settingsPath, 'utf8');
        existingSettings = JSON.parse(content);
        console.log(chalk.yellow('  Found existing .qoder/settings.json'));
      } catch {
        console.warn(chalk.yellow('  Could not parse settings.json, creating new'));
      }
    }

    // Use pre-collected configuration or skip if not available
    let mcpConfig = options.mcpConfig;
    if (!mcpConfig) {
      // If no pre-collected config, use default
      mcpConfig = 'full';
    }

    const qoderSettings = {
      'mcp.enabled': mcpConfig !== 'disabled',
      'mcp.level': mcpConfig === 'full' ? 'advanced' : 'basic',
      'bmad.advancedFeatures': options.enableAdvancedFeatures ?? true,
      'chat.agent.enabled': true,
      'chat.agent.maxRequests': 20,
    };

    // Merge settings (existing take precedence)
    const mergedSettings = { ...qoderSettings, ...existingSettings };

    // Write settings
    await fs.writeFile(settingsPath, JSON.stringify(mergedSettings, null, 2));
    console.log(chalk.green('  ✓ Qoder settings configured with MCP integration'));
  }

  /**
   * Create MCP configuration files
   */
  async createMcpConfigurations(mcpDir, bmadDir, options) {
    // Create MCP server configuration
    const mcpConfig = {
      servers: {
        bmad: {
          command: 'node',
          args: ['tools/bmad-npx-wrapper.js', 'mcp-server'],
          env: {
            BMAD_MCP_ENABLED: 'true',
            BMAD_MCP_PORT: '3174',
          },
        },
        playwright: {
          command: 'npx',
          args: ['@playwright/mcp@latest'],
        },
      },
    };

    const mcpConfigPath = path.join(mcpDir, 'config.json');
    await this.writeFile(mcpConfigPath, JSON.stringify(mcpConfig, null, 2));
    console.log(chalk.green('  ✓ MCP server configuration created'));

    // Create MCP tools manifest
    const toolsManifest = {
      version: '1.0',
      tools: [
        {
          name: 'bmad-agent-executor',
          description: 'Execute BMAD agents with full context',
          inputSchema: {
            type: 'object',
            properties: {
              agentModule: { type: 'string', description: 'Module containing the agent' },
              agentName: { type: 'string', description: 'Name of the agent to execute' },
              userInput: { type: 'string', description: 'User input to pass to the agent' },
            },
            required: ['agentModule', 'agentName'],
          },
        },
        {
          name: 'bmad-workflow-runner',
          description: 'Run BMAD workflows with guided execution',
          inputSchema: {
            type: 'object',
            properties: {
              workflowModule: { type: 'string', description: 'Module containing the workflow' },
              workflowName: { type: 'string', description: 'Name of the workflow to run' },
            },
            required: ['workflowModule', 'workflowName'],
          },
        },
        {
          name: 'bmad-document-generator',
          description: 'Generate documents using BMAD templates',
          inputSchema: {
            type: 'object',
            properties: {
              templatePath: { type: 'string', description: 'Path to the document template' },
              variables: { type: 'object', description: 'Variables to populate in the template' },
            },
            required: ['templatePath'],
          },
        },
      ],
    };

    const toolsManifestPath = path.join(mcpDir, 'tools.json');
    await this.writeFile(toolsManifestPath, JSON.stringify(toolsManifest, null, 2));
    console.log(chalk.green('  ✓ MCP tools manifest created'));
  }

  /**
   * Read and process file content for Qoder
   */
  async readAndProcess(filePath, metadata) {
    const fs = require('fs-extra');
    const content = await fs.readFile(filePath, 'utf8');
    return this.processContent(content, metadata);
  }

  /**
   * Override processContent to add JSON metadata for Qoder
   * @param {string} content - File content
   * @param {Object} metadata - File metadata
   * @returns {string} Processed content with Qoder template
   */
  processContent(content, metadata = {}) {
    // First apply base processing (includes activation injection for agents)
    let prompt = super.processContent(content, metadata);

    // Determine the type and description based on content
    const isAgent = content.includes('<agent');
    const isTask = content.includes('<task');
    const isTool = content.includes('<tool');
    const isWorkflow = content.includes('workflow:') || content.includes('name:');

    let description = '';
    let category = '';

    if (isAgent) {
      // Extract agent title if available
      const titleMatch = content.match(/title="([^"]+)"/);
      const title = titleMatch ? titleMatch[1] : metadata.name;
      description = `BMAD ${metadata.module.toUpperCase()} Agent: ${title}`;
      category = 'agent';
    } else if (isTask) {
      // Extract task name if available
      const nameMatch = content.match(/name="([^"]+)"/);
      const taskName = nameMatch ? nameMatch[1] : metadata.name;
      description = `BMAD ${metadata.module.toUpperCase()} Task: ${taskName}`;
      category = 'task';
    } else if (isTool) {
      // Extract tool name if available
      const nameMatch = content.match(/name="([^"]+)"/);
      const toolName = nameMatch ? nameMatch[1] : metadata.name;
      description = `BMAD ${metadata.module.toUpperCase()} Tool: ${toolName}`;
      category = 'tool';
    } else if (isWorkflow) {
      // Workflow
      description = `BMAD ${metadata.module.toUpperCase()} Workflow: ${metadata.name}`;
      category = 'workflow';
    } else {
      description = `BMAD ${metadata.module.toUpperCase()}: ${metadata.name}`;
      category = 'unknown';
    }

    // Create JSON structure for Qoder
    const qoderCommand = {
      name: `${metadata.module}-${metadata.name}`,
      description: description,
      category: category,
      prompt: prompt,
      mcpEnabled: true,
      metadata: {
        module: metadata.module,
        type: category,
        bmadPath: `/bmad:${metadata.module}:${category}:${metadata.name}`,
      },
    };

    return JSON.stringify(qoderCommand, null, 2);
  }

  /**
   * Format name as title
   */
  formatTitle(name) {
    return name
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Cleanup Qoder configuration - surgically remove only BMAD files
   */
  async cleanup(projectDir) {
    const fs = require('fs-extra');
    const bmadCommandsDir = path.join(projectDir, this.configDir, this.commandsDir, this.bmadDir);
    const mcpDir = path.join(projectDir, this.configDir, this.mcpDir);

    if (await fs.pathExists(bmadCommandsDir)) {
      // Only remove BMAD files
      const files = await fs.readdir(bmadCommandsDir);
      let removed = 0;

      for (const file of files) {
        if (file.startsWith('bmad-')) {
          await fs.remove(path.join(bmadCommandsDir, file));
          removed++;
        }
      }

      if (removed > 0) {
        console.log(chalk.dim(`  Cleaned up ${removed} existing BMAD configurations`));
      }
    }

    // Clean up MCP configurations
    if (await fs.pathExists(mcpDir)) {
      await fs.remove(mcpDir);
      console.log(chalk.dim(`  Cleaned up MCP configurations`));
    }
  }
}

module.exports = { QoderSetup };
