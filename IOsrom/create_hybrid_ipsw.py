#!/usr/bin/env python3
"""Create hybrid IPSW using iPad1,1 5.1.1 base with iOS 9 components"""
import os
import sys
import shutil
import zipfile

def create_hybrid_ipsw(ipad1_ipsw, ipad2_ipsw, output_ipsw):
    """Create hybrid IPSW using iPad1,1 base with patched iPad2,1 components"""
    temp_base = "temp_base"
    temp_source = "temp_source"
    
    try:
        # Clean temp directories
        for temp_dir in [temp_base, temp_source]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        
        print("[+] Extracting iPad1,1 5.1.1 base...")
        with zipfile.ZipFile(ipad1_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_base)
        
        print("[+] Extracting iPad2,1 9.3.5 source...")
        with zipfile.ZipFile(ipad2_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_source)
        
        # Copy kernelcache from iPad2,1 (will be patched)
        source_kernel = None
        for root, dirs, files in os.walk(temp_source):
            for file in files:
                if 'kernelcache' in file.lower():
                    source_kernel = os.path.join(root, file)
                    break
        
        if source_kernel:
            # Find target location in iPad1,1 structure
            for root, dirs, files in os.walk(temp_base):
                for file in files:
                    if 'kernelcache' in file.lower():
                        target_kernel = os.path.join(root, file)
                        print(f"[+] Replacing kernelcache: {file}")
                        shutil.copy2(source_kernel, target_kernel)
                        break
        
        # Keep iPad1,1 BuildManifest, Restore.plist (signed for iPad1,1)
        print("[+] Keeping iPad1,1 signatures and manifests...")
        
        # Create hybrid IPSW
        print("[+] Creating hybrid IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_base):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_base)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Hybrid IPSW created: {output_ipsw}")
        print("[!] Note: This uses iPad1,1 5.1.1 base with iOS 9 kernelcache")
        return True
        
    except Exception as e:
        print(f"[!] Hybrid creation failed: {e}")
        return False
    finally:
        # Cleanup
        for temp_dir in [temp_base, temp_source]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_hybrid_ipsw.py <ipad1_5.1.1.ipsw> <ipad2_9.3.5.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = create_hybrid_ipsw(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)