#!/usr/bin/env python3
"""Force NAND write - keep device in recovery"""
import subprocess
import time
from pathlib import Path

def force_write():
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("FORCE NAND WRITE")
    print("Put iPad in Recovery Mode NOW")
    input("Press Enter when iPad shows 'Connect to iTunes' screen...")
    
    # Verify connection
    result = subprocess.run([str(irecovery), "-q"], capture_output=True, cwd=str(chargfast_dir))
    if result.returncode != 0:
        print("ERROR: Device not detected")
        return
    
    print("[+] Device detected")
    
    # Get pwned - fast
    print("[+] Pwning device...")
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir), timeout=10)
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir), timeout=5)
    time.sleep(1)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir), timeout=10)
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir), timeout=5)
    time.sleep(1)
    
    # Keep connection alive - set environment
    print("[+] Locking device in recovery...")
    subprocess.run([str(irecovery), "-c", "setenv auto-boot false"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast_dir))
    
    # Direct NAND commands
    print("[+] Opening NAND...")
    subprocess.run([str(irecovery), "-c", "nand open"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "nand part system"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "nand erase 0 0x2000000"], cwd=str(chargfast_dir))
    
    # Flash components
    components = [
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3", "0x0"),
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3", "0x100000"),
        ("extracted/kernelcache.release.k48", "0x400000")
    ]
    
    for comp, addr in components:
        comp_path = chargfast_dir / comp
        if comp_path.exists():
            print(f"[+] Flashing {comp_path.name}...")
            subprocess.run([str(irecovery), "-f", str(comp_path)], cwd=str(chargfast_dir), timeout=30)
            subprocess.run([str(irecovery), "-c", f"nand write {addr}"], cwd=str(chargfast_dir), timeout=30)
    
    # Close NAND
    subprocess.run([str(irecovery), "-c", "nand close"], cwd=str(chargfast_dir))
    
    # Re-enable auto-boot
    print("[+] Setting boot...")
    subprocess.run([str(irecovery), "-c", "setenv auto-boot true"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "reset"], cwd=str(chargfast_dir))
    
    print("[+] DONE - Device should boot")

if __name__ == "__main__":
    force_write()
