import { ScrollSpeedLogic } from '../ScrollSpeedLogic';
import { ScrollConfig } from '../types';

describe('ScrollSpeedLogic', () => {
  let scrollLogic: ScrollSpeedLogic;

  it('should generate a plan for scrolling down', () => {
    scrollLogic = new ScrollSpeedLogic();
    const plan = scrollLogic.calculateScrollPlan(1, 200);

    expect(plan.steps.length).toBeGreaterThan(1);
    expect(plan.totalDuration).toBeGreaterThan(0);
    expect(plan.steps[0].lineNumber).toBeGreaterThan(1);
    expect(plan.steps[plan.steps.length - 2].lineNumber).toBe(200); // Before final pause
  });

  it('should generate a plan for scrolling up', () => {
    scrollLogic = new ScrollSpeedLogic();
    const plan = scrollLogic.calculateScrollPlan(500, 50);

    expect(plan.steps.length).toBeGreaterThan(1);
    expect(plan.steps[0].lineNumber).toBeLessThan(500);
    expect(plan.steps[plan.steps.length - 2].lineNumber).toBe(50);
  });

  it('should handle zero distance with a simple pause', () => {
    scrollLogic = new ScrollSpeedLogic({ minPause: 150 });
    const plan = scrollLogic.calculateScrollPlan(10, 10);

    expect(plan.steps.length).toBe(1);
    expect(plan.steps[0].lineNumber).toBe(10);
    expect(plan.totalDuration).toBe(150);
  });

  it('should apply deceleration near the target', () => {
    const config: ScrollConfig = {
      baseSpeed: 100,
      maxSpeed: 5000,
      acceleration: 10000,
      decelerationDistance: 50,
      minPause: 100,
      maxPause: 1000,
    };
    scrollLogic = new ScrollSpeedLogic(config);
    const plan = scrollLogic.calculateScrollPlan(1, 1000);

    // Find the step where deceleration should start
    const decelerationStartStep = plan.steps.find(
      (step) => step.lineNumber >= 950
    );
    const stepBeforeDeceleration = plan.steps[
      plan.steps.indexOf(decelerationStartStep!) - 1
    ];

    // The delay between steps should increase as it decelerates
    expect(decelerationStartStep!.delay).toBeGreaterThan(
      stepBeforeDeceleration.delay
    );
  });
});
