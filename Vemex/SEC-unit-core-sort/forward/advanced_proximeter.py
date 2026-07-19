import subprocess
import re
import json
import time
import math
from typing import List, Dict, Tuple

class AdvancedProximeterScanner:
    """
    An advanced scanner to detect nearby wireless devices emitting GHz band signals
    within a 2-4km radius around the center radio device, excluding those connected to this router.
    """
    
    def __init__(self):
        # GHz band channels mapping
        self.band_channels = {
            "2.4GHz": list(range(1, 15)),  # Channels 1-14
            "5GHz": list(range(36, 166, 4)) + [165]  # Common 5GHz channels
        }
        
    def scan_wireless_devices(self) -> List[Dict]:
        """
        Scan for all nearby wireless devices using system tools.
        Returns detailed information about each device.
        """
        devices = []
        
        try:
            # Try different methods depending on the OS
            import platform
            system = platform.system().lower()
            
            if system == "windows":
                devices = self._scan_windows_devices()
            else:
                devices = self._scan_unix_devices()
                
        except Exception as e:
            print(f"Error scanning wireless devices: {e}")
            
        return devices
    
    def _scan_windows_devices(self) -> List[Dict]:
        """
        Scan for wireless devices on Windows systems.
        """
        devices = []
        
        try:
            # Scan for WiFi networks with BSSID details
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_netsh_output(result.stdout))
                
        except Exception as e:
            print(f"Error in Windows WiFi scan: {e}")
            
        return devices
    
    def _scan_unix_devices(self) -> List[Dict]:
        """
        Scan for wireless devices on Unix-like systems (Linux/Mac).
        """
        devices = []
        
        try:
            # Try using iwlist (Linux)
            result = subprocess.run(
                ['iwlist', 'scan'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_iwlist_output(result.stdout))
                return devices
        except FileNotFoundError:
            pass  # iwlist not available
        except Exception as e:
            print(f"Error with iwlist: {e}")
            
        try:
            # Try using airport (Mac)
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                devices.extend(self._parse_airport_output(result.stdout))
                return devices
        except FileNotFoundError:
            pass  # airport not available
        except Exception as e:
            print(f"Error with airport: {e}")
            
        return devices
    
    def _parse_netsh_output(self, output: str) -> List[Dict]:
        """
        Parse Windows netsh WiFi scan output.
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
                        'signal_dbm': None,
                        'channel': None,
                        'band': None
                    }
                    current_network['bssids'].append(current_bssid)
                    
            elif line.startswith('Signal') and current_network and current_network['bssids']:
                signal_match = re.search(r'Signal\s*:\s*(\d+)%', line)
                if signal_match:
                    signal_percent = int(signal_match.group(1))
                    # Convert percentage to dBm
                    signal_dbm = (signal_percent / 2) - 100
                    current_network['bssids'][-1]['signal_dbm'] = signal_dbm
                    
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
    
    def _parse_iwlist_output(self, output: str) -> List[Dict]:
        """
        Parse Linux iwlist scan output.
        """
        devices = []
        current_cell = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            cell_match = re.search(r'Cell\s+(\d+)\s+-\s+Address:\s+(.*)', line)
            if cell_match:
                if current_cell:
                    devices.append(current_cell)
                    
                current_cell = {
                    'bssid': cell_match.group(2),
                    'ssid': '',
                    'signal_dbm': None,
                    'channel': None,
                    'band': None
                }
                
            elif line.startswith('ESSID:') and current_cell:
                essid_match = re.search(r'ESSID:"(.*)"', line)
                if essid_match:
                    current_cell['ssid'] = essid_match.group(1)
                    
            elif line.startswith('Channel:') and current_cell:
                channel_match = re.search(r'Channel:(\d+)', line)
                if channel_match:
                    channel = int(channel_match.group(1))
                    current_cell['channel'] = channel
                    current_cell['band'] = self._determine_band(channel)
                    
            elif line.startswith('Quality=') and current_cell:
                quality_match = re.search(r'Signal level=(-?\d+) dBm', line)
                if quality_match:
                    current_cell['signal_dbm'] = int(quality_match.group(1))
        
        # Add the last cell if exists
        if current_cell:
            devices.append(current_cell)
            
        # Convert single device format to network format
        networks = []
        for device in devices:
            network = {
                'ssid': device['ssid'],
                'bssids': [{
                    'bssid': device['bssid'],
                    'signal_dbm': device['signal_dbm'],
                    'channel': device['channel'],
                    'band': device['band']
                }]
            }
            networks.append(network)
            
        return networks
    
    def _parse_airport_output(self, output: str) -> List[Dict]:
        """
        Parse Mac airport scan output.
        """
        devices = []
        lines = output.split('\n')
        
        # Skip header lines
        data_lines = lines[1:] if len(lines) > 1 else []
        
        for line in data_lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    ssid = parts[0]
                    bssid = parts[1]
                    rssi = parts[2]
                    channel = parts[3]
                    
                    try:
                        signal_dbm = int(rssi)
                        channel_num = int(channel.split(',')[0])  # Handle channel,width format
                        
                        network = {
                            'ssid': ssid,
                            'bssids': [{
                                'bssid': bssid,
                                'signal_dbm': signal_dbm,
                                'channel': channel_num,
                                'band': self._determine_band(channel_num)
                            }]
                        }
                        devices.append(network)
                    except ValueError:
                        continue
                        
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
    
    def calculate_free_space_path_loss(self, frequency_ghz: float, distance_km: float) -> float:
        """
        Calculate free space path loss (FSPL) in dB.
        FSPL = 20*log10(d) + 20*log10(f) + 32.45
        where d is distance in km and f is frequency in GHz
        """
        if distance_km <= 0 or frequency_ghz <= 0:
            return 0
            
        fspl = 20 * math.log10(distance_km) + 20 * math.log10(frequency_ghz * 1000) + 32.45
        return fspl
    
    def estimate_distance_from_signal(self, signal_dbm: float, frequency_ghz: float = 2.4, 
                                     tx_power_dbm: float = 20.0) -> float:
        """
        Estimate distance in kilometers from received signal strength.
        Uses the free space path loss model:
        Distance = 10^((TxPower - RxPower - 32.45 - 20*log10(f*1000)) / 20)
        where f is in GHz
        """
        if signal_dbm >= tx_power_dbm:
            return 0.001  # Very close
            
        try:
            # Calculate distance using FSPL formula rearranged
            exponent = (tx_power_dbm - signal_dbm - 32.45 - 20 * math.log10(frequency_ghz * 1000)) / 20
            distance_km = math.pow(10, exponent)
            return min(distance_km, 10.0)  # Cap at 10km
        except (ValueError, OverflowError):
            return 5.0  # Return default if calculation fails
    
    def filter_ghz_devices_in_range(self, devices: List[Dict], 
                                   min_distance_km: float = 2.0, 
                                   max_distance_km: float = 4.0) -> List[Dict]:
        """
        Filter devices that:
        1. Are emitting GHz band signals (2.4GHz or 5GHz)
        2. Are within the specified distance range (2-4km)
        3. Are not connected to the current router
        """
        filtered_devices = []
        
        # Get currently connected network
        connected_ssid = self.get_connected_network()
        
        for device in devices:
            ssid = device.get('ssid', '')
            
            # Skip if this is the current network we're connected to
            if ssid == connected_ssid:
                continue
                
            # Check each BSSID of this network
            for bssid_info in device.get('bssids', []):
                signal_dbm = bssid_info.get('signal_dbm')
                band = bssid_info.get('band')
                channel = bssid_info.get('channel')
                
                # Check if it's a GHz band device
                if band in ["2.4GHz", "5GHz"] and signal_dbm is not None:
                    # Estimate frequency in GHz based on band
                    frequency_ghz = 2.4 if band == "2.4GHz" else 5.0
                    
                    # Estimate distance
                    estimated_distance = self.estimate_distance_from_signal(
                        signal_dbm, frequency_ghz
                    )
                    
                    # Check if distance is within our range
                    if min_distance_km <= estimated_distance <= max_distance_km:
                        device_copy = device.copy()
                        device_copy['bssid_info'] = bssid_info
                        device_copy['estimated_distance_km'] = estimated_distance
                        device_copy['frequency_ghz'] = frequency_ghz
                        filtered_devices.append(device_copy)
                        break  # We only need one BSSID that matches criteria
                        
        return filtered_devices
    
    def get_connected_network(self) -> str:
        """
        Get the SSID of the currently connected network.
        """
        try:
            import platform
            system = platform.system().lower()
            
            if system == "windows":
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
                        
            else:  # Unix-like systems
                try:
                    # Try using iwconfig
                    result = subprocess.run(
                        ['iwconfig'], 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        ssid_match = re.search(r'ESSID:"(.*)"', result.stdout)
                        if ssid_match:
                            return ssid_match.group(1)
                except FileNotFoundError:
                    pass
                    
                try:
                    # Try using networksetup (Mac)
                    result = subprocess.run(
                        ['networksetup', '-getairportnetwork', 'en0'], 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        network_match = re.search(r'Current Wi-Fi Network:\s*(.*)', result.stdout)
                        if network_match:
                            return network_match.group(1).strip()
                except FileNotFoundError:
                    pass
                    
        except Exception:
            pass
            
        return ""
    
    def scan_and_analyze(self) -> List[Dict]:
        """
        Perform a complete scan and analysis operation.
        """
        print("Scanning for wireless devices...")
        devices = self.scan_wireless_devices()
        
        if not devices:
            print("No devices found.")
            return []
            
        print(f"Found {len(devices)} wireless networks.")
        print("Analyzing GHz band devices 2-4km away that are not connected to this router...")
        
        ghz_devices = self.filter_ghz_devices_in_range(
            devices, min_distance_km=2.0, max_distance_km=4.0
        )
        
        return ghz_devices
    
    def display_detailed_results(self, devices: List[Dict]):
        """
        Display detailed results of the scan.
        """
        if not devices:
            print("\nNo GHz band devices found within 2-4km that are not connected to this router.")
            return
            
        print(f"\nFound {len(devices)} GHz band devices within 2-4km not connected to this router:")
        print("=" * 90)
        
        for i, device in enumerate(devices, 1):
            ssid = device.get('ssid', 'Unknown')
            bssid_info = device.get('bssid_info', {})
            bssid = bssid_info.get('bssid', 'Unknown')
            signal_dbm = bssid_info.get('signal_dbm', 'Unknown')
            channel = bssid_info.get('channel', 'Unknown')
            band = bssid_info.get('band', 'Unknown')
            frequency = device.get('frequency_ghz', 'Unknown')
            distance = device.get('estimated_distance_km', 'Unknown')
            
            print(f"{i}. SSID: {ssid}")
            print(f"   BSSID (MAC): {bssid}")
            print(f"   Signal Strength: {signal_dbm} dBm")
            print(f"   Channel: {channel}")
            print(f"   Band: {band} ({frequency} GHz)")
            print(f"   Estimated Distance: {distance:.2f} km")
            print()

def main():
    """
    Main function to run the advanced proximeter scanner.
    """
    print("Advanced Proximeter Scanner for GHz Band Device Detection")
    print("Detecting devices 2-4km away not connected to this router...")
    print()
    
    scanner = AdvancedProximeterScanner()
    devices = scanner.scan_and_analyze()
    scanner.display_detailed_results(devices)

if __name__ == "__main__":
    main()