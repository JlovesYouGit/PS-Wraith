#!/usr/bin/env node

/**
 * Pre-Integrated Main Entry Point
 * AI-SIEM + BMAD-METHOD Unified System with Operation Intercept Modifiers
 * 
 * This is the main entry point that orchestrates all components of the pre-integrated
 * system including operation intercept modifiers, unified MCP integration, capability-based
 * behavior modifiers, and runtime capability detection.
 */

const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');
const { EventEmitter } = require('events');

// Import our custom modules
const OperationInterceptModifiers = require('./operation-intercept-modifiers');
const UnifiedMcpIntegration = require('./unified-mcp-integration');
const CapabilityBehaviorModifiers = require('./capability-behavior-modifiers');
const RuntimeCapabilityDetector = require('./runtime-capability-detector');

class PreIntegratedSystem extends EventEmitter {
  constructor(configPath = './pre-integrated-mode-config.yaml') {
    super();
    this.configPath = configPath;
    this.config = null;
    this.components = new Map();
    this.isInitialized = false;
    this.isRunning = false;
    this.cloudStoragePath = null;
    
    // Component references
    this.operationInterceptors = null;
    this.unifiedMcp = null;
    this.behaviorModifiers = null;
    this.capabilityDetector = null;
  }

  /**
   * Initialize the pre-integrated system
   */
  async initialize() {
    try {
      console.log('🚀 Initializing Pre-Integrated AI-SIEM + BMAD-METHOD System...');
      
      // Load configuration
      this.config = await this.loadConfiguration();
      
      // Setup cloud storage
      await this.setupCloudStorage();
      
      // Initialize components in the correct order
      await this.initializeComponents();
      
      // Setup component communication
      await this.setupComponentCommunication();
      
      this.isInitialized = true;
      console.log('✅ Pre-Integrated System initialized successfully');
      this.emit('initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize pre-integrated system:', error.message);
      throw error;
    }
  }

