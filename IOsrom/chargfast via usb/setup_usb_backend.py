#!/usr/bin/env python3
"""
Setup USB Backend - Download and install libusb-1.0.dll
"""
import urllib.request
import os
import sys

def download_libusb_dll():
    """Download libusb-1.0.dll directly."""
    print("📥 Downloading libusb-1.0.dll...")
    
    # Direct DLL download URLs
    urls = [
        "https://raw.githubusercontent.com/pyusb/pyusb/main/libusb-1.0.dll",
        "https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.dll"
    ]
    
    for url in urls:
        try:
            print(f"   Trying: {url}")
            urllib.request.urlretrieve(url, "libusb-1.0.dll")
            
            if os.path.exists("libusb-1.0.dll") and os.path.getsize("libusb-1.0.dll") > 1000:
                print("   ✅ libusb-1.0.dll downloaded successfully!")
                return True
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    # Manual approach
    print("\n💡 Manual download required:")
    print("1. Go to: https://libusb.info/")
    print("2. Download: Latest Windows binaries")
    print("3. Extract: libusb-1.0.dll (64-bit)")
    print("4. Copy to current directory")
    
    return False

def test_usb_backend():
    """Test if USB backend is working."""
    print("\n🔧 Testing USB backend...")
    
    try:
        import usb.core
        import usb.backend.libusb1
        
        # Try to get backend
        backend = usb.backend.libusb1.get_backend()
        if backend is None:
            print("❌ libusb1 backend not available")
            return False
        
        print("✅ libusb1 backend available!")
        
        # Try to find devices
        devices = list(usb.core.find(find_all=True))
        print(f"✅ Found {len(devices)} USB devices")
        
        # Look for iPad specifically
        ipad = usb.core.find(idVendor=0x05AC, idProduct=0x1281)
        if ipad:
            print("✅ iPad found in Recovery Mode!")
            print(f"   Device: {ipad}")
            return True
        else:
            print("💡 iPad not found (may not be in Recovery Mode)")
            return True  # Backend works, just no iPad
        
    except Exception as e:
        print(f"❌ USB backend test failed: {e}")
        return False

def main():
    """Main function."""
    print("🔧 USB Backend Setup")
    print("=" * 25)
    
    if os.path.exists("libusb-1.0.dll"):
        print("✅ libusb-1.0.dll already exists")
    else:
        if not download_libusb_dll():
            return 1
    
    if test_usb_backend():
        print("\n🎉 USB Backend Ready!")
        print("✅ You can now run: python ULTIMATE_REAL_FLIPPER.py")
        return 0
    else:
        print("\n❌ USB Backend Setup Failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())