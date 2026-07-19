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

# Boot to restore ramdisk
load(extracted / "038-1437-004.dmg")
run("ramdisk")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")

load(extracted / "kernelcache.release.k48")
run("bootx")

print("[+] Booting restore ramdisk with ASR...")
print("[+] Wait 90 seconds, then device will be in Restore mode")
print("[+] ASR will be listening on USB for filesystem image")
time.sleep(90)

# Now send filesystem via ASR protocol
print("[+] Sending filesystem to ASR...")
subprocess.run([
    str(chargfast / "idevicerestore.exe"),
    "--custom",
    "--erase", 
    "N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw"
], stdin=subprocess.PIPE, input=b"YES\n", cwd=str(chargfast))