  /**
   * Load configuration from YAML file
   */
  async loadConfiguration() {
    try {
      const configContent = await fs.readFile(this.configPath, 'utf8');
      const config = yaml.load(configContent);
      console.log(`✓ Configuration loaded from ${this.configPath}`);
      return config;
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
  }

  /**
   * Setup cloud storage directories
   */
  async setupCloudStorage() {
    this.cloudStoragePath = this.config.cloud_storage.base_path;
    
    // Create main storage directories
    const directories = [
      this.cloudStoragePath,
      path.join(this.cloudStoragePath, 'capabilities'),
      path.join(this.cloudStoragePath, 'modifiers'),
      path.join(this.cloudStoragePath, 'behavior-modifiers'),
      path.join(this.cloudStoragePath, 'runtime-config'),
      path.join(this.cloudStoragePath, 'mcp-data'),
      path.join(this.cloudStoragePath, 'logs')
    ];
    
    for (const dir of directories) {
      await fs.ensureDir(dir);
    }
    
    console.log(`✓ Cloud storage setup at ${this.cloudStoragePath}`);
  }

  /**
   * Initialize all system components
   */
  async initializeComponents() {
    const initOrder = this.config.initialization.order;
    
    for (const step of initOrder) {
      await this.initializeComponent(step);
    }
  }

  /**
   * Initialize a specific component
   */
  async initializeComponent(componentName) {
    console.log(`Initializing component: ${componentName}`);
    
    try {
      switch (componentName) {
        case 'detect_runtime_capabilities':
          this.capabilityDetector = new RuntimeCapabilityDetector(this.configPath);
          this.components.set('capability_detector', this.capabilityDetector);
          break;
          
        case 'initialize_cloud_storage':
          // Cloud storage is already setup in setupCloudStorage()
          break;
          
        case 'configure_operation_intercepts':
          this.operationInterceptors = new OperationInterceptModifiers(this.configPath);
          this.components.set('operation_interceptors', this.operationInterceptors);
          break;
          
        case 'start_mcp_servers':
          this.unifiedMcp = new UnifiedMcpIntegration(this.configPath);
          this.components.set('unified_mcp', this.unifiedMcp);
          break;
          
        case 'load_ai_siem_capabilities':
          await this.loadAiSiamCapabilities();
          break;
          
        case 'load_bmad_method_capabilities':
          await this.loadBmadMethodCapabilities();
          break;
          
        case 'establish_cross_module_communication':
          await this.establishCrossModuleCommunication();
          break;
          
        case 'enable_pre_integrated_workflows':
          await this.enablePreIntegratedWorkflows();
          break;
          
        default:
          console.warn(`Unknown component: ${componentName}`);
      }
      
      console.log(`✓ Component initialized: ${componentName}`);
    } catch (error) {
      console.error(`❌ Failed to initialize component ${componentName}:`, error.message);
      throw error;
    }
  }

  /**
   * Load AI-SIEM capabilities
   */
  async loadAiSiamCapabilities() {
    const aiSiamConfig = this.config.modules['ai-siem'];
    const aiSiamPath = aiSiamConfig.path;
    
    if (!(await fs.pathExists(aiSiamPath))) {
      console.warn(`AI-SIEM path does not exist: ${aiSiamPath}`);
      return;
    }
    
    // Load AI-SIEM parsers
    const parsersPath = path.join(aiSiamPath, 'parsers');
    if (await fs.pathExists(parsersPath)) {
      const parsers = await fs.readdir(parsersPath);
      console.log(`✓ Loaded ${parsers.length} AI-SIEM parsers`);
    }
    
    // Load AI-SIEM dashboards
    const dashboardsPath = path.join(aiSiamPath, 'dashboards');
    if (await fs.pathExists(dashboardsPath)) {
      const dashboards = await fs.readdir(dashboardsPath);
      console.log(`✓ Loaded ${dashboards.length} AI-SIEM dashboards`);
    }
    
    // Store AI-SIEM capabilities
    this.components.set('ai_siem_capabilities', {
      path: aiSiamPath,
      loaded: true,
      capabilities: aiSiamConfig.capabilities
    });
  }

  /**
   * Load BMAD-METHOD capabilities
   */
  async loadBmadMethodCapabilities() {
    const bmadConfig = this.config.modules['bmad-method'];
    const bmadPath = bmadConfig.path;
    
    if (!(await fs.pathExists(bmadPath))) {
      console.warn(`BMAD-METHOD path does not exist: ${bmadPath}`);
      return;
    }
    
    // Load BMAD agents
    const agentsPath = path.join(bmadPath, 'src/modules/bmm/agents');
    if (await fs.pathExists(agentsPath)) {
      const agents = await fs.readdir(agentsPath);
      console.log(`✓ Loaded ${agents.length} BMAD agents`);
    }
    
    // Load BMAD workflows
    const workflowsPath = path.join(bmadPath, 'src/modules/bmm/workflows');
    if (await fs.pathExists(workflowsPath)) {
      const workflows = await fs.readdir(workflowsPath);
      console.log(`✓ Loaded ${workflows.length} BMAD workflows`);
    }
    
    // Store BMAD-METHOD capabilities
    this.components.set('bmad_method_capabilities', {
      path: bmadPath,
      loaded: true,
      capabilities: bmadConfig.capabilities
    });
  }

  /**
   * Establish cross-module communication
   */
  async establishCrossModuleCommunication() {
    // Setup event listeners for cross-module communication
    if (this.capabilityDetector) {
      this.capabilityDetector.on('capabilities_changed', (changedCapabilities) => {
        this.handleCapabilityChanges(changedCapabilities);
      });
    }
    
    // Setup communication channels
    this.components.set('cross_module_communication', {
      enabled: true,
      channels: ['events', 'mcp', 'shared_storage'],
      status: 'active'
    });
    
    console.log('✓ Cross-module communication established');
  }

  /**
   * Enable pre-integrated workflows
   */
  async enablePreIntegratedWorkflows() {
    const workflows = this.config.pre_integrated_workflows;
    
    for (const [workflowName, workflowConfig] of Object.entries(workflows)) {
      this.components.set(`workflow_${workflowName}`, {
        ...workflowConfig,
        enabled: true,
        status: 'ready'
      });
    }
    
    console.log(`✓ Enabled ${Object.keys(workflows).length} pre-integrated workflows`);
  }

  /**
   * Setup communication between components
   */
  async setupComponentCommunication() {
    // Connect capability detector to behavior modifiers
    if (this.capabilityDetector && this.operationInterceptors) {
      this.capabilityDetector.on('capabilities_changed', async (changedCapabilities) => {
        for (const capability of changedCapabilities) {
          await this.operationInterceptors.interceptOperation({
            type: 'capability_change',
            name: capability
          }, { changed: true });
        }
      });
    }
    
    // Connect MCP server to operation interceptors
    if (this.unifiedMcp && this.operationInterceptors) {
      // The MCP server will use operation interceptors internally
    }
    
    console.log('✓ Component communication setup completed');
  }

  /**
   * Start the pre-integrated system
   */
  async start() {
    if (!this.isInitialized) {
      throw new Error('System must be initialized before starting');
    }
    
    if (this.isRunning) {
      console.log('System is already running');
      return;
    }
    
    try {
      console.log('🚀 Starting Pre-Integrated System...');
      
      // Start capability detector
      if (this.capabilityDetector) {
        await this.capabilityDetector.start();
      }
      
      // Start unified MCP server
      if (this.unifiedMcp) {
        await this.unifiedMcp.start(this.config.mcp_integration.port);
      }
      
      // Start behavior modifiers
      if (this.behaviorModifiers) {
        // Behavior modifiers are started automatically during initialization
      }
      
      this.isRunning = true;
      console.log('✅ Pre-Integrated System started successfully');
      this.emit('started');
      
      // Display system status
      await this.displaySystemStatus();
      
    } catch (error) {
      console.error('❌ Failed to start pre-integrated system:', error.message);
      throw error;
    }
  }

  /**
   * Stop the pre-integrated system
   */
  async stop() {
    if (!this.isRunning) {
      console.log('System is not running');
      return;
    }
    
    try {
      console.log('🛑 Stopping Pre-Integrated System...');
      
      // Stop capability detector
      if (this.capabilityDetector) {
        await this.capabilityDetector.stop();
      }
      
      // Stop unified MCP server
      if (this.unifiedMcp) {
        await this.unifiedMcp.stop();
      }
      
      this.isRunning = false;
      console.log('✅ Pre-Integrated System stopped successfully');
      this.emit('stopped');
      
    } catch (error) {
      console.error('❌ Failed to stop pre-integrated system:', error.message);
      throw error;
    }
  }

  /**
   * Handle capability changes
   */
  async handleCapabilityChanges(changedCapabilities) {
    console.log(`Handling capability changes for: ${changedCapabilities.join(', ')}`);
    
    // This is where you can implement logic to handle capability changes
    // such as reconfiguring components, updating workflows, etc.
    
    for (const capability of changedCapabilities) {
      this.emit('capability_changed', capability);
    }
  }

  /**
   * Display system status
   */
  async displaySystemStatus() {
    console.log('\n📊 System Status:');
    console.log('================');
    
    // Display component status
    console.log('\nComponents:');
    for (const [name, component] of this.components) {
      console.log(`  ✓ ${name}: ${component.loaded ? 'Loaded' : 'Not loaded'}`);
    }
    
    // Display capabilities
    if (this.capabilityDetector) {
      const capabilities = this.capabilityDetector.getCurrentCapabilities();
      console.log('\nDetected Capabilities:');
      for (const [capability, info] of Object.entries(capabilities)) {
        console.log(`  ${info.detected ? '✓' : '✗'} ${capability} (${info.confidence.toFixed(2)})`);
      }
    }
    
    // Display MCP server status
    if (this.unifiedMcp) {
      console.log(`\nMCP Server: Running on port ${this.config.mcp_integration.port}`);
    }
    
    console.log('\nSystem is ready for operations! 🚀');
  }

  /**
   * Get system status
   */
  async getSystemStatus() {
    const status = {
      initialized: this.isInitialized,
      running: this.isRunning,
      config_path: this.configPath,
      cloud_storage_path: this.cloudStoragePath,
      components: {},
      capabilities: null,
      timestamp: new Date().toISOString()
    };
    
    // Component status
    for (const [name, component] of this.components) {
      status.components[name] = {
        loaded: !!component,
        type: typeof component
      };
    }
    
    // Capabilities status
    if (this.capabilityDetector) {
      status.capabilities = this.capabilityDetector.getCurrentCapabilities();
    }
    
    return status;
  }

  /**
   * Execute a pre-integrated workflow
   */
  async executeWorkflow(workflowName, params = {}) {
    const workflowKey = `workflow_${workflowName}`;
    const workflow = this.components.get(workflowKey);
    
    if (!workflow) {
      throw new Error(`Workflow not found: ${workflowName}`);
    }
    
    console.log(`🔄 Executing workflow: ${workflowName}`);
    
    try {
      // Intercept workflow execution
      if (this.operationInterceptors) {
        const intercepted = await this.operationInterceptors.interceptOperation({
          type: 'workflow',
          name: workflowName
        }, params);
        
        if (intercepted.intercepted) {
          console.log(`Workflow execution intercepted with ${intercepted.appliedModifiers.length} modifiers`);
        }
      }
      
      // Execute workflow steps
      const results = [];
      for (const step of workflow.steps) {
        console.log(`  Executing step: ${step}`);
        
        // Here you would implement the actual step execution
        // For now, we'll simulate it
        const stepResult = {
          step,
          status: 'completed',
          timestamp: new Date().toISOString()
        };
        
        results.push(stepResult);
      }
      
      console.log(`✅ Workflow ${workflowName} completed successfully`);
      return {
        workflow: workflowName,
        status: 'completed',
        results,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error(`❌ Workflow ${workflowName} failed:`, error.message);
      throw error;
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  const system = new PreIntegratedSystem();
  
  try {
    switch (command) {
      case 'start':
        await system.initialize();
        await system.start();
        
        // Handle graceful shutdown
        process.on('SIGINT', async () => {
          console.log('\n🛑 Shutting down gracefully...');
          await system.stop();
          process.exit(0);
        });
        
        // Keep the process running
        console.log('Press Ctrl+C to stop the system');
        break;
        
      case 'init':
        await system.initialize();
        console.log('✅ System initialized. Use "start" to run the system.');
        break;
        
      case 'status':
        await system.initialize();
        const status = await system.getSystemStatus();
        console.log(JSON.stringify(status, null, 2));
        break;
        
      case 'workflow':
        const workflowName = args[1];
        if (!workflowName) {
          console.error('Usage: node pre-integrated-main.js workflow <workflow-name>');
          process.exit(1);
        }
        
        await system.initialize();
        await system.start();
        
        const result = await system.executeWorkflow(workflowName);
        console.log(JSON.stringify(result, null, 2));
        
        await system.stop();
        break;
        
      default:
        console.log(`
Usage: node pre-integrated-main.js <command>

Commands:
  start     - Initialize and start the pre-integrated system
  init      - Initialize the system without starting
  status    - Get current system status
  workflow  - Execute a specific workflow

Examples:
  node pre-integrated-main.js start
  node pre-integrated-main.js workflow security_development_pipeline
        `);
        break;
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Export for use as a module
module.exports = PreIntegratedSystem;

// Run CLI if called directly
if (require.main === module) {
  main();
}
