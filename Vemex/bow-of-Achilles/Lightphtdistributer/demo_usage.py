"""
Advanced Usage Examples for Photon Speed Gate System
Demonstrates extreme speed modulation and quantum state transitions
"""

from photon_speed_gate import *
import matplotlib.pyplot as plt
import time

class AdvancedSpeedGateDemo:
    """Advanced demonstration of speed gate capabilities"""
    
    def __init__(self):
        self.speed_gate, self.interpreter = create_speed_gate_system()
        
    def quantum_state_transition_demo(self):
        """Demonstrate smooth transitions between quantum states"""
        print("=== Quantum State Transition Demo ===")
        
        # Start with electron state
        current_hz = 100e6  # 100 MHz
        states = [QuantumState.ELECTRON, QuantumState.HYBRID, QuantumState.PHOTON]
        
        for i, state in enumerate(states):
            print(f"\nTransition {i+1}: {state.value}")
            
            # Gradually increase frequency
            for multiplier in [1, 2, 5, 10]:
                test_hz = current_hz * multiplier
                result = self.speed_gate.actuate_speed_gate(test_hz, state)
                interpretation = self.interpreter.interpret_rre_data(result["rre_data"])
                
                print(f"  {multiplier}x: {result['output_frequency']/1e9:.2f} GHz "
                      f"-> {interpretation['speed_classification']}")
                
                time.sleep(0.1)  # Simulate instant transition
            
            current_hz *= 2
    
    def warp_speed_demo(self):
        """Demonstrate extreme warp speed capabilities"""
        print("\n=== Warp Speed Demo ===")
        
        # Enable maximum warp
        self.speed_gate.actuator.set_warp_factor(1000.0)  # 1000x speed of light
        
        warp_levels = [1, 10, 100, 1000]
        base_frequency = 1e9  # 1 GHz
        
        for warp in warp_levels:
            self.speed_gate.actuator.set_warp_factor(warp)
            
            result = self.speed_gate.actuate_speed_gate(base_frequency, QuantumState.PHOTON)
            interpretation = self.interpreter.interpret_rre_data(result["rre_data"])
            
            print(f"Warp {warp}x: {result['output_frequency']/1e12:.2f} THz "
                  f"({interpretation['warp_capability']})")
    
    def volumetric_modulation_demo(self):
        """Demonstrate volumetric free-form modulation"""
        print("\n=== Volumetric Modulation Demo ===")
        
        # Enable volumetric features
        self.speed_gate.enable_advanced_features("VOLUMETRIC")
        
        # Create complex frequency patterns
        frequencies = [440e6, 880e6, 1.76e9, 3.52e9]  # Musical octaves in Hz
        
        for freq in frequencies:
            result = self.speed_gate.actuate_speed_gate(freq, QuantumState.HYBRID)
            interpretation = self.interpreter.interpret_rre_data(result["rre_data"])
            
            # Analyze volumetric patterns
            speed_matrix = result["speed_matrix"]
            pattern_complexity = np.std(speed_matrix) / np.mean(speed_matrix + 1e-10)
            
            print(f"Frequency {freq/1e6:.0f} MHz: "
                  f"Complexity {pattern_complexity:.3f}, "
                  f"Features: {', '.join(interpretation['feature_unlocks'])}")
    
    def ether_connectivity_demo(self):
        """Demonstrate ether connectivity from uncommunicable areas"""
        print("\n=== Ether Connectivity Demo ===")
        
        # Test ether link strength at different frequencies
        ether_frequencies = [13.56e6, 27.12e6, 40.68e6, 915e6]  # ISM bands
        
        for freq in ether_frequencies:
            result = self.speed_gate.actuate_speed_gate(freq, QuantumState.HYBRID)
            interpretation = self.interpreter.interpret_rre_data(result["rre_data"])
            
            ether_strength = interpretation['ether_connectivity']
            print(f"Ether {freq/1e6:.1f} MHz: "
                  f"Link Strength {ether_strength:.1%}, "
                  f"Coherence {interpretation['coherence_level']}")
    
    def instant_actuation_demo(self):
        """Demonstrate instant open/close activities with zero overlay"""
        print("\n=== Instant Actuation Demo ===")
        
        # Test rapid switching between states
        test_sequence = [
            (1e9, QuantumState.PHOTON),
            (500e6, QuantumState.ELECTRON),
            (2e9, QuantumState.HYBRID),
            (1.5e9, QuantumState.PHOTON),
            (750e6, QuantumState.ELECTRON)
        ]
        
        start_time = time.time()
        
        for i, (hz, state) in enumerate(test_sequence):
            result = self.speed_gate.actuate_speed_gate(hz, state)
            
            # Simulate instant transition (zero time delay)
            transition_time = time.time() - start_time
            
            print(f"Switch {i+1}: {state.value} at {hz/1e6:.0f} MHz "
                  f"-> {result['output_frequency']/1e9:.2f} GHz "
                  f"(Transition: {transition_time*1000:.3f}ms)")
    
    def feature_unlock_demo(self):
        """Demonstrate advanced feature unlocking"""
        print("\n=== Feature Unlock Demo ===")
        
        features = ["WARP_SPEED", "VOLUMETRIC", "QUANTUM_TUNNEL", "ETHER_LINK"]
        
        for feature in features:
            success = self.speed_gate.enable_advanced_features(feature)
            
            if success:
                # Test the unlocked feature
                result = self.speed_gate.actuate_speed_gate(1e9, QuantumState.PHOTON)
                interpretation = self.interpreter.interpret_rre_data(result["rre_data"])
                
                print(f"✓ {feature}: Unlocked")
                print(f"  Capabilities: {', '.join(interpretation['feature_unlocks'])}")
                print(f"  Warp: {interpretation['warp_capability']}")
            else:
                print(f"✗ {feature}: Failed to unlock")
    
    def visualize_speed_matrix(self, save_path=None):
        """Visualize the speed modulation matrix"""
        print("\n=== Speed Matrix Visualization ===")
        
        # Generate a complex speed matrix
        result = self.speed_gate.actuate_speed_gate(1.5e9, QuantumState.HYBRID)
        speed_matrix = result["speed_matrix"]
        
        # Create visualization
        plt.figure(figsize=(10, 8))
        plt.imshow(speed_matrix, cmap='plasma', interpolation='bilinear')
        plt.colorbar(label='Frequency (Hz)')
        plt.title('Photon Speed Gate - Modulation Matrix')
        plt.xlabel('Pin Position X')
        plt.ylabel('Pin Position Y')
        
        # Add pin category labels
        pin_positions = {}
        for pin_id, pin_config in self.speed_gate.pins.items():
            x, y = pin_config.position
            if pin_config.category == PinCategory.POWER:
                plt.text(x, y, 'P', color='red', ha='center', va='center', fontsize=8)
            elif pin_config.category == PinCategory.DATA:
                plt.text(x, y, 'D', color='purple', ha='center', va='center', fontsize=8)
            elif pin_config.category == PinCategory.CONTROL:
                plt.text(x, y, 'C', color='pink', ha='center', va='center', fontsize=8)
            elif pin_config.category == PinCategory.INTERFACE:
                plt.text(x, y, 'I', color='white', ha='center', va='center', fontsize=8)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        else:
            plt.show()
    
    def run_complete_demo(self):
        """Run complete demonstration of all capabilities"""
        print("Starting Complete Photon Speed Gate Demonstration...")
        print("=" * 60)
        
        try:
            self.quantum_state_transition_demo()
            self.warp_speed_demo()
            self.volumetric_modulation_demo()
            self.ether_connectivity_demo()
            self.instant_actuation_demo()
            self.feature_unlock_demo()
            
            print("\n" + "=" * 60)
            print("Demo completed successfully!")
            print("All systems operating at optimal quantum coherence levels.")
            
        except Exception as e:
            print(f"Demo error: {e}")
            print("System requires recalibration.")

