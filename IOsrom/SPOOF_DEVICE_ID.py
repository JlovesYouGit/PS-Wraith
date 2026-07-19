#!/usr/bin/env python3
"""Spoof device hardware ID to match iPadOS 26 expectations"""
import subprocess
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

print("[+] Spoofing device hardware to iPad15,6 (M3)...")

# Spoof hardware identifiers in NVRAM
commands = [
    "setenv product-type iPad15,6",
    "setenv board-id 0x3C",
    "setenv chip-id 0x8030",
    "setenv hardware-model J617AP",
    "saveenv"
]

for cmd in commands:
    print(f"  {cmd}")
    subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast))

print("\n[+] Device now identifies as iPad Air 13-inch M3")
print("[+] Verify:")
result = subprocess.run([str(irecovery), "-c", "getenv product-type"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

print("\n[!] Now restore with iTunes using iPad1,1_MASKED_iPadOS26.ipsw")
