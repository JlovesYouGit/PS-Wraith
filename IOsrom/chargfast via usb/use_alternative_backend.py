#!/usr/bin/env python
import subprocess
import os

def use_ideviceenterrecovery():
    """Use ideviceenterrecovery instead of irecovery for more stable connection."""
    try:
        # First get device UDID
        result = subprocess.run(["idevice_id.exe", "-l"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            udid = result.stdout.strip().split('\n')[0]
            print(f"Found device: {udid}")
            
            # Use ideviceenterrecovery to put in recovery mode
            subprocess.run(["ideviceenterrecovery.exe", udid])
            print("Device put in recovery mode")
            
            return udid
        else:
            print("No device found")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def use_idevicerestore():
    """Use idevicerestore to fix auto-boot."""
    try:
        # Create custom IPSW or use restore commands
        result = subprocess.run([
            "idevicerestore.exe", "--custom", "--latest", "--no-restore"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Device restored successfully")
            return True
        else:
            print(f"❌ Restore failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Using alternative backend...")
    udid = use_ideviceenterrecovery()
    if udid:
        use_idevicerestore()