# SpectrumAnalyzer Pro User Guide

## Overview

SpectrumAnalyzer Pro is a professional WiFi spectrum analysis and network testing suite that provides:

- **Real-time WiFi scanning** with advanced signal analysis
- **3D spectrum visualization** for interference detection
- **Tower location mapping** using OpenStreetMap data
- **Network monitoring** and security assessment
- **Cross-platform support** (Windows, Linux, macOS)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Administrator/root privileges (for WiFi scanning)
- Internet connection (for tower mapping)

### Installation

1. **Download the repository:**
   ```bash
   git clone https://github.com/JlovesYouGit/SpectrumAnalyzer-Pro.git
   cd SpectrumAnalyzer-Pro
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Features Guide

### 1. GUI Interface (Recommended for Beginners)

Launch the graphical interface:
```bash
python main.py gui
```

The GUI provides:
- **Live spectrum monitoring** with real-time updates
- **Interactive 3D plots** showing signal strength and interference
- **Network details** including security analysis
- **Export capabilities** for reports and data
- **Visual interference analysis** with channel recommendations

### 2. WiFi Spectrum Scanning

Perform comprehensive WiFi analysis:
```bash
python main.py wifi-scan
```

This feature:
- Detects all nearby WiFi access points
- Analyzes signal strength and quality
- Identifies vendor information from MAC addresses
- Calculates approximate distances
- Provides channel interference analysis
- Suggests optimal channels for new networks

**Sample Output:**
```
=== WiFi Spectrum Scan Results ===
SSID: MyNetwork
BSSID: aa:bb:cc:dd:ee:ff
Signal: 85%
Channel: 6
Security: WPA2
Vendor: Netgear
----------------------------------------
```

### 3. Tower Location Mapping

Map radio and communication towers in your area:

**By location name:**
```bash
python main.py tower-scan --place "San Francisco, CA" --output towers.csv
```

**By coordinates:**
```bash
python main.py tower-scan --bbox "37.60,-122.55,37.90,-122.30" --output towers.csv
```

This creates:
- **CSV file** with tower locations and details
- **HTML map** showing tower positions (if `--map-file` specified)
- **Coverage analysis** for radio frequency planning

### 4. 3D Spectrum Visualization

Generate interactive 3D plots:
```bash
python main.py spectrum-3d
```

Features:
- **3D signal strength plots** showing spatial distribution
- **Frequency analysis** across different bands
- **Interference visualization** with hotspot identification
- **Time-based analysis** for monitoring changes
- **Export options** for presentations and reports

## Advanced Usage

### Command Line Options

Get detailed help:
```bash
python main.py help
```

### Programmatic Access

For developers and advanced users:

```python
# WiFi scanning
from spectrum_grabber.wifi_scanner import scan_wifi_cross_platform
access_points = scan_wifi_cross_platform()

# Enhanced analysis
from enhanced_wifi_scanner import enhanced_wifi_scan
detailed_results = enhanced_wifi_scan()

# Tower mapping
from spectrum_grabber.overpass_grabber import get_towers_by_place
towers = get_towers_by_place("New York, NY")
```

### Configuration

The application automatically detects your platform and uses appropriate scanning methods:

- **Windows**: Uses `netsh wlan` commands (most comprehensive)
- **Linux**: Uses `nmcli` or `iwlist` (requires NetworkManager)
- **macOS**: Uses `airport` utility (limited functionality)

## Building Standalone Executable

Create a portable .exe file:

1. **Install build tools:**
   ```bash
   pip install pyinstaller
   ```

2. **Build executable:**
   ```bash
   python build_exe.py
   ```

3. **Install system-wide (Windows):**
   ```bash
   # Run as administrator
   dist\install.bat
   ```

The executable includes all dependencies and can run without Python installed.

## Troubleshooting

### Common Issues

**"No WiFi adapters found"**
- Ensure WiFi is enabled
- Run as administrator/root
- Check if your WiFi adapter supports scanning

**"Permission denied"**
- Run with administrator privileges
- On Linux: `sudo python main.py`
- On Windows: Run PowerShell as Administrator

**"Module not found"**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.9+)

**GUI doesn't start**
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- Update matplotlib: `pip install --upgrade matplotlib`

### Performance Tips

- **Close other network tools** during scanning
- **Use wired connection** for tower mapping to avoid interference
- **Run periodic scans** rather than continuous monitoring
- **Export data regularly** to avoid memory issues

### Platform-Specific Notes

**Windows:**
- Best performance and feature support
- Requires "Run as Administrator" for full functionality
- Works with all WiFi adapters

**Linux:**
- Requires NetworkManager or wireless-tools
- Some features may need root privileges
- Performance varies by WiFi driver

**macOS:**
- Limited scanning capabilities
- May require developer tools installation
- Some advanced features unavailable

## Data Export and Reports

### Export Formats

- **CSV**: Raw data for analysis in Excel/spreadsheets
- **JSON**: Structured data for programming
- **HTML**: Interactive maps and reports
- **PNG/PDF**: Charts and visualizations

### Report Generation

The GUI includes built-in report generation:
1. Run your analysis
2. Click "Export Report"
3. Choose format and location
4. Share with stakeholders

## Security and Privacy

- **No data collection**: All analysis is performed locally
- **No internet required**: Except for tower mapping
- **Secure scanning**: Only passive monitoring, no network intrusion
- **Privacy protection**: SSID and MAC addresses can be anonymized

## Support and Contributing

- **Issues**: Report bugs on GitHub
- **Documentation**: See README.md for technical details
- **Contributing**: Pull requests welcome
- **License**: Open source under MIT license

## Legal Notice

This tool is for legitimate network analysis and troubleshooting only. Users are responsible for complying with local laws and regulations regarding WiFi scanning and spectrum analysis. Do not use this tool to access networks without permission.
