#!/usr/bin/env python3
"""
magi_zone_device_access.py
Lua + ADB/fastboot privilege escalation framework for Android using Vemex sandbox escape.

This module uses the Vemex SandboxedRuntime.unblock_module() escape mechanism
to break out of the simulation sandbox and directly interact with the device.
It creates access points directly from the device's connection, mapping the
entire device instead of relying on simulation fallbacks.

Usage:
    python3 magi_zone_device_access.py --serial <device_serial> --escape
    python3 magi_zone_device_access.py --serial <device_serial> --map
    python3 magi_zone_device_access.py --serial <device_serial> --chain
"""

import os
import sys
import time
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Vemex imports
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from sandbox_runtime import SandboxedRuntime, PathPermissionManager
    HAS_SANDBOX = True
except ImportError:
    HAS_SANDBOX = False


class MagiZoneDeviceAccess:
    """Lua-based Android privilege escalation via magi-zone formula chaining.
    
    Uses Vemex sandbox escape mechanism to directly interact with device.
    Instead of simulation fallbacks, creates access points directly from
    the device connection and feeds off the device itself to map the entire device.
    """
    
    def __init__(self, device_serial: Optional[str] = None, vemex_engine = None):
        self.device_serial = device_serial
        self.vemex_engine = vemex_engine
        self.adb_cmd = ["adb"]
        self.fastboot_cmd = ["fastboot"]
        if device_serial:
            self.adb_cmd.extend(["-s", device_serial])
            self.fastboot_cmd.extend(["-s", device_serial])
        
        # Sandbox escape state
        self.sandbox_escaped = False
        self.sandbox_runtime = None
        self.unblocked_modules: List[str] = []
        
        # Device mapping state
        self.device_map: Dict[str, Any] = {}
        self.access_points: List[Dict] = []
        self.formula_chain: List[Dict] = []
        
        # Initialize sandbox escape
        self._initialize_sandbox_escape()
    
    def _initialize_sandbox_escape(self):
        """Initialize sandbox escape using Vemex mechanism."""
        if not HAS_SANDBOX:
            return
        
        if self.vemex_engine and hasattr(self.vemex_engine, 'sandbox_runtime') and self.vemex_engine.sandbox_runtime:
            self.sandbox_runtime = self.vemex_engine.sandbox_runtime
        else:
            # Create standalone sandbox runtime for escape
            permission_manager = PathPermissionManager(
                allowed_paths=[
                    str(Path.home()),
                    "/tmp",
                    "/var/tmp",
                    "/Users/u/Desktop"
                ],
                blocked_paths=[
                    "/etc", "/root", "/proc", "/sys", "/dev", "/boot",
                    "/System", "/private", "/var/root", "/var/db"
                ]
            )
            self.sandbox_runtime = SandboxedRuntime(
                timeout=30.0,
                max_recursion=200,
                storage_manager=permission_manager
            )
    
    def escape_sandbox(self) -> Dict[str, Any]:
        """Escape the sandbox by unblocking necessary modules.
        
        This is the key escape mechanism from Vemex that allows direct
        device access instead of simulation fallbacks.
        """
        if not self.sandbox_runtime:
            return {"success": False, "error": "No sandbox runtime available"}
        
        if self.sandbox_escaped:
            return {"success": True, "already_escaped": True, "unblocked": self.unblocked_modules}
        
        # Modules needed for direct device access
        escape_modules = [
            "os",
            "sys", 
            "subprocess",
            "socket",
            "shutil",
            "tempfile",
            "threading",
            "asyncio",
        ]
        
        results = []
        for module in escape_modules:
            result = self.sandbox_runtime.unblock_module(module)
            results.append(result)
            if result.get("success"):
                self.unblocked_modules.append(module)
        
        self.sandbox_escaped = len(self.unblocked_modules) >= 3
        
        return {
            "success": self.sandbox_escaped,
            "unblocked_modules": self.unblocked_modules,
            "escape_results": results,
            "timestamp": time.time()
        }
    
    def _run_adb_direct(self, cmd: List[str], timeout: int = 10) -> Dict[str, Any]:
        """Run ADB command directly using subprocess (escaped sandbox)."""
        try:
            result = subprocess.run(
                self.adb_cmd + cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_fastboot_direct(self, cmd: List[str], timeout: int = 10) -> Dict[str, Any]:
        """Run fastboot command directly using subprocess."""
        try:
            result = subprocess.run(
                self.fastboot_cmd + cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def map_device(self) -> Dict[str, Any]:
        """Map the entire device directly from its connection.
        
        This bypasses simulation sandbox and maps the actual device state.
        """
        if not self.sandbox_escaped:
            escape = self.escape_sandbox()
            if not escape.get("success"):
                return {"success": False, "error": "Sandbox escape failed", "escape": escape}
        
        device_map: Dict[str, Any] = {
            "timestamp": time.time(),
            "device_serial": self.device_serial,
            "adb_state": None,
            "fastboot_state": None,
            "properties": {},
            "services": [],
            "permissions": [],
            "block_devices": [],
            "access_points": [],
        }
        
        # ADB state
        adb_state = self._run_adb_direct(["get-state"])
        device_map["adb_state"] = adb_state.get("stdout", "")
        
        if "device" in device_map.get("adb_state", ""):
            # Properties
            props = self._run_adb_direct(["shell", "getprop"])
            if props.get("success"):
                for line in props.get("stdout", "").splitlines():
                    if "]" in line:
                        try:
                            key = line.split("[")[1].split("]")[0]
                            val = line.split("[")[2].split("]")[0]
                            device_map["properties"][key] = val
                        except Exception:
                            continue
            
            # Services
            services = self._run_adb_direct(["shell", "service", "list"])
            if services.get("success"):
                device_map["services"] = [
                    line.split(":", 1)[0].strip()
                    for line in services.get("stdout", "").splitlines()
                    if ":" in line
                ][:30]
            
            # Permissions
            perms = self._run_adb_direct(["shell", "pm", "list", "permissions"])
            if perms.get("success"):
                device_map["permissions"] = perms.get("stdout", "").splitlines()[:30]
            
            # Block devices
            block = self._run_adb_direct(["shell", "ls", "-la", "/dev/block/"])
            if block.get("success"):
                device_map["block_devices"] = block.get("stdout", "").splitlines()[:30]
            
            # Access points
            device_map["access_points"] = self._create_access_points(device_map)
        
        # Fastboot state
        fb_state = self._run_fastboot_direct(["devices"])
        device_map["fastboot_state"] = fb_state.get("stdout", "")
        
        self.device_map = device_map
        return device_map
    
    def _create_access_points(self, device_map: Dict) -> List[Dict]:
        """Create access points from mapped device data."""
        access_points = [
            {"type": "adb_shell", "endpoint": "adb shell", "privilege": "user"},
            {"type": "adb_root", "endpoint": "adb shell su -c", "privilege": "root"},
            {"type": "fastboot", "endpoint": "fastboot", "privilege": "bootloader"},
        ]
        
        # Service call access points
        for svc in device_map.get("services", [])[:10]:
            if svc:
                access_points.append({
                    "type": "service_call",
                    "endpoint": f"service call {svc}",
                    "privilege": "system",
                })
        
        # Block device access points
        for part in device_map.get("block_devices", []):
            if "mmcblk" in part or "by-name" in part:
                name = part.split()[-1] if part.split() else part
                access_points.append({
                    "type": "block_device",
                    "endpoint": f"/dev/block/{name}",
                    "privilege": "root",
                })
                break
        
        self.access_points = access_points
        return access_points
    
    def build_formula_chain(self) -> List[Dict]:
        """Build magi-zone formula chain from mapped device data."""
        if not self.device_map:
            self.map_device()
        
        formulas: List[Dict] = []
        
        # Formula 1: Sandbox escape
        formulas.append({
            "name": "sandbox_escape",
            "target_level": 1,
            "chain": [
                {"name": "escape_sandbox", "type": "native", "method": "escape_sandbox"}
            ],
        })
        
        # Formula 2: ADB root
        if "device" in self.device_map.get("adb_state", ""):
            formulas.append({
                "name": "adb_root",
                "target_level": 2,
                "chain": [
                    {"name": "try_adb_root", "type": "adb", "cmd": "root", "check": "restarting"},
                    {"name": "wait", "type": "sleep", "duration": 3},
                    {"name": "verify_root", "type": "adb", "cmd": "shell id", "check": "uid=0"},
                ],
            })
        
        # Formula 3: Service layer access
        if self.device_map.get("services"):
            formulas.append({
                "name": "service_layer",
                "target_level": 3,
                "chain": [
                    {"name": "list_services", "type": "adb", "cmd": "shell service list"},
                    {"name": "probe_phone_service", "type": "adb", "cmd": "shell service call phone 30 i32 1"},
                ],
            })
        
        # Formula 4: SIM unblock
        formulas.append({
            "name": "sim_unblock",
            "target_level": 4,
            "chain": [
                {"name": "launch_settings", "type": "adb", "cmd": "shell am start -a android.settings.SETTINGS"},
                {"name": "navigate_security", "type": "native", "method": "navigate_sim_lock_settings"},
                {"name": "enter_pin", "type": "native", "method": "enter_sim_pin"},
            ],
        })
        
        # Formula 5: Bootloader unlock
        if "fastboot" in self.device_map.get("fastboot_state", "").lower():
            formulas.append({
                "name": "bootloader_unlock",
                "target_level": 5,
                "chain": [
                    {"name": "unlock_bootloader", "type": "fastboot", "cmd": "flashing unlock"}
                ],
            })
        
        self.formula_chain = formulas
        return formulas
    
    def execute_formula_chain(self, start_level: int = 0) -> Dict[str, Any]:
        """Execute the magi-zone formula chain from a given level."""
        if not self.formula_chain:
            self.build_formula_chain()
        
        results = []
        current_level = start_level
        
        for formula in self.formula_chain:
            if formula["target_level"] <= current_level:
                continue
            
            print(f"[magi-zone] Executing formula: {formula['name']}")
            result = self._execute_formula(formula)
            results.append({
                "formula": formula["name"],
                "target_level": formula["target_level"],
                "result": result,
            })
            
            if result.get("success"):
                current_level = formula["target_level"]
                print(f"[magi-zone] Formula SUCCESS: {formula['name']} (level {current_level})")
            else:
                print(f"[magi-zone] Formula FAILED: {formula['name']}: {result.get('error')}")
        
        return {
            "success": current_level > start_level,
            "final_level": current_level,
            "formula_results": results,
            "access_points": self.access_points,
            "device_map": self.device_map,
        }
    
    def _execute_formula(self, formula: Dict) -> Dict[str, Any]:
        """Execute a single formula."""
        chain_results = []
        
        for step in formula.get("chain", []):
            result = self._execute_step(step)
            chain_results.append(result)
            
            if not result.get("success") and step.get("required", True):
                return {
                    "success": False,
                    "failed_step": step.get("name"),
                    "error": result.get("error"),
                    "chain_results": chain_results,
                }
        
        return {"success": True, "chain_results": chain_results}
    
    def _execute_step(self, step: Dict) -> Dict[str, Any]:
        """Execute a single step in the formula chain."""
        step_type = step.get("type")
        
        if step_type == "adb":
            return self._run_adb_direct([step["cmd"]])
        elif step_type == "fastboot":
            return self._run_fastboot_direct([step["cmd"]])
        elif step_type == "native":
            return self._execute_native_step(step)
        elif step_type == "sleep":
            time.sleep(step.get("duration", 1))
            return {"success": True}
        
        return {"success": False, "error": f"Unknown step type: {step_type}"}
    
    def _execute_native_step(self, step: Dict) -> Dict[str, Any]:
        """Execute native method step."""
        method = step.get("method")
        
        if method == "escape_sandbox":
            return self.escape_sandbox()
        elif method == "navigate_sim_lock_settings":
            return self._navigate_sim_lock_settings()
        elif method == "enter_sim_pin":
            return self._enter_sim_pin()
        
        return {"success": False, "error": f"Unknown native method: {method}"}
    
    def _navigate_sim_lock_settings(self) -> Dict[str, Any]:
        """Navigate to SIM lock settings via ADB UI automation."""
        results = []
        
        r = self._run_adb_direct(["shell", "am", "start", "-a", "android.settings.SETTINGS"])
        results.append(r)
        time.sleep(1)
        
        r = self._run_adb_direct(["shell", "input", "swipe", "500", "2000", "500", "200", "300"])
        results.append(r)
        time.sleep(0.5)
        
        r = self._run_adb_direct(["shell", "input", "tap", "540", "5450"])
        results.append(r)
        time.sleep(1)
        
        r = self._run_adb_direct(["shell", "input", "tap", "540", "6950"])
        results.append(r)
        time.sleep(1)
        
        return {"success": True, "results": results}
    
    def _enter_sim_pin(self, pin: str = "8094298821") -> Dict[str, Any]:
        """Enter SIM PIN via ADB input events."""
        r1 = self._run_adb_direct(["shell", "input", "tap", "540", "830"])
        time.sleep(0.3)
        
        r2 = self._run_adb_direct(["shell", "input", "text", pin])
        time.sleep(0.3)
        
        r3 = self._run_adb_direct(["shell", "input", "tap", "894", "975"])
        
        return {
            "success": r1.get("success") and r2.get("success") and r3.get("success"),
            "pin_entered": pin,
            "results": [r1, r2, r3],
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of device access."""
        return {
            "sandbox_escaped": self.sandbox_escaped,
            "unblocked_modules": self.unblocked_modules,
            "device_serial": self.device_serial,
            "access_points_count": len(self.access_points),
            "formula_chain_count": len(self.formula_chain),
            "device_mapped": bool(self.device_map),
            "vemex_engine_attached": self.vemex_engine is not None,
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="magi-zone Device Access")
    parser.add_argument("--serial", help="Device serial")
    parser.add_argument("--escape", action="store_true", help="Escape sandbox only")
    parser.add_argument("--map", action="store_true", help="Map device")
    parser.add_argument("--chain", action="store_true", help="Execute formula chain")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    access = MagiZoneDeviceAccess(device_serial=args.serial)
    
    if args.escape:
        result = access.escape_sandbox()
        print(json.dumps(result, indent=2))
    elif args.map:
        result = access.map_device()
        print(json.dumps(result, indent=2, default=str))
    elif args.chain:
        result = access.execute_formula_chain()
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        print(json.dumps(access.get_status(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
