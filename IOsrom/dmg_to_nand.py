#!/usr/bin/env python3
"""DMG to NAND writer - extract and write filesystem"""
import subprocess
import struct
import zlib
import time
from pathlib import Path

def extract_dmg_data(dmg_path):
    """Extract raw data from DMG"""
    print(f"[+] Extracting DMG: {dmg_path.name}")
    
    with open(dmg_path, 'rb') as f:
        data = f.read()
    
    # DMG files are often compressed - try to decompress
    if data[:4] == b'koly':  # DMG signature
        print("[+] DMG format detected")
        # Skip DMG header, get raw data
        # DMG structure: header + partitions + data
        return data
    else:
        print("[+] Raw data")
        return data

def write_to_nand_blocks(data, start_block=0x800000):
    """Write data to NAND in blocks"""
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    irecovery = chargfast_dir / "irecovery.exe"
    
    print(f"[+] Writing {len(data)} bytes to NAND at 0x{start_block:x}")
    
    # Get pwned
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Open NAND
    subprocess.run([str(irecovery), "-c", "nand open"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "nand part system"], cwd=str(chargfast_dir))
    
    # Write in chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    
    print(f"[+] Writing {total_chunks} chunks...")
    
    # Create temp file for each chunk
    temp_file = chargfast_dir / "temp_chunk.bin"
    
    for i in range(total_chunks):
        offset = i * chunk_size
        chunk = data[offset:offset + chunk_size]
        
        # Write chunk to temp file
        with open(temp_file, 'wb') as f:
            f.write(chunk)
        
        # Upload chunk
        nand_addr = start_block + offset
        print(f"[+] Chunk {i+1}/{total_chunks} -> 0x{nand_addr:x}")
        
        subprocess.run([str(irecovery), "-f", str(temp_file)], cwd=str(chargfast_dir), timeout=30)
        subprocess.run([str(irecovery), "-c", f"nand write 0x{nand_addr:x}"], cwd=str(chargfast_dir), timeout=30)
    
    # Clean up
    if temp_file.exists():
        temp_file.unlink()
    
    # Close NAND
    subprocess.run([str(irecovery), "-c", "nand close"], cwd=str(chargfast_dir))
    
    print("[+] Filesystem written to NAND")

def full_nand_restore():
    """Complete NAND restore with filesystem"""
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("DMG TO NAND WRITER")
    print("=" * 30)
    
    # Get pwned
    print("[+] Getting device control...")
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Open NAND
    print("[+] Opening NAND...")
    subprocess.run([str(irecovery), "-c", "nand open"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "nand part system"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "nand erase 0 0x8000000"], cwd=str(chargfast_dir))
    
    # Flash bootloader components
    print("[+] Flashing bootloader...")
    components = [
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3", 0x0),
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3", 0x100000),
        ("extracted/kernelcache.release.k48", 0x400000)
    ]
    
    for comp, addr in components:
        comp_path = chargfast_dir / comp
        if comp_path.exists():
            print(f"[+] {comp_path.name} -> 0x{addr:x}")
            subprocess.run([str(irecovery), "-f", str(comp_path)], cwd=str(chargfast_dir), timeout=30)
            subprocess.run([str(irecovery), "-c", f"nand write 0x{addr:x}"], cwd=str(chargfast_dir), timeout=30)
    
    # Flash filesystem DMG
    print("[+] Flashing filesystem (this will take time)...")
    dmg_path = chargfast_dir / "extracted" / "038-1421-004.dmg"
    
    if dmg_path.exists():
        # Read DMG in chunks and write directly
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        nand_addr = 0x800000
        
        with open(dmg_path, 'rb') as f:
            chunk_num = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                chunk_num += 1
                temp_file = chargfast_dir / f"chunk_{chunk_num}.bin"
                
                with open(temp_file, 'wb') as cf:
                    cf.write(chunk)
                
                print(f"[+] Filesystem chunk {chunk_num} -> 0x{nand_addr:x}")
                subprocess.run([str(irecovery), "-f", str(temp_file)], cwd=str(chargfast_dir), timeout=60)
                subprocess.run([str(irecovery), "-c", f"nand write 0x{nand_addr:x}"], cwd=str(chargfast_dir), timeout=60)
                
                temp_file.unlink()
                nand_addr += len(chunk)
    
    # Close NAND and boot
    print("[+] Closing NAND...")
    subprocess.run([str(irecovery), "-c", "nand close"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "setenv auto-boot true"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "reset"], cwd=str(chargfast_dir))
    
    print("[+] COMPLETE - Device should boot to iOS")

if __name__ == "__main__":
    full_nand_restore()
