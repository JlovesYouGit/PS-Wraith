#!/usr/bin/env python3
"""Download checkra1n properly"""
import subprocess

print("[+] Downloading checkra1n in WSL...")

result = subprocess.run(["wsl", "-e", "bash", "-c", """
cd /tmp
echo "Downloading checkra1n..."
curl -L -o checkra1n https://assets.checkra.in/downloads/linux/cli/x86_64/dac9968939ea6e6bfbdedeb41d7e2579c4711dc2c5083f91dced66ca397dc51d/checkra1n
ls -lh checkra1n
chmod +x checkra1n
./checkra1n --version
sudo cp checkra1n /usr/local/bin/
"""], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

if "0.12" in result.stdout or "checkra1n" in result.stdout:
    print("\n[+] checkra1n installed!")
else:
    print("\n[-] Failed. Trying alternative download...")
    result = subprocess.run(["wsl", "-e", "bash", "-c", """
cd /tmp
wget https://checkra.in/assets/downloads/linux/cli/x86_64/checkra1n || curl -O https://checkra.in/assets/downloads/linux/cli/x86_64/checkra1n
chmod +x checkra1n
./checkra1n --version
"""], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
