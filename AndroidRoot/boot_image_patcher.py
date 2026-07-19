#!/usr/bin/env python3
"""
Android Boot Image Patcher
Patches boot.img, recovery.img, and ramdisk for root/exploits
Equivalent to iOS ramdisk/boot patching
"""
import os
import struct
import zlib
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class AndroidBootImage:
    """Android boot image header and parser"""
    
    # Boot image magic
    BOOT_MAGIC = b'ANDROID!'
    
    # Page sizes
    PAGE_SIZE = 2048
    KERNEL_PAGE_SIZE = 2048
    RAMDISK_PAGE_SIZE = 2048
    
    def __init__(self, image_path: str):
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Boot image not found: {image_path}")
        
        self.magic = b''
        self.kernel_size = 0
        self.kernel_addr = 0
        self.ramdisk_size = 0
        self.ramdisk_addr = 0
        self.second_size = 0
        self.second_addr = 0
        self.tags_addr = 0
        self.page_size = 0
        self.dt_size = 0
        self.os_version = 0
        self.name = b''
        self.cmdline = b''
        self.id = b''
        self.extra_cmdline = b''
        
        self._parse_header()
    
    def _parse_header(self):
        """Parse boot image header"""
        with open(self.image_path, 'rb') as f:
            self.magic = f.read(8)
            if self.magic != self.BOOT_MAGIC:
                raise ValueError(f"Invalid boot image magic: {self.magic}")
            
            self.kernel_size = struct.unpack('<I', f.read(4))[0]
            self.kernel_addr = struct.unpack('<I', f.read(4))[0]
            self.ramdisk_size = struct.unpack('<I', f.read(4))[0]
            self.ramdisk_addr = struct.unpack('<I', f.read(4))[0]
            self.second_size = struct.unpack('<I', f.read(4))[0]
            self.second_addr = struct.unpack('<I', f.read(4))[0]
            self.tags_addr = struct.unpack('<I', f.read(4))[0]
            self.page_size = struct.unpack('<I', f.read(4))[0]
            self.dt_size = struct.unpack('<I', f.read(4))[0]
            self.os_version = struct.unpack('<I', f.read(4))[0]
            self.name = f.read(16)
            self.cmdline = f.read(512)
            self.id = f.read(32)
            self.extra_cmdline = f.read(32)
    
    def extract_kernel(self, output_path: str) -> str:
        """Extract kernel from boot image"""
        with open(self.image_path, 'rb') as f:
            # Skip header (aligned to page size)
            header_size = ((self.page_size + 2047) // 2048) * 2048
            f.seek(header_size)
            
            kernel_data = f.read(self.kernel_size)
            
            with open(output_path, 'wb') as out:
                out.write(kernel_data)
            
            return output_path
    
    def extract_ramdisk(self, output_path: str) -> str:
        """Extract ramdisk from boot image"""
        with open(self.image_path, 'rb') as f:
            # Skip header
            header_size = ((self.page_size + 2047) // 2048) * 2048
            f.seek(header_size + self._align(self.kernel_size))
            
            ramdisk_data = f.read(self.ramdisk_size)
            
            with open(output_path, 'wb') as out:
                out.write(ramdisk_data)
            
            return output_path
    
    def _align(self, size: int) -> int:
        """Align size to page boundary"""
        return ((size + self.page_size - 1) // self.page_size) * self.page_size
    
    def repack(self, kernel_path: str, ramdisk_path: str, output_path: str,
               cmdline: Optional[str] = None, second_path: Optional[str] = None) -> str:
        """Repack boot image with modified kernel/ramdisk"""
        kernel_data = Path(kernel_path).read_bytes()
        ramdisk_data = Path(ramdisk_path).read_bytes()
        
        if second_path and Path(second_path).exists():
            second_data = Path(second_path).read_bytes()
        else:
            second_data = b''
            self.second_size = 0
        
        # Update sizes
        self.kernel_size = len(kernel_data)
        self.ramdisk_size = len(ramdisk_data)
        self.second_size = len(second_data)
        
        if cmdline:
            self.cmdline = cmdline.encode('utf-8')[:512]
        
        with open(output_path, 'wb') as f:
            # Write header
            f.write(self.BOOT_MAGIC)
            f.write(struct.pack('<I', self.kernel_size))
            f.write(struct.pack('<I', self.kernel_addr))
            f.write(struct.pack('<I', self.ramdisk_size))
            f.write(struct.pack('<I', self.ramdisk_addr))
            f.write(struct.pack('<I', self.second_size))
            f.write(struct.pack('<I', self.second_addr))
            f.write(struct.pack('<I', self.tags_addr))
            f.write(struct.pack('<I', self.page_size))
            f.write(struct.pack('<I', self.dt_size))
            f.write(struct.pack('<I', self.os_version))
            f.write(self.name[:16].ljust(16, b'\x00'))
            f.write(self.cmdline[:512].ljust(512, b'\x00'))
            f.write(self.id[:32].ljust(32, b'\x00'))
            f.write(self.extra_cmdline[:32].ljust(32, b'\x00'))
            
            # Pad header to page boundary
            header_pos = f.tell()
            pad_size = self._align(header_pos) - header_pos
            f.write(b'\x00' * pad_size)
            
            # Write kernel (page aligned)
            f.write(kernel_data)
            pad_size = self._align(self.kernel_size) - self.kernel_size
            f.write(b'\x00' * pad_size)
            
            # Write ramdisk (page aligned)
            f.write(ramdisk_data)
            pad_size = self._align(self.ramdisk_size) - self.ramdisk_size
            f.write(b'\x00' * pad_size)
            
            # Write second (page aligned)
            if second_data:
                f.write(second_data)
                pad_size = self._align(self.second_size) - self.second_size
                f.write(b'\x00' * pad_size)
        
        return output_path


class BootImagePatcher:
    """Patch Android boot images for root/exploits"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="boot_patch_"))
    
    def patch_boot_image(self, boot_image_path: str, output_path: Optional[str] = None,
                         add_root: bool = True, add_debug: bool = True,
                         custom_cmdline: Optional[str] = None) -> str:
        """Patch boot image with root and debug options"""
        boot_img = AndroidBootImage(boot_image_path)
        
        # Extract components
        kernel_path = str(self.temp_dir / "kernel")
        ramdisk_path = str(self.temp_dir / "ramdisk.cpio.gz")
        
        boot_img.extract_kernel(kernel_path)
        boot_img.extract_ramdisk(ramdisk_path)
        
        # Extract ramdisk
        ramdisk_dir = self.temp_dir / "ramdisk"
        ramdisk_dir.mkdir(exist_ok=True)
        self._extract_cpio(ramdisk_path, ramdisk_dir)
        
        # Patch ramdisk
        if add_root:
            self._add_root_support(ramdisk_dir)
        if add_debug:
            self._add_debug_support(ramdisk_dir)
        
        # Repack ramdisk
        new_ramdisk_path = str(self.temp_dir / "ramdisk_patched.cpio.gz")
        self._repack_cpio(ramdisk_dir, new_ramdisk_path)
        
        # Update cmdline
        cmdline = boot_img.cmdline.decode('utf-8', errors='ignore').strip()
        if add_root:
            cmdline += " androidboot.selinux=permissive"
        if custom_cmdline:
            cmdline += f" {custom_cmdline}"
        
        # Repack boot image
        if not output_path:
            output_path = str(self.temp_dir / "boot_patched.img")
        
        boot_img.repack(
            kernel_path=kernel_path,
            ramdisk_path=new_ramdisk_path,
            output_path=output_path,
            cmdline=cmdline
        )
        
        return output_path
    
    def _extract_cpio(self, cpio_path: str, output_dir: Path):
        """Extract CPIO archive"""
        subprocess.run(["gzip", "-dc", cpio_path], 
                      stdout=open(self.temp_dir / "ramdisk.cpio", 'wb'))
        subprocess.run(["cpio", "-idmv"], 
                      stdin=open(self.temp_dir / "ramdisk.cpio", 'rb'),
                      cwd=output_dir, check=True)
    
    def _repack_cpio(self, ramdisk_dir: Path, output_path: str):
        """Repack CPIO archive"""
        proc = subprocess.Popen(
            ["cpio", "-o", "-H", "newc", "-R", "root:root"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        subprocess.run(["gzip"], stdin=proc.stdout, stdout=open(output_path, 'wb'))
        proc.stdin.close()
    
    def _add_root_support(self, ramdisk_dir: Path):
        """Add root support to ramdisk"""
        # Add init.rc modifications for root
        init_rc = ramdisk_dir / "init.rc"
        if init_rc.exists():
            content = init_rc.read_text()
            # Add permissive SELinux
            if "androidboot.selinux=permissive" not in content:
                content = content.replace(
                    "on init",
                    "on init\n    setprop androidboot.selinux permissive"
                )
                init_rc.write_text(content)
        
        # Add su binary if it doesn't exist
        su_binary = ramdisk_dir / "sbin" / "su"
        if not su_binary.exists():
            su_binary.parent.mkdir(parents=True, exist_ok=True)
            # Minimal su stub
            su_binary.write_bytes(b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 100)
            su_binary.chmod(0o755)
    
    def _add_debug_support(self, ramdisk_dir: Path):
        """Add debug support to ramdisk"""
        # Modify fstab for debug
        fstab = ramdisk_dir / "fstab.qcom"  # Qualcomm example
        if fstab.exists():
            content = fstab.read_text()
            # Add debug options
            content = content.replace(
                "defaults",
                "defaults,ro,debug"
            )
            fstab.write_text(content)
    
    def cleanup(self):
        """Cleanup temp files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
