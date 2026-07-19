#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

subprocess.run([str(irecovery), "-f", str(extracted / "038-1437-004.dmg")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "fsboot"], cwd=str(chargfast))

print("Wait 60s then check device with: irecovery -q")
