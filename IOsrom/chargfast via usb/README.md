# ChargFast via USB - iOS Recovery Tools

A comprehensive Python utility for iOS device management, USB scanning, and auto-boot recovery fixing.

## Features

- 🍎 **iOS Recovery Management**: Fix auto-boot issues with irecovery integration
- 🔍 **Multi-method USB detection**: PyUSB, PowerShell, and WMI fallbacks
- 📱 **Apple Device Detection**: Enhanced scanning for iPad/iPhone devices
- 🔧 **Auto-boot Fixer**: Resolve iOS charging and boot loop issues
- 📊 **JSON output format**: Perfect for automation and integration
- 🖥️ **Text output format**: Human-readable console output
- 🪟 **Windows optimized**: Works reliably on Windows 10/11
- 🐍 **Virtual environment**: Isolated dependencies

## Quick Start - Fix iOS Auto-Boot Issue

**If your iOS device won't charge or is stuck in boot loop:**

1. **Download iOS tools** (if not already done):
   - Download `libimobiledevice.1.2.1-r1122-win-x64.zip` from [GitHub releases](https://github.com/libimobiledevice-win32/imobiledevice-net/releases)
   - Extract to current directory (should have `irecovery.exe`)

2. **Put your iOS device in recovery mode**:
   - Connect via USB
   - Hold Power + Home (or Volume Down on newer devices)
   - Wait for recovery mode screen

3. **Run the fix**:
   ```bash
   python fix_auto_boot.py
   ```
   Or double-click: `FIX_AUTOBOOT.bat`

## Full Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup iOS tools:
```bash
python setup_ios_tools.py
```

## Usage

### iOS Recovery & Auto-Boot Fixing

#### Fix auto-boot issue (main use case):
```bash
python fix_auto_boot.py
```

#### Check for iOS devices in recovery mode:
```bash
python src/usb_scanner.py --ios-recovery
```

#### Full iOS device management:
```bash
python src/ios_recovery_manager.py --scan
python src/ios_recovery_manager.py --info
python src/ios_recovery_manager.py --auto-boot enable
```

### USB Device Scanning

#### Enhanced Apple device scan:
```bash
python src/usb_scanner.py --apple-scan
```

#### Basic JSON output (default):
```bash
python src/usb_scanner.py
```

#### Text format output:
```bash
python src/usb_scanner.py --format text
```

#### Find specific iPad devices:
```bash
python src/ipad_finder.py
python src/target_ipad.py
```

## Example Output

### JSON Format:
```json
{
  "timestamp": "2025-10-02T13:34:05.995781",
  "method": "PowerShell",
  "device_count": 10,
  "devices": [
    {
      "name": "TP-Link Bluetooth 5.4 USB Adapter",
      "instance_id": "USB\\VID_2357&PID_0604\\E848B8C82000",
      "device_class": "Bluetooth",
      "manufacturer": "TP-Link Systems Inc.",
      "status": "OK",
      "vendor_id": "0x2357",
      "product_id": "0x0604"
    }
  ]
}
```

## Development

This project is configured to work with VS Code and uses a local virtual environment.
- Python interpreter: `./venv/Scripts/python.exe`
- Debugger: Modern `debugpy` configuration
- Dependencies: Locally installed in virtual environment

## Detection Methods

### USB Detection
1. **PyUSB**: Direct USB library access (requires backend)
2. **PowerShell**: Windows Get-PnpDevice cmdlet (primary method)
3. **WMI**: Windows Management Instrumentation (fallback)

### iOS Detection
1. **irecovery**: Direct communication with iOS devices in recovery mode
2. **Enhanced Apple Scan**: Multi-method Apple device detection
3. **Device Manager Integration**: Windows device enumeration

## Dependencies

### Python Packages
- pyusb: USB device access library
- libusb1: USB backend for Windows
- pywinusb: Windows-specific USB support

### iOS Recovery Tools
- irecovery.exe: iOS recovery mode communication
- libimobiledevice: iOS device management suite
- Download from: [libimobiledevice-win32 releases](https://github.com/libimobiledevice-win32/imobiledevice-net/releases)

## Project Structure

```
├── src/
│   ├── usb_scanner.py           # Enhanced USB scanner with iOS support
│   ├── ios_recovery_manager.py  # iOS recovery management
│   ├── ipad_finder.py           # iPad-specific device finder
│   ├── target_ipad.py           # iPad targeting utility
│   └── auto_boot_fixer.py       # Auto-boot issue resolver
├── fix_auto_boot.py             # Simple auto-boot fixer (main tool)
├── FIX_AUTOBOOT.bat            # Windows batch file for easy access
├── setup_ios_tools.py           # Setup and verification script
├── irecovery.exe               # iOS recovery tool (download required)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Troubleshooting

### iOS Device Not Detected
1. Ensure device is in recovery mode (connect + hold buttons)
2. Check USB cable and port
3. Verify irecovery.exe is present
4. Run: `python setup_ios_tools.py`

### Auto-Boot Fix Not Working
1. Device must be in recovery mode (iBoot)
2. Try different USB port/cable
3. Ensure Windows recognizes the device
4. Check Device Manager for Apple devices

### "irecovery not found" Error
1. Download libimobiledevice tools
2. Extract irecovery.exe to project directory
3. Verify with: `irecovery.exe -q`