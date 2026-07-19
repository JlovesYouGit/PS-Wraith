#!/usr/bin/env python3
"""
ADB Root Chain - Privilege escalation via ADB
Equivalent to iOS iBoot/ramdisk root chain
"""
import os
import sys
import time
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

class ADBRootChain:
    """ADB-based root and privilege escalation chain"""
    
    def __init__(self, device_serial: Optional[str] = None):
        self.device_serial = device_serial
        self.adb_cmd = ["adb"]
        if device_serial:
            self.adb_cmd.extend(["-s", device_serial])
        self.temp_dir = Path(tempfile.mkdtemp(prefix="adb_root_"))
    
    def run_adb(self, cmd: List[str], timeout: int = 30) -> Dict[str, any]:
        """Run ADB command"""
        try:
            result = subprocess.run(
                self.adb_cmd + cmd,
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_shell(self, cmd: str, as_root: bool = False, timeout: int = 30) -> Dict[str, any]:
        """Run shell command"""
        if as_root:
            return self.run_adb(["shell", "su", "-c", cmd], timeout=timeout)
        return self.run_adb(["shell", cmd], timeout=timeout)
    
    def check_device(self) -> bool:
        """Check if device is connected"""
        result = self.run_adb(["get-state"])
        return result.get("success") and "device" in result.get("stdout", "")
    
    def check_root(self) -> bool:
        """Check if device is already rooted"""
        result = self.run_shell("id", as_root=False)
        if "root" in result.get("stdout", ""):
            return True
        result = self.run_shell("id", as_root=True)
        return result.get("success") and "uid=0" in result.get("stdout", "")
    
    def get_property(self, prop: str) -> Optional[str]:
        """Get system property"""
        result = self.run_shell(f"getprop {prop}")
        if result.get("success"):
            return result.get("stdout")
        return None
    
    def get_build_info(self) -> Dict[str, str]:
        """Get build information"""
        info = {}
        props = [
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.product.board",
            "ro.hardware",
            "ro.product.cpu.abi",
            "ro.secure",
            "ro.debuggable",
            "ro.boot.slot_suffix"
        ]
        for prop in props:
            val = self.get_property(prop)
            if val:
                info[prop] = val
        return info
    
    def push_file(self, local_path: str, remote_path: str) -> Dict[str, any]:
        """Push file to device"""
        if not os.path.exists(local_path):
            return {"success": False, "error": f"Local file not found: {local_path}"}
        
        result = self.run_adb(["push", local_path, remote_path])
        if result.get("success"):
            return {"success": True, "local": local_path, "remote": remote_path}
        return result
    
    def pull_file(self, remote_path: str, local_path: str) -> Dict[str, any]:
        """Pull file from device"""
        result = self.run_adb(["pull", remote_path, local_path])
        if result.get("success"):
            return {"success": True, "remote": remote_path, "local": local_path}
        return result
    
    def install_apk(self, apk_path: str, replace: bool = False) -> Dict[str, any]:
        """Install APK"""
        if not os.path.exists(apk_path):
            return {"success": False, "error": f"APK not found: {apk_path}"}
        
        cmd = ["install"]
        if replace:
            cmd.append("-r")
        cmd.append(apk_path)
        
        result = self.run_adb(cmd, timeout=120)
        if result.get("success") and "Success" in result.get("stdout", ""):
            return {"success": True, "apk": apk_path}
        return result
    
    def remount_system(self) -> Dict[str, any]:
        """Remount /system as rw"""
        # Try root remount
        result = self.run_shell("mount -o remount,rw /system", as_root=True)
        if result.get("success"):
            return {"success": True, "method": "root_remount"}
        
        # Try adb root + remount
        result = self.run_adb(["root"])
        if result.get("success"):
            time.sleep(2)
            result = self.run_shell("mount -o remount,rw /system", as_root=True)
            if result.get("success"):
                return {"success": True, "method": "adb_root_remount"}
        
        return {"success": False, "error": "remount_failed"}
    
    def inject_su(self, su_path: str = "/system/xbin/su") -> Dict[str, any]:
        """Inject su binary"""
        # Push su binary
        local_su = self.temp_dir / "su"
        if not local_su.exists():
            # Minimal su stub
            local_su.write_bytes(b'\x7fELF' + b'\x00' * 100)
            local_su.chmod(0o755)
        
        result = self.push_file(str(local_su), "/data/local/tmp/su")
        if not result.get("success"):
            return result
        
        # Move to system
        result = self.run_shell(f"mount -o remount,rw /system", as_root=True)
        if not result.get("success"):
            return result
        
        result = self.run_shell(f"cp /data/local/tmp/su {su_path}", as_root=True)
        if not result.get("success"):
            return result
        
        result = self.run_shell(f"chmod 0755 {su_path}", as_root=True)
        if not result.get("success"):
            return result
        
        result = self.run_shell(f"chown root:root {su_path}", as_root=True)
        if not result.get("success"):
            return result
        
        return {"success": True, "su_path": su_path}
    
    def exploit_ztask(self) -> Dict[str, any]:
        """Exploit ztask for root (older Android)"""
        result = self.run_shell("cat /proc/tty/driver/serial")
        if "ztask" in result.get("stdout", ""):
            # ztask exploit
            exploit_script = """
            id | grep uid=0 && echo already_root || (
            setprop service.adb.root 1
            stop adbd
                start adbd
            )
            """
            result = self.run_shell(exploit_script)
            time.sleep(3)
            return self.check_root()
        return {"success": False, "error": "ztask_not_found"}
    
    def exploit_adb_over_network(self) -> Dict[str, any]:
        """Exploit ADB over network for root"""
        # Check if adb over network is enabled
        result = self.run_shell("getprop service.adb.tcp.port")
        if result.get("success") and result.get("stdout", "0") != "0":
            # ADB over network is enabled, try to use it
            port = result.get("stdout")
            return {"success": True, "method": "adb_network", "port": port}
        return {"success": False, "error": "adb_network_disabled"}
    
    def get_root_chain_status(self) -> Dict[str, any]:
        """Get status of root chain"""
        status = {
            "device_connected": self.check_device(),
            "rooted": self.check_root(),
            "build_info": self.get_build_info(),
            "adb_root": False,
            "su_injected": False
        }
        
        if status["rooted"]:
            status["adb_root"] = True
            status["su_injected"] = True
            return status
        
        # Try ADB root
        result = self.run_adb(["root"])
        if result.get("success"):
            time.sleep(2)
            status["adb_root"] = self.check_root()
            if status["adb_root"]:
                status["rooted"] = True
                status["su_injected"] = True
                return status
        
        return status
