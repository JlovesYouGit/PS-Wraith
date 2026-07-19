#!/usr/bin/env python3
"""
Vemex USSD Auth Layer
=====================
Authentication layer between USSD requests and carrier responses.

Ensures the device is properly authenticated with the carrier before
USSD/balance checks, and matches returned values against expected state.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_sim_automation import VemexSIMAutomation, USSDSession
    HAS_SIM_AUTO = True
except ImportError:
    HAS_SIM_AUTO = False


@dataclass
class AuthState:
    device_serial: str
    authenticated: bool = False
    session_token: Optional[str] = None
    cookie_token: Optional[str] = None
    last_auth_time: Optional[float] = None
    auth_attempts: int = 0
    max_auth_attempts: int = 3
    auth_timeout: float = 300.0
    expected_balance: Optional[str] = None
    matched: bool = False


class USSDAuthLayer:
    """Auth layer for USSD/balance checks."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    DEFAULT_MSISDN = "8094298821"
    DEFAULT_CEDULA = "00112345678"

    def __init__(self, device_serial: str = "1bbfce51", sim_automation: Optional[VemexSIMAutomation] = None):
        self.device_serial = device_serial
        self.sim = sim_automation or (VemexSIMAutomation(device_serial=device_serial) if HAS_SIM_AUTO else None)
        self.auth_state = AuthState(device_serial=device_serial)
        self.ussd_responses: List[Dict[str, Any]] = []

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def is_session_valid(self) -> bool:
        """Check if auth session is still valid."""
        if not self.auth_state.authenticated:
            return False
        if self.auth_state.last_auth_time and (time.time() - self.auth_state.last_auth_time) > self.auth_state.auth_timeout:
            return False
        return True

    def _select_interface(self) -> str:
        """Select best available interface, preferring cellular."""
        for iface in ["rmnet_data1", "rmnet_data2", "rmnet_data3", "rmnet_data4"]:
            ip = self._adb(f"ip addr show {iface} 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -n 1")
            if ip:
                return iface
        
        wifi_ip = self._adb("ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -n 1")
        if wifi_ip:
            return "wlan0"
        
        return "rmnet_data1"

    def authenticate_portal(self, msisdn: str = DEFAULT_MSISDN, cedula: str = DEFAULT_CEDULA) -> Dict[str, Any]:
        """Authenticate with CLARO prepaid portal and capture session."""
        result = {
            "success": False,
            "authenticated": False,
            "session_token": None,
            "cookie_token": None,
            "response": None,
            "debug_measurement_id": None,
            "error": None,
        }

        if self.auth_state.auth_attempts >= self.auth_state.max_auth_attempts:
            result["error"] = "max_auth_attempts_reached"
            return result

        self.auth_state.auth_attempts += 1

        interface = self._select_interface()
        header_file = "/data/local/tmp/auth_layer_headers.txt"
        cookie_file = "/data/local/tmp/auth_layer_cookies.txt"

        body = f"msisdn={msisdn}&cedula={cedula}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Android/16",
            "X-Forwarded-For": "10.79.93.188",
        }

        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {interface} --max-time 15 "
            f"-c {cookie_file} -b {cookie_file} "
            f"-D {header_file} -o /dev/null "
            f"-X POST -d '{body}' "
            f"-H 'Content-Type: application/x-www-form-urlencoded' "
            f"-H 'User-Agent: Android/16' "
            f"-H 'X-Forwarded-For: 10.79.93.188' "
            f"{self.PORTAL_URL}\""
        )

        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            headers_raw = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
            cookies_raw = self._adb(f"cat {cookie_file} 2>/dev/null || echo ''")

            cookie_match = re.search(r"agp-redirect-id=([^;]+)", cookies_raw)
            if not cookie_match:
                cookie_match = re.search(r"agp-redirect-id=([^;\n\r]+)", cookies_raw)
            if not cookie_match:
                for line in cookies_raw.splitlines():
                    if line.startswith("# ") or not line.strip():
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 7 and parts[5] == "agp-redirect-id":
                        cookie_match = re.match(r"(.+)", parts[6])
                        break
            
            if cookie_match:
                self.auth_state.session_token = cookie_match.group(1)
                self.auth_state.cookie_token = f"agp-redirect-id={cookie_match.group(1)}"
                self.auth_state.authenticated = True
                self.auth_state.last_auth_time = time.time()
                result["success"] = True
                result["authenticated"] = True
                result["session_token"] = self.auth_state.session_token
                result["cookie_token"] = self.auth_state.cookie_token
                result["response"] = headers_raw[:500]
            else:
                result["error"] = "no_session_cookie"
                result["response"] = headers_raw[:500]
        except Exception as e:
            result["error"] = str(e)

        return result

    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid auth session."""
        if self.is_session_valid():
            return True
        result = self.authenticate_portal()
        if result.get("session_token"):
            self.auth_state.session_token = result["session_token"]
        if result.get("cookie_token"):
            self.auth_state.cookie_token = result["cookie_token"]
        self.auth_state.authenticated = result.get("authenticated", False)
        if self.auth_state.authenticated:
            self.auth_state.last_auth_time = time.time()
        return self.auth_state.authenticated

    def send_authenticated_ussd(self, code: str) -> Dict[str, Any]:
        """Send USSD with auth context and match expected balance."""
        if not self.ensure_authenticated():
            return {
                "code": code,
                "success": False,
                "error": "auth_failed",
                "raw_response": "",
                "balance": None,
                "matched": False,
            }

        session = self.sim.send_ussd(code) if self.sim else USSDSession(code=code, raw_response="")
        response = {
            "code": code,
            "success": bool(session.raw_response and "ERROR" not in session.raw_response),
            "raw_response": session.raw_response,
            "balance": session.balance,
            "currency": session.currency,
            "expiry": session.expiry,
            "bonus": session.bonus,
            "parsed": session.parsed,
            "timestamp": session.timestamp,
        }

        if session.balance and self.auth_state.expected_balance:
            response["matched"] = session.balance == self.auth_state.expected_balance
            self.auth_state.matched = response["matched"]
        elif session.balance:
            self.auth_state.expected_balance = session.balance
            response["matched"] = True
            self.auth_state.matched = True
        else:
            response["matched"] = False

        self.ussd_responses.append(response)
        return response

    def verify_balance_match(self, expected: str, actual: Optional[str]) -> Dict[str, Any]:
        """Verify balance matches expected value."""
        result = {
            "expected": expected,
            "actual": actual,
            "matched": False,
            "delta": None,
        }

        if actual is None:
            result["error"] = "no_actual_balance"
            return result

        try:
            exp_val = float(expected)
            act_val = float(actual)
            delta = round(abs(act_val - exp_val), 2)
            result["delta"] = round(act_val - exp_val, 2)
            result["matched"] = delta < 0.005
        except Exception as e:
            result["error"] = f"parse_error: {e}"

        self.auth_state.expected_balance = expected
        self.auth_state.matched = result["matched"]
        return result

    def run_authenticated_balance_check(self, interface: str = "interface_1") -> Dict[str, Any]:
        """Run balance check with auth layer."""
        if not self.ensure_authenticated():
            return {"success": False, "error": "auth_failed", "interface": interface}

        code_map = {
            "interface_1": "*122#",
            "interface_2": "*112#",
        }
        code = code_map.get(interface, "*122#")
        ussd_result = self.send_authenticated_ussd(code)

        match = None
        if ussd_result.get("balance") and self.auth_state.expected_balance:
            match = self.verify_balance_match(self.auth_state.expected_balance, ussd_result["balance"])

        return {
            "success": ussd_result.get("success", False),
            "interface": interface,
            "ussd_code": code,
            "ussd_result": ussd_result,
            "match": match,
            "auth": {
                "authenticated": self.auth_state.authenticated,
                "session_token": self.auth_state.session_token,
                "cookie_token": self.auth_state.cookie_token,
                "expected_balance": self.auth_state.expected_balance,
                "matched": self.auth_state.matched,
            },
        }

    def get_auth_state(self) -> Dict[str, Any]:
        """Get current auth state."""
        return {
            "device_serial": self.device_serial,
            "authenticated": self.auth_state.authenticated,
            "session_token": self.auth_state.session_token,
            "cookie_token": self.auth_state.cookie_token,
            "last_auth_time": self.auth_state.last_auth_time,
            "auth_attempts": self.auth_state.auth_attempts,
            "session_valid": self.is_session_valid(),
            "expected_balance": self.auth_state.expected_balance,
            "matched": self.auth_state.matched,
            "ussd_response_count": len(self.ussd_responses),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex USSD Auth Layer")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--auth", action="store_true", help="Authenticate with portal")
    parser.add_argument("--ussd", default=None, help="Send authenticated USSD code")
    parser.add_argument("--balance", action="store_true", help="Run authenticated balance check")
    parser.add_argument("--interface", default="interface_1", help="Balance interface")
    parser.add_argument("--state", action="store_true", help="Show auth state")
    parser.add_argument("--match", default=None, help="Verify balance against expected value")
    args = parser.parse_args()

    auth_layer = USSDAuthLayer(device_serial=args.serial)

    if args.auth:
        result = auth_layer.authenticate_portal()
        print(json.dumps(result, indent=2, default=str))
    elif args.ussd:
        result = auth_layer.send_authenticated_ussd(args.ussd)
        print(json.dumps(result, indent=2, default=str))
    elif args.balance:
        result = auth_layer.run_authenticated_balance_check(args.interface)
        print(json.dumps(result, indent=2, default=str))
    elif args.match:
        actual = auth_layer.send_authenticated_ussd("*122#" if args.interface == "interface_1" else "*112#").get("balance")
        result = auth_layer.verify_balance_match(args.match, actual)
        print(json.dumps(result, indent=2, default=str))
    elif args.state:
        result = auth_layer.get_auth_state()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
