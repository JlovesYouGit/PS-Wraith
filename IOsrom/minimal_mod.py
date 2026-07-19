#!/usr/bin/env python3
"""Minimal modification - only patch kernelcache, keep everything else intact"""
import os
import sys
import shutil
import zipfile
import tempfile

def minimal_modification(ios4_ipsw, ios9_ipsw, output_ipsw):
    """Minimal mod - only replace kernelcache, keep rest identical"""
    
    # First, direct copy the original
    print("[+] Creating base copy...")
    shutil.copy2(ios4_ipsw, output_ipsw)
    
    # Now modify only the kernelcache inside the ZIP
    print("[+] Patching kernelcache only...")
    
    try:
        # Extract iOS 9 kernelcache
        with zipfile.ZipFile(ios9_ipsw, 'r') as ios9_zip:
            ios9_files = ios9_zip.namelist()
            ios9_kernel = None
            for f in ios9_files:
                if 'kernelcache' in f.lower():
                    ios9_kernel = f
                    break
            
            if not ios9_kernel:
                print("[!] No kernelcache in iOS 9 IPSW")
                return False
            
            ios9_kernel_data = ios9_zip.read(ios9_kernel)
        
        # Update the iOS 4 IPSW with iOS 9 kernelcache
        with zipfile.ZipFile(output_ipsw, 'a') as ios4_zip:
            ios4_files = ios4_zip.namelist()
            ios4_kernel = None
            for f in ios4_files:
                if 'kernelcache' in f.lower():
                    ios4_kernel = f
                    break
            
            if ios4_kernel:
                print(f"[+] Replacing {ios4_kernel} with iOS 9 version")
                # Remove old kernelcache and add new one
                # Note: zipfile doesn't support direct replacement, so we rebuild
                
                # Read all files except kernelcache
                temp_files = {}
                for f in ios4_files:
                    if f != ios4_kernel:
                        temp_files[f] = ios4_zip.read(f)
                
                # Rebuild ZIP with new kernelcache
                with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                    # Add all original files except kernelcache
                    for filename, data in temp_files.items():
                        new_zip.writestr(filename, data)
                    
                    # Add iOS 9 kernelcache with original filename
                    new_zip.writestr(ios4_kernel, ios9_kernel_data)
        
        print(f"[✅] Minimal mod complete: {output_ipsw}")
        print("[+] Only kernelcache replaced, everything else identical")
        return True
        
    except Exception as e:
        print(f"[!] Minimal mod failed: {e}")
        # Restore original if failed
        shutil.copy2(ios4_ipsw, output_ipsw)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python minimal_mod.py <ios4.ipsw> <ios9.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = minimal_modification(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)