#!/usr/bin/env python3
"""Stealth Frankenstein - iOS 9 kernel disguised as iOS 4.3.3"""
import os
import sys
import shutil
import zipfile
import struct

def stealth_frankenstein(ios4_ipsw, ios9_ipsw, output_ipsw):
    """Make iOS 9 kernel look exactly like iOS 4.3.3 kernel"""
    
    print("[+] Creating stealth frankenstein...")
    shutil.copy2(ios4_ipsw, output_ipsw)
    
    try:
        # Extract original iOS 4 kernelcache for metadata
        with zipfile.ZipFile(ios4_ipsw, 'r') as ios4_zip:
            ios4_files = ios4_zip.namelist()
            ios4_kernel_name = None
            for f in ios4_files:
                if 'kernelcache' in f.lower():
                    ios4_kernel_name = f
                    break
            
            if not ios4_kernel_name:
                print("[!] No iOS 4 kernelcache found")
                return False
            
            ios4_kernel_data = ios4_zip.read(ios4_kernel_name)
            print(f"[+] Original iOS 4 kernel: {ios4_kernel_name}")
            print(f"[+] Size: {len(ios4_kernel_data)} bytes")
            print(f"[+] Header: {ios4_kernel_data[:16].hex()}")
        
        # Extract iOS 9 kernelcache payload
        with zipfile.ZipFile(ios9_ipsw, 'r') as ios9_zip:
            ios9_files = ios9_zip.namelist()
            ios9_kernel_name = None
            for f in ios9_files:
                if 'kernelcache' in f.lower():
                    ios9_kernel_name = f
                    break
            
            if not ios9_kernel_name:
                print("[!] No iOS 9 kernelcache found")
                return False
            
            ios9_kernel_data = ios9_zip.read(ios9_kernel_name)
            print(f"[+] iOS 9 kernel: {ios9_kernel_name}")
            print(f"[+] Size: {len(ios9_kernel_data)} bytes")
        
        # Create hybrid kernel: iOS 4 metadata + iOS 9 payload (truncated to iOS 4 size)
        print("[+] Creating stealth hybrid kernel...")
        
        if ios4_kernel_data.startswith(b'Img3') and len(ios4_kernel_data) >= 20:
            # Extract iOS 4 IMG3 metadata
            ios4_total_size = struct.unpack('<I', ios4_kernel_data[4:8])[0]
            ios4_data_size = struct.unpack('<I', ios4_kernel_data[8:12])[0]
            ios4_signed_size = struct.unpack('<I', ios4_kernel_data[12:16])[0]
            ios4_type = ios4_kernel_data[16:20]
            
            print(f"[+] iOS 4 metadata: size={ios4_total_size}, data={ios4_data_size}, type={ios4_type}")
            
            # Use iOS 9 payload but truncate to iOS 4 size
            if len(ios9_kernel_data) >= 20:
                ios9_payload = ios9_kernel_data[20:]  # Skip iOS 9 header
                
                # Truncate iOS 9 payload to match iOS 4 data size
                if len(ios9_payload) > ios4_data_size:
                    ios9_payload = ios9_payload[:ios4_data_size]
                elif len(ios9_payload) < ios4_data_size:
                    # Pad with zeros if needed
                    ios9_payload += b'\x00' * (ios4_data_size - len(ios9_payload))
                
                # Build stealth kernel: iOS 4 header + iOS 9 payload
                stealth_kernel = (
                    b'Img3' +                           # iOS 4 magic
                    struct.pack('<I', ios4_total_size) + # iOS 4 total size
                    struct.pack('<I', ios4_data_size) +  # iOS 4 data size
                    struct.pack('<I', ios4_signed_size) + # iOS 4 signed size
                    ios4_type +                          # iOS 4 type
                    ios9_payload                         # iOS 9 payload (truncated)
                )
                
                print(f"[+] Stealth kernel size: {len(stealth_kernel)} bytes")
                print(f"[+] Header: {stealth_kernel[:16].hex()}")
                
            else:
                print("[!] iOS 9 kernel too small")
                return False
        else:
            print("[!] iOS 4 kernel not IMG3 format")
            return False
        
        # Replace kernelcache in IPSW
        print("[+] Injecting stealth kernel...")
        with zipfile.ZipFile(output_ipsw, 'r') as zip_read:
            temp_files = {}
            for f in zip_read.namelist():
                if f != ios4_kernel_name:
                    temp_files[f] = zip_read.read(f)
        
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            # Add all original files except kernelcache
            for filename, data in temp_files.items():
                zip_write.writestr(filename, data)
            
            # Add stealth kernelcache
            zip_write.writestr(ios4_kernel_name, stealth_kernel)
        
        print(f"[✅] Stealth Frankenstein created: {output_ipsw}")
        print("[+] Appears as iOS 4.3.3 but contains iOS 9 code")
        return True
        
    except Exception as e:
        print(f"[!] Stealth creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python stealth_frankenstein.py <ios4.ipsw> <ios9.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = stealth_frankenstein(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)