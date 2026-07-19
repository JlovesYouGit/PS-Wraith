#!/usr/bin/env python3
"""Find MSYS2 installation"""
import os
import glob

def find_msys2():
    """Find MSYS2 paths"""
    search_paths = [
        "C:\\msys64\\**\\gcc.exe",
        "C:\\msys2\\**\\gcc.exe", 
        "C:\\**\\msys64\\**\\gcc.exe",
        "D:\\msys64\\**\\gcc.exe"
    ]
    
    for pattern in search_paths:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            print(f"[+] Found GCC: {match}")
    
    # Also check PATH
    import shutil
    gcc = shutil.which("gcc")
    if gcc:
        print(f"[+] GCC in PATH: {gcc}")
    
    # Check common MSYS2 locations
    msys_dirs = ["C:\\msys64", "C:\\msys2"]
    for dir in msys_dirs:
        if os.path.exists(dir):
            print(f"[+] MSYS2 found: {dir}")

if __name__ == "__main__":
    find_msys2()