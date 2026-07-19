/**
 * Unified MCP Integration for AI-SIEM and BMAD-METHOD
 * 
 * This module provides a unified MCP server that integrates both AI-SIEM and BMAD-METHOD
 * capabilities with operation intercept modifiers and cloud storage runtime features.
 */

const express = require('express');
const { Server } = require('http');
const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');
const cors = require('cors');

class UnifiedMcpIntegration {
  constructor(configPath = './pre-integrated-mode-config.yaml') {
    this.configPath = configPath;
    this.config = null;
    this.app = express();
    this.server = null;
    this.port = 3174;
    this.tools = new Map();
    this.capabilities = new Map();
    this.operationInterceptors = null;
    
    this.initialize();
  }

  /**
   * Initialize the unified MCP integration
   */
  async initialize() {
    try {
      // Load configuration
      this.config = await this.loadConfiguration();
      
      // Setup Express app
      this.setupExpressApp();
      
      // Initialize operation interceptors
      await this.initializeOperationInterceptors();
      
      // Register unified tools
      await this.registerUnifiedTools();
      
      // Setup module-specific capabilities
      await this.setupModuleCapabilities();
      
      console.log('✓ Unified MCP integration initialized successfully');
    } catch (error) {
      console.error('Failed to initialize unified MCP integration:', error.message);
      throw error;
    }
  }

