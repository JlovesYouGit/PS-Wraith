#!/usr/bin/env python3
"""Simple MSYS2 build"""
import subprocess
import os

def simple_build():
    """Simple build using MSYS2 gcc"""
    source_dir = "1.0.0 source code\\libimobiledevice-idevicerestore-a88351d\\src"
    
    # Find MSYS2 gcc
    gcc_paths = [
        "C:\\msys64\\mingw64\\bin\\gcc.exe",
        "C:\\msys2\\mingw64\\bin\\gcc.exe"
    ]
    
    gcc = None
    for path in gcc_paths:
        if os.path.exists(path):
            gcc = path
            break
    
    if not gcc:
        print("[!] MSYS2 GCC not found")
        return False
    
    os.makedirs("idevice", exist_ok=True)
    
    # Simple compile
    cmd = [
        gcc, "-o", "idevice\\idevicerestore.exe",
        f"{source_dir}\\idevicerestore.c",
        f"{source_dir}\\common.c", 
        f"{source_dir}\\restore.c",
        "-lws2_32"
    ]
    
    print(f"[+] Building: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[✅] Built idevicerestore.exe")
        return True
    else:
        print(f"[!] Build failed: {result.stderr}")
        return False

if __name__ == "__main__":
    simple_build()