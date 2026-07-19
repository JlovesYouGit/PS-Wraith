#!/usr/bin/env python3
import os
import sys
from img4tool import IMG4Tool
from img3tool import IMG3Tool
from ipsw_tool import IPSWTool
from lzss_tool import decompress_lzss

def extract_firmware(ipsw_path, output_dir):
    """Complete firmware extraction pipeline"""
    os.makedirs(output_dir, exist_ok=True)
    
    ipsw = IPSWTool()
    img4 = IMG4Tool()
    img3 = IMG3Tool()
    
    print(f"[+] Extracting IPSW: {ipsw_path}")
    ipsw.extract_all(ipsw_path, output_dir)
    
    # Find and extract kernelcache
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if 'kernelcache' in file.lower():
                kernel_path = os.path.join(root, file)
                kernel_dec = kernel_path + '.dec'
                
                print(f"[+] Extracting kernelcache: {file}")
                try:
                    # Try IMG4 first, then IMG3 as fallback
                    if file.endswith('.img3') or 'k93' in file:
                        img3.extract(kernel_path, kernel_dec)
                    else:
                        try:
                            img4.extract(kernel_path, kernel_dec)
                        except ValueError:
                            # Fallback to IMG3 if IMG4 fails
                            img3.extract(kernel_path, kernel_dec)
                    
                    # Try LZSS decompression
                    with open(kernel_dec, 'rb') as f:
                        data = f.read()
                    
                    if data.startswith(b'complzss'):
                        print(f"[+] Decompressing LZSS...")
                        decompressed = decompress_lzss(data)
                        with open(kernel_dec + '.lzss', 'wb') as f:
                            f.write(decompressed)
                        print(f"[+] Decompressed kernelcache ready: {kernel_dec}.lzss")
                    
                except Exception as e:
                    print(f"[!] Failed to extract {file}: {e}")
            
            # Extract iBoot
            if 'iboot' in file.lower() or file.startswith('iBoot'):
                iboot_path = os.path.join(root, file)
                iboot_dec = iboot_path + '.dec'
                
                print(f"[+] Extracting iBoot: {file}")
                try:
                    # Try IMG4 first, then IMG3 as fallback
                    if file.endswith('.img3') or 'k93' in file:
                        img3.extract(iboot_path, iboot_dec)
                    else:
                        try:
                            img4.extract(iboot_path, iboot_dec)
                        except ValueError:
                            # Fallback to IMG3 if IMG4 fails
                            img3.extract(iboot_path, iboot_dec)
                except Exception as e:
                    print(f"[!] Failed to extract {file}: {e}")
    
    print(f"[✅] Extraction complete: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_all.py <ipsw_path> <output_dir>")
        sys.exit(1)
    
    extract_firmware(sys.argv[1], sys.argv[2])