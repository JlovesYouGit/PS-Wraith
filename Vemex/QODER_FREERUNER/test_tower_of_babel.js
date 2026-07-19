/**
 * Test script for Tower of Babel functionality
 */

const towerOfBabel = require('./SharedClientCache/bin/tower_of_babel.js');

async function testTowerOfBabel() {
  console.log('🗼 Testing Tower of Babel functionality...\n');
  
  // Test 1: Extract search keywords
  console.log('Test 1: Extracting search keywords...');
  const taskContext = "Implement a REST API using Node.js and Express with JWT authentication";
  const keywords = towerOfBabel.extractSearchKeywords(taskContext);
  console.log('Extracted keywords:', keywords);
  console.log('');
  
  // Test 2: Extract languages, frameworks, and technologies
  console.log('Test 2: Extracting languages, frameworks, and technologies...');
  const languages = towerOfBabel.extractLanguages(taskContext);
  const frameworks = towerOfBabel.extractFrameworks(taskContext);
  const technologies = towerOfBabel.extractTechnologies(taskContext);
  console.log('Languages:', languages);
  console.log('Frameworks:', frameworks);
  console.log('Technologies:', technologies);
  console.log('');
  
  // Test 3: Calculate relevance
  console.log('Test 3: Calculating relevance...');
  const content = "Node.js Express JWT authentication tutorial with examples";
  const relevance = towerOfBabel.calculateRelevance(content, taskContext);
  console.log('Relevance score:', relevance.toFixed(2));
  console.log('');
  
  // Test 4: Determine content type
  console.log('Test 4: Determining content type...');
  const contentType = towerOfBabel.determineContentType("Express JWT Authentication Guide", content);
  console.log('Content type:', contentType);
  console.log('');
  
  // Test 5: Cache functionality
  console.log('Test 5: Testing cache functionality...');
  const cacheStats = towerOfBabel.getCacheStats();
  console.log('Cache size:', cacheStats.size);
  console.log('');
  
  console.log('✅ All Tower of Babel tests completed!');
}

// Run the tests
testTowerOfBabel().catch(console.error);