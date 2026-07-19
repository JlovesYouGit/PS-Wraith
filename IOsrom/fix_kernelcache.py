#!/usr/bin/env python3
"""Fix corrupted kernelcache by using original"""
import zipfile
import sys
import os

def fix_kernelcache(original_ipsw, broken_ipsw, output_ipsw):
    """Replace corrupted kernelcache with original"""
    try:
        # Extract broken IPSW
        temp_dir = "temp_fix"
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting broken IPSW...")
        with zipfile.ZipFile(broken_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Get original kernelcache
        print("[+] Getting original kernelcache...")
        with zipfile.ZipFile(original_ipsw, 'r') as zip_ref:
            kernels = [f for f in zip_ref.namelist() if 'kernelcache' in f.lower()]
            if kernels:
                original_kernel = zip_ref.read(kernels[0])
                
                # Find kernelcache in broken IPSW
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if 'kernelcache' in file.lower():
                            kernel_path = os.path.join(root, file)
                            print(f"[+] Replacing: {file}")
                            with open(kernel_path, 'wb') as f:
                                f.write(original_kernel)
                            break
        
        # Rebuild IPSW
        print("[+] Rebuilding IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Fixed IPSW: {output_ipsw}")
        return True
        
    except Exception as e:
        print(f"[!] Fix failed: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python fix_kernelcache.py <original.ipsw> <broken.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = fix_kernelcache(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)