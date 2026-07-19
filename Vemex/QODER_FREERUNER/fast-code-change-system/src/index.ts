/**
 * Fast Code Change Application System
 * Main entry point and exports
 */

// Export all types
export * from './types';

// Export core components
export { ChangeParser } from './parser/ChangeParser';
export { IDENavigator } from './navigator/IDENavigator';
export { InlineLock } from './lock/InlineLock';
export { ScrollSpeedLogic } from './scroll/ScrollSpeedLogic';
export { FastChangeApplicator } from './applicator/FastChangeApplicator';
