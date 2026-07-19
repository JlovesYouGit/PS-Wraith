#!/usr/bin/env python3
"""Simple Frankenstein - minimal changes to preserve IPSW structure"""
import os
import sys
import shutil
import zipfile

def create_simple_frankenstein(ios4_ipsw, output_ipsw):
    """Create simple frankenstein keeping iOS 4 structure intact"""
    temp_dir = "temp_simple_frank"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting iOS 4.3.3 base...")
        with zipfile.ZipFile(ios4_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        print("[+] Keeping original iOS 4.3.3 structure...")
        print("[+] This will be jailbroken with sn0wbreeze")
        print("[+] iOS 9 components added via Cydia after jailbreak")
        
        # Create output IPSW (exact copy for now)
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Simple Frankenstein IPSW: {output_ipsw}")
        print("[!] This is clean iOS 4.3.3 - sn0wbreeze should accept it")
        return True
        
    except Exception as e:
        print(f"[!] Creation failed: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simple_frankenstein.py <ios4.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = create_simple_frankenstein(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)