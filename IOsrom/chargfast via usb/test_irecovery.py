#!/usr/bin/env python
"""
Simple test to verify irecovery functionality.
"""
import subprocess
import sys
from pathlib import Path

def test_irecovery():
    """Test if irecovery is working."""
    print("Testing irecovery functionality...")
    
    # Check if irecovery.exe exists
    irecovery_path = Path("irecovery.exe")
    if not irecovery_path.exists():
        print("❌ irecovery.exe not found in current directory")
        print("📥 Download from: https://github.com/libimobiledevice-win32/imobiledevice-net/releases")
        return False
    
    print("✅ irecovery.exe found")
    
    # Test irecovery connection
    try:
        print("🔍 Testing device connection...")
        result = subprocess.run([
            "irecovery.exe", "-q"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ iOS device found in recovery mode!")
            print("📱 Device information:")
            for line in result.stdout.split('\n'):
                if line.strip() and ':' in line:
                    print(f"   {line.strip()}")
            
            print("\n🔧 Ready to fix auto-boot issue!")
            print("Run the following commands:")
            print("   irecovery.exe -c \"setenv auto-boot true\"")
            print("   irecovery.exe -c \"saveenv\"") 
            print("   irecovery.exe -c \"reboot\"")
            
            return True
        else:
            print("ℹ️  No iOS device in recovery mode detected")
            print("💡 This is normal if your device is booting normally")
            print("🔄 To put device in recovery mode:")
            print("   1. Connect device via USB")
            print("   2. Hold Power + Home buttons (or Volume Down on newer devices)")
            print("   3. Wait for recovery mode screen")
            
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Connection timeout")
        return False
    except FileNotFoundError:
        print("❌ irecovery.exe not found or not executable")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🍎 iOS Recovery Test")
    print("=" * 30)
    test_irecovery()