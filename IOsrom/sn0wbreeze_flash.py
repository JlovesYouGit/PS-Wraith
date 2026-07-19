#!/usr/bin/env python3
"""Flash custom IPSW using sn0wbreeze"""
import os
import sys
import subprocess

def flash_with_sn0wbreeze(ipsw_path):
    """Flash IPSW using sn0wbreeze"""
    sn0wbreeze_dir = "Snowbreeze"
    
    if not os.path.exists(sn0wbreeze_dir):
        print(f"[!] sn0wbreeze directory not found: {sn0wbreeze_dir}")
        return False
    
    # Find sn0wbreeze executable
    sn0wbreeze_exe = None
    for root, dirs, files in os.walk(sn0wbreeze_dir):
        for file in files:
            if 'sn0wbreeze' in file.lower() and file.endswith('.exe'):
                sn0wbreeze_exe = os.path.join(root, file)
                break
        if sn0wbreeze_exe:
            break
    
    if not sn0wbreeze_exe:
        print("[!] sn0wbreeze.exe not found in snowbreze directory")
        return False
    
    print(f"[+] Found sn0wbreeze: {sn0wbreeze_exe}")
    print(f"[+] Target IPSW: {ipsw_path}")
    
    try:
        print("[+] Instructions:")
        print("1. sn0wbreeze will open")
        print("2. Click 'Browse for IPSW' and select your base IPSW")
        print("3. Choose 'Expert Mode' for custom options")
        print("4. Enable 'Install SSH', 'Install Cydia'")
        print("5. Build custom IPSW")
        print("6. Flash the generated IPSW")
        print()
        input("Press Enter to launch sn0wbreeze...")
        
        print("[+] Launching sn0wbreeze...")
        subprocess.Popen([sn0wbreeze_exe], cwd=sn0wbreeze_dir)
        
        print("[✅] sn0wbreeze launched")
        print(f"[+] Use this as base IPSW: {os.path.abspath(ipsw_path)}")
        print("[+] After building, flash the generated custom IPSW")
        return True
        
    except Exception as e:
        print(f"[!] sn0wbreeze launch failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sn0wbreeze_flash.py <base.ipsw>")
        sys.exit(1)
    
    success = flash_with_sn0wbreeze(sys.argv[1])