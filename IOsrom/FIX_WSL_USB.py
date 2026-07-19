#!/usr/bin/env python3
"""Fix WSL USB setup"""
import subprocess

print("[+] Installing correct USB packages in WSL...")

commands = [
    "sudo apt update",
    "sudo apt install -y linux-tools-generic hwdata usbutils",
    "sudo apt install -y linux-tools-5.15.0-*-generic || true",
]

for cmd in commands:
    print(f"\n  Running: {cmd}")
    subprocess.run(["wsl", "-e", "bash", "-c", cmd])

print("\n[+] Installing checkra1n...")
checkra1n_install = """
cd /tmp
wget -q https://assets.checkra.in/downloads/linux/cli/x86_64/dac9968939ea6e6bfbdedeb41d7e2579c4711dc2c5083f91dced66ca397dc51d/checkra1n
chmod +x checkra1n
sudo mv checkra1n /usr/local/bin/
checkra1n --version
"""
result = subprocess.run(["wsl", "-e", "bash", "-c", checkra1n_install], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if "checkra1n" in result.stdout or "0.12" in result.stdout:
    print("\n[+] Setup complete!")
    print("[+] Now run: python WSL_RESTORE_IOS433.py")
else:
    print("\n[-] checkra1n installation failed")
