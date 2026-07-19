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

# Load ramdisk to specific address
print("[+] Loading ramdisk to 0x09000000...")
load(extracted / "038-1449-004.dmg")
run("ramdisk")

# Set boot-args with ramdisk address
run("setenv boot-args rd=md0 md0=0x09000000 nand-enable-reformat=1 -v")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")

load(extracted / "kernelcache.release.k48")

# Boot kernel
print("[+] Booting kernel...")
run("bootx")

print("[+] Wait 60s...")
time.sleep(60)

result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
if "Recovery" in result.stdout:
    print("[-] Still in Recovery - ramdisk failed to boot")
    print(result.stdout)
else:
    print("[+] Device mode changed!")
    print(result.stdout)
