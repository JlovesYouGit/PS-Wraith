#!/usr/bin/env python3
"""
Enhanced WiFi scanner with spectrum analysis techniques to boost detection range.
Uses advanced netsh commands and signal analysis to find more distant access points.
"""

import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from spectrum_grabber.wifi_scanner import AccessPoint, WiFiScanError


@dataclass
class EnhancedAccessPoint(AccessPoint):
    """Extended AccessPoint with additional spectrum analysis data."""

    rssi_dbm: Optional[int] = None
    noise_floor: Optional[int] = None
    snr: Optional[int] = None
    beacon_interval: Optional[int] = None
    capabilities: Optional[str] = None
    vendor: Optional[str] = None


class SpectrumAnalyzer:
    """Advanced WiFi spectrum analysis for extended range detection."""

    def __init__(self):
        self.oui_database = self._load_oui_database()

    def _load_oui_database(self) -> dict[str, str]:
        """Load basic OUI (vendor) database for MAC address identification."""
        return {
            'c8:70:23': 'Netgear',
            '80:69:1a': 'Linksys',
            '00:1b:63': 'Apple',
            '00:26:bb': 'Apple',
            'ac:87:a3': 'Apple',
            '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox',
            '00:0c:29': 'VMware',
            '00:15:5d': 'Microsoft Hyper-V',
        }

    def get_vendor(self, bssid: str) -> str:
        """Identify vendor from MAC address OUI."""
        if not bssid or len(bssid) < 8:
            return "Unknown"

        oui = bssid[:8].lower()
        return self.oui_database.get(oui, "Unknown")

    def estimate_distance(self, signal_percent: int, frequency_mhz: int) -> tuple[str, int]:
        """
        Estimate distance based on signal strength and frequency.
        Returns (distance_range, estimated_meters)
        """
        # Convert percentage to approximate RSSI (rough estimation)
        # Typical WiFi: 100% ≈ -30dBm, 0% ≈ -90dBm
        rssi_dbm = -90 + (signal_percent * 0.6)

        # Free space path loss formula: FSPL = 20*log10(d) + 20*log10(f) + 32.44
        # Rearranged: d = 10^((FSPL - 20*log10(f) - 32.44) / 20)
        # Assuming transmit power of 20dBm (100mW)
        tx_power = 20
        path_loss = tx_power - rssi_dbm

        import math

        frequency_ghz = frequency_mhz / 1000
        distance_m = 10 ** ((path_loss - 20 * math.log10(frequency_ghz) - 32.44) / 20)

        if distance_m < 10:
            return "Very Close (<10m)", int(distance_m)
        elif distance_m < 50:
            return "Close (10-50m)", int(distance_m)
        elif distance_m < 100:
            return "Medium (50-100m)", int(distance_m)
        elif distance_m < 300:
            return "Far (100-300m)", int(distance_m)
        else:
            return "Very Far (>300m)", int(distance_m)

    def analyze_channel_interference(self, access_points: list[AccessPoint]) -> dict:
        """Analyze channel usage and interference patterns."""
        channel_usage = {}
        band_usage = {'2.4GHz': 0, '5GHz': 0, '6GHz': 0}

        for ap in access_points:
            # Count channel usage
            if ap.channel not in channel_usage:
                channel_usage[ap.channel] = []
            channel_usage[ap.channel].append(ap)

            # Count band usage
            band_usage[ap.band] = band_usage.get(ap.band, 0) + 1

        # Find optimal channels (less congested)
        optimal_24 = []
        optimal_5 = []

        # 2.4GHz optimal channels (1, 6, 11 are non-overlapping)
        for ch in [1, 6, 11]:
            if ch not in channel_usage:
                optimal_24.append(ch)

        # 5GHz has many non-overlapping channels
        common_5ghz = [36, 40, 44, 48, 149, 153, 157, 161]
        for ch in common_5ghz:
            if ch not in channel_usage:
                optimal_5.append(ch)

        return {
            'channel_usage': channel_usage,
            'band_usage': band_usage,
            'optimal_24ghz': optimal_24,
            'optimal_5ghz': optimal_5,
            'total_interference': len(channel_usage),
        }


