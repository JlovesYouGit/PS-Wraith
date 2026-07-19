#!/usr/bin/env python3

"""
Test script for performance extensions with C and potential Rust components.
"""

import math
import time

# Import our performance extensions
try:
    from performance_extensions import PerformanceExtensions
    extensions_available = True
    print("Performance extensions loaded successfully!")
except ImportError as e:
    extensions_available = False
    print(f"Failed to import performance extensions: {e}")

def create_test_signal():
    """Create a test signal with ultrasonic characteristics."""
    signal = []
    for i in range(1000):
        # Base signal
        value = math.sin(2 * math.pi * 50 * i / 1000.0) + 0.5 * math.sin(2 * math.pi * 120 * i / 1000.0)
        # Add some ultrasonic-like peaks
        if i % 100 == 0:
            value += 0.8
        signal.append(value)
    return signal

def test_ultrasonic_detection():
    """Test ultrasonic signature detection."""
    print("\nTesting ultrasonic signature detection...")
    
    # Create test signal
    test_signal = create_test_signal()
    
    if extensions_available:
        # Use performance extensions
        extensions = PerformanceExtensions()
        start_time = time.time()
        detected = extensions.detect_ultrasonic_signature(test_signal, 0.5)
        end_time = time.time()
        print(f"Detection result: {detected}")
        print(f"Time taken: {end_time - start_time:.6f} seconds")
    else:
        # Fallback to simple Python implementation
        print("Using fallback Python implementation...")
        # Simple detection algorithm
        average_power = sum(x*x for x in test_signal) / len(test_signal)
        peaks = 0
        for i in range(1, len(test_signal)-1):
            if (test_signal[i] > 0.5 and 
                test_signal[i] > test_signal[i-1] and 
                test_signal[i] > test_signal[i+1]):
                peaks += 1
        detected = (average_power > 0.25) and (peaks > 5)
        print(f"Detection result: {detected}")

def test_resonant_overload():
    """Test resonant frequency overload."""
    print("\nTesting resonant frequency overload...")
    
    # Create test signal
    test_signal = create_test_signal()
    
    if extensions_available:
        # Use performance extensions
        extensions = PerformanceExtensions()
        start_time = time.time()
        overloaded_signal = extensions.apply_resonant_overload(test_signal, 2417000000.0, 1000.0)
        end_time = time.time()
        print(f"Original signal length: {len(test_signal)}")
        print(f"Overloaded signal length: {len(overloaded_signal)}")
        print(f"Time taken: {end_time - start_time:.6f} seconds")
        print(f"First 3 original values: {test_signal[:3]}")
        print(f"First 3 overloaded values: {overloaded_signal[:3]}")
    else:
        # Fallback to simple Python implementation
        print("Using fallback Python implementation...")
        # Simple overload simulation
        overloaded_signal = []
        for i, value in enumerate(test_signal):
            resonant_component = 1000.0 * math.sin(2 * math.pi * 2417000000.0 * i / len(test_signal))
            new_value = value + resonant_component
            # Simple clipping
            if new_value > 1.0:
                new_value = 1.0
            elif new_value < -1.0:
                new_value = -1.0
            overloaded_signal.append(new_value)
        print(f"Original signal length: {len(test_signal)}")
        print(f"Overloaded signal length: {len(overloaded_signal)}")
        print(f"First 3 original values: {test_signal[:3]}")
        print(f"First 3 overloaded values: {overloaded_signal[:3]}")

def main():
    """Main test function."""
    print("Performance Extensions Test Suite")
    print("=" * 35)
    
    # Test ultrasonic detection
    test_ultrasonic_detection()
    
    # Test resonant overload
    test_resonant_overload()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()