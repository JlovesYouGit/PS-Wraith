#!/usr/bin/env python3
"""Use existing restore tools as fallback"""
import os
import subprocess
import sys

def use_redsn0w(ipsw_path):
    """Use redsn0w for restore"""
    redsn0w_exe = "redSn0w\\redsn0w-0.7.1.exe"
    if os.path.exists(redsn0w_exe):
        print(f"[+] Using redsn0w: {redsn0w_exe}")
        print("[+] Put device in DFU mode, then run redsn0w manually")
        print(f"[+] IPSW: {ipsw_path}")
        subprocess.run([redsn0w_exe])
        return True
    return False

def use_sn0wbreeze(ipsw_path):
    """Use sn0wbreeze for restore"""
    # Check for sn0wbreeze executable
    sn0w_paths = ["Snowbreeze\\sn0wbreeze-v2.9.14", "sn0wbreeze"]
    for path in sn0w_paths:
        if os.path.exists(path):
            print(f"[+] Found sn0wbreeze at: {path}")
            print("[+] Use sn0wbreeze GUI to create custom firmware")
            print(f"[+] Input IPSW: {ipsw_path}")
            return True
    return False

def direct_restore(ipsw_path):
    """Direct restore without idevicerestore"""
    print(f"[+] Direct restore mode for: {ipsw_path}")
    print("[+] Instructions:")
    print("1. Put device in DFU mode")
    print("2. Use iTunes/3uTools to restore with custom IPSW")
    print("3. Or use redsn0w/sn0wbreeze from your tools")
    
    choice = input("\nSelect tool: (1)redsn0w (2)sn0wbreeze (3)manual: ")
    
    if choice == "1":
        return use_redsn0w(ipsw_path)
    elif choice == "2":
        return use_sn0wbreeze(ipsw_path)
    else:
        print(f"[+] Manual restore with: {ipsw_path}")
        return True

if __name__ == "__main__":
    ipsw = "iPad1,1_iOS9_A4_Final.ipsw"
    if len(sys.argv) > 1:
        ipsw = sys.argv[1]
    
    direct_restore(ipsw)