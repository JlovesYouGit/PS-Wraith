#!/usr/bin/env python3
"""Setup checkm8 tools for raw IPSW flash"""
import os
import subprocess
import sys

def setup_tools():
    """Clone required tools"""
    # Clean up dead folder
    if os.path.exists("ipwndfu-win32"):
        import shutil
        shutil.rmtree("ipwndfu-win32")
    
    repos = [
        ("https://github.com/axi0mX/ipwndfu.git", "ipwndfu-win32"),
        ("https://github.com/dora2-iOS/secureboot_tools.git", "secureboot_tools"),
        ("https://github.com/libimobiledevice-win32/libusbk-release.git", "libusbk-release")
    ]
    
    for repo, folder in repos:
        if not os.path.exists(folder):
            print(f"[+] Cloning {folder}...")
            try:
                subprocess.run(["git", "clone", repo, folder], check=True)
            except subprocess.CalledProcessError:
                print(f"[!] Failed to clone {repo}")
                continue
        else:
            print(f"[+] {folder} exists")
    
    # Install pyusb
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyusb"], check=True)
    except subprocess.CalledProcessError:
        print("[!] Failed to install pyusb")
    
    print("[+] Run libusbk-release\\InstallDriver.exe manually for DFU driver")
    print("[✅] Setup complete")

if __name__ == "__main__":
    setup_tools()