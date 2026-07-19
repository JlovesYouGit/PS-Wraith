#!/usr/bin/env python3
"""
Android NAND Tool - Direct NAND/eMMC/Block Device Access
Equivalent to iOS NAND tool chain
"""
import os
import sys
import struct
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class AndroidNANDTool:
    """Direct NAND/eMMC block device access"""
    
    # Android block device paths
    BLOCK_DEVICES = {
        "emmc": "/dev/block/mmcblk0",
        "emmc_boot0": "/dev/block/mmcblk0boot0",
        "emmc_boot1": "/dev/block/mmcblk0boot1",
        "emmc_rpmb": "/dev/block/mmcblk0rpmb",
        "nand": "/dev/mtd0",
        "mtd": "/dev/mtd",
        "mtdblock": "/dev/mtdblock0",
        "boot": "/dev/block/by-name/boot",
        "recovery": "/dev/block/by-name/recovery",
        "bootloader": "/dev/block/by-name/bootloader",
        "system": "/dev/block/by-name/system",
        "vendor": "/dev/block/by-name/vendor",
        "odm": "/dev/block/by-name/odm",
        "radio": "/dev/block/by-name/radio",
        "xbl": "/dev/block/by-name/xbl",
        "abl": "/dev/block/by-name/abl",
        "tz": "/dev/block/by-name/tz",
        "hyp": "/dev/block/by-name/hyp",
    }
    
    def __init__(self, adb_serial: Optional[str] = None):
        self.adb_serial = adb_serial
        self.adb_cmd = ["adb"]
        if adb_serial:
            self.adb_cmd.extend(["-s", adb_serial])
    
    def run_adb_shell(self, cmd: str, timeout: int = 30, as_root: bool = False) -> Dict[str, any]:
        """Run ADB shell command"""
        full_cmd = self.adb_cmd + ["shell"]
        if as_root:
            full_cmd.extend(["su", "-c", cmd])
        else:
            full_cmd.extend(["sh", "-c", cmd])
        
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_adb_su(self, cmd: str, timeout: int = 30) -> Dict[str, any]:
        """Run command as root via su"""
        return self.run_adb_shell(cmd, timeout=timeout, as_root=True)
    
    def check_root(self) -> bool:
        """Check if device has root access"""
        result = self.run_adb_su("id")
        return result.get("success") and "uid=0" in result.get("stdout", "")
    
    def list_block_devices(self) -> List[Dict[str, str]]:
        """List all block devices"""
        result = self.run_adb_shell("ls -la /dev/block/")
        devices = []
        if result.get("success"):
            for line in result.get("stdout", "").split('\n'):
                if 'mmcblk' in line or 'mtd' in line or 'by-name' in line:
                    devices.append({"line": line})
        return devices
    
    def list_partitions(self) -> List[Dict[str, str]]:
        """List all partitions"""
        result = self.run_adb_shell("cat /proc/partitions")
        partitions = []
        if result.get("success"):
            for line in result.get("stdout", "").split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    partitions.append({
                        "major": parts[0],
                        "minor": parts[1],
                        "blocks": parts[2],
                        "name": parts[3]
                    })
        return partitions
    
    def read_block_device(self, device_path: str, offset: int = 0, size: int = 4096) -> Dict[str, any]:
        """Read from block device"""
        cmd = f"dd if={device_path} bs=1 skip={offset} count={size} 2>/dev/null"
        result = self.run_adb_su(cmd)
        if result.get("success") and result.get("stdout"):
            data = result.get("stdout")
            return {
                "success": True,
                "device": device_path,
                "offset": offset,
                "size": len(data),
                "data": data[:256]  # First 256 bytes
            }
        return result
    
    def write_block_device(self, device_path: str, data: bytes, offset: int = 0) -> Dict[str, any]:
        """Write to block device"""
        # Use Python to write via stdin
        try:
            proc = subprocess.Popen(
                self.adb_cmd + ["shell", "su", "-c", 
                    f"dd of={device_path} bs=1 seek={offset} 2>/dev/null"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(input=data, timeout=30)
            return {
                "success": proc.returncode == 0,
                "device": device_path,
                "offset": offset,
                "size": len(data),
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_bootloader(self) -> Dict[str, any]:
        """Read bootloader partition"""
        return self.read_block_device("/dev/block/by-name/bootloader", 0, 65536)
    
    def read_boot(self) -> Dict[str, any]:
        """Read boot partition"""
        return self.read_block_device("/dev/block/by-name/boot", 0, 65536)
    
    def read_xbl(self) -> Dict[str, any]:
        """Read XBL partition"""
        return self.read_block_device("/dev/block/by-name/xbl", 0, 65536)
    
    def read_tz(self) -> Dict[str, any]:
        """Read TrustZone partition"""
        return self.read_block_device("/dev/block/by-name/tz", 0, 65536)
    
    def dump_partition(self, partition: str, output_path: str) -> Dict[str, any]:
        """Dump partition to file"""
        device = self.BLOCK_DEVICES.get(partition, f"/dev/block/by-name/{partition}")
        cmd = f"dd if={device} of={output_path} bs=1M 2>/dev/null"
        result = self.run_adb_su(cmd, timeout=120)
        if result.get("success"):
            return {"success": True, "partition": partition, "output": output_path}
        return result
    
    def flash_partition_image(self, partition: str, image_path: str) -> Dict[str, any]:
        """Flash partition image via fastboot or dd"""
        if os.path.exists(image_path):
            # Try fastboot first
            pass
        # Use dd as fallback
        device = self.BLOCK_DEVICES.get(partition, f"/dev/block/by-name/{partition}")
        cmd = f"dd if={image_path} of={device} bs=1M 2>/dev/null"
        result = self.run_adb_su(cmd, timeout=120)
        if result.get("success"):
            return {"success": True, "partition": partition, "image": image_path}
        return result
    
    def get_mtd_info(self) -> List[Dict[str, str]]:
        """Get MTD partition info"""
        result = self.run_adb_shell("cat /proc/mtd")
        mtds = []
        if result.get("success"):
            for line in result.get("stdout", "").split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    mtds.append({
                        "dev": parts[0],
                        "size": parts[1],
                        "erasesize": parts[2],
                        "name": parts[3].strip("()")
                    })
        return mtds
    
    def read_mtd(self, mtd_device: str, output_path: str) -> Dict[str, any]:
        """Read MTD partition"""
        cmd = f"nanddump -f {output_path} {mtd_device} 2>/dev/null || dd if={mtd_device} of={output_path} bs=1M 2>/dev/null"
        result = self.run_adb_su(cmd, timeout=120)
        if result.get("success"):
            return {"success": True, "mtd": mtd_device, "output": output_path}
        return result
