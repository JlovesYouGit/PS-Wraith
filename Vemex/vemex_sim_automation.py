#!/usr/bin/env python3
"""
Vemex SIM Automation Module
============================
USSD/balance checks via Android telephony for the device.

Sandbox model:
- Isolated USSD/balance checks through Android telephony service
- No memory editing or game cheat functionality
- Device-side only via ADB/telephony APIs
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class USSDSession:
    code: str
    raw_response: str
    balance: Optional[str] = None
    currency: Optional[str] = None
    expiry: Optional[str] = None
    bonus: Optional[str] = None
    parsed: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class SIMAccountState:
    serial: str
    operator: str
    mcc_mnc: str
    sim_state: str
    ussd_sessions: List[USSDSession] = field(default_factory=list)
    data_registered: bool = False
    voice_registered: bool = False
    last_balance_check: Optional[float] = None


class VemexSIMAutomation:
    """USSD/balance automation sandbox for Android telephony."""

    BALANCE_CODES = {
        "interface_1": "*122#",
        "interface_2": "*112#",
    }

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.account = SIMAccountState(
            serial=device_serial,
            operator="CLARO DOM",
            mcc_mnc="37002",
            sim_state="LOADED",
        )

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def probe_telephony(self) -> Dict[str, Any]:
        """Read telephony state from device."""
        output = self._adb("dumpsys telephony.registry | grep -E 'mVoiceRegState|mDataRegState|mOperatorAlpha|mSimState' | head -n 5")
        voice = "UNKNOWN"
        data = "UNKNOWN"
        operator = ""
        sim_state = "UNKNOWN"

        for line in output.splitlines():
            if "mVoiceRegState=" in line:
                voice = line.split("mVoiceRegState=")[1].split(")")[0].strip() + ")"
            if "mDataRegState=" in line:
                data = line.split("mDataRegState=")[1].split(")")[0].strip() + ")"
            if "mOperatorAlphaLong=" in line:
                operator = line.split("mOperatorAlphaLong=")[1].split(",")[0].strip()
            if "mSimState=" in line:
                sim_state = line.split("mSimState=")[1].split(",")[0].strip()

        self.account.voice_registered = "IN_SERVICE" in voice or "0" == voice
        self.account.data_registered = "IN_SERVICE" in data or "0" == data
        self.account.operator = operator or self.account.operator
        self.account.sim_state = sim_state or self.account.sim_state

        return {
            "voice": voice,
            "data": data,
            "operator": self.account.operator,
            "sim_state": self.account.sim_state,
        }

    def send_ussd(self, code: str) -> USSDSession:
        """Send USSD code via telephony service."""
        session = USSDSession(code=code, raw_response="")

        try:
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "service", "call", "phone", "11", "i32", "0", "s16", code],
                capture_output=True, text=True, timeout=15,
            )
            session.raw_response = result.stdout.strip()
        except Exception as e:
            session.raw_response = f"ERROR: {e}"

        session = self._parse_ussd_response(session)
        self.account.ussd_sessions.append(session)
        return session

    def _parse_ussd_response(self, session: USSDSession) -> USSDSession:
        """Parse USSD response for balance/data."""
        text = session.raw_response

        balance_match = re.search(r"(\d+\.\d{2})\s*(USD|DOP|EUR|US\$)", text, re.IGNORECASE)
        if balance_match:
            session.balance = balance_match.group(1)
            session.currency = balance_match.group(2).upper()

        expiry_match = re.search(r"(?:exp|vence|vto|venc)[^\d]*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
        if expiry_match:
            session.expiry = expiry_match.group(1)

        bonus_match = re.search(r"bonus[^\d]*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if bonus_match:
            session.bonus = bonus_match.group(1)

        session.parsed = bool(session.balance or session.expiry or session.bonus)
        return session

    def check_balance(self, interface: str = "interface_1") -> Dict[str, Any]:
        """Check balance for specified interface."""
        code = self.BALANCE_CODES.get(interface, "*122#")
        session = self.send_ussd(code)
        self.account.last_balance_check = time.time()

        return {
            "interface": interface,
            "ussd_code": code,
            "balance": session.balance,
            "currency": session.currency,
            "expiry": session.expiry,
            "bonus": session.bonus,
            "raw_response": session.raw_response,
            "parsed": session.parsed,
            "timestamp": session.timestamp,
        }

    def check_all_balances(self) -> Dict[str, Any]:
        """Check balances for all interfaces."""
        results = {}
        for interface in self.BALANCE_CODES:
            results[interface] = self.check_balance(interface)
            time.sleep(1)
        return results

    def get_account_state(self) -> Dict[str, Any]:
        """Get full account state."""
        telephony = self.probe_telephony()
        return {
            "device_serial": self.account.serial,
            "operator": self.account.operator,
            "mcc_mnc": self.account.mcc_mnc,
            "sim_state": self.account.sim_state,
            "voice_registered": self.account.voice_registered,
            "data_registered": self.account.data_registered,
            "telephony": telephony,
            "ussd_sessions": [
                {
                    "code": s.code,
                    "balance": s.balance,
                    "currency": s.currency,
                    "expiry": s.expiry,
                    "bonus": s.bonus,
                    "parsed": s.parsed,
                    "timestamp": s.timestamp,
                }
                for s in self.account.ussd_sessions
            ],
            "last_balance_check": self.account.last_balance_check,
        }

    def run_backend_tests(self) -> Dict[str, Any]:
        """Run backend test suite for SIM automation."""
        results = {"tests": [], "passed": 0, "failed": 0}

        def test(name, condition, detail=""):
            passed = bool(condition)
            results["tests"].append({
                "name": name,
                "passed": passed,
                "detail": detail,
            })
            results["passed"] += int(passed)
            results["failed"] += int(not passed)
            return passed

        test("ADB_AVAILABLE", self._adb("echo ok") == "ok", "ADB connectivity")
        state = self.probe_telephony()
        test("VOICE_REGISTERED", state.get("voice") == "0(IN_SERVICE)", f"voice={state.get('voice')}")
        test("DATA_REGISTERED", state.get("data") == "0(IN_SERVICE)", f"data={state.get('data')}")
        test("OPERATOR_CLARO", "CLARO" in (state.get("operator") or "").upper(), f"operator={state.get('operator')}")
        test("SIM_LOADED", state.get("sim_state") == "LOADED", f"sim_state={state.get('sim_state')}")

        for interface, code in self.BALANCE_CODES.items():
            session = self.send_ussd(code)
            test(f"USSD_{interface}", bool(session.raw_response and "ERROR" not in session.raw_response), f"code={code}")
            time.sleep(0.5)

        return results

    def run_interface_tests(self) -> Dict[str, Any]:
        """Run interface/behavior test suite."""
        results = {"tests": [], "passed": 0, "failed": 0}

        def test(name, condition, detail=""):
            passed = bool(condition)
            results["tests"].append({
                "name": name,
                "passed": passed,
                "detail": detail,
            })
            results["passed"] += int(passed)
            results["failed"] += int(not passed)
            return passed

        balance_1 = self.check_balance("interface_1")
        test("BALANCE_INTERFACE_1", balance_1.get("balance") is not None or balance_1.get("parsed"), balance_1.get("raw_response", "")[:120])

        time.sleep(1)
        balance_2 = self.check_balance("interface_2")
        test("BALANCE_INTERFACE_2", balance_2.get("balance") is not None or balance_2.get("parsed"), balance_2.get("raw_response", "")[:120])

        account = self.get_account_state()
        test("ACCOUNT_STATE", bool(account.get("ussd_sessions")), f"sessions={len(account.get('ussd_sessions', []))}")
        test("OPERATOR_PRESENT", bool(account.get("operator")), f"operator={account.get('operator')}")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex SIM Automation")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--balance", action="store_true", help="Check all balances")
    parser.add_argument("--ussd", default=None, help="Send custom USSD code")
    parser.add_argument("--state", action="store_true", help="Show account state")
    parser.add_argument("--backend-tests", action="store_true", help="Run backend tests")
    parser.add_argument("--interface-tests", action="store_true", help="Run interface tests")
    args = parser.parse_args()

    sim = VemexSIMAutomation(device_serial=args.serial)

    if args.balance:
        result = sim.check_all_balances()
        print(json.dumps(result, indent=2, default=str))
    elif args.ussd:
        session = sim.send_ussd(args.ussd)
        print(json.dumps({
            "code": session.code,
            "raw_response": session.raw_response,
            "balance": session.balance,
            "currency": session.currency,
            "expiry": session.expiry,
            "bonus": session.bonus,
            "parsed": session.parsed,
        }, indent=2, default=str))
    elif args.state:
        result = sim.get_account_state()
        print(json.dumps(result, indent=2, default=str))
    elif args.backend_tests:
        result = sim.run_backend_tests()
        print(json.dumps(result, indent=2, default=str))
    elif args.interface_tests:
        result = sim.run_interface_tests()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
