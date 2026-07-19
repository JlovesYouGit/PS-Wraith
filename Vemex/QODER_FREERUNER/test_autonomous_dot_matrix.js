/**
 * Test script for autonomous dot matrix validation functionality
 */

const dotMatrixAnalyzer = require('./SharedClientCache/bin/dot_matrix_analyzer.js');

async function testAutonomousDotMatrix() {
  console.log('🔢 Testing autonomous dot matrix validation functionality...\n');
  
  // Test 1: Set autonomous mode
  console.log('Test 1: Setting autonomous mode...');
  try {
    dotMatrixAnalyzer.setAutonomousMode(true);
    console.log('Autonomous mode: ✅ Enabled');
  } catch (error) {
    console.log('Autonomous mode: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 2: Set validation threshold
  console.log('Test 2: Setting validation threshold...');
  try {
    dotMatrixAnalyzer.setValidationThreshold(0.8);
    console.log('Validation threshold: ✅ Set to 0.8');
  } catch (error) {
    console.log('Validation threshold: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 3: Analyze data with high confidence insights
  console.log('Test 3: Analyzing data with high confidence insights...');
  try {
    const highConfidenceData = [0.9, 0.85, 0.92, 0.88, 0.91];
    const result = await dotMatrixAnalyzer.analyzeDataWithValidation(highConfidenceData);
    
    console.log('Analysis result:', result.proceed ? '✅ Proceed' : '❌ Halt');
    console.log('Validation:', result.validation.valid ? '✅ Valid' : '❌ Invalid');
    console.log('Agreement:', result.agreement.agreed ? '✅ Agreed' : '❌ Not agreed');
    console.log('Confidence:', result.validation.confidence.toFixed(2));
  } catch (error) {
    console.log('High confidence analysis: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 4: Analyze data with low confidence insights
  console.log('Test 4: Analyzing data with low confidence insights...');
  try {
    const lowConfidenceData = [0.3, 0.2, 0.4, 0.45, 0.35];
    const result = await dotMatrixAnalyzer.analyzeDataWithValidation(lowConfidenceData);
    
    console.log('Analysis result:', result.proceed ? '✅ Proceed' : '❌ Halt');
    console.log('Validation:', result.validation.valid ? '✅ Valid' : '❌ Invalid');
    console.log('Agreement:', result.agreement.agreed ? '✅ Agreed' : '❌ Not agreed');
    console.log('Confidence:', result.validation.confidence.toFixed(2));
  } catch (error) {
    console.log('Low confidence analysis: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 5: Question results
  console.log('Test 5: Questioning results...');
  try {
    const testData = { insights: [{ type: 'pattern', confidence: 0.9 }] };
    const agreement = await dotMatrixAnalyzer.questionResults(testData);
    
    console.log('Question results:', agreement.agreed ? '✅ Agreed' : '❌ Not agreed');
  } catch (error) {
    console.log('Question results: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test 6: Connect dots between analyses
  console.log('Test 6: Connecting dots between analyses...');
  try {
    // First analysis
    const data1 = [0.8, 0.7, 0.9, 0.85];
    dotMatrixAnalyzer.analyzeData(data1);
    
    // Second analysis
    const data2 = [0.82, 0.75, 0.88, 0.9];
    const currentAnalysis = dotMatrixAnalyzer.analyzeData(data2);
    
    const connection = dotMatrixAnalyzer.connectDots(currentAnalysis);
    
    console.log('Dot connection:', connection.connected ? '✅ Connected' : '❌ Not connected');
    if (connection.correlations) {
      console.log('Correlations found:', connection.correlations.length);
    }
  } catch (error) {
    console.log('Dot connection: ❌ Error -', error.message);
  }
  console.log('');
  
  console.log('✅ All autonomous dot matrix validation tests completed!');
}

// Run the tests
testAutonomousDotMatrix().catch(console.error);