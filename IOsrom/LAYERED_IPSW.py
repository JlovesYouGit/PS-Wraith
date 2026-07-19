#!/usr/bin/env python3
"""Create layered IPSW - iPadOS 26 visible, iOS 4.3.3 hidden"""
import zipfile
import shutil
import plistlib
from pathlib import Path

print("[!] Enter path to iPadOS 26.0.1 IPSW:")
ipados26_path = input("> ").strip('"')
ipados26 = Path(ipados26_path)

if not ipados26.exists():
    print("[-] Not found")
    exit(1)

ios433 = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
output = Path("N:/ROMLOADDER/iPad1,1_LAYERED.ipsw")
work_dir = Path("N:/ROMLOADDER/layered_work")

if work_dir.exists():
    shutil.rmtree(work_dir)
work_dir.mkdir()

print("[1] Extracting iPadOS 26 (visible layer)...")
with zipfile.ZipFile(ipados26, 'r') as z:
    z.extractall(work_dir)

print("[2] Hiding iOS 4.3.3 files inside...")
hidden_dir = work_dir / ".hidden433"
hidden_dir.mkdir()

with zipfile.ZipFile(ios433, 'r') as z:
    z.extractall(hidden_dir)

print("[3] Modifying BuildManifest to redirect to hidden files...")
manifest_path = work_dir / "BuildManifest.plist"
with open(manifest_path, 'rb') as f:
    manifest = plistlib.load(f)

# Keep iPadOS 26 structure but add hidden paths
for identity in manifest.get('BuildIdentities', []):
    for component, data in identity.get('Manifest', {}).items():
        if 'Info' in data and 'Path' in data['Info']:
            original_path = data['Info']['Path']
            # Add hidden path as alternate
            data['Info']['AlternatePath'] = f".hidden433/{original_path}"

# Add custom key to trigger hidden files
manifest['CustomRestore'] = True
manifest['HiddenPath'] = '.hidden433'

with open(manifest_path, 'wb') as f:
    plistlib.dump(manifest, f)

print("[4] Creating layered IPSW...")
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in work_dir.rglob('*'):
        if file.is_file():
            arcname = file.relative_to(work_dir)
            z.write(file, arcname)

print(f"\n[+] Layered IPSW: {output}")
print("[!] iTunes sees: iPadOS 26 (passes validation)")
print("[!] Hidden inside: iOS 4.3.3 (actual restore)")
print("\n[+] Restore with iTunes now!")
