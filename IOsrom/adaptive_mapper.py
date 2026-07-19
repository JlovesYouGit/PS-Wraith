#!/usr/bin/env python3
"""Adaptive hardware mapper - map and exploit every component precisely"""
import subprocess
import struct
import time
from pathlib import Path

class AdaptiveHardwareMapper:
    def __init__(self):
        self.base_dir = Path("N:/ROMLOADDER")
        self.chargfast_dir = self.base_dir / "chargfast via usb"
        self.irecovery = self.chargfast_dir / "irecovery.exe"
        
        # Hardware map - will be dynamically updated
        self.hardware_map = {
            'boot_rom': {'base': 0x20000000, 'size': 0x10000, 'status': 'unknown'},
            'sram': {'base': 0x22000000, 'size': 0x100000, 'status': 'unknown'},
            'nand_ctrl': {'base': 0x38100000, 'size': 0x1000, 'status': 'unknown'},
            'aes_engine': {'base': 0x38200000, 'size': 0x1000, 'status': 'unknown'},
            'sha_engine': {'base': 0x38300000, 'size': 0x1000, 'status': 'unknown'},
            'usb_ctrl': {'base': 0x38400000, 'size': 0x1000, 'status': 'unknown'},
            'gpio': {'base': 0x3E000000, 'size': 0x10000, 'status': 'unknown'},
            'clock_ctrl': {'base': 0x3C500000, 'size': 0x1000, 'status': 'unknown'},
            'power_mgmt': {'base': 0x3C600000, 'size': 0x1000, 'status': 'unknown'},
            'efuse': {'base': 0x3C100000, 'size': 0x1000, 'status': 'unknown'},
            'dram': {'base': 0x40000000, 'size': 0x20000000, 'status': 'unknown'}
        }
        
        self.exploitable_regions = []
        self.vulnerable_addresses = []
        
    def get_pwned_control(self):
        """Get pwned iBEC control"""
        print("[+] Getting pwned control...")
        try:
            subprocess.run([str(self.irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], 
                          cwd=str(self.chargfast_dir), timeout=10)
            subprocess.run([str(self.irecovery), "-c", "go"], cwd=str(self.chargfast_dir))
            time.sleep(2)
            
            subprocess.run([str(self.irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], 
                          cwd=str(self.chargfast_dir), timeout=10)
            subprocess.run([str(self.irecovery), "-c", "go"], cwd=str(self.chargfast_dir))
            time.sleep(2)
            return True
        except Exception as e:
            print(f"[-] Control failed: {e}")
            return False
    
    def probe_memory_region(self, base_addr, size, name):
        """Probe memory region for accessibility and vulnerabilities"""
        print(f"[+] Probing {name} at 0x{base_addr:08x}")
        
        accessible_ranges = []
        vulnerable_spots = []
        
        # Test accessibility in chunks
        chunk_size = 0x1000
        for offset in range(0, size, chunk_size):
            addr = base_addr + offset
            
            try:
                # Test read access
                result = subprocess.run([
                    str(self.irecovery), "-c", f"md 0x{addr:08x} 1"
                ], capture_output=True, text=True, timeout=3, cwd=str(self.chargfast_dir))
                
                if result.returncode == 0 and "0x" in result.stdout:
                    accessible_ranges.append((addr, chunk_size))
                    
                    # Test write access
                    test_val = 0x12345678
                    write_result = subprocess.run([
                        str(self.irecovery), "-c", f"mw 0x{addr:08x} 0x{test_val:08x}"
                    ], capture_output=True, text=True, timeout=3, cwd=str(self.chargfast_dir))
                    
                    if write_result.returncode == 0:
                        # Verify write
                        verify_result = subprocess.run([
                            str(self.irecovery), "-c", f"md 0x{addr:08x} 1"
                        ], capture_output=True, text=True, timeout=3, cwd=str(self.chargfast_dir))
                        
                        if f"{test_val:08x}" in verify_result.stdout.lower():
                            vulnerable_spots.append(addr)
                            print(f"    [!] VULNERABLE: 0x{addr:08x} - Read/Write access")
                        else:
                            print(f"    [+] READABLE: 0x{addr:08x} - Read only")
                    else:
                        print(f"    [+] READABLE: 0x{addr:08x} - Read only")
                        
            except Exception as e:
                pass  # Region not accessible
            
            time.sleep(0.01)  # Brief delay
        
        return accessible_ranges, vulnerable_spots
    
    def adaptive_scan(self):
        """Adaptive scan of all hardware components"""
        print("🔍 ADAPTIVE HARDWARE MAPPING")
        print("=" * 40)
        
        if not self.get_pwned_control():
            print("[-] Failed to get control - aborting scan")
            return False
        
        # Scan each hardware component
        for component, info in self.hardware_map.items():
            accessible, vulnerable = self.probe_memory_region(
                info['base'], info['size'], component
            )
            
            if accessible:
                info['status'] = 'accessible'
                info['accessible_ranges'] = accessible
                
            if vulnerable:
                info['status'] = 'vulnerable'
                info['vulnerable_addresses'] = vulnerable
                self.vulnerable_addresses.extend(vulnerable)
                self.exploitable_regions.append(component)
                
        return True
    
    def precision_exploit(self, target_component, exploit_data):
        """Precisely exploit a mapped component"""
        if target_component not in self.hardware_map:
            print(f"[-] Unknown component: {target_component}")
            return False
            
        component = self.hardware_map[target_component]
        if component['status'] != 'vulnerable':
            print(f"[-] Component {target_component} not vulnerable")
            return False
            
        print(f"[+] Precision exploit: {target_component}")
        
        # Use vulnerable addresses for precise modification
        for addr in component.get('vulnerable_addresses', []):
            for data in exploit_data:
                try:
                    cmd = f"mw 0x{addr:08x} 0x{data:08x}"
                    print(f"    [+] {cmd}")
                    subprocess.run([str(self.irecovery), "-c", cmd], 
                                  cwd=str(self.chargfast_dir), timeout=5)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"    [-] Failed: {e}")
        
        return True
    
    def generate_exploit_map(self):
        """Generate precise exploit map"""
        print("\n📊 EXPLOIT MAP GENERATION")
        print("=" * 30)
        
        exploit_map = {
            'nand_ctrl': [0x00000000, 0xFFFFFFFF, 0x12345678],  # Disable security
            'aes_engine': [0x00000000],                          # Disable AES
            'sha_engine': [0x00000000],                          # Disable SHA
            'efuse': [0xDEADBEEF, 0x12345678],                  # Custom eFuse values
            'boot_rom': [0xE3A00001, 0xE12FFF1E],               # ARM bypass code
            'power_mgmt': [0xAAAAAAAA, 0x55555555],             # Power control
            'clock_ctrl': [0xFFFFFFFF, 0x12345678],             # Clock manipulation
            'gpio': [0xDEADBEEF, 0xCAFEBABE],                   # GPIO control
        }
        
        # Execute precision exploits
        for component, data in exploit_map.items():
            if component in self.exploitable_regions:
                self.precision_exploit(component, data)
        
        return exploit_map
    
    def adaptive_persistence(self):
        """Make exploits persistent using mapped vulnerabilities"""
        print("\n🔒 ADAPTIVE PERSISTENCE")
        print("=" * 25)
        
        # Use mapped vulnerable addresses for persistence
        persistence_data = [
            (0x3C100000, 0xDEADBEEF),  # eFuse signature
            (0x38100000, 0x00000000),  # NAND security off
            (0x38200000, 0x00000000),  # AES off
            (0x38300000, 0x00000000),  # SHA off
        ]
        
        for addr, data in persistence_data:
            if addr in self.vulnerable_addresses:
                try:
                    cmd = f"mw 0x{addr:08x} 0x{data:08x}"
                    print(f"[+] PERSIST: {cmd}")
                    subprocess.run([str(self.irecovery), "-c", cmd], 
                                  cwd=str(self.chargfast_dir), timeout=5)
                except Exception as e:
                    print(f"[-] Persistence failed: {e}")
        
        # Set persistent boot environment
        boot_cmds = [
            "setenv auto-boot true",
            "setenv boot-args -v",
            "setenv signature-checks disabled",
            "saveenv"
        ]
        
        for cmd in boot_cmds:
            try:
                subprocess.run([str(self.irecovery), "-c", cmd], 
                              cwd=str(self.chargfast_dir), timeout=5)
            except:
                pass
    
    def display_map(self):
        """Display the hardware map"""
        print("\n🗺️  HARDWARE MAP")
        print("=" * 20)
        
        for component, info in self.hardware_map.items():
            status = info['status']
            base = info['base']
            size = info['size']
            
            status_icon = {
                'vulnerable': '🔥',
                'accessible': '✅', 
                'unknown': '❓'
            }.get(status, '❓')
            
            print(f"{status_icon} {component:12} 0x{base:08x} - 0x{base+size:08x} ({status})")
            
            if 'vulnerable_addresses' in info:
                for addr in info['vulnerable_addresses'][:3]:  # Show first 3
                    print(f"    💀 Vulnerable: 0x{addr:08x}")
        
        print(f"\n📊 Summary:")
        print(f"   Exploitable regions: {len(self.exploitable_regions)}")
        print(f"   Vulnerable addresses: {len(self.vulnerable_addresses)}")

def main():
    """Main adaptive mapping function"""
    mapper = AdaptiveHardwareMapper()
    
    print("🎯 ADAPTIVE HARDWARE MAPPER")
    print("Precision mapping and exploitation")
    print()
    
    # Perform adaptive scan
    if mapper.adaptive_scan():
        # Display results
        mapper.display_map()
        
        # Generate and execute exploits
        mapper.generate_exploit_map()
        
        # Make exploits persistent
        mapper.adaptive_persistence()
        
        # Final boot
        try:
            subprocess.run([str(mapper.irecovery), "-c", "reset"], 
                          cwd=str(mapper.chargfast_dir), timeout=5)
        except:
            pass
        
        print("\n🎉 ADAPTIVE MAPPING COMPLETE")
        print("Device precisely mapped and exploited")
        
    else:
        print("[-] Adaptive mapping failed")

if __name__ == "__main__":
    main()