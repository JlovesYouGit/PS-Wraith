# AndroidRoot - Android Root/Boot Exploit Chain

Android-native equivalents to the iOS `IOsrom` NAND/boot chain tools.

## Tools

| Tool | Description | iOS Equivalent |
|------|-------------|----------------|
| `fastboot_exploit.py` | Fastboot bootloader exploitation | DFU/irecovery |
| `android_nand_tool.py` | Direct NAND/eMMC/block access | NAND tools |
| `boot_image_patcher.py` | Boot.img patching & repacking | Ramdisk tools |
| `adb_root_chain.py` | ADB root & privilege escalation | iBoot root chain |
| `qualcomm_edl.py` | Qualcomm Emergency Download mode | DFU mode |
| `mediatek_brom.py` | MediaTek BootROM mode | DFU mode |
| `ramdisk_booter.py` | Custom ramdisk boot | iOS ramdisk boot |
| `avb_bypass.py` | Android Verified Boot bypass | TSS bypass |
| `silicon_burner_android.py` | Permanent hardware mod | Silicon burner |
| `android_root_chain.py` | Main orchestrator | NAND chain |

## Usage

```bash
# Quick start
cd AndroidRoot
python3 main.py

# Detect device only
python3 main.py --detect

# Attempt root chain
python3 main.py --root --serial <device_serial>
```

## Chain Order

1. Detect device/chipset
2. Check existing root status
3. Try ADB root
4. Try fastboot unlock
5. Try boot image patch
6. Try EDL/BROM exploit

## Notes

- Requires `adb` and `fastboot` in PATH
- Some methods require unlocked bootloader
- EDL/BROM methods require hardware-level access
- Root access is required for NAND direct access
