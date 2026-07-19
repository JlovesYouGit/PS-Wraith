# idevicerestore Usage Guide

## Quick Start

1. **Setup idevicerestore** (one-time):
   ```
   python setup_idevicerestore.py
   ```

2. **Restore with latest IPSW**:
   ```
   python restore_latest.py
   ```

## Available IPSW Files

Your current IPSW files (sorted by version):
- `iPad2,1_9.3.5_13G36_Restore.ipsw` - **LATEST** (iOS 9.3.5 for iPad 2)
- `iPad1,1_iOS9_A4_Final.ipsw` - Custom iOS 9 for iPad 1
- `iPad1,1_5.1.1_9B206_Restore.ipsw` - iOS 5.1.1 for iPad 1
- `iPad1,1_4.3.3_8J3_Restore.ipsw` - iOS 4.3.3 for iPad 1
- `iPad1,1_Perfect.ipsw` - Custom perfect IPSW
- `iPad1,1_Stealth.ipsw` - Custom stealth IPSW
- `iPad1,1_Clean.ipsw` - Clean custom IPSW

## Manual Usage

### Restore with specific IPSW:
```bash
python idevicerestore_flash.py iPad2,1_9.3.5_13G36_Restore.ipsw
```

### Restore with auto-detected latest IPSW:
```bash
python idevicerestore_flash.py
```

## Device Preparation

1. **Put device in DFU Mode**:
   - Connect device to computer
   - Hold Home + Power for 10 seconds
   - Release Power, keep holding Home for 5 more seconds
   - Screen should be completely black (no Apple logo)

2. **Verify DFU Mode**:
   - Device appears in Device Manager as "Apple Recovery (DFU) USB Driver"
   - iTunes may show "iTunes has detected an iPhone in recovery mode"

## Troubleshooting

### idevicerestore not found
- Run `python setup_idevicerestore.py`
- Manually place `idevicerestore.exe` in the `idevice/` folder
- Build from source in `1.0.0 source code/libimobiledevice-idevicerestore-a88351d/`

### Device not detected
- Ensure device is in DFU mode (black screen)
- Try different USB cable/port
- Install iTunes for device drivers
- Check Device Manager for Apple devices

### Restore fails
- Verify IPSW integrity: `python check_ipsw_integrity.py <ipsw_file>`
- Ensure device model matches IPSW
- Try different IPSW file
- Check USB connection stability

## Command Line Options

idevicerestore supports these options:
- `-e` - Erase mode (recommended)
- `-u` - Update mode
- `-c` - Check mode only
- `-d` - Enable debug output
- `-h` - Show help

## Notes

- **iPad2,1_9.3.5_13G36_Restore.ipsw** is the most recent official IPSW
- Custom IPSW files may require specific device states or jailbreaks
- Always backup device data before restoring
- Restore process can take 15-30 minutes
- Device will reboot multiple times during restore

## File Structure
```
ROMLOADDER/
├── idevice/
│   └── idevicerestore.exe          # Main restore tool
├── *.ipsw                          # IPSW firmware files
├── idevicerestore_flash.py         # Main restore script
├── restore_latest.py               # Quick restore with latest IPSW
├── setup_idevicerestore.py         # Setup script
└── IDEVICERESTORE_GUIDE.md         # This guide
```