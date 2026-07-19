#!/usr/bin/env python3
"""Raw IPSW flash using checkm8"""
import os
import subprocess
import sys

def flash_raw():
    """Flash IPSW parts directly without Apple"""
    ipsw_dir = "iPad1,1_iOS9_A4_Final"
    
    print("[+] checkm8 Raw Flash - No Apple Permission Required")
    print("[+] Put device in DFU mode (black screen)")
    input("Press Enter when ready...")
    
    steps = [
        ("Pwn DFU (checkm8)", ["python", "ipwndfu-win32\\ipwndfu", "-p"]),
        ("Send patched iBoot", ["python", "secureboot_tools\\send_iboot.py", f"{ipsw_dir}\\iBoot.patched"]),
        ("Send kernel", ["python", "secureboot_tools\\send_kernel.py", f"{ipsw_dir}\\kernelcache.release.n90ap"]),
        ("Write rootfs", ["python", "secureboot_tools\\nand_write.py", f"{ipsw_dir}\\rootfs9.dmg", "/dev/disk0s1s1"]),
        ("Reboot", ["python", "secureboot_tools\\reset.py"])
    ]
    
    for desc, cmd in steps:
        print(f"[+] {desc}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[!] Failed: {result.stderr}")
            return False
        print(f"[✅] {desc} complete")
    
    print("[✅] Raw flash complete - device should boot iOS 9")
    return True

if __name__ == "__main__":
    flash_raw()