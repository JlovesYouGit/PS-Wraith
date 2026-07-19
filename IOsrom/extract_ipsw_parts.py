#!/usr/bin/env python3
"""Extract IPSW components for raw flash"""
import os
import zipfile
import shutil

def extract_ipsw():
    """Extract iPad1,1_iOS9_A4_Final.ipsw components"""
    ipsw_file = "iPad1,1_iOS9_A4_Final.ipsw"
    extract_dir = "iPad1,1_iOS9_A4_Final"
    
    if not os.path.exists(ipsw_file):
        print(f"[!] {ipsw_file} not found")
        return False
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    
    print(f"[+] Extracting {ipsw_file}...")
    with zipfile.ZipFile(ipsw_file, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Find key components
    components = {
        "iBoot.patched": "iBoot*",
        "kernelcache.release.n90ap": "kernelcache*",
        "rootfs9.dmg": "*.dmg"
    }
    
    for target, pattern in components.items():
        found = False
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if pattern.replace("*", "") in file.lower():
                    src = os.path.join(root, file)
                    dst = os.path.join(extract_dir, target)
                    shutil.copy2(src, dst)
                    print(f"[+] Found {target}: {file}")
                    found = True
                    break
            if found:
                break
    
    print(f"[✅] Components extracted to {extract_dir}/")
    return True

if __name__ == "__main__":
    extract_ipsw()