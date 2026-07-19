/**
 * Test script for Akashik Record functionality
 */

const akashikRecord = require('./SharedClientCache/bin/akashik_record.js');

async function testAkashikRecord() {
  console.log('🔮 Testing Akashik Record functionality...\n');
  
  // Test 1: Initialize system
  console.log('Test 1: Initializing Akashik Record system...');
  try {
    await akashikRecord.initialize();
    console.log('✅ Initialization successful');
  } catch (error) {
    console.error('❌ Initialization failed:', error.message);
  }
  console.log('');
  
  // Test 2: Get synchronization status
  console.log('Test 2: Getting synchronization status...');
  try {
    const status = akashikRecord.getSyncStatus();
    console.log('Status:', JSON.stringify(status, null, 2));
  } catch (error) {
    console.error('❌ Failed to get status:', error.message);
  }
  console.log('');
  
  // Test 3: Store a knowledge record
  console.log('Test 3: Storing a knowledge record...');
  try {
    const testKnowledge = {
      id: 'test_record_1',
      knowledge: {
        insights: {
          mainConcepts: ['quantum', 'processing', 'synchronization'],
          implementationGuidance: [{ title: 'Quantum Sync', summary: 'Synchronize cores' }],
          bestPractices: [{ title: 'Token Management', description: 'Manage token rates' }]
        }
      },
      timestamp: Date.now(),
      source: 'test'
    };
    
    akashikRecord.storeKnowledgeRecord(testKnowledge);
    console.log('✅ Knowledge record stored');
  } catch (error) {
    console.error('❌ Failed to store knowledge record:', error.message);
  }
  console.log('');
  
  // Test 4: Retrieve knowledge record
  console.log('Test 4: Retrieving knowledge record...');
  try {
    const record = akashikRecord.getKnowledgeRecord('test_record_1');
    console.log('Retrieved record:', record ? 'Found' : 'Not found');
    if (record) {
      console.log('Record details:', JSON.stringify(record, null, 2));
    }
  } catch (error) {
    console.error('❌ Failed to retrieve knowledge record:', error.message);
  }
  console.log('');
  
  // Test 5: Get all records
  console.log('Test 5: Getting all knowledge records...');
  try {
    const records = akashikRecord.getAllKnowledgeRecords();
    console.log('Total records:', records.length);
  } catch (error) {
    console.error('❌ Failed to get all records:', error.message);
  }
  console.log('');
  
  // Test 6: Token rate calculation
  console.log('Test 6: Calculating optimal token rate...');
  try {
    const testKnowledge = {
      knowledge: {
        insights: {
          mainConcepts: ['a', 'b', 'c', 'd', 'e'],
          implementationGuidance: [{}, {}, {}],
          bestPractices: [{}, {}]
        }
      }
    };
    
    const rate = akashikRecord.calculateOptimalTokenRate(testKnowledge);
    console.log('Optimal token rate:', rate.toFixed(2), 'tokens/second');
  } catch (error) {
    console.error('❌ Failed to calculate token rate:', error.message);
  }
  console.log('');
  
  console.log('✅ All Akashik Record tests completed!');
}

// Run the tests
testAkashikRecord().catch(console.error);