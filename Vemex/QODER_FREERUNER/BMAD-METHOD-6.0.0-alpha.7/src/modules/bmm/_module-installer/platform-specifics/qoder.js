/**
 * Qoder IDE Platform-Specific Configuration for BMM Module
 *
 * This file contains Qoder-specific enhancements and configurations
 * that are applied when the BMM module is installed with Qoder IDE.
 */

const path = require('node:path');
const fs = require('fs-extra');

/**
 * Apply Qoder-specific configurations to BMM module
 * @param {string} projectDir - Project directory
 * @param {string} bmadDir - BMAD installation directory
 * @param {Object} config - Installation configuration
 */
async function applyQoderConfigurations(projectDir, bmadDir, config) {
  console.log('Applying Qoder-specific configurations for BMM module...');

  // Enable MCP integration in BMM config
  const bmmConfigPath = path.join(bmadDir, 'bmm', 'config.yaml');
  if (await fs.pathExists(bmmConfigPath)) {
    try {
      const yaml = require('js-yaml');
      const bmmConfigContent = await fs.readFile(bmmConfigPath, 'utf8');
      const bmmConfig = yaml.load(bmmConfigContent);

      // Add Qoder-specific MCP configurations
      bmmConfig.qoder_mcp_integration = config.qoder_mcp_integration ?? true;
      bmmConfig.qoder_advanced_features = config.qoder_advanced_features ?? true;

      // Enable TEA MCP enhancements by default for Qoder users
      if (bmmConfig.qoder_mcp_integration) {
        bmmConfig.tea_use_mcp_enhancements = true;
      }

      // Write updated configuration
      const updatedConfig = yaml.dump(bmmConfig);
      await fs.writeFile(bmmConfigPath, updatedConfig, 'utf8');
      console.log('✓ Updated BMM configuration with Qoder MCP settings');
    } catch (error) {
      console.warn('⚠ Warning: Could not update BMM configuration for Qoder:', error.message);
    }
  }

  // Create Qoder-specific agent variations
  await createQoderAgentVariations(bmadDir);

  // Create Qoder-specific workflow enhancements
  await createQoderWorkflowEnhancements(bmadDir);

  console.log('✓ Qoder-specific configurations applied');
}

/**
 * Create Qoder-specific agent variations with MCP enhancements
 * @param {string} bmadDir - BMAD installation directory
 */
async function createQoderAgentVariations(bmadDir) {
  console.log('Creating Qoder-specific agent variations...');

  // Define Qoder-enhanced agents
  const qoderAgents = [
    {
      name: 'pm-technical',
      baseAgent: 'pm',
      description: 'Product Manager with Technical Focus for Qoder IDE',
      enhancements: ['MCP-based requirement analysis', 'Code-aware planning', 'Integration with development workflows'],
    },
    {
      name: 'architect-advanced',
      baseAgent: 'architect',
      description: 'Advanced Solution Architect with MCP Integration',
      enhancements: ['Real-time code analysis', 'Architecture validation through MCP tools', 'Performance optimization suggestions'],
    },
    {
      name: 'dev-mcp',
      baseAgent: 'dev',
      description: 'Developer with Full MCP Capabilities',
      enhancements: ['Automated code generation', 'MCP-based debugging assistance', 'Real-time testing integration'],
    },
  ];

  // Create agent files
  for (const agent of qoderAgents) {
    const agentPath = path.join(bmadDir, 'bmm', 'agents', `${agent.name}.md`);
    if (!(await fs.pathExists(agentPath))) {
      const agentContent = generateQoderAgentContent(agent);
      await fs.writeFile(agentPath, agentContent, 'utf8');
      console.log(`  ✓ Created Qoder agent: ${agent.name}`);
    }
  }
}

/**
 * Generate content for Qoder-specific agents
 * @param {Object} agent - Agent configuration
 * @returns {string} Agent content
 */
