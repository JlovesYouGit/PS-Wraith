import { IDENavigator } from '../IDENavigator';
import { IIDEApi, IActiveTextEditor } from '../ide/api';
import { NavigationTarget, Range } from '../types';

/**
 * A mock implementation of the IIDEApi for testing purposes.
 */
class MockIDE implements IIDEApi {
  private editors: Map<string, IActiveTextEditor> = new Map();
  public lastRevealedRange: Range | null = null;

  constructor(initialFiles: { [filePath: string]: string }) {
    for (const filePath in initialFiles) {
      this.editors.set(filePath, {
        filePath,
        content: initialFiles[filePath],
        selection: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
        revealRange: (range: Range) => {
          this.lastRevealedRange = range;
        },
      });
    }
  }

  async openFile(filePath: string): Promise<IActiveTextEditor> {
    if (this.editors.has(filePath)) {
      return this.editors.get(filePath)!;
    }
    throw new Error(`File not found: ${filePath}`);
  }

  async replaceText(filePath: string, range: Range, newText: string): Promise<void> {
    // Not needed for this test file
  }

  async getFileContent(filePath: string): Promise<string> {
    if (this.editors.has(filePath)) {
      return this.editors.get(filePath)!.content;
    }
    throw new Error(`File not found: ${filePath}`);
  }

  async fileExists(filePath: string): Promise<boolean> {
    return this.editors.has(filePath);
  }
}

describe('IDENavigator', () => {
  let mockIde: MockIDE;
  let navigator: IDENavigator;

  beforeEach(() => {
    mockIde = new MockIDE({
      '/test/file1.ts': 'line 1\nline 2\nline 3',
      '/test/file2.ts': 'another file content',
    });
    navigator = new IDENavigator(mockIde);
  });

  it('should open a file and navigate to a position', async () => {
    const target: NavigationTarget = {
      filePath: '/test/file1.ts',
      position: { line: 2, character: 5 },
    };

    const result = await navigator.navigateTo(target);

    expect(result.success).toBe(true);
    expect(result.currentPosition.filePath).toBe('/test/file1.ts');
    expect(result.currentPosition.position).toEqual({ line: 2, character: 5 });
    expect(mockIde.lastRevealedRange?.start).toEqual({ line: 2, character: 5 });
  });

  it('should switch between files and navigate', async () => {
    // Navigate to first file
    await navigator.navigateTo({
      filePath: '/test/file1.ts',
      position: { line: 1, character: 0 },
    });

    // Navigate to second file
    const target2: NavigationTarget = {
      filePath: '/test/file2.ts',
      position: { line: 0, character: 10 },
    };
    const result2 = await navigator.navigateTo(target2);

    expect(result2.success).toBe(true);
    expect(result2.currentPosition.filePath).toBe('/test/file2.ts');
    expect(result2.currentPosition.position).toEqual({ line: 0, character: 10 });
  });

  it('should return an error for a non-existent file', async () => {
    const target: NavigationTarget = {
      filePath: '/test/nonexistent.ts',
      position: { line: 0, character: 0 },
    };

    const result = await navigator.navigateTo(target);

    expect(result.success).toBe(false);
    expect(result.error).toContain('File not found');
  });
});
