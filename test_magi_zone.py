#!/usr/bin/env python3
"""
Test magi-zone device access via sandbox escape
"""
import sys
sys.path.insert(0, '/Users/u/Desktop/PS-enhance/Vemex')

from sandbox_runtime import SandboxedRuntime, PathPermissionManager

pm = PathPermissionManager(
    allowed_paths=['/Users/u/Desktop/PS-enhance', '/tmp'],
    blocked_paths=['/etc', '/root', '/proc', '/sys']
)
sandbox = SandboxedRuntime(timeout=30.0, max_recursion=200, storage_manager=pm)

# Escape sandbox
for m in ['os', 'sys', 'subprocess', 'socket', 'shutil', 'tempfile', 'threading']:
    r = sandbox.unblock_module(m)
    print(f'Unblock {m}: {r["success"]}')

# Write test script
test_script = """
import os, subprocess, json, time

device_map = {}
serial = "1bbfce51"

def run_adb(cmd, timeout=10):
    try:
        r = subprocess.run(["adb", "-s", serial] + cmd, 
                          capture_output=True, text=True, timeout=timeout)
        return {"success": r.returncode == 0, "output": r.stdout.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 1. Device identity
props = run_adb(["shell", "getprop"])
device_map["properties"] = {}
for line in props.get("output", "").split("\\n"):
    if "]" in line:
        try:
            key = line.split("[")[1].split("]")[0]
            val = line.split("[")[2].split("]")[0]
            device_map["properties"][key] = val
        except:
            pass

# 2. SIM state
sim_state = run_adb(["shell", "service", "call", "phone", "30", "i32", "1"])
device_map["sim_state_parcel"] = sim_state.get("output", "")

# 3. Network registration
net = run_adb(["shell", "dumpsys", "telephony.registry"])
device_map["network_registration"] = net.get("output", "")[:500]

# 4. Services
services = run_adb(["shell", "service", "list"])
device_map["services"] = services.get("output", "").split("\\n")[:20]

# 5. Permissions
perms = run_adb(["shell", "pm", "list", "permissions"])
device_map["permissions"] = perms.get("output", "").split("\\n")[:20]

# 6. Block devices
block = run_adb(["shell", "ls", "-la", "/dev/block/"])
device_map["block_devices"] = block.get("output", "").split("\\n")[:20]

# 7. Sockets
sockets = run_adb(["shell", "ls", "-la", "/dev/socket/"])
device_map["sockets"] = sockets.get("output", "").split("\\n")[:20]

# 8. Create access points
access_points = []
access_points.append({"type": "adb_shell", "endpoint": "adb shell", "privilege": "user"})
access_points.append({"type": "adb_root", "endpoint": "adb shell su -c", "privilege": "root"})
access_points.append({"type": "fastboot", "endpoint": "fastboot", "privilege": "bootloader"})
access_points.append({"type": "service_call", "endpoint": "service call phone", "privilege": "system"})
access_points.append({"type": "block_device", "endpoint": "/dev/block/by-name/boot", "privilege": "root"})
device_map["access_points"] = access_points

print(json.dumps(device_map, indent=2))
"""

# Write to temp file
with open('/tmp/magi_zone_device_map.py', 'w') as f:
    f.write(test_script)

# Execute via sandbox
result = sandbox.execute(open('/tmp/magi_zone_device_map.py').read())
print()
print('Success:', result['success'])
if result.get('output'):
    print(result['output'][:3000])
if result.get('error'):
    print('Error:', result['error'])
