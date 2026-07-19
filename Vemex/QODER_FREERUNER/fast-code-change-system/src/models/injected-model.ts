import { InjectedModelState, QrCompletionPattern } from '../types';
import { QrHashService } from '../services/qr-hash.service';

/**
 * Simulates a model whose behavior is governed by the QR hash completion mechanism.
 */
export class InjectedModel {
  private state: InjectedModelState;
  private qrHashService: QrHashService;

  /**
   * Initializes the model with a new task, creating a fresh QR pattern.
   * @param qrWidth The width of the QR pattern for this task.
   * @param qrHeight The height of the QR pattern for this task.
   */
  constructor(qrWidth: number, qrHeight: number) {
    this.qrHashService = new QrHashService();

    // 1. Initialize the pattern structure
    let qrPattern = this.qrHashService.initializeQrPattern(qrWidth, qrHeight);

    // 2. Populate it with the required hashes for the task
    qrPattern = this.qrHashService.populateRequiredHashes(qrPattern);

    this.state = {
      qrPattern,
      tokensReceived: 0,
      tokensGenerated: 0,
    };
  }

  /**
   * Simulates the model receiving tokens.
   * @param count The number of tokens received.
   */
  public receiveTokens(count: number): void {
    this.state.tokensReceived += count;
    this.updateQrPattern();
  }

  /**
   * Simulates the model generating tokens.
   * @param count The number of tokens generated.
   */
  public generateTokens(count: number): void {
    this.state.tokensGenerated += count;
    this.updateQrPattern();
  }

  /**
   * Calls the service to process the current token flow and update the QR pattern.
   */
  private updateQrPattern(): void {
    this.state.qrPattern = this.qrHashService.processTokenFlow(
      this.state.qrPattern,
      this.state.tokensGenerated,
      this.state.tokensReceived
    );
  }

  /**
   * Checks if the model is allowed to report completion.
   * @returns True if the QR pattern is 100% filled, otherwise false.
   */
  public canReportCompletion(): boolean {
    return this.state.qrPattern.completionRate === 100;
  }

  /**
   * Gets the current state of the model for inspection.
   * @returns The current InjectedModelState.
   */
  public getCurrentState(): InjectedModelState {
    return this.state;
  }
}
