#!/usr/bin/env python3
"""Write filesystem directly to NAND"""
import subprocess
import zipfile
from pathlib import Path

def write_filesystem():
    """Extract and write filesystem to NAND"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    print("💾 FILESYSTEM WRITER")
    print("=" * 20)
    
    # Extract filesystem DMG
    with zipfile.ZipFile(ipsw, 'r') as z:
        dmg_files = [f for f in z.namelist() if f.endswith('.dmg')]
        print(f"📁 Found {len(dmg_files)} DMG files")
        
        for dmg in dmg_files:
            if 'restore' in dmg.lower() or '038-' in dmg:
                print(f"📤 Extracting: {dmg}")
                z.extract(dmg, chargfast_dir)
                
                # Write DMG to NAND
                dmg_path = chargfast_dir / dmg
                print(f"💾 Writing to NAND: {dmg_path.name}")
                
                try:
                    # Mount and write filesystem
                    subprocess.run([
                        str(irecovery), "-c", f"ramdisk {dmg_path}"
                    ], cwd=str(chargfast_dir), timeout=60)
                    
                    subprocess.run([
                        str(irecovery), "-c", "fsboot"
                    ], cwd=str(chargfast_dir), timeout=30)
                    
                    print("✅ Filesystem written")
                    return True
                    
                except Exception as e:
                    print(f"❌ Write failed: {e}")
    
    return False

if __name__ == "__main__":
    write_filesystem()