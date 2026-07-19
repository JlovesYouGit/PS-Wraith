import { ApplicationResult } from './types';

/**
 * Manages the history of all code change executions.
 */
export class ExecutionHistoryManager {
  private executionHistory: ApplicationResult[] = [];

  /**
   * Records the result of a completed execution.
   * @param result The result of the application process.
   */
  public recordExecution(result: ApplicationResult): void {
    this.executionHistory.push(result);
  }

  /**
   * Retrieves the entire history of executions.
   * @returns An array of all recorded ApplicationResult objects.
   */
  public getHistory(): ApplicationResult[] {
    return [...this.executionHistory];
  }

  /**
   * Clears the entire execution history.
   */
  public clearHistory(): void {
    this.executionHistory = [];
  }

  /**
   * Gets the most recent execution from the history.
   * @returns The last ApplicationResult, or undefined if history is empty.
   */
  public getLatestExecution(): ApplicationResult | undefined {
    return this.executionHistory[this.executionHistory.length - 1];
  }
}
