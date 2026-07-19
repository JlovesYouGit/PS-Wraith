#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

print("[+] Loading iBSS...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

print("[+] Loading iBEC...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

print("[+] Loading ramdisk...")
subprocess.run([str(irecovery), "-f", str(extracted / "038-1437-004.dmg")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast))

print("[+] Loading devicetree...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast))

print("[+] Loading kernel...")
subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))

print("[+] Booting...")
subprocess.run([str(irecovery), "-c", "bootx"], cwd=str(chargfast))

print("[+] Waiting 60s...")
time.sleep(60)

print("[+] Checking device mode...")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
