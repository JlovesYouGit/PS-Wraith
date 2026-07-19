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

# Load iBSS/iBEC
load(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

load(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

# Set boot args for ramdisk
run("setenv boot-args rd=md0 -v")
run("saveenv")

# Load ramdisk
load(extracted / "038-1437-004.dmg")
run("ramdisk")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")

load(extracted / "kernelcache.release.k48")
run("bootx")

print("[+] Ramdisk booting with correct boot-args...")
print("[+] Wait 90s then check device mode with: irecovery -q")
