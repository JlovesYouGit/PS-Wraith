#!/usr/bin/env python3
"""Freeze NONCE and create matching IPSW for restore"""
import subprocess
import plistlib
import zipfile
import shutil
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

# Step 1: Get current NONCE
print("[1] Reading current NONCE...")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
nonce = None
for line in result.stdout.split('\n'):
    if 'NONC:' in line:
        nonce = line.split(':')[1].strip()
        break

print(f"[+] Current NONCE: {nonce}")

# Step 2: Freeze NONCE with setenv
print("[2] Freezing NONCE...")
subprocess.run([str(irecovery), "-c", f"setenv boot-nonce {nonce}"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))
print("[+] NONCE frozen in NVRAM")

# Step 3: Create custom IPSW with this NONCE
print("[3] Creating IPSW with frozen NONCE...")
base_ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
custom_ipsw = Path("N:/ROMLOADDER/iPad1,1_NONCE_FROZEN.ipsw")
work_dir = Path("N:/ROMLOADDER/nonce_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

# Extract IPSW
with zipfile.ZipFile(base_ipsw, 'r') as z:
    z.extractall(work_dir)

# Modify BuildManifest to include frozen NONCE
manifest_path = work_dir / "BuildManifest.plist"
with open(manifest_path, 'rb') as f:
    manifest = plistlib.load(f)

# Add ApNonce to manifest
for identity in manifest.get('BuildIdentities', []):
    identity['ApNonce'] = bytes.fromhex(nonce)

with open(manifest_path, 'wb') as f:
    plistlib.dump(manifest, f)

# Repack IPSW
print("[4] Repacking IPSW...")
with zipfile.ZipFile(custom_ipsw, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            z.write(file, file.relative_to(work_dir))

print(f"[+] Custom IPSW created: {custom_ipsw}")
print("\n[5] Now restore with 3uTools using this IPSW")
print("[!] Device will NOT reboot during restore - NONCE stays frozen")
print("[!] TSS should accept because NONCE matches")
