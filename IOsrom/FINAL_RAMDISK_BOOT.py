#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
extracted = chargfast / "extracted"
irecovery = chargfast / "irecovery.exe"

def run(cmd, show=True):
    result = subprocess.run([str(irecovery), "-c", cmd], capture_output=True, text=True, cwd=str(chargfast))
    if show:
        print(f"  CMD: {cmd}")
        if result.stdout: print(f"  OUT: {result.stdout.strip()}")
        if result.stderr: print(f"  ERR: {result.stderr.strip()}")
    return result

def load(file, show=True):
    if show: print(f"  Loading: {file.name} ({file.stat().st_size} bytes)")
    result = subprocess.run([str(irecovery), "-f", str(file)], capture_output=True, text=True, cwd=str(chargfast))
    if show and result.stdout: print(f"  OUT: {result.stdout.strip()}")
    return result

print("[1] Load iBSS")
load(extracted / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

print("[2] Load iBEC")
load(extracted / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")
run("go")
time.sleep(2)

print("[3] Load restore ramdisk")
load(extracted / "038-1449-004.dmg")
run("ramdisk")

print("[4] Load devicetree")
load(extracted / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3")
run("devicetree")

print("[5] Load kernel")
load(extracted / "kernelcache.release.k48")

print("[6] Boot with fsboot")
run("fsboot")

print("[7] Waiting 60s for ramdisk boot...")
for i in range(6):
    time.sleep(10)
    result = run("getenv boot-args", show=False)
    if result.returncode != 0:
        print(f"  {(i+1)*10}s: Device no longer responding (booting...)")
        break
    else:
        print(f"  {(i+1)*10}s: Still in iBoot")

time.sleep(30)
print("[8] Check final mode:")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
