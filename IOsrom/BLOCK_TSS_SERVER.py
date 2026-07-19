#!/usr/bin/env python3
"""Block TSS server and force local restore"""
import subprocess
from pathlib import Path

hosts_file = Path("C:/Windows/System32/drivers/etc/hosts")

print("[+] Adding TSS server block to hosts file...")
print("[!] Run as Administrator")

block_entries = """
# Block Apple TSS server
127.0.0.1 gs.apple.com
127.0.0.1 albert.apple.com
"""

try:
    with open(hosts_file, "a") as f:
        f.write(block_entries)
    print("[+] TSS servers blocked")
    print("[+] Now run 3uTools restore again")
    print("[+] It should fail TSS but continue with local files")
except PermissionError:
    print("[-] Need Administrator privileges")
    print("[!] Run PowerShell as Admin and execute:")
    print(f'    Add-Content -Path "{hosts_file}" -Value "{block_entries}"')
