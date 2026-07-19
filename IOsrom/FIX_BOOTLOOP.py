#!/usr/bin/env python3
"""Fix bootloop by resetting to Recovery mode"""
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

print("[+] Waiting for device in bootloop...")
time.sleep(5)

print("[+] Attempting to enter Recovery mode...")
result = subprocess.run([str(irecovery), "-c", "reset"], cwd=str(chargfast))

time.sleep(5)

result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

if "Recovery" in result.stdout:
    print("[+] Device back in Recovery mode")
else:
    print("[-] Device not responding. Hold Power+Home for 10s to force restart")
