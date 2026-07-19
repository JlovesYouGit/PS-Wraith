#!/usr/bin/env python3
"""Use Legacy iOS Kit tools"""
import os
import shutil

def setup_from_legacy_kit():
    """Copy tools from Legacy iOS Kit"""
    legacy_path = "git-hash_2025-09-30-2a7836e\\Legacy-iOS-Kit-latest\\Legacy-iOS-Kit-latest\\bin\\linux\\x86_64"
    
    if not os.path.exists(legacy_path):
        print("[!] Legacy iOS Kit not found")
        return False
    
    # Create directories
    os.makedirs("idevice", exist_ok=True)
    os.makedirs("ipwndfu-win32", exist_ok=True)
    os.makedirs("secureboot_tools", exist_ok=True)
    
    # Copy tools
    tools = {
        "idevicerestore": "idevice\\idevicerestore.exe",
        "irecovery": "ipwndfu-win32\\irecovery.exe", 
        "gaster": "ipwndfu-win32\\gaster.exe",
        "ipwnder": "ipwndfu-win32\\ipwnder.exe"
    }
    
    for src_name, dst_path in tools.items():
        src_path = os.path.join(legacy_path, src_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"[+] Copied {src_name} -> {dst_path}")
        else:
            print(f"[!] {src_name} not found")
    
    print("[✅] Tools copied from Legacy iOS Kit")
    return True

if __name__ == "__main__":
    setup_from_legacy_kit()