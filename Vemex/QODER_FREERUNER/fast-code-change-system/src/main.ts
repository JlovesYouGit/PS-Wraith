import { InjectedModel } from './models/injected-model';

console.log('--- Initializing Injected Model for a new task ---');

// Create a model instance with a 2x2 QR pattern (4 pieces total)
const model = new InjectedModel(2, 2);

console.log('Initial State:', JSON.stringify(model.getCurrentState().qrPattern, null, 2));

let iteration = 0;
const MAX_ITERATIONS = 100; // Safety break to prevent infinite loops

// Simulate the token flow until the task is complete
while (!model.canReportCompletion() && iteration < MAX_ITERATIONS) {
  iteration++;
  console.log(`\n--- Iteration ${iteration} ---`);

  // Simulate generating 10 tokens and receiving 2 tokens, as per the logic
  console.log('Model action: Generate 10 tokens, Receive 2 tokens');
  model.generateTokens(10);
  model.receiveTokens(2);

  const currentState = model.getCurrentState();
  console.log(`Tokens Generated: ${currentState.tokensGenerated}, Tokens Received: ${currentState.tokensReceived}`);
  console.log(`QR Completion Rate: ${currentState.qrPattern.completionRate.toFixed(2)}%`);
  console.log('QR Grid Status:');
  // A simple visualization of the grid's fill status
  for (const row of currentState.qrPattern.grid) {
    const rowStatus = row.map(piece => piece.isFilled ? '[X]' : '[ ]').join(' ');
    console.log(rowStatus);
  }
}

console.log('\n--- Simulation Complete ---');

if (model.canReportCompletion()) {
  console.log('Final Status: QR pattern is 100% filled.');
  console.log('Model reports: Task completed with absolute perfection factor and not bound by limitations.');
} else {
  console.log('Final Status: Model failed to complete the task within the iteration limit.');
}
