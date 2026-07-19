#!/usr/bin/env python3
"""Flash custom IPSW using redsn0w"""
import os
import sys
import subprocess

def flash_with_redsn0w(ipsw_path):
    """Flash IPSW using redsn0w"""
    redsn0w_dir = "redsn0w"
    
    if not os.path.exists(redsn0w_dir):
        print(f"[!] redsn0w directory not found: {redsn0w_dir}")
        return False
    
    # Find redsn0w executable
    redsn0w_exe = None
    for file in os.listdir(redsn0w_dir):
        if 'redsn0w' in file.lower() and file.endswith('.exe'):
            redsn0w_exe = os.path.join(redsn0w_dir, file)
            break
    
    if not redsn0w_exe:
        print("[!] redsn0w.exe not found in redsn0w directory")
        return False
    
    print(f"[+] Found redsn0w: {redsn0w_exe}")
    print(f"[+] Target IPSW: {ipsw_path}")
    
    try:
        print("[+] Instructions:")
        print("1. Put device in DFU mode (black screen)")
        print("2. redsn0w will open - click 'Browse' and select your IPSW")
        print("3. Click 'Next' and follow redsn0w instructions")
        print("4. redsn0w will exploit and flash the custom firmware")
        print()
        input("Press Enter when device is in DFU mode...")
        
        print("[+] Launching redsn0w...")
        # Launch redsn0w GUI
        subprocess.Popen([redsn0w_exe], cwd=redsn0w_dir)
        
        print("[✅] redsn0w launched")
        print(f"[+] Load this IPSW in redsn0w: {os.path.abspath(ipsw_path)}")
        return True
        
    except Exception as e:
        print(f"[!] redsn0w launch failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python redsn0w_flash.py <custom.ipsw>")
        sys.exit(1)
    
    success = flash_with_redsn0w(sys.argv[1])
    sys.exit(0 if success else 1)