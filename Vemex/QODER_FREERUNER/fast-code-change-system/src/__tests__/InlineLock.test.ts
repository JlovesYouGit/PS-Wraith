import { InlineLock } from '../InlineLock';
import { IDENavigator } from '../IDENavigator';
import { IIDEApi, IActiveTextEditor } from '../ide/api';
import { EditOperation, Range } from '../types';

// Re-using the MockIDE from IDENavigator.test.ts by putting it in a shared test utility file would be better,
// but for simplicity, it's duplicated here.
class MockIDE implements IIDEApi {
  private editors: Map<string, IActiveTextEditor> = new Map();

  constructor(initialFiles: { [filePath: string]: string }) {
    for (const filePath in initialFiles) {
      this.editors.set(filePath, {
        filePath,
        content: initialFiles[filePath],
        selection: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
        revealRange: (range: Range) => {},
      });
    }
  }

  async openFile(filePath: string): Promise<IActiveTextEditor> {
    if (this.editors.has(filePath)) {
      return this.editors.get(filePath)!;
    }
    throw new Error(`File not found: ${filePath}`);
  }

  async getFileContent(filePath: string): Promise<string> {
    if (this.editors.has(filePath)) {
      return this.editors.get(filePath)!.content;
    }
    throw new Error(`File not found: ${filePath}`);
  }

  async replaceText(filePath: string, range: Range, newText: string): Promise<void> {}
  async fileExists(filePath: string): Promise<boolean> {
    return this.editors.has(filePath);
  }
}

describe('InlineLock', () => {
  let mockIde: MockIDE;
  let navigator: IDENavigator;
  let inlineLock: InlineLock;

  beforeEach(() => {
    mockIde = new MockIDE({
      '/test/file.ts': 'const hello = "world";\nconst value = 123;\n',
    });
    navigator = new IDENavigator(mockIde);
    inlineLock = new InlineLock(navigator, mockIde);
  });

  it('should successfully lock when content matches', async () => {
    const operation: EditOperation = {
      id: '1',
      filePath: '/test/file.ts',
      range: { start: { line: 1, character: 6 }, end: { line: 1, character: 11 } },
      operationType: 'replace',
      oldContent: 'value',
      newContent: 'newValue',
      priority: 1,
    };

    const result = await inlineLock.lockPosition(operation);

    expect(result.isLocked).toBe(true);
    expect(result.contentMatch).toBe(true);
  });

  it('should fail to lock when content does not match', async () => {
    const operation: EditOperation = {
      id: '1',
      filePath: '/test/file.ts',
      range: { start: { line: 1, character: 6 }, end: { line: 1, character: 11 } },
      operationType: 'replace',
      oldContent: 'wrongContent',
      newContent: 'newValue',
      priority: 1,
    };

    const result = await inlineLock.lockPosition(operation);

    expect(result.isLocked).toBe(true); // Locked on position, but content mismatch
    expect(result.contentMatch).toBe(false);
    expect(result.conflictDetails?.expected).toBe('wrongContent');
    expect(result.conflictDetails?.actual).toBe('value');
  });

  it('should return a navigation error if the file cannot be opened', async () => {
    const operation: EditOperation = {
      id: '1',
      filePath: '/test/nonexistent.ts',
      range: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
      operationType: 'insert',
      oldContent: '',
      newContent: 'test',
      priority: 1,
    };

    const result = await inlineLock.lockPosition(operation);

    expect(result.isLocked).toBe(false);
    expect(result.conflictDetails?.actual).toContain('Navigation failed');
  });

  describe('verifyContent', () => {
    it('should return match for identical strings', () => {
      const { match, similarity } = inlineLock.verifyContent('abc', 'abc');
      expect(match).toBe(true);
      expect(similarity).toBe(1);
    });

    it('should return no match and a similarity score for different strings', () => {
      const { match, similarity } = inlineLock.verifyContent('apple', 'apply');
      expect(match).toBe(false);
      expect(similarity).toBeCloseTo(0.8); // 'apply' is 4/5 of 'apple'
    });
  });
});
