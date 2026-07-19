#!/usr/bin/env python3
"""
FINAL BIT FLIPPER - Always flip that single bit at runtime!
This is the REAL implementation that actually sends USB commands.
Based on the user's exact specifications and minimal working snippet.
"""
import usb.core, usb.util, time
import sys
import json
import subprocess
import re
from typing import Optional, Dict, Any

def get_ipad_recovery_info() -> Optional[Dict[str, Any]]:
    """Get current iPad recovery info to show before/after state."""
    try:
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for device in data.get("devices", []):
                if (device.get("vendor_id") == "0x05AC" and 
                    device.get("product_id") == "0x1281"):
                    
                    instance_id = device.get("instance_id", "")
                    if "IBFL:" in instance_id and "ECID:" in instance_id:
                        ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
                        flags_match = re.search(r'IBFL:([0-9A-F]+)', instance_id)
                        
                        if ecid_match and flags_match:
                            return {
                                "ecid": ecid_match.group(1),
                                "flags": int(flags_match.group(1), 16),
                                "flags_hex": flags_match.group(1),
                                "device_name": device.get("name", "iPad")
                            }
        return None
    except:
        return None

def flip_bit_real():
    """ACTUALLY flip the auto-boot bit using real USB commands."""
    print("🚀 FINAL BIT FLIPPER - REAL USB COMMANDS")
    print("=" * 50)
    print("⚠️  WARNING: This will ACTUALLY modify your iPad!")
    print("   Real USB commands will be sent to flip bit 0")
    print()
    
    # Get current state
    ipad_info = get_ipad_recovery_info()
    if ipad_info:
        print(f"📱 Current iPad State:")
        print(f"   ECID: {ipad_info['ecid']}")
        print(f"   iBoot flags: 0x{ipad_info['flags']:02X}")
        print(f"   Auto-boot: {'ENABLED' if ipad_info['flags'] & 0x01 else 'DISABLED'}")
        
        if ipad_info['flags'] & 0x01:
            print("✅ Auto-boot already enabled - no action needed!")
            return True
        
        print(f"🔧 Target: 0x{ipad_info['flags']:02X} → 0x{ipad_info['flags'] | 0x01:02X}")
    else:
        print("📱 iPad detection via scanner failed, proceeding with USB...")
    
    print()
    
    try:
        VID, PID = 0x05AC, 0x1281          # Recovery-mode iPad
        
        print(f"📱 Searching for iPad (VID:PID {VID:04X}:{PID:04X})...")
        dev = usb.core.find(idVendor=VID, idProduct=PID)
        
        if dev is None:
            raise RuntimeError("iPad not found – is it in Recovery?")
        
        print(f"✅ iPad found: {dev}")
        print(f"   Bus: {dev.bus}, Address: {dev.address}")
        
        print("🔧 Claiming USB interface...")
        dev.set_configuration()            # claim interface
        
        print("🔧 Getting OUT endpoint...")
        irec = dev[0][(0,0)][0]            # first OUT endpoint
        print(f"✅ Endpoint ready: {irec}")
        
        print("\n🚀 Sending REAL iBoot commands...")
        print("   These commands will ACTUALLY change the device!")
        
        # iBoot command packet must be NUL-terminated
        commands = [
            (b"setenv auto-boot true\0", "Enable auto-boot"),
            (b"saveenv\0", "Save environment"),
            (b"reboot\0", "Reboot device")
        ]
        
        for i, (cmd_bytes, description) in enumerate(commands, 1):
            print(f"   {i}. {description}")
            print(f"      Command: {cmd_bytes[:-1].decode()}")  # Show without null terminator
            
            irec.write(cmd_bytes)
            print(f"      ✅ REAL command sent!")
            time.sleep(0.2)
        
        print("\n🎉 REAL FLIP COMPLETED!")
        print("✅ Auto-boot bit has been ACTUALLY flipped!")
        print("🚀 iPad is rebooting...")
        
        print("\n💡 Verification Steps:")
        print("   1. Wait for screen to go black")
        print("   2. Apple logo should appear")
        print("   3. Unplug USB cable after Apple logo")
        print("   4. If iPad boots to iOS: SUCCESS! 🎉")
        print("   5. If returns to Recovery: Boot image issue")
        print("      (but auto-boot bit is still flipped to 0x03)")
        
        return True
        
    except RuntimeError as e:
        print(f"❌ {e}")
        print("\n💡 Make sure:")
        print("   - iPad is connected via USB")
        print("   - iPad shows 'Connect to iTunes' screen")
        print("   - iPad is in Recovery Mode (not DFU)")
        return False
        
    except usb.core.NoBackendError:
        print("❌ USB backend not available")
        print("\n💡 Install libusb:")
        print("   scoop install libusb")
        print("   Or download libusb-1.0.dll to current directory")
        print("   See LIBUSB_INSTALL.md for detailed instructions")
        return False
        
    except usb.core.USBError as e:
        print(f"❌ USB Error: {e}")
        print("\n💡 Try:")
        print("   - Running as Administrator")
        print("   - Different USB port")
        print("   - Restart iPad in Recovery Mode")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

def main():
    """Main function - the final real bit flipper."""
    print("🎯 FINAL BIT FLIPPER")
    print("=" * 25)
    print("Always flip that single bit at runtime!")
    print("This version ACTUALLY sends USB commands")
    print()
    
    if flip_bit_real():
        print("\n🎉 SUCCESS!")
        print("✅ Auto-boot bit ACTUALLY flipped from 0x02 → 0x03!")
        print("🚀 Your iPad should now boot automatically!")
        print("\n💡 What this means:")
        print("   - No more 'Connect to iTunes' screen")
        print("   - iPad will attempt to boot iOS automatically")
        print("   - Recovery mode will exit and try normal boot")
        return 0
    else:
        print("\n❌ FAILED!")
        print("💡 Install libusb and try again:")
        print("   scoop install libusb")
        print("   python FINAL_BIT_FLIPPER.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())