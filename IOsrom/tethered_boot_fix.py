#!/usr/bin/env python3
"""Tethered boot fix for bypassed iPad"""
import subprocess
import sys
from pathlib import Path

def tethered_boot():
    """Boot iPad with tethered kernel"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    # Find kernel file
    kernel_files = [
        base_dir / "extracted" / "kernelcache.release.k93",
        base_dir / "iPad1,1_iOS9_A4_Final" / "kernelcache.release.k48",
        base_dir / "workspace" / "kernelcache.patched"
    ]
    
    kernel = None
    for k in kernel_files:
        if k.exists():
            kernel = k
            break
    
    if not kernel:
        print("❌ No kernel found")
        return False
    
    print(f"🚀 Tethered boot with: {kernel.name}")
    
    try:
        # Upload and boot kernel
        print("📱 Uploading kernel...")
        result1 = subprocess.run([str(irecovery), "-f", str(kernel)], timeout=30)
        
        if result1.returncode == 0:
            print("✅ Kernel uploaded")
            print("🚀 Booting...")
            result2 = subprocess.run([str(irecovery), "-c", "bootx"], timeout=10)
            
            if result2.returncode == 0:
                print("✅ Tethered boot successful!")
                return True
        
        print("❌ Tethered boot failed")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    tethered_boot()