#!/usr/bin/env python3
"""Push iPad NAND bypass project to GitHub"""
import subprocess
from pathlib import Path

project_dir = Path("N:/ROMLOADDER")

print("[1] Creating .gitignore...")
gitignore = """
# Large firmware files
*.dmg
*.ipsw
*.dfu
*.img3

# Extracted firmware
extracted/
*_work/
*_temp/
manual_restore/
restore_temp/

# Windows executables
*.exe
*.dll

# Python cache
__pycache__/
*.pyc

# Logs
*.log

# USB tools
ipwndfu-win32/
libimobiledevice*/
"""

with open(project_dir / ".gitignore", "w") as f:
    f.write(gitignore)

print("[2] Initializing git...")
subprocess.run(["git", "init"], cwd=str(project_dir))

print("[3] Adding files...")
subprocess.run(["git", "add", "."], cwd=str(project_dir))

print("[4] Committing...")
subprocess.run(["git", "commit", "-m", "iPad1,1 NAND bypass project - IBFL 0x03 achieved"], cwd=str(project_dir))

print("[5] Adding remote...")
subprocess.run(["git", "remote", "add", "origin", "https://github.com/JlovesYouGit/IOsrom.git"], cwd=str(project_dir))

print("[6] Setting branch to main...")
subprocess.run(["git", "branch", "-M", "main"], cwd=str(project_dir))

print("[7] Pushing to GitHub...")
subprocess.run(["git", "push", "-u", "origin", "main"], cwd=str(project_dir))

print("\n[+] Done! Project pushed to GitHub")
print("[+] Repository: https://github.com/JlovesYouGit/IOsrom")
