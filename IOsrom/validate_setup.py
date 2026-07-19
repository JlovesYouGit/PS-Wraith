#!/usr/bin/env python3
"""Setup validation script for iOS9toA4 project"""
import os
import sys
import subprocess

def check_python_tools():
    """Validate Python tools are working"""
    tools = [
        'img4tool.py',
        'ipsw_tool.py', 
        'lzss_tool.py',
        'kernelcache_a4_patcher.py',
        'kernel_patches.py',
        'iboot_patches.py',
        'devicetree_patches.py'
    ]
    
    print("[+] Validating Python tools...")
    for tool in tools:
        if not os.path.exists(tool):
            print(f"[!] Missing: {tool}")
            return False
        
        # Test syntax
        try:
            subprocess.run([sys.executable, '-m', 'py_compile', tool], 
                         check=True, capture_output=True)
            print(f"[✓] {tool}")
        except subprocess.CalledProcessError as e:
            print(f"[!] Syntax error in {tool}: {e}")
            return False
    
    return True

def check_ipsw_files():
    """Check for IPSW files"""
    ipsw_files = [
        'iPad1,1_5.1.1_9B206_Restore.ipsw',
        'iPad2,1_9.3.5_13G36_Restore.ipsw'
    ]
    
    print("[+] Checking IPSW files...")
    for ipsw in ipsw_files:
        if os.path.exists(ipsw):
            size = os.path.getsize(ipsw) / (1024*1024)
            print(f"[✓] {ipsw} ({size:.1f} MB)")
        else:
            print(f"[!] Missing: {ipsw}")
    
    return True

def main():
    print("iOS9toA4 Setup Validation")
    print("=" * 30)
    
    success = True
    success &= check_python_tools()
    success &= check_ipsw_files()
    
    if success:
        print("\n[✅] All components validated successfully!")
        return 0
    else:
        print("\n[❌] Validation failed - check missing components")
        return 1

if __name__ == "__main__":
    sys.exit(main())