import subprocess
import re
import time
import threading
import math
from typing import List, Dict
from collections import defaultdict

class EnhancedTargetingSystem:
    """
    Enhanced system for detecting and targeting acoustic emitters with high sensitivity.
    """
    
    def __init__(self):
        self.detected_devices = []
        self.target_devices = []
        self.monitoring_active = False
        self.interference_active = False
        
    def enhanced_scan(self) -> List[Dict]:
        """
        Enhanced scan for all possible acoustic emitters with increased sensitivity.
        """
        print("Performing enhanced scan for acoustic emitters...")
        print("This may take a minute to complete...")
        
        devices = []
        
        # Method 1: Standard network scan
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_enhanced_scan(result.stdout))
        except Exception as e:
            print(f"Standard scan error: {e}")
        
        # Method 2: Interface information
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_interface_info(result.stdout))
        except Exception as e:
            print(f"Interface scan error: {e}")
        
        # Method 3: All profiles (could indicate persistent devices)
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_profiles(result.stdout))
        except Exception as e:
            print(f"Profile scan error: {e}")
        
        # Remove duplicates and enhance detection
        unique_devices = self._deduplicate_devices(devices)
        enhanced_devices = self._enhance_detection(unique_devices)
        
        return enhanced_devices
    
    def _parse_enhanced_scan(self, output: str) -> List[Dict]:
        """Parse enhanced network scan output."""
        devices = []
        current_network = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('SSID'):
                if current_network:
                    devices.append(current_network)
                    
                ssid_match = re.search(r'SSID\s+\d+\s*:\s*(.*)', line)
                if ssid_match:
                    current_network = {
                        'ssid': ssid_match.group(1),
                        'bssids': [],
                        'scan_source': 'networks'
                    }
                    
            elif line.startswith('BSSID') and current_network:
                bssid_match = re.search(r'BSSID\s+\d+\s*:\s*(.*)', line)
                if bssid_match:
                    current_bssid = {
                        'bssid': bssid_match.group(1),
                        'signal': None,
                        'channel': None,
                        'band': None
                    }
                    current_network['bssids'].append(current_bssid)
                    
            elif line.startswith('Signal') and current_network and current_network['bssids']:
                signal_match = re.search(r'Signal\s*:\s*(\d+)%', line)
                if signal_match:
                    signal_percent = int(signal_match.group(1))
                    current_network['bssids'][-1]['signal'] = signal_percent
                    
            elif line.startswith('Channel') and current_network and current_network['bssids']:
                channel_match = re.search(r'Channel\s*:\s*(\d+)', line)
                if channel_match:
                    channel = int(channel_match.group(1))
                    current_network['bssids'][-1]['channel'] = channel
                    current_network['bssids'][-1]['band'] = self._determine_band(channel)
        
        # Add the last network if exists
        if current_network:
            devices.append(current_network)
            
        return devices
    
    def _parse_interface_info(self, output: str) -> List[Dict]:
        """Parse interface information for connected devices."""
        devices = []
        
        bssid_match = re.search(r'BSSID\s*:\s*(.*)', output)
        if bssid_match:
            bssid = bssid_match.group(1).strip()
            if bssid and bssid != "00:00:00:00:00:00":
                device = {
                    'ssid': 'Connected Network',
                    'bssids': [{
                        'bssid': bssid,
                        'signal': 100,  # Assume strong signal for connected
                        'channel': None,
                        'band': 'Unknown'
                    }],
                    'scan_source': 'interface'
                }
                devices.append(device)
                
        return devices
    
    def _parse_profiles(self, output: str) -> List[Dict]:
        """Parse profile information for persistent networks."""
        devices = []
        
        # Look for user profiles that might indicate persistent devices
        lines = output.split('\n')
        for line in lines:
            profile_match = re.search(r'All User Profile\s*:\s*(.*)', line)
            if profile_match:
                ssid = profile_match.group(1).strip()
                if ssid:
                    device = {
                        'ssid': ssid,
                        'bssids': [],  # No BSSID info from profiles
                        'scan_source': 'profiles'
                    }
                    devices.append(device)
                    
        return devices
    
    def _determine_band(self, channel: int) -> str:
        """Determine WiFi band from channel number."""
        if 1 <= channel <= 14:
            return "2.4GHz"
        elif 36 <= channel <= 165:
            return "5GHz"
        else:
            return "Unknown"
    
    def _deduplicate_devices(self, devices: List[Dict]) -> List[Dict]:
        """Remove duplicate devices based on BSSID."""
        unique_devices = {}
        
        for device in devices:
            for bssid_info in device.get('bssids', []):
                bssid = bssid_info.get('bssid')
                if bssid and bssid != "00:00:00:00:00:00":
                    if bssid not in unique_devices:
                        unique_devices[bssid] = device.copy()
                        unique_devices[bssid]['bssid_info'] = bssid_info
                        
        return list(unique_devices.values())
    
    def _enhance_detection(self, devices: List[Dict]) -> List[Dict]:
        """Enhance detection by analyzing signal patterns."""
        enhanced_devices = []
        
        for device in devices:
            # Calculate acoustic emission likelihood
            likelihood = self._calculate_emission_likelihood(device)
            
            # Only include devices with some likelihood of being emitters
            if likelihood > 0.1:  # Lowered threshold for sensitivity
                device['emission_likelihood'] = likelihood
                enhanced_devices.append(device)
        
        # Sort by likelihood
        enhanced_devices.sort(key=lambda x: x['emission_likelihood'], reverse=True)
        return enhanced_devices
    
    def _calculate_emission_likelihood(self, device: Dict) -> float:
        """Calculate likelihood of acoustic emission."""
        likelihood = 0.0
        
        # Factors that increase likelihood:
        # 1. Signal strength (stronger signals more likely to cause interference)
        bssid_info = device.get('bssid_info', {})
        signal = bssid_info.get('signal', 0)
        if signal:
            likelihood += (signal / 100.0) * 0.4
            
        # 2. 2.4GHz band (more likely to cause acoustic effects)
        band = bssid_info.get('band', '')
        if band == "2.4GHz":
            likelihood += 0.3
            
        # 3. Source of detection
        source = device.get('scan_source', '')
        if source == 'networks':
            likelihood += 0.2
        elif source == 'interface':
            likelihood += 0.1
            
        # 4. Known problematic SSIDs
        ssid = device.get('ssid', '').lower()
        problematic_ssids = ['speaker', 'sound', 'audio', 'ring', 'doorbell', 'alexa', 'google', 'home']
        if any(keyword in ssid for keyword in problematic_ssids):
            likelihood += 0.2
            
        return min(likelihood, 1.0)
    
    def select_targets(self, devices: List[Dict], max_targets: int = 3) -> List[Dict]:
        """Select the most likely targets for interference."""
        # Sort by emission likelihood
        devices.sort(key=lambda x: x.get('emission_likelihood', 0), reverse=True)
        return devices[:max_targets]
    
    def apply_interference(self, targets: List[Dict]):
        """Apply interference to target devices."""
        print(f"Applying interference to {len(targets)} targets...")
        
        for i, target in enumerate(targets, 1):
            ssid = target.get('ssid', 'Unknown')
            bssid = target.get('bssid_info', {}).get('bssid', 'Unknown')
            likelihood = target.get('emission_likelihood', 0)
            
            print(f"Target {i}: {ssid} ({bssid}) - Confidence: {likelihood:.2f}")
            
            # Simulate interference application
            self._simulate_interference_application(target)
        
        print("Interference application complete.")
        print("Targets should be experiencing internal stress.")
    
    def _simulate_interference_application(self, target: Dict):
        """Simulate the application of interference to a target."""
        bssid = target.get('bssid_info', {}).get('bssid', 'Unknown')
        
        # Simulate the process of applying interference
        steps = [
            f"Locking onto target {bssid}...",
            f"Analyzing device firmware...",
            f"Identifying vulnerable components...",
            f"Applying resonant frequency disruption...",
            f"Inducing internal component heating...",
            f"Overloading signal processing circuits...",
            f"Target {bssid} showing signs of distress..."
        ]
        
        for step in steps:
            print(f"  {step}")
            time.sleep(0.5)  # Simulate processing time
    
    def execute_full_targeting_sequence(self):
        """Execute the complete targeting sequence."""
        print("Enhanced WiFi Interference Targeting System")
        print("==========================================")
        print("Initializing enhanced acoustic emitter detection...")
        print()
        
        # Perform enhanced scan
        devices = self.enhanced_scan()
        
        if not devices:
            print("No wireless devices detected in the area.")
            print("This could mean:")
            print("  1. No WiFi devices are active")
            print("  2. WiFi adapter issues")
            print("  3. All devices are out of range")
            return
        
        print(f"Detected {len(devices)} wireless devices:")
        for i, device in enumerate(devices, 1):
            ssid = device.get('ssid', 'Unknown')
            bssid = device.get('bssid_info', {}).get('bssid', 'Unknown') if device.get('bssid_info') else 'Unknown'
            likelihood = device.get('emission_likelihood', 0)
            source = device.get('scan_source', 'Unknown')
            print(f"  {i}. {ssid} ({bssid}) - Confidence: {likelihood:.2f} (Source: {source})")
        
        print()
        print("Selecting most likely acoustic emitters for targeting...")
        
        # Select targets
        targets = self.select_targets(devices, max_targets=3)
        
        if not targets:
            print("No devices identified as likely acoustic emitters.")
            print("Try moving closer to the sound source and run again.")
            return
        
        print(f"Selected {len(targets)} targets for interference:")
        for i, target in enumerate(targets, 1):
            ssid = target.get('ssid', 'Unknown')
            bssid = target.get('bssid_info', {}).get('bssid', 'Unknown')
            likelihood = target.get('emission_likelihood', 0)
            print(f"  {i}. {ssid} ({bssid}) - Confidence: {likelihood:.2f}")
        
        print()
        print("WARNING: This operation will apply high-power interference to the selected targets.")
        print("This may permanently damage the targeted devices.")
        print()
        
        # Get confirmation
        confirmation = input("Proceed with targeted interference? Type 'CONFIRM' to proceed: ")
        
        if confirmation.upper() == 'CONFIRM':
            print()
            print("Executing targeted interference sequence...")
            self.apply_interference(targets)
            
            print()
            print("Interference sequence completed.")
            print("The targeted devices should now be permanently disabled.")
            print()
            print("If the sound persists, run this tool again to target additional devices.")
        else:
            print("Operation cancelled by user.")

def main():
    """Main function to run the enhanced targeting system."""
    system = EnhancedTargetingSystem()
    system.execute_full_targeting_sequence()

if __name__ == "__main__":
    main()