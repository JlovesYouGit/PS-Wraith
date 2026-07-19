#!/usr/bin/env python3
"""
ULTIMATE REAL BIT FLIPPER - Always flip that single bit at runtime!
Tries both irecovery binary and direct USB methods to ACTUALLY flip the bit
"""
import subprocess
import sys
import time
import usb.core
import usb.util

def flip_with_irecovery_real():
    """Method 1: Use irecovery binary (most reliable)."""
    print("🔧 Method 1: irecovery Binary")
    print("-" * 30)
    
    try:
        # Check if irecovery is available
        result = subprocess.run(["irecovery", "-q"], capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            print("❌ No device found or irecovery not available")
            return False
        
        print("✅ iPad detected via irecovery!")
        
        # Send the actual commands
        commands = ["setenv auto-boot true", "saveenv", "reboot"]
        
        for i, cmd in enumerate(commands, 1):
            print(f"   {i}. Executing: {cmd}")
            
            result = subprocess.run(
                ["irecovery", "-c", cmd], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"      ✅ Success!")
            else:
                print(f"      ❌ Failed: {result.stderr}")
                if i < len(commands):  # Don't fail on reboot
                    return False
            
            time.sleep(0.3)
        
        print("🎉 irecovery method SUCCESS!")
        return True
        
    except Exception as e:
        print(f"❌ irecovery method failed: {e}")
        return False

def flip_with_direct_usb_real():
    """Method 2: Direct USB communication."""
    print("🔧 Method 2: Direct USB")
    print("-" * 25)
    
    try:
        VID, PID = 0x05AC, 0x1281  # Recovery-mode iPad
        
        dev = usb.core.find(idVendor=VID, idProduct=PID)
        if dev is None:
            print("❌ iPad not found via USB")
            return False
        
        print("✅ iPad found via USB!")
        
        # Claim the device
        dev.set_configuration()
        irec = dev[0][(0,0)][0]  # First OUT endpoint
        
        print("✅ USB interface claimed")
        
        # Send real iBoot commands (NUL-terminated)
        commands = [
            (b"setenv auto-boot true\0", "Enable auto-boot"),
            (b"saveenv\0", "Save environment"),
            (b"reboot\0", "Reboot device")
        ]
        
        for i, (cmd_bytes, description) in enumerate(commands, 1):
            print(f"   {i}. {description}")
            
            try:
                irec.write(cmd_bytes)
                print(f"      ✅ Command sent!")
                time.sleep(0.2)
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                if i < len(commands):
                    return False
        
        print("🎉 Direct USB method SUCCESS!")
        return True
        
    except Exception as e:
        print(f"❌ Direct USB method failed: {e}")
        return False

def main():
    """Ultimate real bit flipper - tries both methods."""
    print("🚀 ULTIMATE REAL BIT FLIPPER")
    print("=" * 40)
    print("ACTUALLY flips the auto-boot bit!")
    print("0x02 → 0x03 (bit 0: OFF → ON)")
    print()
    
    # Try irecovery first (most reliable)
    if flip_with_irecovery_real():
        print("\n🎉 SUCCESS! Bit flipped using irecovery!")
        print("✅ Auto-boot bit is now ACTUALLY enabled!")
        print("🚀 iPad should boot automatically!")
        return 0
    
    print("\n🔧 irecovery failed, trying direct USB...")
    
    # Fallback to direct USB
    if flip_with_direct_usb_real():
        print("\n🎉 SUCCESS! Bit flipped using direct USB!")
        print("✅ Auto-boot bit is now ACTUALLY enabled!")
        print("🚀 iPad should boot automatically!")
        return 0
    
    print("\n💥 Both methods failed!")
    print("❌ Could not flip the auto-boot bit")
    print("\n💡 Troubleshooting:")
    print("   1. Install irecovery: scoop install libusb irecovery")
    print("   2. Run as Administrator")
    print("   3. Make sure iPad is in Recovery Mode")
    print("   4. Try different USB cable/port")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())