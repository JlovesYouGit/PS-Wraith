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

print("[+] Waiting 60s for ramdisk boot...")
time.sleep(60)

print("[+] Running idevicerestore...")
proc = subprocess.Popen([str(chargfast / "idevicerestore.exe"), "--erase", "--custom", "N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw"], stdin=subprocess.PIPE, cwd=str(chargfast), text=True)
proc.communicate(input="YES\n")
print("[+] Done!")
