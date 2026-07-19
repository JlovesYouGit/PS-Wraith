/**
 * Runtime Capability Detection and Configuration System
 * 
 * This module provides dynamic capability detection, configuration management,
 * and runtime adaptation for the integrated AI-SIEM and BMAD-METHOD system.
 */

const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');
const { EventEmitter } = require('events');

class RuntimeCapabilityDetector extends EventEmitter {
  constructor(configPath = './pre-integrated-mode-config.yaml') {
    super();
    this.configPath = configPath;
    this.config = null;
    this.detectedCapabilities = new Map();
    this.capabilityHistory = new Array();
    this.detectionMethods = new Map();
    this.configurationManager = null;
    this.cloudStoragePath = null;
    this.isRunning = false;
    this.scanInterval = null;
    
    this.initialize();
  }

  /**
   * Initialize the runtime capability detector
   */
  async initialize() {
    try {
      // Load configuration
      this.config = await this.loadConfiguration();
      
      // Setup cloud storage path
      this.cloudStoragePath = this.config.cloud_storage.base_path;
      await fs.ensureDir(this.cloudStoragePath);
      
      // Initialize detection methods
      await this.initializeDetectionMethods();
      
      // Setup configuration manager
      await this.setupConfigurationManager();
      
      // Load existing capability history
      await this.loadCapabilityHistory();
      
      console.log('✓ Runtime capability detector initialized successfully');
    } catch (error) {
      console.error('Failed to initialize runtime capability detector:', error.message);
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
   * Initialize detection methods
   */
  async initializeDetectionMethods() {
    const detectionConfig = this.config.runtime_detection;
    
    for (const method of detectionConfig.detection_methods) {
      this.detectionMethods.set(method, {
        name: method,
        enabled: true,
        last_run: null,
        success_count: 0,
        failure_count: 0,
        execution_time: []
      });
    }
  }

  /**
   * Setup configuration manager
   */
  async setupConfigurationManager() {
    this.configurationManager = {
      applyDetected: this.config.runtime_detection.auto_configuration.apply_detected,
      persistConfiguration: this.config.runtime_detection.auto_configuration.persist_configuration,
      
      async applyConfiguration(capability, detected) {
        if (!this.applyDetected) return false;
        
        try {
          const configPath = path.join(
            this.cloudStoragePath,
            'runtime-config',
            `${capability}.json`
          );
          
          const config = {
            capability,
            detected,
            timestamp: new Date().toISOString(),
            auto_applied: true,
            configuration: await this.generateCapabilityConfig(capability, detected)
          };
          
          await fs.ensureDir(path.dirname(configPath));
          await fs.writeJson(configPath, config, { spaces: 2 });
          
          return true;
        } catch (error) {
          console.error(`Failed to apply configuration for ${capability}:`, error.message);
          return false;
        }
      },
      
      async generateCapabilityConfig(capability, detected) {
        const baseConfig = {
          enabled: detected,
          priority: 'medium',
          auto_configure: true
        };
        
        switch (capability) {
          case 'cloud_storage_access':
            return {
              ...baseConfig,
              storage_path: this.cloudStoragePath,
              persistent_cache: true,
              backup_enabled: true
            };
            
          case 'mcp_server_connectivity':
            return {
              ...baseConfig,
              server_port: this.config.mcp_integration.port,
              auto_start: this.config.mcp_integration.auto_start,
              health_check_interval: 30
            };
            
          case 'ai_siem_parsers':
            return {
              ...baseConfig,
              parser_directory: path.join(
                this.config.modules['ai-siem'].path,
                'parsers'
              ),
              auto_load: true,
              validation_enabled: true
            };
            
          case 'bmad_agents':
            return {
              ...baseConfig,
              agent_directory: path.join(
                this.config.modules['bmad-method'].path,
                'src/modules/bmm/agents'
              ),
              auto_initialize: true,
              collaboration_enabled: true
            };
            
          case 'cross_module_integration':
            return {
              ...baseConfig,
              integration_enabled: true,
              communication_protocol: 'mcp',
              data_sharing: true,
              workflow_coordination: true
            };
            
          default:
            return baseConfig;
        }
      }
    };
  }

  /**
   * Load existing capability history
   */
  async loadCapabilityHistory() {
    try {
      const historyPath = path.join(this.cloudStoragePath, 'capability-history.json');
      
      if (await fs.pathExists(historyPath)) {
        const history = await fs.readJson(historyPath);
        this.capabilityHistory = history;
      }
    } catch (error) {
      console.warn('Failed to load capability history:', error.message);
      this.capabilityHistory = [];
    }
  }

  /**
   * Start capability detection
   */
  async start() {
    if (this.isRunning) {
      console.log('Runtime capability detector is already running');
      return;
    }
    
    this.isRunning = true;
    
    // Perform initial scan
    await this.performFullScan();
    
    // Start periodic scanning
    const scanInterval = this.config.runtime_detection.scan_interval * 1000;
    this.scanInterval = setInterval(async () => {
      await this.performIncrementalScan();
    }, scanInterval);
    
    console.log(`✓ Runtime capability detector started (scan interval: ${this.config.runtime_detection.scan_interval}s)`);
    this.emit('started');
  }

  /**
   * Stop capability detection
   */
  async stop() {
    if (!this.isRunning) {
      return;
    }
    
    this.isRunning = false;
    
    if (this.scanInterval) {
      clearInterval(this.scanInterval);
      this.scanInterval = null;
    }
    
    console.log('✓ Runtime capability detector stopped');
    this.emit('stopped');
  }

  /**
   * Perform a full capability scan
   */
  async performFullScan() {
    console.log('Performing full capability scan...');
    
    const startTime = Date.now();
    const results = new Map();
    
    for (const capability of this.config.runtime_detection.capabilities_to_detect) {
      const result = await this.detectCapability(capability, 'full_scan');
      results.set(capability, result);
    }
    
    const scanTime = Date.now() - startTime;
    
    // Record scan results
    await this.recordScanResults('full_scan', results, scanTime);
    
    // Apply auto-configuration if enabled
    if (this.config.runtime_detection.auto_configuration.enabled) {
      await this.applyAutoConfiguration(results);
    }
    
    console.log(`Full scan completed in ${scanTime}ms`);
    this.emit('full_scan_completed', Object.fromEntries(results));
  }

  /**
   * Perform an incremental capability scan
   */
  async performIncrementalScan() {
    console.log('Performing incremental capability scan...');
    
    const startTime = Date.now();
    const results = new Map();
    const changedCapabilities = [];
    
    for (const capability of this.config.runtime_detection.capabilities_to_detect) {
      const previousState = this.detectedCapabilities.get(capability);
      const result = await this.detectCapability(capability, 'incremental_scan');
      
      // Check if capability state changed
      if (!previousState || previousState.detected !== result.detected) {
        changedCapabilities.push(capability);
        console.log(`Capability ${capability} changed: ${previousState?.detected} -> ${result.detected}`);
      }
      
      results.set(capability, result);
    }
    
    const scanTime = Date.now() - startTime;
    
    // Record scan results
    await this.recordScanResults('incremental_scan', results, scanTime);
    
    // Apply auto-configuration for changed capabilities
    if (this.config.runtime_detection.auto_configuration.enabled && changedCapabilities.length > 0) {
      const changedResults = new Map();
      for (const cap of changedCapabilities) {
        changedResults.set(cap, results.get(cap));
      }
      await this.applyAutoConfiguration(changedResults);
    }
    
    // Emit change events
    if (changedCapabilities.length > 0) {
      this.emit('capabilities_changed', changedCapabilities);
    }
    
    this.emit('incremental_scan_completed', Object.fromEntries(results));
  }

  /**
   * Detect a specific capability using available methods
   */
  async detectCapability(capability, scanType = 'full_scan') {
    const startTime = Date.now();
    let detected = false;
    let confidence = 0.0;
    let method_used = null;
    let error = null;
    
    // Try each detection method until one succeeds
    for (const method of this.config.runtime_detection.detection_methods) {
      try {
        const methodResult = await this.detectCapabilityWithMethod(capability, method);
        
        if (methodResult.success) {
          detected = methodResult.detected;
          confidence = methodResult.confidence;
          method_used = method;
          
          // Update method statistics
          const methodStats = this.detectionMethods.get(method);
          methodStats.success_count++;
          methodStats.execution_time.push(Date.now() - startTime);
          methodStats.last_run = new Date().toISOString();
          
          break;
        }
      } catch (err) {
        error = err.message;
        
        // Update method statistics
        const methodStats = this.detectionMethods.get(method);
        methodStats.failure_count++;
        methodStats.last_run = new Date().toISOString();
      }
    }
    
    const result = {
      capability,
      detected,
      confidence,
      method_used,
      scan_type: scanType,
      timestamp: new Date().toISOString(),
      execution_time: Date.now() - startTime,
      error
    };
    
    // Update detected capabilities
    this.detectedCapabilities.set(capability, result);
    
    return result;
  }

  /**
   * Detect capability using a specific method
   */
  async detectCapabilityWithMethod(capability, method) {
    switch (method) {
      case 'file_system_scan':
        return await this.detectWithFileSystemScan(capability);
        
      case 'configuration_analysis':
        return await this.detectWithConfigurationAnalysis(capability);
        
      case 'module_inspection':
        return await this.detectWithModuleInspection(capability);
        
      case 'capability_probing':
        return await this.detectWithCapabilityProbing(capability);
        
      default:
        throw new Error(`Unknown detection method: ${method}`);
    }
  }

  /**
   * Detect capability using file system scan
   */
  async detectWithFileSystemScan(capability) {
    switch (capability) {
      case 'cloud_storage_access':
        const exists = await fs.pathExists(this.cloudStoragePath);
        return { success: true, detected: exists, confidence: exists ? 0.95 : 0.0 };
        
      case 'mcp_server_connectivity':
        const mcpServerPath = path.join(
          this.config.modules['bmad-method'].path,
          'tools/cli/mcp/mcp-server.js'
        );
        const mcpExists = await fs.pathExists(mcpServerPath);
        return { success: true, detected: mcpExists, confidence: mcpExists ? 0.9 : 0.0 };
        
      case 'ai_siem_parsers':
        const parsersPath = path.join(
          this.config.modules['ai-siem'].path,
          'parsers'
        );
        const parsersExist = await fs.pathExists(parsersPath);
        const parserCount = parsersExist ? (await fs.readdir(parsersPath)).length : 0;
        return { 
          success: true, 
          detected: parserCount > 0, 
          confidence: parserCount > 0 ? 0.8 : 0.0 
        };
        
      case 'bmad_agents':
        const agentsPath = path.join(
          this.config.modules['bmad-method'].path,
          'src/modules/bmm/agents'
        );
        const agentsExist = await fs.pathExists(agentsPath);
        const agentCount = agentsExist ? (await fs.readdir(agentsPath)).length : 0;
        return { 
          success: true, 
          detected: agentCount > 0, 
          confidence: agentCount > 0 ? 0.8 : 0.0 
        };
        
      default:
        return { success: false, detected: false, confidence: 0.0 };
    }
  }

  /**
   * Detect capability using configuration analysis
   */
  async detectWithConfigurationAnalysis(capability) {
    try {
      switch (capability) {
        case 'cloud_storage_access':
          const cloudConfig = this.config.cloud_storage;
          return { 
            success: true, 
            detected: cloudConfig.enabled, 
            confidence: cloudConfig.enabled ? 0.9 : 0.0 
          };
          
        case 'mcp_server_connectivity':
          const mcpConfig = this.config.mcp_integration;
          return { 
            success: true, 
            detected: mcpConfig.enabled, 
            confidence: mcpConfig.enabled ? 0.85 : 0.0 
          };
          
        case 'operation_interception':
          const interceptConfig = this.config.operation_intercept;
          return { 
            success: true, 
            detected: interceptConfig.enabled, 
            confidence: interceptConfig.enabled ? 0.85 : 0.0 
          };
          
        default:
          return { success: false, detected: false, confidence: 0.0 };
      }
    } catch (error) {
      return { success: false, detected: false, confidence: 0.0 };
    }
  }

  /**
   * Detect capability using module inspection
   */
  async detectWithModuleInspection(capability) {
    try {
      switch (capability) {
        case 'cross_module_integration':
          const aiSiamPath = this.config.modules['ai-siem'].path;
          const bmadPath = this.config.modules['bmad-method'].path;
          const bothExist = await fs.pathExists(aiSiamPath) && await fs.pathExists(bmadPath);
          return { 
            success: true, 
            detected: bothExist, 
            confidence: bothExist ? 0.9 : 0.0 
          };
          
        default:
          return { success: false, detected: false, confidence: 0.0 };
      }
    } catch (error) {
      return { success: false, detected: false, confidence: 0.0 };
    }
  }

  /**
   * Detect capability using capability probing
   */
  async detectWithCapabilityProbing(capability) {
    try {
      switch (capability) {
        case 'runtime_configuration':
          // Try to access runtime configuration
          const runtimeConfigPath = path.join(this.cloudStoragePath, 'runtime-config');
          const configExists = await fs.pathExists(runtimeConfigPath);
          return { 
            success: true, 
            detected: configExists, 
            confidence: configExists ? 0.7 : 0.0 
          };
          
        default:
          return { success: false, detected: false, confidence: 0.0 };
      }
    } catch (error) {
      return { success: false, detected: false, confidence: 0.0 };
    }
  }

  /**
   * Record scan results in history
   */
  async recordScanResults(scanType, results, scanTime) {
    const scanRecord = {
      scan_type: scanType,
      timestamp: new Date().toISOString(),
      scan_time_ms: scanTime,
      capabilities: Object.fromEntries(results),
      total_capabilities: results.size,
      detected_capabilities: Array.from(results.values()).filter(r => r.detected).length
    };
    
    this.capabilityHistory.push(scanRecord);
    
    // Keep only last 100 scan records
    if (this.capabilityHistory.length > 100) {
      this.capabilityHistory = this.capabilityHistory.slice(-100);
    }
    
    // Persist history
    await this.persistCapabilityHistory();
  }

  /**
   * Apply auto-configuration based on detection results
   */
  async applyAutoConfiguration(results) {
    for (const [capability, result] of results) {
      const applied = await this.configurationManager.applyConfiguration(
        capability, 
        result.detected
      );
      
      if (applied) {
        console.log(`✓ Auto-configuration applied for ${capability}: ${result.detected}`);
      }
    }
  }

  /**
   * Persist capability history to cloud storage
   */
  async persistCapabilityHistory() {
    try {
      const historyPath = path.join(this.cloudStoragePath, 'capability-history.json');
      await fs.writeJson(historyPath, this.capabilityHistory, { spaces: 2 });
    } catch (error) {
      console.error('Failed to persist capability history:', error.message);
    }
  }

  /**
   * Get current capability status
   */
  getCurrentCapabilities() {
    const capabilities = {};
    
    for (const [capability, result] of this.detectedCapabilities) {
      capabilities[capability] = {
        detected: result.detected,
        confidence: result.confidence,
        last_detected: result.timestamp,
        method_used: result.method_used
      };
    }
    
    return capabilities;
  }

  /**
   * Get capability statistics
   */
  getCapabilityStatistics() {
    const stats = {
      total_capabilities: this.detectedCapabilities.size,
      detected_capabilities: Array.from(this.detectedCapabilities.values())
        .filter(r => r.detected).length,
      detection_methods: {},
      scan_history: {
        total_scans: this.capabilityHistory.length,
        last_scan: this.capabilityHistory.length > 0 ? 
          this.capabilityHistory[this.capabilityHistory.length - 1].timestamp : null,
        average_scan_time: this.calculateAverageScanTime()
      }
    };
    
    // Calculate method statistics
    for (const [methodName, methodStats] of this.detectionMethods) {
      stats.detection_methods[methodName] = {
        success_count: methodStats.success_count,
        failure_count: methodStats.failure_count,
        success_rate: methodStats.success_count + methodStats.failure_count > 0 ?
          methodStats.success_count / (methodStats.success_count + methodStats.failure_count) : 0,
        average_execution_time: methodStats.execution_time.length > 0 ?
          methodStats.execution_time.reduce((a, b) => a + b, 0) / methodStats.execution_time.length : 0,
        last_run: methodStats.last_run
      };
    }
    
    return stats;
  }

  /**
   * Calculate average scan time
   */
  calculateAverageScanTime() {
    if (this.capabilityHistory.length === 0) return 0;
    
    const totalTime = this.capabilityHistory.reduce((sum, scan) => sum + scan.scan_time_ms, 0);
    return totalTime / this.capabilityHistory.length;
  }

  /**
   * Get detection status
   */
  getDetectionStatus() {
    return {
      is_running: this.isRunning,
      scan_interval: this.config.runtime_detection.scan_interval,
      last_scan: this.capabilityHistory.length > 0 ? 
        this.capabilityHistory[this.capabilityHistory.length - 1].timestamp : null,
      capabilities_detected: Array.from(this.detectedCapabilities.values())
        .filter(r => r.detected).length,
      total_capabilities: this.detectedCapabilities.size
    };
  }

  /**
   * Force detection of specific capability
   */
  async forceDetectCapability(capability) {
    if (!this.config.runtime_detection.capabilities_to_detect.includes(capability)) {
      throw new Error(`Capability not configured for detection: ${capability}`);
    }
    
    console.log(`Force detecting capability: ${capability}`);
    const result = await this.detectCapability(capability, 'forced_scan');
    
    // Apply auto-configuration if enabled
    if (this.config.runtime_detection.auto_configuration.enabled) {
      const results = new Map();
      results.set(capability, result);
      await this.applyAutoConfiguration(results);
    }
    
    return result;
  }
}

module.exports = RuntimeCapabilityDetector;
