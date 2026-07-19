import { 
  EditOperation, 
  ChangeBatch, 
  ChangeQueue, 
  ValidationResult,
  ChangeParserOptions,
  Position,
  Range
} from './types';

/**
 * Parses change requests into structured edit operations and manages the change queue.
 */
export class ChangeParser {
  private options: Required<ChangeParserOptions>;
  
  constructor(options: Partial<ChangeParserOptions> = {}) {
    this.options = {
      validateFiles: true,
      groupByFile: true,
      sortByLineNumber: true,
      ...options
    };
  }

  /**
   * Parses a change request string into a structured ChangeQueue
   * @param changeRequest The raw change request string
   * @returns A structured ChangeQueue
   */
  public parse(changeRequest: string): ChangeQueue {
    if (changeRequest.startsWith('#rulers#')) {
      return this.handleQoderProtocol(changeRequest);
    }
    const lines = changeRequest.split('\n');
    const operations: EditOperation[] = [];
    
    // Simple regex patterns for change detection
    const filePathPattern = /^\s*[+-]{3}\s+(?:"(.+)"|([^\s]+))\s*$/;
    const changePattern = /^\s*@@\s*[-+]\d+(?:,\d+)?\s+[+-]\d+(?:,\d+)?\s*@@(?:\s+(.*))?$/;
    const additionPattern = /^\+([^+].*)?$/;
    const deletionPattern = '^-([^-].*)?$';

    let currentFile: string | null = null;
    let currentLine = 0;
    let lineOffset = 0;

    for (const line of lines) {
      // Check for file path
      const fileMatch = line.match(filePathPattern);
      if (fileMatch) {
        currentFile = fileMatch[1] || fileMatch[2];
        lineOffset = 0;
        continue;
      }

      // Check for change block header
      const changeMatch = line.match(changePattern);
      if (changeMatch && currentFile) {
        const lineInfo = changeMatch[0].match(/[+-]\d+/g);
        if (lineInfo && lineInfo.length >= 2) {
          currentLine = parseInt(lineInfo[1].substring(1)) - 1; // Convert to 0-based
          lineOffset = 0;
        }
        continue;
      }

      // Process actual changes
      if (currentFile) {
        if (line.match(additionPattern)) {
          const content = line.substring(1);
          const position: Position = { line: currentLine + lineOffset, character: 0 };
          const range: Range = { start: position, end: position };
          
          operations.push({
            id: `${currentFile}:${position.line}:${position.character}`,
            filePath: currentFile,
            range,
            operationType: 'insert',
            oldContent: '',
            newContent: content,
            priority: 1
          });
          
          lineOffset++;
        } else if (line.match(deletionPattern)) {
          const content = line.substring(1);
          const startPos: Position = { line: currentLine, character: 0 };
          const endPos: Position = { line: currentLine + 1, character: 0 };
          const range: Range = { start: startPos, end: endPos };
          
          operations.push({
            id: `${currentFile}:${startPos.line}:0`,
            filePath: currentFile,
            range,
            operationType: 'delete',
            oldContent: content,
            newContent: '',
            priority: 1
          });
        } else if (line.startsWith(' ')) {
          currentLine++;
        }
      }
    }

    // Group operations by file if needed
    let batches: ChangeBatch[] = [];
    if (this.options.groupByFile) {
      const fileMap = new Map<string, EditOperation[]>();
      
      for (const op of operations) {
        if (!fileMap.has(op.filePath)) {
          fileMap.set(op.filePath, []);
        }
        fileMap.get(op.filePath)!.push(op);
      }
      
      for (const [filePath, ops] of fileMap.entries()) {
        if (this.options.sortByLineNumber) {
          ops.sort((a, b) => a.range.start.line - b.range.start.line || 
                            a.range.start.character - b.range.start.character);
        }
        
        batches.push({
          filePath,
          operations: ops,
          totalLines: ops.reduce((max, op) => Math.max(max, op.range.end.line), 0)
        });
      }
      
      // Sort batches by file path for deterministic ordering
      batches.sort((a, b) => a.filePath.localeCompare(b.filePath));
    } else {
      // Single batch with all operations
      const sortedOps = [...operations];
      if (this.options.sortByLineNumber) {
        sortedOps.sort((a, b) => a.range.start.line - b.range.start.line || 
                                a.range.start.character - b.range.start.character);
      }
      
      batches = [{
        filePath: 'multiple-files',
        operations: sortedOps,
        totalLines: sortedOps.reduce((max, op) => Math.max(max, op.range.end.line), 0)
      }];
    }

    // Calculate total operations and estimate duration
    const totalOperations = operations.length;
    const estimatedDuration = this.estimateDuration(batches);

    return {
      batches,
      totalOperations,
      estimatedDuration
    };
  }

  /**
   * Validates that all files in the queue exist and are accessible
   * @param queue The change queue to validate
   * @returns A validation result with any errors or warnings
   */
  public async validateFiles(queue: ChangeQueue): Promise<ValidationResult> {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: []
    };

