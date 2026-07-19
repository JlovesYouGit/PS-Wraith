#!/usr/bin/env python3
"""Check if kernelcache is encrypted"""
import zipfile
import sys

def check_encryption(ipsw_path):
    """Check kernelcache encryption status"""
    try:
        with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
            kernels = [f for f in zip_ref.namelist() if 'kernelcache' in f.lower()]
            if not kernels:
                return False
            
            kernel_data = zip_ref.read(kernels[0])
            
            print(f"[+] Kernelcache: {kernels[0]}")
            print(f"[+] Size: {len(kernel_data)} bytes")
            print(f"[+] First 16 bytes: {kernel_data[:16].hex()}")
            
            # Check for encryption patterns
            if kernel_data.startswith(b'3gmI'):
                print("[+] Status: Encrypted kernelcache (normal for iOS 5+)")
                print("[+] This is expected - kernelcaches are encrypted in IPSW")
                return True
            elif kernel_data.startswith(b'Img3'):
                print("[+] Status: Unencrypted IMG3")
                return True
            else:
                print("[!] Status: Unknown format")
                return False
                
    except Exception as e:
        print(f"[!] Check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_encryption.py <ipsw_file>")
        sys.exit(1)
    
    check_encryption(sys.argv[1])