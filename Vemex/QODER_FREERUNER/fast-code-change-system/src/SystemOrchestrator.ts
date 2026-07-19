import { ChangeParser } from './ChangeParser';
import { IDENavigator } from './IDENavigator';
import { InlineLock } from './InlineLock';
import { ScrollSpeedLogic } from './ScrollSpeedLogic';
import { FastChangeApplicator } from './FastChangeApplicator';
import { IIDEApi } from './ide/api';
import { ChangeQueue, ApplicationResult, ScrollPlan, IInteractionLayer, ExecutionState, SystemConfig, IWebSearcher, ISolutionExtractor, ModelFeedback, EntropyPayload } from './types';
import { ConfigurationManager } from './ConfigurationManager';
import { ExecutionHistoryManager } from './ExecutionHistoryManager';
import { WebSearcher } from './WebSearcher';
import { SolutionExtractor } from './SolutionExtractor';
import { EntropyManager } from './EntropyManager';
import { BytiseModifierImpl } from './BytiseModifier';

/**
 * The main orchestrator that wires all components of the Fast Code Change System together.
 */
export class SystemOrchestrator {

  public async cleanupBrokenPuzzles(): Promise<void> {
    const brokenPuzzles = this.feedback.getBrokenPuzzles();
    for (const puzzle of brokenPuzzles) {
      try {
        await this.ide.replaceText(puzzle.filePath, puzzle.range, ''); // Replace with empty string to delete
        console.log(`Cleaned up broken puzzle ${puzzle.id} in ${puzzle.filePath}`);
      } catch (error) {
        console.error(`Failed to clean up broken puzzle ${puzzle.id}:`, error);
      }
    }
  }


  public async analyzeFileForPuzzles(filePath: string): Promise<void> {
    try {
      const content = await this.ide.getFileContent(filePath);
      const puzzles = this.bytiseModifier.analyze(filePath, content);
      puzzles.forEach(puzzle => this.feedback.registerPuzzle(puzzle));
      console.log(`Found ${puzzles.length} puzzles in ${filePath}`);
    } catch (error) {
      console.error(`Failed to read or analyze file ${filePath}:`, error);
    }
  }

  private parser: ChangeParser;
  private navigator: IDENavigator;
  private lock: InlineLock;
  private scroller: ScrollSpeedLogic;
  private applicator: FastChangeApplicator;
  private configManager: ConfigurationManager;
  private historyManager: ExecutionHistoryManager;
  private searcher: IWebSearcher;
  private extractor: ISolutionExtractor;
  private feedback: EntropyManager;
  private bytiseModifier: BytiseModifierImpl;

  constructor(
    private readonly ide: IIDEApi,
    private readonly interactionLayer: IInteractionLayer,
    initialConfig?: Partial<SystemConfig>
  ) {
    this.configManager = new ConfigurationManager(initialConfig);
    const config = this.configManager.getConfig();

    // Initialize all the components with config
    this.parser = new ChangeParser(config.parser);
    this.navigator = new IDENavigator(this.ide);
    this.lock = new InlineLock(this.navigator, this.ide);
    this.scroller = new ScrollSpeedLogic(config.scrolling);
    this.historyManager = new ExecutionHistoryManager();
    this.searcher = new WebSearcher();
    this.extractor = new SolutionExtractor();
    this.feedback = new EntropyManager();
    this.bytiseModifier = new BytiseModifierImpl();
    this.applicator = new FastChangeApplicator(this.lock, this.ide, this.interactionLayer, this.feedback);
  }

  public updateConfig(config: Partial<SystemConfig>) {
    this.configManager.updateConfig(config);
    const newConfig = this.configManager.getConfig();
    // Re-initialize components with new config
    this.parser = new ChangeParser(newConfig.parser);
    this.scroller = new ScrollSpeedLogic(newConfig.scrolling);
  }

  /**
   * Parses a raw change request string into a structured and validated ChangeQueue.
   * @param changeRequest The raw string containing the diff/patch.
   * @returns A promise that resolves to the parsed and validated ChangeQueue, or null if validation fails.
   */
  public async prepareChangeQueue(changeRequest: string): Promise<ChangeQueue | null> {
    // 1. Parse the raw string
    let queue = this.parser.parse(changeRequest);

    // 2. Validate the files mentioned in the queue
    const validationResult = await this.parser.validateFiles(queue);
    if (!validationResult.isValid) {
      // In a real application, you'd expose these errors to the user
      console.error('File validation failed:', validationResult.errors);
      return null;
    }

    // 3. Optimize the queue (e.g., merge operations)
    queue = this.parser.optimizeQueue(queue);

    return queue;
  }

