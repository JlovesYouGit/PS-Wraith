#!/usr/bin/env python3
"""Check IPSW structure and why sn0wbreeze fails"""
import os
import zipfile
from pathlib import Path

def check_ipsw_structure():
    """Check IPSW internal structure"""
    base_dir = Path("N:/ROMLOADDER")
    ipsw_file = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    if not ipsw_file.exists():
        print(f"❌ IPSW not found: {ipsw_file}")
        return False
    
    print(f"📱 Checking IPSW: {ipsw_file.name}")
    print(f"📏 Size: {ipsw_file.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        with zipfile.ZipFile(ipsw_file, 'r') as zip_ref:
            files = zip_ref.namelist()
            print(f"📄 Files in IPSW: {len(files)}")
            
            # Check for required files that sn0wbreeze needs
            required_files = [
                'BuildManifest.plist',
                'Restore.plist',
                'kernelcache.release.k48',  # iPad1,1 kernel
                'iBSS.k48ap.RELEASE.img3',
                'iBEC.k48ap.RELEASE.img3',
                'LLB.k48ap.RELEASE.img3'
            ]
            
            print("\n🔍 Required files check:")
            missing = []
            for req_file in required_files:
                found = any(req_file in f for f in files)
                if found:
                    print(f"  ✅ {req_file}: Found")
                else:
                    print(f"  ❌ {req_file}: Missing")
                    missing.append(req_file)
            
            # Check firmware folder structure
            firmware_files = [f for f in files if 'Firmware' in f]
            print(f"\n📁 Firmware files: {len(firmware_files)}")
            
            # Look for iPad1,1 specific files
            ipad_files = [f for f in files if 'k48' in f.lower()]
            print(f"📱 iPad1,1 (k48) files: {len(ipad_files)}")
            for f in ipad_files[:5]:  # Show first 5
                print(f"  - {f}")
            
            if missing:
                print(f"\n❌ Missing files may cause sn0wbreeze failure:")
                for m in missing:
                    print(f"  - {m}")
                return False
            else:
                print(f"\n✅ IPSW structure looks valid for sn0wbreeze")
                return True
                
    except zipfile.BadZipFile:
        print("❌ IPSW file is corrupted or not a valid ZIP")
        return False
    except Exception as e:
        print(f"❌ Error checking IPSW: {e}")
        return False

if __name__ == "__main__":
    check_ipsw_structure()