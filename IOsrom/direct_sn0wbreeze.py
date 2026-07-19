#!/usr/bin/env python3
"""Direct sn0wbreeze launcher"""
import os
import sys
import subprocess

def launch_sn0wbreeze_direct():
    """Launch sn0wbreeze directly"""
    sn0wbreeze_path = r"N:\ROMLOADDER\Snowbreeze\sn0wbreeze-v2.9.14\sn0wbreezedl-master\sn0wbreeze-v2.9.14.exe"
    
    if not os.path.exists(sn0wbreeze_path):
        print(f"[!] sn0wbreeze not found: {sn0wbreeze_path}")
        return False
    
    try:
        print(f"[+] Launching sn0wbreeze directly...")
        print(f"[+] Path: {sn0wbreeze_path}")
        
        # Launch directly without Python wrapper
        subprocess.Popen([sn0wbreeze_path], shell=True)
        
        print("[✅] sn0wbreeze launched")
        print("[+] Instructions:")
        print("1. Load your iPad1,1_Perfect.ipsw in sn0wbreeze")
        print("2. Choose Expert Mode")
        print("3. Enable SSH, Cydia, SpringBoard mods")
        print("4. Build custom IPSW")
        print("5. Flash to device")
        
        return True
        
    except Exception as e:
        print(f"[!] Launch failed: {e}")
        return False

if __name__ == "__main__":
    launch_sn0wbreeze_direct()