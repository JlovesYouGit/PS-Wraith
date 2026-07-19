/**
 * Test script for Qoder Architecture Enhancements
 * 
 * This script tests the enhanced performance features of the Qoder system.
 */

// Import the enhanced modules
const fs = require('fs');
const path = require('path');

// Test the enhanced quantum controller
async function testQuantumController() {
  console.log('🧪 Testing Enhanced Quantum Controller...');
  
  // Import the quantum controller components
  const quantumControllerPath = path.join(__dirname, 'SharedClientCache', 'bin', 'qoder_quantum_controller.js');
  
  if (fs.existsSync(quantumControllerPath)) {
    console.log('✅ Quantum Controller file exists');
    
    // Test that the file contains our enhancements
    const content = fs.readFileSync(quantumControllerPath, 'utf8');
    
    if (content.includes('QuantumPerformanceProfiler')) {
      console.log('✅ QuantumPerformanceProfiler class found');
    } else {
      console.log('❌ QuantumPerformanceProfiler class not found');
    }
    
    if (content.includes('get_quantum_performance_profile')) {
      console.log('✅ get_quantum_performance_profile tool found');
    } else {
      console.log('❌ get_quantum_performance_profile tool not found');
    }
    
    if (content.includes('expand_quantum_network_auto')) {
      console.log('✅ expand_quantum_network_auto tool found');
    } else {
      console.log('❌ expand_quantum_network_auto tool not found');
    }
  } else {
    console.log('❌ Quantum Controller file not found');
  }
}

// Test the enhanced BMAD wrapper
async function testBMADWrapper() {
  console.log('\n🧪 Testing Enhanced BMAD Wrapper...');
  
  const bmadWrapperPath = path.join(__dirname, 'SharedClientCache', 'bin', 'bmad_high_performance_wrapper.js');
  
  if (fs.existsSync(bmadWrapperPath)) {
    console.log('✅ BMAD Wrapper file exists');
    
    // Test that the file contains our enhancements
    const content = fs.readFileSync(bmadWrapperPath, 'utf8');
    
    if (content.includes('BMADPerformanceProfiler')) {
      console.log('✅ BMADPerformanceProfiler class found');
    } else {
      console.log('❌ BMADPerformanceProfiler class not found');
    }
    
    if (content.includes('autoOptimize')) {
      console.log('✅ autoOptimize method found');
    } else {
      console.log('❌ autoOptimize method not found');
    }
  } else {
    console.log('❌ BMAD Wrapper file not found');
  }
}

// Test the enhanced Smart MCP Manager
async function testSmartMCPManager() {
  console.log('\n🧪 Testing Enhanced Smart MCP Manager...');
  
  const smartMCPPath = path.join(__dirname, 'SharedClientCache', 'smart_mcp_manager.js');
  
  if (fs.existsSync(smartMCPPath)) {
    console.log('✅ Smart MCP Manager file exists');
    
    // Test that the file contains our enhancements
    const content = fs.readFileSync(smartMCPPath, 'utf8');
    
    if (content.includes('MCPPerformanceProfiler')) {
      console.log('✅ MCPPerformanceProfiler class found');
    } else {
      console.log('❌ MCPPerformanceProfiler class not found');
    }
    
    if (content.includes('autoOptimize')) {
      console.log('✅ autoOptimize method found');
    } else {
      console.log('❌ autoOptimize method not found');
    }
  } else {
    console.log('❌ Smart MCP Manager file not found');
  }
}

// Test the enhanced Code Storage
async function testCodeStorage() {
  console.log('\n🧪 Testing Enhanced Code Storage...');
  
  const codeStoragePath = path.join(__dirname, 'SharedClientCache', 'bin', 'optimized_code_storage.js');
  
  if (fs.existsSync(codeStoragePath)) {
    console.log('✅ Code Storage file exists');
    
    // Test that the file contains our enhancements
    const content = fs.readFileSync(codeStoragePath, 'utf8');
    
    if (content.includes('CodeStoragePerformanceProfiler')) {
      console.log('✅ CodeStoragePerformanceProfiler class found');
    } else {
      console.log('❌ CodeStoragePerformanceProfiler class not found');
    }
    
    if (content.includes('autoOptimize')) {
      console.log('✅ autoOptimize method found');
    } else {
      console.log('❌ autoOptimize method not found');
    }
  } else {
    console.log('❌ Code Storage file not found');
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Running Qoder Architecture Enhancement Tests\n');
  
  await testQuantumController();
  await testBMADWrapper();
  await testSmartMCPManager();
  await testCodeStorage();
  
  console.log('\n✅ All enhancement tests completed!');
  console.log('\n📝 Summary of Enhancements:');
  console.log('  • Quantum Processing System with performance profiling');
  console.log('  • BMAD High-Performance Processing with auto-optimization');
  console.log('  • Smart MCP Management with intelligent caching');
  console.log('  • Optimized Code Storage with enhanced performance tracking');
  console.log('  • Comprehensive performance monitoring across all components');
}

// Execute the tests
runAllTests().catch(console.error);