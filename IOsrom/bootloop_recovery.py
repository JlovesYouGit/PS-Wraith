#!/usr/bin/env python3
"""Bootloop recovery - fix the silicon burns"""
import subprocess
import time
from pathlib import Path

def recover_bootloop():
    """Recover from bootloop caused by silicon burns"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("🚑 BOOTLOOP RECOVERY")
    print("Fixing silicon burn damage")
    print()
    
    # Force DFU mode during bootloop
    print("[+] Force device into DFU mode:")
    print("    1. Hold Power + Home for 15 seconds")
    print("    2. Release Power, keep Home for 10 seconds")
    print("    3. Screen should be BLACK")
    
    input("Press Enter when in DFU mode...")
    
    # Try to get pwned state
    for attempt in range(5):
        try:
            print(f"[+] Recovery attempt {attempt + 1}")
            
            # Upload iBSS
            subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], 
                         cwd=str(chargfast_dir), timeout=10)
            subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir), timeout=5)
            time.sleep(3)
            
            # Upload iBEC
            subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], 
                         cwd=str(chargfast_dir), timeout=10)
            subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir), timeout=5)
            time.sleep(3)
            
            # Check if we got control
            result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print("[+] Got control back!")
                break
                
        except Exception as e:
            print(f"[-] Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    # Fix the damage
    print("[+] Fixing silicon burn damage...")
    
    # Reset problematic registers
    recovery_cmds = [
        # Reset boot ROM patches
        "mw 0x20001000 0x00000000",
        "mw 0x20001004 0x00000000", 
        "mw 0x20001008 0x00000000",
        
        # Reset eFuses to safe values
        "mw 0x3C100000 0x00000000",
        "mw 0x3C100004 0x00000000",
        "mw 0x3C100008 0x00000000",
        
        # Safe boot environment
        "setenv boot-args -v",
        "setenv auto-boot true",
        "saveenv",
        
        # Try to boot kernel directly
        "bootx"
    ]
    
    for cmd in recovery_cmds:
        print(f"[+] Recovery: {cmd}")
        try:
            subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir), timeout=5)
        except:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    recover_bootloop()