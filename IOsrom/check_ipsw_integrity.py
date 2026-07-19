#!/usr/bin/env python3
"""Check IPSW integrity and components"""
import zipfile
import os
import sys

def check_ipsw(ipsw_path):
    """Verify IPSW integrity and required components"""
    try:
        print(f"[+] Checking IPSW: {ipsw_path}")
        
        # Check ZIP integrity
        with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
            bad_files = zip_ref.testzip()
            if bad_files:
                print(f"[!] Corrupted files: {bad_files}")
                return False
            
            files = zip_ref.namelist()
            print(f"[+] ZIP integrity: OK ({len(files)} files)")
            
            # Check required components
            required = [
                'BuildManifest.plist',
                'Restore.plist'
            ]
            
            for req in required:
                if req in files:
                    print(f"[✓] {req}")
                else:
                    print(f"[✗] Missing: {req}")
            
            # Check kernelcache
            kernels = [f for f in files if 'kernelcache' in f.lower()]
            if kernels:
                for k in kernels:
                    print(f"[✓] Kernelcache: {k}")
            else:
                print("[✗] No kernelcache found")
            
            # Check IMG3 files
            img3_files = [f for f in files if f.endswith('.img3')]
            print(f"[+] IMG3 files: {len(img3_files)}")
            
            # Extract and check BuildManifest
            try:
                manifest_data = zip_ref.read('BuildManifest.plist')
                if b'iPad1,1' in manifest_data:
                    print("[✓] BuildManifest contains iPad1,1")
                else:
                    print("[!] BuildManifest missing iPad1,1")
                    
                if b'k48ap' in manifest_data:
                    print("[✓] BuildManifest contains k48ap")
                else:
                    print("[!] BuildManifest missing k48ap")
                    
            except Exception as e:
                print(f"[!] BuildManifest check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"[!] IPSW check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_ipsw_integrity.py <ipsw_file>")
        sys.exit(1)
    
    check_ipsw(sys.argv[1])