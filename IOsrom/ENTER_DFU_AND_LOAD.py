#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

print("[!] Put device in DFU mode:")
print("    1. Hold Power + Home for 10 seconds")
print("    2. Release Power, keep holding Home for 10 seconds")
print("    3. Screen should be BLACK (not Apple logo)")
print()
input("Press ENTER when device is in DFU mode...")

print("\n[+] Checking mode...")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

if "DFU" not in result.stdout:
    print("[-] Device not in DFU mode. Try again.")
    exit(1)

print("\n[+] Loading iBSS to DFU mode device...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
time.sleep(3)

print("\n[+] After iBSS:")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

print("\n[+] Loading iBEC...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
time.sleep(3)

print("\n[+] After iBEC:")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

if "iBoot" in result.stdout:
    print("\n[+] SUCCESS - iBEC loaded, device in iBoot mode")
else:
    print("\n[-] FAILED - iBEC did not load")
