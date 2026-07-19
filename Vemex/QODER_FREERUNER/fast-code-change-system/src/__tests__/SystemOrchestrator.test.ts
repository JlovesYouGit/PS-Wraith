import { SystemOrchestrator } from '../SystemOrchestrator';
import { IIDEApi, IActiveTextEditor } from '../ide/api';
import { Range, IInteractionLayer, ChangeConflict, ExecutionState } from '../types';

// Mock for the interaction layer
class MockInteractionLayer implements IInteractionLayer {
  async resolveConflict(conflict: ChangeConflict): Promise<'skip' | 'retry' | 'abort'> {
    return 'skip'; // Default to skipping conflicts in this test
  }
  updateProgress(state: ExecutionState): void {}
}

// A comprehensive mock IDE for the end-to-end test
class MockIDE implements IIDEApi {
  public files: Map<string, string> = new Map();

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
}

describe('SystemOrchestrator', () => {
  let mockIde: MockIDE;
  let orchestrator: SystemOrchestrator;
  const changeRequest = `
--- a/src/file.ts
+++ b/src/file.ts
@@ -1,3 +1,4 @@
 const a = 1;
-const b = 2;
+const b = 99;
 const c = 3;
+const d = 4;
`;

  beforeEach(() => {
    mockIde = new MockIDE({ '/src/file.ts': 'const a = 1;\nconst b = 2;\nconst c = 3;' });
    const mockInteractionLayer = new MockInteractionLayer();
    orchestrator = new SystemOrchestrator(mockIde, mockInteractionLayer, {});
  });

  it('should prepare a change queue successfully', async () => {
    const queue = await orchestrator.prepareChangeQueue(changeRequest);
    expect(queue).not.toBeNull();
    expect(queue!.totalOperations).toBe(2);
    expect(queue!.batches[0].filePath).toBe('/src/file.ts');
  });

  it('should execute the full change process', async () => {
    const queue = await orchestrator.prepareChangeQueue(changeRequest);
    expect(queue).not.toBeNull();

    const scrollSteps: number[] = [];
    const onScrollStep = async (line: number) => {
      scrollSteps.push(line);
    };

    const result = await orchestrator.execute(queue!, onScrollStep);

    expect(result.success).toBe(true);
    expect(result.appliedChanges.length).toBe(2);
    expect(result.conflicts.length).toBe(0);
    expect(scrollSteps.length).toBeGreaterThan(2); // Check that scrolling happened

    const finalContent = mockIde.files.get('/src/file.ts');
    expect(finalContent).toContain('const b = 99;');
    expect(finalContent).toContain('const d = 4;');
  });

  it('should return null if file validation fails', async () => {
    const invalidRequest = `
--- a/src/nonexistent.ts
+++ b/src/nonexistent.ts
@@ -1,1 +1,1 @@
-a
+b
`;
    const queue = await orchestrator.prepareChangeQueue(invalidRequest);
    expect(queue).toBeNull();
  });
});