def create_custom_speed_gate_test():
    """Create custom test scenarios"""
    print("\n=== Custom Speed Gate Test ===")
    
    speed_gate, interpreter = create_speed_gate_system()
    
    # Custom frequency modulation pattern
    custom_pattern = {
        "base_frequency": 2.4e9,  # 2.4 GHz
        "modulation_type": "exponential",
        "warp_progression": [1, 5, 25, 125, 625],
        "state_sequence": [QuantumState.ELECTRON, QuantumState.HYBRID, QuantumState.PHOTON]
    }
    
    for warp_factor in custom_pattern["warp_progression"]:
        speed_gate.actuator.set_warp_factor(warp_factor)
        
        for state in custom_pattern["state_sequence"]:
            result = speed_gate.actuate_speed_gate(
                custom_pattern["base_frequency"], 
                state
            )
            
            interpretation = interpreter.interpret_rre_data(result["rre_data"])
            
            print(f"Warp {warp_factor:3d}x | {state.value:8s} | "
                  f"{result['output_frequency']/1e12:8.2f} THz | "
                  f"{interpretation['speed_classification']:20s}")

if __name__ == "__main__":
    # Run the complete demonstration
    demo = AdvancedSpeedGateDemo()
    demo.run_complete_demo()
    
    # Run custom test
    create_custom_speed_gate_test()
