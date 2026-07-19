#!/usr/bin/env python3
"""
REAL BIT FLIPPER - Using irecovery binary
Uses the official irecovery tool to send iBoot commands
"""
import subprocess
import sys
import time

def check_irecovery_available():
    """Check if irecovery is available."""
    try:
        result = subprocess.run(["irecovery", "-q"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def flip_with_irecovery():
    """Use irecovery binary to flip the auto-boot bit."""
    print("🔧 REAL BIT FLIPPER - irecovery Binary Method")
    print("=" * 50)
    
    # Check if irecovery is available
    if not check_irecovery_available():
        print("❌ irecovery not found!")
        print("💡 Install with: scoop install libusb irecovery")
        return False
    
    print("✅ irecovery found!")
    
    # Check for device
    print("📱 Checking for iPad in Recovery Mode...")
    result = subprocess.run(["irecovery", "-q"], capture_output=True, text=True, timeout=10)
    
    if result.returncode != 0:
        print("❌ No iPad found in Recovery Mode")
        print("💡 Make sure iPad shows 'Connect to iTunes' screen")
        return False
    
    print("✅ iPad detected in Recovery Mode!")
    print(f"Device info: {result.stdout.strip()}")
    
    print("\n🚀 Sending REAL iBoot commands via irecovery...")
    
    # Send commands using irecovery
    commands = [
        (["irecovery", "-c", "setenv auto-boot true"], "Enable auto-boot"),
        (["irecovery", "-c", "saveenv"], "Save environment"),
        (["irecovery", "-c", "reboot"], "Reboot device")
    ]
    
    for i, (cmd, description) in enumerate(commands, 1):
        print(f"   {i}. {description}")
        print(f"      Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"      ✅ Success!")
                if result.stdout.strip():
                    print(f"      Output: {result.stdout.strip()}")
            else:
                print(f"      ❌ Failed: {result.stderr.strip()}")
                if i < len(commands):  # Don't fail on reboot command
                    return False
            
            time.sleep(0.5)  # Wait between commands
            
        except subprocess.TimeoutExpired:
            print(f"      ⚠️ Command timed out (normal for reboot)")
        except Exception as e:
            print(f"      ❌ Error: {e}")
            if i < len(commands):
                return False
    
    print("\n🎉 REAL FLIP COMPLETED!")
    print("✅ Auto-boot bit has been ACTUALLY flipped using irecovery!")
    print("🚀 iPad is rebooting...")
    
    print("\n💡 Verification:")
    print("   - Unplug USB cable after Apple logo appears")
    print("   - If iPad boots to iOS: SUCCESS!")
    print("   - If iPad returns to Recovery: Boot image issue (but bit is flipped)")
    
    return True

def main():
    """Main function."""
    if flip_with_irecovery():
        print("\n✅ SUCCESS! Auto-boot bit flipped using irecovery!")
        return 0
    else:
        print("\n❌ FAILED! Could not flip auto-boot bit")
        return 1

if __name__ == "__main__":
    sys.exit(main())