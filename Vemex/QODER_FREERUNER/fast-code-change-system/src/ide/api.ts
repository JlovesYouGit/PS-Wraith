import { Position, Range } from '../types';

/**
 * Represents a simplified abstraction of an active text editor in the IDE.
 */
export interface IActiveTextEditor {
  filePath: string;
  content: string;
  selection: Range;
  revealRange(range: Range): void;
}

/**
 * Defines the interface for core IDE functionalities that the system will rely on.
 * This abstraction allows for easier testing and decouples the system from specific IDE APIs.
 */
export interface IIDEApi {
  /**
   * Opens a file in the IDE.
   * @param filePath The absolute path to the file.
   * @returns A promise that resolves to the active text editor.
   */
  openFile(filePath: string): Promise<IActiveTextEditor>;

  /**
   * Applies a text replacement in a given file.
   * @param filePath The absolute path to the file.
   * @param range The range of text to replace.
   * @param newText The new text to insert.
   * @returns A promise that resolves when the edit has been applied.
   */
  replaceText(filePath: string, range: Range, newText: string): Promise<void>;

  /**
   * Retrieves the current content of a file.
   * @param filePath The absolute path to the file.
   * @returns A promise that resolves to the file's content.
   */
  getFileContent(filePath: string): Promise<string>;

  /**
   * Checks if a file exists in the workspace.
   * @param filePath The absolute path to the file.
   * @returns A promise that resolves to true if the file exists, false otherwise.
   */
  fileExists(filePath: string): Promise<boolean>;
}
