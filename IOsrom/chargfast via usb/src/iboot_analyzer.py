#!/usr/bin/env python3
"""
iBoot flags analyzer and boot management for iPad.
Based on Apple's internal docs and chronic-dev wiki.
"""
import json
import sys
import subprocess
from typing import Dict, Any, List, Optional

def decode_iboot_flags(flags_hex: str) -> Dict[str, Any]:
    """
    Decode iBoot flags according to Apple's internal documentation.
    
    bit meanings for 32-bit devices:
    bit 0 (0x01): "auto-boot" – jump straight to kernel instead of stopping at iBoot prompt
    bit 1 (0x02): "secure-epoch-valid" – uses new AP-security epoch (post-BB-epoch-1)
    bit 2 (0x04): "force-LLB-recovery" – make LLB enter recovery even if image validates
    bit 3 (0x08): "force-iBoot-recovery" – make iBoot enter recovery
    bit 4 (0x10): "production-switch" – board flipped to production mode (disables JTAG)
    bit 5 (0x20): "development-switch" – board in dev mode (extra USB commands, no sig checks)
    bit 6 (0x40): "always-DFU" – immediately enter DFU after BootROM
    bit 7 (0x80): reserved / chip-specific
    """
    try:
        flags_int = int(flags_hex, 16) if isinstance(flags_hex, str) else flags_hex
    except (ValueError, TypeError):
        return {"error": "Invalid flags value", "raw": flags_hex}
    
    flags_analysis = {
        "raw_hex": f"0x{flags_int:02X}",
        "raw_decimal": flags_int,
        "flags": {
            "auto_boot": bool(flags_int & 0x01),
            "secure_epoch_valid": bool(flags_int & 0x02),
            "force_llb_recovery": bool(flags_int & 0x04),
            "force_iboot_recovery": bool(flags_int & 0x08),
            "production_switch": bool(flags_int & 0x10),
            "development_switch": bool(flags_int & 0x20),
            "always_dfu": bool(flags_int & 0x40),
            "reserved_bit7": bool(flags_int & 0x80)
        },
        "interpretation": {},
        "boot_behavior": ""
    }
    
    # Interpret the flags
    flags = flags_analysis["flags"]
    interp = flags_analysis["interpretation"]
    
    if flags["auto_boot"]:
        interp["auto_boot"] = "Device will automatically boot to kernel"
    else:
        interp["auto_boot"] = "Device stops at iBoot prompt if boot chain fails"
    
    if flags["secure_epoch_valid"]:
        interp["secure_epoch"] = "Using new AP-security epoch (post-baseband-epoch-1)"
    else:
        interp["secure_epoch"] = "Using legacy security epoch"
    
    if flags["force_llb_recovery"]:
        interp["llb_recovery"] = "LLB forced into recovery mode"
    
    if flags["force_iboot_recovery"]:
        interp["iboot_recovery"] = "iBoot forced into recovery mode"
    
    if flags["production_switch"]:
        interp["production"] = "Production mode (JTAG paths disabled)"
    else:
        interp["production"] = "Development/debug mode available"
    
    if flags["development_switch"]:
        interp["development"] = "Development mode (extra USB commands, no signature checks)"
    
    if flags["always_dfu"]:
        interp["dfu"] = "Always enter DFU after BootROM"
    
    # Determine boot behavior
    if not flags["auto_boot"]:
        if flags["force_iboot_recovery"] or flags["force_llb_recovery"]:
            flags_analysis["boot_behavior"] = "Forced recovery mode - will show 'Connect to iTunes'"
        else:
            flags_analysis["boot_behavior"] = "Will stop at iBoot prompt on boot failure"
    else:
        flags_analysis["boot_behavior"] = "Will attempt automatic boot to iOS"
    
    return flags_analysis

