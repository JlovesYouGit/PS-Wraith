#!/usr/bin/env python3
"""Simple WSL restore - use Windows usbipd, Linux checkra1n"""
import subprocess
import time

print("="*60)
print("SIMPLE WSL iOS 4.3.3 RESTORE")
print("="*60)

print("\n[STEP 1] Install usbipd-win on Windows")
print("Run in PowerShell as Admin:")
print("  winget install dorssel.usbipd-win")
input("\nPress ENTER after installing...")

print("\n[STEP 2] Installing checkra1n in WSL...")
result = subprocess.run(["wsl", "-e", "bash", "-c", """
cd /tmp
wget -q https://assets.checkra.in/downloads/linux/cli/x86_64/dac9968939ea6e6bfbdedeb41d7e2579c4711dc2c5083f91dced66ca397dc51d/checkra1n 2>/dev/null
chmod +x checkra1n
sudo mv checkra1n /usr/local/bin/ 2>/dev/null
checkra1n --version
"""], capture_output=True, text=True)

print(result.stdout)
if "0.12" not in result.stdout:
    print("[-] checkra1n install failed")
    exit(1)

print("\n[STEP 3] Put iPad in DFU mode")
print("  - Hold Power + Home for 10 seconds")
print("  - Release Power, keep Home for 10 seconds")
print("  - Screen BLACK")
input("\nPress ENTER when in DFU...")

print("\n[STEP 4] Finding iPad USB...")
result = subprocess.run(["powershell", "usbipd", "list"], capture_output=True, text=True)
print(result.stdout)

busid = input("\nEnter BUSID (e.g. 1-4): ").strip()

print(f"\n[STEP 5] Attaching {busid} to WSL...")
subprocess.run(["powershell", "usbipd", "bind", "--busid", busid])
subprocess.run(["powershell", "usbipd", "attach", "--wsl", "--busid", busid])
time.sleep(3)

print("\n[STEP 6] Running checkra1n...")
subprocess.run(["wsl", "-e", "sudo", "checkra1n", "-c", "-V"])

print("\n[STEP 7] Writing filesystem via SSH...")
subprocess.run(["wsl", "-e", "bash", "-c", """
sudo apt install -y sshpass iproxy 2>/dev/null
iproxy 2222 22 &
sleep 5
sshpass -p alpine ssh -o StrictHostKeyChecking=no root@localhost -p 2222 << 'EOF'
cd /tmp
# Filesystem will be copied here
dd if=/tmp/038-1421-004.dmg of=/dev/rdisk0s1 bs=1m
reboot
EOF
"""])

print("\n[!] Copy filesystem manually:")
print("  scp -P 2222 'N:/ROMLOADDER/chargfast via usb/extracted/038-1421-004.dmg' root@localhost:/tmp/")
