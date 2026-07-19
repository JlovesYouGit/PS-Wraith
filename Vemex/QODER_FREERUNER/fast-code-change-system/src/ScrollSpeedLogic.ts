import { ScrollConfig, ScrollPlan, ScrollStep } from './types';

/**
 * Calculates a smooth scrolling plan between two points in a file.
 */
export class ScrollSpeedLogic {
  private config: Required<ScrollConfig>;

  constructor(config?: Partial<ScrollConfig>) {
    this.config = {
      baseSpeed: 100, // lines per second
      maxSpeed: 2000, // lines per second
      acceleration: 4000, // lines per second^2
      decelerationDistance: 50, // lines
      minPause: 200, // ms
      maxPause: 1000, // ms
      ...config,
    };
  }

  /**
   * Calculates a scroll plan for navigating between two lines in a file.
   * @param startLine The starting line number.
   * @param endLine The ending line number.
   * @returns A ScrollPlan detailing the steps and duration.
   */
  public calculateScrollPlan(startLine: number, endLine: number): ScrollPlan {
    const steps: ScrollStep[] = [];
    let totalDuration = 0;
    const distance = Math.abs(endLine - startLine);

    if (distance === 0) {
      // No scrolling needed, just a pause.
      const pause = this.config.minPause;
      steps.push({ lineNumber: endLine, delay: pause });
      return { steps, totalDuration: pause };
    }

    const direction = Math.sign(endLine - startLine);
    let currentLine = startLine;
    let currentSpeed = this.config.baseSpeed;
    let timeElapsed = 0; // in seconds

    while (currentLine !== endLine) {
      const remainingDistance = Math.abs(endLine - currentLine);

      // Determine if we need to decelerate
      if (remainingDistance <= this.config.decelerationDistance) {
        const decelerationFactor = remainingDistance / this.config.decelerationDistance;
        currentSpeed = Math.max(
          this.config.baseSpeed,
          this.config.maxSpeed * decelerationFactor
        );
      } else {
        // Accelerate if not at max speed
        currentSpeed = Math.min(
          this.config.maxSpeed,
          currentSpeed + this.config.acceleration * (1 / currentSpeed) // dt = 1 / speed
        );
      }

      // Calculate how many lines to jump in this step
      // Make larger jumps at higher speeds for efficiency
      const lineJump = Math.max(1, Math.round(currentSpeed / 100)); // Heuristic
      const nextLine = this.getNextLine(currentLine, endLine, lineJump, direction);
      const distanceToTravel = Math.abs(nextLine - currentLine);
      const delaySeconds = distanceToTravel / currentSpeed;
      timeElapsed += delaySeconds;

      currentLine = nextLine;
      const delayMs = delaySeconds * 1000;
      totalDuration += delayMs;

      steps.push({ lineNumber: currentLine, delay: delayMs });
    }

    // Add the final pause at the target
    const finalPause = this.config.minPause;
    steps.push({ lineNumber: endLine, delay: finalPause });
    totalDuration += finalPause;

    return { steps, totalDuration };
  }

  private getNextLine(
    current: number,
    end: number,
    jump: number,
    direction: number
  ): number {
    const next = current + jump * direction;
    if (direction > 0) {
      return Math.min(next, end);
    } else {
      return Math.max(next, end);
    }
  }
}
