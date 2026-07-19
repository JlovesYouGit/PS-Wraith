#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

def run(cmd):
    subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast))

def load(file):
    subprocess.run([str(irecovery), "-f", str(file)], cwd=str(chargfast))

load(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

load(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

run("setenv boot-args rd=md0 nand-enable-reformat=1 -v")
run("saveenv")

# Use ERASE ramdisk (038-1449-004.dmg) not update ramdisk
load(extracted / "038-1449-004.dmg")
run("ramdisk")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")

load(extracted / "kernelcache.release.k48")
run("bootx")

print("[+] Booting ERASE ramdisk...")
time.sleep(90)

result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
