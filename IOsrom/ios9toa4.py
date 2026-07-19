#!/usr/bin/env python3
"""
iOS9toA4 - Unified Backend Architecture
Complete firmware downgrade pipeline from A5 to A4 compatibility
"""
import os
import sys
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict

# Import all tools
from img4tool import IMG4Tool
from img3tool import IMG3Tool
from ipsw_tool import IPSWTool
from lzss_tool import decompress_lzss
from kernelcache_a4_patcher import KernelPatcher
import kernel_patches
import iboot_patches
import devicetree_patches

@dataclass
class FirmwareComponent:
    """Represents a firmware component"""
    name: str
    path: str
    extracted_path: Optional[str] = None
    patched_path: Optional[str] = None
    component_type: str = "unknown"

class iOS9toA4Backend:
    """Unified backend for iOS9toA4 firmware conversion"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        
        # Initialize tools
        self.img4_tool = IMG4Tool()
        self.img3_tool = IMG3Tool()
        self.ipsw_tool = IPSWTool()
        
        # Component tracking
        self.components: Dict[str, FirmwareComponent] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def extract_ipsw(self, ipsw_path: str) -> bool:
        """Extract IPSW and catalog components"""
        try:
            extract_dir = self.workspace / "extracted"
            self.logger.info(f"Extracting IPSW: {ipsw_path}")
            self.ipsw_tool.extract_all(ipsw_path, str(extract_dir))
            
            # Catalog components
            self._catalog_components(extract_dir)
            return True
            
        except Exception as e:
            self.logger.error(f"IPSW extraction failed: {e}")
            return False
    
    def _catalog_components(self, extract_dir: Path):
        """Catalog all firmware components"""
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = Path(root) / file
                
                if 'kernelcache' in file.lower():
                    self.components['kernelcache'] = FirmwareComponent(
                        name='kernelcache',
                        path=str(file_path),
                        component_type='kernel'
                    )
                elif 'iboot' in file.lower():
                    self.components['iboot'] = FirmwareComponent(
                        name='iboot',
                        path=str(file_path),
                        component_type='bootloader'
                    )
                elif 'devicetree' in file.lower():
                    self.components['devicetree'] = FirmwareComponent(
                        name='devicetree',
                        path=str(file_path),
                        component_type='devicetree'
                    )
    
    def extract_component(self, component_name: str) -> bool:
        """Extract a specific component"""
        if component_name not in self.components:
            self.logger.error(f"Component not found: {component_name}")
            return False
        
        component = self.components[component_name]
        output_path = str(self.workspace / f"{component_name}.dec")
        
        try:
            self.logger.info(f"Extracting {component_name}")
            
            # Auto-detect format and extract
            if self._is_img3_format(component.path):
                self.img3_tool.extract(component.path, output_path)
            else:
                try:
                    self.img4_tool.extract(component.path, output_path)
                except ValueError:
                    # Fallback to IMG3
                    self.img3_tool.extract(component.path, output_path)
            
            component.extracted_path = output_path
            
            # Handle LZSS compression for kernelcache
            if component_name == 'kernelcache':
                self._decompress_if_needed(component)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract {component_name}: {e}")
            return False
    
    def _is_img3_format(self, file_path: str) -> bool:
        """Check if file is IMG3 format"""
        return file_path.endswith('.img3') or 'k93' in file_path
    
    def _decompress_if_needed(self, component: FirmwareComponent):
        """Decompress LZSS if needed"""
        with open(component.extracted_path, 'rb') as f:
            data = f.read()
        
        if data.startswith(b'complzss'):
            self.logger.info("Decompressing LZSS...")
            decompressed = decompress_lzss(data)
            lzss_path = component.extracted_path + '.lzss'
            
            with open(lzss_path, 'wb') as f:
                f.write(decompressed)
            
            component.extracted_path = lzss_path
    
    def patch_component(self, component_name: str) -> bool:
        """Apply A4 compatibility patches to component"""
        if component_name not in self.components:
            self.logger.error(f"Component not found: {component_name}")
            return False
        
        component = self.components[component_name]
        if not component.extracted_path:
            self.logger.error(f"Component not extracted: {component_name}")
            return False
        
        try:
            self.logger.info(f"Patching {component_name} for A4 compatibility")
            
            if component_name == 'kernelcache':
                patcher = KernelPatcher(component.extracted_path)
                patcher.apply_all_patches()
                patcher.close()
                component.patched_path = component.extracted_path
                
            elif component_name == 'iboot':
                iboot_patches.patch_iboot(component.extracted_path)
                component.patched_path = component.extracted_path + '.patched'
                
            elif component_name == 'devicetree':
                devicetree_patches.patch_devicetree(component.extracted_path)
                component.patched_path = component.extracted_path + '.patched'
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to patch {component_name}: {e}")
            return False
    
    def rebuild_ipsw(self, output_path: str) -> bool:
        """Rebuild IPSW with patched components"""
        try:
            self.logger.info("Rebuilding IPSW with A4 patches...")
            
            # Create new IPSW structure
            rebuild_dir = self.workspace / "rebuild"
            rebuild_dir.mkdir(exist_ok=True)
            
            # Copy original structure
            extract_dir = self.workspace / "extracted"
            import shutil
            shutil.copytree(extract_dir, rebuild_dir, dirs_exist_ok=True)
            
            # Fix BuildManifest.plist for device compatibility
            manifest_path = rebuild_dir / "BuildManifest.plist"
            if manifest_path.exists():
                self._fix_buildmanifest(str(manifest_path))
            
            # Replace patched components
            for name, component in self.components.items():
                if component.patched_path and os.path.exists(component.patched_path):
                    # Rebuild component into IMG format
                    rebuilt_path = str(rebuild_dir / Path(component.path).name)
                    
                    if self._is_img3_format(component.path):
                        # For IMG3, just copy the patched file
                        shutil.copy2(component.patched_path, rebuilt_path)
                    else:
                        # For IMG4, rebuild the container
                        self.img4_tool.create(component.patched_path, rebuilt_path)
            
            # Create final IPSW
            shutil.make_archive(output_path.replace('.ipsw', ''), 'zip', rebuild_dir)
            os.rename(output_path.replace('.ipsw', '') + '.zip', output_path)
            
            self.logger.info(f"Rebuilt IPSW: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"IPSW rebuild failed: {e}")
            return False
    
    def run_complete_pipeline(self, ipsw_path: str, output_path: str, use_limera1n: bool = False) -> bool:
        """Run complete iOS9toA4 conversion pipeline"""
        self.logger.info("Starting iOS9toA4 complete pipeline")
        
        # Step 1: Extract IPSW
        if not self.extract_ipsw(ipsw_path):
            return False
        
        # Step 2: Extract components
        for component_name in ['kernelcache', 'iboot', 'devicetree']:
            if component_name in self.components:
                if not self.extract_component(component_name):
                    self.logger.warning(f"Failed to extract {component_name}")
        
        # Step 3: Patch components
        for component_name in ['kernelcache', 'iboot', 'devicetree']:
            if component_name in self.components:
                if not self.patch_component(component_name):
                    self.logger.warning(f"Failed to patch {component_name}")
        
        # Step 4: Rebuild IPSW
        if not self.rebuild_ipsw(output_path):
            return False
        
        # Step 5: Flash with limera1n if requested
        if use_limera1n:
            self.logger.info("Flashing with limera1n exploit...")
            return self._flash_with_limera1n(output_path)
        
        self.logger.info("iOS9toA4 pipeline completed successfully!")
        self.logger.info(f"Flash manually or use: python limera1n_flash.py {output_path}")
        return True
    
    def get_status(self) -> Dict:
        """Get current pipeline status"""
        status = {
            'workspace': str(self.workspace),
            'components': {}
        }
        
        for name, component in self.components.items():
            status['components'][name] = {
                'found': True,
                'extracted': component.extracted_path is not None,
                'patched': component.patched_path is not None,
                'type': component.component_type
            }
        
        return status
    
    def _flash_with_limera1n(self, ipsw_path: str) -> bool:
        """Flash IPSW using limera1n exploit"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, 'limera1n_flash.py', ipsw_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("limera1n flash completed")
                return True
            else:
                self.logger.error(f"limera1n flash failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"limera1n integration failed: {e}")
            return False
    
    def _fix_buildmanifest(self, manifest_path: str):
        """Fix BuildManifest.plist for A4 device compatibility"""
        try:
            import shutil
            # Backup original
            shutil.copy2(manifest_path, manifest_path + ".backup")
            
            # Read and do text replacements
            with open(manifest_path, 'rb') as f:
                data = f.read()
            
            # Simple byte replacements to avoid plist corruption
            data = data.replace(b'iPad2,1', b'iPad1,1')
            data = data.replace(b'iPad2,2', b'iPad1,1')
            data = data.replace(b'iPad2,3', b'iPad1,1')
            data = data.replace(b'k93ap', b'k48ap')  # Board config
            
            with open(manifest_path, 'wb') as f:
                f.write(data)
            
            self.logger.info("Fixed BuildManifest.plist for iPad1,1 compatibility")
            
        except Exception as e:
            # Restore backup if fix failed
            try:
                shutil.copy2(manifest_path + ".backup", manifest_path)
            except:
                pass
            self.logger.warning(f"Failed to fix BuildManifest: {e}")

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python ios9toa4.py <input.ipsw> <output.ipsw> [--limera1n|--redsn0w|--sn0wbreeze]")
        print("       python ios9toa4.py --status")
        sys.exit(1)
    
    if sys.argv[1] == '--status':
        backend = iOS9toA4Backend()
        status = backend.get_status()
        print(f"Workspace: {status['workspace']}")
        if status['components']:
            for name, info in status['components'].items():
                print(f"  {name}: extracted={info['extracted']}, patched={info['patched']}")
        else:
            print("  No components found")
        return
    
    if len(sys.argv) < 3:
        print("Usage: python ios9toa4.py <input.ipsw> <output.ipsw> [--limera1n|--redsn0w|--sn0wbreeze]")
        sys.exit(1)
    
    input_ipsw = sys.argv[1]
    output_ipsw = sys.argv[2]
    use_limera1n = '--limera1n' in sys.argv
    use_redsn0w = '--redsn0w' in sys.argv
    use_sn0wbreeze = '--sn0wbreeze' in sys.argv
    
    if not os.path.exists(input_ipsw):
        print(f"Error: Input IPSW not found: {input_ipsw}")
        sys.exit(1)
    
    backend = iOS9toA4Backend()
    if use_redsn0w:
        # Build IPSW then launch redsn0w
        success = backend.run_complete_pipeline(input_ipsw, output_ipsw, False)
        if success:
            import subprocess
            subprocess.run([sys.executable, 'redsn0w_flash.py', output_ipsw])
    elif use_sn0wbreeze:
        # Launch sn0wbreeze with base IPSW
        import subprocess
        subprocess.run([sys.executable, 'sn0wbreeze_flash.py', input_ipsw])
        success = True
    else:
        success = backend.run_complete_pipeline(input_ipsw, output_ipsw, use_limera1n)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()