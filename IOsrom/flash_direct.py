#!/usr/bin/env python3
"""Direct flash using Windows-compatible tools"""
import subprocess
import os

def flash_direct():
    """Flash using Windows binaries from Legacy Kit"""
    
    # Use Windows-compatible idevicerestore directly
    idevicerestore_path = "git-hash_2025-09-30-2a7836e\\Legacy-iOS-Kit-latest\\Legacy-iOS-Kit-latest\\bin\\linux\\x86_64\\idevicerestore"
    
    if not os.path.exists(idevicerestore_path):
        print("[!] idevicerestore not found in Legacy iOS Kit")
        return False
    
    print("[+] Direct IPSW Flash")
    print("[+] Put device in DFU mode (black screen)")
    input("Press Enter when ready...")
    
    # Copy to local path for easier execution
    if not os.path.exists("idevice"):
        os.makedirs("idevice")
    
    import shutil
    local_idevicerestore = "idevice\\idevicerestore.exe"
    shutil.copy2(idevicerestore_path, local_idevicerestore)
    
    # Run idevicerestore with no signature checks
    cmd = [local_idevicerestore, "-e", "-w", "iPad1,1_iOS9_A4_Final.ipsw"]
    print(f"[+] Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"[+] Return code: {result.returncode}")
    if result.stdout:
        print(f"[+] Output: {result.stdout}")
    if result.stderr:
        print(f"[!] Errors: {result.stderr}")
    
    return result.returncode == 0

if __name__ == "__main__":
    flash_direct()