  /**
   * Executes the full process of applying changes from a raw request string.
   * This method simulates the visual scrolling and then applies the changes.
   * @param queue The ChangeQueue to be executed.
   * @param onScrollStep A callback function that is called for each step in the scroll plan.
   * @returns A promise that resolves to the final ApplicationResult.
   */
  public async findAndApplySolution(problemDescription: string, onScrollStep?: (line: number) => Promise<void>): Promise<ApplicationResult | null> {
    const modelId = problemDescription;
    // 1. Search for a solution
    let searchResults = await this.searcher.search(problemDescription);

    // Re-rank search results based on entropy score
    searchResults.sort((a, b) => {
        const scoreA = this.feedback.getEntropyScore(a.link);
        const scoreB = this.feedback.getEntropyScore(b.link);
        return scoreB - scoreA; // Sort descending
    });
    if (searchResults.length === 0) {
      console.log('No solutions found.');
      return null;
    }

    // 2. Ask user to select a solution
    const selectedResult = await this.interactionLayer.selectSearchResult(searchResults);
    const solutionId = selectedResult?.link ?? 'no_selection';
    if (!selectedResult) {
      console.log('No solution selected.');
      return null;
    }

    // 3. Extract the change from the selected solution
    const changeRequest = await this.extractor.extract(selectedResult.link);
    if (!changeRequest) {
        console.log('Failed to extract change request.');
        this.feedback?.recordEntropy({ modelId: solutionId, entropy: 'bad', details: 'Failed to extract change request' });
        return null;
    }

    // 4. Prepare and execute the change
    const queue = await this.prepareChangeQueue(changeRequest);
    if (!queue) {
      console.log('Failed to prepare change queue.');
      this.feedback?.recordEntropy({ modelId: solutionId, entropy: 'bad', details: 'Failed to prepare change queue' });
      return null;
    }

    const result = await this.execute(queue, onScrollStep);

    this.feedback?.recordEntropy({
        modelId: solutionId,
        entropy: result.success && result.conflicts.length === 0 ? 'good' : 'bad',
        details: {
            conflicts: result.conflicts,
            appliedChangeCount: result.appliedChanges.length,
        }
    });

    return result;
  }

  /**
   * Executes a change from a constant, injected change request string.
   * This bypasses the search and selection steps and is useful for testing.
   * @param changeRequest The raw string containing the diff/patch.
   * @param solutionId A unique identifier for the solution being tested.
   * @returns A promise that resolves to the final ApplicationResult.
   */
  public async executeInjectedChange(changeRequest: string, solutionId: string): Promise<ApplicationResult | null> {
    // 1. Prepare the change queue from the injected request
    const queue = await this.prepareChangeQueue(changeRequest);
    if (!queue) {
      console.log('Failed to prepare change queue for injected change.');
      this.feedback.recordEntropy({ modelId: solutionId, entropy: 'bad', details: 'Failed to prepare change queue' });
      return null;
    }

    // 2. Execute the change
    const result = await this.execute(queue);

    // 3. Record entropy for the injected solution
    this.feedback.recordEntropy({
        modelId: solutionId,
        entropy: result.success && result.conflicts.length === 0 ? 'good' : 'bad',
        details: {
            conflicts: result.conflicts,
            appliedChangeCount: result.appliedChanges.length,
        }
    });

    return result;
  }

  public async execute(queue: ChangeQueue, onScrollStep?: (line: number) => Promise<void>): Promise<ApplicationResult> {

    let lastLine = 0;
    let lastFile = '';

    for (const batch of queue.batches) {
      if (lastFile !== batch.filePath) {
        // Open the new file, no scrolling simulation for file jumps
        await this.navigator.navigateTo({ filePath: batch.filePath, position: { line: 0, character: 0 } });
        lastFile = batch.filePath;
        lastLine = 0;
      }

      for (const operation of batch.operations) {
        const targetLine = operation.range.start.line;

        // 1. Calculate and execute the scroll plan
        if (onScrollStep) {
          const scrollPlan = this.scroller.calculateScrollPlan(lastLine, targetLine);
          for (const step of scrollPlan.steps) {
            await onScrollStep(step.lineNumber);
            await new Promise(resolve => setTimeout(resolve, step.delay));
          }
        }

        // 2. Navigate directly to the final position before applying
        await this.navigator.navigateTo({ filePath: operation.filePath, position: operation.range.start });

        lastLine = targetLine;
      }
    }

    // 3. After all scrolling is complete, apply the changes interactively
    const result = await this.applicator.applyChanges({
      status: 'pending',
      queue,
      appliedChanges: [],
      conflicts: [],
      currentStep: 0,
    });

    this.historyManager.recordExecution(result);

    return result;
  }
}
