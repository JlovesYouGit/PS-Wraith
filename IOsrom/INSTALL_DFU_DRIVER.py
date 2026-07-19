#!/usr/bin/env python3
import subprocess
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
zadig = chargfast / "zadig-2.9.exe"

print("[!] Installing WinUSB driver for DFU mode device")
print()
print("Steps:")
print("1. Put device in DFU mode (black screen)")
print("2. Zadig will open")
print("3. Options -> List All Devices")
print("4. Select 'Apple Mobile Device (DFU Mode)' or 'Apple Recovery (iBoot)'")
print("5. Select WinUSB driver")
print("6. Click 'Replace Driver' or 'Install Driver'")
print()
input("Press ENTER to launch Zadig...")

subprocess.run([str(zadig)])

print("\n[+] Driver installed. Now run: python DFU_LOAD_DIRECT.py")
