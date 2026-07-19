#!/usr/bin/env python3
"""Build idevicerestore using MSYS2"""
import os
import subprocess

def build_with_msys2():
    """Build using MSYS2"""
    source_dir = "1.0.0 source code\\libimobiledevice-idevicerestore-a88351d"
    
    # MSYS2 build commands
    build_script = f"""
cd "{os.path.abspath(source_dir)}"
pacman -S --noconfirm mingw-w64-x86_64-gcc mingw-w64-x86_64-pkg-config mingw-w64-x86_64-libimobiledevice
gcc -o idevicerestore.exe src/*.c -limobiledevice -lplist -lcurl -lssl -lcrypto -lws2_32
cp idevicerestore.exe ../../idevice/
"""
    
    # Write build script
    with open("build_msys2.sh", "w") as f:
        f.write(build_script)
    
    # Run in MSYS2
    msys2_paths = [
        "C:\\msys64\\usr\\bin\\bash.exe",
        "C:\\msys2\\usr\\bin\\bash.exe", 
        "msys2.exe"
    ]
    
    msys2_bash = None
    for path in msys2_paths:
        if os.path.exists(path):
            msys2_bash = path
            break
    
    if not msys2_bash:
        print("[!] MSYS2 bash not found")
        return False
    
    print(f"[+] Building with MSYS2: {msys2_bash}")
    result = subprocess.run([msys2_bash, "build_msys2.sh"])
    
    return result.returncode == 0

if __name__ == "__main__":
    build_with_msys2()