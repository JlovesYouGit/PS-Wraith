#!/usr/bin/env python3
"""Get idevicerestore executable"""
import os
import urllib.request
import zipfile

def download_idevicerestore():
    """Download pre-built idevicerestore"""
    
    # Create idevice directory
    if not os.path.exists("idevice"):
        os.makedirs("idevice")
    
    # Check existing tools that might have idevicerestore
    tools_paths = [
        "sn0wbreeze\\idevicerestore.exe",
        "redSn0w\\idevicerestore.exe", 
        "ifaith-v1.5.9\\idevicerestore.exe"
    ]
    
    for path in tools_paths:
        if os.path.exists(path):
            import shutil
            shutil.copy(path, "idevice\\idevicerestore.exe")
            print(f"[✅] Copied idevicerestore from {path}")
            return True
    
    print("[!] No pre-built idevicerestore found")
    print("[!] Try: python build_idevicerestore.py")
    return False

if __name__ == "__main__":
    download_idevicerestore()