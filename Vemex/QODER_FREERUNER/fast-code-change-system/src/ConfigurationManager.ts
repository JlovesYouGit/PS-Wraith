import { ScrollConfig, ChangeParserOptions } from './types';

/**
 * Represents the full set of user-configurable options for the system.
 */
export interface SystemConfig {
  parser: ChangeParserOptions;
  scrolling: ScrollConfig;
}

/**
 * Manages the system's configuration, providing default values and the ability to override them.
 */
export class ConfigurationManager {
  private currentConfig: SystemConfig;

  constructor(customConfig?: Partial<SystemConfig>) {
    const defaultConfig: SystemConfig = {
      parser: {
        validateFiles: true,
        groupByFile: true,
        sortByLineNumber: true,
      },
      scrolling: {
        baseSpeed: 100,
        maxSpeed: 2000,
        acceleration: 4000,
        decelerationDistance: 50,
        minPause: 200,
        maxPause: 1000,
      },
    };

    // Deep merge custom config over defaults
    this.currentConfig = {
      ...defaultConfig,
      ...customConfig,
      parser: { ...defaultConfig.parser, ...customConfig?.parser },
      scrolling: { ...defaultConfig.scrolling, ...customConfig?.scrolling },
    };
  }

  /**
   * Returns the currently active configuration.
   */
  public getConfig(): SystemConfig {
    return this.currentConfig;
  }

  /**
   * Updates a part of the configuration.
   * @param updatedConfig A partial configuration object to merge into the existing config.
   */
  public updateConfig(updatedConfig: Partial<SystemConfig>): void {
    this.currentConfig = {
      ...this.currentConfig,
      ...updatedConfig,
      parser: { ...this.currentConfig.parser, ...updatedConfig?.parser },
      scrolling: { ...this.currentConfig.scrolling, ...updatedConfig?.scrolling },
    };
  }
}
