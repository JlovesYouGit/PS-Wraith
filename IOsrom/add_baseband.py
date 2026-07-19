#!/usr/bin/env python3
"""Add iOS 4.3.3 baseband to stealth frankenstein IPSW"""
import os
import sys
import shutil
import zipfile

def add_baseband(ios4_ipsw, stealth_ipsw, output_ipsw):
    """Add iOS 4.3.3 baseband to stealth IPSW"""
    temp_ios4 = "temp_ios4_bb"
    temp_stealth = "temp_stealth_bb"
    
    try:
        # Clean temp directories
        for temp_dir in [temp_ios4, temp_stealth]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        
        print("[+] Extracting iOS 4.3.3 for baseband...")
        with zipfile.ZipFile(ios4_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_ios4)
        
        print("[+] Extracting stealth IPSW...")
        with zipfile.ZipFile(stealth_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_stealth)
        
        # Find baseband files in iOS 4.3.3
        baseband_files = []
        for root, dirs, files in os.walk(temp_ios4):
            for file in files:
                if any(x in file.lower() for x in ['baseband', 'radio', 'bbfw']):
                    baseband_files.append((os.path.join(root, file), file))
                    print(f"[+] Found baseband: {file}")
        
        # Copy baseband files to stealth IPSW
        for src_path, filename in baseband_files:
            # Find corresponding location in stealth IPSW
            for root, dirs, files in os.walk(temp_stealth):
                if filename in files:
                    dst_path = os.path.join(root, filename)
                    print(f"[+] Replacing {filename}")
                    shutil.copy2(src_path, dst_path)
                    break
            else:
                # If not found, add to same relative location
                rel_path = os.path.relpath(src_path, temp_ios4)
                dst_path = os.path.join(temp_stealth, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                print(f"[+] Adding {filename}")
                shutil.copy2(src_path, dst_path)
        
        # Rebuild IPSW
        print("[+] Creating IPSW with matching baseband...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_stealth):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_stealth)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] IPSW with matching baseband: {output_ipsw}")
        return True
        
    except Exception as e:
        print(f"[!] Baseband addition failed: {e}")
        return False
    finally:
        # Cleanup
        for temp_dir in [temp_ios4, temp_stealth]:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_baseband.py <ios4.ipsw> <stealth.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = add_baseband(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)