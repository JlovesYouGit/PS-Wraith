import { IIDEApi } from './ide/api';
import { IDENavigator } from './IDENavigator';
import { EditOperation, LockResult, Position } from './types';

/**
 * Provides a mechanism to lock onto a specific code position and verify its content
 * before applying a change.
 */
export class InlineLock {
  constructor(
    private readonly navigator: IDENavigator,
    private readonly ide: IIDEApi
  ) {}

  /**
   * Attempts to lock onto the position specified by an edit operation and verify the content.
   * @param operation The edit operation to lock and verify.
   * @returns A promise that resolves to a LockResult.
   */
  public async lockPosition(operation: EditOperation): Promise<LockResult> {
    // 1. Navigate to the start of the range for the operation
    const navResult = await this.navigator.navigateTo({
      filePath: operation.filePath,
      position: operation.range.start,
    });

    if (!navResult.success) {
      return {
        isLocked: false,
        position: operation.range.start,
        contentMatch: false,
        conflictDetails: {
          expected: operation.oldContent,
          actual: `Navigation failed: ${navResult.error}`,
          similarity: 0,
        },
      };
    }

    // 2. Get the current content of the file to verify the lock
    const fileContent = await this.ide.getFileContent(operation.filePath);
    const lines = fileContent.split('\n');
    const { start, end } = operation.range;

    // Extract the actual content from the specified range
    let actualContent = '';
    if (start.line === end.line) {
      actualContent = lines[start.line].substring(start.character, end.character);
    } else {
      // Handle multi-line ranges
      const firstLine = lines[start.line].substring(start.character);
      const lastLine = lines[end.line].substring(0, end.character);
      const middleLines = lines.slice(start.line + 1, end.line);
      actualContent = [firstLine, ...middleLines, lastLine].join('\n');
    }

    // 3. Verify the content
    const { match, similarity } = this.verifyContent(
      operation.oldContent,
      actualContent
    );

    if (!match) {
      return {
        isLocked: true, // We are at the position, but content doesn't match
        position: start,
        contentMatch: false,
        conflictDetails: {
          expected: operation.oldContent,
          actual: actualContent,
          similarity,
        },
      };
    }

    // 4. Success: Position is locked and content matches
    return {
      isLocked: true,
      position: start,
      contentMatch: true,
    };
  }

  /**
   * Verifies if the actual content matches the expected content and calculates a similarity score.
   * @param expected The expected content.
   * @param actual The actual content from the editor.
   * @returns An object with a boolean 'match' and a 'similarity' score (0 to 1).
   */
  public verifyContent(
    expected: string,
    actual: string
  ): { match: boolean; similarity: number } {
    if (expected === actual) {
      return { match: true, similarity: 1 };
    }

    // Simple similarity calculation (e.g., Levenshtein distance based)
    const longer = expected.length > actual.length ? expected : actual;
    const shorter = expected.length > actual.length ? actual : expected;
    const distance = this.calculateLevenshteinDistance(longer, shorter);
    const similarity = (longer.length - distance) / longer.length;

    return { match: false, similarity };
  }

  /**
   * Calculates the Levenshtein distance between two strings.
   */
  private calculateLevenshteinDistance(a: string, b: string): number {
    const matrix = Array(b.length + 1)
      .fill(null)
      .map(() => Array(a.length + 1).fill(null));

    for (let i = 0; i <= a.length; i++) {
      matrix[0][i] = i;
    }
    for (let j = 0; j <= b.length; j++) {
      matrix[j][0] = j;
    }

    for (let j = 1; j <= b.length; j++) {
      for (let i = 1; i <= a.length; i++) {
        const indicator = a[i - 1] === b[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1, // deletion
          matrix[j - 1][i] + 1, // insertion
          matrix[j - 1][i - 1] + indicator // substitution
        );
      }
    }

    return matrix[b.length][a.length];
  }
}
