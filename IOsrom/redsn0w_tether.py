#!/usr/bin/env python3
"""Launch redsn0w for proper tethered boot"""
import subprocess
import os
from pathlib import Path

def launch_redsn0w():
    """Launch redsn0w for tethered boot"""
    base_dir = Path("N:/ROMLOADDER")
    redsn0w_exe = base_dir / "redSn0w" / "redsn0w-win_0.1" / "redsn0w" / "redsn0w.exe"
    ipsw_path = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    print("🚀 REDSN0W TETHERED BOOT")
    print("=" * 30)
    print("1. Stop Apple Mobile Device Service")
    print("2. Launch redsn0w")
    print("3. Select IPSW → iPad1,1_4.3.3_8J3_Restore.ipsw")
    print("4. Back → Just boot")
    print("5. Follow DFU instructions")
    print()
    
    # Stop Apple service
    try:
        print("🔧 Stopping Apple Mobile Device Service...")
        subprocess.run([
            "powershell", "-Command", 
            "Stop-Service 'Apple Mobile Device Service' -Force"
        ], check=False)
        print("✅ Service stopped")
    except:
        print("⚠️  Service stop failed (may not be running)")
    
    print(f"\n🔧 Launching redsn0w...")
    print(f"📱 IPSW to select: {ipsw_path}")
    
    if redsn0w_exe.exists():
        try:
            subprocess.Popen([str(redsn0w_exe)], cwd=str(redsn0w_exe.parent))
            print("✅ Redsn0w launched!")
            print("\n📋 Steps in redsn0w:")
            print("  1. Extras → Select IPSW")
            print(f"  2. Browse to: {ipsw_path}")
            print("  3. Back → Just boot")
            print("  4. Put iPad in DFU mode when prompted")
            print("  5. Wait for tethered boot (~30 seconds)")
            return True
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False
    else:
        print(f"❌ Redsn0w not found: {redsn0w_exe}")
        return False

if __name__ == "__main__":
    launch_redsn0w()