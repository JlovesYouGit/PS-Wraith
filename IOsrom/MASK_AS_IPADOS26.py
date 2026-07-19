#!/usr/bin/env python3
"""Mask iOS 4.3.3 as iPadOS 26.0.1 (currently signed)"""
import subprocess
import plistlib
import zipfile
import shutil
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

# Get and freeze NONCE
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
nonce = None
for line in result.stdout.split('\n'):
    if 'NONC:' in line:
        nonce = line.split(':')[1].strip()
        break

print(f"[+] NONCE: {nonce}")
subprocess.run([str(irecovery), "-c", f"setenv boot-nonce {nonce}"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))

print("[1] Extracting iOS 4.3.3...")
base_ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
masked_ipsw = Path("N:/ROMLOADDER/iPad1,1_MASKED_iPadOS26.ipsw")
work_dir = Path("N:/ROMLOADDER/mask_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

with zipfile.ZipFile(base_ipsw, 'r') as z:
    z.extractall(work_dir)

print("[2] Masking as iPadOS 26.0.1...")
manifest_path = work_dir / "BuildManifest.plist"
with open(manifest_path, 'rb') as f:
    manifest = plistlib.load(f)

# Mask as iPadOS 26.0.1 (23A355)
manifest['ProductVersion'] = '26.0.1'
manifest['ProductBuildVersion'] = '23A355'
manifest['SupportedProductTypes'] = ['iPad15,6']

for identity in manifest.get('BuildIdentities', []):
    identity['ApNonce'] = bytes.fromhex(nonce)
    identity['ApChipID'] = '0x8030'  # M3 chip
    identity['ApBoardID'] = '0x3C'   # iPad Air 13-inch
    
    if 'Info' in identity:
        identity['Info']['BuildNumber'] = '23A355'
        identity['Info']['BuildTrain'] = 'SydneyE'
        identity['Info']['DeviceClass'] = 'iPad15,6'

with open(manifest_path, 'wb') as f:
    plistlib.dump(manifest, f)

# Update Restore.plist
restore_path = work_dir / "Restore.plist"
if restore_path.exists():
    with open(restore_path, 'rb') as f:
        restore = plistlib.load(f)
    
    restore['ProductVersion'] = '26.0.1'
    restore['ProductBuildVersion'] = '23A355'
    restore['ProductType'] = 'iPad15,6'
    
    with open(restore_path, 'wb') as f:
        plistlib.dump(restore, f)

print("[3] Repacking...")
with zipfile.ZipFile(masked_ipsw, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            z.write(file, file.relative_to(work_dir))

print(f"\n[+] Masked IPSW: {masked_ipsw}")
print("[!] iTunes will see: iPadOS 26.0.1 (iPad Air 13-inch M3)")
print("[!] TSS will approve (currently signed)")
print("[!] Device will get: iOS 4.3.3 files")
print("\n[+] Restore with iTunes now!")
