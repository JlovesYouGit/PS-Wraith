#!/usr/bin/env python3
"""
magi-zone-android
Lua + ADB/fastboot privilege escalation framework for Android.
Converts magi-zone concepts into device-side execution via Lua scripts.
"""
import os
import sys
import time
import subprocess
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class MagiZoneAndroid:
    """Lua-based Android privilege escalation via magi-zone formula chaining."""
    
    def __init__(self, device_serial: Optional[str] = None):
        self.device_serial = device_serial
        self.adb_cmd = ["adb"]
        if device_serial:
            self.adb_cmd.extend(["-s", device_serial])
        self.runtime_dir = Path(__file__).parent
        self.lua_dir = self.runtime_dir / "lua"
        self.scripts_dir = self.runtime_dir / "scripts"
        self.temp_dir = Path(tempfile.mkdtemp(prefix="magi_zone_android_"))
    
    def run_adb(self, cmd: List[str], timeout: int = 30) -> Dict[str, any]:
        try:
            result = subprocess.run(self.adb_cmd + cmd, capture_output=True, text=True, timeout=timeout)
            return {"success": result.returncode == 0, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_shell(self, cmd: str, as_root: bool = False, timeout: int = 30) -> Dict[str, any]:
        if as_root:
            return self.run_adb(["shell", "su", "-c", cmd], timeout=timeout)
        return self.run_adb(["shell", cmd], timeout=timeout)
    
    def push_file(self, local_path: str, remote_path: str) -> Dict[str, any]:
        if not os.path.exists(local_path):
            return {"success": False, "error": f"Local file not found: {local_path}"}
        return self.run_adb(["push", local_path, remote_path])
    
    def pull_file(self, remote_path: str, local_path: str) -> Dict[str, any]:
        return self.run_adb(["pull", remote_path, local_path])
    
    def check_device(self) -> bool:
        result = self.run_adb(["get-state"])
        return result.get("success") and "device" in result.get("stdout", "")
    
    def check_root(self) -> bool:
        result = self.run_shell("id")
        if "root" in result.get("stdout", ""):
            return True
        result = self.run_shell("id", as_root=True)
        return result.get("success") and "uid=0" in result.get("stdout", "")
    
    def build_lua_runtime(self) -> str:
        """Build a minimal Lua runtime zip for Android."""
        lua_runtime_zip = self.temp_dir / "lua_runtime.zip"
        
        with zipfile.ZipFile(lua_runtime_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add Lua interpreter stub (shell script)
            zf.writestr("lua", """#!/system/bin/sh
# Minimal Lua runtime wrapper for Android
LUA_DIR="/data/local/tmp/lua"
SCRIPT="$1"
shift
exec "$LUA_DIR/lua_android" "$LUA_DIR/$SCRIPT" "$@"
""")
            # Add Lua loader
            zf.writestr("lua_android.c", """
// Minimal Lua interpreter stub for Android
// This would be compiled for Android ARM64
#include <stdio.h>
int main(int argc, char *argv[]) {
    printf("Lua runtime placeholder for ARM64\\n");
    return 0;
}
""")
            # Add magi-zone bootstrap
            zf.writestr("magi_zone_bootstrap.lua", """
-- magi-zone bootstrap for Android
local magi = {}
magi.zone = "android_root"
magi.formula = {}
magi.access_level = 0

function magi.elevate(formula)
    print("[magi-zone] Elevating via formula: " .. formula.name)
    for _, step in ipairs(formula.chain) do
        print("[magi-zone] Step: " .. step.name)
        if step.type == "adb" then
            os.execute(step.cmd)
        elseif step.type == "lua" then
            dofile(step.path)
        elseif step.type == "fastboot" then
            os.execute("fastboot " .. step.cmd)
        end
    end
    magi.access_level = formula.target_level
    return true
end

return magi
""")
            # Add root escalation formula
            zf.writestr("formulas/root_adb.lua", """
-- ADB root escalation formula
local formula = {
    name = "adb_root_escalation",
    target_level = 1,
    chain = {
        {name="check_adb_root", type="adb", cmd="adb root"},
        {name="wait_for_root", type="sleep", duration=3},
        {name="verify_root", type="adb", cmd="adb shell id"}
    }
}
return formula
""")
            # Add bootloader unlock formula
            zf.writestr("formulas/unlock_bootloader.lua", """
-- Bootloader unlock formula
local formula = {
    name = "unlock_bootloader",
    target_level = 2,
    chain = {
        {name="reboot_bootloader", type="adb", cmd="adb reboot bootloader"},
        {name="wait_bootloader", type="sleep", duration=5},
        {name="unlock", type="fastboot", cmd="flashing unlock"},
        {name="reboot", type="fastboot", cmd="reboot"}
    }
}
return formula
""")
            # Add SELinux permissive formula
            zf.writestr("formulas/selinux_permissive.lua", """
-- SELinux permissive formula
local formula = {
    name = "selinux_permissive",
    target_level = 1,
    chain = {
        {name="set_prop", type="adb", cmd="adb shell setenforce 0"},
        {name="verify", type="adb", cmd="adb shell getenforce"}
    }
}
return formula
""")
            # Add SIM unblock formula
            zf.writestr("formulas/sim_unblock.lua", """
-- SIM unblock formula via magi-zone
local formula = {
    name = "sim_unblock_via_ui",
    target_level = 1,
    chain = {
        {name="launch_settings", type="adb", cmd="adb shell am start -a android.settings.SETTINGS"},
        {name="wait_ui", type="sleep", duration=2},
        {name="navigate_security", type="lua", path="formulas/sim_unblock_nav.lua"},
        {name="enter_pin", type="lua", path="formulas/sim_unblock_pin.lua"}
    }
}
return formula
""")
            zf.writestr("formulas/sim_unblock_nav.lua", """
-- SIM unblock UI navigation
local function tap(x, y)
    os.execute("adb shell input tap " .. x .. " " .. y)
end

local function swipe(x1, y1, x2, y2, duration)
    os.execute("adb shell input swipe " .. x1 .. " " .. y1 .. " " .. x2 .. " " .. y2 .. " " .. (duration or 300))
end

-- Navigate to Security and privacy
swipe(500, 2000, 500, 200, 300)
os.execute("sleep 1")
tap(540, 5450)
os.execute("sleep 1")
tap(540, 6950)
os.execute("sleep 1")
""")
            zf.writestr("formulas/sim_unblock_pin.lua", """
-- Enter SIM PIN
local PIN = os.getenv("SIM_PIN") or "8094298821"
os.execute('adb shell input text "' .. PIN .. '"')
os.execute("sleep 0.5")
os.execute("adb shell input keyevent 66")  -- OK
""")
            # Add master formula that chains everything
            zf.writestr("master_formula.lua", """
-- Master formula: chain all escalation steps
local magi = dofile("magi_zone_bootstrap.lua")

local formulas = {
    dofile("formulas/root_adb.lua"),
    dofile("formulas/selinux_permissive.lua"),
    dofile("formulas/unlock_bootloader.lua"),
    dofile("formulas/sim_unblock.lua")
}

for _, formula in ipairs(formulas) do
    print("[master] Executing formula: " .. formula.name)
    local ok = magi.elevate(formula)
    if not ok then
        print("[master] Formula failed: " .. formula.name)
    end
end

print("[master] Final access level: " .. magi.access_level)
""")
        
        return str(lua_runtime_zip)
    
    def deploy_runtime(self) -> Dict[str, any]:
        """Deploy Lua runtime to device."""
        runtime_zip = self.build_lua_runtime()
        remote_zip = "/data/local/tmp/magi_zone_runtime.zip"
        
        result = self.push_file(runtime_zip, remote_zip)
        if not result.get("success"):
            return result
        
        # Extract on device
        extract_result = self.run_shell("unzip -o /data/local/tmp/magi_zone_runtime.zip -d /data/local/tmp/magi_zone/")
        if not extract_result.get("success"):
            # Try with toybox unzip or mkdir + manual extract
            mkdir_result = self.run_shell("mkdir -p /data/local/tmp/magi_zone/lua /data/local/tmp/magi_zone/formulas")
            if mkdir_result.get("success"):
                # Push key files individually
                self._push_key_lua_files()
                return {"success": True, "method": "manual_deploy", "runtime": "/data/local/tmp/magi_zone"}
        
        return {"success": True, "runtime": "/data/local/tmp/magi_zone", "zip": remote_zip}
    
    def _push_key_lua_files(self):
        """Push individual Lua files to device."""
        key_files = [
            ("magi_zone_bootstrap.lua", "/data/local/tmp/magi_zone/"),
            ("master_formula.lua", "/data/local/tmp/magi_zone/"),
        ]
        for local_name, remote_dir in key_files:
            local_path = self.temp_dir / local_name
            if local_path.exists():
                self.push_file(str(local_path), remote_dir + local_name)
    
    def execute_formula(self, formula_name: str, env: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """Execute a specific formula on the device."""
        # Check if runtime is deployed
        check = self.run_shell("ls /data/local/tmp/magi_zone/")
        if not check.get("success"):
            deploy = self.deploy_runtime()
            if not deploy.get("success"):
                return {"success": False, "error": "runtime_deploy_failed", "detail": deploy}
        
        # Execute formula via ADB shell
        script_path = f"/data/local/tmp/magi_zone/{formula_name}"
        cmd = f"sh {script_path}" if formula_name.endswith(".sh") else f"lua {script_path}"
        
        if env:
            env_str = " ".join([f"{k}={v}" for k, v in env.items()])
            cmd = f"export {env_str} && {cmd}"
        
        return self.run_shell(cmd)
    
    def execute_master_formula(self, env: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """Execute the master formula that chains all escalation steps."""
        return self.execute_formula("master_formula.lua", env)
    
    def push_and_run_lua(self, lua_script: str, script_name: str, env: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """Push a Lua script to device and execute it."""
        local_path = self.temp_dir / script_name
        local_path.write_text(lua_script)
        
        remote_path = f"/data/local/tmp/{script_name}"
        result = self.push_file(str(local_path), remote_path)
        if not result.get("success"):
            return result
        
        return self.execute_formula(script_name, env)
    
    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="magi-zone-android: Lua-based Android root/escalation")
    parser.add_argument("--serial", help="Device serial")
    parser.add_argument("--deploy", action="store_true", help="Deploy Lua runtime to device")
    parser.add_argument("--run", help="Execute formula by name")
    parser.add_argument("--master", action="store_true", help="Execute master formula chain")
    parser.add_argument("--push-lua", help="Push and run a Lua script file")
    args = parser.parse_args()
    
    magi = MagiZoneAndroid(device_serial=args.serial)
    
    if not magi.check_device():
        print("[-] No device connected")
        sys.exit(1)
    
    if args.deploy:
        result = magi.deploy_runtime()
        print(f"Deploy: {result}")
    elif args.run:
        result = magi.execute_formula(args.run)
        print(f"Run: {result}")
    elif args.master:
        result = magi.execute_master_formula()
        print(f"Master: {result}")
    elif args.push_lua:
        script = Path(args.push_lua).read_text()
        name = Path(args.push_lua).name
        result = magi.push_and_run_lua(script, name)
        print(f"Push+Run: {result}")
    else:
        parser.print_help()
    
    magi.cleanup()


if __name__ == "__main__":
    main()
