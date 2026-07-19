#!/usr/bin/env python3
"""Debug WSL environment"""
import subprocess

print("="*60)
print("WSL DEBUG")
print("="*60)

print("\n[1] WSL version:")
subprocess.run(["wsl", "--version"])

print("\n[2] WSL status:")
subprocess.run(["wsl", "--status"])

print("\n[3] Files in /tmp:")
result = subprocess.run(["wsl", "-e", "ls", "-lah", "/tmp"], capture_output=True, text=True)
print(result.stdout)

print("\n[4] Network test:")
result = subprocess.run(["wsl", "-e", "ping", "-c", "2", "google.com"], capture_output=True, text=True)
print(result.stdout)

print("\n[5] Curl test:")
result = subprocess.run(["wsl", "-e", "curl", "-I", "https://checkra.in"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

print("\n[6] Try manual download:")
result = subprocess.run(["wsl", "-e", "bash", "-c", "cd /tmp && curl -v -L -o checkra1n https://assets.checkra.in/downloads/linux/cli/x86_64/dac9968939ea6e6bfbdedeb41d7e2579c4711dc2c5083f91dced66ca397dc51d/checkra1n && ls -lh checkra1n && file checkra1n"], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
