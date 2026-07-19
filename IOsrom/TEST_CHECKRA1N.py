#!/usr/bin/env python3
"""Test if checkra1n works"""
import subprocess

print("[+] Testing checkra1n...")

result = subprocess.run(["wsl", "-e", "bash", "-c", """
cd /tmp
chmod +x checkra1n
./checkra1n --version
echo "---"
./checkra1n --help
"""], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

if result.returncode == 0 or "checkra1n" in result.stdout.lower():
    print("\n[+] checkra1n works!")
    print("\n[!] Now put iPad in DFU mode and run:")
    print("    python RUN_CHECKRA1N.py")
else:
    print("\n[-] checkra1n failed to run")
