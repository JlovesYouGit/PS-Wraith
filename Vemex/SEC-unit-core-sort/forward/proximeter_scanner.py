import subprocess
import re
import json
import time
from typing import List, Dict

class ProximeterScanner:
    """
    A scanner to detect nearby wireless devices and analyze their GHz band emissions
    within a specified range (2-4km) around the center radio device.
    """
    
    def __init__(self):
        self.devices = []
        
    def scan_wifi_devices(self) -> List[Dict]:
        """
        Scan for nearby WiFi devices using system tools.
        Returns a list of detected devices with their properties.
        """
        try:
            # On Windows, use netsh to scan for WiFi networks
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return self._parse_windows_wifi_output(result.stdout)
            else:
                print("Failed to scan WiFi networks")
                return []
                
        except subprocess.TimeoutExpired:
            print("WiFi scan timed out")
            return []
        except Exception as e:
            print(f"Error scanning WiFi devices: {e}")
            return []
    
    def _parse_windows_wifi_output(self, output: str) -> List[Dict]:
        """
        Parse the Windows netsh WiFi scan output.
        """
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
                        'bssids': []
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
    
    def _determine_band(self, channel: int) -> str:
        """
        Determine if the channel is in 2.4GHz or 5GHz band.
        """
        if 1 <= channel <= 14:
            return "2.4GHz"
        elif 36 <= channel <= 165:
            return "5GHz"
        else:
            return "Unknown"
    
    def estimate_distance(self, signal_percent: int) -> float:
        """
        Estimate distance in kilometers based on signal strength.
        This is a rough estimation and varies greatly based on environment.
        """
        # Convert percentage to dBm (rough approximation)
        signal_dbm = (signal_percent / 2) - 100
        
        # Free space path loss formula (simplified)
        # Distance = 10^((TxPower - RxPower - PathLossConstant) / (10 * PathLossExponent))
        # Using typical values for indoor WiFi:
        # TxPower ~ 20dBm, PathLossConstant ~ 30, PathLossExponent ~ 2.7
        tx_power = 20
        path_loss_constant = 30
        path_loss_exponent = 2.7
        
        if signal_dbm >= -30:
            return 0.001  # Very close (<1m)
        elif signal_dbm >= -50:
            return 0.01   # Close (1-10m)
        elif signal_dbm >= -60:
            return 0.1    # Medium (10-100m)
        elif signal_dbm >= -70:
            return 1.0    # Far (100m-1km)
        elif signal_dbm >= -80:
            return 2.0    # Very far (1-2km)
        else:
            return 5.0    # Extremely far (>2km)
    
    def filter_devices_by_distance_and_connection(self, devices: List[Dict], 
                                                min_distance_km: float = 2.0, 
                                                max_distance_km: float = 4.0) -> List[Dict]:
        """
        Filter devices that are:
        1. Within the specified distance range (2-4km)
        2. Not connected to the current router
        """
        filtered_devices = []
        
        # Get currently connected network SSID
        connected_ssid = self.get_connected_network()
        
        for device in devices:
            ssid = device.get('ssid', '')
            
            # Skip if this is the current network we're connected to
            if ssid == connected_ssid:
                continue
                
            # Check each BSSID of this network
            for bssid_info in device.get('bssids', []):
                signal = bssid_info.get('signal')
                if signal is not None:
                    estimated_distance = self.estimate_distance(signal)
                    
                    # Check if distance is within our range
                    if min_distance_km <= estimated_distance <= max_distance_km:
                        device_copy = device.copy()
                        device_copy['bssid_info'] = bssid_info
                        device_copy['estimated_distance_km'] = estimated_distance
                        filtered_devices.append(device_copy)
                        break  # We only need one BSSID that matches criteria
                        
        return filtered_devices
    
    def get_connected_network(self) -> str:
        """
        Get the SSID of the currently connected network.
        """
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                ssid_match = re.search(r'SSID\s*:\s*(.*)', result.stdout)
                if ssid_match:
                    return ssid_match.group(1).strip()
        except Exception:
            pass
            
        return ""
    
    def scan_and_filter_devices(self) -> List[Dict]:
        """
        Perform a complete scan and filter operation.
        """
        print("Scanning for WiFi devices...")
        devices = self.scan_wifi_devices()
        
        if not devices:
            print("No devices found.")
            return []
            
        print(f"Found {len(devices)} WiFi networks.")
        print("Filtering devices 2-4km away that are not connected to this router...")
        
        filtered_devices = self.filter_devices_by_distance_and_connection(
            devices, min_distance_km=2.0, max_distance_km=4.0
        )
        
        return filtered_devices
    
    def display_results(self, devices: List[Dict]):
        """
        Display the filtered results in a readable format.
        """
        if not devices:
            print("\nNo devices found within 2-4km that are not connected to this router.")
            return
            
        print(f"\nFound {len(devices)} devices within 2-4km not connected to this router:")
        print("-" * 80)
        
        for i, device in enumerate(devices, 1):
            ssid = device.get('ssid', 'Unknown')
            bssid_info = device.get('bssid_info', {})
            bssid = bssid_info.get('bssid', 'Unknown')
            signal = bssid_info.get('signal', 'Unknown')
            channel = bssid_info.get('channel', 'Unknown')
            band = bssid_info.get('band', 'Unknown')
            distance = device.get('estimated_distance_km', 'Unknown')
            
            print(f"{i}. SSID: {ssid}")
            print(f"   BSSID: {bssid}")
            print(f"   Signal Strength: {signal}%")
            print(f"   Channel: {channel}")
            print(f"   Band: {band}")
            print(f"   Estimated Distance: {distance} km")
            print()

def main():
    """
    Main function to run the proximeter scanner.
    """
    scanner = ProximeterScanner()
    devices = scanner.scan_and_filter_devices()
    scanner.display_results(devices)

if __name__ == "__main__":
    main()