import signal_processing_ext
import math

# Test the detect_ultrasonic_signature function
print("Testing detect_ultrasonic_signature function...")

# Create a test signal with ultrasonic characteristics
test_signal = []
for i in range(1000):
    # Base signal
    value = math.sin(2 * math.pi * 50 * i / 1000.0) + 0.5 * math.sin(2 * math.pi * 120 * i / 1000.0)
    # Add some ultrasonic-like peaks
    if i % 100 == 0:
        value += 0.8
    test_signal.append(value)

# Test detection
detected = signal_processing_ext.detect_ultrasonic_signature(test_signal, 0.5)
print(f"Ultrasonic signature detected: {detected}")

# Test the apply_resonant_overload function
print("\nTesting apply_resonant_overload function...")

# Apply resonant overload
overloaded_signal = signal_processing_ext.apply_resonant_overload(test_signal, 2417000000.0, 1000.0)
print(f"Original signal length: {len(test_signal)}")
print(f"Overloaded signal length: {len(overloaded_signal)}")
print(f"First 5 original values: {test_signal[:5]}")
print(f"First 5 overloaded values: {overloaded_signal[:5]}")

print("\nC extension tests completed successfully!")