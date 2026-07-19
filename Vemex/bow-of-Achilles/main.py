#!/usr/bin/env python3
"""
SpectrumAnalyzer Pro - WiFi Spectrum Analysis and Network Testing Suite
Main entry point for the application.
"""

import argparse
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


def show_gui():
    """Launch the main GUI interface."""
    try:
        from spectrum_analysis.enhanced_live_viewer import main as enhanced_viewer

        enhanced_viewer()
    except ImportError as e:
        print(f"Error launching GUI: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return False
    return True


def run_wifi_scan():
    """Run WiFi scanning functionality."""
    try:
        from enhanced_wifi_scanner import enhanced_wifi_scan

        results = enhanced_wifi_scan()

        print("\n=== WiFi Spectrum Scan Results ===")
        for ap in results:
            print(f"SSID: {ap.ssid}")
            print(f"BSSID: {ap.bssid}")
            print(f"Signal: {ap.signal_percent}%")
            print(f"Channel: {ap.channel}")
            print(f"Security: {ap.security}")
            if hasattr(ap, 'vendor') and ap.vendor:
                print(f"Vendor: {ap.vendor}")
            print("-" * 40)

    except Exception as e:
        print(f"Error running WiFi scan: {e}")
        return False
    return True


def run_tower_scan(place=None, bbox=None, output_file=None, map_file=None):
    """Run tower scanning functionality."""
    try:
        from spectrum_grabber.overpass_grabber import main as tower_main

        # Build arguments for tower scanner
        args = []
        if place:
            args.extend(['--place', place])
        elif bbox:
            args.extend(['--bbox', bbox])

        if output_file:
            args.extend(['--out-file', output_file])
        if map_file:
            args.extend(['--map-file', map_file])

        # Run tower scanner
        sys.argv = ['overpass_grabber.py'] + args
        tower_main()

    except Exception as e:
        print(f"Error running tower scan: {e}")
        return False
    return True


def run_spectrum_analysis():
    """Run 3D spectrum analysis."""
    try:
        from spectrum_3d_visualizer import main as spectrum_main

        spectrum_main()
    except Exception as e:
        print(f"Error running spectrum analysis: {e}")
        return False
    return True


def show_help():
    """Show detailed help information."""
    help_text = """
SpectrumAnalyzer Pro - WiFi Spectrum Analysis and Network Testing Suite

USAGE:
    python main.py [command] [options]

COMMANDS:
    gui                 Launch the graphical user interface (default)
    wifi-scan          Perform WiFi spectrum scanning
    tower-scan         Scan for radio/communication towers
    spectrum-3d        Run 3D spectrum visualization
    help               Show this help message

EXAMPLES:
    # Launch GUI (default)
    python main.py
    python main.py gui

    # Run WiFi scan
    python main.py wifi-scan

    # Scan towers by location
    python main.py tower-scan --place "San Francisco, CA" --output towers.csv

    # Scan towers by coordinates
    python main.py tower-scan --bbox "37.60,-122.55,37.90,-122.30" --output towers.csv

    # Run 3D spectrum analysis
    python main.py spectrum-3d

REQUIREMENTS:
    - Python 3.9+
    - All dependencies: pip install -r requirements.txt
    - Windows: Recommended for best WiFi scanning support
    - Linux/macOS: Limited WiFi scanning capabilities

For more information, see README.md
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SpectrumAnalyzer Pro - WiFi Spectrum Analysis Suite", add_help=False
    )

    parser.add_argument(
        'command',
        nargs='?',
        default='gui',
        choices=['gui', 'wifi-scan', 'tower-scan', 'spectrum-3d', 'help'],
        help='Command to run',
    )

    # Tower scan specific arguments
    parser.add_argument('--place', help='Place name for tower scanning')
    parser.add_argument('--bbox', help='Bounding box for tower scanning (south,west,north,east)')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--map-file', help='HTML map output file')

    args = parser.parse_args()

    if args.command == 'help':
        show_help()
        return 0

    print("🌐 SpectrumAnalyzer Pro - WiFi Spectrum Analysis Suite")
    print("=" * 50)

    success = False

    if args.command == 'gui':
        print("🖥️  Launching GUI interface...")
        success = show_gui()

    elif args.command == 'wifi-scan':
        print("📡 Running WiFi spectrum scan...")
        success = run_wifi_scan()

    elif args.command == 'tower-scan':
        print("🗼 Running tower scan...")
        success = run_tower_scan(
            place=args.place, bbox=args.bbox, output_file=args.output, map_file=args.map_file
        )

    elif args.command == 'spectrum-3d':
        print("📊 Running 3D spectrum analysis...")
        success = run_spectrum_analysis()

    if success:
        print("✅ Operation completed successfully!")
        return 0
    else:
        print("❌ Operation failed. Check error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
