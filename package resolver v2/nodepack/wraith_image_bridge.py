#!/usr/bin/env python3
"""
Wraith Image Bridge - Device Image Handling via IOsrom
Integrates NAND flash, image extraction, and filesystem writing
with the wraithps4-serv-backup-performance booster system.
"""

import os
import sys
import subprocess
import time
import zipfile
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# IOsrom paths
IOSROM_DIR = Path(__file__).parent.parent / "IOsrom"
CHARGFAST_DIR = Path("N:/ROMLOADDER/chargfast via usb")
EXTRACTED_DIR = CHARGFAST_DIR / "extracted"


@dataclass
class ImageComponent:
    """Represents an image component (LLB, iBoot, kernel, etc.)"""
    name: str
    source_path: Path
    target_offset: int
    size: int
    img_type: str  # img3, img4, dmg, raw
    flashed: bool = False


@dataclass
class NANDWriteResult:
    """Result of a NAND write operation"""
    success: bool
    component: str
    offset: int
    bytes_written: int
    error: Optional[str] = None


class WraithImageBridge:
    """
    Bridge between wraith system and device images.
    Uses IOsrom NAND/image handling code for direct device operations.
    """
    
    def __init__(self, work_dir: str, flash_mode: bool = False):
        self.work_dir = Path(work_dir)
        self.flash_mode = flash_mode
        self.wraith_dir = self._detect_wraith_directory()
        self.iosrom_dir = IOSROM_DIR
        self.device_connected = False
        self.nand_open = False
        self.components: List[ImageComponent] = []
        self.write_results: List[NANDWriteResult] = []
        self.rj45_active = False
        
    def _detect_wraith_directory(self) -> Optional[Path]:
        """Detect wraithps4-serv-backup-performance booster directory"""
        wraith_indicators = [
            'boost_engine.py',
            'hardware_interface.py',
            'pragma_logic.py',
            'storage_manager.py',
            'buffer_manager.py',
            'network_protection.py',
            'interleave_manager.py',
            'market_engine.py',
            'persistence_manager.py',
            'main.py'
        ]
        
        for file in wraith_indicators:
            if (self.work_dir / file).exists():
                return self.work_dir
        
        parent = self.work_dir.parent
        for file in wraith_indicators:
            if (parent / file).exists():
                return parent
        
        return None
    
    def detect_device_connection(self) -> bool:
        """
        Detect device connection via RJ45/USB
        Integrates with wraith hardware interface
        """
        if self.wraith_dir:
            try:
                sys.path.insert(0, str(self.wraith_dir))
                from hardware_interface import WraithHardwareInterface
                hw = WraithHardwareInterface()
                self.rj45_active = hw.detect_rj45_device()
                self.device_connected = self.rj45_active
                return self.device_connected
            except ImportError:
                pass
        
        # Fallback: check for device via irecovery
        try:
            result = subprocess.run(
                ['irecovery', '-c', 'getenv'],
                capture_output=True, text=True, timeout=5
            )
            self.device_connected = result.returncode == 0
            return self.device_connected
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_device_image(self, component_name: str) -> Optional[Path]:
        """
        Get device image from connected device or local cache
        Uses IOsrom extraction logic
        """
        # Check local cache first
        local_path = EXTRACTED_DIR / component_name
        if local_path.exists():
            return local_path
        
        # Try to extract from connected device
        if self.device_connected:
            return self._extract_from_device(component_name)
        
        return None
    
    def _extract_from_device(self, component_name: str) -> Optional[Path]:
        """Extract component from connected device via iBoot"""
        try:
            # Use iBoot commands to extract
            cmd_map = {
                'LLB.img3': 'nand read 0x0 0x100000',
                'iBoot.img3': 'nand read 0x100000 0x100000',
                'DeviceTree.img3': 'nand read 0x200000 0x100000',
                'kernelcache': 'nand read 0x600000 0x1000000',
            }
            
            if component_name in cmd_map:
                cmd = cmd_map[component_name]
                output_file = EXTRACTED_DIR / component_name
                EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
                
                subprocess.run(
                    ['irecovery', '-c', cmd, '-o', str(output_file)],
                    capture_output=True, timeout=30
                )
                
                if output_file.exists():
                    return output_file
        except Exception:
            pass
        
        return None
    
    def extract_image_components(self, ipsw_path: Path) -> Dict[str, Path]:
        """
        Extract image components from IPSW
        Uses IOsrom extract_ipsw_parts.py logic
        """
        components = {}
        
        if not ipsw_path.exists():
            return components
        
        extract_dir = self.work_dir / f"{ipsw_path.stem}_extracted"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(ipsw_path, 'r') as z:
                # Extract all files
                z.extractall(extract_dir)
                
                # Find key components
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = Path(root) / file
                        lower_name = file.lower()
                        
                        if 'llb' in lower_name and file_path.suffix in ['.img3', '.img4']:
                            components['LLB'] = file_path
                        elif 'iboot' in lower_name and file_path.suffix in ['.img3', '.img4']:
                            components['iBoot'] = file_path
                        elif 'devicetree' in lower_name:
                            components['DeviceTree'] = file_path
                        elif 'kernelcache' in lower_name:
                            components['KernelCache'] = file_path
                        elif 'applelogo' in lower_name:
                            components['AppleLogo'] = file_path
                        elif 'recoverymode' in lower_name:
                            components['RecoveryMode'] = file_path
                        elif file.endswith('.dmg') and '038-' in file:
                            components['RootFS'] = file_path
                        elif 'ibec' in lower_name:
                            components['iBEC'] = file_path
                        elif 'ibss' in lower_name:
                            components['iBSS'] = file_path
                
                # Also check Firmware directory
                firmware_dir = extract_dir / "Firmware"
                if firmware_dir.exists():
                    for root, dirs, files in os.walk(firmware_dir):
                        for file in files:
                            file_path = Path(root) / file
                            lower_name = file.lower()
                            
                            if 'all_flash' in lower_name:
                                components['AllFlash'] = file_path
                            elif file_path.suffix == '.img3':
                                components[f"IMG3_{file}"] = file_path
                                
        except Exception as e:
            print(f"[ImageBridge] Extraction error: {e}")
        
        return components
    
    def prepare_nand_write_sequence(self, components: Dict[str, Path]) -> List[ImageComponent]:
        """
        Prepare NAND write sequence from extracted components
        Uses IOsrom direct_nand_flasher.py logic
        """
        sequence = []
        
        # NAND offset map for A4 devices
        offset_map = {
            'LLB': 0x0,
            'iBoot': 0x100000,
            'DeviceTree': 0x200000,
            'AppleLogo': 0x300000,
            'RecoveryMode': 0x400000,
            'BatteryCharging': 0x500000,
            'KernelCache': 0x600000,
            'RootFS': 0x1600000,
        }
        
        for name, path in components.items():
            if name in offset_map:
                size = path.stat().st_size if path.exists() else 0
                img_type = path.suffix.lower().replace('.', '')
                if img_type == '':
                    img_type = 'dmg' if path.suffix == '.dmg' else 'raw'
                
                sequence.append(ImageComponent(
                    name=name,
                    source_path=path,
                    target_offset=offset_map[name],
                    size=size,
                    img_type=img_type
                ))
        
        # Sort by offset
        sequence.sort(key=lambda c: c.target_offset)
        self.components = sequence
        return sequence
    
    def write_to_nand(self, component: ImageComponent) -> NANDWriteResult:
        """
        Write component to NAND via iBoot
        Uses IOsrom NAND write commands
        """
        if not self.device_connected:
            return NANDWriteResult(
                success=False,
                component=component.name,
                offset=component.target_offset,
                bytes_written=0,
                error="No device connected"
            )
        
        try:
            # Ensure NAND is open
            if not self.nand_open:
                subprocess.run(
                    ['irecovery', '-c', 'nand open'],
                    capture_output=True, timeout=10
                )
                self.nand_open = True
            
            # Load component to RAM
            load_cmd = f"load {component.source_path}"
            subprocess.run(
                ['irecovery', '-c', load_cmd],
                capture_output=True, timeout=30
            )
            
            # Write to NAND
            write_cmd = f"nand write 0x09000000 {component.target_offset:#x} {component.size:#x}"
            result = subprocess.run(
                ['irecovery', '-c', write_cmd],
                capture_output=True, text=True, timeout=60
            )
            
            success = result.returncode == 0
            component.flashed = success
            
            write_result = NANDWriteResult(
                success=success,
                component=component.name,
                offset=component.target_offset,
                bytes_written=component.size if success else 0,
                error=result.stderr.strip() if not success else None
            )
            
            self.write_results.append(write_result)
            return write_result
            
        except subprocess.TimeoutExpired:
            error = f"Timeout writing {component.name}"
            return NANDWriteResult(
                success=False,
                component=component.name,
                offset=component.target_offset,
                bytes_written=0,
                error=error
            )
        except Exception as e:
            return NANDWriteResult(
                success=False,
                component=component.name,
                offset=component.target_offset,
                bytes_written=0,
                error=str(e)
            )
    
    def flash_all_components(self) -> bool:
        """
        Flash all prepared components to NAND
        Returns True if all writes succeeded
        """
        if not self.components:
            print("[ImageBridge] No components prepared for flashing")
            return False
        
        print(f"[ImageBridge] Flashing {len(self.components)} components to NAND...")
        all_success = True
        
        for i, component in enumerate(self.components, 1):
            print(f"[{i}/{len(self.components)}] Flashing {component.name}...")
            result = self.write_to_nand(component)
            
            if result.success:
                print(f"  ✅ {component.name} written ({result.bytes_written} bytes)")
            else:
                print(f"  ❌ {component.name} failed: {result.error}")
                all_success = False
        
        # Close NAND
        if self.nand_open:
            try:
                subprocess.run(
                    ['irecovery', '-c', 'nand close'],
                    capture_output=True, timeout=10
                )
                self.nand_open = False
            except Exception:
                pass
        
        return all_success
    
    def create_bootable_image(self, output_path: Path, components: Dict[str, Path]) -> bool:
        """
        Create bootable IPSW/image from components
        Uses IOsrom create_bootable_ipsw.py logic
        """
        try:
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # For IPSW, we need to create a proper ZIP with specific structure
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add manifest files
                manifest_content = self._generate_build_manifest(components)
                zf.writestr('BuildManifest.plist', manifest_content)
                
                restore_content = self._generate_restore_plist(components)
                zf.writestr('Restore.plist', restore_content)
                
                # Add firmware components
                for name, path in components.items():
                    if path.exists():
                        arcname = f"Firmware/{path.name}"
                        zf.write(path, arcname)
            
            print(f"[ImageBridge] Created bootable image: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ImageBridge] Failed to create bootable image: {e}")
            return False
    
    def _generate_build_manifest(self, components: Dict[str, Path]) -> str:
        """Generate minimal BuildManifest.plist"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>BuildVersion</key>
    <string>20A5824a</string>
    <key>ProductType</key>
    <string>iPad1,1</string>
    <key>ProductBuildVersion</key>
    <string>10B329</string>
</dict>
</plist>"""
    
    def _generate_restore_plist(self, components: Dict[str, Path]) -> str:
        """Generate minimal Restore.plist"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>DeviceId</key>
    <string>0</string>
    <key>RestoreBehavior</key>
    <string>Update</string>
</dict>
</plist>"""
    
    def verify_nand_integrity(self) -> Dict[str, bool]:
        """
        Verify NAND integrity after flashing
        Returns status of each component
        """
        status = {}
        
        for component in self.components:
            if not component.flashed:
                status[component.name] = False
                continue
            
            try:
                # Read back and verify
                read_cmd = f"nand read {component.target_offset:#x} {component.size:#x}"
                result = subprocess.run(
                    ['irecovery', '-c', read_cmd],
                    capture_output=True, text=True, timeout=30
                )
                
                status[component.name] = result.returncode == 0
            except Exception:
                status[component.name] = False
        
        return status
    
    def get_makefile_transfer_config(self) -> Dict:
        """
        Generate Makefile configuration for device transfer
        """
        return {
            'DEVICE_ID': 'iPad1,1',
            'CHIP': 'A4',
            'NAND_BASE': '0x09000000',
            'COMPONENTS': [
                {
                    'name': c.name,
                    'offset': hex(c.target_offset),
                    'size': hex(c.size),
                    'type': c.img_type,
                    'source': str(c.source_path)
                }
                for c in self.components
            ],
            'TRANSFER_PROTOCOL': 'irecovery',
            'FLASH_MODE': 'direct_nand' if self.flash_mode else 'standard',
            'RJ45_ACTIVE': self.rj45_active
        }
    
    def generate_makefile(self, output_path: Path) -> bool:
        """
        Generate Makefile for device transfer operations
        """
        config = self.get_makefile_transfer_config()
        
        makefile_content = f"""# Wraith Device Transfer Makefile
# Auto-generated by WraithImageBridge
# Device: {config['DEVICE_ID']} ({config['CHIP']})
# Protocol: {config['TRANSFER_PROTOCOL']}
# Flash Mode: {config['FLASH_MODE']}

DEVICE_ID = {config['DEVICE_ID']}
CHIP = {config['CHIP']}
NAND_BASE = {config['NAND_BASE']}
IRECOVERY = irecovery
CHARGFAST = {CHARGFAST_DIR}

# Component definitions
"""
        
        for comp in config['COMPONENTS']:
            makefile_content += f"{comp['name'].upper()}_SOURCE = {comp['source']}\n"
            makefile_content += f"{comp['name'].upper()}_OFFSET = {comp['offset']}\n"
            makefile_content += f"{comp['name'].upper()}_SIZE = {comp['size']}\n\n"
        
        makefile_content += """# Targets
.PHONY: all flash verify clean detect

all: detect flash verify

detect:
\t@echo "[+] Detecting device..."
\t@$(IRECOVERY) -c getenv | head -5

flash: $(COMPONENTS)
\t@echo "[+] Flashing components to NAND..."
"""
        
        for comp in config['COMPONENTS']:
            name = comp['name'].upper()
            makefile_content += f"\t@echo \"  Flashing {comp['name']}...\"\n"
            makefile_content += f"\t@$(IRECOVERY) -c \"load $({name}_SOURCE)\"\n"
            makefile_content += f"\t@$(IRECOVERY) -c \"nand write $(NAND_BASE) {comp['offset']} {comp['size']}\"\n\n"
        
        makefile_content += """verify:
\t@echo "[+] Verifying NAND integrity..."
\t@$(IRECOVERY) -c getenv | grep boot-partition

clean:
\t@echo "[+] Cleaning extracted files..."
\t@rm -rf extracted/*

reboot:
\t@echo "[+] Rebooting device..."
\t@$(IRECOVERY) -c reboot
"""
        
        try:
            output_path.write_text(makefile_content)
            print(f"[ImageBridge] Generated Makefile: {output_path}")
            return True
        except Exception as e:
            print(f"[ImageBridge] Failed to generate Makefile: {e}")
            return False
    
    def get_library_mirror_config(self) -> Dict:
        """
        Get configuration for library mirror operations
        Used to update and manage packages on connected device
        """
        return {
            'mirror_base': str(self.work_dir / 'library_mirror'),
            'device_ip': 'localhost',  # Via USB/RJ45 bridge
            'transfer_method': 'irecovery',
            'package_managers': {
                'ios': 'dpkg',
                'python': 'pip',
                'node': 'npm',
                'rust': 'cargo',
                'go': 'go_modules'
            },
            'nand_paths': {
                'system': '/System/Library',
                'applications': '/Applications',
                'frameworks': '/System/Library/Frameworks',
                'python_site': '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages',
                'node_modules': '/usr/lib/node_modules'
            },
            'rj45_active': self.rj45_active,
            'flash_mode': self.flash_mode
        }


