use std::f64::consts::PI;

/// Perform a fast Fourier transform on signal data
/// This is a simplified implementation for demonstration purposes
#[no_mangle]
pub extern "C" fn fast_fourier_transform_rust(signal: *const f64, result: *mut f64, n: usize) {
    unsafe {
        let signal_slice = std::slice::from_raw_parts(signal, n);
        let result_slice = std::slice::from_raw_parts_mut(result, n);
        
        // Simplified FFT - in practice, you'd use a proper FFT library
        for i in 0..n {
            result_slice[i] = (signal_slice[i] * signal_slice[i]).sqrt();  // Magnitude calculation
        }
    }
}

/// Detect ultrasonic signatures in signal data
#[no_mangle]
pub extern "C" fn detect_ultrasonic_signature_rust(signal: *const f64, length: usize, threshold: f64) -> i32 {
    unsafe {
        let signal_slice = std::slice::from_raw_parts(signal, length);
        let mut ultrasonic_count = 0;
        let mut average_power = 0.0f64;
        
        // Calculate average power
        for &sample in signal_slice.iter() {
            average_power += sample * sample;
        }
        average_power /= length as f64;
        
        // Detect peaks above threshold
        for i in 1..length-1 {
            if signal_slice[i] > threshold && 
               signal_slice[i] > signal_slice[i-1] && 
               signal_slice[i] > signal_slice[i+1] {
                ultrasonic_count += 1;
            }
        }
        
        // Return 1 if ultrasonic signature detected, 0 otherwise
        if average_power > threshold * threshold && ultrasonic_count > 5 {
            1
        } else {
            0
        }
    }
}

/// Apply resonant frequency overload to a signal
#[no_mangle]
pub extern "C" fn apply_resonant_overload_rust(signal: *mut f64, length: usize, frequency: f64, intensity: f64) {
    unsafe {
        let signal_slice = std::slice::from_raw_parts_mut(signal, length);
        
        for (i, sample) in signal_slice.iter_mut().enumerate() {
            // Add resonant frequency component
            let resonant_component = intensity * (2.0 * PI * frequency * i as f64 / length as f64).sin();
            *sample += resonant_component;
            
            // Apply non-linear distortion to simulate overload
            if *sample > 0.9 {
                *sample = 0.9 + 0.1 * (sample - 0.9).tanh();
            } else if *sample < -0.9 {
                *sample = -0.9 + 0.1 * (sample + 0.9).tanh();
            }
        }
    }
}

/// Generate a high-intensity electromagnetic pulse
#[no_mangle]
pub extern "C" fn generate_em_pulse_rust(output: *mut f64, length: usize, intensity: f64, pulse_duration: usize) {
    unsafe {
        let output_slice = std::slice::from_raw_parts_mut(output, length);
        
        for (i, sample) in output_slice.iter_mut().enumerate() {
            if i < pulse_duration {
                // Gaussian pulse shape
                let t = i as f64 / pulse_duration as f64;
                *sample = intensity * (-((t - 0.5) * (t - 0.5)) / 0.02).exp();
            } else {
                *sample = 0.0;
            }
        }
    }
}

/// Simulate thermal runaway in electronic components
#[no_mangle]
pub extern "C" fn simulate_thermal_runaway_rust(temperatures: *mut f64, num_components: usize, power_input: f64, thermal_resistance: f64) {
    unsafe {
        let temp_slice = std::slice::from_raw_parts_mut(temperatures, num_components);
        
        for temp in temp_slice.iter_mut() {
            // Simple thermal model: temperature rise = power * thermal resistance
            let temp_rise = power_input * thermal_resistance;
            *temp += temp_rise;
            
            // Add some randomness to simulate component variations
            let random_factor = (rand::random::<f64>() - 0.5) * 10.0;
            *temp += random_factor;
            
            // Cap at maximum realistic temperature
            if *temp > 300.0 {
                *temp = 300.0;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ultrasonic_detection() {
        let signal = vec![0.1, 0.2, 0.8, 0.2, 0.1];  // Simple test signal
        let result = detect_ultrasonic_signature_rust(signal.as_ptr(), signal.len(), 0.5);
        assert_eq!(result, 0);  // Should not detect with this simple signal
    }
}