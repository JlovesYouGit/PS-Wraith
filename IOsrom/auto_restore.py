#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast_dir / "irecovery.exe"
idevicerestore = chargfast_dir / "idevicerestore.exe"
ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")

print("AUTO RESTORE")

# Load iBSS/iBEC
print("[+] Loading iBSS...")
subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
time.sleep(2)

print("[+] Loading iBEC...")
subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], cwd=str(chargfast_dir))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
time.sleep(2)

# Restore with custom flag
print("[+] Starting restore...")
subprocess.run([
    str(idevicerestore),
    "--custom",
    "--erase", 
    "--no-input",
    "-R",
    str(ipsw)
], cwd=str(chargfast_dir))

print("[+] Done")
