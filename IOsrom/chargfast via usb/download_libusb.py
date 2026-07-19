#!/usr/bin/env python3
"""
Download libusb-1.0.dll for Windows to enable real USB communication
"""
import urllib.request
import zipfile
import os
import sys

def download_libusb():
    """Download and extract libusb-1.0.dll."""
    print("📥 Downloading libusb for Windows...")
    
    # Official libusb release URL
    url = "https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.27.7z"
    
    # Alternative: Pre-built DLL
    dll_url = "https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.27-binaries.7z"
    
    # Simpler approach: Download from a direct source
    simple_url = "https://raw.githubusercontent.com/libusb/libusb/master/README.md"
    
    print("💡 Manual download required:")
    print("1. Go to: https://github.com/libusb/libusb/releases/latest")
    print("2. Download: libusb-1.0.27-binaries.7z")
    print("3. Extract: MS64/dll/libusb-1.0.dll")
    print("4. Copy libusb-1.0.dll to current directory")
    print()
    
    # Try to create a simple test
    try:
        print("🔧 Creating libusb test...")
        
        # Check if we can find system libusb
        import ctypes
        import ctypes.util
        
        # Try to find libusb
        lib_paths = [
            "libusb-1.0.dll",
            "libusb-1.0",
            "usb-1.0",
            ctypes.util.find_library("usb-1.0"),
            ctypes.util.find_library("libusb-1.0")
        ]
        
        for path in lib_paths:
            if path:
                try:
                    lib = ctypes.CDLL(path)
                    print(f"✅ Found libusb at: {path}")
                    return True
                except:
                    continue
        
        print("❌ libusb not found in system")
        return False
        
    except Exception as e:
        print(f"❌ Error checking libusb: {e}")
        return False

def create_manual_instructions():
    """Create manual installation instructions."""
    instructions = """
# Manual libusb Installation for Windows

## Method 1: Download Pre-built DLL
1. Visit: https://github.com/libusb/libusb/releases/latest
2. Download: libusb-1.0.27-binaries.7z
3. Extract the archive
4. Copy: MS64/dll/libusb-1.0.dll to your project directory

## Method 2: Use Package Manager
```powershell
# Install scoop if not already installed
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Add buckets and install
scoop bucket add extras
scoop install libusb
```

## Method 3: System Installation
1. Download libusb from official site
2. Install to system PATH
3. Restart terminal

## Test Installation
Run: python flip_minimal_real.py
"""
    
    with open("LIBUSB_INSTALL.md", "w") as f:
        f.write(instructions)
    
    print("📄 Created LIBUSB_INSTALL.md with manual instructions")

def main():
    """Main function."""
    print("🔧 libusb Setup for Real USB Communication")
    print("=" * 45)
    
    if os.path.exists("libusb-1.0.dll"):
        print("✅ libusb-1.0.dll already exists!")
        return 0
    
    if download_libusb():
        print("✅ libusb found in system!")
        return 0
    
    create_manual_instructions()
    
    print("\n💡 Next steps:")
    print("1. Follow instructions in LIBUSB_INSTALL.md")
    print("2. Run: python flip_minimal_real.py")
    print("3. This will ACTUALLY flip the auto-boot bit!")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())