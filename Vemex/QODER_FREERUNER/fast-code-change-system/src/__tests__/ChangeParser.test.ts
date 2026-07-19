import { ChangeParser } from '../ChangeParser';
import * as path from 'path';

describe('ChangeParser', () => {
  let parser: ChangeParser;

  beforeEach(() => {
    parser = new ChangeParser();
  });

  describe('parse', () => {
    it('should parse a simple change request', () => {
      const changeRequest = `
        --- a/src/file1.ts
        +++ b/src/file1.ts
        @@ -1,5 +1,5 @@
         // Some code
        -const oldValue = 42;
        +const newValue = 24;
         // More code
      `;

      const result = parser.parse(changeRequest);

      expect(result.totalOperations).toBe(1);
      expect(result.batches.length).toBe(1);
      expect(result.batches[0].filePath).toContain('src/file1.ts');
      expect(result.batches[0].operations[0].operationType).toBe('replace');
      expect(result.batches[0].operations[0].oldContent).toContain('oldValue');
      expect(result.batches[0].operations[0].newContent).toContain('newValue');
    });

    it('should handle multiple changes in the same file', () => {
      const changeRequest = `
        --- a/src/file1.ts
        +++ b/src/file1.ts
        @@ -1,5 +1,7 @@
         // Some code
        -const oldValue = 42;
        +const newValue = 24;
        +
+        // New comment
-        // Old comment
      `;

      const result = parser.parse(changeRequest);
      expect(result.totalOperations).toBe(2);
    });

    it('should handle changes in multiple files', () => {
      const changeRequest = `
        --- a/src/file1.ts
        +++ b/src/file1.ts
        @@ -1,5 +1,5 @@
         // Some code
        -const oldValue = 42;
        +const newValue = 24;
         // More code
        --- a/src/file2.ts
        +++ b/src/file2.ts
        @@ -1,5 +1,5 @@
         // Another file
        -const x = 1;
        +const x = 2;
      `;

      const result = parser.parse(changeRequest);
      expect(result.totalOperations).toBe(2);
      expect(result.batches.length).toBe(2);
    });
  });

  describe('optimizeQueue', () => {
    it('should merge adjacent insertions', () => {
      const parser = new ChangeParser();
      const operations = [
        {
          id: '1',
          filePath: 'test.js',
          range: { start: { line: 1, character: 0 }, end: { line: 1, character: 0 } },
          operationType: 'insert' as const,
          oldContent: '',
          newContent: 'line1\n',
          priority: 1
        },
        {
          id: '2',
          filePath: 'test.js',
          range: { start: { line: 1, character: 0 }, end: { line: 1, character: 0 } },
          operationType: 'insert' as const,
          oldContent: '',
          newContent: 'line2\n',
          priority: 1
        }
      ];

      const queue = {
        batches: [{
          filePath: 'test.js',
          operations,
          totalLines: 2
        }],
        totalOperations: 2,
        estimatedDuration: 0
      };

      const optimized = parser.optimizeQueue(queue);
      expect(optimized.totalOperations).toBe(1);
      expect(optimized.batches[0].operations[0].newContent).toBe('line1\nline2\n');
    });
  });

  describe('validateFiles', () => {
    it('should validate file existence', async () => {
      const parser = new ChangeParser({ validateFiles: true });
      const queue = {
        batches: [{
          filePath: path.join(__dirname, 'nonexistent.txt'),
          operations: [{
            id: '1',
            filePath: path.join(__dirname, 'nonexistent.txt'),
            range: { start: { line: 1, character: 0 }, end: { line: 1, character: 5 } },
            operationType: 'insert' as const,
            oldContent: '',
            newContent: 'test',
            priority: 1
          }],
          totalLines: 1
        }],
        totalOperations: 1,
        estimatedDuration: 0
      };

      const result = await parser.validateFiles(queue);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });
});
