#!/usr/bin/env python3
"""
Android Ramdisk Booter
Boot custom ramdisk without flashing
Equivalent to iOS ramdisk boot
"""
import os
import sys
import subprocess
import tempfile
import zipfile
import gzip
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class AndroidRamdiskBooter:
    """Boot custom ramdisk via fastboot"""
    
    def __init__(self, device_serial: Optional[str] = None):
        self.device_serial = device_serial
        self.fastboot_cmd = ["fastboot"]
        if device_serial:
            self.fastboot_cmd.extend(["-s", device_serial])
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ramdisk_boot_"))
    
    def run_fastboot(self, cmd: List[str], timeout: int = 60) -> Dict[str, any]:
        """Run fastboot command"""
        try:
            result = subprocess.run(
                self.fastboot_cmd + cmd,
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_boot_ramdisk(self, boot_image_path: str) -> Optional[str]:
        """Extract ramdisk from boot image"""
        try:
            boot_img = AndroidBootImage(boot_image_path)
            ramdisk_path = str(self.temp_dir / "ramdisk.cpio.gz")
            boot_img.extract_ramdisk(ramdisk_path)
            return ramdisk_path
        except Exception as e:
            print(f"[-] Failed to extract ramdisk: {e}")
            return None
    
    def create_custom_ramdisk(self, base_boot_img: str, 
                              add_bins: Dict[str, bytes] = None,
                              modify_init: bool = True) -> str:
        """Create custom ramdisk"""
        ramdisk_gz = self.extract_boot_ramdisk(base_boot_img)
        if not ramdisk_gz:
            return ""
        
        ramdisk_dir = self.temp_dir / "ramdisk"
        ramdisk_dir.mkdir(exist_ok=True)
        
        # Extract CPIO
        try:
            with gzip.open(ramdisk_gz, 'rb') as f_in:
                cpio_data = f_in.read()
            
            with open(self.temp_dir / "ramdisk.cpio", 'wb') as f_out:
                f_out.write(cpio_data)
            
            subprocess.run(
                ["cpio", "-idmv"],
                input=cpio_data,
                cwd=ramdisk_dir,
                check=True
            )
        except Exception as e:
            print(f"[-] Failed to extract CPIO: {e}")
            return ""
        
        # Modify ramdisk
        if modify_init:
            self._modify_init(ramdisk_dir)
        
        # Add custom binaries
        if add_bins:
            for name, data in add_bins.items():
                bin_path = ramdisk_dir / name
                bin_path.parent.mkdir(parents=True, exist_ok=True)
                bin_path.write_bytes(data)
                bin_path.chmod(0o755)
        
        # Repack
        new_ramdisk_gz = self.temp_dir / "ramdisk_patched.cpio.gz"
        self._repack_cpio(ramdisk_dir, new_ramdisk_gz)
        
        return str(new_ramdisk_gz)
    
    def _modify_init(self, ramdisk_dir: Path):
        """Modify init.rc for custom boot"""
        init_rc = ramdisk_dir / "init.rc"
        if init_rc.exists():
            content = init_rc.read_text()
            # Add root and debug
            content = content.replace(
                "ro.secure=1",
                "ro.secure=0"
            ).replace(
                "ro.debuggable=0",
                "ro.debuggable=1"
            )
            init_rc.write_text(content)
    
    def _repack_cpio(self, ramdisk_dir: Path, output_path: str):
        """Repack CPIO archive"""
        proc = subprocess.Popen(
            ["cpio", "-o", "-H", "newc", "-R", "root:root"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=ramdisk_dir
        )
        with gzip.open(output_path, 'wb') as f:
            f.write(proc.stdout.read())
        proc.stdin.close()
        proc.wait()
    
    def boot_custom_ramdisk(self, boot_image_path: str, 
                            custom_ramdisk_gz: str) -> Dict[str, any]:
        """Boot with custom ramdisk"""
        # Create boot image with custom ramdisk
        from boot_image_patcher import AndroidBootImage
        
        boot_img = AndroidBootImage(boot_image_path)
        kernel_path = str(self.temp_dir / "kernel")
        boot_img.extract_kernel(kernel_path)
        
        # Repack with custom ramdisk
        custom_boot = str(self.temp_dir / "custom_boot.img")
        boot_img.repack(
            kernel_path=kernel_path,
            ramdisk_path=custom_ramdisk_gz,
            output_path=custom_boot,
            cmdline="androidboot.selinux=permissive"
        )
        
        # Boot image
        result = self.run_fastboot(["boot", custom_boot])
        if result.get("success"):
            return {"success": True, "image": custom_boot}
        return result
    
    def cleanup(self):
        """Cleanup temp files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

# Import here to avoid circular dependency
try:
    from .boot_image_patcher import AndroidBootImage
except ImportError:
    pass
