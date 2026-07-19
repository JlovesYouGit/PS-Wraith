#!/usr/bin/env python3
"""Flash using Legacy iOS Kit tools"""
import subprocess
import os

def flash_with_legacy_kit():
    """Flash using copied Legacy iOS Kit tools"""
    
    print("[+] Legacy iOS Kit Flash")
    print("[+] Put device in DFU mode")
    input("Press Enter when ready...")
    
    # Use gaster for checkm8
    print("[+] Running checkm8...")
    result = subprocess.run(["ipwndfu-win32\\gaster.exe", "pwn"])
    if result.returncode != 0:
        print("[!] checkm8 failed")
        return False
    
    print("[+] Device pwned, ready for raw flash")
    print("[+] Use idevicerestore with no-baseband:")
    
    cmd = ["idevice\\idevicerestore.exe", "-e", "-w", "iPad1,1_iOS9_A4_Final.ipsw"]
    print(f"[+] Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    flash_with_legacy_kit()