def get_ipad_iboot_info() -> Optional[Dict[str, Any]]:
    """
    Get iBoot information from the connected iPad.
    """
    try:
        # Run the detailed iPad scanner
        result = subprocess.run([
            sys.executable, "src/ipad_detailed_info.py"
        ], capture_output=True, text=True)
        
        # Also get raw JSON data
        json_result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True)
        
        if json_result.returncode == 0:
            data = json.loads(json_result.stdout)
            apple_devices = [d for d in data.get("devices", []) if d.get("vendor_id") == "0x05AC"]
            
            # Find device with iBoot flags
            for device in apple_devices:
                instance_id = device.get("instance_id", "")
                if "IBFL:" in instance_id:
                    import re
                    
                    # Extract all recovery mode information
                    info = {
                        "device_name": device.get("name", "Unknown"),
                        "vendor_id": device.get("vendor_id"),
                        "product_id": device.get("product_id"),
                        "instance_id": instance_id
                    }
                    
                    # Extract technical details
                    patterns = {
                        "chip_id": r'CPID:([0-9A-F]+)',
                        "chip_revision": r'CPRV:([0-9A-F]+)',
                        "chip_fusing_mode": r'CPFM:([0-9A-F]+)',
                        "secure_epoch": r'SCEP:([0-9A-F]+)',
                        "board_id": r'BDID:([0-9A-F]+)',
                        "ecid": r'ECID:([0-9A-F]+)',
                        "iboot_flags": r'IBFL:([0-9A-F]+)',
                        "serial_number": r'SRNM:\[([^\]]+)\]',
                        "secure_rom_tag": r'SRTG:\[([^\]]+)\]'
                    }
                    
                    for key, pattern in patterns.items():
                        match = re.search(pattern, instance_id)
                        if match:
                            info[key] = match.group(1)
                    
                    return info
        
        return None
        
    except Exception as e:
        print(f"Error getting iBoot info: {e}", file=sys.stderr)
        return None

def create_iboot_commands(enable_auto_boot: bool = True) -> List[str]:
    """
    Create iBoot commands for boot management.
    """
    commands = []
    
    if enable_auto_boot:
        commands.append("setenv auto-boot true")
        commands.append("saveenv")
        commands.append("reboot")
    else:
        commands.append("setenv auto-boot false")
        commands.append("saveenv")
    
    return commands

def generate_python_boot_script(ipad_info: Dict[str, Any]) -> str:
    """
    Generate a Python script for iBoot communication.
    """
    ecid = ipad_info.get("ecid", "UNKNOWN")
    
    script = f'''#!/usr/bin/env python3
"""
iBoot boot management script for iPad ECID {ecid}
Generated automatically from USB analysis.

Requirements:
- pip install pyirecovery
- libusb installed (Windows: scoop install libusb)
"""
import irecovery
import sys
import time

# iPad Information
ECID = "0x{ecid}"
CHIP_ID = "{ipad_info.get('chip_id', 'UNKNOWN')}"
BOARD_ID = "{ipad_info.get('board_id', 'UNKNOWN')}"
SERIAL = "{ipad_info.get('serial_number', 'UNKNOWN')}"

# iBoot Commands
AUTO_BOOT_ON  = b"setenv auto-boot true\\n"   # Enable auto-boot flag
AUTO_BOOT_OFF = b"setenv auto-boot false\\n"  # Disable auto-boot flag  
SAVEENV       = b"saveenv\\n"                 # Write to NVRAM
REBOOT        = b"reboot\\n"                  # Reset SOC

def wait_device():
    """Wait until an iBoot/DFU device appears on the bus."""
    print("[*] Waiting for iPad in Recovery/DFU mode...")
    print(f"[*] Looking for ECID: {{ECID}}")
    
    while True:
        try:
            dev = irecovery.IRecovery()
            if dev and dev.ecid:
                return dev
        except:
            pass
        time.sleep(0.5)

def main():
    """Main boot management function."""
    print("🔧 iPad iBoot Boot Manager")
    print("=" * 40)
    print(f"Target Device: iPad 1st Gen (A4)")
    print(f"ECID: {{ECID}}")
    print(f"Chip ID: {{CHIP_ID}}")
    print(f"Board ID: {{BOARD_ID}}")
    print(f"Serial: {{SERIAL}}")
    print()
    
    dev = wait_device()
    print(f"[✅] Connected to iBoot (ECID 0x{{dev.ecid:016X}})")
    
    # Verify this is the correct device
    if f"0x{{dev.ecid:016X}}" != ECID:
        print(f"[❌] ECID mismatch! Expected {{ECID}}, got 0x{{dev.ecid:016X}}")
        return 1
    
    print("[🔧] Enabling auto-boot...")
    
    # 1. Enable auto-boot
    dev.send_command(AUTO_BOOT_ON)
    print(f"    -> {{AUTO_BOOT_ON.strip().decode()}}")
    
    # 2. Save to NVRAM
    dev.send_command(SAVEENV)
    print(f"    -> {{SAVEENV.strip().decode()}}")
    
    # 3. Reboot device
    dev.send_command(REBOOT)
    print(f"    -> {{REBOOT.strip().decode()}}")
    
    print("[🚀] Device rebooting - attempting to boot iOS...")
    print("[💡] If it still shows 'Connect to iTunes', the iOS image may be corrupted")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\\n[❌] Aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[❌] Error: {{e}}")
        sys.exit(1)
'''
    
    return script

