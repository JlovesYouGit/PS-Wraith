import { IIDEApi } from './ide/api';
import { InlineLock } from './InlineLock';
import { ChangeQueue, EditOperation, ApplicationResult, AppliedChange, ChangeConflict, IInteractionLayer, ExecutionState, PuzzleEntropyPayload, SolvedPuzzle } from './types';
import { EntropyManager } from './EntropyManager';
import * as crypto from 'crypto';
import { isValidSha256 } from './utils';

/**
 * Orchestrates the process of applying a queue of changes to the codebase interactively.
 */
export class FastChangeApplicator {
  constructor(
    private readonly lock: InlineLock,
    private readonly ide: IIDEApi,
    private readonly interactionLayer: IInteractionLayer,
    private readonly feedback: EntropyManager
  ) {}

  /**
   * Applies all changes in a given ChangeQueue, handling conflicts interactively.
   * @param state The current execution state.
   * @returns A promise that resolves to the final ApplicationResult.
   */
  public async applyChanges(state: ExecutionState): Promise<ApplicationResult> {
    let operationIndex = state.currentStep;

    while (operationIndex < state.queue.totalOperations) {
      const operation = this.getOperationByIndex(state.queue, operationIndex);
      if (!operation) break; // Should not happen

      state.currentStep = operationIndex;
      this.interactionLayer.updateProgress(state);

      let attempt = 0;
      let successful = false;

      while (attempt < 2 && !successful) {
        const lockResult = await this.lock.lockPosition(operation);

        if (!lockResult.isLocked || !lockResult.contentMatch) {
          const conflict: ChangeConflict = {
            operation,
            message: !lockResult.isLocked ? `Navigation failed: ${lockResult.conflictDetails?.actual}` : 'Content mismatch.',
            details: lockResult.conflictDetails,
          };
          state.conflicts.push(conflict);
          state.status = 'paused_for_conflict';
          this.interactionLayer.updateProgress(state);

          const userAction = await this.interactionLayer.resolveConflict(conflict);

          if (userAction === 'abort') {
            state.status = 'canceled';
            this.interactionLayer.updateProgress(state);
            return this.buildResult(state);
          } else if (userAction === 'skip') {
            break; // Exit the attempt loop and move to the next operation
          } else { // 'retry'
            attempt++;
            continue; // Retry locking and applying
          }
        }

        try {
          // --- Puzzle Validation BEFORE applying change ---
          if (operation.oldContent.includes('// PUZZLE:') && !operation.newContent.includes('// PUZZLE:')) {
            const puzzleId = crypto.createHash('md5').update(`${operation.filePath}:${operation.range.start.line}`).digest('hex');
            const puzzle = this.feedback.getPuzzle(puzzleId);

            if (puzzle) {
              const solutionHash = crypto.createHash('sha256').update(operation.newContent).digest('hex');

              if (!isValidSha256(solutionHash)) {
                puzzle.status = 'broken';
                this.feedback.recordEntropy({ modelId: 'system', entropy: 'bad', details: 'Malformed solution hash' });
                console.error(`Puzzle ${puzzleId} has a malformed solution hash. Skipping operation.`);
                continue; // Skip to next operation
              }

              if (!this.feedback.arePrerequisitesMet(puzzleId)) {
                puzzle.status = 'broken';
                this.feedback.recordEntropy({ modelId: 'system', entropy: 'bad', details: 'Puzzle prerequisites not met' });
                console.error(`Prerequisites for puzzle ${puzzleId} are not met. Skipping operation.`);
                continue; // Skip to next operation
              }
            }
          }

          // --- Apply Change ---
          await this.ide.replaceText(operation.filePath, operation.range, operation.newContent);
          state.appliedChanges.push({ operation, timestamp: new Date() });
          successful = true;

          // --- Post-Application Puzzle Logic ---
          if (operation.oldContent.includes('// PUZZLE:') && !operation.newContent.includes('// PUZZLE:')) {
            const puzzleId = crypto.createHash('md5').update(`${operation.filePath}:${operation.range.start.line}`).digest('hex');
            const puzzle = this.feedback.getPuzzle(puzzleId);
            if (puzzle && puzzle.status !== 'broken') { // Re-check status
              const solutionHash = puzzle.solutionHash! // Already calculated and validated
              
              const solvedPuzzle: SolvedPuzzle = {
                puzzleId,
                solutionCode: operation.newContent,
                solutionHash,
                timestamp: new Date(),
              };
              this.feedback.saveSolvedPuzzle(solvedPuzzle);

              const puzzlePayload: PuzzleEntropyPayload = {
                puzzleId,
                modelId: 'user_action',
                entropy: 'good',
                event: 'puzzle_solved',
                details: 'Puzzle solved by applying change',
              };
              this.feedback.recordPuzzleEvent(puzzlePayload);

              console.log(`Puzzle ${puzzleId} solved. Solution hash: ${solutionHash}`);
            }
          }
        } catch (error: any) {
          // This is treated as a conflict as well
          const conflict: ChangeConflict = {
            operation,
            message: `IDE Error: ${error.message}`,
          };
          // Handle this just like the content mismatch
          // (This part could be refactored to reduce duplication)
        }
      }

      operationIndex++;
    }

    state.status = 'completed';
    this.interactionLayer.updateProgress(state);
    return this.buildResult(state);
  }

  private getOperationByIndex(queue: ChangeQueue, index: number): EditOperation | null {
    let currentIndex = 0;
    for (const batch of queue.batches) {
      if (index < currentIndex + batch.operations.length) {
        return batch.operations[index - currentIndex];
      }
      currentIndex += batch.operations.length;
    }
    return null;
  }

  private buildResult(state: ExecutionState): ApplicationResult {
    return {
      success: state.conflicts.length === 0 && state.status === 'completed',
      appliedChanges: state.appliedChanges,
      conflicts: state.conflicts,
    };
  }
}
