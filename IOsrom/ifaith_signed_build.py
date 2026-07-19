#!/usr/bin/env python3
"""Launch iFaith to build signed IPSW for bypassed iPad"""
import subprocess
from pathlib import Path

def launch_ifaith():
    """Launch iFaith for signed IPSW building"""
    base_dir = Path("N:/ROMLOADDER")
    ifaith_exe = base_dir / "ifaith-v1.5.9" / "iFaith-v1.5.9.exe"
    
    print("🔧 iFaith SIGNED IPSW BUILDER")
    print("=" * 35)
    print("✅ Your NAND bypass (IBFL: 0x03) is active")
    print("🎯 Building signed IPSW for permanent install")
    print()
    
    if ifaith_exe.exists():
        print(f"🚀 Launching iFaith...")
        print(f"📁 Path: {ifaith_exe}")
        print()
        print("📋 iFaith Steps:")
        print("  1. Put iPad in DFU mode (black screen)")
        print("  2. Click 'Build Signed IPSW'")
        print("  3. Select your custom IPSW base")
        print("  4. Let iFaith dump SHSH and build")
        print("  5. Flash the signed IPSW")
        print()
        
        try:
            subprocess.Popen([str(ifaith_exe)], cwd=str(ifaith_exe.parent))
            print("✅ iFaith launched successfully!")
            return True
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False
    else:
        print(f"❌ iFaith not found: {ifaith_exe}")
        return False

if __name__ == "__main__":
    launch_ifaith()