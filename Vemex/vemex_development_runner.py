#!/usr/bin/env python3
"""
Vemex Development Runner
========================
Live development mode for SIM automation pipeline.

Connects to actual device, runs full pipeline:
portal auth -> USSD balance check -> token storage -> frozen mode
Outputs debug JSON for analysis.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))
from vemex_portal_debug_measure import PortalDebugMeasure
from vemex_permanent_balance_token import PermanentBalanceToken
from vemex_ussd_auth_layer import USSDAuthLayer
from vemex_frozen_balance import VemexFrozenBalance
from vemex_sim_automation import VemexSIMAutomation


class VemexDevelopmentRunner:
    """Live development runner for SIM automation pipeline."""

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.sim = VemexSIMAutomation(device_serial=device_serial)
        self.auth = USSDAuthLayer(device_serial=device_serial, sim_automation=self.sim)
        self.token_mgr = PermanentBalanceToken(device_serial=device_serial, auth_layer=self.auth)
        self.frozen = VemexFrozenBalance(device_serial=device_serial, auth_layer=self.auth)
        self.debug = PortalDebugMeasure(device_serial=device_serial)

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def run_pipeline(self, interface: str = "interface_1", enable_frozen: bool = False) -> Dict[str, Any]:
        """Run full development pipeline."""
        report = {
            "device_serial": self.device_serial,
            "timestamp": time.time(),
            "interface": interface,
            "steps": [],
        }

        print(f"[VEMEX DEV] Starting pipeline on {self.device_serial}")
        print(f"[VEMEX DEV] Interface: {interface}")

        # Step 1: Telephony state
        print("[1/5] Probing telephony...")
        telephony = self.sim.probe_telephony()
        report["steps"].append({"step": "telephony", "result": telephony})
        print(f"  Operator: {telephony.get('operator')}")
        print(f"  Voice: {telephony.get('voice')}")
        print(f"  Data: {telephony.get('data')}")

        # Step 2: Portal debug measurement
        print("[2/5] Measuring portal...")
        measurement = self.debug.measure_request(
            method="POST",
            body="msisdn=8094298821&cedula=00112345678",
        )
        report["steps"].append({"step": "portal_measurement", "result": {
            "measurement_id": measurement.measurement_id,
            "success": measurement.success,
            "status_code": measurement.response.status_code,
            "redirect_url": measurement.response.redirect_url,
            "cookies": measurement.response.cookies,
            "duration_ms": measurement.request.duration_ms,
            "notes": measurement.notes,
        }})
        print(f"  Status: {measurement.response.status_code}")
        print(f"  Redirect: {measurement.response.redirect_url}")
        print(f"  Cookies: {measurement.response.cookies}")

        # Step 3: Auth layer
        print("[3/5] Authenticating...")
        auth_result = self.auth.authenticate_portal()
        report["steps"].append({"step": "auth", "result": auth_result})
        print(f"  Authenticated: {auth_result.get('authenticated')}")
        print(f"  Session: {auth_result.get('session_token')}")

        # Step 4: Balance check and token storage
        print("[4/5] Checking balance and storing token...")
        token_result = self.token_mgr.refresh_from_ussd(interface)
        report["steps"].append({"step": "token", "result": token_result})
        print(f"  Action: {token_result.get('action')}")
        print(f"  Balance: {token_result.get('balance')}")
        print(f"  Token ID: {token_result.get('token_id')}")

        # Step 5: Frozen mode
        print("[5/5] Frozen mode...")
        if enable_frozen:
            frozen_result = self.frozen.enable_frozen_mode(
                token_result.get("balance", "197.94"),
                token_result.get("currency", "DOP"),
                interface,
            )
            report["steps"].append({"step": "frozen_enable", "result": frozen_result})
            print(f"  Frozen: {frozen_result.get('frozen_balance')}")
            print(f"  Hook: {frozen_result.get('telephony_hook_active')}")
        else:
            status = self.frozen.get_status()
            report["steps"].append({"step": "frozen_status", "result": status})
            print(f"  Frozen enabled: {status.get('frozen_enabled')}")

        # Save debug JSON
        debug_path = self.debug.save_measurements(f"dev_pipeline_{int(time.time())}.json")
        report["debug_saved_to"] = debug_path

        print(f"\n[VEMEX DEV] Pipeline complete")
        print(f"[VEMEX DEV] Debug JSON: {debug_path}")
        return report

    def run_monitor(self, interval: float = 30.0, iterations: int = 10) -> Dict[str, Any]:
        """Run monitoring loop."""
        report = {
            "device_serial": self.device_serial,
            "mode": "monitor",
            "interval": interval,
            "iterations": iterations,
            "samples": [],
        }

        print(f"[VEMEX DEV] Starting monitor: {iterations} iterations every {interval}s")
        for i in range(iterations):
            print(f"\n--- Iteration {i + 1}/{iterations} ---")
            sample = self.run_pipeline(enable_frozen=False)
            report["samples"].append(sample)
            if i < iterations - 1:
                time.sleep(interval)

        monitor_path = f"/data/local/tmp/vemex_dev_monitor_{int(time.time())}.json"
        try:
            with open("/tmp/vemex_dev_monitor.json", "w") as f:
                json.dump(report, f, indent=2)
            subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/vemex_dev_monitor.json", monitor_path],
                capture_output=True, text=True, timeout=10,
            )
            print(f"\n[VEMEX DEV] Monitor saved to {monitor_path}")
        except Exception:
            pass

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex Development Runner")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--interface", default="interface_1", help="Balance interface")
    parser.add_argument("--frozen", action="store_true", help="Enable frozen mode after pipeline")
    parser.add_argument("--monitor", action="store_true", help="Run monitoring loop")
    parser.add_argument("--interval", type=float, default=30.0, help="Monitor interval seconds")
    parser.add_argument("--iterations", type=int, default=10, help="Monitor iterations")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    runner = VemexDevelopmentRunner(device_serial=args.serial)

    if args.monitor:
        result = runner.run_monitor(interval=args.interval, iterations=args.iterations)
    else:
        result = runner.run_pipeline(interface=args.interface, enable_frozen=args.frozen)

    if args.json:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
