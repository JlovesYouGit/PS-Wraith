#!/usr/bin/env python3
"""Create fake TSS response for frozen NONCE"""
import subprocess
import plistlib
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

# Get NONCE
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))
nonce = ecid = None
for line in result.stdout.split('\n'):
    if 'NONC:' in line:
        nonce = line.split(':')[1].strip()
    if 'ECID:' in line:
        ecid = line.split(':')[1].strip()

print(f"NONCE: {nonce}")
print(f"ECID: {ecid}")

# Freeze NONCE
subprocess.run([str(irecovery), "-c", f"setenv boot-nonce {nonce}"], cwd=str(chargfast))
subprocess.run([str(irecovery), "-c", "saveenv"], cwd=str(chargfast))

# Create fake SHSH blob
shsh_dir = Path("N:/ROMLOADDER/shsh")
shsh_dir.mkdir(exist_ok=True)

shsh_file = shsh_dir / f"{int(ecid, 16)}-iPad1,1-4.3.3.shsh"

fake_shsh = {
    'ApNonce': bytes.fromhex(nonce),
    'ECID': int(ecid, 16),
    'generator': '0x1111111111111111'
}

with open(shsh_file, 'wb') as f:
    plistlib.dump(fake_shsh, f)

print(f"\n[+] Fake SHSH created: {shsh_file}")
print("[+] Now use TinyUmbrella or redsn0w to restore with local SHSH")
print("[!] Or try iTunes - it might use local SHSH if TSS fails")
