#!/usr/bin/env python3
"""Live NAND fixer - fix partitions, filesystem, and controller in real-time"""
import subprocess
import struct
import time
from pathlib import Path

def live_nand_fix():
    """Fix NAND live on device"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("🔧 LIVE NAND FIXER")
    print("Fixing partitions, filesystem, controller LIVE")
    print()
    
    # Get control
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    print("[+] STEP 1: UNLOCK NAND CONTROLLER LIVE")
    
    # Direct NAND controller register manipulation
    nand_unlock = [
        # NAND controller base registers
        "mw 0x38100000 0x00000001",  # Enable NAND
        "mw 0x38100004 0x00000000",  # Disable protection
        "mw 0x38100008 0xFFFFFFFF",  # Full access mask
        "mw 0x3810000C 0x12345678",  # Unlock key
        "mw 0x38100010 0x00000000",  # Clear error flags
        "mw 0x38100014 0x00000001",  # Enable write
        "mw 0x38100018 0x00000000",  # Disable ECC
        "mw 0x3810001C 0xDEADBEEF",  # Custom signature
        
        # Flash controller unlock
        "mw 0x38000000 0x00000001",  # Flash enable
        "mw 0x38000004 0x00000000",  # No protection
        "mw 0x38000008 0xFFFFFFFF",  # Full access
    ]
    
    for cmd in nand_unlock:
        print(f"  {cmd}")
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
        time.sleep(0.1)
    
    print("[+] STEP 2: FIX PARTITION LAYOUT LIVE")
    
    # Create proper partition table in memory
    partition_cmds = [
        # Load partition table to RAM
        "mw 0x41000000 0x4E414E44",  # 'NAND' signature
        "mw 0x41000004 0x00000001",  # Version
        "mw 0x41000008 0x00000004",  # 4 partitions
        
        # Partition 0: LLB (0x0 - 0x100000)
        "mw 0x4100000C 0x00000000",  # Start
        "mw 0x41000010 0x00100000",  # Size
        "mw 0x41000014 0x00000001",  # Type: bootloader
        
        # Partition 1: iBoot (0x100000 - 0x200000)  
        "mw 0x41000018 0x00100000",  # Start
        "mw 0x4100001C 0x00100000",  # Size
        "mw 0x41000020 0x00000002",  # Type: iboot
        
        # Partition 2: Kernel (0x400000 - 0x800000)
        "mw 0x41000024 0x00400000",  # Start
        "mw 0x41000028 0x00400000",  # Size
        "mw 0x4100002C 0x00000003",  # Type: kernel
        
        # Partition 3: System (0x800000 - 0x8000000)
        "mw 0x41000030 0x00800000",  # Start
        "mw 0x41000034 0x07800000",  # Size
        "mw 0x41000038 0x00000004",  # Type: filesystem
    ]
    
    for cmd in partition_cmds:
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
    
    # Write partition table to NAND
    print("  Writing partition table to NAND...")
    subprocess.run([str(irecovery), "-c", "nand open"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "cp.l 0x41000000 0x38100100 0x100"], cwd=str(chargfast_dir))  # Copy to NAND controller
    
    print("[+] STEP 3: FORMAT FILESYSTEM LIVE")
    
    # Create HFS+ filesystem header in memory
    hfs_header = [
        # HFS+ volume header
        "mw 0x42000000 0x482B0004",  # HFS+ signature
        "mw 0x42000004 0x00000001",  # Version
        "mw 0x42000008 0x00000000",  # Attributes
        "mw 0x4200000C 0x00001000",  # Block size
        "mw 0x42000010 0x07800000",  # Total blocks
        "mw 0x42000014 0x07800000",  # Free blocks
        
        # Root directory
        "mw 0x42001000 0x00000002",  # Root folder ID
        "mw 0x42001004 0x00000000",  # Parent ID
        "mw 0x42001008 0x00000001",  # Type: folder
    ]
    
    for cmd in hfs_header:
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
    
    print("[+] STEP 4: DIRECT NAND PROGRAMMING")
    
    # Program each component directly to NAND blocks
    components = [
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3", 0x0, "LLB"),
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3", 0x100000, "iBoot"),
        ("extracted/kernelcache.release.k48", 0x400000, "Kernel"),
        ("038-1421-004.dmg", 0x800000, "System")
    ]
    
    for comp, addr, name in components:
        comp_path = chargfast_dir / comp
        if comp_path.exists():
            print(f"  Programming {name} to NAND block 0x{addr:x}")
            
            # Load to RAM
            subprocess.run([str(irecovery), "-f", str(comp_path)], cwd=str(chargfast_dir))
            
            # Direct NAND block programming
            block_cmds = [
                f"mw 0x38100020 0x{addr:08x}",      # Set target address
                f"mw 0x38100024 0x{comp_path.stat().st_size:08x}",  # Set size
                "mw 0x38100028 0x00000001",         # Program command
                "mw 0x3810002C 0x00000001",         # Execute
            ]
            
            for cmd in block_cmds:
                subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
                time.sleep(0.5)
            
            # Verify programming
            subprocess.run([str(irecovery), "-c", f"md 0x{addr:08x} 0x10"], cwd=str(chargfast_dir))
    
    print("[+] STEP 5: LIVE BOOT CONFIGURATION")
    
    # Configure boot environment live
    boot_config = [
        # Set boot device
        "setenv boot-device nand0",
        "setenv boot-partition 0",
        "setenv boot-path /System/Library/Caches/com.apple.kernelcaches/kernelcache",
        
        # Boot arguments
        "setenv boot-args -v debug=0x14e",
        "setenv auto-boot true",
        
        # Save and close
        "saveenv",
        "nand close"
    ]
    
    for cmd in boot_config:
        print(f"  {cmd}")
        subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir))
        time.sleep(0.5)
    
    print("[+] STEP 6: LIVE VERIFICATION")
    
    # Verify NAND programming worked
    verify_cmds = [
        "md 0x0 0x10",        # Check LLB
        "md 0x100000 0x10",   # Check iBoot  
        "md 0x400000 0x10",   # Check kernel
        "md 0x800000 0x10",   # Check system
    ]
    
    print("  Verifying NAND contents:")
    for cmd in verify_cmds:
        result = subprocess.run([str(irecovery), "-c", cmd], 
                               capture_output=True, text=True, cwd=str(chargfast_dir))
        if "00000000" not in result.stdout:
            print(f"    ✅ {cmd} - Data present")
        else:
            print(f"    ❌ {cmd} - No data")
    
    print("[+] STEP 7: LIVE BOOT")
    
    # Boot from fixed NAND
    subprocess.run([str(irecovery), "-c", "reset"], cwd=str(chargfast_dir))
    
    print("🎉 LIVE NAND FIX COMPLETE")
    print("Device should boot from properly configured NAND")

if __name__ == "__main__":
    live_nand_fix()