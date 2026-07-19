#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

chargfast = Path("N:/ROMLOADDER/chargfast via usb")
irecovery = chargfast / "irecovery.exe"

print("[+] Waiting 30s for ramdisk boot...")
time.sleep(30)

print("\n[+] Checking device mode:")
result = subprocess.run([str(irecovery), "-q"], capture_output=True, text=True, cwd=str(chargfast))

if result.returncode != 0 or not result.stdout:
    print("[-] Device not responding - might have booted to ramdisk")
    print("[+] Trying to connect via iproxy...")
    
    iproxy = chargfast / "iproxy.exe"
    print("\n[+] Starting iproxy 2222:22...")
    print("    Run in another terminal: ssh root@localhost -p 2222")
    print("    Password: alpine")
    subprocess.run([str(iproxy), "2222", "22"], cwd=str(chargfast))
else:
    print(result.stdout)
    if "Recovery" in result.stdout:
        print("\n[-] Still in Recovery mode - ramdisk did NOT boot")
        print("[!] The ramdisk kernel is NOT executing")
