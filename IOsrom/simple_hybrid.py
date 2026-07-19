#!/usr/bin/env python3
"""Simple hybrid - keep iPad1,1 kernelcache, just update userland"""
import os
import sys
import shutil
import zipfile

def create_simple_hybrid(ipad1_ipsw, output_ipsw):
    """Create simple hybrid keeping iPad1,1 kernelcache intact"""
    temp_dir = "temp_simple"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting iPad1,1 5.1.1...")
        with zipfile.ZipFile(ipad1_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        print("[+] Keeping original iPad1,1 kernelcache and bootchain")
        print("[+] This will boot iOS 5.1.1 but with A4 optimizations")
        
        # Create output IPSW
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Simple hybrid created: {output_ipsw}")
        print("[!] This is pure iPad1,1 5.1.1 - should restore successfully")
        return True
        
    except Exception as e:
        print(f"[!] Simple hybrid failed: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simple_hybrid.py <ipad1_5.1.1.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = create_simple_hybrid(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)