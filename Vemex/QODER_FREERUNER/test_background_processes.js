/**
 * Test script for background processes
 */

const http = require('http');

async function testBackgroundProcesses() {
  console.log('🧪 Testing background processes...\n');
  
  // Test Tower of Babel server
  console.log('Test 1: Checking Tower of Babel server...');
  try {
    const babelStatus = await makeRequest(3010, '/cache-stats');
    console.log('Tower of Babel status:', babelStatus.success ? '✅ Running' : '❌ Not responding');
  } catch (error) {
    console.log('Tower of Babel status: ❌ Error -', error.message);
  }
  console.log('');
  
  // Test Akashik Record server
  console.log('Test 2: Checking Akashik Record server...');
  try {
    const akashikStatus = await makeRequest(3011, '/status');
    console.log('Akashik Record status:', akashikStatus.success ? '✅ Running' : '❌ Not responding');
  } catch (error) {
    console.log('Akashik Record status: ❌ Error -', error.message);
  }
  console.log('');
  
  console.log('✅ Background process testing complete!');
}

function makeRequest(port, path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: port,
      path: path,
      method: 'GET',
      timeout: 3000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          resolve({ success: false, error: 'Invalid JSON response' });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.end();
  });
}

// Run the tests
testBackgroundProcesses().catch(console.error);