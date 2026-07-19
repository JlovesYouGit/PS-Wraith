const chalk = require('chalk');

/**
 * Core Module Installer
 * Standard module installer function that executes after IDE installations
 *
 * @param {Object} options - Installation options
 * @param {string} options.projectRoot - The root directory of the target project
 * @param {Object} options.config - Module configuration from install-config.yaml
 * @param {Array<string>} options.installedIDEs - Array of IDE codes that were installed
 * @param {Object} options.logger - Logger instance for output
 * @returns {Promise<boolean>} - Success status
 */
async function install(options) {
  const { projectRoot, config, installedIDEs, logger } = options;

  try {
    logger.log(chalk.blue('🏗️  Installing Core Module...'));

    // Core agent configs are created by the main installer's createAgentConfigs method
    // No need to create them here - they'll be handled along with all other agents

    // Handle IDE-specific configurations if needed
    if (installedIDEs && installedIDEs.length > 0) {
      logger.log(chalk.cyan(`Configuring Core for IDEs: ${installedIDEs.join(', ')}`));

      // Add any IDE-specific Core configurations here
      for (const ide of installedIDEs) {
        await configureForIDE(ide, projectRoot, config, logger);
      }
    }

    logger.log(chalk.green('✓ Core Module installation complete'));
    return true;
  } catch (error) {
    logger.error(chalk.red(`Error installing Core module: ${error.message}`));
    return false;
  }
}

/**
 * Configure Core module for specific IDE
 * @private
 */
async function configureForIDE(ide, projectRoot, config, logger) {
  // Add IDE-specific configurations here
  switch (ide) {
    case 'claude-code': {
      // Claude Code specific Core configurations
      break;
    }
    case 'cursor': {
      // Cursor specific Core configurations
      break;
    }
    case 'windsurf': {
      // Windsurf specific Core configurations
      break;
    }
    case 'qoder': {
      // Qoder specific Core configurations
      logger.log(chalk.cyan('  Applying Qoder-specific core configurations...'));

      // Enable MCP integration in core config
      const coreConfigPath = `${projectRoot}/bmad/core/config.yaml`;
      const fs = require('fs-extra');

      if (await fs.pathExists(coreConfigPath)) {
        try {
          const yaml = require('js-yaml');
          const coreConfigContent = await fs.readFile(coreConfigPath, 'utf8');
          const coreConfig = yaml.load(coreConfigContent);

          // Add Qoder-specific configurations
          coreConfig.qoder_mcp_enabled = true;
          coreConfig.qoder_advanced_features = config.qoder_advanced_features ?? true;

          // Write updated configuration
          const updatedConfig = yaml.dump(coreConfig);
          await fs.writeFile(coreConfigPath, updatedConfig, 'utf8');
          logger.log(chalk.green('  ✓ Qoder MCP integration enabled in core configuration'));
        } catch (error) {
          logger.warn(chalk.yellow('  ⚠ Warning: Could not update core configuration for Qoder:', error.message));
        }
      }
      break;
    }
    // Add more IDEs as needed
    default: {
      // No specific configuration needed
      break;
    }
  }
}

module.exports = { install };