  /**
   * Load configuration from YAML file
   */
  async loadConfiguration() {
    try {
      const configContent = await fs.readFile(this.configPath, 'utf8');
      return yaml.load(configContent);
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
  }

  /**
   * Setup Express application with middleware
   */
  setupExpressApp() {
    this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
    
    // Request logging middleware
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
    
    // Setup routes
    this.setupRoutes();
  }

  /**
   * Setup API routes
   */
  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: this.config.version,
        modules: Object.keys(this.config.modules)
      });
    });

    // List all available tools
    this.app.get('/tools', async (req, res) => {
      try {
        const tools = await this.listTools();
        res.json({ tools });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Execute a tool
    this.app.post('/tools/:toolName/execute', async (req, res) => {
      try {
        const { toolName } = req.params;
        const params = req.body;
        
        const result = await this.executeTool(toolName, params);
        res.json(result);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Get capabilities
    this.app.get('/capabilities', async (req, res) => {
      try {
        const capabilities = await this.getCapabilities();
        res.json({ capabilities });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Module-specific endpoints
    this.app.get('/modules/:moduleName/status', async (req, res) => {
      try {
        const { moduleName } = req.params;
        const status = await this.getModuleStatus(moduleName);
        res.json(status);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Operation interception endpoint
    this.app.post('/intercept', async (req, res) => {
      try {
        const operation = req.body;
        const result = await this.interceptOperation(operation);
        res.json(result);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Error handling middleware
    this.app.use((err, req, res, next) => {
      console.error('MCP Server Error:', err);
      res.status(500).json({ error: 'Internal server error' });
    });
  }

  /**
   * Initialize operation interceptors
   */
  async initializeOperationInterceptors() {
    const OperationInterceptModifiers = require('./operation-intercept-modifiers');
    this.operationInterceptors = new OperationInterceptModifiers(this.configPath);
  }

  /**
   * Register unified tools for both modules
   */
  async registerUnifiedTools() {
    // AI-SIEM Tools
    await this.registerAiSiamTools();
    
    // BMAD-METHOD Tools
    await this.registerBmadMethodTools();
    
    // Unified Cross-Module Tools
    await this.registerUnifiedCrossModuleTools();
  }

  /**
   * Register AI-SIEM specific tools
   */
  async registerAiSiamTools() {
    const aiSiamTools = [
      {
        name: 'siem_query_executor',
        description: 'Execute SIEM queries with enhanced capabilities',
        capabilities: ['threat_detection', 'log_analysis'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'siem',
            name: 'query_executor'
          }, params);
          
          return {
            status: 'success',
            tool: 'siem_query_executor',
            intercepted: intercepted.intercepted,
            result: `SIEM query executed with ${intercepted.intercepted ? 'intercepted' : 'original'} parameters`,
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'threat_intelligence_analyzer',
        description: 'Analyze threat intelligence with cloud storage enhancement',
        capabilities: ['threat_detection', 'intelligence_analysis'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'siem',
            name: 'threat_intelligence_analyzer'
          }, params);
          
          return {
            status: 'success',
            tool: 'threat_intelligence_analyzer',
            intercepted: intercepted.intercepted,
            result: 'Threat intelligence analysis completed',
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'security_dashboard_generator',
        description: 'Generate security dashboards with runtime capabilities',
        capabilities: ['dashboard_generation', 'visualization'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'siem',
            name: 'dashboard_generator'
          }, params);
          
          return {
            status: 'success',
            tool: 'security_dashboard_generator',
            intercepted: intercepted.intercepted,
            result: 'Security dashboard generated successfully',
            timestamp: new Date().toISOString()
          };
        }
      }
    ];

    for (const tool of aiSiamTools) {
      this.tools.set(tool.name, tool);
    }
  }

  /**
   * Register BMAD-METHOD specific tools
   */
  async registerBmadMethodTools() {
    const bmadTools = [
      {
        name: 'bmad_agent_executor',
        description: 'Execute BMAD agents with enhanced behavior',
        capabilities: ['agent_execution', 'workflow_management'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'bmad',
            name: 'agent_executor'
          }, params);
          
          return {
            status: 'success',
            tool: 'bmad_agent_executor',
            intercepted: intercepted.intercepted,
            result: 'BMAD agent executed successfully',
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'workflow_runner',
        description: 'Run BMAD workflows with cloud storage persistence',
        capabilities: ['workflow_execution', 'process_automation'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'bmad',
            name: 'workflow_runner'
          }, params);
          
          return {
            status: 'success',
            tool: 'workflow_runner',
            intercepted: intercepted.intercepted,
            result: 'BMAD workflow executed successfully',
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'document_generator',
        description: 'Generate documents using BMAD templates with enhancement',
        capabilities: ['document_generation', 'template_processing'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'bmad',
            name: 'document_generator'
          }, params);
          
          return {
            status: 'success',
            tool: 'document_generator',
            intercepted: intercepted.intercepted,
            result: 'Document generated successfully',
            timestamp: new Date().toISOString()
          };
        }
      }
    ];

    for (const tool of bmadTools) {
      this.tools.set(tool.name, tool);
    }
  }

  /**
   * Register unified cross-module tools
   */
  async registerUnifiedCrossModuleTools() {
    const unifiedTools = [
      {
        name: 'cross_module_executor',
        description: 'Execute operations across AI-SIEM and BMAD modules',
        capabilities: ['cross_module_execution', 'integration'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'unified',
            name: 'cross_module_executor'
          }, params);
          
          return {
            status: 'success',
            tool: 'cross_module_executor',
            intercepted: intercepted.intercepted,
            result: 'Cross-module operation executed successfully',
            involved_modules: ['ai-siem', 'bmad-method'],
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'capability_sharer',
        description: 'Share capabilities between modules',
        capabilities: ['capability_sharing', 'module_communication'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'unified',
            name: 'capability_sharer'
          }, params);
          
          return {
            status: 'success',
            tool: 'capability_sharer',
            intercepted: intercepted.intercepted,
            result: 'Capabilities shared between modules successfully',
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'unified_workflow_orchestrator',
        description: 'Orchestrate workflows across both modules',
        capabilities: ['workflow_orchestration', 'process_coordination'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'unified',
            name: 'unified_workflow_orchestrator'
          }, params);
          
          return {
            status: 'success',
            tool: 'unified_workflow_orchestrator',
            intercepted: intercepted.intercepted,
            result: 'Unified workflow orchestrated successfully',
            timestamp: new Date().toISOString()
          };
        }
      },
      
      {
        name: 'integrated_security_development',
        description: 'Integrate security monitoring with development workflows',
        capabilities: ['security_integration', 'development_coordination'],
        execute: async (params) => {
          const intercepted = await this.operationInterceptors.interceptOperation({
            type: 'unified',
            name: 'integrated_security_development'
          }, params);
          
          return {
            status: 'success',
            tool: 'integrated_security_development',
            intercepted: intercepted.intercepted,
            result: 'Security and development integration completed',
            timestamp: new Date().toISOString()
          };
        }
      }
    ];

    for (const tool of unifiedTools) {
      this.tools.set(tool.name, tool);
    }
  }

  /**
   * Setup module-specific capabilities
   */
  async setupModuleCapabilities() {
    // AI-SIEM Capabilities
    this.capabilities.set('ai-siem', {
      security_monitoring: true,
      threat_detection: true,
      log_parsing: true,
      dashboard_generation: true,
      alert_management: true,
      cloud_storage_integration: true
    });

    // BMAD-METHOD Capabilities
    this.capabilities.set('bmad-method', {
      agile_development: true,
      agent_orchestration: true,
      workflow_execution: true,
      document_generation: true,
      mcp_integration: true,
      cloud_storage_persistence: true
    });

    // Unified Capabilities
    this.capabilities.set('unified', {
      cross_module_communication: true,
      capability_sharing: true,
      unified_workflows: true,
      operation_interception: true,
      runtime_enhancement: true
    });
  }

  /**
   * Start the MCP server
   */
  async start(port = null) {
    if (port) {
      this.port = port;
    }

    return new Promise((resolve, reject) => {
      this.server = this.app.listen(this.port, () => {
        console.log(`✓ Unified MCP server started on port ${this.port}`);
        console.log(`✓ Available tools: ${this.tools.size}`);
        console.log(`✓ Registered modules: ${Object.keys(this.config.modules).join(', ')}`);
        resolve();
      });

      this.server.on('error', (error) => {
        console.error('Failed to start MCP server:', error);
        reject(error);
      });
    });
  }

  /**
   * Stop the MCP server
   */
  async stop() {
    if (this.server) {
      return new Promise((resolve) => {
        this.server.close(() => {
          console.log('✓ Unified MCP server stopped');
          resolve();
        });
      });
    }
  }

  /**
   * List all available tools
   */
  async listTools() {
    const toolList = [];
    
    for (const [name, tool] of this.tools) {
      toolList.push({
        name,
        description: tool.description,
        capabilities: tool.capabilities
      });
    }
    
    return toolList;
  }

  /**
   * Execute a specific tool
   */
  async executeTool(toolName, params = {}) {
    const tool = this.tools.get(toolName);
    
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }
    
    try {
      return await tool.execute(params);
    } catch (error) {
      throw new Error(`Failed to execute tool ${toolName}: ${error.message}`);
    }
  }

  /**
   * Get all capabilities
   */
  async getCapabilities() {
    const allCapabilities = {};
    
    for (const [module, caps] of this.capabilities) {
      allCapabilities[module] = caps;
    }
    
    return allCapabilities;
  }

  /**
   * Get module status
   */
  async getModuleStatus(moduleName) {
    const moduleConfig = this.config.modules[moduleName];
    
    if (!moduleConfig) {
      throw new Error(`Module not found: ${moduleName}`);
    }
    
    const capabilities = this.capabilities.get(moduleName) || {};
    const modulePath = moduleConfig.path;
    
    return {
      name: moduleName,
      enabled: moduleConfig.enabled,
      priority: moduleConfig.priority,
      path: modulePath,
      path_exists: await fs.pathExists(modulePath),
      capabilities,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Intercept operation using operation interceptors
   */
  async interceptOperation(operation) {
    if (!this.operationInterceptors) {
      return { intercepted: false, result: null };
    }
    
    return await this.operationInterceptors.interceptOperation(operation);
  }
}

module.exports = UnifiedMcpIntegration;
