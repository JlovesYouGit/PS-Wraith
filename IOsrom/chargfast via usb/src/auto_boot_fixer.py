#!/usr/bin/env python3
"""
Automatic iBoot Auto-Boot Bit Flipper
Automatically detects iPad and flips the auto-boot bit (bit 0) at runtime.
Changes iBoot flags from 0x02 → 0x03 to enable automatic booting.
"""
import time
import sys
import subprocess
import json
from typing import Optional, Dict, Any

def get_ipad_info() -> Optional[Dict[str, Any]]:
    """
    Get iPad information if connected in Recovery Mode.
    """
    try:
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            apple_devices = [d for d in data.get("devices", []) if d.get("vendor_id") == "0x05AC"]
            
            # Find iPad in Recovery Mode (Product ID 0x1281)
            for device in apple_devices:
                if device.get("product_id") == "0x1281":
                    instance_id = device.get("instance_id", "")
                    if "IBFL:" in instance_id and "ECID:" in instance_id:
                        import re
                        
                        # Extract key information
                        info = {
                            "device_name": device.get("name", "Unknown"),
                            "vendor_id": device.get("vendor_id"),
                            "product_id": device.get("product_id"),
                            "instance_id": instance_id
                        }
                        
                        # Extract technical details
                        patterns = {
                            "chip_id": r'CPID:([0-9A-F]+)',
                            "ecid": r'ECID:([0-9A-F]+)',
                            "iboot_flags": r'IBFL:([0-9A-F]+)',
                            "serial_number": r'SRNM:\[([^\]]+)\]'
                        }
                        
                        for key, pattern in patterns.items():
                            match = re.search(pattern, instance_id)
                            if match:
                                info[key] = match.group(1)
                        
                        return info
        
        return None
        
    except Exception as e:
        print(f"Error detecting iPad: {e}")
        return None

def flip_auto_boot_bit(ipad_info: Dict[str, Any]) -> bool:
    """
    Flip the auto-boot bit using irecovery.
    Changes iBoot flags from 0x02 → 0x03.
    """
    try:
        import irecovery
        
        print("🔧 Connecting to iPad in Recovery Mode...")
        
        # Wait for device connection
        max_attempts = 10
        device = None
        
        for attempt in range(max_attempts):
            try:
                device = irecovery.IRecovery()
                if device and device.ecid:
                    break
            except:
                pass
            
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1}/{max_attempts} - waiting for device...")
                time.sleep(1)
        
        if not device:
            print("❌ Could not connect to iPad")
            return False
        
        expected_ecid = f"0x{ipad_info.get('ecid', ''):0>16}"
        actual_ecid = f"0x{device.ecid:016X}"
        
        print(f"✅ Connected to iPad (ECID: {actual_ecid})")
        
        # Verify this is the correct device
        if expected_ecid != "0x0000000000000000" and expected_ecid != actual_ecid:
            print(f"⚠️  ECID mismatch! Expected {expected_ecid}, got {actual_ecid}")
            print("   Proceeding anyway...")
        
        current_flags = ipad_info.get("iboot_flags", "02")
        current_flags_int = int(current_flags, 16)
        
        print(f"📊 Current iBoot flags: 0x{current_flags_int:02X} ({current_flags_int})")
        
        # Check if auto-boot is already enabled
        if current_flags_int & 0x01:
            print("✅ Auto-boot already enabled!")
            return True
        
        print("🔧 Flipping auto-boot bit (0x02 → 0x03)...")
        
        # Send iBoot commands to enable auto-boot
        commands = [
            b"setenv auto-boot true\n",
            b"saveenv\n",
            b"reboot\n"
        ]
        
        for i, cmd in enumerate(commands, 1):
            cmd_str = cmd.decode().strip()
            print(f"   {i}. Sending: {cmd_str}")
            
            try:
                device.send_command(cmd)
                time.sleep(0.5)  # Small delay between commands
            except Exception as e:
                print(f"   ⚠️  Command failed: {e}")
                if "reboot" not in cmd_str:  # Don't fail on reboot command
                    return False
        
        print("🚀 Auto-boot bit flipped! iPad should now boot automatically.")
        print("💡 Device is rebooting - it should attempt to boot iOS instead of showing 'Connect to iTunes'")
        
        return True
        
    except ImportError:
        print("❌ pyirecovery not available. Please install: pip install pyirecovery")
        return False
    except Exception as e:
        print(f"❌ Error flipping auto-boot bit: {e}")
        return False

def monitor_and_fix():
    """
    Continuously monitor for iPad and automatically fix auto-boot bit.
    """
    print("🔍 iPad Auto-Boot Bit Flipper - Runtime Monitor")
    print("=" * 55)
    print("Monitoring for iPad in Recovery Mode...")
    print("Press Ctrl+C to stop")
    print()
    
    last_seen_ecid = None
    
    try:
        while True:
            ipad_info = get_ipad_info()
            
            if ipad_info:
                current_ecid = ipad_info.get("ecid")
                
                # Only process if this is a new device or first detection
                if current_ecid != last_seen_ecid:
                    print(f"📱 iPad detected!")
                    print(f"   ECID: {current_ecid}")
                    print(f"   Chip ID: {ipad_info.get('chip_id', 'Unknown')}")
                    print(f"   Serial: {ipad_info.get('serial_number', 'Unknown')}")
                    
                    current_flags = ipad_info.get("iboot_flags", "02")
                    current_flags_int = int(current_flags, 16)
                    
                    print(f"   Current iBoot flags: 0x{current_flags_int:02X}")
                    
                    # Check if auto-boot bit needs to be flipped
                    if not (current_flags_int & 0x01):
                        print("   🔧 Auto-boot disabled - fixing now...")
                        
                        if flip_auto_boot_bit(ipad_info):
                            print("   ✅ Auto-boot bit successfully flipped!")
                            last_seen_ecid = current_ecid
                        else:
                            print("   ❌ Failed to flip auto-boot bit")
                    else:
                        print("   ✅ Auto-boot already enabled - no action needed")
                        last_seen_ecid = current_ecid
                    
                    print()
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error in monitoring loop: {e}")

def main():
    """
    Main function - can run in single-shot or monitor mode.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_and_fix()
    else:
        print("🔧 iPad Auto-Boot Bit Flipper")
        print("=" * 35)
        
        # Single-shot mode
        ipad_info = get_ipad_info()
        
        if not ipad_info:
            print("❌ No iPad found in Recovery Mode")
            print("\nMake sure your iPad is:")
            print("- Connected via USB")
            print("- In Recovery Mode (showing 'Connect to iTunes')")
            return 1
        
        print("📱 iPad detected in Recovery Mode!")
        print(f"   ECID: {ipad_info.get('ecid', 'Unknown')}")
        print(f"   Chip ID: {ipad_info.get('chip_id', 'Unknown')}")
        
        current_flags = ipad_info.get("iboot_flags", "02")
        current_flags_int = int(current_flags, 16)
        
        print(f"   Current iBoot flags: 0x{current_flags_int:02X}")
        
        if current_flags_int & 0x01:
            print("✅ Auto-boot already enabled!")
            return 0
        
        print("🔧 Flipping auto-boot bit...")
        
        if flip_auto_boot_bit(ipad_info):
            print("✅ Success! Auto-boot bit flipped (0x02 → 0x03)")
            print("🚀 iPad should now boot automatically instead of showing 'Connect to iTunes'")
            return 0
        else:
            print("❌ Failed to flip auto-boot bit")
            return 1

if __name__ == "__main__":
    sys.exit(main())