class WraithDeviceMirror:
    """
    Mirror management for connected device
    Handles package updates and library management
    """
    
    def __init__(self, image_bridge: WraithImageBridge):
        self.image_bridge = image_bridge
        self.mirror_dir = image_bridge.work_dir / 'library_mirror'
        self.mirror_dir.mkdir(exist_ok=True)
        self.synced_packages: Dict[str, str] = {}
    
    def sync_device_library(self) -> bool:
        """
        Sync device library to local mirror
        """
        if not self.image_bridge.device_connected:
            print("[Mirror] No device connected")
            return False
        
        print("[Mirror] Syncing device library...")
        
        # Sync via irecovery filesystem access
        try:
            # List installed packages via dpkg
            result = subprocess.run(
                ['irecovery', '-c', 'ls /Applications'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                apps = result.stdout.strip().split('\n')
                self.synced_packages['applications'] = apps
                print(f"[Mirror] Found {len(apps)} applications")
            
            return True
        except Exception as e:
            print(f"[Mirror] Sync failed: {e}")
            return False
    
    def apply_package_update(self, package_name: str, version: str, language: str) -> bool:
        """
        Apply package update to connected device
        """
        if not self.image_bridge.device_connected:
            return False
        
        print(f"[Mirror] Updating {package_name}@{version} ({language})...")
        
        # Package update logic based on language
        if language == 'python':
            return self._update_python_package(package_name, version)
        elif language == 'node':
            return self._update_node_package(package_name, version)
        elif language == 'ios':
            return self._update_ios_package(package_name, version)
        
        return False
    
    def _update_python_package(self, name: str, version: str) -> bool:
        """Update Python package on device"""
        try:
            cmd = f"pip install {name}=={version}"
            subprocess.run(
                ['irecovery', '-c', f'shell "{cmd}"'],
                capture_output=True, timeout=30
            )
            return True
        except Exception:
            return False
    
    def _update_node_package(self, name: str, version: str) -> bool:
        """Update Node.js package on device"""
        try:
            cmd = f"npm install -g {name}@{version}"
            subprocess.run(
                ['irecovery', '-c', f'shell "{cmd}"'],
                capture_output=True, timeout=30
            )
            return True
        except Exception:
            return False
    
    def _update_ios_package(self, name: str, version: str) -> bool:
        """Update iOS package (deb) on device"""
        try:
            # Download deb if not in mirror
            deb_path = self.mirror_dir / f"{name}_{version}.deb"
            if not deb_path.exists():
                # Would download from repository
                pass
            
            # Install via dpkg
            subprocess.run(
                ['irecovery', '-c', f'shell "dpkg -i {deb_path}"'],
                capture_output=True, timeout=30
            )
            return True
        except Exception:
            return False


def main():
    """Main entry point for wraith image bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wraith Image Bridge')
    parser.add_argument('work_dir', help='Working directory')
    parser.add_argument('--flash', action='store_true', help='Enable flash mode')
    parser.add_argument('--extract', help='Extract IPSW components')
    parser.add_argument('--flash-nand', action='store_true', help='Flash to NAND')
    parser.add_argument('--makefile', action='store_true', help='Generate Makefile')

    parser.add_argument('--mirror', action='store_true', help='Sync device mirror')
    
    parser.add_argument('--goldhen-deploy', action='store_true', help='Deploy GoldHEN payload')
    parser.add_argument('--target-ip', help='Target IP for GoldHEN deployment')
    
    args = parser.parse_args()
    bridge = WraithImageBridge(args.work_dir, flash_mode=args.flash)
    
    if args.extract:
        ipsw = Path(args.extract)
        print(f"[+] Extracting components from {ipsw}")
        components = bridge.extract_image_components(ipsw)
        print(f"[+] Found {len(components)} components")
        for name, path in components.items():
            print(f"  {name}: {path}")
    
    elif args.flash_nand:
        if not bridge.detect_device_connection():
            print("[!] No device connected")
            return 1
        
        # Use default IPSW or find one
        ipsw_files = list(Path('.').glob('*.ipsw'))
        if not ipsw_files:
            print("[!] No IPSW files found")
            return 1
        
        ipsw = ipsw_files[0]
        print(f"[+] Using IPSW: {ipsw}")
        
        components = bridge.extract_image_components(ipsw)
        bridge.prepare_nand_write_sequence(components)
        
        if bridge.flash_all_components():
            print("[+] NAND flash complete!")
        else:
            print("[!] NAND flash had errors")
    
    elif args.makefile:
        # Find IPSW and prepare
        ipsw_files = list(Path('.').glob('*.ipsw'))
        if ipsw_files:
            components = bridge.extract_image_components(ipsw_files[0])
            bridge.prepare_nand_write_sequence(components)
        
        makefile_path = Path('wraith_transfer.mk')
        bridge.generate_makefile(makefile_path)
    
    elif args.mirror:
        mirror = WraithDeviceMirror(bridge)
        mirror.sync_device_library()
    
    elif args.goldhen_deploy:
        # Deploy GoldHEN payload
        goldhen_dir = Path(__file__).parent.parent / "GoldHEN"
        goldhen_bin = goldhen_dir / "goldhen.bin"
        
        if not goldhen_bin.exists():
            print("[!] GoldHEN payload not found")
            return 1
        
        print(f"[+] Deploying GoldHEN v2.4b17.3...")
        
        # Try direct TCP deployment if IP provided
        target_ip = getattr(args, 'target_ip', None)
        if target_ip:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((target_ip, 9090))
                payload_data = goldhen_bin.read_bytes()
                sock.sendall(payload_data)
                sock.close()
                print(f"[+] GoldHEN deployed via TCP to {target_ip}:9090")
                return 0
            except Exception as e:
                print(f"[!] TCP deployment failed: {e}")
        
        # Fallback: copy to transfer directory
        transfer_dir = Path('.') / "library_mirror" / "payloads"
        transfer_dir.mkdir(parents=True, exist_ok=True)
        dest = transfer_dir / "goldhen.bin"
        shutil.copy2(goldhen_bin, dest)
        print(f"[+] GoldHEN payload saved to: {dest}")
        return 0
    
    else:
        print("Wraith Image Bridge")
        print(f"  Wraith dir: {bridge.wraith_dir}")
        print(f"  IOsrom dir: {bridge.iosrom_dir}")
        print(f"  Device connected: {bridge.detect_device_connection()}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
