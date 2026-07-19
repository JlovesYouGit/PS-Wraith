#!/usr/bin/env python3
"""Check kernelcache structure and integrity"""
import zipfile
import struct
import sys
import os

def check_kernelcache(ipsw_path):
    """Analyze kernelcache structure"""
    try:
        with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
            # Find kernelcache
            kernels = [f for f in zip_ref.namelist() if 'kernelcache' in f.lower()]
            
            if not kernels:
                print("[!] No kernelcache found")
                return False
            
            kernel_file = kernels[0]
            print(f"[+] Found kernelcache: {kernel_file}")
            
            # Extract and analyze
            kernel_data = zip_ref.read(kernel_file)
            print(f"[+] Size: {len(kernel_data)} bytes")
            print(f"[+] First 32 bytes: {kernel_data[:32].hex()}")
            print(f"[+] Magic: {repr(kernel_data[:8])}")
            
            # Check IMG3 structure
            if kernel_data.startswith(b'Img3'):
                print("[+] Format: IMG3")
                if len(kernel_data) >= 20:
                    total_size = struct.unpack('<I', kernel_data[4:8])[0]
                    data_size = struct.unpack('<I', kernel_data[8:12])[0]
                    signed_size = struct.unpack('<I', kernel_data[12:16])[0]
                    img_type = kernel_data[16:20]
                    
                    print(f"[+] Total size: {total_size}")
                    print(f"[+] Data size: {data_size}")
                    print(f"[+] Signed size: {signed_size}")
                    print(f"[+] Type: {repr(img_type)}")
                    
                    # Check if sizes make sense
                    if total_size != len(kernel_data):
                        print(f"[!] Size mismatch: header says {total_size}, actual {len(kernel_data)}")
                    
                    if data_size + 20 > len(kernel_data):
                        print(f"[!] Data size invalid: {data_size} + 20 > {len(kernel_data)}")
                    
                    # Check payload
                    if len(kernel_data) >= 20:
                        payload = kernel_data[20:20+min(data_size, len(kernel_data)-20)]
                        print(f"[+] Payload start: {repr(payload[:16])}")
                        
                        # Check if compressed
                        if payload.startswith(b'complzss'):
                            print("[+] Payload: LZSS compressed")
                        elif payload.startswith(b'\x7fELF'):
                            print("[+] Payload: ELF binary")
                        elif payload.startswith(b'\xce\xfa\xed\xfe'):
                            print("[+] Payload: Mach-O binary")
                        else:
                            print(f"[?] Payload: Unknown format")
                else:
                    print("[!] IMG3 header too small")
            else:
                print(f"[!] Not IMG3 format: {repr(kernel_data[:8])}")
            
            return True
            
    except Exception as e:
        print(f"[!] Check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_kernelcache.py <ipsw_file>")
        sys.exit(1)
    
    check_kernelcache(sys.argv[1])