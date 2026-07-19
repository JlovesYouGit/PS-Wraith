#!/usr/bin/env python3
"""Fix corrupted BuildManifest.plist"""
import os
import sys
import shutil

def fix_manifest(ipsw_dir):
    """Copy original BuildManifest and fix it properly"""
    manifest_path = os.path.join(ipsw_dir, "BuildManifest.plist")
    
    if not os.path.exists(manifest_path):
        print("BuildManifest.plist not found")
        return False
    
    # Backup original
    shutil.copy2(manifest_path, manifest_path + ".backup")
    
    # Read as text and do minimal fixes
    try:
        with open(manifest_path, 'rb') as f:
            data = f.read()
        
        # Convert to string for text replacement
        text = data.decode('utf-8', errors='ignore')
        
        # Simple text replacements for device compatibility
        text = text.replace('iPad2,1', 'iPad1,1')
        text = text.replace('iPad2,2', 'iPad1,1') 
        text = text.replace('iPad2,3', 'iPad1,1')
        text = text.replace('k93ap', 'k48ap')  # Board config
        
        # Write back
        with open(manifest_path, 'wb') as f:
            f.write(text.encode('utf-8'))
        
        print("Fixed BuildManifest.plist")
        return True
        
    except Exception as e:
        # Restore backup if fix failed
        shutil.copy2(manifest_path + ".backup", manifest_path)
        print(f"Failed to fix manifest: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_manifest.py <ipsw_directory>")
        sys.exit(1)
    
    fix_manifest(sys.argv[1])