def main():
    """Main iBoot analyzer function."""
    print("🔧 iBoot Flags Analyzer & Boot Manager")
    print("=" * 50)
    
    # Get iPad information
    ipad_info = get_ipad_iboot_info()
    
    if not ipad_info:
        print("❌ No iPad with iBoot information found!")
        print("\nMake sure your iPad is:")
        print("- Connected via USB")
        print("- In Recovery Mode")
        print("- Showing 'Connect to iTunes'")
        return 1
    
    print("✅ iPad iBoot Information Found!")
    print()
    
    # Display basic info
    print("📱 Device Information:")
    print(f"   Name: {ipad_info.get('device_name', 'Unknown')}")
    print(f"   Vendor ID: {ipad_info.get('vendor_id', 'Unknown')}")
    print(f"   Product ID: {ipad_info.get('product_id', 'Unknown')}")
    print(f"   ECID: {ipad_info.get('ecid', 'Unknown')}")
    print(f"   Chip ID: {ipad_info.get('chip_id', 'Unknown')} (A4 - iPad 1st Gen)")
    print(f"   Board ID: {ipad_info.get('board_id', 'Unknown')}")
    print(f"   Serial: {ipad_info.get('serial_number', 'Unknown')}")
    print()
    
    # Analyze iBoot flags
    iboot_flags = ipad_info.get("iboot_flags")
    if iboot_flags:
        print("🔧 iBoot Flags Analysis:")
        flags_analysis = decode_iboot_flags(iboot_flags)
        
        print(f"   Raw Value: {flags_analysis['raw_hex']} ({flags_analysis['raw_decimal']})")
        print()
        
        print("   Flag Breakdown:")
        flag_descriptions = {
            "auto_boot": "Auto-boot to kernel (bit 0)",
            "secure_epoch_valid": "Secure epoch valid (bit 1)", 
            "force_llb_recovery": "Force LLB recovery (bit 2)",
            "force_iboot_recovery": "Force iBoot recovery (bit 3)",
            "production_switch": "Production mode (bit 4)",
            "development_switch": "Development mode (bit 5)",
            "always_dfu": "Always DFU mode (bit 6)",
            "reserved_bit7": "Reserved bit (bit 7)"
        }
        
        for flag, value in flags_analysis["flags"].items():
            status = "✅ SET" if value else "❌ CLEAR"
            description = flag_descriptions.get(flag, flag.replace('_', ' ').title())
            print(f"     {description}: {status}")
        
        print()
        print("   Interpretation:")
        for key, meaning in flags_analysis["interpretation"].items():
            print(f"     • {meaning}")
        
        print()
        print(f"🚀 Boot Behavior: {flags_analysis['boot_behavior']}")
        
        # Specific analysis for the current flags (0x02)
        if flags_analysis["raw_hex"] == "0x02":
            print()
            print("🎯 Current State Analysis:")
            print("   • Secure epoch valid (bit 1 set)")
            print("   • Auto-boot DISABLED (bit 0 clear)")
            print("   • Device stops at iBoot prompt on boot failure")
            print("   • This is why you see 'Connect to iTunes'")
            print()
            print("💡 Solution: Enable auto-boot flag (change 0x02 → 0x03)")
    
    print()
    print("🛠️ Boot Management Options:")
    print("1. Generate Python script for iBoot communication")
    print("2. Show iBoot commands")
    print()
    
    # Generate boot script
    script_content = generate_python_boot_script(ipad_info)
    
    # Save the script
    script_filename = f"boot_ipad_{ipad_info.get('ecid', 'unknown')}.py"
    try:
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"📄 Boot script generated: {script_filename}")
    except Exception as e:
        print(f"❌ Error saving script: {e}")
    
    # Show commands
    print()
    print("🔧 Manual iBoot Commands:")
    commands = create_iboot_commands(True)
    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. {cmd}")
    
    print()
    print("📋 Installation Requirements:")
    print("   Windows: scoop install libusb irecovery")
    print("   Python:  pip install pyirecovery")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())