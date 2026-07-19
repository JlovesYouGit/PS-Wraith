import { ModelFeedback, EntropyPayload, Puzzle, PuzzleStatus, PuzzleEntropyPayload, PuzzleEvent, SolvedPuzzle } from './types';

interface EntropyStats {
  good: number;
  bad: number;
}

/**
 * Manages the entropy feedback for different models and puzzles.
 */
export class EntropyManager implements ModelFeedback {
  private entropyData: Map<string, EntropyStats> = new Map();
  private puzzles: Map<string, Puzzle> = new Map();
  private solvedPuzzles: Map<string, SolvedPuzzle> = new Map();
  private puzzleChain: Map<string, string> = new Map(); // Maps nextPuzzleId -> currentPuzzleId

  public recordEntropy(payload: EntropyPayload): void {
    const { modelId, entropy } = payload;
    if (!this.entropyData.has(modelId)) {
      this.entropyData.set(modelId, { good: 0, bad: 0 });
    }

    const stats = this.entropyData.get(modelId)!;
    stats[entropy]++;
    console.log(`Recorded '${entropy}' entropy for model: ${modelId}`, stats);
  }

  public recordPuzzleEvent(payload: PuzzleEntropyPayload): void {
    const { puzzleId, event, modelId } = payload;
    const puzzle = this.puzzles.get(puzzleId);

    if (!puzzle) {
      console.error(`Puzzle with id ${puzzleId} not found`);
      return;
    }

    if (event === 'puzzle_solved') {
      puzzle.status = 'solved';
      const stats = this.entropyData.get(modelId)!;
      stats.good += puzzle.reward;
      console.log(`'good' entropy awarded for model: ${modelId}`, stats);

      if (puzzle.nextPuzzleId) {
        const nextPuzzle = this.puzzles.get(puzzle.nextPuzzleId);
        if (nextPuzzle) {
          // Unlock the next puzzle (e.g., by changing its status or notifying the user)
          console.log(`Puzzle ${puzzle.nextPuzzleId} is now unlocked.`);
        }
      }
    } else if (event === 'puzzle_postponed') {
      puzzle.status = 'broken';
      // Deduct good entropy
      const stats = this.entropyData.get(modelId);
      if (stats && stats.good > 0) {
        stats.good--;
      } else if (stats) {
        stats.bad++;
      }
      console.log(`'good' entropy deducted for model: ${modelId}`, stats);
    }
  }

  public registerPuzzle(puzzle: Puzzle): void {
    this.puzzles.set(puzzle.id, puzzle);
    if (puzzle.nextPuzzleId) {
      this.puzzleChain.set(puzzle.nextPuzzleId, puzzle.id);
    }
  }

  public getPuzzle(puzzleId: string): Puzzle | undefined {
    return this.puzzles.get(puzzleId);
  }

  public getEntropyScore(modelId: string): number {
    if (!this.entropyData.has(modelId)) {
      return 0; // Neutral score for unknown models
    }
    const { good, bad } = this.entropyData.get(modelId)!;
    return good - bad;
  }

  public saveSolvedPuzzle(solvedPuzzle: SolvedPuzzle): void {
    this.solvedPuzzles.set(solvedPuzzle.puzzleId, solvedPuzzle);
  }

  public getBrokenPuzzles(): Puzzle[] {
    const brokenPuzzles: Puzzle[] = [];
    for (const puzzle of this.puzzles.values()) {
      if (puzzle.status === 'broken') {
        brokenPuzzles.push(puzzle);
      }
    }
    return brokenPuzzles;
  }

  public arePrerequisitesMet(puzzleId: string): boolean {
    let currentId: string | undefined = this.puzzleChain.get(puzzleId);
    while (currentId) {
      const puzzle = this.puzzles.get(currentId);
      if (!puzzle || puzzle.status !== 'solved') {
        return false; // A prerequisite is not met
      }
      currentId = this.puzzleChain.get(currentId);
    }
    return true; // All prerequisites are met
  }

  public getRankedScores(): [string, number][] {
    const scores: [string, number][] = Array.from(this.entropyData.entries()).map(([modelId, stats]) => {
        const score = this.getEntropyScore(modelId);
        return [modelId, score];
    });

    return scores.sort((a, b) => b[1] - a[1]); // Sort descending by score
  }
}
