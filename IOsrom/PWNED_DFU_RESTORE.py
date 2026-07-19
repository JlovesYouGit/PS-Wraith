#!/usr/bin/env python3
"""Use idevicerestore with pwned DFU mode to bypass TSS"""
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"
idevicerestore = chargfast / "idevicerestore.exe"

print("[1] Put device in DFU mode manually")
print("    Hold Power+Home 10s, release Power, keep Home 10s")
input("Press ENTER when in DFU (black screen)...")

print("\n[2] Pwning DFU with iBSS...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
time.sleep(3)

print("\n[3] Device now in Pwned DFU mode")
print("[4] Running idevicerestore with --pwn flag...")

# Use --pwn to skip exploit, device already pwned
proc = subprocess.Popen([
    str(idevicerestore),
    "--pwn",
    "--erase",
    "N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw"
], stdin=subprocess.PIPE, cwd=str(chargfast), text=True)

proc.communicate(input="YES\n")

print("\n[+] Check result")
