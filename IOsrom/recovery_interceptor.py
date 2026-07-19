#!/usr/bin/env python3
"""Intercept Recovery Mode and force boot"""
import subprocess
import time
from pathlib import Path

def recovery_intercept():
    """Wait for Recovery Mode and immediately boot"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("🎯 RECOVERY MODE INTERCEPTOR")
    print("=" * 30)
    print("⏳ Waiting for Recovery Mode...")
    
    while True:
        try:
            result = subprocess.run([
                str(irecovery), "-q"
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0 and "MODE: Recovery" in result.stdout:
                print("📱 RECOVERY MODE DETECTED!")
                print("🚀 IMMEDIATE BOOT SEQUENCE...")
                
                # Don't set any environment variables - just boot
                boot_commands = [
                    # Upload iBSS
                    ([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], "iBSS"),
                    ([str(irecovery), "-c", "go"], "Execute iBSS"),
                    
                    # Wait and upload iBEC
                    (["timeout", "2"], "Wait"),
                    ([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], "iBEC"),
                    ([str(irecovery), "-c", "go"], "Execute iBEC"),
                    
                    # Wait and upload kernel
                    (["timeout", "2"], "Wait"),
                    ([str(irecovery), "-f", "extracted/kernelcache.release.k48"], "Kernel"),
                    ([str(irecovery), "-c", "bootx"], "Boot Kernel"),
                ]
                
                for cmd, desc in boot_commands:
                    print(f"  ⚡ {desc}...")
                    try:
                        if cmd[0] == "timeout":
                            time.sleep(int(cmd[1]))
                        else:
                            subprocess.run(cmd, cwd=str(chargfast_dir), timeout=5)
                    except Exception as e:
                        print(f"    ⚠️  {desc} failed: {e}")
                
                print("✅ Boot sequence complete!")
                return True
                
        except Exception as e:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    recovery_intercept()