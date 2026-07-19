#!/usr/bin/env python
import subprocess
import sys

def check_apple_devices():
    """Check for any Apple devices connected."""
    try:
        # Check via PowerShell for Apple devices
        cmd = [
            "powershell", "-Command",
            "Get-PnpDevice | Where-Object { $_.InstanceId -like '*VID_05AC*' -or $_.FriendlyName -like '*Apple*' -or $_.FriendlyName -like '*iPad*' -or $_.FriendlyName -like '*iPhone*' } | Select-Object FriendlyName, Status"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        
        if result.returncode == 0 and result.stdout.strip():
            print("📱 Apple devices found:")
            print(result.stdout)
            return True
        else:
            print("❌ No Apple devices detected")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_recovery_mode():
    """Check if device is in recovery mode."""
    try:
        result = subprocess.run(["irecovery.exe", "-q"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Device in recovery mode!")
            print(result.stdout)
            return True
        else:
            print("❌ No device in recovery mode")
            return False
    except:
        print("❌ Cannot check recovery mode")
        return False

if __name__ == "__main__":
    print("🔍 Checking for iOS devices...")
    
    has_apple = check_apple_devices()
    has_recovery = check_recovery_mode()
    
    if not has_apple:
        print("\n💡 Device not detected. Try:")
        print("- Different USB cable/port")
        print("- Check Device Manager for Apple devices")
        print("- Restart device")
    elif not has_recovery:
        print("\n💡 Device found but not in recovery mode.")
        print("To enter recovery mode:")
        print("1. Connect device via USB")
        print("2. Hold Power + Home buttons (10+ seconds)")
        print("3. Release when you see recovery screen")
        print("4. Run this script again")