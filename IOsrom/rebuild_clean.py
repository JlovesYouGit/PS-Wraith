#!/usr/bin/env python3
"""Clean rebuild of IPSW with proper manifest handling"""
import os
import sys
import shutil
import zipfile

def rebuild_ipsw_clean(source_ipsw, output_ipsw):
    """Rebuild IPSW with minimal changes to avoid corruption"""
    temp_dir = "temp_rebuild"
    
    try:
        # Clean temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting original IPSW...")
        with zipfile.ZipFile(source_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Fix BuildManifest.plist
        manifest_path = os.path.join(temp_dir, "BuildManifest.plist")
        if os.path.exists(manifest_path):
            print("[+] Fixing BuildManifest.plist...")
            with open(manifest_path, 'rb') as f:
                data = f.read()
            
            # Minimal device ID changes
            data = data.replace(b'iPad2,1', b'iPad1,1')
            data = data.replace(b'k93ap', b'k48ap')
            
            with open(manifest_path, 'wb') as f:
                f.write(data)
        
        # Create new IPSW
        print("[+] Creating new IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Clean IPSW created: {output_ipsw}")
        return True
        
    except Exception as e:
        print(f"[!] Rebuild failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python rebuild_clean.py <source.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = rebuild_ipsw_clean(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)