def enhanced_wifi_scan(
    interface: Optional[str] = None,
    extended_range: bool = True,
    multiple_scans: int = 3,
    scan_delay: float = 2.0,
) -> list[EnhancedAccessPoint]:
    """
    Enhanced WiFi scanning with spectrum analysis techniques.

    Args:
        interface: WiFi interface to use
        extended_range: Use techniques to detect distant APs
        multiple_scans: Number of scans to perform (helps detect intermittent APs)
        scan_delay: Delay between scans in seconds
    """
    analyzer = SpectrumAnalyzer()
    all_access_points = {}  # Use dict to deduplicate by BSSID

    print(f"Performing {multiple_scans} enhanced WiFi scans...")

    for scan_num in range(multiple_scans):
        print(f"Scan {scan_num + 1}/{multiple_scans}...")

        # Use more detailed netsh command for extended information
        cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
        if interface:
            cmd.extend([f'interface="{interface}"'])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)

            # Parse the enhanced output
            scan_aps = _parse_enhanced_netsh_output(result.stdout, analyzer)

            # Merge results (keep strongest signal for each BSSID)
            for ap in scan_aps:
                if (
                    ap.bssid not in all_access_points
                    or ap.signal_percent > all_access_points[ap.bssid].signal_percent
                ):
                    all_access_points[ap.bssid] = ap

            if scan_num < multiple_scans - 1:
                time.sleep(scan_delay)

        except subprocess.CalledProcessError as e:
            raise WiFiScanError(f"Enhanced WiFi scan failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise WiFiScanError("Enhanced WiFi scan timeout")

    access_points = list(all_access_points.values())

    # Sort by signal strength (strongest first)
    access_points.sort(key=lambda ap: ap.signal_percent, reverse=True)

    print(f"Enhanced scan complete: {len(access_points)} unique access points found")
    return access_points


def _parse_enhanced_netsh_output(
    output: str, analyzer: SpectrumAnalyzer
) -> list[EnhancedAccessPoint]:
    """Parse netsh output with enhanced analysis."""
    access_points = []
    lines = output.split("\n")
    current_ssid = None
    current_bssids = []
    seen_at = datetime.now()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # New SSID block
        if line.startswith("SSID") and ":" in line:
            # Process previous SSID if exists
            if current_ssid and current_bssids:
                for bssid_info in current_bssids:
                    ap = _create_enhanced_access_point(current_ssid, bssid_info, analyzer, seen_at)
                    access_points.append(ap)

            # Start new SSID
            current_ssid = line.split(":", 1)[1].strip()
            current_bssids = []

        # BSSID information
        elif line.startswith("BSSID") and ":" in line:
            bssid = line.split(":", 1)[1].strip()
            bssid_info = {"bssid": bssid}

            # Look ahead for related information
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(("SSID", "BSSID")):
                info_line = lines[j].strip()
                if ":" in info_line:
                    key, value = info_line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if "signal" in key:
                        signal_match = re.search(r"(\d+)%", value)
                        if signal_match:
                            bssid_info["signal"] = int(signal_match.group(1))
                    elif "channel" in key:
                        channel_match = re.search(r"\d+", value)
                        if channel_match:
                            bssid_info["channel"] = int(channel_match.group())
                    elif "authentication" in key:
                        bssid_info["auth"] = value
                    elif "encryption" in key:
                        bssid_info["cipher"] = value
                    elif "radio type" in key:
                        bssid_info["radio_type"] = value
                j += 1

            current_bssids.append(bssid_info)
            i = j - 1

        i += 1

    # Process final SSID
    if current_ssid and current_bssids:
        for bssid_info in current_bssids:
            ap = _create_enhanced_access_point(current_ssid, bssid_info, analyzer, seen_at)
            access_points.append(ap)

    return access_points


def _create_enhanced_access_point(
    ssid: str, bssid_info: dict, analyzer: SpectrumAnalyzer, seen_at: datetime
) -> EnhancedAccessPoint:
    """Create EnhancedAccessPoint with spectrum analysis."""
    from spectrum_grabber.wifi_scanner import _channel_to_frequency, _get_band_from_frequency

    channel = bssid_info.get("channel", 1)
    frequency = _channel_to_frequency(channel)
    band = _get_band_from_frequency(frequency)
    signal_percent = bssid_info.get("signal", 0)
    bssid = bssid_info.get("bssid", "")

    # Enhanced analysis
    vendor = analyzer.get_vendor(bssid)
    distance_range, distance_m = analyzer.estimate_distance(signal_percent, frequency)

    # Estimate RSSI from signal percentage (rough approximation)
    rssi_dbm = -90 + (signal_percent * 0.6)

    return EnhancedAccessPoint(
        ssid=ssid,
        bssid=bssid,
        signal_percent=signal_percent,
        channel=channel,
        auth=bssid_info.get("auth", "Unknown"),
        cipher=bssid_info.get("cipher", "Unknown"),
        band=band,
        frequency_mhz=frequency,
        seen_at=seen_at,
        rssi_dbm=int(rssi_dbm),
        vendor=vendor,
        capabilities=bssid_info.get("radio_type", "Unknown"),
    )


def main():
    """Main function to demonstrate enhanced WiFi scanning."""
    print("=== ENHANCED WIFI SPECTRUM ANALYZER ===")
    print()

    try:
        # Perform enhanced scan
        access_points = enhanced_wifi_scan(extended_range=True, multiple_scans=3)

        if not access_points:
            print("No access points found.")
            return

        # Analyze spectrum
        analyzer = SpectrumAnalyzer()
        interference_analysis = analyzer.analyze_channel_interference(access_points)

        print(f"\n=== DETECTED ACCESS POINTS ({len(access_points)}) ===")
        for i, ap in enumerate(access_points, 1):
            distance_range, distance_m = analyzer.estimate_distance(
                ap.signal_percent, ap.frequency_mhz
            )

            print(f"{i}. {ap.ssid}")
            print(f"   BSSID: {ap.bssid} ({ap.vendor})")
            print(f"   Signal: {ap.signal_percent}% (~{ap.rssi_dbm}dBm)")
            print(f"   Channel: {ap.channel} ({ap.frequency_mhz} MHz, {ap.band})")
            print(f"   Distance: {distance_range} (~{distance_m}m)")
            print(f"   Security: {ap.auth}")
            print()

        print("=== SPECTRUM ANALYSIS ===")
        print(f"Band usage: {interference_analysis['band_usage']}")
        print(
            f"Channel interference: {interference_analysis['total_interference']} channels in use"
        )
        print(f"Optimal 2.4GHz channels: {interference_analysis['optimal_24ghz']}")
        print(
            f"Optimal 5GHz channels: {interference_analysis['optimal_5ghz'][:5]}..."
        )  # Show first 5

        # Show most congested channels
        congested = [
            (ch, len(aps))
            for ch, aps in interference_analysis['channel_usage'].items()
            if len(aps) > 1
        ]
        if congested:
            print(f"Congested channels: {dict(congested)}")

    except WiFiScanError as e:
        print(f"Enhanced WiFi scan failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