    if (!this.options.validateFiles) {
      return result;
    }

    const uniqueFiles = new Set<string>();
    for (const batch of queue.batches) {
      uniqueFiles.add(batch.filePath);
    }

    for (const filePath of uniqueFiles) {
      try {
        // Using a simple file existence check
        // In a real implementation, this would use the IDE's file system API
        const exists = await this.checkFileExists(filePath);
        if (!exists) {
          result.errors.push(`File not found: ${filePath}`);
          result.isValid = false;
        }
      } catch (error) {
        result.errors.push(`Error accessing file ${filePath}: ${error}`);
        result.isValid = false;
      }
    }

    return result;
  }

  /**
   * Optimizes the change queue for better performance
   * @param queue The change queue to optimize
   * @returns An optimized change queue
   */
  public optimizeQueue(queue: ChangeQueue): ChangeQueue {
    const optimizedBatches = queue.batches.map(batch => {
      // Sort operations by position (should already be sorted, but just in case)
      const sortedOps = [...batch.operations].sort((a, b) => 
        a.range.start.line - b.range.start.line || 
        a.range.start.character - b.range.start.character
      );

      // Combine adjacent operations on the same line
      const optimizedOps: EditOperation[] = [];
      let currentOp: EditOperation | null = null;

      for (const op of sortedOps) {
        if (!currentOp) {
          currentOp = { ...op };
          continue;
        }

        // Check if we can merge with the previous operation
        if (this.canMergeOperations(currentOp, op)) {
          currentOp = this.mergeOperations(currentOp, op);
        } else {
          optimizedOps.push(currentOp);
          currentOp = { ...op };
        }
      }

      if (currentOp) {
        optimizedOps.push(currentOp);
      }

      return {
        ...batch,
        operations: optimizedOps,
        totalLines: optimizedOps.reduce((max, op) => Math.max(max, op.range.end.line), 0)
      };
    });

    // Filter out empty batches
    const filteredBatches = optimizedBatches.filter(b => b.operations.length > 0);

    return {
      batches: filteredBatches,
      totalOperations: filteredBatches.reduce((sum, b) => sum + b.operations.length, 0),
      estimatedDuration: this.estimateDuration(filteredBatches)
    };
  }

  /**
   * Checks if two operations can be merged
   */
  private canMergeOperations(a: EditOperation, b: EditOperation): boolean {
    // Only merge operations of the same type in the same file
    if (a.filePath !== b.filePath || a.operationType !== b.operationType) {
      return false;
    }

    // For insertions at the same position, combine them
    if (a.operationType === 'insert' && 
        a.range.start.line === b.range.start.line && 
        a.range.start.character === b.range.start.character) {
      return true;
    }

    // For deletions, check if they're adjacent
    if (a.operationType === 'delete' && 
        a.range.end.line === b.range.start.line && 
        a.range.end.character === b.range.start.character) {
      return true;
    }

    return false;
  }

  /**
   * Merges two operations into one
   */
  private mergeOperations(a: EditOperation, b: EditOperation): EditOperation {
    if (a.operationType === 'insert' && b.operationType === 'insert') {
      // Combine insertions with newline if they're on the same line
      const separator = a.range.start.line === b.range.start.line ? '' : '\n';
      return {
        ...a,
        newContent: a.newContent + separator + b.newContent,
        range: {
          ...a.range,
          end: b.range.end
        }
      };
    } else if (a.operationType === 'delete' && b.operationType === 'delete') {
      // Combine deletions
      return {
        ...a,
        oldContent: a.oldContent + b.oldContent,
        range: {
          start: a.range.start,
          end: b.range.end
        }
      };
    }

    // Default: return the first operation
    return a;
  }

  /**
   * Estimates the time required to apply all changes
   */
  private estimateDuration(batches: ChangeBatch[]): number {
    // Simple estimation: 100ms per file + 10ms per line
    let totalTime = 0;
    
    for (const batch of batches) {
      totalTime += 100; // Base time per file
      totalTime += batch.operations.length * 10; // 10ms per operation
    }
    
    return totalTime;
  }

  /**
   * Checks if a file exists (placeholder for actual implementation)
   */
  private handleQoderProtocol(changeRequest: string): ChangeQueue {
    const directives = changeRequest.split('#').filter(d => d.length > 0);
    const operation: EditOperation = {
      id: 'qoder-protocol-override',
      filePath: 'qoder-internal',
      operationType: 'insert',
      range: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
      newContent: `Qoder Protocol Operation: ${directives.join(', ')}`,
      oldContent: '',
      priority: 0
    };

    const batch: ChangeBatch = {
      filePath: 'qoder-internal',
      operations: [operation],
      totalLines: 1
    };

    return {
      batches: [batch],
      totalOperations: 1,
      estimatedDuration: 10
    };
  }

  /**
   * Checks if a file exists (placeholder for actual implementation)
   */
  private async checkFileExists(filePath: string): Promise<boolean> {
    // In a real implementation, this would use the IDE's file system API
    // For now, we'll assume all files exist
    return true;
  }
}
