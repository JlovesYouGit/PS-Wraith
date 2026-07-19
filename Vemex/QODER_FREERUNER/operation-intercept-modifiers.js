/**
 * Operation Intercept Modifiers for Cloud Storage Disk Runtime Capabilities
 * 
 * This module provides intercept modifiers that enhance model operations with
 * cloud storage capabilities and runtime behavior adaptation.
 */

const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');

class OperationInterceptModifiers {
  constructor(configPath = './pre-integrated-mode-config.yaml') {
    this.configPath = configPath;
    this.config = null;
    this.cloudStoragePath = null;
    this.interceptedOperations = new Map();
    this.capabilityCache = new Map();
    this.modifiers = new Map();
    
    this.initialize();
  }

  /**
   * Initialize the operation intercept modifiers
   */
  async initialize() {
    try {
      // Load configuration
      this.config = await this.loadConfiguration();
      
      // Setup cloud storage path
      this.cloudStoragePath = this.config.cloud_storage.base_path;
      await fs.ensureDir(this.cloudStoragePath);
      
      // Initialize intercept modifiers
      await this.initializeInterceptModifiers();
      
      // Setup runtime capability detection
      await this.setupCapabilityDetection();
      
      console.log('✓ Operation intercept modifiers initialized successfully');
    } catch (error) {
      console.error('Failed to initialize operation intercept modifiers:', error.message);
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
   * Initialize intercept modifiers based on configuration
   */
  async initializeInterceptModifiers() {
    const modifiers = this.config.operation_intercept.modifiers;
    
    for (const [modifierName, modifierConfig] of Object.entries(modifiers)) {
      this.modifiers.set(modifierName, {
        ...modifierConfig,
        active: true,
        interceptCount: 0,
        lastUsed: null
      });
      
      // Create modifier-specific storage
      const modifierPath = path.join(this.cloudStoragePath, 'modifiers', modifierName);
      await fs.ensureDir(modifierPath);
      
      // Store modifier configuration
      await fs.writeJson(
        path.join(modifierPath, 'config.json'),
        modifierConfig,
        { spaces: 2 }
      );
    }
  }

  /**
   * Setup runtime capability detection
   */
  async setupCapabilityDetection() {
    const detectionConfig = this.config.runtime_detection;
    
    if (detectionConfig.enabled) {
      // Create capability detection storage
      const capabilityPath = path.join(this.cloudStoragePath, 'capabilities');
      await fs.ensureDir(capabilityPath);
      
      // Initialize capability cache
      await this.initializeCapabilityCache();
      
      // Start periodic capability scanning if configured
      if (detectionConfig.scan_interval > 0) {
        this.startCapabilityScanning(detectionConfig.scan_interval);
      }
    }
  }

  /**
   * Initialize capability cache with detected capabilities
   */
  async initializeCapabilityCache() {
    const capabilities = this.config.runtime_detection.capabilities_to_detect;
    
    for (const capability of capabilities) {
      const detected = await this.detectCapability(capability);
      this.capabilityCache.set(capability, {
        detected,
        timestamp: new Date().toISOString(),
        enhanced: false
      });
    }
    
    // Persist capability cache
    await this.persistCapabilityCache();
  }

  /**
   * Detect a specific capability
   */
  async detectCapability(capability) {
    try {
      switch (capability) {
        case 'cloud_storage_access':
          return await fs.pathExists(this.cloudStoragePath);
          
        case 'mcp_server_connectivity':
          return await this.checkMcpServerConnectivity();
          
        case 'ai_siem_parsers':
          return await this.checkAiSiamParsers();
          
        case 'bmad_agents':
          return await this.checkBmadAgents();
          
        case 'cross_module_integration':
          return await this.checkCrossModuleIntegration();
          
        default:
          return false;
      }
    } catch (error) {
      console.warn(`Failed to detect capability ${capability}:`, error.message);
      return false;
    }
  }

  /**
   * Check MCP server connectivity
   */
  async checkMcpServerConnectivity() {
    try {
      const mcpConfig = this.config.mcp_integration;
      if (!mcpConfig.enabled) return false;
      
      // Check if MCP server files exist
      const mcpServerPath = path.join(
        this.config.modules['bmad-method'].path,
        'tools/cli/mcp/mcp-server.js'
      );
      
      return await fs.pathExists(mcpServerPath);
    } catch (error) {
      return false;
    }
  }

  /**
   * Check AI-SIEM parsers availability
   */
  async checkAiSiamParsers() {
    try {
      const parsersPath = path.join(
        this.config.modules['ai-siem'].path,
        'parsers'
      );
      
      if (!(await fs.pathExists(parsersPath))) return false;
      
      const parserCount = (await fs.readdir(parsersPath)).length;
      return parserCount > 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Check BMAD agents availability
   */
  async checkBmadAgents() {
    try {
      const agentsPath = path.join(
        this.config.modules['bmad-method'].path,
        'src/modules/bmm/agents'
      );
      
      if (!(await fs.pathExists(agentsPath))) return false;
      
      const agentCount = (await fs.readdir(agentsPath)).length;
      return agentCount > 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Check cross-module integration capability
   */
  async checkCrossModuleIntegration() {
    try {
      const aiSiamPath = this.config.modules['ai-siem'].path;
      const bmadPath = this.config.modules['bmad-method'].path;
      
      return await fs.pathExists(aiSiamPath) && await fs.pathExists(bmadPath);
    } catch (error) {
      return false;
    }
  }

  /**
   * Start periodic capability scanning
   */
  startCapabilityScanning(interval) {
    setInterval(async () => {
      await this.scanCapabilities();
    }, interval * 1000);
  }

  /**
   * Scan all capabilities and update cache
   */
  async scanCapabilities() {
    for (const [capability, cacheEntry] of this.capabilityCache) {
      const detected = await this.detectCapability(capability);
      
      // Update cache if detection status changed
      if (cacheEntry.detected !== detected) {
        this.capabilityCache.set(capability, {
          ...cacheEntry,
          detected,
          timestamp: new Date().toISOString()
        });
        
        console.log(`Capability ${capability} status changed: ${detected}`);
      }
    }
    
    await this.persistCapabilityCache();
  }

  /**
   * Persist capability cache to cloud storage
   */
  async persistCapabilityCache() {
    const cachePath = path.join(this.cloudStoragePath, 'capabilities', 'cache.json');
    await fs.writeJson(cachePath, Object.fromEntries(this.capabilityCache), { spaces: 2 });
  }

  /**
   * Intercept an operation and apply modifiers
   */
  async interceptOperation(operation, params = {}) {
    const operationKey = `${operation.type}:${operation.name}`;
    
    // Check if operation should be intercepted
    if (!this.shouldIntercept(operationKey)) {
      return { intercepted: false, result: null };
    }
    
    // Apply applicable modifiers
    const modifiedParams = await this.applyModifiers(operationKey, params);
    
    // Store operation interception
    this.interceptedOperations.set(operationKey, {
      timestamp: new Date().toISOString(),
      originalParams: params,
      modifiedParams,
      modifiers: this.getApplicableModifiers(operationKey)
    });
    
    // Persist interception log
    await this.persistInterceptionLog();
    
    return {
      intercepted: true,
      modifiedParams,
      appliedModifiers: this.getApplicableModifiers(operationKey)
    };
  }

  /**
   * Check if operation should be intercepted
   */
  shouldIntercept(operationKey) {
    const interceptPoints = this.config.operation_intercept.intercept_points;
    
    for (const point of interceptPoints) {
      if (operationKey.includes(point)) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Apply applicable modifiers to operation parameters
   */
  async applyModifiers(operationKey, params) {
    let modifiedParams = { ...params };
    
    for (const [modifierName, modifierConfig] of this.modifiers) {
      if (modifierConfig.active && this.isModifierApplicable(modifierConfig, operationKey)) {
        modifiedParams = await this.applyModifier(modifierName, modifierConfig, modifiedParams);
        
        // Update modifier stats
        modifierConfig.interceptCount++;
        modifierConfig.lastUsed = new Date().toISOString();
      }
    }
    
    return modifiedParams;
  }

  /**
   * Check if modifier is applicable to operation
   */
  isModifierApplicable(modifierConfig, operationKey) {
    const targetOperations = modifierConfig.target_operations || [];
    
    for (const targetOp of targetOperations) {
      if (operationKey.includes(targetOp)) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Apply a specific modifier to parameters
   */
  async applyModifier(modifierName, modifierConfig, params) {
    switch (modifierName) {
      case 'cloud_storage_enhancement':
        return await this.applyCloudStorageEnhancement(params);
        
      case 'behavior_adaptation':
        return await this.applyBehaviorAdaptation(params);
        
      case 'capability_interception':
        return await this.applyCapabilityInterception(params);
        
      default:
        return params;
    }
  }

  /**
   * Apply cloud storage enhancement modifier
   */
  async applyCloudStorageEnhancement(params) {
    return {
      ...params,
      cloud_storage_enabled: true,
      cloud_storage_path: this.cloudStoragePath,
      persistent_state: true,
      runtime_capabilities: Array.from(this.capabilityCache.keys())
    };
  }

  /**
   * Apply behavior adaptation modifier
   */
  async applyBehaviorAdaptation(params) {
    const activeCapabilities = Array.from(this.capabilityCache.entries())
      .filter(([_, cache]) => cache.detected)
      .map(([capability, _]) => capability);
    
    return {
      ...params,
      adaptive_behavior: true,
      available_capabilities: activeCapabilities,
      behavior_modifiers: this.determineBehaviorModifiers(activeCapabilities)
    };
  }

  /**
   * Apply capability interception modifier
   */
  async applyCapabilityInterception(params) {
    return {
      ...params,
      capability_interception: true,
      enhanced_capabilities: this.getEnhancedCapabilities(),
      runtime_enhancement: true
    };
  }

  /**
   * Determine behavior modifiers based on active capabilities
   */
  determineBehaviorModifiers(activeCapabilities) {
    const modifiers = [];
    
    if (activeCapabilities.includes('ai_siem_parsers')) {
      modifiers.push('security_focused');
    }
    
    if (activeCapabilities.includes('bmad_agents')) {
      modifiers.push('development_focused');
    }
    
    if (activeCapabilities.includes('cross_module_integration')) {
      modifiers.push('integrated_mode');
    }
    
    return modifiers;
  }

  /**
   * Get enhanced capabilities
   */
  getEnhancedCapabilities() {
    const enhanced = [];
    
    for (const [capability, cache] of this.capabilityCache) {
      if (cache.detected) {
        enhanced.push({
          name: capability,
          enhanced: true,
          timestamp: cache.timestamp
        });
      }
    }
    
    return enhanced;
  }

  /**
   * Get applicable modifiers for operation
   */
  getApplicableModifiers(operationKey) {
    const applicable = [];
    
    for (const [modifierName, modifierConfig] of this.modifiers) {
      if (modifierConfig.active && this.isModifierApplicable(modifierConfig, operationKey)) {
        applicable.push(modifierName);
      }
    }
    
    return applicable;
  }

  /**
   * Persist interception log to cloud storage
   */
  async persistInterceptionLog() {
    const logPath = path.join(this.cloudStoragePath, 'interception-log.json');
    const logData = {
      timestamp: new Date().toISOString(),
      intercepted_operations: Object.fromEntries(this.interceptedOperations),
      modifiers: Object.fromEntries(this.modifiers),
      capabilities: Object.fromEntries(this.capabilityCache)
    };
    
    await fs.writeJson(logPath, logData, { spaces: 2 });
  }

  /**
   * Get current status of all modifiers and capabilities
   */
  async getStatus() {
    return {
      initialized: true,
      cloud_storage_path: this.cloudStoragePath,
      modifiers: Object.fromEntries(this.modifiers),
      capabilities: Object.fromEntries(this.capabilityCache),
      intercepted_operations: this.interceptedOperations.size,
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = OperationInterceptModifiers;
