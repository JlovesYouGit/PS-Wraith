#!/usr/bin/env python3
"""
celestial_routing.py
Command routing and actuation layer for device access.

Merges Vemex sandbox escape with uppi-m-ti celestial routing concepts:
- Sandbox escape grants live device access
- Celestial routing directs commands through device node space
- Density conversion turns mapped state into executable action
- Lua chaining manages sequential command execution
- File creation and internal execution complete the loop
"""

import os
import sys
import time
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from sandbox_runtime import SandboxedRuntime, PathPermissionManager
except ImportError:
    SandboxedRuntime = None
    PathPermissionManager = None


class CelestialRouter:
    """Routes commands through device node space using escaped sandbox access."""
    
    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.adb_cmd = ["adb", "-s", device_serial]
        self.sandbox: Optional[SandboxedRuntime] = None
        self.escaped = False
        self.node_map: Dict[str, Any] = {}
        self.routes: List[Dict] = []
    
    def escape(self) -> Dict[str, Any]:
        """Escape sandbox and initialize router."""
        if self.escaped:
            return {"success": True, "already_escaped": True}
        
        if SandboxedRuntime is None:
            return {"success": False, "error": "Sandbox runtime not available"}
        
        pm = PathPermissionManager(
            allowed_paths=["/Users/u/Desktop/PS-enhance", "/tmp", "/var/tmp"],
            blocked_paths=["/etc", "/root", "/proc", "/sys", "/dev", "/boot", "/System", "/private"]
        )
        self.sandbox = SandboxedRuntime(timeout=30.0, max_recursion=200, storage_manager=pm)
        
        modules = ["os", "sys", "subprocess", "socket", "shutil", "tempfile", "threading", "asyncio"]
        for m in modules:
            self.sandbox.unblock_module(m)
        
        self.escaped = True
        return {"success": True, "unblocked": modules}
    
    def route(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Route command through device node space."""
        if not self.escaped:
            self.escape()
        
        cmd_type = command.get("type", "adb")
        target = command.get("target", "")
        payload = command.get("payload", {})
        
        if cmd_type == "adb":
            return self._route_adb(target, payload)
        elif cmd_type == "fastboot":
            return self._route_fastboot(target, payload)
        elif cmd_type == "service_call":
            return self._route_service_call(target, payload)
        elif cmd_type == "block_device":
            return self._route_block_device(target, payload)
        elif cmd_type == "lua":
            return self._route_lua(target, payload)
        
        return {"success": False, "error": f"Unknown command type: {cmd_type}"}
    
    def _route_adb(self, target: str, payload: Dict) -> Dict[str, Any]:
        """Route ADB command directly."""
        cmd_parts = self.adb_cmd + target.split()
        try:
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
                "route": "adb_direct"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "route": "adb_direct"}
    
    def _route_fastboot(self, target: str, payload: Dict) -> Dict[str, Any]:
        """Route fastboot command."""
        cmd_parts = ["fastboot", "-s", self.device_serial] + target.split()
        try:
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "route": "fastboot_direct"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "route": "fastboot_direct"}
    
    def _route_service_call(self, target: str, payload: Dict) -> Dict[str, Any]:
        """Route service call command."""
        parts = target.split()
        service = parts[0] if parts else "phone"
        code = parts[1] if len(parts) > 1 else "30"
        args = parts[2:] if len(parts) > 2 else []
        
        cmd = self.adb_cmd + ["shell", "service", "call", service, code] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "parcel": self._parse_parcel(result.stdout.strip()),
                "route": "service_call"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "route": "service_call"}
    
    def _route_block_device(self, target: str, payload: Dict) -> Dict[str, Any]:
        """Route block device command."""
        device_path = payload.get("device", f"/dev/block/by-name/{target}")
        operation = payload.get("operation", "read")
        offset = payload.get("offset", 0)
        size = payload.get("size", 4096)
        
        if operation == "read":
            cmd = self.adb_cmd + ["shell", "su", "-c", f"dd if={device_path} bs=1 skip={offset} count={size} 2>/dev/null"]
        elif operation == "write":
            data = payload.get("data", "")
            cmd = self.adb_cmd + ["shell", "su", "-c", f"echo '{data}' | dd of={device_path} bs=1 seek={offset} 2>/dev/null"]
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "device": device_path,
                "operation": operation,
                "route": "block_device"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "route": "block_device"}
    
    def _route_lua(self, target: str, payload: Dict) -> Dict[str, Any]:
        """Route Lua script execution."""
        script = payload.get("script", "")
        env = payload.get("env", {})
        
        # Write Lua script to temp file
        lua_file = Path(tempfile.gettempdir()) / f"magi_zone_{int(time.time())}.lua"
        lua_file.write_text(script)
        
        # Push to device
        remote_path = f"/data/local/tmp/{lua_file.name}"
        push_cmd = self.adb_cmd + ["push", str(lua_file), remote_path]
        try:
            subprocess.run(push_cmd, capture_output=True, text=True, timeout=10)
        except:
            pass
        
        # Execute
        exec_cmd = self.adb_cmd + ["shell", f"lua {remote_path}"]
        try:
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "script": target,
                "route": "lua_execution"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "route": "lua_execution"}
    
    def _parse_parcel(self, parcel_hex: str) -> Dict[str, Any]:
        """Parse Android parcel response."""
        if not parcel_hex:
            return {}
        
        # Remove spaces and convert
        hex_str = parcel_hex.replace(" ", "").replace("\n", "")
        try:
            data = bytes.fromhex(hex_str)
            return {
                "raw": parcel_hex,
                "length": len(data),
                "first_word": hex_str[:8] if len(hex_str) >= 8 else hex_str
            }
        except:
            return {"raw": parcel_hex}
    
    def build_node_map(self) -> Dict[str, Any]:
        """Build device node map from live state."""
        self.node_map = {
            "timestamp": time.time(),
            "device_serial": self.device_serial,
            "adb_state": self.route({"type": "adb", "target": "get-state"}),
            "properties": {},
            "services": [],
            "permissions": [],
            "block_devices": [],
            "access_points": []
        }
        
        # Get properties
        prop_result = self.route({"type": "adb", "target": "shell getprop"})
        if prop_result.get("success"):
            for line in prop_result.get("stdout", "").splitlines():
                if "]" in line:
                    try:
                        key = line.split("[")[1].split("]")[0]
                        val = line.split("[")[2].split("]")[0]
                        self.node_map["properties"][key] = val
                    except:
                        continue
        
        # Get services
        svc_result = self.route({"type": "adb", "target": "shell service list"})
        if svc_result.get("success"):
            self.node_map["services"] = [
                line.split(":", 1)[0].strip()
                for line in svc_result.get("stdout", "").splitlines()
                if ":" in line
            ][:30]
        
        # Get permissions
        perm_result = self.route({"type": "adb", "target": "shell pm list permissions"})
        if perm_result.get("success"):
            self.node_map["permissions"] = perm_result.get("stdout", "").splitlines()[:30]
        
        # Get block devices
        block_result = self.route({"type": "adb", "target": "shell ls -la /dev/block/"})
        if block_result.get("success"):
            self.node_map["block_devices"] = block_result.get("stdout", "").splitlines()[:30]
        
        # Create access points from node map
        self.node_map["access_points"] = self._create_access_points()
        
        return self.node_map
    
    def _create_access_points(self) -> List[Dict]:
        """Create access points from node map."""
        access_points = [
            {"type": "adb_shell", "endpoint": "adb shell", "privilege": "user", "node": "shell"},
            {"type": "adb_root", "endpoint": "adb shell su -c", "privilege": "root", "node": "root"},
            {"type": "fastboot", "endpoint": "fastboot", "privilege": "bootloader", "node": "bootloader"},
        ]
        
        for svc in self.node_map.get("services", [])[:10]:
            if svc:
                access_points.append({
                    "type": "service_call",
                    "endpoint": f"service call {svc}",
                    "privilege": "system",
                    "node": f"service:{svc}"
                })
        
        for dev in self.node_map.get("block_devices", []):
            if "mmcblk" in dev or "by-name" in dev:
                name = dev.split()[-1] if dev.split() else dev
                access_points.append({
                    "type": "block_device",
                    "endpoint": f"/dev/block/{name}",
                    "privilege": "root",
                    "node": f"block:{name}"
                })
                break
        
        return access_points
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "escaped": self.escaped,
            "device_serial": self.device_serial,
            "node_map_built": bool(self.node_map),
            "access_points": len(self.node_map.get("access_points", [])),
            "services": len(self.node_map.get("services", [])),
        }


class LuaCommandChain:
    """Lua-based command chaining and execution management."""
    
    def __init__(self, router: CelestialRouter):
        self.router = router
        self.scripts_dir = Path(tempfile.mkdtemp(prefix="magi_lua_"))
        self.execution_log: List[Dict] = []
    
    def create_script(self, name: str, commands: List[Dict]) -> Path:
        """Create Lua script from command chain."""
        lua = self._generate_lua(name, commands)
        script_path = self.scripts_dir / f"{name}.lua"
        script_path.write_text(lua)
        return script_path
    
    def _generate_lua(self, name: str, commands: List[Dict]) -> str:
        """Generate Lua script from command chain."""
        lua = f"""#!/usr/bin/env lua
-- {name}
-- Auto-generated by celestial routing

local router = {{}}
router.device = "{self.router.device_serial}"
router.log = {{}}

function router.log(msg)
    io.write("[{name}] " .. tostring(msg) .. "\\n")
    io.flush()
end

function router.exec(cmd)
    router.log("EXEC: " .. cmd)
    local handle = io.popen(cmd .. " 2>&1")
    local output = handle:read("*a")
    handle:close()
    return output
end

function router.adb(cmd)
    return router.exec("adb -s " .. router.device .. " " .. cmd)
end

"""
        
        for i, cmd in enumerate(commands):
            lua += f"-- Step {i+1}: {cmd.get('name', 'step')}\n"
            if cmd.get("type") == "adb":
                lua += f"local r{i} = router.adb('{cmd['target']}')\n"
                lua += f"router.log('Result: ' .. tostring(r{i}))\n\n"
            elif cmd.get("type") == "sleep":
                lua += f"os.execute('sleep {cmd.get('duration', 1)}')\n\n"
        
        lua += f"router.log('{name} complete')\n"
        return lua
    
    def execute_chain(self, name: str, commands: List[Dict]) -> Dict[str, Any]:
        """Execute command chain via Lua."""
        script_path = self.create_script(name, commands)
        
        # Push to device
        remote_path = f"/data/local/tmp/{name}.lua"
        push_cmd = self.router.adb_cmd + ["push", str(script_path), remote_path]
        try:
            subprocess.run(push_cmd, capture_output=True, text=True, timeout=10)
        except:
            pass
        
        # Execute
        exec_cmd = self.router.adb_cmd + ["shell", f"lua {remote_path}"]
        try:
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=60)
            log_entry = {
                "script": name,
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "timestamp": time.time()
            }
            self.execution_log.append(log_entry)
            return log_entry
        except Exception as e:
            log_entry = {
                "script": name,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
            self.execution_log.append(log_entry)
            return log_entry
    
    def create_root_chain(self) -> List[Dict]:
        """Create root escalation command chain."""
        return [
            {"name": "check_root", "type": "adb", "target": "shell id"},
            {"name": "try_adb_root", "type": "adb", "target": "root", "sleep_after": 3},
            {"name": "verify_root", "type": "adb", "target": "shell id"},
            {"name": "remount_system", "type": "adb", "target": "shell mount -o remount,rw /system"},
            {"name": "inject_su", "type": "lua", "script": "inject_su"},
        ]
    
    def create_sim_unblock_chain(self, pin: str = "8094298821") -> List[Dict]:
        """Create SIM unblock command chain."""
        return [
            {"name": "launch_settings", "type": "adb", "target": "shell am start -a android.settings.SETTINGS"},
            {"name": "wait_ui", "type": "sleep", "duration": 2},
            {"name": "scroll_settings", "type": "adb", "target": "shell input swipe 500 2000 500 200 300"},
            {"name": "tap_security", "type": "adb", "target": "shell input tap 540 5450"},
            {"name": "wait_security", "type": "sleep", "duration": 1},
            {"name": "tap_sim_lock", "type": "adb", "target": "shell input tap 540 6950"},
            {"name": "wait_sim_lock", "type": "sleep", "duration": 1},
            {"name": "focus_pin_field", "type": "adb", "target": "shell input tap 540 830"},
            {"name": "enter_pin", "type": "adb", "target": f"shell input text {pin}"},
            {"name": "tap_ok", "type": "adb", "target": "shell input tap 894 975"},
        ]
    
    def execute_root_chain(self) -> Dict[str, Any]:
        """Execute root escalation chain."""
        chain = self.create_root_chain()
        return self.execute_chain("root_escalation", chain)
    
    def execute_sim_unblock_chain(self, pin: str = "8094298821") -> Dict[str, Any]:
        """Execute SIM unblock chain."""
        chain = self.create_sim_unblock_chain(pin)
        return self.execute_chain("sim_unblock", chain)


class DensityConverter:
    """Converts internal device state density into executable actions."""
    
    def __init__(self, router: CelestialRouter):
        self.router = router
        self.density_map: Dict[str, float] = {}
    
    def measure_density(self) -> Dict[str, Any]:
        """Measure device state density from node map."""
        if not self.router.node_map:
            self.router.build_node_map()
        
        props = self.router.node_map.get("properties", {})
        services = self.router.node_map.get("services", [])
        permissions = self.router.node_map.get("permissions", [])
        
        density = {
            "ro.secure": 1.0 if props.get("ro.secure") == "1" else 0.0,
            "ro.debuggable": 1.0 if props.get("ro.debuggable") == "1" else 0.0,
            "service_count": len(services) / 100.0,
            "permission_count": len(permissions) / 100.0,
            "block_device_access": 1.0 if any("mmcblk" in d for d in self.router.node_map.get("block_devices", [])) else 0.0,
        }
        
        self.density_map = density
        return density
    
    def convert_to_action(self, density: Dict[str, float]) -> List[Dict]:
        """Convert density measurements to executable actions."""
        actions = []
        
        if density.get("ro.secure", 1.0) > 0.5:
            actions.append({
                "name": "attempt_adb_root",
                "type": "adb",
                "target": "root",
                "priority": 1.0 - density["ro.secure"]
            })
        
        if density.get("service_count", 0) > 0.5:
            actions.append({
                "name": "probe_services",
                "type": "service_call",
                "target": "phone 30 i32 1",
                "priority": density["service_count"]
            })
        
        if density.get("block_device_access", 0) > 0.5:
            actions.append({
                "name": "read_block_device",
                "type": "block_device",
                "target": "boot",
                "payload": {"operation": "read", "device": "/dev/block/by-name/boot", "size": 4096},
                "priority": density["block_device_access"]
            })
        
        return sorted(actions, key=lambda x: x.get("priority", 0), reverse=True)


class ActuationEngine:
    """Executes actions derived from density conversion."""
    
    def __init__(self, router: CelestialRouter, lua_chain: LuaCommandChain):
        self.router = router
        self.lua_chain = lua_chain
        self.converter = DensityConverter(router)
        self.results: List[Dict] = []
    
    def actuate(self) -> Dict[str, Any]:
        """Full actuation cycle: escape -> map -> measure -> convert -> execute."""
        results = {
            "escape": self.router.escape(),
            "node_map": self.router.build_node_map(),
            "density": self.converter.measure_density(),
            "actions": self.converter.convert_to_action(self.converter.density_map),
            "executions": [],
            "success": False
        }
        
        # Execute actions
        for action in results["actions"][:5]:  # Top 5 actions
            if action.get("type") == "adb":
                exec_result = self.router.route({
                    "type": "adb",
                    "target": action["target"]
                })
            elif action.get("type") == "service_call":
                exec_result = self.router.route({
                    "type": "service_call",
                    "target": action["target"]
                })
            elif action.get("type") == "block_device":
                exec_result = self.router.route({
                    "type": "block_device",
                    "target": action["target"],
                    "payload": action.get("payload", {})
                })
            else:
                continue
            
            results["executions"].append({
                "action": action.get("name"),
                "result": exec_result
            })
            
            if exec_result.get("success"):
                results["success"] = True
                break
        
        # If no action succeeded, try Lua chains
        if not results["success"]:
            root_result = self.lua_chain.execute_root_chain()
            results["executions"].append({"action": "lua_root_chain", "result": root_result})
            if root_result.get("success"):
                results["success"] = True
            
            if not results["success"]:
                sim_result = self.lua_chain.execute_sim_unblock_chain()
                results["executions"].append({"action": "lua_sim_unblock", "result": sim_result})
                if sim_result.get("success"):
                    results["success"] = True
        
        self.results.append(results)
        return results
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "router": self.router.get_status(),
            "density": self.converter.density_map,
            "executions": len(self.results),
            "last_success": self.results[-1]["success"] if self.results else False
        }


def create_celestial_router(device_serial: str = "1bbfce51") -> CelestialRouter:
    return CelestialRouter(device_serial=device_serial)


def create_lua_chain(router: CelestialRouter) -> LuaCommandChain:
    return LuaCommandChain(router)


def create_actuation_engine(device_serial: str = "1bbfce51") -> ActuationEngine:
    router = create_celestial_router(device_serial)
    lua_chain = create_lua_chain(router)
    return ActuationEngine(router, lua_chain)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Celestial Routing Actuation Engine")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--escape", action="store_true", help="Escape sandbox only")
    parser.add_argument("--map", action="store_true", help="Build node map")
    parser.add_argument("--actuate", action="store_true", help="Run full actuation cycle")
    parser.add_argument("--root-chain", action="store_true", help="Execute root Lua chain")
    parser.add_argument("--sim-unblock", action="store_true", help="Execute SIM unblock Lua chain")
    args = parser.parse_args()
    
    router = create_celestial_router(args.serial)
    lua_chain = create_lua_chain(router)
    engine = ActuationEngine(router, lua_chain)
    
    if args.escape:
        result = router.escape()
        print(json.dumps(result, indent=2))
    elif args.map:
        node_map = router.build_node_map()
        print(json.dumps(node_map, indent=2, default=str))
    elif args.actuate:
        result = engine.actuate()
        print(json.dumps(result, indent=2, default=str))
    elif args.root_chain:
        result = lua_chain.execute_root_chain()
        print(json.dumps(result, indent=2))
    elif args.sim_unblock:
        result = lua_chain.execute_sim_unblock_chain()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
