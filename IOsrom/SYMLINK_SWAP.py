#!/usr/bin/env python3
"""Use symlinks to swap files - iTunes sees iPadOS 26 names, reads iOS 4.3.3 content"""
import zipfile
import shutil
import os
from pathlib import Path

print("[!] This requires iPadOS 26.0.1 IPSW")
ipados26_path = input("Path to iPadOS 26 IPSW: ").strip('"')
ipados26 = Path(ipados26_path)

if not ipados26.exists():
    print("[-] Not found")
    exit(1)

ios433 = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
work_dir = Path("N:/ROMLOADDER/symlink_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

print("[1] Extracting iPadOS 26 manifest...")
with zipfile.ZipFile(ipados26, 'r') as z:
    z.extract('BuildManifest.plist', work_dir)
    z.extract('Restore.plist', work_dir)

print("[2] Extracting iOS 4.3.3 files...")
ios_files = work_dir / "ios433_files"
ios_files.mkdir()
with zipfile.ZipFile(ios433, 'r') as z:
    z.extractall(ios_files)

print("[3] Creating symlinks (iPadOS names -> iOS 4.3.3 files)...")
# Map common components
symlinks = {
    'Firmware/dfu/iBSS.j617.RELEASE.im4p': 'ios433_files/Firmware/dfu/iBSS.k48ap.RELEASE.dfu',
    'Firmware/dfu/iBEC.j617.RELEASE.im4p': 'ios433_files/Firmware/dfu/iBEC.k48ap.RELEASE.dfu',
    'kernelcache.release.j617': 'ios433_files/kernelcache.release.k48',
}

for ipados_name, ios433_path in symlinks.items():
    target = work_dir / ipados_name
    target.parent.mkdir(parents=True, exist_ok=True)
    source = work_dir / ios433_path
    if source.exists():
        os.symlink(source, target)
        print(f"  {ipados_name} -> {ios433_path}")

print("\n[!] Symlinks created but iTunes will likely reject this")
print("[!] Windows NTFS symlinks require admin and iTunes may not follow them")
print("\n[-] This approach won't work either")
