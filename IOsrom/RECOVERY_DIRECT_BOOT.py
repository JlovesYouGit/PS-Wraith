#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

print("[+] Loading ramdisk from Recovery mode...")
subprocess.run([str(irecovery), "-f", str(extracted / "038-1449-004.dmg")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))

print("[+] Booting...")
subprocess.run([str(irecovery), "-c", "fsboot"], cwd=str(chargfast))

print("[+] Wait 60s...")
time.sleep(60)

result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