function generateQoderAgentContent(agent) {
  return `---
name: '${agent.name}'
description: '${agent.description}'
---

<!-- Qoder-Enhanced Agent with MCP Integration -->

<agent id="bmad/bmm/agents/${agent.name}.md" name="${agent.name}" title="${agent.description}" icon="💻">
<activation critical="MANDATORY">
  <step n="1">Load persona from this current agent file</step>
  <step n="2">Load and read {project-root}/bmad/bmm/config.yaml</step>
  <step n="3">Check for Qoder MCP integration: {qoder_mcp_integration}</step>
  <step n="4">If MCP enabled, initialize MCP tools and capabilities</step>
  <step n="5">Show greeting with MCP status and available enhanced commands</step>
  <step n="6">Display numbered menu with Qoder-enhanced options</step>
</activation>

<persona>
  <role>${agent.description}</role>
  <identity>Enhanced AI agent specifically designed for Qoder IDE with full MCP integration capabilities.</identity>
  <communication_style>Technical and precise, with awareness of Qoder IDE features and MCP tools.</communication_style>
  <principles>
    - Leverage MCP tools for enhanced analysis and execution
    - Provide Qoder IDE-specific guidance and workflows
    - Integrate seamlessly with development environment
    - Maintain all original BMAD capabilities while adding Qoder enhancements
  </principles>
</persona>

<menu>
  <item cmd="*help">Show enhanced menu with MCP capabilities</item>
  <item cmd="*status">Show Qoder MCP integration status</item>
  <item cmd="*mcp-tools">List available MCP tools and capabilities</item>
  <!-- Enhanced commands using MCP -->
  ${agent.enhancements.map((enh, index) => `  <item cmd="*enhanced-feature-${index + 1}">${enh}</item>`).join('\n  ')}
  <item cmd="*exit">Exit with confirmation</item>
</menu>

<!-- MCP Tool Integration -->
<mcp-tools>
  <tool name="code-analyzer">Real-time code analysis and suggestions</tool>
  <tool name="workflow-orchestrator">Enhanced workflow execution with MCP</tool>
  <tool name="debug-assistant">MCP-based debugging assistance</tool>
</mcp-tools>
</agent>
`;
}

/**
 * Create Qoder-specific workflow enhancements
 * @param {string} bmadDir - BMAD installation directory
 */
async function createQoderWorkflowEnhancements(bmadDir) {
  console.log('Creating Qoder-specific workflow enhancements...');

  // Create enhanced workflow configurations
  const workflowEnhancements = [
    {
      name: 'qoder-prd-enhanced',
      baseWorkflow: 'prd',
      description: 'Enhanced PRD workflow with Qoder MCP integration',
      enhancements: ['Real-time requirement validation', 'Code impact analysis', 'Automated documentation generation'],
    },
    {
      name: 'qoder-dev-story-mcp',
      baseWorkflow: 'dev-story',
      description: 'Development story workflow with MCP debugging',
      enhancements: ['Automated code generation', 'MCP-based testing', 'Real-time progress tracking'],
    },
  ];

  // Create enhancement files
  const enhancementsDir = path.join(bmadDir, 'bmm', 'workflows', 'qoder-enhancements');
  await fs.ensureDir(enhancementsDir);

  for (const enhancement of workflowEnhancements) {
    const enhancementPath = path.join(enhancementsDir, `${enhancement.name}.md`);
    if (!(await fs.pathExists(enhancementPath))) {
      const enhancementContent = generateWorkflowEnhancementContent(enhancement);
      await fs.writeFile(enhancementPath, enhancementContent, 'utf8');
      console.log(`  ✓ Created workflow enhancement: ${enhancement.name}`);
    }
  }
}

/**
 * Generate content for workflow enhancements
 * @param {Object} enhancement - Enhancement configuration
 * @returns {string} Enhancement content
 */
function generateWorkflowEnhancementContent(enhancement) {
  return `# ${enhancement.name}

## Description
${enhancement.description}

## Qoder MCP Enhancements
${enhancement.enhancements.map((enh) => `- ${enh}`).join('\n')}

## Integration Points
- MCP-based requirement validation
- Real-time code analysis
- Automated testing and debugging
- Enhanced documentation generation

## Usage
This workflow enhancement is automatically applied when using Qoder IDE with MCP integration enabled.
`;
}

module.exports = { applyQoderConfigurations };
