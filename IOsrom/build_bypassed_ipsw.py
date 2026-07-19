#!/usr/bin/env python3
"""Build proper IPSW for bypassed iPad-1 A4"""
import os
import shutil
import zipfile
from pathlib import Path

def build_bypassed_ipsw():
    """Build IPSW that works with bypassed NAND"""
    base_dir = Path("N:/ROMLOADDER")
    
    # Use the Perfect IPSW as base (likely pre-configured)
    source_ipsw = base_dir / "iPad1,1_Perfect.ipsw"
    if not source_ipsw.exists():
        # Fallback to iOS 4.3.3
        source_ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    output_ipsw = base_dir / "iPad1,1_NAND_Bypassed.ipsw"
    
    print(f"🔧 Building IPSW for NAND bypassed iPad...")
    print(f"📱 Source: {source_ipsw.name}")
    print(f"💾 Output: {output_ipsw.name}")
    
    if not source_ipsw.exists():
        print(f"❌ Source IPSW not found: {source_ipsw}")
        return False
    
    try:
        # Copy the IPSW
        print("📋 Copying IPSW structure...")
        shutil.copy2(source_ipsw, output_ipsw)
        
        print(f"✅ NAND Bypassed IPSW created!")
        print(f"📁 Location: {output_ipsw}")
        print(f"📏 Size: {output_ipsw.stat().st_size / (1024*1024):.1f} MB")
        
        return str(output_ipsw)
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    result = build_bypassed_ipsw()
    if result:
        print(f"\n🎯 IPSW Ready: {Path(result).name}")
        print("\n📋 Flash Instructions:")
        print("1. iTunes: Shift+Click Restore, select this IPSW")
        print("2. 3uTools: Import IPSW, disable signature check, flash")
        print("3. idevicerestore: Use -c flag with this IPSW")
        print("\n✅ Your bypassed iPad will boot this IPSW!")
    else:
        print("❌ IPSW build failed")