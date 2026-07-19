#!/usr/bin/env python3
"""Create hybrid IPSW - iOS 9 manifest with iOS 4.3.3 files, recalculated hashes"""
import subprocess
import plistlib
import zipfile
import shutil
import hashlib
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

# Get NONCE
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
nonce = None
for line in result.stdout.split('\n'):
    if 'NONC:' in line:
        nonce = line.split(':')[1].strip()
        break

print(f"[+] NONCE: {nonce}")

# Freeze NONCE
subprocess.run([str(irecovery), "-c", f"setenv boot-nonce {nonce}"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))

print("[1] Extracting iOS 4.3.3...")
base_ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
hybrid_ipsw = Path("N:/ROMLOADDER/iPad1,1_HYBRID.ipsw")
work_dir = Path("N:/ROMLOADDER/hybrid_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

with zipfile.ZipFile(base_ipsw, 'r') as z:
    z.extractall(work_dir)

print("[2] Recalculating file hashes...")
manifest_path = work_dir / "BuildManifest.plist"
with open(manifest_path, 'rb') as f:
    manifest = plistlib.load(f)

# Update hashes for actual files
for identity in manifest.get('BuildIdentities', []):
    identity['ApNonce'] = bytes.fromhex(nonce)
    
    for component, data in identity.get('Manifest', {}).items():
        if 'Info' in data and 'Path' in data['Info']:
            file_path = work_dir / data['Info']['Path']
            if file_path.exists():
                # Recalculate SHA1
                sha1 = hashlib.sha1()
                with open(file_path, 'rb') as f:
                    sha1.update(f.read())
                
                # Update digest in manifest
                data['Digest'] = sha1.digest()
                print(f"  {component}: {sha1.hexdigest()}")

# Keep version as 4.3.3 but mark as "custom"
manifest['ProductVersion'] = '4.3.3'
manifest['ProductBuildVersion'] = '8J3-CUSTOM'

with open(manifest_path, 'wb') as f:
    plistlib.dump(manifest, f)

print("[3] Repacking...")
with zipfile.ZipFile(hybrid_ipsw, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            z.write(file, file.relative_to(work_dir))

print(f"\n[+] Hybrid IPSW: {hybrid_ipsw}")
print("[!] This has correct hashes for iOS 4.3.3 files")
print("[!] Try restore with iTunes - should pass file validation")
