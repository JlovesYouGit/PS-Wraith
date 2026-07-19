#!/usr/bin/env python3
"""Create redsn0w-compatible IPSW"""
import os
import sys
import shutil
import zipfile

def create_redsn0w_ipsw(base_ipsw, output_ipsw):
    """Create IPSW that redsn0w can recognize"""
    temp_dir = "temp_redsn0w"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting base IPSW...")
        with zipfile.ZipFile(base_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # redsn0w needs specific structure - keep original manifest
        print("[+] Keeping original BuildManifest for redsn0w compatibility...")
        
        # Just patch the kernelcache in place
        kernel_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if 'kernelcache' in file.lower():
                    kernel_path = os.path.join(root, file)
                    break
        
        if kernel_path:
            print(f"[+] Found kernelcache: {os.path.basename(kernel_path)}")
            print("[+] Note: Using original encrypted kernelcache for redsn0w")
            print("[+] A4 patches will be applied during jailbreak process")
        
        # Create redsn0w-compatible IPSW
        print("[+] Creating redsn0w-compatible IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] redsn0w-compatible IPSW: {output_ipsw}")
        print("[!] This is original IPSW - A4 patches applied via jailbreak")
        return True
        
    except Exception as e:
        print(f"[!] Creation failed: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_redsn0w_ipsw.py <base.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = create_redsn0w_ipsw(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)