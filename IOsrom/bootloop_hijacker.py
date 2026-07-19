#!/usr/bin/env python3
"""Hijack bootloop and inject our ROM"""
import subprocess
import time
import sys
from pathlib import Path

def hijack_bootloop():
    """Catch device in bootloop and inject ROM"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("🔥 BOOTLOOP HIJACKER")
    print("=" * 20)
    print("⚡ Catching device in bootloop...")
    print("🎯 Injecting ROM during reboot cycle")
    print()
    
    # Wait for device to appear in bootloop
    print("⏳ Waiting for bootloop device...")
    
    for attempt in range(30):  # 30 second window
        try:
            result = subprocess.run([
                str(irecovery), "-q"
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                print(f"📱 Device caught! Attempt {attempt + 1}")
                print("🚀 RAPID INJECTION...")
                
                # Rapid fire commands before it reboots again
                commands = [
                    # Upload kernel immediately
                    ([str(irecovery), "-f", str(base_dir / "extracted/kernelcache.release.k93")], "Kernel"),
                    ([str(irecovery), "-c", "bootx"], "Boot"),
                ]
                
                for cmd, desc in commands:
                    try:
                        print(f"  ⚡ {desc}...")
                        subprocess.run(cmd, timeout=3)
                        time.sleep(0.1)  # Minimal delay
                    except:
                        pass  # Keep trying
                
                print("✅ Injection complete!")
                return True
                
        except:
            pass
        
        time.sleep(1)
        print(f"  ⏳ Waiting... {attempt + 1}/30")
    
    print("❌ Failed to catch bootloop")
    return False

def continuous_hijack():
    """Continuously try to hijack bootloop"""
    print("🔄 CONTINUOUS BOOTLOOP HIJACK")
    print("=" * 35)
    print("Press Ctrl+C to stop")
    print()
    
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    try:
        while True:
            try:
                # Check if device is available
                result = subprocess.run([
                    str(irecovery), "-q"
                ], capture_output=True, text=True, timeout=1)
                
                if result.returncode == 0:
                    print("📱 Device detected - HIJACKING!")
                    
                    # Immediate kernel injection
                    kernels = [
                        base_dir / "extracted/kernelcache.release.k93",
                        base_dir / "iPad1,1_iOS9_A4_Final/kernelcache.release.k48",
                        base_dir / "workspace/kernelcache.patched"
                    ]
                    
                    for kernel in kernels:
                        if kernel.exists():
                            print(f"⚡ Injecting: {kernel.name}")
                            try:
                                subprocess.run([
                                    str(irecovery), "-f", str(kernel)
                                ], timeout=2)
                                subprocess.run([
                                    str(irecovery), "-c", "bootx"
                                ], timeout=1)
                                break
                            except:
                                continue
                    
                    time.sleep(5)  # Wait for boot attempt
                
            except:
                pass
            
            time.sleep(0.5)  # Fast polling
            
    except KeyboardInterrupt:
        print("\n🛑 Hijack stopped")
        return True

if __name__ == "__main__":
    print("🎯 BOOTLOOP HIJACKER")
    print("Catch device in bootloop and inject ROM")
    print()
    
    choice = input("1. Single hijack attempt\n2. Continuous hijack\nChoice (1/2): ")
    
    if choice == "1":
        hijack_bootloop()
    else:
        continuous_hijack()