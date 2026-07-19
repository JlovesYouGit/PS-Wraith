/**
 * Capability-Based Behavior Modifiers for Model Operations
 * 
 * This module provides behavior modification capabilities that adapt model operations
 * based on available capabilities and runtime context.
 */

const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');

class CapabilityBehaviorModifiers {
  constructor(configPath = './pre-integrated-mode-config.yaml') {
    this.configPath = configPath;
    this.config = null;
    this.behaviorModifiers = new Map();
    this.capabilityStates = new Map();
    this.adaptationHistory = new Array();
    this.cloudStoragePath = null;
    
    this.initialize();
  }

  /**
   * Initialize capability-based behavior modifiers
   */
  async initialize() {
    try {
      // Load configuration
      this.config = await this.loadConfiguration();
      
      // Setup cloud storage path
      this.cloudStoragePath = this.config.cloud_storage.base_path;
      await fs.ensureDir(this.cloudStoragePath);
      
      // Initialize behavior modifiers
      await this.initializeBehaviorModifiers();
      
      // Setup capability monitoring
      await this.setupCapabilityMonitoring();
      
      console.log('✓ Capability-based behavior modifiers initialized successfully');
    } catch (error) {
      console.error('Failed to initialize capability behavior modifiers:', error.message);
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
   * Initialize behavior modifiers from configuration
   */
  async initializeBehaviorModifiers() {
    const behaviorConfig = this.config.model_behavior.behavior_modifiers;
    
    for (const [modifierName, modifierConfig] of Object.entries(behaviorConfig)) {
      this.behaviorModifiers.set(modifierName, {
        ...modifierConfig,
        active: false,
        activation_count: 0,
        last_activated: null,
        adaptation_history: []
      });
    }
    
    // Create behavior modifiers storage
    const modifiersPath = path.join(this.cloudStoragePath, 'behavior-modifiers');
    await fs.ensureDir(modifiersPath);
    
    // Persist initial configuration
    await this.persistBehaviorModifiers();
  }

  /**
   * Setup capability monitoring
   */
  async setupCapabilityMonitoring() {
    // Initialize capability states
    await this.initializeCapabilityStates();
    
    // Start monitoring if enabled
    if (this.config.model_behavior.capability_based.enabled) {
      this.startCapabilityMonitoring();
    }
  }

  /**
   * Initialize capability states
   */
  async initializeCapabilityStates() {
    const defaultCapabilities = this.config.model_behavior.default_capabilities;
    
    for (const capability of defaultCapabilities) {
      this.capabilityStates.set(capability, {
        available: true,
        last_checked: new Date().toISOString(),
        confidence: 1.0,
        source: 'default_configuration'
      });
    }
    
    // Load additional capabilities from modules
    await this.loadModuleCapabilities();
  }

  /**
   * Load capabilities from configured modules
   */
  async loadModuleCapabilities() {
    const modules = this.config.modules;
    
    for (const [moduleName, moduleConfig] of Object.entries(modules)) {
      if (moduleConfig.enabled && moduleConfig.capabilities) {
        for (const capability of moduleConfig.capabilities) {
          this.capabilityStates.set(capability, {
            available: true,
            last_checked: new Date().toISOString(),
            confidence: 0.9,
            source: `module_${moduleName}`
          });
        }
      }
    }
  }

  /**
   * Start capability monitoring
   */
  startCapabilityMonitoring() {
    // Monitor capabilities every 30 seconds
    setInterval(async () => {
      await this.updateCapabilityStates();
      await this.evaluateBehaviorModifiers();
    }, 30000);
  }

  /**
   * Update capability states
   */
  async updateCapabilityStates() {
    for (const [capability, state] of this.capabilityStates) {
      const newState = await this.checkCapability(capability);
      
      // Update state if changed
      if (newState.available !== state.available || newState.confidence !== state.confidence) {
        this.capabilityStates.set(capability, {
          ...newState,
          last_checked: new Date().toISOString()
        });
        
        console.log(`Capability ${capability} state changed:`, newState);
      }
    }
    
    await this.persistCapabilityStates();
  }

  /**
   * Check a specific capability
   */
  async checkCapability(capability) {
    try {
      switch (capability) {
        case 'cloud_storage_access':
          return {
            available: await fs.pathExists(this.cloudStoragePath),
            confidence: 0.95
          };
          
        case 'mcp_tool_integration':
          return await this.checkMcpIntegration();
          
        case 'operation_interception':
          return await this.checkOperationInterception();
          
        case 'runtime_configuration':
          return {
            available: true,
            confidence: 0.9
          };
          
        case 'security_monitoring':
          return await this.checkSecurityMonitoring();
          
        case 'agent_orchestration':
          return await this.checkAgentOrchestration();
          
        default:
          return {
            available: false,
            confidence: 0.0
          };
      }
    } catch (error) {
      console.warn(`Failed to check capability ${capability}:`, error.message);
      return {
        available: false,
        confidence: 0.0
      };
    }
  }

  /**
   * Check MCP integration capability
   */
  async checkMcpIntegration() {
    try {
      const mcpConfig = this.config.mcp_integration;
      if (!mcpConfig.enabled) {
        return { available: false, confidence: 0.0 };
      }
      
      // Check if MCP server files exist
      const mcpServerPath = path.join(
        this.config.modules['bmad-method'].path,
        'tools/cli/mcp/mcp-server.js'
      );
      
      const exists = await fs.pathExists(mcpServerPath);
      return { available: exists, confidence: exists ? 0.9 : 0.0 };
    } catch (error) {
      return { available: false, confidence: 0.0 };
    }
  }

  /**
   * Check operation interception capability
   */
  async checkOperationInterception() {
    try {
      const interceptConfig = this.config.operation_intercept;
      const interceptFile = path.join(this.cloudStoragePath, 'interception-log.json');
      
      const exists = await fs.pathExists(interceptFile);
      return { 
        available: interceptConfig.enabled && exists, 
        confidence: interceptConfig.enabled ? 0.85 : 0.0 
      };
    } catch (error) {
      return { available: false, confidence: 0.0 };
    }
  }

  /**
   * Check security monitoring capability
   */
  async checkSecurityMonitoring() {
    try {
      const aiSiamPath = this.config.modules['ai-siem'].path;
      const parsersPath = path.join(aiSiamPath, 'parsers');
      
      const exists = await fs.pathExists(parsersPath);
      return { available: exists, confidence: exists ? 0.8 : 0.0 };
    } catch (error) {
      return { available: false, confidence: 0.0 };
    }
  }

  /**
   * Check agent orchestration capability
   */
  async checkAgentOrchestration() {
    try {
      const bmadPath = this.config.modules['bmad-method'].path;
      const agentsPath = path.join(bmadPath, 'src/modules/bmm/agents');
      
      const exists = await fs.pathExists(agentsPath);
      return { available: exists, confidence: exists ? 0.8 : 0.0 };
    } catch (error) {
      return { available: false, confidence: 0.0 };
    }
  }

  /**
   * Evaluate and activate behavior modifiers based on capabilities
   */
  async evaluateBehaviorModifiers() {
    for (const [modifierName, modifierConfig] of this.behaviorModifiers) {
      const shouldActivate = await this.shouldActivateModifier(modifierName, modifierConfig);
      
      if (shouldActivate && !modifierConfig.active) {
        await this.activateBehaviorModifier(modifierName);
      } else if (!shouldActivate && modifierConfig.active) {
        await this.deactivateBehaviorModifier(modifierName);
      }
    }
  }

  /**
   * Check if a behavior modifier should be activated
   */
  async shouldActivateModifier(modifierName, modifierConfig) {
    const trigger = modifierConfig.trigger;
    
    switch (trigger) {
      case 'ai-siem_module_active':
        return this.capabilityStates.get('security_monitoring')?.available || false;
        
      case 'bmad_method_module_active':
        return this.capabilityStates.get('agent_orchestration')?.available || false;
        
      case 'both_modules_active':
        const aiSiamActive = this.capabilityStates.get('security_monitoring')?.available || false;
        const bmadActive = this.capabilityStates.get('agent_orchestration')?.available || false;
        return aiSiamActive && bmadActive;
        
      default:
        return false;
    }
  }

  /**
   * Activate a behavior modifier
   */
  async activateBehaviorModifier(modifierName) {
    const modifier = this.behaviorModifiers.get(modifierName);
    if (!modifier) return;
    
    modifier.active = true;
    modifier.activation_count++;
    modifier.last_activated = new Date().toISOString();
    
    // Apply behavior modifications
    await this.applyBehaviorModifications(modifierName, modifier);
    
    // Record activation in history
    this.adaptationHistory.push({
      type: 'activation',
      modifier: modifierName,
      timestamp: new Date().toISOString(),
      capabilities: Array.from(this.capabilityStates.keys())
    });
    
    console.log(`✓ Activated behavior modifier: ${modifierName}`);
    await this.persistBehaviorModifiers();
  }

  /**
   * Deactivate a behavior modifier
   */
  async deactivateBehaviorModifier(modifierName) {
    const modifier = this.behaviorModifiers.get(modifierName);
    if (!modifier) return;
    
    modifier.active = false;
    
    // Record deactivation in history
    this.adaptationHistory.push({
      type: 'deactivation',
      modifier: modifierName,
      timestamp: new Date().toISOString(),
      capabilities: Array.from(this.capabilityStates.keys())
    });
    
    console.log(`✓ Deactivated behavior modifier: ${modifierName}`);
    await this.persistBehaviorModifiers();
  }

  /**
   * Apply behavior modifications for a modifier
   */
  async applyBehaviorModifications(modifierName, modifier) {
    const modifications = modifier.modifications;
    
    for (const modification of modifications) {
      await this.applyModification(modification, modifierName);
    }
    
    // Store in modifier history
    modifier.adaptation_history.push({
      timestamp: new Date().toISOString(),
      modifications: modifications,
      capabilities: Array.from(this.capabilityStates.keys())
    });
  }

  /**
   * Apply a specific modification
   */
  async applyModification(modification, modifierName) {
    switch (modification) {
      case 'prioritize_security_operations':
        await this.prioritizeSecurityOperations();
        break;
        
      case 'enhance_threat_detection':
        await this.enhanceThreatDetection();
        break;
        
      case 'enable_monitoring_mode':
        await this.enableMonitoringMode();
        break;
        
      case 'enable_agile_workflows':
        await this.enableAgileWorkflows();
        break;
        
      case 'enhance_agent_collaboration':
        await this.enhanceAgentCollaboration();
        break;
        
      case 'enable_documentation_mode':
        await this.enableDocumentationMode();
        break;
        
      case 'enable_cross_module_communication':
        await this.enableCrossModuleCommunication();
        break;
        
      case 'enhance_capability_sharing':
        await this.enhanceCapabilitySharing();
        break;
        
      case 'enable_unified_workflows':
        await this.enableUnifiedWorkflows();
        break;
        
      default:
        console.warn(`Unknown modification: ${modification}`);
    }
  }

  /**
   * Apply security-focused modifications
   */
  async prioritizeSecurityOperations() {
    const config = {
      priority_mode: 'security_focused',
      enhanced_monitoring: true,
      threat_prioritization: true
    };
    
    await this.saveModificationConfig('security_prioritization', config);
  }

  /**
   * Enhance threat detection capabilities
   */
  async enhanceThreatDetection() {
    const config = {
      enhanced_detection: true,
      real_time_analysis: true,
      automated_response: true
    };
    
    await this.saveModificationConfig('threat_detection_enhancement', config);
  }

  /**
   * Enable monitoring mode
   */
  async enableMonitoringMode() {
    const config = {
      monitoring_active: true,
      log_level: 'detailed',
      alert_threshold: 'low'
    };
    
    await this.saveModificationConfig('monitoring_mode', config);
  }

  /**
   * Apply development-focused modifications
   */
  async enableAgileWorkflows() {
    const config = {
      agile_mode: true,
      iterative_development: true,
      rapid_prototyping: true
    };
    
    await this.saveModificationConfig('agile_workflows', config);
  }

  /**
   * Enhance agent collaboration
   */
  async enhanceAgentCollaboration() {
    const config = {
      collaboration_enhanced: true,
      multi_agent_coordination: true,
      shared_context: true
    };
    
    await this.saveModificationConfig('agent_collaboration', config);
  }

  /**
   * Enable documentation mode
   */
  async enableDocumentationMode() {
    const config = {
      documentation_mode: true,
      auto_generation: true,
      comprehensive_logging: true
    };
    
    await this.saveModificationConfig('documentation_mode', config);
  }

  /**
   * Apply integrated mode modifications
   */
  async enableCrossModuleCommunication() {
    const config = {
      cross_module_comm: true,
      data_sharing: true,
      coordinated_operations: true
    };
    
    await this.saveModificationConfig('cross_module_communication', config);
  }

  /**
   * Enhance capability sharing
   */
  async enhanceCapabilitySharing() {
    const config = {
      capability_sharing: true,
      dynamic_allocation: true,
      resource_optimization: true
    };
    
    await this.saveModificationConfig('capability_sharing', config);
  }

  /**
   * Enable unified workflows
   */
  async enableUnifiedWorkflows() {
    const config = {
      unified_workflows: true,
      integrated_processes: true,
      seamless_coordination: true
    };
    
    await this.saveModificationConfig('unified_workflows', config);
  }

  /**
   * Save modification configuration
   */
  async saveModificationConfig(modificationName, config) {
    const configPath = path.join(
      this.cloudStoragePath, 
      'behavior-modifiers', 
      `${modificationName}.json`
    );
    
    await fs.writeJson(configPath, config, { spaces: 2 });
  }

  /**
   * Get current behavior adaptations
   */
  getBehaviorAdaptations() {
    const activeModifiers = Array.from(this.behaviorModifiers.entries())
      .filter(([_, config]) => config.active)
      .map(([name, config]) => ({
        name,
        activation_count: config.activation_count,
        last_activated: config.last_activated,
        modifications: config.modifications
      }));
    
    return {
      active_modifiers: activeModifiers,
      available_capabilities: Array.from(this.capabilityStates.keys()),
      adaptation_history: this.adaptationHistory.slice(-10), // Last 10 adaptations
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Adapt model behavior based on current capabilities
   */
  async adaptModelBehavior(operation, context = {}) {
    const adaptations = this.getBehaviorAdaptations();
    const activeModifiers = adaptations.active_modifiers;
    
    let modifiedOperation = { ...operation };
    
    // Apply active behavior modifiers
    for (const modifier of activeModifiers) {
      modifiedOperation = await this.applyBehaviorToOperation(
        modifiedOperation, 
        modifier, 
        context
      );
    }
    
    // Apply capability-based enhancements
    modifiedOperation = await this.applyCapabilityEnhancements(
      modifiedOperation, 
      context
    );
    
    return {
      original_operation: operation,
      modified_operation: modifiedOperation,
      applied_modifiers: activeModifiers.map(m => m.name),
      capabilities_used: adaptations.available_capabilities,
      adaptation_timestamp: new Date().toISOString()
    };
  }

  /**
   * Apply behavior modifier to operation
   */
  async applyBehaviorToOperation(operation, modifier, context) {
    // Add modifier-specific behavior to operation
    const modifiedOperation = {
      ...operation,
      behavior_modifiers: [...(operation.behavior_modifiers || []), modifier.name],
      priority: this.determineOperationPriority(operation, modifier),
      enhanced_capabilities: modifier.modifications
    };
    
    return modifiedOperation;
  }

  /**
   * Apply capability enhancements to operation
   */
  async applyCapabilityEnhancements(operation, context) {
    const enhancedOperation = { ...operation };
    
    // Add available capabilities to operation
    enhancedOperation.available_capabilities = Array.from(this.capabilityStates.keys())
      .filter(cap => this.capabilityStates.get(cap).available);
    
    // Add capability-based optimizations
    enhancedOperation.optimizations = this.determineOptimizations(
      enhancedOperation.available_capabilities
    );
    
    return enhancedOperation;
  }

  /**
   * Determine operation priority based on behavior modifier
   */
  determineOperationPriority(operation, modifier) {
    const basePriority = operation.priority || 'medium';
    
    // Adjust priority based on modifier
    if (modifier.name.includes('security')) {
      return 'high';
    } else if (modifier.name.includes('development')) {
      return basePriority;
    } else if (modifier.name.includes('integrated')) {
      return 'high';
    }
    
    return basePriority;
  }

  /**
   * Determine optimizations based on available capabilities
   */
  determineOptimizations(capabilities) {
    const optimizations = [];
    
    if (capabilities.includes('cloud_storage_access')) {
      optimizations.push('persistent_caching');
    }
    
    if (capabilities.includes('mcp_tool_integration')) {
      optimizations.push('tool_enhancement');
    }
    
    if (capabilities.includes('operation_interception')) {
      optimizations.push('runtime_adaptation');
    }
    
    if (capabilities.includes('security_monitoring') && capabilities.includes('agent_orchestration')) {
      optimizations.push('security_development_integration');
    }
    
    return optimizations;
  }

  /**
   * Persist behavior modifiers to cloud storage
   */
  async persistBehaviorModifiers() {
    const modifiersPath = path.join(
      this.cloudStoragePath, 
      'behavior-modifiers',
      'current-state.json'
    );
    
    const state = {
      modifiers: Object.fromEntries(this.behaviorModifiers),
      adaptation_history: this.adaptationHistory,
      timestamp: new Date().toISOString()
    };
    
    await fs.writeJson(modifiersPath, state, { spaces: 2 });
  }

  /**
   * Persist capability states to cloud storage
   */
  async persistCapabilityStates() {
    const statesPath = path.join(
      this.cloudStoragePath, 
      'capability-states.json'
    );
    
    const states = {
      capabilities: Object.fromEntries(this.capabilityStates),
      timestamp: new Date().toISOString()
    };
    
    await fs.writeJson(statesPath, states, { spaces: 2 });
  }

  /**
   * Get current status
   */
  async getStatus() {
    return {
      initialized: true,
      active_modifiers: Array.from(this.behaviorModifiers.entries())
        .filter(([_, config]) => config.active)
        .map(([name, _]) => name),
      available_capabilities: Array.from(this.capabilityStates.entries())
        .filter(([_, state]) => state.available)
        .map(([name, _]) => name),
      total_adaptations: this.adaptationHistory.length,
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = CapabilityBehaviorModifiers;
