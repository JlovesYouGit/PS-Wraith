#!/usr/bin/env python3
"""Build Windows idevicerestore from source"""
import os
import subprocess
import shutil

def build_windows():
    """Build idevicerestore for Windows"""
    source_dir = "1.0.0 source code\\libimobiledevice-idevicerestore-a88351d"
    
    # Check for build tools
    if not shutil.which("gcc") and not shutil.which("cl"):
        print("[!] No compiler found. Install:")
        print("1. Visual Studio Build Tools, or")
        print("2. MinGW-w64, or") 
        print("3. MSYS2")
        return False
    
    os.chdir(source_dir)
    
    # Simple Windows build
    sources = [
        "src/idevicerestore.c", "src/common.c", "src/tss.c", 
        "src/restore.c", "src/recovery.c", "src/dfu.c", 
        "src/normal.c", "src/ipsw.c", "src/img3.c", "src/img4.c"
    ]
    
    # Try MinGW first
    if shutil.which("gcc"):
        cmd = ["gcc", "-o", "idevicerestore.exe"] + sources + ["-lws2_32", "-lcrypt32"]
        print(f"[+] Building with MinGW: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
    else:
        # Try MSVC
        cmd = ["cl", "/Fe:idevicerestore.exe"] + sources + ["ws2_32.lib", "crypt32.lib"]
        print(f"[+] Building with MSVC: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists("idevicerestore.exe"):
        # Copy to main directory
        shutil.copy2("idevicerestore.exe", "..\\..\\idevice\\idevicerestore.exe")
        print("[✅] Built Windows idevicerestore.exe")
        return True
    else:
        print(f"[!] Build failed: {result.stderr}")
        return False

if __name__ == "__main__":
    build_windows()