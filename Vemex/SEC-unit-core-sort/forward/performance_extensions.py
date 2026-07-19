import ctypes
import os

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available, performance will be reduced")

# Try to import our C extension
try:
    import signal_processing_ext
    C_EXTENSION_AVAILABLE = True
except ImportError:
    C_EXTENSION_AVAILABLE = False
    print("Warning: C extension not available, using pure Python implementations")

class PerformanceExtensions:
    """
    Python interface to high-performance C and Rust extensions for threat elimination.
    """
    
    def __init__(self):
        # Load the C library
        self._load_c_library()
        
        # Load the Rust library (if available)
        self._load_rust_library()
        
        # Check if numpy is available
        self.numpy_available = NUMPY_AVAILABLE
        
        # Check if C extension is available
        self.c_extension_available = C_EXTENSION_AVAILABLE
    
    def _load_c_library(self):
        """
        Load the C extension library.
        """
        try:
            # Determine the library name based on the platform
            if os.name == 'nt':  # Windows
                lib_name = 'signal_processing.dll'
            else:  # Unix-like systems
                lib_name = 'libsignal_processing.so'
            
            # Try to load the library
            self.c_lib = ctypes.CDLL(lib_name)
            
            # Define function signatures
            self.c_lib.fast_fourier_transform.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int
            ]
            
            self.c_lib.detect_ultrasonic_signature.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int,
                ctypes.c_double
            ]
            self.c_lib.detect_ultrasonic_signature.restype = ctypes.c_int
            
            self.c_lib.apply_resonant_overload.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_double
            ]
            
            self.c_lib.generate_em_pulse.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_int
            ]
            
            self.c_lib.simulate_thermal_runaway.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_double
            ]
            
            print("C extension library loaded successfully")
        except Exception as e:
            print(f"Failed to load C extension library: {e}")
            self.c_lib = None
    
    def _load_rust_library(self):
        """
        Load the Rust extension library.
        """
        try:
            # Determine the library name based on the platform
            if os.name == 'nt':  # Windows
                lib_name = 'threat_elimination_core.dll'
            else:  # Unix-like systems
                lib_name = 'libthreat_elimination_core.so'
            
            # Try to load the library
            self.rust_lib = ctypes.CDLL(lib_name)
            
            # Define function signatures (same as C library)
            self.rust_lib.fast_fourier_transform_rust.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_ulong
            ]
            
            self.rust_lib.detect_ultrasonic_signature_rust.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_ulong,
                ctypes.c_double
            ]
            self.rust_lib.detect_ultrasonic_signature_rust.restype = ctypes.c_int
            
            self.rust_lib.apply_resonant_overload_rust.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_ulong,
                ctypes.c_double,
                ctypes.c_double
            ]
            
            self.rust_lib.generate_em_pulse_rust.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_ulong,
                ctypes.c_double,
                ctypes.c_ulong
            ]
            
            self.rust_lib.simulate_thermal_runaway_rust.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_ulong,
                ctypes.c_double,
                ctypes.c_double
            ]
            
            print("Rust extension library loaded successfully")
        except Exception as e:
            print(f"Failed to load Rust extension library: {e}")
            self.rust_lib = None
    
    def fast_fourier_transform(self, signal):
        """
        Perform fast Fourier transform using the best available implementation.
        """
        if isinstance(signal, np.ndarray):
            signal_array = signal.astype(np.float64)
        else:
            signal_array = np.array(signal, dtype=np.float64)
        
        result_array = np.zeros_like(signal_array)
        
        # Use Rust implementation if available, otherwise C, otherwise pure Python
        if self.rust_lib is not None:
            self.rust_lib.fast_fourier_transform_rust(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                result_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array)
            )
        elif self.c_lib is not None:
            self.c_lib.fast_fourier_transform(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                result_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array)
            )
        else:
            # Fallback to pure Python implementation
            result_array = np.abs(np.fft.fft(signal_array))
        
        return result_array
    
    def detect_ultrasonic_signature(self, signal, threshold=0.1):
        """
        Detect ultrasonic signatures using the best available implementation.
        """
        # Use our C extension if available
        if C_EXTENSION_AVAILABLE:
            return signal_processing_ext.detect_ultrasonic_signature(signal, threshold)
        
        # Fallback to existing implementations
        if isinstance(signal, np.ndarray):
            signal_array = signal.astype(np.float64)
        else:
            signal_array = np.array(signal, dtype=np.float64)
        
        # Use Rust implementation if available, otherwise C, otherwise pure Python
        if self.rust_lib is not None:
            result = self.rust_lib.detect_ultrasonic_signature_rust(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array),
                threshold
            )
            return bool(result)
        elif self.c_lib is not None:
            result = self.c_lib.detect_ultrasonic_signature(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array),
                threshold
            )
            return bool(result)
        else:
            # Fallback to pure Python implementation
            average_power = np.mean(signal_array ** 2)
            peaks = np.sum((signal_array[1:-1] > threshold) & 
                          (signal_array[1:-1] > signal_array[:-2]) & 
                          (signal_array[1:-1] > signal_array[2:]))
            return (average_power > threshold ** 2) and (peaks > 5)
    
    def apply_resonant_overload(self, signal, frequency=2417000000.0, intensity=1000.0):
        """
        Apply resonant frequency overload using the best available implementation.
        """
        # Use our C extension if available
        if C_EXTENSION_AVAILABLE:
            return signal_processing_ext.apply_resonant_overload(signal, frequency, intensity)
        
        # Fallback to existing implementations
        if isinstance(signal, np.ndarray):
            signal_array = signal.astype(np.float64)
        else:
            signal_array = np.array(signal, dtype=np.float64)
        
        # Use Rust implementation if available, otherwise C, otherwise pure Python
        if self.rust_lib is not None:
            self.rust_lib.apply_resonant_overload_rust(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array),
                frequency,
                intensity
            )
        elif self.c_lib is not None:
            self.c_lib.apply_resonant_overload(
                signal_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(signal_array),
                frequency,
                intensity
            )
        else:
            # Fallback to pure Python implementation
            t = np.arange(len(signal_array))
            resonant_component = intensity * np.sin(2 * np.pi * frequency * t / len(signal_array))
            signal_array += resonant_component
            
            # Apply non-linear distortion
            mask_high = signal_array > 0.9
            mask_low = signal_array < -0.9
            
            signal_array[mask_high] = 0.9 + 0.1 * np.tanh(signal_array[mask_high] - 0.9)
            signal_array[mask_low] = -0.9 + 0.1 * np.tanh(signal_array[mask_low] + 0.9)
        
        return signal_array
    
    def generate_em_pulse(self, length=100, intensity=10000.0, pulse_duration=50):
        """
        Generate a high-intensity electromagnetic pulse using the best available implementation.
        """
        result_array = np.zeros(length, dtype=np.float64)
        
        # Use Rust implementation if available, otherwise C, otherwise pure Python
        if self.rust_lib is not None:
            self.rust_lib.generate_em_pulse_rust(
                result_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                length,
                intensity,
                pulse_duration
            )
        elif self.c_lib is not None:
            self.c_lib.generate_em_pulse(
                result_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                length,
                intensity,
                pulse_duration
            )
        else:
            # Fallback to pure Python implementation
            t = np.arange(length)
            mask = t < pulse_duration
            t_normalized = t[mask] / pulse_duration
            result_array[mask] = intensity * np.exp(-((t_normalized - 0.5) ** 2) / 0.02)
        
        return result_array
    
    def simulate_thermal_runaway(self, initial_temperatures, power_input=100.0, thermal_resistance=0.5):
        """
        Simulate thermal runaway using the best available implementation.
        """
        if isinstance(initial_temperatures, np.ndarray):
            temp_array = initial_temperatures.astype(np.float64)
        else:
            temp_array = np.array(initial_temperatures, dtype=np.float64)
        
        # Use Rust implementation if available, otherwise C, otherwise pure Python
        if self.rust_lib is not None:
            self.rust_lib.simulate_thermal_runaway_rust(
                temp_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(temp_array),
                power_input,
                thermal_resistance
            )
        elif self.c_lib is not None:
            self.c_lib.simulate_thermal_runaway(
                temp_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                len(temp_array),
                power_input,
                thermal_resistance
            )
        else:
            # Fallback to pure Python implementation
            temp_rise = power_input * thermal_resistance
            temp_array += temp_rise
            
            # Add randomness
            random_factors = (np.random.random(len(temp_array)) - 0.5) * 10.0
            temp_array += random_factors
            
            # Cap at maximum temperature
            temp_array = np.minimum(temp_array, 300.0)
        
        return temp_array

# Example usage
if __name__ == "__main__":
    # Create an instance of the performance extensions
    extensions = PerformanceExtensions()
    
    # Test FFT
    test_signal = np.sin(2 * np.pi * 50 * np.arange(1000) / 1000.0) + \
                  0.5 * np.sin(2 * np.pi * 120 * np.arange(1000) / 1000.0)
    fft_result = extensions.fast_fourier_transform(test_signal)
    print("FFT completed successfully")
    
    # Test ultrasonic detection
    detected = extensions.detect_ultrasonic_signature(test_signal, 0.1)
    print(f"Ultrasonic signature detected: {detected}")
    
    # Test resonant overload
    overloaded_signal = extensions.apply_resonant_overload(test_signal, 2417000000.0, 1000.0)
    print("Resonant overload applied successfully")
    
    # Test EM pulse generation
    pulse = extensions.generate_em_pulse(100, 10000.0, 50)
    print("EM pulse generated successfully")
    
    # Test thermal runaway simulation
    initial_temps = np.full(10, 25.0)  # 10 components at 25°C
    final_temps = extensions.simulate_thermal_runaway(initial_temps, 100.0, 0.5)
    print("Thermal runaway simulation completed successfully")
    
    print("All performance extensions tested successfully!")