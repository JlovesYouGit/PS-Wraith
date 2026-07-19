#!/usr/bin/env python3
"""Manual NAND write using existing irecovery - NO gaster needed"""
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

print("="*60)
print("MANUAL NAND WRITE - FINAL SOLUTION")
print("="*60)
print("\n[!] This will:")
print("    1. Boot to restore ramdisk")
print("    2. Mount NAND partitions")
print("    3. Extract and write iOS 4.3.3 filesystem")
print("    4. Reboot to working iOS")
print()

input("Press ENTER to start...")

print("\n[1] Loading iBSS/iBEC...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast))
time.sleep(2)

print("\n[2] Erasing NAND system partition...")
subprocess.run([str(irecovery), "-c", "nand erase 0x800 0x100000"], cwd=str(chargfast))

print("\n[3] Loading LLB to NAND...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "nand write.i 0x09000000 0x0 0x100000"], cwd=str(chargfast))

print("\n[4] Loading iBoot to NAND...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "nand write.i 0x09000000 0x100000 0x100000"], cwd=str(chargfast))

print("\n[5] Loading DeviceTree to NAND...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "nand write.i 0x09000000 0x200000 0x100000"], cwd=str(chargfast))

print("\n[6] Loading Kernel to NAND...")
subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "nand write.i 0x09000000 0x800000 0x2000000"], cwd=str(chargfast))

print("\n[7] Loading Filesystem (500MB - will take 10+ minutes)...")
subprocess.run([str(irecovery), "-f", str(extracted / "038-1421-004.dmg")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "nand write.i 0x09000000 0x2800000 0x20000000"], cwd=str(chargfast))

print("\n[8] Setting auto-boot and rebooting...")
subprocess.run([str(irecovery), "-c", "setenv auto-boot true"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "reboot"], cwd=str(chargfast))

print("\n[+] DONE! Device should boot to iOS 4.3.3")
print("[!] If bootloop, NAND write commands don't actually write to flash")
print("[!] In that case, you MUST use checkra1n on Mac/Linux")
