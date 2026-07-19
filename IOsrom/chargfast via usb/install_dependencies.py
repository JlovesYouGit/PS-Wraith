#!/usr/bin/env python3
"""
Install all required dependencies for iPad boot management.
"""
import subprocess
import sys
import os
import platform

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔧 {description}")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success!")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    return True

def check_scoop():
    """Check if Scoop is installed on Windows."""
    try:
        result = subprocess.run("scoop --version", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_scoop():
    """Install Scoop package manager on Windows."""
    print("🔧 Installing Scoop package manager...")
    cmd = 'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex'
    return run_command(f'powershell -Command "{cmd}"', "Installing Scoop")

def main():
    """Main installation function."""
    print("🚀 iPad Boot Management Dependencies Installer")
    print("=" * 55)
    
    system = platform.system().lower()
    print(f"📱 Detected OS: {platform.system()} {platform.release()}")
    print()
    
    if system == "windows":
        print("🔧 Windows Installation Process:")
        print()
        
        # Check if Scoop is installed
        if not check_scoop():
            print("❌ Scoop not found. Installing Scoop package manager...")
            if not install_scoop():
                print("❌ Failed to install Scoop. Please install manually:")
                print("   1. Open PowerShell as Administrator")
                print("   2. Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser")
                print("   3. Run: irm get.scoop.sh | iex")
                return 1
        else:
            print("✅ Scoop already installed")
        
        # Install libusb
        if not run_command("scoop install libusb", "Installing libusb"):
            print("⚠️  libusb installation failed. Trying alternative...")
            run_command("scoop bucket add extras", "Adding extras bucket")
            run_command("scoop install libusb", "Retrying libusb installation")
        
        # Install irecovery
        if not run_command("scoop install irecovery", "Installing irecovery"):
            print("⚠️  irecovery not available in main bucket. Trying alternatives...")
            run_command("scoop bucket add extras", "Adding extras bucket")
            run_command("scoop install irecovery", "Retrying irecovery installation")
        
        print()
        print("📋 Manual Installation (if automatic failed):")
        print("   1. Download libusb-win32 from: https://libusb-win32.sourceforge.io/")
        print("   2. Download irecovery from: https://github.com/libimobiledevice/irecovery")
        print("   3. Add to PATH environment variable")
        
    elif system == "darwin":  # macOS
        print("🔧 macOS Installation Process:")
        print()
        
        # Check if Homebrew is installed
        try:
            subprocess.run("brew --version", shell=True, check=True, capture_output=True)
            print("✅ Homebrew already installed")
        except:
            print("❌ Homebrew not found. Installing...")
            cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            run_command(cmd, "Installing Homebrew")
        
        # Install dependencies
        run_command("brew install libusb", "Installing libusb")
        run_command("brew install irecovery", "Installing irecovery")
        
    elif system == "linux":
        print("🔧 Linux Installation Process:")
        print()
        
        # Detect package manager
        if os.path.exists("/usr/bin/apt"):
            run_command("sudo apt update", "Updating package list")
            run_command("sudo apt install -y libusb-1.0-0-dev", "Installing libusb")
            run_command("sudo apt install -y irecovery", "Installing irecovery")
        elif os.path.exists("/usr/bin/yum"):
            run_command("sudo yum install -y libusb1-devel", "Installing libusb")
            run_command("sudo yum install -y irecovery", "Installing irecovery")
        elif os.path.exists("/usr/bin/pacman"):
            run_command("sudo pacman -S libusb", "Installing libusb")
            run_command("sudo pacman -S irecovery", "Installing irecovery")
        else:
            print("❌ Unknown Linux distribution. Please install manually:")
            print("   - libusb-1.0-dev")
            print("   - irecovery")
    
    print()
    print("🐍 Installing Python dependencies...")
    
    # Install Python packages
    python_packages = [
        "pyirecovery",
        "libusb1", 
        "pyusb"
    ]
    
    for package in python_packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    print()
    print("🧪 Testing installation...")
    
    # Test Python imports
    test_imports = [
        ("usb.core", "PyUSB"),
        ("libusb1", "libusb1"),
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"   ✅ {name} import successful")
        except ImportError:
            print(f"   ❌ {name} import failed")
    
    # Test irecovery (optional)
    try:
        import irecovery
        print(f"   ✅ irecovery import successful")
    except ImportError:
        print(f"   ⚠️  irecovery import failed (install pyirecovery manually if needed)")
    
    print()
    print("🎉 Installation complete!")
    print()
    print("📋 Next steps:")
    print("   1. Connect your iPad in Recovery Mode")
    print("   2. Run: python src/iboot_analyzer.py")
    print("   3. Run: python boot_ipad_0000022DA6043DF7.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())