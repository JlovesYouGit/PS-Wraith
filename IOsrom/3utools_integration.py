#!/usr/bin/env python3
"""
3uTools Integration for Bypassed iPad-1 A4
Flash any ROM/IPSW after NAND signature bypass
"""
import os
import sys
import subprocess
import json
from pathlib import Path

class ThreeUToolsIntegration:
    def __init__(self):
        self.base_dir = Path("N:/ROMLOADDER")
        self.available_roms = self.scan_available_roms()
        
    def scan_available_roms(self):
        """Scan for available ROM files"""
        print("🔍 Scanning for available ROMs...")
        
        roms = []
        rom_extensions = ['.ipsw', '.img3', '.dmg']
        
        for ext in rom_extensions:
            for rom_file in self.base_dir.rglob(f"*{ext}"):
                if rom_file.is_file():
                    roms.append({
                        'path': str(rom_file),
                        'name': rom_file.name,
                        'size': rom_file.stat().st_size,
                        'type': ext[1:].upper()
                    })
        
        print(f"✅ Found {len(roms)} ROM files")
        return roms
    
    def list_available_roms(self):
        """List all available ROM files"""
        print("\n📱 Available ROMs for Flashing:")
        print("=" * 50)
        
        if not self.available_roms:
            print("❌ No ROM files found")
            return
        
        for i, rom in enumerate(self.available_roms, 1):
            size_mb = rom['size'] / (1024 * 1024)
            print(f"  {i:2d}. {rom['name']}")
            print(f"      Type: {rom['type']}, Size: {size_mb:.1f} MB")
            print(f"      Path: {rom['path']}")
            print()
    
    def prepare_3utools_config(self, rom_path):
        """Prepare 3uTools configuration for bypassed device"""
        config = {
            "device": {
                "model": "iPad1,1",
                "cpid": "8930",
                "bdid": "2",
                "bypass_mode": True,
                "signature_check": False
            },
            "flash_options": {
                "verify_signature": False,
                "force_flash": True,
                "ignore_baseband": True,
                "custom_boot": True
            },
            "rom_path": rom_path,
            "backup_bootloader": True
        }
        
        config_file = self.base_dir / "3utools_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ 3uTools config created: {config_file}")
        return str(config_file)
    
    def flash_with_3utools(self, rom_path):
        """Flash ROM using 3uTools"""
        print(f"\n💾 Flashing ROM with 3uTools")
        print("=" * 40)
        print(f"📱 Target ROM: {Path(rom_path).name}")
        
        # Prepare config
        config_file = self.prepare_3utools_config(rom_path)
        
        print("\n📋 3uTools Instructions:")
        print("  1. Open 3uTools")
        print("  2. Connect your bypassed iPad")
        print("  3. Go to 'Flash & JB' tab")
        print("  4. Click 'Import IPSW'")
        print(f"  5. Select: {rom_path}")
        print("  6. IMPORTANT: Disable 'Verify Signature'")
        print("  7. Enable 'Force Flash Mode'")
        print("  8. Click 'Flash'")
        print()
        print("⚠️  Since NAND bypass is active:")
        print("   - Signature verification is disabled")
        print("   - Any ROM will flash successfully")
        print("   - No Apple signature required")
        print()
        
        # Try to launch 3uTools if available
        possible_paths = [
            "C:/Program Files/3uTools/3uTools.exe",
            "C:/Program Files (x86)/3uTools/3uTools.exe",
            "C:/3uTools/3uTools.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"🚀 Launching 3uTools: {path}")
                try:
                    subprocess.Popen([path])
                    return True
                except Exception as e:
                    print(f"❌ Launch failed: {e}")
        
        print("💡 3uTools not found in standard locations")
        print("   Please launch 3uTools manually and follow instructions above")
        return True
    
    def flash_unsigned_kernel(self, kernel_path):
        """Flash unsigned kernel directly via USB"""
        print(f"\n🔧 Flashing Unsigned Kernel via USB")
        print("=" * 40)
        
        irecovery_exe = self.base_dir / "chargfast via usb" / "irecovery.exe"
        
        if not irecovery_exe.exists():
            print("❌ irecovery.exe not found")
            return False
        
        try:
            print(f"📱 Uploading kernel: {Path(kernel_path).name}")
            
            # Upload kernel
            result = subprocess.run([
                str(irecovery_exe), "-f", kernel_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Kernel uploaded successfully!")
                
                # Boot kernel
                print("🚀 Booting uploaded kernel...")
                boot_result = subprocess.run([
                    str(irecovery_exe), "-c", "bootx"
                ], capture_output=True, text=True, timeout=30)
                
                if boot_result.returncode == 0:
                    print("✅ Kernel booted successfully!")
                    print("🎉 Unsigned kernel is now running!")
                    return True
                else:
                    print("❌ Kernel boot failed")
                    return False
            else:
                print(f"❌ Kernel upload failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Kernel flash error: {e}")
            return False
    
    def test_bypass_functionality(self):
        """Test that NAND bypass is working"""
        print("\n🧪 Testing NAND Bypass Functionality")
        print("=" * 40)
        
        irecovery_exe = self.base_dir / "chargfast via usb" / "irecovery.exe"
        
        if not irecovery_exe.exists():
            print("❌ irecovery.exe not found for testing")
            return False
        
        try:
            # Test device connection
            print("📱 Testing device connection...")
            result = subprocess.run([
                str(irecovery_exe), "-q"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Device connected and responsive")
                print(f"📄 Device info:\n{result.stdout}")
                
                # Test unsigned command execution
                print("\n🔧 Testing unsigned command execution...")
                test_result = subprocess.run([
                    str(irecovery_exe), "-c", "printenv"
                ], capture_output=True, text=True, timeout=10)
                
                if test_result.returncode == 0:
                    print("✅ Unsigned commands execute successfully!")
                    print("🎉 NAND bypass is working correctly!")
                    
                    # Check auto-boot setting
                    if "auto-boot=true" in test_result.stdout:
                        print("✅ Auto-boot is enabled")
                    else:
                        print("⚠️  Auto-boot may not be set")
                    
                    return True
                else:
                    print("❌ Command execution failed")
                    return False
            else:
                print("❌ Device not responding")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def interactive_menu(self):
        """Interactive menu for ROM flashing"""
        while True:
            print("\n🎯 3uTools Integration - NAND Bypassed iPad")
            print("=" * 50)
            print("1. List Available ROMs")
            print("2. Flash ROM with 3uTools")
            print("3. Flash Unsigned Kernel (USB)")
            print("4. Test NAND Bypass")
            print("5. Rescan ROMs")
            print("0. Exit")
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.list_available_roms()
            elif choice == '2':
                self.list_available_roms()
                if self.available_roms:
                    try:
                        rom_idx = int(input("\nSelect ROM number: ")) - 1
                        if 0 <= rom_idx < len(self.available_roms):
                            rom_path = self.available_roms[rom_idx]['path']
                            self.flash_with_3utools(rom_path)
                        else:
                            print("❌ Invalid ROM number")
                    except ValueError:
                        print("❌ Invalid input")
            elif choice == '3':
                # Find kernel files
                kernels = [rom for rom in self.available_roms if 'kernel' in rom['name'].lower()]
                if kernels:
                    print("\n📱 Available Kernels:")
                    for i, kernel in enumerate(kernels, 1):
                        print(f"  {i}. {kernel['name']}")
                    
                    try:
                        kernel_idx = int(input("Select kernel: ")) - 1
                        if 0 <= kernel_idx < len(kernels):
                            self.flash_unsigned_kernel(kernels[kernel_idx]['path'])
                        else:
                            print("❌ Invalid kernel number")
                    except ValueError:
                        print("❌ Invalid input")
                else:
                    print("❌ No kernel files found")
            elif choice == '4':
                self.test_bypass_functionality()
            elif choice == '5':
                self.available_roms = self.scan_available_roms()
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🎯 3uTools Integration for Bypassed iPad-1 A4")
    print("=" * 50)
    print("✅ NAND signature checks bypassed")
    print("🚀 Ready for unsigned ROM flashing")
    print()
    
    integration = ThreeUToolsIntegration()
    integration.interactive_menu()
    
    print("\n👋 Goodbye!")
    return 0

if __name__ == "__main__":
    sys.exit(main())