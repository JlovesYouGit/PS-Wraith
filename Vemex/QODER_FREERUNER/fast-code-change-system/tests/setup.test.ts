/**
 * Setup verification tests
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
  EditOperation,
  ChangeBatch,
  ChangeQueue,
  NavigationTarget,
  LockResult,
  ScrollConfig
} from '../src/types';

describe('Project Setup', () => {
  it('should have all core types defined', () => {
    // Verify types are importable
    const editOp: Partial<EditOperation> = {
      id: 'test',
      filePath: 'test.ts',
      lineNumber: 1,
      operationType: 'insert',
      newContent: 'test',
      priority: 1
    };
    
    expect(editOp.id).toBe('test');
  });

  it('should have fast-check available', () => {
    // Simple property test to verify fast-check is working
    fc.assert(
      fc.property(fc.integer(), (n) => {
        return n + 0 === n;
      }),
      { numRuns: 100 }
    );
  });

  it('should validate NavigationTarget structure', () => {
    const target: NavigationTarget = {
      filePath: 'test.ts',
      lineNumber: 10,
      columnNumber: 5
    };
    
    expect(target.filePath).toBe('test.ts');
    expect(target.lineNumber).toBe(10);
    expect(target.columnNumber).toBe(5);
  });

  it('should validate ScrollConfig structure', () => {
    const config: ScrollConfig = {
      baseSpeed: 100,
      accelerationFactor: 1.5,
      decelerationDistance: 10,
      interFileDelay: 200
    };
    
    expect(config.baseSpeed).toBe(100);
    expect(config.accelerationFactor).toBe(1.5);
  });
});

describe('fast-check Integration', () => {
  it('should run property-based tests with minimum 100 iterations', () => {
    let runCount = 0;
    
    fc.assert(
      fc.property(fc.string(), (s) => {
        runCount++;
        return s.length >= 0;
      }),
      { numRuns: 100 }
    );
    
    expect(runCount).toBeGreaterThanOrEqual(100);
  });

  it('should generate valid EditOperation structures', () => {
    const editOpArbitrary = fc.record({
      id: fc.string(),
      filePath: fc.string(),
      lineNumber: fc.integer({ min: 1 }),
      operationType: fc.constantFrom('insert', 'delete', 'replace'),
      newContent: fc.string(),
      priority: fc.integer({ min: 0, max: 10 })
    });

    fc.assert(
      fc.property(editOpArbitrary, (op) => {
        return op.lineNumber >= 1 && op.priority >= 0 && op.priority <= 10;
      }),
      { numRuns: 100 }
    );
  });
});
