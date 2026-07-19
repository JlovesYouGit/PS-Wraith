#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

def run(cmd):
    subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast), capture_output=True)

def load(file):
    subprocess.run([str(irecovery), "-f", str(file)], cwd=str(chargfast), capture_output=True)

# Load iBSS/iBEC
load(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

load(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")
run("go")
time.sleep(3)

# Flash all firmware components to NAND
print("[1/8] Flashing LLB...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3")
run("nand write.i 0x09000000 0x0 0x100000")

print("[2/8] Flashing iBoot...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3")
run("nand write.i 0x09000000 0x100000 0x100000")

print("[3/8] Flashing DeviceTree...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("nand write.i 0x09000000 0x200000 0x100000")

print("[4/8] Flashing AppleLogo...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/applelogo.s5l8930x.img3")
run("nand write.i 0x09000000 0x300000 0x100000")

print("[5/8] Flashing RecoveryMode...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/recoverymode-768x1024.s5l8930x.img3")
run("nand write.i 0x09000000 0x400000 0x100000")

print("[6/8] Flashing BatteryCharging...")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/batterycharging0.s5l8930x.img3")
run("nand write.i 0x09000000 0x500000 0x100000")

print("[7/8] Flashing Kernel...")
load(extracted / "kernelcache.release.k48")
run("nand write.i 0x09000000 0x600000 0x1000000")

print("[8/8] Flashing System (500MB - will take 5+ minutes)...")
load(extracted / "038-1421-004.dmg")
run("nand write.i 0x09000000 0x1600000 0x20000000")

print("[+] COMPLETE! Rebooting...")
run("setenv auto-boot true")
run("saveenv")
run("reboot")
