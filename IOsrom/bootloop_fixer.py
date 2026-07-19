#!/usr/bin/env python3
"""Fix bootloop - kernel/filesystem issue"""
import subprocess
import time
from pathlib import Path

def fix_bootloop():
    """Fix the fucking bootloop"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("🔧 BOOTLOOP FIXER")
    print("Apple logo loop = bootloader works, kernel/fs fucked")
    print()
    
    # Force device back to recovery
    print("[+] Forcing back to recovery mode...")
    time.sleep(5)  # Wait for bootloop
    
    # Try to catch it
    for i in range(10):
        try:
            result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print("[+] Caught device in recovery!")
                break
        except:
            pass
        time.sleep(1)
    
    # Get pwned again
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Fix the kernel issue
    print("[+] Fixing kernel boot arguments...")
    kernel_fixes = [
        "setenv boot-args -v debug=0x14e",  # Verbose + debug
        "setenv boot-device nand0s1",       # Correct boot device
        "setenv boot-path /",               # Root path
        "saveenv"
    ]
    
    for fix in kernel_fixes:
        subprocess.run([str(irecovery), "-c", fix], cwd=str(chargfast_dir))
    
    # Try different kernel
    print("[+] Trying different kernel...")
    kernels = [
        "extracted/kernelcache.release.k48",
        base_dir / "iPad1,1_iOS9_A4_Final/kernelcache.release.k48",
        base_dir / "workspace/kernelcache.patched"
    ]
    
    for kernel in kernels:
        if Path(kernel).exists():
            print(f"[+] Testing kernel: {Path(kernel).name}")
            subprocess.run([str(irecovery), "-f", str(kernel)], cwd=str(chargfast_dir))
            subprocess.run([str(irecovery), "-c", "bootx"], cwd=str(chargfast_dir))
            time.sleep(10)  # Wait for boot
            
            # Check if it worked
            try:
                result = subprocess.run([str(irecovery), "-q"], capture_output=True, timeout=2)
                if result.returncode != 0:
                    print("[+] SUCCESS! Device booted!")
                    return True
            except:
                print("[+] SUCCESS! Device booted!")
                return True
            
            print("[-] Still in bootloop, trying next kernel...")
    
    print("[-] All kernels failed. Filesystem issue.")
    return False

if __name__ == "__main__":
    fix_bootloop()