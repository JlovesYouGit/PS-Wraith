/**
 * Core types for the Fast Code Change System
 */

export type OperationType = 'insert' | 'delete' | 'replace';

export interface Position {
  line: number;
  character: number;
}

export interface Range {
  start: Position;
  end: Position;
}

export interface EditOperation {
  id: string;
  filePath: string;
  range: Range;
  operationType: OperationType;
  oldContent: string;
  newContent: string;
  priority: number;
}

export interface ChangeBatch {
  filePath: string;
  operations: EditOperation[];
  totalLines: number;
}

export interface ChangeQueue {
  batches: ChangeBatch[];
  totalOperations: number;
  estimatedDuration: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface NavigationTarget {
  filePath: string;
  position: Position;
}

export interface NavigationResult {
  success: boolean;
  currentPosition: NavigationTarget;
  error?: string;
}

export interface LockResult {
  isLocked: boolean;
  position: Position;
  contentMatch: boolean;
  conflictDetails?: {
    expected: string;
    actual: string;
    similarity: number;
  };
}

export interface ScrollConfig {
  baseSpeed: number;
  maxSpeed: number;
  acceleration: number;
  decelerationDistance: number;
  minPause: number;
  maxPause: number;
}

export interface ScrollStep {
  lineNumber: number;
  delay: number; // in milliseconds
}

export interface ScrollPlan {
  steps: ScrollStep[];
  totalDuration: number; // in milliseconds
}

export interface ChangeParserOptions {
  validateFiles: boolean;
  groupByFile: boolean;
  sortByLineNumber: boolean;
}

export interface AppliedChange {
  operation: EditOperation;
  timestamp: Date;
}

export interface ChangeConflict {
  operation: EditOperation;
  message: string;
  details?: {
    expected: string;
    actual: string;
    similarity: number;
  };
}

export interface ApplicationResult {
  success: boolean;
  appliedChanges: AppliedChange[];
  conflicts: ChangeConflict[];
}

export type ExecutionStatus = 'pending' | 'running' | 'paused_for_conflict' | 'completed' | 'canceled';

export interface ExecutionState {
  status: ExecutionStatus;
  queue: ChangeQueue;
  appliedChanges: AppliedChange[];
  conflicts: ChangeConflict[];
  currentStep: number; // Index of the current operation being processed
}

/**
 * Defines the contract for a UI layer to interact with the execution process.
 */
export interface IInteractionLayer {
  /**
   * Called when the execution needs the user to resolve a conflict.
   * @param conflict The conflict that needs resolution.
   * @returns A promise that resolves to 'skip', 'retry', or 'abort'.
   */
  resolveConflict(conflict: ChangeConflict): Promise<'skip' | 'retry' | 'abort'>;

  /**
   * Called to update the UI with the current progress.
   * @param state The current execution state.
   */
  updateProgress(state: ExecutionState): void;

  /**
   * Asks the user to select a search result from a list.
   * @param results The list of search results.
   * @returns A promise that resolves to the selected search result or null if canceled.
   */
  selectSearchResult(results: SearchResult[]): Promise<SearchResult | null>;
}

export interface SystemConfig {
  parser: ChangeParserOptions;
  scrolling: ScrollConfig;
}

export interface SearchResult {
  title: string;
  link: string;
  snippet: string;
}

export interface IWebSearcher {
  search(query: string): Promise<SearchResult[]>;
}

export interface ISolutionExtractor {
  extract(url:string): Promise<string>;
}

export type ModelEntropy = 'good' | 'bad';

export interface EntropyPayload {
  modelId: string;
  entropy: ModelEntropy;
  details: any; 
}

export interface ModelFeedback {
  recordEntropy(payload: EntropyPayload): void;
}

export type PuzzleStatus = 'unsolved' | 'solved' | 'broken';

export interface Puzzle {
  id: string;
  filePath: string;
  range: Range;
  description: string;
  status: PuzzleStatus;
  difficulty: number;
  reward: number;
  nextPuzzleId?: string;
  solutionHash?: string;
}

export interface BytiseModifier {
  analyze(filePath: string, content: string): Puzzle[];
}

export type PuzzleEvent = 'puzzle_solved' | 'puzzle_postponed';

export interface PuzzleEntropyPayload extends EntropyPayload {
  puzzleId: string;
  event: PuzzleEvent;
}

export interface SolvedPuzzle {
  puzzleId: string;
  solutionCode: string;
  solutionHash: string;
  timestamp: Date;
}

/**
 * Represents a single cryptographic piece of the QR pattern.
 * Each piece requires a valid hash to be considered 'filled'.
 */
export interface QrHashPiece {
  /** The (x, y) coordinate of this piece in the QR pattern grid. */
  position: [number, number];

  /** The hash required to fill this piece. Initially null. */
  requiredHash: string | null;

  /** The hash provided by the model's token generation process. */
  providedHash: string | null;

  /** Whether the provided hash matches the required hash. */
  isFilled: boolean;
}

/**
 * Represents the entire QR pattern that gates model completion.
 * The task is only complete when all pieces are filled.
 */
export interface QrCompletionPattern {
  /** The dimensions of the QR grid (width, height). */
  dimensions: [number, number];

  /** A 2D array representing the grid of hash pieces. */
  grid: QrHashPiece[][];

  /** The overall completion percentage (0-100). */
  completionRate: number;
}

/**
 * Represents the state of a model after the QR hash logic has been 'injected'.
 * This tracks the model's progress toward filling the QR pattern.
 */
export interface InjectedModelState {
  /** The unique QR pattern associated with the current task. */
  qrPattern: QrCompletionPattern;

  /** A log of tokens received by the model. */
  tokensReceived: number;

  /** A log of tokens generated by the model. */
  tokensGenerated: number;
}

