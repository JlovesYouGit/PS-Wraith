#!/usr/bin/env python3
"""Flash custom IPSW using limera1n exploit"""
import os
import sys
import subprocess

def flash_with_limera1n(ipsw_path):
    """Flash IPSW using limera1n exploit"""
    limera1n_dir = "limera1n"
    
    if not os.path.exists(limera1n_dir):
        print(f"[!] limera1n directory not found: {limera1n_dir}")
        return False
    
    # Find limera1n executable
    limera1n_exe = None
    for file in os.listdir(limera1n_dir):
        if file.lower().startswith('limera1n') and file.endswith('.exe'):
            limera1n_exe = os.path.join(limera1n_dir, file)
            break
    
    if not limera1n_exe:
        print("[!] limera1n.exe not found in limera directory")
        return False
    
    print(f"[+] Found limera1n: {limera1n_exe}")
    print(f"[+] Target IPSW: {ipsw_path}")
    
    try:
        print("[+] Put device in DFU mode and press Enter...")
        input()
        
        print("[+] Running limera1n exploit...")
        # Run limera1n to exploit device
        result = subprocess.run([limera1n_exe], cwd=limera1n_dir, capture_output=True)
        
        if result.returncode == 0:
            print("[✅] limera1n exploit successful")
            
            # Now flash custom IPSW
            print("[+] Flashing custom IPSW...")
            print(f"[+] Use iTunes or other tool to flash: {ipsw_path}")
            print("[+] Device should now accept unsigned firmware")
            return True
        else:
            print(f"[!] limera1n failed: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"[!] Flash failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python limera1n_flash.py <custom.ipsw>")
        sys.exit(1)
    
    success = flash_with_limera1n(sys.argv[1])
    sys.exit(0 if success else 1)