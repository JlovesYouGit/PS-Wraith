#!/usr/bin/env python3
"""Setup checkra1n in WSL with USB passthrough"""
import subprocess
import time

print("="*60)
print("WSL CHECKRA1N SETUP")
print("="*60)

print("\n[1] Installing usbipd-win (USB passthrough for WSL)...")
print("[!] Run in PowerShell as Administrator:")
print("    winget install --interactive --exact dorssel.usbipd-win")
print()
input("Press ENTER after installing usbipd-win...")

print("\n[2] Installing USB tools in WSL...")
wsl_commands = [
    "sudo apt update",
    "sudo apt install -y usbip hwdata usbutils",
    "sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20"
]

for cmd in wsl_commands:
    print(f"  {cmd}")
    subprocess.run(["wsl", "-e", "bash", "-c", cmd])

print("\n[3] Installing checkra1n in WSL...")
checkra1n_setup = """
cd /tmp
wget https://assets.checkra.in/downloads/linux/cli/x86_64/dac9968939ea6e6bfbdedeb41d7e2579c4711dc2c5083f91dced66ca397dc51d/checkra1n
chmod +x checkra1n
sudo mv checkra1n /usr/local/bin/
"""
subprocess.run(["wsl", "-e", "bash", "-c", checkra1n_setup])

print("\n[4] Testing checkra1n...")
result = subprocess.run(["wsl", "-e", "checkra1n", "--version"], capture_output=True, text=True)
print(result.stdout)

if "checkra1n" in result.stdout.lower():
    print("\n[+] checkra1n installed successfully!")
    print("\n[!] Now run: python WSL_RESTORE_IOS433.py")
else:
    print("\n[-] checkra1n installation failed")
