#!/usr/bin/env python3
"""Flash custom IPSW using idevicerestore"""
import os
import sys
import subprocess
import glob

def get_latest_ipsw():
    """Find the target IPSW file"""
    target_ipsw = "iPad1,1_iOS9_A4_Final.ipsw"
    if os.path.exists(target_ipsw):
        return target_ipsw
    return None

def flash_with_idevicerestore(ipsw_path=None):
    """Flash IPSW using idevicerestore"""
    if not ipsw_path:
        ipsw_path = get_latest_ipsw()
        if not ipsw_path:
            print("[!] No IPSW files found")
            return False
        print(f"[+] Using latest IPSW: {ipsw_path}")
    
    if not os.path.exists(ipsw_path):
        print(f"[!] IPSW file not found: {ipsw_path}")
        return False
    
    # Check for pre-built idevicerestore
    idevicerestore_exe = None
    possible_paths = [
        "idevice\\idevicerestore.exe",
        "idevicerestore.exe",
        "tools\\idevicerestore.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            idevicerestore_exe = path
            break
    
    if not idevicerestore_exe:
        print("[!] idevicerestore.exe not found. Using fallback tools...")
        return subprocess.run([sys.executable, "use_existing_tools.py", ipsw_path]).returncode == 0
    
    print(f"[+] Found idevicerestore: {idevicerestore_exe}")
    print(f"[+] Target IPSW: {ipsw_path}")
    
    try:
        print("[+] Instructions:")
        print("1. Put device in DFU mode (black screen)")
        print("2. Connect device via USB")
        print("3. idevicerestore will flash the IPSW")
        print()
        input("Press Enter when device is in DFU mode...")
        
        print("[+] Running idevicerestore...")
        # Convert to absolute path
        abs_ipsw_path = os.path.abspath(ipsw_path)
        abs_exe_path = os.path.abspath(idevicerestore_exe)
        
        # Run idevicerestore with options
        cmd = [abs_exe_path, "-e", "-u", abs_ipsw_path]  # -e = erase, -u = update
        
        print(f"[+] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        print(f"[+] Return code: {result.returncode}")
        if result.stdout:
            print(f"[+] Output: {result.stdout}")
        if result.stderr:
            print(f"[!] Errors: {result.stderr}")
        
        if result.returncode == 0:
            print("[✅] idevicerestore completed successfully")
            print("[+] Device should now boot with the restored firmware")
            return True
        else:
            print(f"[!] idevicerestore failed with return code: {result.returncode}")
            return False
        
    except subprocess.TimeoutExpired:
        print("[!] idevicerestore timed out after 30 minutes")
        return False
    except Exception as e:
        print(f"[!] idevicerestore execution failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python idevicerestore_flash.py [ipsw_file]")
        print("If no IPSW file specified, will use the most recent one found")
        sys.exit(1)
    
    ipsw_file = sys.argv[1] if len(sys.argv) == 2 else None
    
    print("[+] idevicerestore IPSW Flash Tool")
    print("[+] This will restore your device with the specified IPSW")
    print()
    
    success = flash_with_idevicerestore(ipsw_file)
    sys.exit(0 if success else 1)