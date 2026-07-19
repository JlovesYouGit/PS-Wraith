#!/usr/bin/env python3
"""Just copy the original IPSW to test restore"""
import shutil
import sys

def copy_original(original_ipsw, output_ipsw):
    """Copy original IPSW for testing"""
    try:
        print(f"[+] Copying {original_ipsw} to {output_ipsw}")
        shutil.copy2(original_ipsw, output_ipsw)
        print("[✅] Copy complete")
        return True
    except Exception as e:
        print(f"[!] Copy failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python use_original.py <original.ipsw> <output.ipsw>")
        sys.exit(1)
    
    copy_original(sys.argv[1], sys.argv[2])