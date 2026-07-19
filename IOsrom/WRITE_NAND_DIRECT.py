#!/usr/bin/env python3
"""DIRECT NAND WRITE - Bypass all restore tools, write filesystem directly via iBoot commands"""
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"
filesystem = extracted / "038-1421-004.dmg"

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

# Load filesystem DMG to RAM
print(f"[+] Loading {filesystem.stat().st_size} byte filesystem to RAM...")
load(filesystem)

# Write RAM to NAND at system partition offset
print("[+] Writing to NAND flash...")
run("nand erase 0x800 0x40000")  # Erase system partition
run("nand write 0x09000000 0x800 0x40000")  # Write from RAM to NAND

# Load and write boot components
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3")
run("nand write 0x09000000 0x0 0x1")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3")
run("nand write 0x09000000 0x100 0x1")

load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("nand write 0x09000000 0x200 0x1")

load(extracted / "kernelcache.release.k48")
run("nand write 0x09000000 0x300 0x1")

print("[+] NAND write complete. Rebooting...")
run("reboot")
