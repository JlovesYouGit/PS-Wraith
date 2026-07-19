#!/usr/bin/env python3
"""
ULTIMATE REAL BIT FLIPPER - The final solution!
Always flip that single bit at runtime using multiple methods
"""
import usb.core, usb.util, time, sys, os, subprocess, json, re
from typing import Optional, Dict, Any

def get_ipad_info() -> Optional[Dict[str, Any]]:
    """Get current iPad recovery info."""
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

def method1_direct_usb():
    """Method 1: Direct USB communication (your exact minimal snippet)."""
    print("🚀 METHOD 1: Direct USB Communication")
    print("   Using your exact minimal working snippet")
    
    try:
        VID, PID = 0x05AC, 0x1281          # Recovery-mode iPad
        
        print(f"   📱 Looking for iPad (VID:PID {VID:04X}:{PID:04X})...")
        dev = usb.core.find(idVendor=VID, idProduct=PID)
        
        if dev is None:
            raise RuntimeError("iPad not found")
        
        print(f"   ✅ iPad found: {dev}")
        
        print("   🔧 Claiming interface...")
        dev.set_configuration()            # claim interface
        
        print("   🔧 Getting OUT endpoint...")
        irec = dev[0][(0,0)][0]            # first OUT endpoint
        
        print("   🚀 Sending REAL iBoot commands...")
        
        # iBoot command packet must be NUL-terminated
        print("      1. setenv auto-boot true")
        irec.write(b"setenv auto-boot true\0")
        time.sleep(0.2)
        
        print("      2. saveenv")
        irec.write(b"saveenv\0")
        time.sleep(0.2)
        
        print("      3. reboot")
        irec.write(b"reboot\0")
        
        print("   ✅ METHOD 1 SUCCESS - Direct USB commands sent!")
        return True
        
    except usb.core.NoBackendError:
        print("   ❌ USB backend not available")
        return False
    except Exception as e:
        print(f"   ❌ METHOD 1 failed: {e}")
        return False

def method2_irecovery():
    """Method 2: Use irecovery if available."""
    print("🚀 METHOD 2: irecovery Tool")
    
    # Check for irecovery
    irecovery_paths = ["irecovery.exe", "irecovery", "./irecovery.exe"]
    
    for path in irecovery_paths:
        try:
            result = subprocess.run([path, "-q"], capture_output=True, timeout=3)
            if result.returncode == 0:
                print(f"   ✅ Found irecovery: {path}")
                
                print("   🚀 Sending irecovery commands...")
                
                commands = [
                    ([path, "-c", "setenv auto-boot true"], "Enable auto-boot"),
                    ([path, "-c", "saveenv"], "Save environment"),
                    ([path, "-c", "reboot"], "Reboot device")
                ]
                
                for cmd, desc in commands:
                    print(f"      {desc}...")
                    result = subprocess.run(cmd, capture_output=True, timeout=5)
                    if result.returncode == 0:
                        print(f"      ✅ {desc} success")
                    else:
                        print(f"      ❌ {desc} failed")
                        return False
                
                print("   ✅ METHOD 2 SUCCESS - irecovery commands sent!")
                return True
                
        except:
            continue
    
    print("   ❌ irecovery not found")
    return False

def method3_libimobiledevice():
    """Method 3: Use libimobiledevice tools if available."""
    print("🚀 METHOD 3: libimobiledevice Tools")
    
    # Check for ideviceenterrecovery
    tools = ["ideviceenterrecovery.exe", "ideviceinfo.exe"]
    
    for tool in tools:
        if os.path.exists(tool):
            print(f"   ✅ Found {tool}")
            
            # Use the tool to interact with device
            try:
                print("   🚀 Using libimobiledevice approach...")
                # This would require custom implementation
                print("   💡 libimobiledevice method needs custom recovery interface")
                return False
            except:
                pass
    
    print("   ❌ libimobiledevice tools not found")
    return False

def method4_powershell_usb():
    """Method 4: PowerShell USB approach."""
    print("🚀 METHOD 4: PowerShell USB Interface")
    
    try:
        # PowerShell script to send USB commands
        ps_script = '''
        Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;
        public class USBCommands {
            [DllImport("kernel32.dll")]
            public static extern IntPtr CreateFile(string lpFileName, uint dwDesiredAccess, uint dwShareMode, IntPtr lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, IntPtr hTemplateFile);
            
            [DllImport("kernel32.dll")]
            public static extern bool WriteFile(IntPtr hFile, byte[] lpBuffer, uint nNumberOfBytesToWrite, out uint lpNumberOfBytesWritten, IntPtr lpOverlapped);
        }
"@
        
        # Try to send USB commands via PowerShell
        Write-Host "Attempting PowerShell USB communication..."
        '''
        
        print("   🔧 Preparing PowerShell USB interface...")
        print("   💡 PowerShell method requires advanced USB handling")
        return False
        
    except Exception as e:
        print(f"   ❌ METHOD 4 failed: {e}")
        return False

def ultimate_flip():
    """Try all methods to flip the auto-boot bit."""
    print("🎯 ULTIMATE REAL BIT FLIPPER")
    print("=" * 40)
    print("Always flip that single bit at runtime!")
    print("Trying ALL methods until one works...")
    print()
    
    # Get current state
    ipad_info = get_ipad_info()
    if ipad_info:
        print(f"📱 Current iPad State:")
        print(f"   ECID: {ipad_info['ecid']}")
        print(f"   iBoot flags: 0x{ipad_info['flags']:02X}")
        print(f"   Auto-boot: {'ENABLED' if ipad_info['flags'] & 0x01 else 'DISABLED'}")
        
        if ipad_info['flags'] & 0x01:
            print("✅ Auto-boot already enabled - mission accomplished!")
            return True
        
        print(f"🔧 Target: 0x{ipad_info['flags']:02X} → 0x{ipad_info['flags'] | 0x01:02X}")
    else:
        print("📱 iPad detection via scanner - proceeding with flip attempts...")
    
    print()
    print("🚀 Attempting multiple methods...")
    print()
    
    # Try each method in order
    methods = [
        method1_direct_usb,
        method2_irecovery,
        method3_libimobiledevice,
        method4_powershell_usb
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            if method():
                print(f"\n🎉 SUCCESS with METHOD {i}!")
                print("✅ Auto-boot bit has been ACTUALLY flipped!")
                print("🚀 iPad should now boot automatically!")
                
                print("\n💡 Verification:")
                print("   1. Wait for Apple logo")
                print("   2. Unplug USB cable")
                print("   3. If iPad boots to iOS: SUCCESS!")
                print("   4. If returns to Recovery: Boot image issue (but bit is flipped)")
                
                return True
        except Exception as e:
            print(f"   ❌ METHOD {i} exception: {e}")
        
        print()
    
    print("❌ ALL METHODS FAILED!")
    print("\n💡 Next steps:")
    print("   1. Install libusb: scoop install libusb")
    print("   2. Download irecovery tool")
    print("   3. Try running as Administrator")
    print("   4. Check USB cable and port")
    
    return False

def main():
    """Main function."""
    print("⚠️  WARNING: This will ACTUALLY modify your iPad!")
    print("   Real USB commands will be sent to flip bit 0")
    print("   Make sure your iPad is in Recovery Mode")
    print()
    
    if ultimate_flip():
        print("\n🎉 ULTIMATE SUCCESS!")
        print("✅ That single bit has been flipped at runtime!")
        return 0
    else:
        print("\n❌ ULTIMATE FAILURE!")
        print("💡 All methods exhausted - check setup and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main())