#!/usr/bin/env python3
"""Fix BuildManifest.plist for device compatibility"""
import plistlib
import sys
import os

def fix_buildmanifest(manifest_path):
    """Update BuildManifest.plist for A4 compatibility"""
    try:
        with open(manifest_path, 'rb') as f:
            manifest = plistlib.load(f)
    except Exception as e:
        print(f"Error reading manifest: {e}")
        return False
    
    # Update supported products
    if 'SupportedProductTypes' in manifest:
        # Add iPad1,1 support
        if 'iPad1,1' not in manifest['SupportedProductTypes']:
            manifest['SupportedProductTypes'].append('iPad1,1')
        
        # Remove iPad2,x entries to avoid conflicts
        manifest['SupportedProductTypes'] = [
            p for p in manifest['SupportedProductTypes'] 
            if not p.startswith('iPad2,')
        ]
    
    # Update build identities
    if 'BuildIdentities' in manifest:
        for identity in manifest['BuildIdentities']:
            if 'Info' in identity:
                # Change device class
                if 'DeviceClass' in identity['Info']:
                    identity['Info']['DeviceClass'] = 'iPad'
                
                # Update restore behavior
                if 'RestoreBehavior' in identity['Info']:
                    identity['Info']['RestoreBehavior'] = 'Erase'
    
    # Write back
    try:
        with open(manifest_path, 'wb') as f:
            plistlib.dump(manifest, f)
        print(f"Fixed BuildManifest.plist: {manifest_path}")
        return True
    except Exception as e:
        print(f"Error writing manifest: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_buildmanifest.py <BuildManifest.plist>")
        sys.exit(1)
    
    fix_buildmanifest(sys.argv[1])