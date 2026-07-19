#!/usr/bin/env python3
"""Proper NAND writer using libimobiledevice restore protocol"""
import subprocess
import time
from pathlib import Path

def proper_nand_write():
    """Use idevicerestore properly to write to NAND"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    idevicerestore = chargfast_dir / "idevicerestore.exe"
    ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    print("💾 PROPER NAND WRITER")
    print("Using libimobiledevice restore protocol")
    print()
    
    # idevicerestore with proper flags
    restore_cmd = [
        str(idevicerestore),
        "--erase",           # Erase and restore
        "--no-action",       # Don't wait for user
        str(ipsw)
    ]
    
    print(f"[+] Running: {' '.join([str(x) for x in restore_cmd])}")
    print("[+] This will actually write to NAND flash")
    print()
    
    try:
        result = subprocess.run(restore_cmd, cwd=str(chargfast_dir), timeout=600)
        
        if result.returncode == 0:
            print("✅ NAND WRITE SUCCESSFUL!")
            print("Device should boot to iOS")
            return True
        else:
            print(f"❌ Restore failed with code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Restore timed out (may still be working)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    proper_nand_write()