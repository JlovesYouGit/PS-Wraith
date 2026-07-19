#!/usr/bin/env python3
"""Complete iOS 4.3.3 restore using checkra1n in WSL"""
import subprocess
import time

print("="*60)
print("WSL iOS 4.3.3 RESTORE")
print("="*60)

print("\n[1] Put iPad in DFU mode:")
print("    - Hold Power + Home for 10 seconds")
print("    - Release Power, keep holding Home for 10 seconds")
print("    - Screen should be BLACK")
input("\nPress ENTER when in DFU mode...")

print("\n[2] Finding iPad USB device...")
result = subprocess.run(["powershell", "-Command", "usbipd list"], capture_output=True, text=True)
print(result.stdout)

busid = input("\nEnter BUSID of Apple device (e.g. 1-4): ").strip()

print(f"\n[3] Attaching USB device {busid} to WSL...")
subprocess.run(["powershell", "-Command", f"usbipd bind --busid {busid}"])
subprocess.run(["powershell", "-Command", f"usbipd attach --wsl --busid {busid}"])

time.sleep(3)

print("\n[4] Verifying device in WSL...")
result = subprocess.run(["wsl", "-e", "lsusb"], capture_output=True, text=True)
print(result.stdout)

if "Apple" not in result.stdout:
    print("\n[-] Device not found in WSL")
    print("[!] Try: usbipd attach --wsl --busid " + busid)
    exit(1)

print("\n[5] Running checkra1n...")
subprocess.run(["wsl", "-e", "sudo", "checkra1n", "-c", "-V"])

print("\n[6] Device should be jailbroken. Installing OpenSSH...")
subprocess.run(["wsl", "-e", "bash", "-c", """
iproxy 2222 22 &
sleep 5
ssh-keygen -R [localhost]:2222
sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no root@localhost -p 2222 'apt-get update && apt-get install -y openssh'
"""])

print("\n[7] Copying iOS 4.3.3 filesystem to device...")
filesystem = "/mnt/n/ROMLOADDER/chargfast via usb/extracted/038-1421-004.dmg"
subprocess.run(["wsl", "-e", "bash", "-c", f"""
sshpass -p 'alpine' scp -P 2222 '{filesystem}' root@localhost:/tmp/
sshpass -p 'alpine' ssh -p 2222 root@localhost 'dd if=/tmp/038-1421-004.dmg of=/dev/rdisk0s1 bs=1m && reboot'
"""])

print("\n[+] DONE! Device should reboot to iOS 4.3.3")
