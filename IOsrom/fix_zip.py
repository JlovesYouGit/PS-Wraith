#!/usr/bin/env python3
"""Fix corrupted ZIP/IPSW files"""
import zipfile
import sys
import os

def fix_zip(input_file, output_file):
    """Attempt to fix corrupted ZIP file"""
    try:
        print(f"[+] Attempting to fix: {input_file}")
        
        # Try to read with different methods
        with zipfile.ZipFile(input_file, 'r') as zip_in:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zip_out:
                for item in zip_in.infolist():
                    try:
                        data = zip_in.read(item.filename)
                        zip_out.writestr(item, data)
                        print(f"  ✓ {item.filename}")
                    except Exception as e:
                        print(f"  ✗ {item.filename}: {e}")
        
        print(f"[✅] Fixed ZIP: {output_file}")
        return True
        
    except Exception as e:
        print(f"[!] Fix failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_zip.py <corrupted.ipsw> <fixed.ipsw>")
        sys.exit(1)
    
    success = fix_zip(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)