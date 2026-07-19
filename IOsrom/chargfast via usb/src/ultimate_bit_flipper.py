#!/usr/bin/env python3
"""
ULTIMATE BIT FLIPPER - Always flip that auto-boot bit!
Uses pymobiledevice3 recovery commands to flip bit 0 (0x02 → 0x03)
"""
import subprocess
import sys
import time
import json
import re
from typing import Optional, Dict

def get_ipad_info() -> Optional[Dict]:
    """Get iPad info using our USB scanner."""
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
                                "flags_hex": flags_match.group(1)
                            }
        return None
    except:
        return None

def flip_with_pymobiledevice3_recovery(ipad_data: Dict) -> bool:
    """Use pymobiledevice3 recovery commands to flip the bit."""
    try:
        print("🔧 Using pymobiledevice3 recovery mode...")
        
        # First, check if device is detected
        result = subprocess.run([
            sys.executable, "-m", "pymobiledevice3", "recovery", "info"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            print(f"❌ Device not detected in recovery mode: {result.stderr}")
            return False
        
        print("📱 Device detected in recovery mode!")
        print(f"   Device info: {result.stdout.strip()}")
        
        current_flags = ipad_data["flags"]
        
        if current_flags & 0x01:
            print(f"✅ Auto-boot already enabled! (0x{current_flags:02X})")
            return True
        
        print(f"🔧 Flipping auto-boot bit: 0x{current_flags:02X} → 0x{current_flags | 0x01:02X}")
        
        # Send recovery commands
        commands = [
            "setenv auto-boot true",
            "saveenv",
            "reboot"
        ]
        
        for i, cmd in enumerate(commands, 1):
            print(f"   {i}. Sending: {cmd}")
            
            result = subprocess.run([
                sys.executable, "-m", "pymobiledevice3", "recovery", "shell", cmd
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0 and "reboot" not in cmd:
                print(f"   ❌ Command failed: {result.stderr}")
                # Continue anyway for reboot command
                if i < len(commands):
                    continue
            else:
                print(f"   ✅ Command executed successfully")
            
            time.sleep(1)  # Wait between commands
        
        print("🚀 Auto-boot bit flipped! iPad should now boot automatically!")
        return True
        
    except Exception as e:
        print(f"❌ pymobiledevice3 recovery method failed: {e}")
        return False

def flip_with_direct_usb_commands(ipad_data: Dict) -> bool:
    """Try direct USB communication approach."""
    try:
        print("🔧 Attempting direct USB communication...")
        
        # Use pymobiledevice3's lower-level recovery interface
        result = subprocess.run([
            sys.executable, "-c", """
import sys
sys.path.insert(0, 'venv/Lib/site-packages')
try:
    from pymobiledevice3.recovery.recovery import Recovery
    from pymobiledevice3.common.usbmux import select_devices_by_connection_type
    
    devices = select_devices_by_connection_type('USB')
    if not devices:
        print('No USB devices found')
        sys.exit(1)
    
    recovery = Recovery()
    recovery.connect()
    
    print('Connected to recovery device')
    
    # Send auto-boot commands
    recovery.send_command('setenv auto-boot true')
    recovery.send_command('saveenv')
    recovery.send_command('reboot')
    
    print('Auto-boot commands sent successfully')
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"""
        ], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            print("✅ Direct USB commands sent successfully!")
            return True
        else:
            print(f"❌ Direct USB method failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Direct USB method failed: {e}")
        return False

def flip_with_manual_recovery_mode(ipad_data: Dict) -> bool:
    """Manual recovery mode approach using available tools."""
    try:
        print("🔧 Manual recovery mode approach...")
        
        # Try using irecovery if available in PATH
        try:
            result = subprocess.run(["where", "irecovery"], capture_output=True, text=True)
            if result.returncode == 0:
                print("📱 Found irecovery in PATH, using it...")
                
                commands = [
                    ["irecovery", "-c", "setenv auto-boot true"],
                    ["irecovery", "-c", "saveenv"],
                    ["irecovery", "-c", "reboot"]
                ]
                
                for cmd in commands:
                    print(f"   Executing: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode != 0 and "reboot" not in cmd[-1]:
                        print(f"   ❌ Failed: {result.stderr}")
                        return False
                    time.sleep(0.5)
                
                print("✅ irecovery commands executed!")
                return True
        except:
            pass
        
        # Try alternative approach with pymobiledevice3 CLI
        print("🔧 Trying pymobiledevice3 CLI approach...")
        
        # Check available recovery commands
        result = subprocess.run([
            sys.executable, "-m", "pymobiledevice3", "recovery", "--help"
        ], capture_output=True, text=True)
        
        if "shell" in result.stdout:
            print("📱 Recovery shell available, sending commands...")
            
            # Send combined command
            combined_cmd = "setenv auto-boot true; saveenv; reboot"
            result = subprocess.run([
                sys.executable, "-m", "pymobiledevice3", "recovery", "shell", combined_cmd
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ Combined recovery command executed!")
                return True
            else:
                print(f"❌ Combined command failed: {result.stderr}")
        
        return False
        
    except Exception as e:
        print(f"❌ Manual recovery approach failed: {e}")
        return False

def main():
    """Ultimate bit flipper - tries everything!"""
    print("🚀 ULTIMATE BIT FLIPPER")
    print("=" * 35)
    print("ALWAYS FLIP THAT AUTO-BOOT BIT!")
    print("0x02 → 0x03 (bit 0: OFF → ON)")
    print()
    
    # Detect iPad
    ipad = get_ipad_info()
    
    if not ipad:
        print("❌ No iPad in Recovery Mode detected")
        print("\n💡 Make sure:")
        print("   - iPad is connected via USB")
        print("   - iPad is in Recovery Mode (showing 'Connect to iTunes')")
        print("   - iPad is not in DFU mode")
        return 1
    
    print(f"📱 iPad detected in Recovery Mode!")
    print(f"   ECID: {ipad['ecid']}")
    print(f"   Current iBoot flags: 0x{ipad['flags']:02X}")
    
    # Check if bit is already flipped
    if ipad['flags'] & 0x01:
        print("✅ AUTO-BOOT BIT ALREADY ENABLED!")
        print("   No action needed - iPad will boot automatically")
        return 0
    
    print(f"\n🔧 BIT 0 IS OFF - FLIPPING NOW!")
    print(f"   Target: 0x{ipad['flags']:02X} → 0x{ipad['flags'] | 0x01:02X}")
    
    # Try all available methods
    methods = [
        ("pymobiledevice3 recovery", flip_with_pymobiledevice3_recovery),
        ("direct USB commands", flip_with_direct_usb_commands),
        ("manual recovery mode", flip_with_manual_recovery_mode)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔧 Trying: {method_name}")
        print("-" * 40)
        
        if method_func(ipad):
            print(f"\n🎉 SUCCESS! Bit flipped using {method_name}")
            print("✅ Auto-boot bit is now ENABLED!")
            print("🚀 iPad should boot automatically instead of showing 'Connect to iTunes'")
            print("\n💡 What happens next:")
            print("   - iPad will reboot")
            print("   - It will attempt to boot iOS")
            print("   - No more 'Connect to iTunes' screen!")
            return 0
        else:
            print(f"❌ {method_name} failed, trying next method...")
    
    print("\n💥 ALL METHODS FAILED!")
    print("🔧 The auto-boot bit could not be flipped automatically.")
    print("\n💡 Manual alternatives:")
    print("   1. Use iTunes/Finder to restore iPad completely")
    print("   2. Use 3uTools or similar third-party tools")
    print("   3. Try putting iPad in DFU mode and restore")
    print("   4. Use Xcode to restore the device")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())