#!/usr/bin/env python3
"""Raw flash using working repos"""
import subprocess
import os

def flash():
    """Execute raw flash sequence"""
    print("[+] Raw Flash - Device must be in DFU mode")
    input("Press Enter when device is in DFU (black screen)...")
    
    commands = [
        ["python", "ipwndfu-win32\\ipwndfu", "-p"],
        ["python", "secureboot_tools\\send_iboot.py", "iPad1,1_iOS9_A4_Final\\iBoot.patched"],
        ["python", "secureboot_tools\\send_kernel.py", "iPad1,1_iOS9_A4_Final\\kernelcache.release.n90ap"],
        ["python", "secureboot_tools\\nand_write.py", "iPad1,1_iOS9_A4_Final\\rootfs9.dmg", "/dev/disk0s1s1"],
        ["python", "secureboot_tools\\reset.py"]
    ]
    
    for cmd in commands:
        print(f"[+] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[!] Command failed")
            return False
    
    print("[✅] Flash complete")
    return True

if __name__ == "__main__":
    flash()