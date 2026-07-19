/**
 * Core type definitions for the Fast Code Change Application System
 */

/**
 * Represents a single atomic code modification operation
 */
export interface EditOperation {
  id: string;
  filePath: string;
  lineNumber: number;
  columnStart?: number;
  columnEnd?: number;
  operationType: 'insert' | 'delete' | 'replace';
  oldContent?: string;  // For validation
  newContent: string;
  priority: number;
}

/**
 * A collection of related edit operations for a single file
 */
export interface ChangeBatch {
  filePath: string;
  operations: EditOperation[];
  totalLines: number;
}

/**
 * Ordered list of pending code modifications to be applied
 */
export interface ChangeQueue {
  batches: ChangeBatch[];
  totalOperations: number;
  estimatedDuration: number;
}

/**
 * Represents a specific location in a file for navigation
 */
export interface NavigationTarget {
  filePath: string;
  lineNumber: number;
  columnNumber?: number;
}

/**
 * Result of attempting to lock onto a code position
 */
export interface LockResult {
  locked: boolean;
  position: { line: number; column: number };
  actualContent: string;
  matchesExpected: boolean;
  conflict?: ConflictDetails;
}

/**
 * Details about a content mismatch conflict
 */
export interface ConflictDetails {
  expected: string;
  actual: string;
  similarity: number;
}

/**
 * Configuration for scroll speed and navigation behavior
 */
export interface ScrollConfig {
  baseSpeed: number;        // Lines per second
  accelerationFactor: number;
  decelerationDistance: number;  // Lines before target
  interFileDelay: number;   // Milliseconds
}

/**
 * A plan for navigating between two locations
 */
export interface ScrollPlan {
  steps: ScrollStep[];
  totalDuration: number;
}

/**
 * A single step in a scroll plan
 */
export interface ScrollStep {
  action: 'scroll' | 'jump' | 'open-file';
  target: NavigationTarget;
  speed: number;
  duration: number;
}

/**
 * Result of navigating to a target location
 */
export interface NavigationResult {
  success: boolean;
  currentPosition: NavigationTarget;
  error?: string;
}

/**
 * Result of applying a single edit operation
 */
export interface OperationResult {
  success: boolean;
  operation: EditOperation;
  error?: string;
  diagnosticErrors?: string[];
}

/**
 * Result of applying a batch of changes
 */
export interface BatchResult {
  successful: number;
  failed: number;
  skipped: number;
  operations: OperationResult[];
}

/**
 * Overall result of applying a change queue
 */
export interface ApplicationResult {
  totalChanges: number;
  successful: number;
  failed: number;
  skipped: number;
  conflicts: ConflictDetails[];
  duration: number;
}

/**
 * Callback for progress updates
 */
export interface ProgressCallback {
  (current: number, total: number, operation: EditOperation): void;
}

/**
 * Validation result for a change queue
 */
export interface ValidationResult {
  valid: boolean;
  missingFiles: string[];
  errors: string[];
}

/**
 * User's choice for resolving a conflict
 */
export type ConflictResolution = 'skip' | 'retry' | 'manual' | 'revert';

/**
 * Configuration for the Fast Code Change System
 */
export interface FastChangeConfig {
  scrollSpeed: {
    base: number;
    acceleration: number;
    deceleration: number;
  };
  validation: {
    strictness: 'strict' | 'moderate' | 'lenient';
    requireContentMatch: boolean;
    useDiagnostics: boolean;
  };
  behavior: {
    autoFormat: boolean;
    pauseOnConflict: boolean;
    maxRetries: number;
  };
}

/**
 * Structured change request format
 */
export interface ChangeRequest {
  description: string;
  changes: Array<{
    file: string;
    modifications: Array<{
      line: number;
      column?: number;
      type: 'insert' | 'delete' | 'replace';
      old?: string;
      new: string;
    }>;
  }>;
}
