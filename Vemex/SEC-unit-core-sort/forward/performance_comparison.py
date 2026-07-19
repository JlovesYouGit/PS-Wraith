#!/usr/bin/env python3

"""
Performance comparison between pure Python and C extension implementations.
"""

import time
import math
import random

# Try to import our C extension
try:
    import signal_processing_ext
    C_EXTENSION_AVAILABLE = True
    print("C extension available for performance comparison")
except ImportError:
    C_EXTENSION_AVAILABLE = False
    print("C extension not available, using pure Python only")

def pure_python_detect_ultrasonic_signature(signal, threshold=0.1):
    """
    Pure Python implementation of ultrasonic signature detection.
    """
    # Calculate average power
    average_power = sum(x * x for x in signal) / len(signal)
    
    # Detect peaks above threshold
    peaks = 0
    for i in range(1, len(signal) - 1):
        if (signal[i] > threshold and 
            signal[i] > signal[i-1] and 
            signal[i] > signal[i+1]):
            peaks += 1
    
    # Return detection result
    return (average_power > threshold * threshold) and (peaks > 5)

def pure_python_apply_resonant_overload(signal, frequency=2417000000.0, intensity=1000.0):
    """
    Pure Python implementation of resonant frequency overload.
    """
    overloaded_signal = []
    length = len(signal)
    
    for i, value in enumerate(signal):
        # Add resonant frequency component
        resonant_component = intensity * math.sin(2 * math.pi * frequency * i / length)
        new_value = value + resonant_component
        
        # Apply non-linear distortion to simulate overload
        if new_value > 0.9:
            new_value = 0.9 + 0.1 * math.tanh(new_value - 0.9)
        elif new_value < -0.9:
            new_value = -0.9 + 0.1 * math.tanh(new_value + 0.9)
            
        overloaded_signal.append(new_value)
    
    return overloaded_signal

def create_large_test_signal(size=100000):
    """
    Create a large test signal for performance testing.
    """
    signal = []
    for i in range(size):
        # Base signal
        value = (math.sin(2 * math.pi * 50 * i / size) + 
                0.5 * math.sin(2 * math.pi * 120 * i / size) +
                0.3 * math.sin(2 * math.pi * 2417 * i / size))
        # Add noise
        value += (random.random() - 0.5) * 0.1
        signal.append(value)
    return signal

def main():
    """
    Main function to compare performance.
    """
    print("Performance Comparison: Pure Python vs C Extension")
    print("=" * 50)
    
    # Create a large test signal
    print("Creating test signal...")
    test_signal = create_large_test_signal(50000)  # 50,000 samples
    print(f"Test signal size: {len(test_signal)} samples")
    print()
    
    # Test pure Python implementation
    print("Testing pure Python implementation...")
    start_time = time.time()
    detected_py = pure_python_detect_ultrasonic_signature(test_signal, 0.1)
    python_detection_time = time.time() - start_time
    print(f"Detection result: {detected_py}")
    print(f"Python detection time: {python_detection_time:.6f} seconds")
    
    start_time = time.time()
    overloaded_signal_py = pure_python_apply_resonant_overload(test_signal, 2417000000.0, 1000.0)
    python_overload_time = time.time() - start_time
    print(f"Python overload time: {python_overload_time:.6f} seconds")
    print()
    
    # Test C extension if available
    if C_EXTENSION_AVAILABLE:
        print("Testing C extension implementation...")
        start_time = time.time()
        detected_c = signal_processing_ext.detect_ultrasonic_signature(test_signal, 0.1)
        c_detection_time = time.time() - start_time
        print(f"Detection result: {detected_c}")
        print(f"C extension detection time: {c_detection_time:.6f} seconds")
        
        start_time = time.time()
        overloaded_signal_c = signal_processing_ext.apply_resonant_overload(test_signal, 2417000000.0, 1000.0)
        c_overload_time = time.time() - start_time
        print(f"C extension overload time: {c_overload_time:.6f} seconds")
        print()
        
        # Calculate performance improvements
        if c_detection_time > 0:
            detection_speedup = python_detection_time / c_detection_time
            print(f"Detection speedup: {detection_speedup:.2f}x faster")
        
        if c_overload_time > 0:
            overload_speedup = python_overload_time / c_overload_time
            print(f"Overload speedup: {overload_speedup:.2f}x faster")
    else:
        print("C extension not available for comparison")
    
    print()
    print("Performance comparison completed!")

if __name__ == "__main__":
    main()