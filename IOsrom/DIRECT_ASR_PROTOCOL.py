#!/usr/bin/env python3
import socket
import struct
import time
from pathlib import Path

# Boot device to restore ramdisk first
import subprocess
chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

def run(cmd):
    subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast), capture_output=True)

def load(file):
    subprocess.run([str(irecovery), "-f", str(file)], cwd=str(chargfast), capture_output=True)

print("[1/4] Loading iBSS/iBEC...")
load(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)
load(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

print("[2/4] Booting restore ramdisk...")
load(extracted / "038-1437-004.dmg")
run("ramdisk")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")
load(extracted / "kernelcache.release.k48")
run("bootx")

print("[3/4] Waiting 90s for ASR to start...")
time.sleep(90)

print("[4/4] Connecting to ASR via USB...")
# Use idevicerestore restore.c protocol
from ctypes import *
libusbmuxd = CDLL(str(chargfast / "usbmuxd.dll"))
libimobiledevice = CDLL(str(chargfast / "imobiledevice.dll"))

# Connect to restore mode device
device = c_void_p()
client = c_void_p()

print("[+] Opening device connection...")
libimobiledevice.idevice_new(byref(device), None)
libimobiledevice.restored_client_new(device, byref(client), b"idevicerestore")

print("[+] Sending filesystem DMG...")
filesystem = extracted / "038-1421-004.dmg"
with open(filesystem, "rb") as f:
    data = f.read()
    print(f"[+] Sending {len(data)} bytes to ASR...")
    # Send via restored protocol
    libimobiledevice.restored_send(client, data, len(data))

print("[+] DONE!")
