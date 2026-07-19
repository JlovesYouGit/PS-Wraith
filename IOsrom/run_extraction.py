#!/usr/bin/env python3
"""Complete extraction and patching pipeline"""
import os
import sys
from extract_all import extract_firmware
from kernelcache_a4_patcher import KernelPatcher

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <ipsw_file>")
        sys.exit(1)
    
    ipsw_file = sys.argv[1]
    output_dir = "extracted"
    
    if not os.path.exists(ipsw_file):
        print(f"Error: IPSW file not found: {ipsw_file}")
        sys.exit(1)
    
    print("[+] Starting iOS9toA4 extraction pipeline...")
    
    # Extract firmware
    extract_firmware(ipsw_file, output_dir)
    
    # Find and patch kernelcache
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if 'kernelcache' in file.lower() and file.endswith('.dec.lzss'):
                kernel_path = os.path.join(root, file)
                print(f"[+] Patching kernelcache: {kernel_path}")
                
                try:
                    patcher = KernelPatcher(kernel_path + '.lzss')
                    patcher.apply_all_patches()
                    patcher.close()
                    print(f"[✅] Kernelcache patched successfully")
                except Exception as e:
                    print(f"[!] Patching failed: {e}")
    
    print("[✅] Pipeline complete!")

if __name__ == "__main__":
    main()
