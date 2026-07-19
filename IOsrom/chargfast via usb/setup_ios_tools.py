#!/usr/bin/env python
"""
Setup script for iOS recovery tools and dependencies.
"""
import subprocess
import sys
import os
from pathlib import Path
import urllib.request
import zipfile

def check_python_packages():
    """Check and install required Python packages."""
    required_packages = [
        "pyusb==1.3.1",
        "libusb1==3.3.1", 
        "pywinusb==0.4.2"
    ]
    
    print("🐍 Checking Python packages...")
    
    for package in required_packages:
        try:
            package_name = package.split("==")[0]
            __import__(package_name)
            print(f"✅ {package_name} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_irecovery():
    """Check if irecovery is available."""
    current_dir = Path.cwd()
    irecovery_exe = current_dir / "irecovery.exe"
    
    if irecovery_exe.exists():
        print("✅ irecovery.exe found")
        return True
    
    print("❌ irecovery.exe not found")
    print("📥 You need to download libimobiledevice tools")
    print("🔗 Download from: https://github.com/libimobiledevice-win32/imobiledevice-net/releases")
    print("📋 Look for: libimobiledevice.1.2.1-r1122-win-x64.zip or similar")
    
    return False

def test_ios_connection():
    """Test if we can connect to an iOS device."""
    current_dir = Path.cwd()
    irecovery_exe = current_dir / "irecovery.exe"
    
    if not irecovery_exe.exists():
        return False
    
    print("🔍 Testing iOS device connection...")
    
    try:
        result = subprocess.run([
            str(irecovery_exe), "-q"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ iOS device found in recovery mode!")
            print("📱 Device info:")
            for line in result.stdout.split('\n'):
                if line.strip() and ':' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("ℹ️  No iOS device in recovery mode (this is normal if device is booting normally)")
            return True  # Not an error, just no device in recovery
            
    except subprocess.TimeoutExpired:
        print("⚠️  Connection timeout - device may not be responding")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_usb_scanner():
    """Test the USB scanner functionality."""
    print("🔍 Testing USB scanner...")
    
    try:
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "text"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ USB scanner working")
            # Check if any Apple devices found
            if "Apple" in result.stdout or "iPad" in result.stdout or "iPhone" in result.stdout:
                print("📱 Apple devices detected!")
            else:
                print("ℹ️  No Apple devices currently detected")
            return True
        else:
            print(f"❌ USB scanner failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing USB scanner: {e}")
        return False

def main():
    """Main setup function."""
    print("🛠️  iOS Recovery Tools Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python packages
    if not check_python_packages():
        success = False
    
    print()
    
    # Check irecovery
    if not check_irecovery():
        success = False
    
    print()
    
    # Test USB scanner
    if not test_usb_scanner():
        success = False
    
    print()
    
    # Test iOS connection if irecovery is available
    if Path.cwd() / "irecovery.exe" in Path.cwd().iterdir():
        test_ios_connection()
    
    print()
    print("=" * 40)
    
    if success:
        print("✅ Setup completed successfully!")
        print()
        print("🚀 Available commands:")
        print("   python src/usb_scanner.py --apple-scan")
        print("   python src/usb_scanner.py --ios-recovery") 
        print("   python fix_auto_boot.py")
        print("   python src/ios_recovery_manager.py --scan")
        print()
        print("💡 To fix iOS charging issues:")
        print("   1. Put your iOS device in recovery mode")
        print("   2. Run: python fix_auto_boot.py")
    else:
        print("❌ Setup incomplete - please resolve the issues above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())