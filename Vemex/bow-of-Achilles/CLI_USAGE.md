# Spectrum Grabber CLI Usage

The `spectrum_grabber.cli` module provides a unified command-line interface for collecting both communication tower data from OpenStreetMap and WiFi access point information from local scans.

## Installation

```bash
pip install -e .  # Install the package in development mode
```

## Basic Usage

```bash
# Display help
python -m spectrum_grabber.cli --help

# WiFi scan only
python -m spectrum_grabber.cli --wifi-scan --no-osm

# Towers only for a location
python -m spectrum_grabber.cli --place "Berkeley, CA"

# Combined towers and WiFi
python -m spectrum_grabber.cli --place "San Francisco, CA" --wifi-scan

# Use specific bounding box
python -m spectrum_grabber.cli --bbox "37.75,-122.45,37.80,-122.40" --wifi-scan
```

## Command-Line Flags

### Location Options (mutually exclusive)
- `--place "PLACE NAME"`: Geocode a place name to get towers in that area
- `--bbox "south,west,north,east"`: Use explicit bounding box coordinates

### WiFi Scanning Options
- `--wifi-scan`: Enable WiFi access point scanning
- `--wifi-interface NAME`: Specify WiFi interface (Windows only)

### Data Collection Options
- `--no-osm`: Skip OpenStreetMap tower data collection

### Output Options
- `--out-csv PATH`: Save unified results to CSV file
- `--out-html PATH`: Generate HTML map (requires folium)

### HTTP Options
- `--user-agent STRING`: Custom User-Agent for API requests
- `--retries N`: HTTP retry count (default: 3)
- `--backoff FLOAT`: Retry backoff factor (default: 0.5)

## Output Format

The CLI produces a unified CSV format with a `kind` column to distinguish between:
- `tower`: Communication towers from OpenStreetMap
- `wifi`: WiFi access points from local scanning

### CSV Columns

**Common columns:**
- `kind`: "tower" or "wifi"
- `latitude`, `longitude`: Geographic coordinates (may be empty for WiFi)
- `name`: Tower name or WiFi SSID
- `source`: Data source

**Tower-specific columns:**
- `id`, `osm_type`: OpenStreetMap identifiers
- `operator`: Tower operator
- `man_made`: OSM man_made tag
- `tower_type`: Communication tower type
- `height`: Tower height

**WiFi-specific columns:**
- `ssid`: WiFi network name
- `bssid`: Access point MAC address
- `channel`: WiFi channel number
- `signal`: Signal strength percentage
- `auth`: Authentication method
- `cipher`: Encryption cipher
- `band`: Frequency band (2.4GHz, 5GHz, 6GHz)
- `frequency_mhz`: Frequency in MHz

## Example Commands

```bash
# Get all data for Berkeley area
python -m spectrum_grabber.cli --place "Berkeley, CA" --wifi-scan --out-csv berkeley_spectrum.csv

# WiFi scan with specific interface
python -m spectrum_grabber.cli --wifi-scan --wifi-interface "Wi-Fi" --out-csv wifi_data.csv

# Towers in specific bounding box with map output
python -m spectrum_grabber.cli --bbox "37.85,-122.35,37.90,-122.25" --out-html towers_map.html

# Combined data with console output (no file)
python -m spectrum_grabber.cli --place "San Francisco, CA" --wifi-scan
```

## Platform Support

- **Windows**: Primary target, uses `netsh wlan` for WiFi scanning
- **Linux**: Uses `nmcli` (NetworkManager) for WiFi scanning
- **macOS**: Uses `airport` utility for WiFi scanning

## Dependencies

- **Required**: `requests`, `urllib3`
- **Optional**: `folium` (for HTML map generation)

## Error Handling

The CLI handles common error conditions:
- Invalid place names or coordinates
- WiFi interface not found
- Network connectivity issues
- Missing WiFi scanning capabilities
- Large bounding boxes (shows warnings)

## Integration Examples

See `example_usage.py` for comprehensive examples of all CLI functionality.
