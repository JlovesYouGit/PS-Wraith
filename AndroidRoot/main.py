#!/usr/bin/env python3
"""
AndroidRoot Quick Start
Entry point for Android root/boot chain tools
"""
import sys
import os

# Ensure AndroidRoot is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Handle both package and direct script import
try:
    from .android_root_chain import AndroidRootChain
except ImportError:
    from android_root_chain import AndroidRootChain

def main():
    chain = AndroidRootChain()
    
    print("AndroidRoot Chain - Quick Start")
    print("=" * 40)
    
    # Detect device
    print("[*] Detecting device...")
    info = chain.detect_device()
    print(f"  ADB: {info.get('adb_connected')}")
    print(f"  Fastboot: {info.get('fastboot_connected')}")
    print(f"  EDL: {info.get('edl_mode')}")
    print(f"  BROM: {info.get('brom_mode')}")
    print(f"  Chipset: {info.get('chipset')}")
    print(f"  Device: {info.get('device')}")
    print(f"  Build: {info.get('build_info', {}).get('ro.build.version.release')}")
    
    if not info.get("adb_connected") and not info.get("fastboot_connected"):
        print("\n[-] No Android device detected")
        return
    
    # Check prerequisites
    prereqs = chain.check_prerequisites()
    print("\n[*] Prerequisites:")
    for tool, available in prereqs.items():
        status = "OK" if available else "MISSING"
        print(f"  {tool}: {status}")
    
    # Attempt root
    print("\n[*] Attempting root chain...")
    result = chain.attempt_root_chain()
    print(f"  Success: {result.get('success')}")
    print(f"  Method: {result.get('method', 'N/A')}")
    if result.get("error"):
        print(f"  Error: {result.get('error')}")
    
    chain.cleanup()

if __name__ == "__main__":
    main()
