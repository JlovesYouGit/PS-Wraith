#!/usr/bin/env python3
"""
Direct Bit Flipper - Uses command-line tools to flip the auto-boot bit
Always flips bit 0 from 0 to 1 (0x02 → 0x03) at runtime
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

def flip_bit_with_irecovery_cli(ipad_data: Dict) -> bool:
    """Use irecovery command-line tool to flip the bit."""
    try:
        # Check if irecovery command is available
        result = subprocess.run(["irecovery", "-q"], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ irecovery command not found - trying pyirecovery module...")
            return flip_bit_with_pyirecovery(ipad_data)
        
        print("🔧 Using irecovery command-line tool...")
        
        current_flags = ipad_data["flags"]
        
        # Check if auto-boot is already enabled
        if current_flags & 0x01:
            print(f"✅ Auto-boot already enabled! (0x{current_flags:02X})")
            return True
        
        print(f"🔧 Flipping bit: 0x{current_flags:02X} → 0x{current_flags | 0x01:02X}")
        
        # Send commands using irecovery CLI
        commands = [
            ["irecovery", "-c", "setenv auto-boot true"],
            ["irecovery", "-c", "saveenv"],
            ["irecovery", "-c", "reboot"]
        ]
        
        for i, cmd in enumerate(commands, 1):
            cmd_str = " ".join(cmd[2:]) if len(cmd) > 2 else cmd[-1]
            print(f"   {i}. Executing: {cmd_str}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0 and "reboot" not in cmd_str:
                print(f"   ❌ Command failed: {result.stderr}")
                return False
            
            time.sleep(0.5)
        
        print("✅ Commands sent successfully!")
        print("🚀 iPad should now auto-boot instead of showing 'Connect to iTunes'")
        return True
        
    except Exception as e:
        print(f"❌ CLI method failed: {e}")
        return flip_bit_with_pyirecovery(ipad_data)

def flip_bit_with_pyirecovery(ipad_data: Dict) -> bool:
    """Fallback: Use pyirecovery Python module."""
    try:
        # Try different import methods
        try:
            from pyirecovery import IRecovery
        except ImportError:
            import pyirecovery
            IRecovery = pyirecovery.IRecovery
        
        print("🔧 Using pyirecovery Python module...")
        
        # Connect to device
        device = IRecovery()
        if not device:
            print("❌ Could not connect to device")
            return False
        
        current_flags = ipad_data["flags"]
        
        if current_flags & 0x01:
            print(f"✅ Auto-boot already enabled! (0x{current_flags:02X})")
            return True
        
        print(f"🔧 Flipping bit: 0x{current_flags:02X} → 0x{current_flags | 0x01:02X}")
        
        # Send commands
        device.send_command("setenv auto-boot true")
        time.sleep(0.2)
        device.send_command("saveenv")
        time.sleep(0.2)
        device.send_command("reboot")
        
        print("✅ Bit flipped successfully!")
        return True
        
    except ImportError:
        print("❌ pyirecovery module not available")
        return False
    except Exception as e:
        print(f"❌ pyirecovery method failed: {e}")
        return False

def flip_bit_with_pymobiledevice3(ipad_data: Dict) -> bool:
    """Alternative: Use pymobiledevice3 for recovery operations."""
    try:
        print("🔧 Trying pymobiledevice3...")
        
        # Use pymobiledevice3 CLI
        result = subprocess.run([
            "python", "-m", "pymobiledevice3", "recovery", "info"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📱 Device detected via pymobiledevice3")
            
            # Try to set auto-boot
            cmd_result = subprocess.run([
                "python", "-m", "pymobiledevice3", "recovery", "shell", 
                "setenv auto-boot true; saveenv; reboot"
            ], capture_output=True, text=True, timeout=15)
            
            if cmd_result.returncode == 0:
                print("✅ Auto-boot enabled via pymobiledevice3!")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ pymobiledevice3 method failed: {e}")
        return False

def main():
    """Main bit flipper with multiple fallback methods."""
    print("🚀 DIRECT BIT FLIPPER")
    print("=" * 30)
    print("Always flips auto-boot bit (0x02 → 0x03)")
    print()
    
    # Detect iPad
    ipad = get_ipad_info()
    
    if not ipad:
        print("❌ No iPad in Recovery Mode detected")
        print("\nMake sure:")
        print("- iPad is connected via USB")
        print("- iPad is in Recovery Mode (showing 'Connect to iTunes')")
        return 1
    
    print(f"📱 iPad detected!")
    print(f"   ECID: {ipad['ecid']}")
    print(f"   Current iBoot flags: 0x{ipad['flags']:02X}")
    
    # Check if bit is already flipped
    if ipad['flags'] & 0x01:
        print("✅ Auto-boot bit already enabled - no action needed!")
        return 0
    
    print("\n🔧 Attempting to flip auto-boot bit...")
    print("   Trying multiple methods...")
    
    # Try different methods in order of preference
    methods = [
        ("irecovery CLI", flip_bit_with_irecovery_cli),
        ("pyirecovery module", flip_bit_with_pyirecovery),
        ("pymobiledevice3", flip_bit_with_pymobiledevice3)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔧 Trying {method_name}...")
        
        if method_func(ipad):
            print(f"✅ SUCCESS! Bit flipped using {method_name}")
            print("🚀 iPad should now boot automatically!")
            return 0
    
    print("\n❌ All methods failed to flip the bit")
    print("💡 Manual steps:")
    print("   1. Use iTunes/Finder to restore iPad")
    print("   2. Or use specialized tools like 3uTools")
    return 1

if __name__ == "__main__":
    sys.exit(main())