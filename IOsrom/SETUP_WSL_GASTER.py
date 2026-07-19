#!/usr/bin/env python3
"""Setup WSL and run gaster from Linux"""
import subprocess
import os

print("="*60)
print("WSL GASTER SETUP")
print("="*60)

print("\n[1] Checking if WSL is installed...")
result = subprocess.run(["wsl", "--status"], capture_output=True, text=True)

if result.returncode != 0:
    print("[-] WSL not installed")
    print("\n[!] Install WSL:")
    print("    1. Open PowerShell as Administrator")
    print("    2. Run: wsl --install")
    print("    3. Restart computer")
    print("    4. Run this script again")
    exit(1)

print("[+] WSL installed")

print("\n[2] Installing dependencies in WSL...")
commands = [
    "sudo apt update",
    "sudo apt install -y libusb-1.0-0-dev usbmuxd",
    "sudo apt install -y python3 python3-pip",
]

for cmd in commands:
    print(f"  Running: {cmd}")
    subprocess.run(["wsl", "-e", "bash", "-c", cmd])

print("\n[3] Downloading gaster for Linux...")
subprocess.run(["wsl", "-e", "bash", "-c", 
    "cd /tmp && wget https://github.com/0x7ff/gaster/releases/download/v1.0/gaster-linux.tar.gz && tar -xzf gaster-linux.tar.gz"])

print("\n[4] Testing gaster...")
result = subprocess.run(["wsl", "-e", "/tmp/gaster", "pwn"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if "checkm8" in result.stdout.lower() or result.returncode == 0:
    print("\n[+] gaster working in WSL!")
    print("\n[!] Put device in DFU mode, then run:")
    print("    python GASTER_RESTORE.py")
else:
    print("\n[-] gaster failed")
    print("[!] You may need to configure USB passthrough to WSL")
