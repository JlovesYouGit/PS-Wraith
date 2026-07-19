#!/usr/bin/env python3
"""Setup idevicerestore for Windows"""
import os
import sys
import urllib.request
import zipfile
import shutil

def download_idevicerestore():
    """Download pre-built idevicerestore for Windows"""
    
    # Create idevice directory if it doesn't exist
    idevice_dir = "idevice"
    if not os.path.exists(idevice_dir):
        os.makedirs(idevice_dir)
        print(f"[+] Created directory: {idevice_dir}")
    
    # Check if idevicerestore already exists
    idevicerestore_exe = os.path.join(idevice_dir, "idevicerestore.exe")
    if os.path.exists(idevicerestore_exe):
        print(f"[+] idevicerestore.exe already exists at: {idevicerestore_exe}")
        return True
    
    print("[+] idevicerestore setup for Windows")
    print("[!] You need to manually obtain idevicerestore.exe")
    print("[!] Options:")
    print("1. Build from source in: 1.0.0 source code\\libimobiledevice-idevicerestore-a88351d")
    print("2. Download pre-built binary from libimobiledevice releases")
    print("3. Use 3uTools or similar that includes idevicerestore")
    print()
    print(f"[+] Place idevicerestore.exe in: {os.path.abspath(idevice_dir)}")
    
    return False

def verify_setup():
    """Verify idevicerestore setup"""
    idevicerestore_exe = os.path.join("idevice", "idevicerestore.exe")
    
    if os.path.exists(idevicerestore_exe):
        print(f"[✅] idevicerestore found: {idevicerestore_exe}")
        
        # Test if it runs
        try:
            import subprocess
            result = subprocess.run([idevicerestore_exe, "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if "idevicerestore" in result.stdout.lower() or "usage" in result.stdout.lower():
                print("[✅] idevicerestore is working correctly")
                return True
            else:
                print("[!] idevicerestore may not be working properly")
                return False
        except Exception as e:
            print(f"[!] Error testing idevicerestore: {e}")
            return False
    else:
        print(f"[!] idevicerestore.exe not found in: {os.path.abspath('idevice')}")
        return False

if __name__ == "__main__":
    print("[+] Setting up idevicerestore...")
    
    if not download_idevicerestore():
        print("\n[!] Manual setup required")
        print("[!] After placing idevicerestore.exe, run this script again to verify")
    
    print("\n[+] Verifying setup...")
    if verify_setup():
        print("\n[✅] Setup complete! You can now use idevicerestore_flash.py")
    else:
        print("\n[!] Setup incomplete. Please ensure idevicerestore.exe is properly installed.")