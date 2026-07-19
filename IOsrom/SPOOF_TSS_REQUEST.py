#!/usr/bin/env python3
"""Spoof TSS request to look like current iOS version"""
import subprocess
import plistlib
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

# Get NONCE and ECID
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
nonce = ecid = None
for line in result.stdout.split('\n'):
    if 'NONC:' in line:
        nonce = line.split(':')[1].strip()
    if 'ECID:' in line:
        ecid = line.split(':')[1].strip()

print(f"[+] NONCE: {nonce}")
print(f"[+] ECID: {ecid}")

# Freeze NONCE
print("[1] Freezing NONCE...")
subprocess.run([str(irecovery), "-c", f"setenv boot-nonce {nonce}"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))

# Create spoofed IPSW
print("[2] Creating spoofed IPSW...")
base_ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
spoofed_ipsw = Path("N:/ROMLOADDER/iPad1,1_SPOOFED.ipsw")
work_dir = Path("N:/ROMLOADDER/spoof_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

with zipfile.ZipFile(base_ipsw, 'r') as z:
    z.extractall(work_dir)

# Modify BuildManifest - spoof as iOS 9.3.5 (last signed for iPad1,1)
manifest_path = work_dir / "BuildManifest.plist"
with open(manifest_path, 'rb') as f:
    manifest = plistlib.load(f)

# Spoof version info
manifest['ProductVersion'] = '9.3.5'
manifest['ProductBuildVersion'] = '13G36'
manifest['BuildDate'] = datetime.now().isoformat()

for identity in manifest.get('BuildIdentities', []):
    identity['ApNonce'] = bytes.fromhex(nonce)
    if 'Info' in identity:
        identity['Info']['BuildNumber'] = '13G36'
        identity['Info']['BuildTrain'] = 'Genoa'

with open(manifest_path, 'wb') as f:
    plistlib.dump(manifest, f)

# Modify Restore.plist
restore_path = work_dir / "Restore.plist"
if restore_path.exists():
    with open(restore_path, 'rb') as f:
        restore = plistlib.load(f)
    
    restore['ProductVersion'] = '9.3.5'
    restore['ProductBuildVersion'] = '13G36'
    
    with open(restore_path, 'wb') as f:
        plistlib.dump(restore, f)

# Repack
print("[3] Repacking spoofed IPSW...")
with zipfile.ZipFile(spoofed_ipsw, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            z.write(file, file.relative_to(work_dir))

print(f"\n[+] Spoofed IPSW: {spoofed_ipsw}")
print("[+] Restore with iTunes/3uTools")
print("[!] TSS will see iOS 9.3.5 (signed) but flash iOS 4.3.3 files")
print("[!] NONCE frozen so device won't reboot during restore")
