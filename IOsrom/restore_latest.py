#!/usr/bin/env python3
"""Quick restore with latest IPSW"""
import os
import glob
import subprocess
import sys

def main():
    """Restore device with the most recent IPSW"""
    
    # Find all IPSW files
    ipsw_files = glob.glob("*.ipsw")
    
    if not ipsw_files:
        print("[!] No IPSW files found in current directory")
        return False
    
    # Use the target IPSW
    target_ipsw = "iPad1,1_iOS9_A4_Final.ipsw"
    if target_ipsw in ipsw_files:
        latest_ipsw = target_ipsw
    else:
        ipsw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_ipsw = ipsw_files[0]
    
    print(f"[+] Found {len(ipsw_files)} IPSW files")
    print(f"[+] Latest IPSW: {latest_ipsw}")
    
    # Show file info
    file_size = os.path.getsize(latest_ipsw) / (1024*1024*1024)  # GB
    print(f"[+] Size: {file_size:.2f} GB")
    
    # List all available IPSW files
    print("\n[+] Available IPSW files:")
    for i, ipsw in enumerate(ipsw_files):
        size_gb = os.path.getsize(ipsw) / (1024*1024*1024)
        marker = "← LATEST" if i == 0 else ""
        print(f"  {i+1}. {ipsw} ({size_gb:.2f} GB) {marker}")
    
    print(f"\n[+] Using: {latest_ipsw}")
    
    # Confirm before proceeding
    response = input("\nProceed with restore? (y/N): ").strip().lower()
    if response != 'y':
        print("[!] Restore cancelled")
        return False
    
    # Run the idevicerestore flash script
    try:
        result = subprocess.run([sys.executable, "idevicerestore_flash.py", latest_ipsw], 
                              check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"[!] Error running idevicerestore_flash.py: {e}")
        return False

if __name__ == "__main__":
    print("[+] iOS Device Restore - Latest IPSW")
    print("[+] This will restore your device with the most recent IPSW file")
    print()
    
    success = main()
    sys.exit(0 if success else 1)