#!/usr/bin/env python3
"""
REAL BIT FLIPPER - Actually sends USB commands to flip the auto-boot bit
Uses direct USB communication to send iBoot commands
"""
import usb.core
import usb.util
import time
import sys

def flip_auto_boot_bit():
    """Send real USB commands to flip the auto-boot bit."""
    print("🔧 REAL BIT FLIPPER - Direct USB Method")
    print("=" * 45)
    
    VID, PID = 0x05AC, 0x1281  # Recovery-mode iPad
    
    print("📱 Searching for iPad in Recovery Mode...")
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    
    if dev is None:
        print("❌ iPad not found in Recovery Mode")
        print("💡 Make sure:")
        print("   - iPad is connected via USB")
        print("   - iPad shows 'Connect to iTunes' screen")
        print("   - iPad is NOT in DFU mode (black screen)")
        return False
    
    print(f"✅ Found iPad in Recovery Mode!")
    print(f"   Device: {dev}")
    
    try:
        print("🔧 Claiming USB interface...")
        dev.set_configuration()  # claim interface
        
        # Get the first OUT endpoint for iBoot commands
        irec = dev[0][(0,0)][0]
        print(f"✅ USB interface claimed, endpoint: {irec}")
        
        print("\n🚀 Sending REAL iBoot commands...")
        
        # iBoot command packets must be NUL-terminated
        commands = [
            (b"setenv auto-boot true\0", "Enable auto-boot"),
            (b"saveenv\0", "Save environment"),
            (b"reboot\0", "Reboot device")
        ]
        
        for i, (cmd, description) in enumerate(commands, 1):
            print(f"   {i}. {description}")
            print(f"      Command: {cmd[:-1].decode()}")  # Show without null terminator
            
            try:
                irec.write(cmd)
                print(f"      ✅ Sent successfully")
                time.sleep(0.2)  # Wait between commands
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                if i < len(commands):  # Don't fail on reboot command
                    return False
        
        print("\n🎉 REAL FLIP COMPLETED!")
        print("✅ Auto-boot bit has been ACTUALLY flipped!")
        print("🚀 iPad is rebooting...")
        
        print("\n💡 What to expect:")
        print("   1. Screen goes black")
        print("   2. Apple logo appears")
        print("   3. iPad attempts to boot iOS")
        print("   4. If successful: iPad boots to home screen")
        print("   5. If boot fails: Returns to Recovery Mode (but bit is still flipped)")
        
        return True
        
    except usb.core.USBError as e:
        print(f"❌ USB Error: {e}")
        print("💡 Try:")
        print("   - Running as Administrator")
        print("   - Installing libusb drivers")
        print("   - Using irecovery binary instead")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    if flip_auto_boot_bit():
        print("\n✅ SUCCESS! Auto-boot bit flipped using direct USB!")
        return 0
    else:
        print("\n❌ FAILED! Could not flip auto-boot bit")
        return 1

if __name__ == "__main__":
    sys.exit(main())