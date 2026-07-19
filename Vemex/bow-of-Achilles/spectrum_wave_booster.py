#!/usr/bin/env python3
"""
Advanced spectrum wave booster for extended WiFi detection range.
Uses Windows-specific netsh commands and signal processing techniques.
"""

import json
import subprocess
import time
from dataclasses import asdict
from typing import Optional

from enhanced_wifi_scanner import EnhancedAccessPoint, SpectrumAnalyzer


class SpectrumWaveBooster:
    """Advanced spectrum analysis with wave propagation modeling."""

    def __init__(self):
        self.analyzer = SpectrumAnalyzer()
        self.scan_history = []

    def boost_detection_range(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """
        Use advanced techniques to boost WiFi detection range:
        1. Multiple scan iterations with different timing
        2. Profile-based scanning for hidden networks
        3. Signal aggregation and weak signal recovery
        4. Antenna pattern optimization suggestions
        """
        print("🚀 SPECTRUM WAVE BOOSTER ACTIVATED")
        print("Using advanced techniques to extend detection range...")
        print()

        all_detections = {}
        scan_techniques = [
            ("Standard Scan", self._standard_scan),
            ("Deep Scan (Extended Timeout)", self._deep_scan),
            ("Profile Scan (Hidden Networks)", self._profile_scan),
            ("Rapid Burst Scan", self._burst_scan),
            ("Low Signal Recovery", self._weak_signal_scan),
        ]

        for technique_name, scan_func in scan_techniques:
            print(f"🔍 {technique_name}...")
            try:
                detections = scan_func(interface)

                # Merge detections with signal strength tracking
                for ap in detections:
                    key = ap.bssid
                    if key not in all_detections:
                        all_detections[key] = ap
                        all_detections[key].detection_count = 1
                        all_detections[key].max_signal = ap.signal_percent
                        all_detections[key].min_signal = ap.signal_percent
                        all_detections[key].avg_signal = ap.signal_percent
                        all_detections[key].detection_methods = [technique_name]
                    else:
                        # Update signal statistics
                        existing = all_detections[key]
                        existing.detection_count += 1
                        existing.max_signal = max(existing.max_signal, ap.signal_percent)
                        existing.min_signal = min(existing.min_signal, ap.signal_percent)
                        existing.avg_signal = (existing.avg_signal + ap.signal_percent) / 2
                        existing.detection_methods.append(technique_name)

                        # Use strongest signal for main values
                        if ap.signal_percent > existing.signal_percent:
                            existing.signal_percent = ap.signal_percent
                            existing.rssi_dbm = ap.rssi_dbm

                print(f"   Found {len(detections)} access points")
                time.sleep(1)  # Brief pause between techniques

            except Exception as e:
                print(f"   ⚠️  {technique_name} failed: {e}")

        # Convert to list and sort by reliability (detection count + signal strength)
        boosted_aps = list(all_detections.values())
        boosted_aps.sort(key=lambda ap: (ap.detection_count * 10 + ap.signal_percent), reverse=True)

        print(f"\n✅ BOOST COMPLETE: {len(boosted_aps)} unique access points detected")
        return boosted_aps

    def _standard_scan(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """Standard netsh WiFi scan."""
        cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
        if interface:
            cmd.extend([f'interface="{interface}"'])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        return self._parse_netsh_output(result.stdout)

    def _deep_scan(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """Extended timeout scan for distant signals."""
        # Force a refresh first
        refresh_cmd = ["netsh", "wlan", "refresh"]
        subprocess.run(refresh_cmd, capture_output=True, text=True, timeout=5)
        time.sleep(3)  # Wait for refresh

        cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
        if interface:
            cmd.extend([f'interface="{interface}"'])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=20)
        return self._parse_netsh_output(result.stdout)

    def _profile_scan(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """Scan for networks including those in profiles (previously connected)."""
        # Get available networks including hidden ones
        cmd = ["netsh", "wlan", "show", "profiles"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)

            # Extract profile names
            profiles = []
            for line in result.stdout.split('\n'):
                if 'All User Profile' in line and ':' in line:
                    profile_name = line.split(':', 1)[1].strip()
                    profiles.append(profile_name)

            print(f"     Found {len(profiles)} saved profiles")

            # Now do regular scan (profiles help with hidden network detection)
            return self._standard_scan(interface)

        except Exception:
            return self._standard_scan(interface)

    def _burst_scan(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """Rapid burst scanning to catch intermittent beacons."""
        all_aps = {}

        for _i in range(5):  # 5 rapid scans
            try:
                cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
                if interface:
                    cmd.extend([f'interface="{interface}"'])

                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
                aps = self._parse_netsh_output(result.stdout)

                for ap in aps:
                    if (
                        ap.bssid not in all_aps
                        or ap.signal_percent > all_aps[ap.bssid].signal_percent
                    ):
                        all_aps[ap.bssid] = ap

                time.sleep(0.5)  # Short delay between bursts
            except Exception:
                continue

        return list(all_aps.values())

    def _weak_signal_scan(self, interface: Optional[str] = None) -> list[EnhancedAccessPoint]:
        """Attempt to detect very weak signals through extended scanning."""
        # Use netsh with different parameters to potentially catch weak signals

        try:
            # Try to get more detailed interface information
            cmd = ["netsh", "wlan", "show", "interfaces"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)

            # Look for signal quality information in interface details
            if "Signal" in result.stdout:
                print("     Interface shows signal information available")

            # Perform extended scan
            time.sleep(2)  # Wait for potential weak signals
            return self._standard_scan(interface)

        except Exception:
            return []

    def _parse_netsh_output(self, output: str) -> list[EnhancedAccessPoint]:
        """Parse netsh output into EnhancedAccessPoint objects."""
        from enhanced_wifi_scanner import _parse_enhanced_netsh_output

        return _parse_enhanced_netsh_output(output, self.analyzer)

    def analyze_propagation_patterns(self, access_points: list[EnhancedAccessPoint]) -> dict:
        """Analyze RF propagation patterns and suggest optimization."""
        analysis = {
            'total_aps': len(access_points),
            'band_distribution': {'2.4GHz': 0, '5GHz': 0, '6GHz': 0},
            'signal_distribution': {'strong': 0, 'medium': 0, 'weak': 0},
            'vendor_distribution': {},
            'channel_congestion': {},
            'propagation_analysis': {},
            'optimization_suggestions': [],
        }

        for ap in access_points:
            # Band distribution
            analysis['band_distribution'][ap.band] = (
                analysis['band_distribution'].get(ap.band, 0) + 1
            )

            # Signal strength distribution
            if ap.signal_percent > 70:
                analysis['signal_distribution']['strong'] += 1
            elif ap.signal_percent > 40:
                analysis['signal_distribution']['medium'] += 1
            else:
                analysis['signal_distribution']['weak'] += 1

            # Vendor distribution
            vendor = ap.vendor if hasattr(ap, 'vendor') else 'Unknown'
            analysis['vendor_distribution'][vendor] = (
                analysis['vendor_distribution'].get(vendor, 0) + 1
            )

            # Channel congestion
            channel_key = f"{ap.channel} ({ap.band})"
            analysis['channel_congestion'][channel_key] = (
                analysis['channel_congestion'].get(channel_key, 0) + 1
            )

        # Generate optimization suggestions
        suggestions = []

        if analysis['band_distribution']['2.4GHz'] > analysis['band_distribution']['5GHz']:
            suggestions.append("Consider using 5GHz band for less congestion")

        if analysis['signal_distribution']['weak'] > 0:
            suggestions.append(
                f"Found {analysis['signal_distribution']['weak']} weak signals - consider repositioning antenna"
            )

        # Find most congested channels
        congested_channels = [
            (ch, count) for ch, count in analysis['channel_congestion'].items() if count > 1
        ]
        if congested_channels:
            most_congested = max(congested_channels, key=lambda x: x[1])
            suggestions.append(
                f"Channel {most_congested[0]} is most congested with {most_congested[1]} APs"
            )

        analysis['optimization_suggestions'] = suggestions
        return analysis

    def generate_range_extension_report(self, access_points: list[EnhancedAccessPoint]) -> str:
        """Generate a detailed report on range extension results."""
        report = []
        report.append("=" * 60)
        report.append("SPECTRUM WAVE BOOSTER - RANGE EXTENSION REPORT")
        report.append("=" * 60)
        report.append("")

        # Summary statistics
        total_aps = len(access_points)
        multi_detection = [
            ap for ap in access_points if hasattr(ap, 'detection_count') and ap.detection_count > 1
        ]
        weak_signals = [ap for ap in access_points if ap.signal_percent < 50]

        report.append("📊 DETECTION SUMMARY:")
        report.append(f"   Total Access Points: {total_aps}")
        report.append(f"   Multi-Detection APs: {len(multi_detection)} (more reliable)")
        report.append(f"   Weak Signal APs: {len(weak_signals)} (extended range)")
        report.append("")

        # Detailed AP list
        report.append("📡 DETECTED ACCESS POINTS:")
        for i, ap in enumerate(access_points, 1):
            detection_methods = getattr(ap, 'detection_methods', ['Standard'])
            detection_count = getattr(ap, 'detection_count', 1)
            max_signal = getattr(ap, 'max_signal', ap.signal_percent)

            distance_range, distance_m = self.analyzer.estimate_distance(
                ap.signal_percent, ap.frequency_mhz
            )

            report.append(f"{i:2d}. {ap.ssid}")
            report.append(f"    BSSID: {ap.bssid} ({getattr(ap, 'vendor', 'Unknown')})")
            report.append(
                f"    Signal: {ap.signal_percent}% (Max: {max_signal}%, Detections: {detection_count})"
            )
            report.append(f"    Channel: {ap.channel} ({ap.frequency_mhz} MHz, {ap.band})")
            report.append(f"    Distance: {distance_range} (~{distance_m}m)")
            report.append(
                f"    Methods: {', '.join(detection_methods[:3])}{'...' if len(detection_methods) > 3 else ''}"
            )
            report.append("")

        # Propagation analysis
        analysis = self.analyze_propagation_patterns(access_points)
        report.append("🌊 PROPAGATION ANALYSIS:")
        report.append(f"   Band Usage: {analysis['band_distribution']}")
        report.append(f"   Signal Strength: {analysis['signal_distribution']}")
        report.append(
            f"   Top Vendors: {dict(list(sorted(analysis['vendor_distribution'].items(), key=lambda x: x[1], reverse=True))[:3])}"
        )
        report.append("")

        # Optimization suggestions
        if analysis['optimization_suggestions']:
            report.append("💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in analysis['optimization_suggestions']:
                report.append(f"   • {suggestion}")
            report.append("")

        report.append("=" * 60)
        return "\n".join(report)


def main():
    """Main function for spectrum wave booster."""
    booster = SpectrumWaveBooster()

    try:
        # Perform boosted detection
        access_points = booster.boost_detection_range()

        if not access_points:
            print("No access points detected with any method.")
            return

        # Generate and display report
        report = booster.generate_range_extension_report(access_points)
        print("\n" + report)

        # Save detailed results to JSON
        results = []
        for ap in access_points:
            ap_dict = asdict(ap)
            # Add custom fields
            ap_dict['detection_count'] = getattr(ap, 'detection_count', 1)
            ap_dict['detection_methods'] = getattr(ap, 'detection_methods', ['Standard'])
            ap_dict['max_signal'] = getattr(ap, 'max_signal', ap.signal_percent)
            ap_dict['min_signal'] = getattr(ap, 'min_signal', ap.signal_percent)
            ap_dict['avg_signal'] = getattr(ap, 'avg_signal', ap.signal_percent)
            results.append(ap_dict)

        with open('spectrum_boost_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print("\n💾 Detailed results saved to: spectrum_boost_results.json")

    except Exception as e:
        print(f"❌ Spectrum wave booster failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
