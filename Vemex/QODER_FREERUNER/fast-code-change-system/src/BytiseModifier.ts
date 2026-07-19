import { BytiseModifier, Puzzle, Range } from './types';
import * as crypto from 'crypto';

/**
 * An advanced implementation of the BytiseModifier.
 * It scans for puzzles in JSON-formatted comments.
 */
export class BytiseModifierImpl implements BytiseModifier {
  public analyze(filePath: string, content: string): Puzzle[] {
    const puzzles: Puzzle[] = [];
    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const match = line.match(/\/\/\s*PUZZLE:\s*({.*});/);

      if (match) {
        try {
          const puzzleData = JSON.parse(match[1]);
          const range: Range = {
            start: { line: i, character: 0 },
            end: { line: i, character: line.length },
          };

          const id = crypto.createHash('md5').update(`${filePath}:${i}`).digest('hex');

          puzzles.push({
            id,
            filePath,
            range,
            description: puzzleData.desc || 'No description',
            status: 'unsolved',
            difficulty: puzzleData.difficulty || 1,
            reward: puzzleData.reward || 10,
            nextPuzzleId: puzzleData.next,
          });
        } catch (error) {
          console.error(`Failed to parse puzzle JSON on line ${i + 1} of ${filePath}:`, error);
        }
      }
    }

    return puzzles;
  }
}
