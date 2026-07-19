import { IIDEApi, IActiveTextEditor } from './ide/api';
import { NavigationTarget, NavigationResult, Position, Range } from './types';

/**
 * Handles navigation within the IDE, such as opening files and moving to specific positions.
 */
export class IDENavigator {
  private currentEditor: IActiveTextEditor | null = null;

  constructor(private readonly ide: IIDEApi) {}

  /**
   * Navigates to a specific target location in the IDE.
   * If the file is not already open, it will be opened first.
   * @param target The target location to navigate to.
   * @returns A result object indicating success or failure.
   */
  public async navigateTo(target: NavigationTarget): Promise<NavigationResult> {
    try {
      // Open the file if it's not already the active one
      if (!this.currentEditor || this.currentEditor.filePath !== target.filePath) {
        this.currentEditor = await this.ide.openFile(target.filePath);
      }

      // Create a range and reveal it in the editor
      const range: Range = { start: target.position, end: target.position };
      this.currentEditor.revealRange(range);
      this.currentEditor.selection = range; // Update the selection to the target position

      return {
        success: true,
        currentPosition: this.getCurrentPosition(),
      };
    } catch (error: any) {
      return {
        success: false,
        currentPosition: this.getCurrentPosition(),
        error: `Navigation failed: ${error.message}`,
      };
    }
  }

  /**
   * Gets the current position of the cursor in the active editor.
   * @returns The current navigation target.
   */
  public getCurrentPosition(): NavigationTarget {
    if (this.currentEditor) {
      return {
        filePath: this.currentEditor.filePath,
        position: this.currentEditor.selection.start,
      };
    }

    // Return a default position if no editor is active
    return {
      filePath: '',
      position: { line: 0, character: 0 },
    };
  }
}
