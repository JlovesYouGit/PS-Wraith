#!/usr/bin/env python3
"""Extract iPad1,1 firmware components"""
import zipfile
import os
from pathlib import Path

def extract_ipad1_firmware():
    """Extract iPad1,1 k48ap components"""
    ipsw_path = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
    extract_dir = Path("N:/ROMLOADDER/chargfast via usb/extracted")
    
    if extract_dir.exists():
        import shutil
        shutil.rmtree(extract_dir)
    
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📱 Extracting iPad1,1 firmware from: {ipsw_path.name}")
    
    with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
        # Extract all files
        zip_ref.extractall(extract_dir)
        
        # List k48ap files
        k48_files = [f for f in zip_ref.namelist() if 'k48' in f.lower()]
        print(f"🔧 Found {len(k48_files)} k48ap files:")
        for f in k48_files:
            print(f"  - {f}")
    
    print(f"✅ Extracted to: {extract_dir}")
    
    # Check for required boot files
    ibss_path = extract_dir / "Firmware" / "dfu" / "iBSS.k48ap.RELEASE.dfu"
    ibec_path = extract_dir / "Firmware" / "dfu" / "iBEC.k48ap.RELEASE.dfu"
    
    if ibss_path.exists():
        print(f"✅ iBSS found: {ibss_path}")
    else:
        print(f"❌ iBSS missing: {ibss_path}")
    
    if ibec_path.exists():
        print(f"✅ iBEC found: {ibec_path}")
    else:
        print(f"❌ iBEC missing: {ibec_path}")
    
    return extract_dir

if __name__ == "__main__":
    extract_ipad1_firmware()