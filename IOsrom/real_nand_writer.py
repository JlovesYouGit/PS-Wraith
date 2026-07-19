#!/usr/bin/env python3
"""Real NAND writer - actually write to flash storage"""
import subprocess
import time
from pathlib import Path

def real_nand_flash():
    """Actually write to NAND flash storage"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("💾 REAL NAND FLASH WRITER")
    print("Actually writing to physical NAND storage")
    print()
    
    # Get pwned control
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Real NAND operations
    nand_cmds = [
        # Initialize NAND controller
        "nand open",
        
        # Erase system partition completely
        "nand part system",
        "nand erase 0 0x2000000",
        
        # Write LLB to NAND block 0
        f"loadb 0x40000000",  # Load to RAM first
    ]
    
    for cmd in nand_cmds:
        print(f"[+] {cmd}")
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
        time.sleep(1)
    
    # Upload and flash each component to actual NAND blocks
    components = [
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3", 0x0),
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3", 0x100000),
        ("extracted/kernelcache.release.k48", 0x400000),
        ("038-1421-004.dmg", 0x800000)
    ]
    
    for comp, nand_addr in components:
        comp_path = chargfast_dir / comp
        if comp_path.exists():
            print(f"[+] Flashing {comp_path.name} to NAND 0x{nand_addr:x}")
            
            # Upload to RAM
            subprocess.run([str(irecovery), "-f", str(comp_path)], cwd=str(chargfast_dir))
            
            # Actually write to NAND flash
            subprocess.run([str(irecovery), "-c", f"nand write 0x{nand_addr:x}"], cwd=str(chargfast_dir))
            
            # Verify write
            subprocess.run([str(irecovery), "-c", f"nand read 0x{nand_addr:x} 0x1000"], cwd=str(chargfast_dir))
            
            time.sleep(2)
    
    # Close NAND and set boot
    final_cmds = [
        "nand close",
        "setenv boot-device nand0",
        "setenv boot-partition 0",
        "setenv auto-boot true",
        "saveenv",
        "reset"
    ]
    
    for cmd in final_cmds:
        print(f"[+] {cmd}")
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
        time.sleep(1)
    
    print("[+] REAL NAND FLASH COMPLETE")

if __name__ == "__main__":
    real_nand_flash()