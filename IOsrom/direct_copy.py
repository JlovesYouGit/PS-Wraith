#!/usr/bin/env python3
"""Direct copy of IPSW without any modifications"""
import shutil
import sys

def direct_copy(source, target):
    """Direct file copy"""
    try:
        print(f"[+] Copying {source} to {target}")
        shutil.copy2(source, target)
        print("[✅] Direct copy complete")
        return True
    except Exception as e:
        print(f"[!] Copy failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python direct_copy.py <source.ipsw> <target.ipsw>")
        sys.exit(1)
    
    direct_copy(sys.argv[1], sys.argv[2])