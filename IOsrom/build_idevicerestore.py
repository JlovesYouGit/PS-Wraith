#!/usr/bin/env python3
"""Build idevicerestore from source"""
import os
import subprocess
import shutil

def build_idevicerestore():
    source_dir = "1.0.0 source code\\libimobiledevice-idevicerestore-a88351d"
    
    if not os.path.exists(source_dir):
        print("[!] Source directory not found")
        return False
    
    # Check for MinGW/MSYS2
    gcc_path = shutil.which("gcc")
    if not gcc_path:
        print("[!] GCC not found. Install MinGW-w64 or MSYS2")
        return False
    
    print(f"[+] Found GCC: {gcc_path}")
    
    # Simple build
    os.chdir(source_dir)
    
    try:
        # Compile main source files
        sources = ["src/idevicerestore.c", "src/common.c", "src/tss.c", "src/restore.c", 
                  "src/recovery.c", "src/dfu.c", "src/normal.c", "src/ipsw.c"]
        
        cmd = ["gcc", "-o", "idevicerestore.exe"] + sources + ["-lcurl", "-lssl", "-lcrypto"]
        
        print(f"[+] Building: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists("idevicerestore.exe"):
            # Copy to idevice folder
            os.chdir("..\\..\\")
            if not os.path.exists("idevice"):
                os.makedirs("idevice")
            
            shutil.copy(f"{source_dir}\\idevicerestore.exe", "idevice\\idevicerestore.exe")
            print("[✅] Built and installed idevicerestore.exe")
            return True
        else:
            print(f"[!] Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[!] Build error: {e}")
        return False

if __name__ == "__main__":
    build_idevicerestore()