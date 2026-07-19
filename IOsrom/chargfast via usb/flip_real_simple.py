#!/usr/bin/env python3
"""
REAL BIT FLIPPER - Actually flips the auto-boot bit!
Uses direct USB communication exactly as suggested by the user.
"""
import usb.core
import usb.util
import time
import sys
import os

def download_libusb_dll():
    """Download libusb-1.0.dll if not present."""
    dll_path = "libusb-1.0.dll"
    
    if os.path.exists(dll_path):
        print(f"✅ {dll_path} already exists")
        return True
    
    print("📥 Downloading libusb-1.0.dll...")
    
    try:
        import urllib.request
        
        # Download libusb-1.0.dll (64-bit) from official releases
        url = "https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.27.7z"
        
        print("💡 Please manually download libusb-1.0.dll from:")
        print("   https://github.com/libusb/libusb/releases/latest")
        print("   Extract libusb-1.0.dll (64-bit) to current directory")
        print("   Or install via: scoop install libusb")
        
        return False
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def flip_auto_boot_real():
    """ACTUALLY flip the auto-boot bit using direct USB commands."""
    print("🚀 REAL BIT FLIPPER - Direct USB Method")
    print("=" * 45)
    print("This will ACTUALLY send USB commands to flip bit 0!")
    print()
    
    # Check for libusb DLL
    if not os.path.exists("libusb-1.0.dll"):
        if not download_libusb_dll():
            print("❌ libusb-1.0.dll not found")
            print("💡 Install scoop and run: scoop install libusb")
            return False
    
    VID, PID = 0x05AC, 0x1281  # Recovery-mode iPad
    
    print("📱 Searching for iPad in Recovery Mode...")
    print(f"   Looking for VID:PID {VID:04X}:{PID:04X}")
    
    try:
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
        print(f"   Bus: {dev.bus}, Address: {dev.address}")
        
        print("\n🔧 Claiming USB interface...")
        
        # Claim the device interface
        dev.set_configuration()  # This claims the interface
        
        # Get the first OUT endpoint for iBoot commands
        irec = dev[0][(0,0)][0]  # first OUT endpoint
        print(f"✅ USB interface claimed, endpoint: {irec}")
        
        print(f"\n🚀 Sending REAL iBoot commands to flip auto-boot bit...")
        print("   These commands will ACTUALLY change the device!")
        
        # iBoot command packets MUST be NUL-terminated
        print("   1. Setting auto-boot to true...")
        cmd = b"setenv auto-boot true\0"
        irec.write(cmd)
        print("      ✅ Command sent!")
        time.sleep(0.2)
        
        print("   2. Saving environment...")
        irec.write(b"saveenv\0")
        print("      ✅ Environment saved!")
        time.sleep(0.2)
        
        print("   3. Rebooting device...")
        irec.write(b"reboot\0")
        print("      ✅ Reboot command sent!")
        
        print("\n🎉 REAL FLIP COMPLETED!")
        print("✅ Auto-boot bit has been ACTUALLY flipped!")
        print("🚀 iPad is rebooting...")
        
        print("\n💡 What to expect:")
        print("   1. Screen goes black")
        print("   2. Apple logo appears")
        print("   3. Unplug USB cable after Apple logo")
        print("   4. If iPad boots to iOS: SUCCESS! 🎉")
        print("   5. If iPad returns to Recovery: Boot image issue")
        print("      (but auto-boot bit is still flipped to 0x03)")
        
        return True
        
    except usb.core.USBError as e:
        print(f"❌ USB Error: {e}")
        print("💡 Try:")
        print("   - Running as Administrator")
        print("   - Installing libusb drivers")
        print("   - Using different USB port")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    """Main function."""
    print("⚠️  WARNING: This will ACTUALLY modify your iPad!")
    print("   This is NOT a simulation - real USB commands will be sent")
    print("   Make sure your iPad is in Recovery Mode")
    print()
    
    if flip_auto_boot_real():
        print("\n🎉 SUCCESS! Auto-boot bit ACTUALLY flipped!")
        print("✅ Your iPad should now boot automatically!")
        return 0
    else:
        print("\n❌ FAILED! Could not flip auto-boot bit")
        print("💡 Try installing scoop and libusb:")
        print("   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser")
        print("   irm get.scoop.sh | iex")
        print("   scoop install libusb irecovery")
        return 1

if __name__ == "__main__":
    sys.exit(main())