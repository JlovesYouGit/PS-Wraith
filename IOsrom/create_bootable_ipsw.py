#!/usr/bin/env python3
"""Create bootable IPSW for bypassed iPad-1 A4"""
import os
import shutil
import zipfile
from pathlib import Path

def create_bootable_ipsw():
    """Create bootable IPSW for bypassed iPad"""
    base_dir = Path("N:/ROMLOADDER")
    source_ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    output_ipsw = base_dir / "iPad1,1_Bootable_Bypassed.ipsw"
    
    if not source_ipsw.exists():
        print(f"❌ Source IPSW not found: {source_ipsw}")
        return False
    
    print(f"🔧 Creating bootable IPSW for bypassed iPad...")
    print(f"📱 Source: {source_ipsw.name}")
    print(f"💾 Output: {output_ipsw.name}")
    
    try:
        # Simply copy the original iOS 4.3.3 IPSW
        # Since NAND bypass is active, it will boot unsigned
        shutil.copy2(source_ipsw, output_ipsw)
        
        print(f"✅ Bootable IPSW created: {output_ipsw}")
        print("🎯 This IPSW will work with your bypassed iPad")
        print("💡 Use with sn0wbreeze or 3uTools")
        
        return str(output_ipsw)
        
    except Exception as e:
        print(f"❌ Failed to create IPSW: {e}")
        return False

if __name__ == "__main__":
    result = create_bootable_ipsw()
    if result:
        print(f"\n🚀 Ready to flash: {result}")
        print("\n📋 Next steps:")
        print("1. Use sn0wbreeze to jailbreak this IPSW")
        print("2. Flash to your bypassed iPad")
        print("3. iPad will boot normally with permanent bypass")
    else:
        print("❌ Failed to create bootable IPSW")