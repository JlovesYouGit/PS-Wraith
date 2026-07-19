#!/usr/bin/env python
import subprocess
import os
import sys

def fix_libusb_backend():
    """Fix libusb backend architecture issues."""
    # Force use of libusb-1.0 backend
    os.environ['PYUSB_DEBUG'] = 'debug'
    os.environ['LIBUSB_DEBUG'] = '4'
    
    # Set backend to use libusb-1.0.dll directly
    try:
        import usb.backend.libusb1
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./libusb-1.0.dll")
        if backend:
            print("✅ libusb-1.0 backend loaded")
        else:
            print("❌ Failed to load libusb-1.0 backend")
    except:
        print("⚠️ PyUSB not available")

def fix_irecovery_backend():
    """Fix irecovery backend to use correct USB library."""
    # Copy required DLLs to system path
    dlls = ["libusb-1.0.dll", "irecovery.dll", "libxml2.dll", "plist.dll"]
    
    for dll in dlls:
        if os.path.exists(dll):
            try:
                # Copy to Windows system directory
                subprocess.run(f'copy "{dll}" "%WINDIR%\\System32\\"', shell=True)
                print(f"✅ Copied {dll} to system")
            except:
                print(f"⚠️ Could not copy {dll}")

def set_usb_backend_env():
    """Set environment variables for stable USB backend."""
    env_vars = {
        'LIBUSB_DEBUG': '0',
        'PYUSB_DEBUG': 'info', 
        'LIBUSB_LOG_LEVEL': '0'
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        subprocess.run(f'setx {var} "{value}"', shell=True)
        print(f"✅ Set {var}={value}")

if __name__ == "__main__":
    print("🔧 Fixing USB backend architecture...")
    fix_libusb_backend()
    fix_irecovery_backend() 
    set_usb_backend_env()
    print("✅ Backend fixes applied - restart terminal and try again")