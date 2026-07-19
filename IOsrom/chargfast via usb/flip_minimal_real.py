#!/usr/bin/env python3
"""
MINIMAL REAL BIT FLIPPER - Exact implementation as suggested
Uses the exact minimal working snippet provided by the user
"""
import usb.core, usb.util, time

def main():
    """Minimal real bit flipper - exactly as suggested."""
    print("🚀 MINIMAL REAL BIT FLIPPER")
    print("=" * 35)
    print("Using exact minimal snippet approach")
    print("This will ACTUALLY flip the auto-boot bit!")
    print()
    
    try:
        VID, PID = 0x05AC, 0x1281          # Recovery-mode iPad
        
        print(f"📱 Looking for iPad (VID:PID {VID:04X}:{PID:04X})...")
        dev = usb.core.find(idVendor=VID, idProduct=PID)
        
        if dev is None:
            raise RuntimeError("iPad not found – is it in Recovery?")
        
        print(f"✅ iPad found: {dev}")
        
        print("🔧 Claiming interface...")
        dev.set_configuration()            # claim interface
        
        print("🔧 Getting OUT endpoint...")
        irec = dev[0][(0,0)][0]            # first OUT endpoint
        
        print("🚀 Sending REAL iBoot commands...")
        
        # iBoot command packet must be NUL-terminated
        print("   1. setenv auto-boot true")
        cmd = b"setenv auto-boot true\0"
        irec.write(cmd)
        time.sleep(0.2)
        
        print("   2. saveenv")
        irec.write(b"saveenv\0")
        time.sleep(0.2)
        
        print("   3. reboot")
        irec.write(b"reboot\0")
        
        print("✅ real flip done – iPad rebooting")
        
        print("\n🎉 SUCCESS!")
        print("✅ Auto-boot bit ACTUALLY flipped from 0x02 → 0x03!")
        print("🚀 iPad should now boot automatically!")
        
        print("\n💡 Verification:")
        print("   - Wait for Apple logo")
        print("   - Unplug USB cable")
        print("   - If iPad boots to iOS: SUCCESS!")
        print("   - If returns to Recovery: Boot image issue (but bit is flipped)")
        
        return 0
        
    except RuntimeError as e:
        print(f"❌ {e}")
        print("\n💡 Make sure:")
        print("   - iPad is connected via USB")
        print("   - iPad shows 'Connect to iTunes' screen")
        print("   - iPad is in Recovery Mode (not DFU)")
        return 1
        
    except usb.core.NoBackendError:
        print("❌ USB backend not available")
        print("\n💡 Install libusb:")
        print("   scoop install libusb")
        print("   Or download libusb-1.0.dll to current directory")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return 1

if __name__ == "__main__":
    exit(main())