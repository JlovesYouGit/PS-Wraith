import { FastChangeApplicator } from '../FastChangeApplicator';
import { InlineLock } from '../InlineLock';
import { IDENavigator } from '../IDENavigator';
import { IIDEApi, IActiveTextEditor } from '../ide/api';
import { ChangeQueue, EditOperation, Range, IInteractionLayer, ChangeConflict, ExecutionState } from '../types';

// A more complete MockIDE for testing the applicator
class MockInteractionLayer implements IInteractionLayer {
  public lastConflict: ChangeConflict | null = null;
  private nextAction: 'skip' | 'retry' | 'abort' = 'skip';

  setNextAction(action: 'skip' | 'retry' | 'abort') {
    this.nextAction = action;
  }

  async resolveConflict(conflict: ChangeConflict): Promise<'skip' | 'retry' | 'abort'> {
    this.lastConflict = conflict;
    return this.nextAction;
  }

  updateProgress(state: ExecutionState): void {}
}

class MockIDE implements IIDEApi {
  public files: Map<string, string> = new Map();
  public lastReplacedText: { filePath: string; range: Range; newText: string } | null = null;
  private shouldThrowOnReplace = false;

  constructor(initialFiles: { [filePath: string]: string }) {
    for (const filePath in initialFiles) {
      this.files.set(filePath, initialFiles[filePath]);
    }
  }

  async openFile(filePath: string): Promise<IActiveTextEditor> {
    if (this.files.has(filePath)) {
      return {
        filePath,
        content: this.files.get(filePath)!,
        selection: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
        revealRange: () => {},
      };
    }
    throw new Error(`File not found: ${filePath}`);
  }

  async getFileContent(filePath: string): Promise<string> {
    return this.files.get(filePath) || '';
  }

  async replaceText(filePath: string, range: Range, newText: string): Promise<void> {
    if (this.shouldThrowOnReplace) {
      throw new Error('IDE Error: Failed to replace text.');
    }
    this.lastReplacedText = { filePath, range, newText };
    // Simulate the text replacement for future checks
    const content = this.files.get(filePath) || '';
    const lines = content.split('\n');
    const { start, end } = range;
    const prefix = lines[start.line].substring(0, start.character);
    const suffix = lines[end.line].substring(end.character);
    lines[start.line] = prefix + newText + suffix;
    this.files.set(filePath, lines.join('\n'));
  }

  async fileExists(filePath: string): Promise<boolean> {
    return this.files.has(filePath);
  }

  forceErrorOnReplace(shouldThrow: boolean) {
    this.shouldThrowOnReplace = shouldThrow;
  }
}

describe('FastChangeApplicator', () => {
  let mockIde: MockIDE;
  let applicator: FastChangeApplicator;
  let mockInteractionLayer: MockInteractionLayer;
  let initialState: ExecutionState;

  beforeEach(() => {
    mockIde = new MockIDE({ '/test/apply.ts': 'const version = 1;' });
    const navigator = new IDENavigator(mockIde);
    const inlineLock = new InlineLock(navigator, mockIde);
    mockInteractionLayer = new MockInteractionLayer();
    applicator = new FastChangeApplicator(inlineLock, mockIde, mockInteractionLayer);

    const operation: EditOperation = {
      id: 'op1',
      filePath: '/test/apply.ts',
      range: { start: { line: 0, character: 16 }, end: { line: 0, character: 17 } },
      operationType: 'replace',
      oldContent: '1',
      newContent: '2',
      priority: 1,
    };

    const queue: ChangeQueue = {
      batches: [{ filePath: '/test/apply.ts', operations: [operation], totalLines: 1 }],
      totalOperations: 1,
      estimatedDuration: 100,
    };

    initialState = {
      status: 'pending',
      queue,
      appliedChanges: [],
      conflicts: [],
      currentStep: 0,
    };
  });

  it('should apply a change successfully', async () => {
    const result = await applicator.applyChanges(initialState);

    expect(result.success).toBe(true);
    expect(result.appliedChanges.length).toBe(1);
    expect(result.conflicts.length).toBe(0);
    expect(mockIde.lastReplacedText?.newText).toBe('2');
    expect(mockIde.files.get('/test/apply.ts')).toBe('const version = 2;');
  });

  it('should report a conflict if content does not match', async () => {
    initialState.queue.batches[0].operations[0].oldContent = '99'; // Mismatched content
    mockInteractionLayer.setNextAction('skip');

    const result = await applicator.applyChanges(initialState);

    expect(result.success).toBe(false);
    expect(result.appliedChanges.length).toBe(0);
    expect(result.conflicts.length).toBe(1);
    expect(result.conflicts[0].message).toContain('Content mismatch');
  });

  it('should report a conflict if replaceText throws an error', async () => {
    mockIde.forceErrorOnReplace(true);
    mockInteractionLayer.setNextAction('abort'); // Tell the UI to abort on this error

    const result = await applicator.applyChanges(initialState);

    expect(result.success).toBe(false);
    expect(result.appliedChanges.length).toBe(0);
    expect(result.conflicts.length).toBe(1);
    expect(result.conflicts[0].message).toContain('Failed to apply edit');
  });
});
