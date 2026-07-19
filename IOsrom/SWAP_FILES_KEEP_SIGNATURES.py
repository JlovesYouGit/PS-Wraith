#!/usr/bin/env python3
"""Use iPadOS 26 signed manifest but swap in iOS 4.3.3 files"""
import zipfile
import shutil
from pathlib import Path

print("[!] You need to download iPadOS 26.0.1 IPSW first")
print("[!] Download from: https://ipsw.me/iPad15,6")
print()

ipados26_path = input("Enter path to iPadOS 26.0.1 IPSW: ").strip('"')
ipados26 = Path(ipados26_path)

if not ipados26.exists():
    print("[-] IPSW not found")
    exit(1)

ios433 = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
output = Path("N:/ROMLOADDER/iPad1,1_FRANKENSTEIN.ipsw")
work_dir = Path("N:/ROMLOADDER/frankenstein_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

print("[1] Extracting iPadOS 26 (signed manifest)...")
with zipfile.ZipFile(ipados26, 'r') as z:
    # Extract only BuildManifest and Restore.plist (signed metadata)
    z.extract('BuildManifest.plist', work_dir)
    z.extract('Restore.plist', work_dir)

print("[2] Extracting iOS 4.3.3 (actual files)...")
with zipfile.ZipFile(ios433, 'r') as z:
    # Extract everything EXCEPT BuildManifest/Restore.plist
    for item in z.namelist():
        if item not in ['BuildManifest.plist', 'Restore.plist']:
            z.extract(item, work_dir)

print("[3] Creating Frankenstein IPSW...")
print("    - Signed manifest from iPadOS 26 (Apple will approve)")
print("    - Actual files from iOS 4.3.3 (device will flash)")

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            z.write(file, file.relative_to(work_dir))

print(f"\n[+] Frankenstein IPSW: {output}")
print("[!] Restore with iTunes - TSS will approve iPadOS 26 signatures")
print("[!] But device gets iOS 4.3.3 files!")
