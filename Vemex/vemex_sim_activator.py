#!/usr/bin/env python3
"""
Vemex SIM Network Activator
============================
Get SIM working on network when data/voice is OUT_OF_SERVICE.

Techniques:
- Force mobile data reconnection
- Set APN as current preferred
- Add default route through active rmnet interface
- Toggle airplane mode to force re-registration
- Power cycle SIM via radio commands
- Clear network state and rebuild
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_route_tracer import VemexRouteTracer
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


class SIMNetworkActivator:
    """Activate SIM data/voice on network."""

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def diagnose(self) -> Dict[str, Any]:
        """Diagnose current SIM/network state."""
        diag = {
            "service_state": {},
            "settings": {},
            "interfaces": {},
            "routes": {},
            "apn": {},
        }

        # Service state
        output = self._adb("dumpsys telephony.registry | grep -E 'mVoiceRegState|mDataRegState|mOperatorAlpha|mNetworkType|mSimState|mDataConnectionState|mDataEnabled' | head -n 10")
        diag["service_state"]["raw"] = output

        # Settings
        diag["settings"]["mobile_data"] = self._adb("settings get global mobile_data")
        diag["settings"]["airplane_mode"] = self._adb("settings get global airplane_mode_on")
        diag["settings"]["data_roaming"] = self._adb("settings get global data_roaming")
        diag["settings"]["preferred_apn"] = self._adb("settings get global preferred_apn")
        diag["settings"]["apn"] = self._adb("settings get global apn")
        diag["settings"]["sim_pin"] = self._adb("settings get secure sim_pin")
        diag["settings"]["sim_puk"] = self._adb("settings get secure sim_puk")

        # Interfaces
        for iface in ["rmnet_data1", "rmnet_data2", "rmnet_data4"]:
            state = self._adb(f"cat /sys/class/net/{iface}/operstate 2>/dev/null || echo unknown")
            ip = self._adb(f"ip addr show {iface} 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -n 1")
            diag["interfaces"][iface] = {"state": state, "ip": ip}

        # Routes
        diag["routes"]["default"] = self._adb("ip route show default")
        diag["routes"]["all"] = self._adb("ip route show")

        return diag

    def fix_apn_and_route(self) -> Dict[str, Any]:
        """Fix APN and routing."""
        results = []

        # Set preferred APN explicitly
        r = self._adb("settings put global preferred_apn 26061")
        results.append({"action": "set_preferred_apn", "result": r})

        # Force APN 26061 as current via content provider
        r = self._adb("content insert --uri content://telephony/carriers/current --bind apn_id:i:26061 2>/dev/null || true")
        results.append({"action": "set_current_apn", "result": r})

        # Add default route through rmnet_data4 if not present
        has_default = "default" in self._adb("ip route show default")
        if not has_default:
            r = self._adb("ip route add default via 10.79.93.189 dev rmnet_data4")
            results.append({"action": "add_default_route", "result": r})
        else:
            results.append({"action": "default_route_exists", "result": "skipped"})

        # Add DNS
        r = self._adb("setprop net.dns1 200.88.127.23")
        results.append({"action": "set_dns1", "result": r})
        r = self._adb("setprop net.dns2 196.3.81.5")
        results.append({"action": "set_dns2", "result": r})

        return {"success": True, "results": results}

    def toggle_airplane_mode(self) -> Dict[str, Any]:
        """Toggle airplane mode to force re-registration."""
        results = []

        # Turn on
        r = self._adb("settings put global airplane_mode_on 1")
        results.append({"action": "airplane_on", "result": r})

        # Broadcast intent
        r = self._adb("am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true 2>/dev/null || true")
        results.append({"action": "broadcast_airplane_on", "result": r})

        time.sleep(3)

        # Turn off
        r = self._adb("settings put global airplane_mode_on 0")
        results.append({"action": "airplane_off", "result": r})

        r = self._adb("am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false 2>/dev/null || true")
        results.append({"action": "broadcast_airplane_off", "result": r})

        time.sleep(5)

        return {"success": True, "results": results}

    def power_cycle_sim(self) -> Dict[str, Any]:
        """Power cycle SIM via radio commands."""
        results = []

        # Power off SIM slot 1
        r = self._adb("cmd phone set-sim-power 1 0 2>/dev/null || echo 'cmd phone not available'")
        results.append({"action": "sim_power_off", "result": r})

        time.sleep(2)

        # Power on SIM slot 1
        r = self._adb("cmd phone set-sim-power 1 1 2>/dev/null || echo 'cmd phone not available'")
        results.append({"action": "sim_power_on", "result": r})

        time.sleep(3)

        return {"success": True, "results": results}

    def reset_network(self) -> Dict[str, Any]:
        """Reset network state."""
        results = []

        # Toggle mobile data
        r = self._adb("svc data disable")
        results.append({"action": "data_disable", "result": r})
        time.sleep(1)
        r = self._adb("svc data enable")
        results.append({"action": "data_enable", "result": r})

        time.sleep(2)

        # Clear captive portal state
        r = self._adb("settings put global captive_portal_mode 0")
        results.append({"action": "captive_portal_mode", "result": r})
        r = self._adb("settings put global captive_portal_detection_enabled 0")
        results.append({"action": "captive_portal_detection", "result": r})

        # Remove proxy
        r = self._adb("settings put global http_proxy :0")
        results.append({"action": "remove_proxy", "result": r})

        return {"success": True, "results": results}

    def verify_connection(self) -> Dict[str, Any]:
        """Verify data connection."""
        results = []

        # Check registration
        output = self._adb("dumpsys telephony.registry | grep -E 'mVoiceRegState|mDataRegState|mOperatorAlpha' | head -n 3")
        results.append({"check": "registration", "output": output})

        # Check APN
        output = self._adb("content query --uri content://telephony/carriers --where 'carrier_enabled=1' --projection _id:name:apn:current | head -n 5")
        results.append({"check": "apn", "output": output})

        # Check connectivity
        output = self._adb("dumpsys connectivity | grep -E 'NetworkAgentInfo|VALIDATED|CONNECTED' | head -n 5")
        results.append({"check": "connectivity", "output": output})

        # Test HTTP
        r = self._adb("curl -s -k -L --interface rmnet_data4 --max-time 10 -o /dev/null -w '%{http_code} %{time_total}' http://claro.com.do")
        results.append({"check": "http_test", "output": r})

        return {"success": True, "results": results}

    def activate_sim(self) -> Dict[str, Any]:
        """Full SIM activation sequence."""
        report = {
            "device_serial": self.device_serial,
            "steps": [],
            "final_diagnosis": {},
        }

        print("[1/5] Diagnosing...")
        diag = self.diagnose()
        report["initial_diagnosis"] = diag
        print(f"  Mobile data: {diag['settings']['mobile_data']}")
        print(f"  Airplane: {diag['settings']['airplane_mode']}")
        print(f"  Data roaming: {diag['settings']['data_roaming']}")
        print(f"  Preferred APN: {diag['settings']['preferred_apn']}")

        print("[2/5] Fixing APN and routing...")
        apn_result = self.fix_apn_and_route()
        report["steps"].append({"step": "fix_apn_route", "result": apn_result})
        print(f"  APN/route fix: {'✓' if apn_result['success'] else '✗'}")

        print("[3/5] Resetting network...")
        reset_result = self.reset_network()
        report["steps"].append({"step": "reset_network", "result": reset_result})
        print(f"  Network reset: {'✓' if reset_result['success'] else '✗'}")

        print("[4/5] Toggling airplane mode...")
        air_result = self.toggle_airplane_mode()
        report["steps"].append({"step": "airplane_mode", "result": air_result})
        print(f"  Airplane toggle: {'✓' if air_result['success'] else '✗'}")

        print("[5/5] Power cycling SIM...")
        sim_result = self.power_cycle_sim()
        report["steps"].append({"step": "power_cycle_sim", "result": sim_result})
        print(f"  SIM power cycle: {'✓' if sim_result['success'] else '✗'}")

        print("[6/6] Verifying...")
        time.sleep(3)
        verify = self.verify_connection()
        report["final_diagnosis"] = verify
        print(f"  Verification complete")

        return report


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="SIM Network Activator")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--diagnose", action="store_true", help="Diagnose only")
    parser.add_argument("--activate", action="store_true", help="Full activation sequence")
    parser.add_argument("--fix-apn", action="store_true", help="Fix APN and route only")
    parser.add_argument("--reset", action="store_true", help="Reset network only")
    parser.add_argument("--airplane", action="store_true", help="Toggle airplane mode")
    parser.add_argument("--sim-power", action="store_true", help="Power cycle SIM")
    args = parser.parse_args()

    activator = SIMNetworkActivator(device_serial=args.serial)

    if args.diagnose:
        result = activator.diagnose()
        print(json.dumps(result, indent=2, default=str))
    elif args.fix_apn:
        result = activator.fix_apn_and_route()
        print(json.dumps(result, indent=2, default=str))
    elif args.reset:
        result = activator.reset_network()
        print(json.dumps(result, indent=2, default=str))
    elif args.airplane:
        result = activator.toggle_airplane_mode()
        print(json.dumps(result, indent=2, default=str))
    elif args.sim_power:
        result = activator.power_cycle_sim()
        print(json.dumps(result, indent=2, default=str))
    elif args.activate:
        result = activator.activate_sim()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
