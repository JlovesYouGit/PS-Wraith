#!/usr/bin/env python
"""
Simple auto-boot fixer for iOS devices.
"""
import subprocess
import sys
from pathlib import Path

def find_irecovery():
    """Find irecovery executable."""
    current_dir = Path.cwd()
    irecovery_exe = current_dir / "irecovery.exe"
    if irecovery_exe.exists():
        return str(irecovery_exe)
    return None

def fix_auto_boot():
    """Fix auto-boot on connected iOS device."""
    irecovery_path = find_irecovery()
    
    if not irecovery_path:
        print("❌ irecovery.exe not found in current directory")
        return False
    
    print("🔧 Fixing auto-boot on iOS device...")
    
    commands = [
        "setenv auto-boot true",
        "saveenv", 
        "reboot"
    ]
    
    for cmd in commands:
        print(f"📤 Executing: {cmd}")
        try:
            result = subprocess.run([
                irecovery_path, "-c", cmd
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                print(f"❌ Command failed: {result.stderr}")
                return False
            else:
                print(f"✅ Command successful")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Command timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("✅ Auto-boot fix completed! Device should reboot normally.")
    return True

def main():
    print("🍎 iOS Auto-Boot Fixer")
    print("=" * 30)
    
    # Check if device is connected first
    irecovery_path = find_irecovery()
    if not irecovery_path:
        print("❌ irecovery.exe not found")
        print("Make sure irecovery.exe is in the current directory")
        return 1
    
    # Test connection
    print("🔍 Checking for iOS device...")
    try:
        result = subprocess.run([
            irecovery_path, "-q"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ No iOS device found in recovery mode")
            print("Make sure your iOS device is:")
            print("- Connected via USB")
            print("- In recovery mode (iBoot)")
            print("- Recognized by Windows")
            return 1
        
        print("✅ iOS device found!")
        
    except Exception as e:
        print(f"❌ Error checking device: {e}")
        return 1
    
    # Fix auto-boot
    if fix_auto_boot():
        print("\n🎉 Success! Your iOS device should now boot normally.")
        return 0
    else:
        print("\n❌ Failed to fix auto-boot. Check device connection.")
        return 1

if __name__ == "__main__":
    sys.exit(main())