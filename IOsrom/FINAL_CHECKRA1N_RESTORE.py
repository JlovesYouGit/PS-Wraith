#!/usr/bin/env python3
"""FINAL iOS 4.3.3 restore using checkra1n in WSL"""
import subprocess
import time

print("="*60)
print("FINAL iOS 4.3.3 RESTORE")
print("="*60)

print("\n[STEP 1] Install usbipd-win")
print("Run in PowerShell as Admin:")
print("  winget install dorssel.usbipd-win")
input("\nPress ENTER after installing (or if already installed)...")

print("\n[STEP 2] Put iPad in DFU mode")
print("  1. Hold Power + Home for 10 seconds")
print("  2. Release Power, keep holding Home for 10 seconds")
print("  3. Screen should be BLACK (no Apple logo)")
input("\nPress ENTER when in DFU mode...")

print("\n[STEP 3] Finding iPad USB device...")
result = subprocess.run(["powershell", "usbipd", "list"], capture_output=True, text=True)
print(result.stdout)

busid = input("\nEnter BUSID of Apple device (e.g. 1-4): ").strip()

print(f"\n[STEP 4] Attaching USB {busid} to WSL...")
subprocess.run(["powershell", "usbipd", "bind", "--busid", busid])
subprocess.run(["powershell", "usbipd", "attach", "--wsl", "--busid", busid])
time.sleep(3)

print("\n[STEP 5] Verifying device in WSL...")
result = subprocess.run(["wsl", "-e", "lsusb"], capture_output=True, text=True)
print(result.stdout)

if "Apple" not in result.stdout:
    print("\n[-] Device not found in WSL!")
    exit(1)

print("\n[STEP 6] Running checkra1n...")
print("[!] This will jailbreak the device")
subprocess.run(["wsl", "-e", "sudo", "/tmp/checkra1n", "-c", "-V"])

print("\n[STEP 7] Device jailbroken! Installing SSH...")
subprocess.run(["wsl", "-e", "bash", "-c", """
sudo apt install -y inetutils-tools sshpass 2>/dev/null
iproxy 2222 22 &
sleep 10
ssh-keygen -R [localhost]:2222 2>/dev/null
sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no root@localhost -p 2222 'echo Connected'
"""])

print("\n[STEP 8] Copying filesystem to device...")
print("[!] This will take 5-10 minutes for 500MB file")
subprocess.run(["wsl", "-e", "bash", "-c", """
sshpass -p 'alpine' scp -P 2222 '/mnt/n/ROMLOADDER/chargfast via usb/extracted/038-1421-004.dmg' root@localhost:/tmp/
"""])

print("\n[STEP 9] Writing to NAND...")
subprocess.run(["wsl", "-e", "bash", "-c", """
sshpass -p 'alpine' ssh -p 2222 root@localhost << 'EOF'
dd if=/tmp/038-1421-004.dmg of=/dev/rdisk0s1 bs=1m
sync
reboot
EOF
"""])

print("\n[+] DONE! Device should reboot to iOS 4.3.3")
