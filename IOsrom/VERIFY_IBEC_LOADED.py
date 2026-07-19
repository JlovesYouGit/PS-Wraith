#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

def query():
    result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
    return result.stdout

print("[+] Initial state:")
print(query())

print("\n[+] Loading iBSS...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(3)

print("\n[+] After iBSS:")
print(query())

print("\n[+] Loading iBEC...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(3)

print("\n[+] After iBEC:")
state = query()
print(state)

if "iBoot" in state:
    print("\n[+] iBEC loaded successfully - device ready for file uploads")
    
    print("\n[+] Testing getenv command:")
    result = subprocess.run([str(irecovery), "-c", "getenv"], capture_output=True, text=True, cwd=str(chargfast))
    print(result.stdout[:500])
else:
    print("\n[-] iBEC not loaded properly")
