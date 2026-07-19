#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

# Boot to ramdisk with SSH enabled
subprocess.run([str(irecovery), "-f", str(extracted / "038-1449-004.dmg")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-f", str(extracted / "kernelcache.release.k48")], cwd=str(chargfast))

# Set boot args for verbose and SSH
subprocess.run([str(irecovery), "-c", "setenv boot-args rd=md0 -v"], cwd=str(chargfast))

subprocess.run([str(irecovery), "-c", "bootx"], cwd=str(chargfast))

print("[+] Ramdisk booting...")
print("[+] If it boots, connect via USB and use iproxy:")
print("    iproxy 2222 22")
print("    ssh root@localhost -p 2222")
print("    password: alpine")
print("[+] Then run: dd if=/path/to/038-1421-004.dmg of=/dev/disk0s1 bs=1m")
