#!/usr/bin/env python3
"""Replace iPadOS 26 kernel with iOS 4.3.3 kernel - device boots iOS 4.3.3"""
import zipfile
import shutil
from pathlib import Path

print("="*60)
print("FRANKENSTEIN IPSW - iPadOS 26 body, iOS 4.3.3 brain")
print("="*60)

ipados26_path = input("\nPath to iPadOS 26.0.1 IPSW: ").strip('"')
ipados26 = Path(ipados26_path)

if not ipados26.exists():
    print("[-] Not found")
    exit(1)

ios433 = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
output = Path("N:/ROMLOADDER/iPad1,1_FRANKENSTEIN_BOOTABLE.ipsw")
work_dir = Path("N:/ROMLOADDER/frankenstein_bootable")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

print("\n[1] Extracting iPadOS 26 (signed by Apple)...")
with zipfile.ZipFile(ipados26, 'r') as z:
    z.extractall(work_dir)

print("[2] Extracting iOS 4.3.3 bootable components...")
ios_temp = work_dir / "ios433_temp"
ios_temp.mkdir()
with zipfile.ZipFile(ios433, 'r') as z:
    z.extractall(ios_temp)

print("[3] Swapping critical boot components...")
# Replace iPadOS 26 boot files with iOS 4.3.3 (A4 compatible)
swaps = [
    ('Firmware/dfu/iBSS.*', 'Firmware/dfu/iBSS.k48ap.RELEASE.dfu'),
    ('Firmware/dfu/iBEC.*', 'Firmware/dfu/iBEC.k48ap.RELEASE.dfu'),
    ('kernelcache.*', 'kernelcache.release.k48'),
]

for ipados_pattern, ios433_file in swaps:
    # Find iPadOS file
    ipados_files = list(work_dir.glob(ipados_pattern))
    ios_source = ios_temp / ios433_file
    
    if ios_source.exists() and ipados_files:
        for ipados_file in ipados_files:
            print(f"  Replacing {ipados_file.name} with {ios433_file}")
            shutil.copy(ios_source, ipados_file)

print("[4] Repacking Frankenstein IPSW...")
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file() and 'ios433_temp' not in str(file):
            z.write(file, file.relative_to(work_dir))

print(f"\n[+] Frankenstein IPSW: {output}")
print("\n[!] What will happen:")
print("    1. iTunes validates iPadOS 26 (passes)")
print("    2. TSS signs iPadOS 26 (approved)")
print("    3. iTunes flashes to device")
print("    4. Device tries to boot iPadOS 26")
print("    5. iBSS/iBEC are iOS 4.3.3 (A4 compatible)")
print("    6. Kernel is iOS 4.3.3 (A4 compatible)")
print("    7. Device MIGHT actually boot!")
print("\n[+] Try restore with iTunes!")
