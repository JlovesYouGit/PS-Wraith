#!/usr/bin/env python3
"""Neural data saver - save and reload AI learning data"""
import numpy as np
import json
import pickle
from pathlib import Path
import time

class NeuralDataManager:
    def __init__(self, ai_instance):
        self.ai = ai_instance
        self.data_dir = Path("N:/ROMLOADDER/ai_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.weights_file = self.data_dir / "neural_weights.pkl"
        self.patterns_file = self.data_dir / "success_patterns.json"
        self.history_file = self.data_dir / "exploit_history.json"
        self.device_profile = self.data_dir / "device_profile.json"
    
    def save_neural_weights(self):
        """Save neural network weights"""
        weights_data = {
            'W1': self.ai.W1.tolist(),
            'W2': self.ai.W2.tolist(),
            'learning_rate': self.ai.learning_rate,
            'timestamp': time.time()
        }
        
        with open(self.weights_file, 'wb') as f:
            pickle.dump(weights_data, f)
        
        print(f"[+] Neural weights saved: {self.weights_file}")
    
    def load_neural_weights(self):
        """Load neural network weights"""
        if self.weights_file.exists():
            try:
                with open(self.weights_file, 'rb') as f:
                    weights_data = pickle.load(f)
                
                self.ai.W1 = np.array(weights_data['W1'])
                self.ai.W2 = np.array(weights_data['W2'])
                self.ai.learning_rate = weights_data['learning_rate']
                
                print(f"[+] Neural weights loaded: {self.weights_file}")
                return True
            except Exception as e:
                print(f"[-] Weight loading failed: {e}")
        return False
    
    def save_success_patterns(self):
        """Save successful exploit patterns"""
        patterns_data = []
        
        for pattern in self.ai.success_patterns:
            pattern_dict = {
                'state': pattern['state'].tolist(),
                'actions': pattern['actions'],
                'reward': pattern['reward'],
                'timestamp': time.time()
            }
            patterns_data.append(pattern_dict)
        
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        print(f"[+] Success patterns saved: {len(patterns_data)} patterns")
    
    def load_success_patterns(self):
        """Load successful exploit patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                
                self.ai.success_patterns = []
                for pattern_dict in patterns_data:
                    pattern = {
                        'state': np.array(pattern_dict['state']),
                        'actions': pattern_dict['actions'],
                        'reward': pattern_dict['reward']
                    }
                    self.ai.success_patterns.append(pattern)
                
                print(f"[+] Success patterns loaded: {len(patterns_data)} patterns")
                return True
            except Exception as e:
                print(f"[-] Pattern loading failed: {e}")
        return False
    
    def save_device_profile(self):
        """Save device-specific profile"""
        profile = {
            'device_ecid': self.get_device_ecid(),
            'hardware_state_avg': np.mean(self.ai.hardware_state).tolist(),
            'target_addresses': self.ai.target_addresses,
            'successful_exploits': self.get_successful_exploits(),
            'boot_success_rate': self.calculate_boot_success_rate(),
            'timestamp': time.time()
        }
        
        with open(self.device_profile, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"[+] Device profile saved")
    
    def get_device_ecid(self):
        """Get device ECID for identification"""
        try:
            import subprocess
            result = subprocess.run([
                str(self.ai.irecovery), "-q"
            ], capture_output=True, text=True, timeout=3, cwd=str(self.ai.chargfast_dir))
            
            if "ECID:" in result.stdout:
                return result.stdout.split("ECID:")[1].split()[0].strip()
        except:
            pass
        return "unknown"
    
    def get_successful_exploits(self):
        """Get list of successful exploit addresses"""
        successful = []
        for pattern in self.ai.success_patterns:
            for action in pattern['actions']:
                if action['confidence'] > 0.7:
                    successful.append({
                        'address': action['address'],
                        'value': action['value'],
                        'confidence': action['confidence']
                    })
        return successful
    
    def calculate_boot_success_rate(self):
        """Calculate boot success rate"""
        if len(self.ai.exploit_history) == 0:
            return 0.0
        
        successes = sum(1 for h in self.ai.exploit_history if h.get('boot_success', False))
        return successes / len(self.ai.exploit_history)
    
    def save_all_data(self):
        """Save all AI learning data"""
        print("[+] SAVING ALL AI DATA")
        self.save_neural_weights()
        self.save_success_patterns()
        self.save_device_profile()
        print("[+] All AI data saved successfully")
    
    def load_all_data(self):
        """Load all AI learning data"""
        print("[+] LOADING ALL AI DATA")
        weights_loaded = self.load_neural_weights()
        patterns_loaded = self.load_success_patterns()
        
        if weights_loaded and patterns_loaded:
            print("[+] AI data loaded - continuing with learned knowledge")
            return True
        else:
            print("[+] No previous data - starting fresh")
            return False

# Enhanced Neural AI with data persistence
class PersistentNeuralAI:
    def __init__(self):
        # Import the original AI
        from neural_exploit_ai import NeuralExploitAI
        self.ai = NeuralExploitAI()
        self.data_manager = NeuralDataManager(self.ai)
        
        # Load previous learning data
        self.data_manager.load_all_data()
    
    def enhanced_exploit_loop(self, max_iterations=100):
        """Enhanced loop with data saving"""
        print("🧠 PERSISTENT NEURAL AI")
        print("Learning from previous attempts")
        print()
        
        for iteration in range(max_iterations):
            print(f"\n[AI] Iteration {iteration + 1}/{max_iterations}")
            
            # Run AI iteration
            state = self.ai.get_hardware_state()
            action_vector = self.ai.forward(state)
            success_count, actions = self.ai.execute_exploit_action(action_vector)
            boot_success = self.ai.attempt_boot()
            
            # Record attempt
            attempt_data = {
                'iteration': iteration,
                'state': state.tolist(),
                'actions': actions,
                'success_count': success_count,
                'boot_success': boot_success,
                'timestamp': time.time()
            }
            self.ai.exploit_history.append(attempt_data)
            
            # Learn from results
            overall_success = boot_success or (success_count > len(actions) * 0.7)
            self.ai.learn_from_result(state, actions, overall_success)
            
            # Save data every 10 iterations
            if (iteration + 1) % 10 == 0:
                print("[+] Saving AI progress...")
                self.data_manager.save_all_data()
            
            if boot_success:
                print("🎉 BOOT SUCCESS ACHIEVED!")
                self.data_manager.save_all_data()
                return True
            
            # Adaptive strategy based on learning
            if len(self.ai.success_patterns) > 5:
                print("[AI] Using learned patterns for next attempt")
                # Use best pattern
                best_pattern = max(self.ai.success_patterns, key=lambda x: x['reward'])
                self.ai.hardware_state = best_pattern['state']
            
            time.sleep(2)
        
        # Save final data
        self.data_manager.save_all_data()
        print("❌ All iterations completed - data saved for next run")
        return False

def main():
    """Main persistent AI"""
    ai = PersistentNeuralAI()
    
    print("🧠 PERSISTENT NEURAL AI EXPLOIT SYSTEM")
    print("Saves and reloads learning data")
    print("Gets smarter with each run")
    print()
    
    success = ai.enhanced_exploit_loop()
    
    if success:
        print("\n🎉 PERSISTENT AI SUCCESS!")
        print("✅ Learning data saved for future use")
    else:
        print("\n🔄 AI LEARNING SAVED")
        print("✅ Run again to continue with learned knowledge")
        print("✅ Each run makes the AI smarter")
    
    return success

if __name__ == "__main__":
    main()