#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

print("[!] Put device in DFU mode (black screen)")
print("    Hold Power+Home 10s, release Power, keep Home 10s")
input("Press ENTER when ready...")

print("\n[+] Loading iBSS...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast))
time.sleep(4)

print("[+] Loading iBEC...")
subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast))
time.sleep(4)

print("\n[+] Checking if iBEC loaded:")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)

if "iBoot" in result.stdout or result.returncode == 0:
    print("\n[+] Device ready. Loading ramdisk...")
    
    subprocess.run([str(irecovery), "-f", str(extracted / "038-1449-004.dmg")], cwd=str(chargfast))
    subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast))
    
    subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
    subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast))
    
    subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))
    subprocess.run([str(irecovery), "-c", "fsboot"], cwd=str(chargfast))
    
    print("\n[+] Booting ramdisk... wait 60s")
    time.sleep(60)
    
    result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
    print(result.stdout)
