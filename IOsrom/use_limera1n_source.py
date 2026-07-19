#!/usr/bin/env python3
"""Use limera1n exploit from idevicerestore source"""
import os
import sys

def use_limera1n_exploit():
    """Use the limera1n exploit from source"""
    limera1n_source = r"1.0.0 source code\libimobiledevice-idevicerestore-a88351d\src\limera1n.c"
    
    if not os.path.exists(limera1n_source):
        print("[!] limera1n source not found")
        return False
    
    print("[+] Found limera1n exploit source")
    print("[+] This contains the A4 bootrom exploit")
    print()
    print("[!] You need to:")
    print("1. Compile idevicerestore from source")
    print("2. Or use pre-compiled idevicerestore binary")
    print("3. Or try different approach")
    print()
    print("[+] Alternative: Try futurerestore or other tools")
    print("[+] Or use the existing limera1n.exe you have")
    
    # Check if we have the compiled limera1n
    limera1n_exe = r"limera1n\limera1n.exe"
    if os.path.exists(limera1n_exe):
        print(f"[+] Found compiled limera1n: {limera1n_exe}")
        print("[+] Try using that with your perfect IPSW")
        return True
    
    return False

if __name__ == "__main__":
    use_limera1n_exploit()