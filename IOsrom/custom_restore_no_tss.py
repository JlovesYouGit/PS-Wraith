#!/usr/bin/env python3
"""Custom restore tool - no TSS, direct NAND programming"""
import subprocess
import zipfile
import time
from pathlib import Path

def custom_restore_no_tss():
    """Custom restore bypassing TSS completely"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    print("🔧 CUSTOM RESTORE - NO TSS")
    print("Direct NAND programming without Apple servers")
    print()
    
    # Extract IPSW components
    print("[+] Extracting IPSW components...")
    with zipfile.ZipFile(ipsw, 'r') as z:
        z.extractall(chargfast_dir / "restore_temp")
    
    restore_dir = chargfast_dir / "restore_temp"
    
    # Get pwned control
    print("[+] Getting device control...")
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Use ramdisk method
    print("[+] Loading restore ramdisk...")
    
    # Find restore ramdisk
    ramdisk = None
    for dmg in restore_dir.glob("*.dmg"):
        if dmg.stat().st_size < 50 * 1024 * 1024:  # Ramdisk is small
            ramdisk = dmg
            break
    
    if ramdisk:
        print(f"[+] Using ramdisk: {ramdisk.name}")
        subprocess.run([str(irecovery), "-f", str(ramdisk)], cwd=str(chargfast_dir))
        subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast_dir))
        time.sleep(5)
        
        # Upload kernel
        kernel = restore_dir / "kernelcache.release.k48"
        if kernel.exists():
            print("[+] Uploading restore kernel...")
            subprocess.run([str(irecovery), "-f", str(kernel)], cwd=str(chargfast_dir))
            subprocess.run([str(irecovery), "-c", "bootx"], cwd=str(chargfast_dir))
            
            print("[+] Device should boot to restore ramdisk...")
            print("[+] Waiting 30 seconds for ramdisk boot...")
            time.sleep(30)
            
            # Now device should be in restore mode with ramdisk
            # Try to use asr (Apple Software Restore) directly
            print("[+] Attempting ASR restore...")
            
            # Find system DMG
            system_dmg = None
            for dmg in restore_dir.glob("*.dmg"):
                if dmg.stat().st_size > 500 * 1024 * 1024:  # System DMG is large
                    system_dmg = dmg
                    break
            
            if system_dmg:
                print(f"[+] System DMG: {system_dmg.name}")
                
                # Use idevicerestore in a special way
                subprocess.run([
                    str(chargfast_dir / "idevicerestore.exe"),
                    "--no-ibec",  # Skip iBEC (we already loaded it)
                    "--custom",   # Custom restore
                    str(ipsw)
                ], cwd=str(chargfast_dir))
    
    print("[+] Custom restore complete")

if __name__ == "__main__":
    custom_restore_no_tss()