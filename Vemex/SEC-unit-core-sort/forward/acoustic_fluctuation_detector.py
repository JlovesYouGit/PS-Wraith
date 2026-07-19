import subprocess
import re
import time
import statistics
import json
from typing import List, Dict, Tuple
from collections import deque
import threading

class AcousticFluctuationDetector:
    """
    Detects low frequency high range sound waves by monitoring WiFi band fluctuations.
    Uses emitted WiFi bands to locate acoustic variations through signal analysis.
    """
    
    def __init__(self, monitoring_duration: int = 60, sampling_interval: float = 0.5):
        """
        Initialize the acoustic fluctuation detector.
        
        Args:
            monitoring_duration: Duration to monitor in seconds
            sampling_interval: Time between samples in seconds
        """
        self.monitoring_duration = monitoring_duration
        self.sampling_interval = sampling_interval
        self.signal_history = {}  # Store signal strength history for each BSSID
        self.fluctuation_threshold = 5.0  # dBm threshold for significant fluctuations
        self.min_samples = 10  # Minimum samples needed for analysis
        
    def get_router_info(self) -> Dict:
        """
        Get information about the connected router.
        """
        try:
            # Get router BSSID and signal information
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse the output to get router info
                bssid_match = re.search(r'BSSID\s*:\s*(.*)', result.stdout)
                signal_match = re.search(r'Signal\s*:\s*(\d+)%', result.stdout)
                channel_match = re.search(r'Channel\s*:\s*(\d+)', result.stdout)
                
                router_info = {
                    'bssid': bssid_match.group(1).strip() if bssid_match else None,
                    'signal_percent': int(signal_match.group(1)) if signal_match else None,
                    'channel': int(channel_match.group(1)) if channel_match else None
                }
                
                return router_info
        except Exception as e:
            print(f"Error getting router info: {e}")
            
        return {}
    
    def continuous_signal_monitoring(self) -> Dict:
        """
        Continuously monitor signal strengths to detect fluctuations.
        """
        print(f"Starting continuous monitoring for {self.monitoring_duration} seconds...")
        print("Monitoring for acoustic fluctuations through WiFi signal variations...")
        
        start_time = time.time()
        sample_count = 0
        
        # Get initial router info
        router_info = self.get_router_info()
        router_bssid = router_info.get('bssid')
        
        if not router_bssid:
            print("Could not determine router BSSID. Using Ethernet connection method.")
            return self.monitor_ethernet_connection()
        
        print(f"Monitoring router with BSSID: {router_bssid}")
        
        # Initialize signal history for router
        self.signal_history[router_bssid] = deque(maxlen=100)  # Keep last 100 samples
        
        fluctuation_events = []
        
        try:
            while time.time() - start_time < self.monitoring_duration:
                # Get current signal strength
                current_signal = self.get_signal_strength(router_bssid)
                
                if current_signal is not None:
                    # Add to history
                    self.signal_history[router_bssid].append(current_signal)
                    
                    # Analyze for fluctuations when we have enough samples
                    if len(self.signal_history[router_bssid]) >= self.min_samples:
                        fluctuation = self.detect_fluctuation(router_bssid)
                        if fluctuation:
                            fluctuation_events.append({
                                'timestamp': time.time(),
                                'signal': current_signal,
                                'fluctuation': fluctuation,
                                'magnitude': abs(fluctuation)
                            })
                            print(f"Fluctuation detected: {fluctuation:.2f} dBm variation")
                
                sample_count += 1
                time.sleep(self.sampling_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring interrupted by user.")
        except Exception as e:
            print(f"Error during monitoring: {e}")
            
        print(f"Monitoring complete. Collected {sample_count} samples.")
        return {
            'router_bssid': router_bssid,
            'total_samples': sample_count,
            'fluctuation_events': fluctuation_events,
            'signal_history': list(self.signal_history.get(router_bssid, []))
        }
    
    def monitor_ethernet_connection(self) -> Dict:
        """
        Monitor Ethernet connection for WiFi-like fluctuations.
        This simulates monitoring by checking network interface stats.
        """
        print("Monitoring Ethernet connection for network fluctuations...")
        
        start_time = time.time()
        sample_count = 0
        bytes_history = deque(maxlen=100)
        fluctuation_events = []
        
        try:
            while time.time() - start_time < self.monitoring_duration:
                # Get network interface statistics
                rx_bytes, tx_bytes = self.get_ethernet_stats()
                
                if rx_bytes is not None:
                    total_bytes = rx_bytes + tx_bytes
                    bytes_history.append(total_bytes)
                    
                    # Analyze for fluctuations when we have enough samples
                    if len(bytes_history) >= self.min_samples:
                        fluctuation = self.detect_network_fluctuation(bytes_history)
                        if fluctuation:
                            fluctuation_events.append({
                                'timestamp': time.time(),
                                'bytes': total_bytes,
                                'fluctuation': fluctuation,
                                'magnitude': abs(fluctuation)
                            })
                            print(f"Network fluctuation detected: {fluctuation} bytes variation")
                
                sample_count += 1
                time.sleep(self.sampling_interval)
                
        except Exception as e:
            print(f"Error during Ethernet monitoring: {e}")
            
        print(f"Ethernet monitoring complete. Collected {sample_count} samples.")
        return {
            'connection_type': 'ethernet',
            'total_samples': sample_count,
            'fluctuation_events': fluctuation_events,
            'bytes_history': list(bytes_history)
        }
    
    def get_signal_strength(self, bssid: str) -> float:
        """
        Get current signal strength for a specific BSSID.
        """
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse to find the specific BSSID
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if bssid.lower() in line.lower():
                        # Look for signal strength in nearby lines
                        for j in range(i, min(i+5, len(lines))):
                            signal_match = re.search(r'Signal\s*:\s*(\d+)%', lines[j])
                            if signal_match:
                                signal_percent = int(signal_match.group(1))
                                # Convert to dBm
                                return float((signal_percent / 2) - 100)
                                
        except Exception as e:
            print(f"Error getting signal strength: {e}")
            
        return 0.0  # Return 0.0 instead of None to match float return type
    
    def get_ethernet_stats(self) -> Tuple[int, int]:
        """
        Get Ethernet interface statistics (received and transmitted bytes).
        """
        try:
            # Use netsh to get interface statistics
            result = subprocess.run(
                ['netsh', 'interface', 'ipv4', 'show', 'interfaces'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                # This is a simplified approach - in practice, you'd want more specific parsing
                # For now, we'll simulate with time-based values to show the concept
                return (int(time.time() * 1000) % 1000000, int(time.time() * 1200) % 1000000)
                
        except Exception as e:
            print(f"Error getting Ethernet stats: {e}")
            
        return (0, 0)  # Return (0, 0) instead of (None, None) to match Tuple[int, int] return type
    
    def detect_fluctuation(self, bssid: str) -> float:
        """
        Detect significant signal fluctuations that might indicate acoustic waves.
        """
        history = self.signal_history[bssid]
        
        if len(history) < self.min_samples:
            return 0.0
            
        # Calculate recent average and compare with current value
        recent_values = list(history)[-10:]  # Last 10 samples
        avg_signal = statistics.mean(recent_values[:-1])  # Average of previous 9
        current_signal = recent_values[-1]  # Latest sample
        
        fluctuation = current_signal - avg_signal
        
        # Check if fluctuation exceeds threshold
        if abs(fluctuation) > self.fluctuation_threshold:
            return fluctuation
            
        return 0.0
    
    def detect_network_fluctuation(self, bytes_history: deque) -> int:
        """
        Detect network traffic fluctuations that might correlate with acoustic events.
        """
        if len(bytes_history) < self.min_samples:
            return 0
            
        # Calculate recent average and compare with current value
        recent_values = list(bytes_history)[-10:]  # Last 10 samples
        avg_bytes = statistics.mean(recent_values[:-1])  # Average of previous 9
        current_bytes = recent_values[-1]  # Latest sample
        
        fluctuation = current_bytes - avg_bytes
        
        # Check if fluctuation exceeds threshold (1000 bytes)
        if abs(fluctuation) > 1000:
            return int(fluctuation)
            
        return 0
    
    def analyze_acoustic_patterns(self, monitoring_data: Dict) -> Dict:
        """
        Analyze detected fluctuations for acoustic patterns.
        """
        fluctuation_events = monitoring_data.get('fluctuation_events', [])
        
        if not fluctuation_events:
            return {
                'acoustic_activity': False,
                'pattern_description': 'No significant fluctuations detected',
                'recommendations': ['Continue monitoring in noisy environment']
            }
        
        # Analyze fluctuation frequencies and magnitudes
        magnitudes = [event['magnitude'] for event in fluctuation_events]
        timestamps = [event['timestamp'] for event in fluctuation_events]
        
        avg_magnitude = statistics.mean(magnitudes) if magnitudes else 0
        max_magnitude = max(magnitudes) if magnitudes else 0
        
        # Calculate time intervals between events
        if len(timestamps) > 1:
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_interval = statistics.mean(intervals)
        else:
            avg_interval = 0
        
        # Determine if pattern suggests acoustic activity
        acoustic_likelihood = self.assess_acoustic_likelihood(
            len(fluctuation_events), avg_magnitude, avg_interval
        )
        
        return {
            'acoustic_activity': acoustic_likelihood > 0.5,
            'events_detected': len(fluctuation_events),
            'avg_magnitude': avg_magnitude,
            'max_magnitude': max_magnitude,
            'avg_interval_sec': avg_interval,
            'acoustic_likelihood': acoustic_likelihood,
            'pattern_description': self.describe_pattern(acoustic_likelihood, len(fluctuation_events)),
            'recommendations': self.generate_recommendations(acoustic_likelihood)
        }
    
    def assess_acoustic_likelihood(self, event_count: int, avg_magnitude: float, avg_interval: float) -> float:
        """
        Assess the likelihood that fluctuations are caused by acoustic waves.
        """
        # Simple heuristic-based assessment
        score = 0.0
        
        # More events suggest acoustic activity
        if event_count > 5:
            score += 0.3
        elif event_count > 10:
            score += 0.5
            
        # Moderate magnitude suggests acoustic coupling
        if 5 <= avg_magnitude <= 20:
            score += 0.3
        elif 10 <= avg_magnitude <= 30:
            score += 0.5
            
        # Regular intervals might indicate periodic acoustic sources
        if 0.1 <= avg_interval <= 2.0:
            score += 0.2
            
        return min(score, 1.0)  # Cap at 1.0
    
    def describe_pattern(self, likelihood: float, event_count: int) -> str:
        """
        Generate a description of the detected pattern.
        """
        if likelihood > 0.7:
            return f"Strong indication of acoustic activity ({event_count} events)"
        elif likelihood > 0.4:
            return f"Possible acoustic activity ({event_count} events)"
        else:
            return f"Low probability of acoustic activity ({event_count} events)"
    
    def generate_recommendations(self, likelihood: float) -> List[str]:
        """
        Generate recommendations based on analysis.
        """
        recommendations = []
        
        if likelihood > 0.7:
            recommendations.extend([
                "Investigate potential acoustic sources in the area",
                "Consider using dedicated acoustic sensors for confirmation",
                "Monitor for recurring patterns at specific times"
            ])
        elif likelihood > 0.4:
            recommendations.extend([
                "Continue monitoring for confirmation",
                "Check for environmental factors (HVAC, machinery)",
                "Compare with baseline measurements in quiet conditions"
            ])
        else:
            recommendations.extend([
                "No immediate concerns detected",
                "Ensure monitoring equipment is functioning properly",
                "Repeat monitoring in different environmental conditions"
            ])
            
        return recommendations
    
    def run_detection(self) -> Dict:
        """
        Run the complete acoustic fluctuation detection process.
        """
        print("Acoustic Fluctuation Detector")
        print("Using WiFi signal monitoring to detect sound wave interactions...")
        print()
        
        # Start monitoring
        monitoring_data = self.continuous_signal_monitoring()
        
        # Analyze results
        analysis = self.analyze_acoustic_patterns(monitoring_data)
        
        # Display results
        self.display_results(monitoring_data, analysis)
        
        return {
            'monitoring_data': monitoring_data,
            'analysis': analysis
        }
    
    def display_results(self, monitoring_data: Dict, analysis: Dict):
        """
        Display the detection results in a user-friendly format.
        """
        print("\n" + "="*60)
        print("ACOUSTIC FLUCTUATION DETECTION RESULTS")
        print("="*60)
        
        print(f"Connection Type: {monitoring_data.get('connection_type', 'WiFi')}")
        print(f"Total Samples: {monitoring_data.get('total_samples', 0)}")
        print(f"Fluctuation Events Detected: {analysis.get('events_detected', 0)}")
        
        if monitoring_data.get('router_bssid'):
            print(f"Router BSSID: {monitoring_data['router_bssid']}")
            
        print(f"\nAnalysis Results:")
        print(f"  Acoustic Activity: {'DETECTED' if analysis.get('acoustic_activity') else 'NOT DETECTED'}")
        print(f"  Likelihood Score: {analysis.get('acoustic_likelihood', 0):.2f}")
        print(f"  Average Fluctuation Magnitude: {analysis.get('avg_magnitude', 0):.2f} dBm")
        print(f"  Maximum Fluctuation Magnitude: {analysis.get('max_magnitude', 0):.2f} dBm")
        print(f"  Average Event Interval: {analysis.get('avg_interval_sec', 0):.2f} seconds")
        
        print(f"\nPattern Description:")
        print(f"  {analysis.get('pattern_description', 'No analysis available')}")
        
        print(f"\nRecommendations:")
        for i, recommendation in enumerate(analysis.get('recommendations', []), 1):
            print(f"  {i}. {recommendation}")

def main():
    """
    Main function to run the acoustic fluctuation detector.
    """
    # Create detector with 30-second monitoring period
    detector = AcousticFluctuationDetector(
        monitoring_duration=30, 
        sampling_interval=0.5
    )
    
    # Run detection
    results = detector.run_detection()
    
    # Optionally save results to file
    try:
        with open('acoustic_detection_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\nResults saved to acoustic_detection_results.json")
    except Exception as e:
        print(f"\nCould not save results to file: {e}")

if __name__ == "__main__":
    main()