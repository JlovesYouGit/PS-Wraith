#!/usr/bin/env python3
"""Rename firmware components for A4 compatibility"""
import os
import sys
import shutil
import zipfile

def rename_firmware_components(ipsw_path, output_path):
    """Rename all firmware components from A5 to A4 naming"""
    temp_dir = "temp_rename"
    
    try:
        # Clean temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        print("[+] Extracting IPSW...")
        with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # File renaming mappings
        renames = {
            # SoC identifier changes
            's5l8940x': 's5l8930x',
            's5l8942x': 's5l8930x', 
            # Board config changes
            'k93ap': 'k48ap',
            'k93': 'k48',
            # Device changes
            'iPad2,1': 'iPad1,1',
            'iPad2,2': 'iPad1,1',
            'iPad2,3': 'iPad1,1'
        }
        
        print("[+] Renaming firmware components...")
        
        # Walk through all files and rename them
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                old_path = os.path.join(root, file)
                new_file = file
                
                # Apply all renaming rules
                for old_name, new_name in renames.items():
                    new_file = new_file.replace(old_name, new_name)
                
                if new_file != file:
                    new_path = os.path.join(root, new_file)
                    print(f"  {file} -> {new_file}")
                    shutil.move(old_path, new_path)
        
        # Also rename directory structures
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for dir_name in dirs:
                old_dir = os.path.join(root, dir_name)
                new_dir_name = dir_name
                
                for old_name, new_name in renames.items():
                    new_dir_name = new_dir_name.replace(old_name, new_name)
                
                if new_dir_name != dir_name:
                    new_dir = os.path.join(root, new_dir_name)
                    print(f"  DIR: {dir_name} -> {new_dir_name}")
                    shutil.move(old_dir, new_dir)
        
        # Fix BuildManifest.plist
        manifest_path = os.path.join(temp_dir, "BuildManifest.plist")
        if os.path.exists(manifest_path):
            print("[+] Fixing BuildManifest.plist...")
            with open(manifest_path, 'rb') as f:
                data = f.read()
            
            # Apply same renaming to manifest
            for old_name, new_name in renames.items():
                data = data.replace(old_name.encode(), new_name.encode())
            
            with open(manifest_path, 'wb') as f:
                f.write(data)
        
        # Create new IPSW
        print("[+] Creating renamed IPSW...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Renamed IPSW created: {output_path}")
        return True
        
    except Exception as e:
        print(f"[!] Rename failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python rename_components.py <source.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = rename_firmware_components(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)