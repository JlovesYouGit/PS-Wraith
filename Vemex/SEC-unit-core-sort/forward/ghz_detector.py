import subprocess
import re
import math
from typing import List, Dict

def detect_ghz_devices(min_distance_km: float = 2.0, max_distance_km: float = 4.0) -> List[Dict]:
    """
    Detect GHz band devices in the specified range that are not connected to this router.
    
    Args:
        min_distance_km: Minimum distance in kilometers (default: 2.0)
        max_distance_km: Maximum distance in kilometers (default: 4.0)
    
    Returns:
        List of dictionaries containing device information
    """
    # Get currently connected network
    connected_ssid = get_connected_network()
    print(f"Currently connected to: {connected_ssid or 'None'}")
    
    # Scan for WiFi networks
    print("Scanning for WiFi networks...")
    networks = scan_wifi_networks()
    
    # Filter GHz band devices in range
    ghz_devices = []
    
    for network in networks:
        ssid = network.get('ssid', '')
        
        # Skip if this is the current network we're connected to
        if ssid == connected_ssid:
            continue
            
        # Check each BSSID of this network
        for bssid_info in network.get('bssids', []):
            signal_dbm = bssid_info.get('signal_dbm')
            band = bssid_info.get('band')
            
            # Check if it's a GHz band device
            if band in ["2.4GHz", "5GHz"] and signal_dbm is not None:
                # Estimate frequency in GHz based on band
                frequency_ghz = 2.4 if band == "2.4GHz" else 5.0
                
                # Estimate distance
                estimated_distance = estimate_distance_from_signal(signal_dbm, frequency_ghz)
                
                # Check if distance is within our range
                if min_distance_km <= estimated_distance <= max_distance_km:
                    device_info = {
                        'ssid': ssid,
                        'bssid': bssid_info.get('bssid', 'Unknown'),
                        'signal_dbm': signal_dbm,
                        'channel': bssid_info.get('channel', 'Unknown'),
                        'band': band,
                        'frequency_ghz': frequency_ghz,
                        'estimated_distance_km': estimated_distance
                    }
                    ghz_devices.append(device_info)
                    break  # We only need one BSSID that matches criteria
    
    return ghz_devices

def scan_wifi_networks() -> List[Dict]:
    """
    Scan for WiFi networks using system tools.
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
            return parse_windows_wifi_output(result.stdout)
        else:
            print("Failed to scan WiFi networks")
            return []
            
    except subprocess.TimeoutExpired:
        print("WiFi scan timed out")
        return []
    except Exception as e:
        print(f"Error scanning WiFi devices: {e}")
        return []

def parse_windows_wifi_output(output: str) -> List[Dict]:
    """
    Parse the Windows netsh WiFi scan output.
    """
    networks = []
    current_network = None
    
    for line in output.split('\n'):
        line = line.strip()
        
        if line.startswith('SSID'):
            if current_network:
                networks.append(current_network)
                
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
                current_network['bssids'][-1]['band'] = determine_band(channel)
    
    # Add the last network if exists
    if current_network:
        networks.append(current_network)
        
    return networks

def determine_band(channel: int) -> str:
    """
    Determine if the channel is in 2.4GHz or 5GHz band.
    """
    if 1 <= channel <= 14:
        return "2.4GHz"
    elif 36 <= channel <= 165:
        return "5GHz"
    else:
        return "Unknown"

def estimate_distance_from_signal(signal_dbm: float, frequency_ghz: float = 2.4, 
                                 tx_power_dbm: float = 20.0) -> float:
    """
    Estimate distance in kilometers from received signal strength.
    Uses the free space path loss model.
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

def get_connected_network() -> str:
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

def display_results(devices: List[Dict], min_distance_km: float, max_distance_km: float):
    """
    Display the detection results.
    """
    print(f"\nGHz Band Devices Detected ({min_distance_km}-{max_distance_km}km range):")
    print("=" * 80)
    
    if not devices:
        print("No GHz band devices found in the specified range.")
        return
    
    print(f"Found {len(devices)} devices:")
    print()
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. SSID: {device['ssid']}")
        print(f"   BSSID: {device['bssid']}")
        print(f"   Signal Strength: {device['signal_dbm']} dBm")
        print(f"   Channel: {device['channel']}")
        print(f"   Band: {device['band']} ({device['frequency_ghz']} GHz)")
        print(f"   Estimated Distance: {device['estimated_distance_km']:.2f} km")
        print()

def main():
    """
    Main function to run the GHz detector.
    """
    print("GHz Band Device Detector")
    print("Detecting devices 2-4km away not connected to this router...")
    print()
    
    # Detect GHz band devices in the 2-4km range
    devices = detect_ghz_devices(min_distance_km=2.0, max_distance_km=4.0)
    
    # Display results
    display_results(devices, 2.0, 4.0)

if __name__ == "__main__":
    main()