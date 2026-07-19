#!/usr/bin/env python3
"""
Vemex WiFi Portal Balance Extractor
====================================
Extract balance/account data from WiFi-validated portal responses.

Since WiFi portal auth works and returns HTML with session cookies,
use it as the primary source for balance data when USSD returns binary.
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
    from vemex_ussd_auth_layer import USSDAuthLayer
    from vemex_permanent_balance_token import PermanentBalanceToken
    from vemex_frozen_balance import VemexFrozenBalance
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


@dataclass
class PortalBalanceData:
    balance: Optional[str] = None
    currency: str = "DOP"
    expiry: Optional[str] = None
    bonus: Optional[str] = None
    phone: Optional[str] = None
    customer_id: Optional[str] = None
    plan: Optional[str] = None
    raw_html: str = ""
    parsed: bool = False
    source: str = "wifi_portal"
    timestamp: float = field(default_factory=time.time)


class WiFiPortalBalanceExtractor:
    """Extract balance data from WiFi portal HTML responses."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    DEFAULT_SERIAL = "1bbfce51"

    def __init__(self, device_serial: str = DEFAULT_SERIAL, auth_layer: Optional[USSDAuthLayer] = None):
        self.device_serial = device_serial
        self.auth = auth_layer or (USSDAuthLayer(device_serial=device_serial) if HAS_VEMEX else None)
        self.token_mgr = PermanentBalanceToken(device_serial=device_serial, auth_layer=self.auth) if HAS_VEMEX else None
        self.frozen = VemexFrozenBalance(device_serial=device_serial, auth_layer=self.auth) if HAS_VEMEX else None
        self.session_cookie: Optional[str] = None
        self.last_extraction: Optional[PortalBalanceData] = None

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def _select_interface(self) -> str:
        """Prefer WiFi for portal extraction."""
        wifi_ip = self._adb("ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | head -n 1")
        if wifi_ip:
            return "wlan0"
        for iface in ["rmnet_data1", "rmnet_data2", "rmnet_data3", "rmnet_data4"]:
            ip = self._adb(f"ip addr show {iface} 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -n 1")
            if ip:
                return iface
        return "rmnet_data1"

    def authenticate_portal(self, msisdn: str = "8094298821", cedula: str = "00112345678") -> Dict[str, Any]:
        """Authenticate with portal and capture session cookie."""
        if self.auth:
            return self.auth.authenticate_portal(msisdn=msisdn, cedula=cedula)

        interface = self._select_interface()
        header_file = "/data/local/tmp/wifi_auth_headers.txt"
        cookie_file = "/data/local/tmp/wifi_auth_cookies.txt"
        body_file = "/data/local/tmp/wifi_auth_body.txt"

        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {interface} --max-time 20 "
            f"-c {cookie_file} -b {cookie_file} "
            f"-D {header_file} -o {body_file} "
            f"-X POST -d 'msisdn={msisdn}&cedula={cedula}' "
            f"-H 'Content-Type: application/x-www-form-urlencoded' "
            f"-H 'User-Agent: Android/16' "
            f"{self.PORTAL_URL}\""
        )

        try:
            subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
            cookies_raw = self._adb(f"cat {cookie_file} 2>/dev/null || echo ''")
            for line in cookies_raw.splitlines():
                if line.startswith("# ") or not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 7 and parts[5] == "agp-redirect-id":
                    self.session_cookie = f"agp-redirect-id={parts[6]}"
                    return {"success": True, "session_token": self.session_cookie}
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "no_session_cookie"}

    def extract_balance_from_portal(self, msisdn: str = "8094298821", cedula: str = "00112345678") -> PortalBalanceData:
        """Authenticate and extract balance from portal HTML."""
        extraction = PortalBalanceData()

        auth_result = self.authenticate_portal(msisdn=msisdn, cedula=cedula)
        if not auth_result.get("success"):
            extraction.raw_html = json.dumps({"auth_error": auth_result.get("error")})
            return extraction

        interface = self._select_interface()
        cookie_file = "/data/local/tmp/wifi_extract_cookies.txt"
        body_file = "/data/local/tmp/wifi_extract_body.txt"
        header_file = "/data/local/tmp/wifi_extract_headers.txt"

        cookie_arg = f"-c {cookie_file} -b {self.session_cookie or ''}"
        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {interface} --max-time 20 "
            f"{cookie_arg} -D {header_file} -o {body_file} "
            f"-H 'User-Agent: Android/16' "
            f"{self.PORTAL_URL}\""
        )

        try:
            subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
            html = self._adb(f"cat {body_file} 2>/dev/null || echo ''")
            extraction.raw_html = html
            extraction = self._parse_portal_html(html, extraction)
            extraction.source = "wifi_portal"
            extraction.timestamp = time.time()
            self.last_extraction = extraction
        except Exception as e:
            extraction.raw_html = json.dumps({"extraction_error": str(e)})

        return extraction

    def _parse_portal_html(self, html: str, extraction: PortalBalanceData) -> PortalBalanceData:
        """Parse portal HTML for balance and account data."""
        if not html or "Portal de Redireccionamiento" not in html:
            return extraction

        balance_patterns = [
            r"Saldo[:\s]+(\d{1,4}[.,]\d{2})",
            r"Balance[:\s]+(\d{1,4}[.,]\d{2})",
            r"\$?\s*(\d{1,4}[.,]\d{2})\s*(DOP|USD|EUR)",
            r"(\d{1,4}[.,]\d{2})\s*(DOP|USD|EUR)",
        ]

        for pattern in balance_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                raw_balance = match.group(1)
                extraction.balance = raw_balance.replace(",", ".")
                if len(match.groups()) > 1 and match.group(2):
                    extraction.currency = match.group(2).upper()
                break

        currency_match = re.search(r"(DOP|USD|EUR|US\$)", html, re.IGNORECASE)
        if currency_match and not extraction.currency:
            extraction.currency = currency_match.group(1).upper()

        expiry_patterns = [
            r"Venc[:\s]+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
            r"Exp[:\s]+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
            r"Válido[:\s]+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        ]
        for pattern in expiry_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                extraction.expiry = match.group(1)
                break

        bonus_match = re.search(r"Bonus[:\s]+(\d{1,4}[.,]\d{2})", html, re.IGNORECASE)
        if bonus_match:
            extraction.bonus = bonus_match.group(1).replace(",", ".")

        phone_match = re.search(r"(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})", html)
        if phone_match:
            extraction.phone = phone_match.group(1)

        customer_match = re.search(r"(?:Cliente|Customer|ID)[:\s]+([A-Z0-9]{6,})", html, re.IGNORECASE)
        if customer_match:
            extraction.customer_id = customer_match.group(1)

        plan_match = re.search(r"(?:Plan|Package)[:\s]+([A-Za-z0-9\s]+?)(?:<|$)", html, re.IGNORECASE)
        if plan_match:
            extraction.plan = plan_match.group(1).strip()

        extraction.parsed = bool(extraction.balance or extraction.expiry or extraction.bonus)
        return extraction

    def store_extraction_as_token(self, extraction: Optional[PortalBalanceData] = None) -> Dict[str, Any]:
        """Store extracted balance as permanent token."""
        if not HAS_VEMEX or not self.token_mgr:
            return {"success": False, "error": "no_token_manager"}

        extraction = extraction or self.last_extraction
        if not extraction or not extraction.balance:
            return {"success": False, "error": "no_balance_in_extraction"}

        return self.token_mgr.refresh_from_ussd("interface_1")

    def run_extraction_pipeline(self, msisdn: str = "8094298821", cedula: str = "00112345678") -> Dict[str, Any]:
        """Run full extraction pipeline."""
        report = {
            "device_serial": self.device_serial,
            "timestamp": time.time(),
            "steps": [],
        }

        print("[1/3] Authenticating portal...")
        auth_result = self.authenticate_portal(msisdn=msisdn, cedula=cedula)
        report["steps"].append({"step": "auth", "result": auth_result})
        print(f"  Authenticated: {auth_result.get('success')}")
        print(f"  Session: {auth_result.get('session_token')}")

        print("[2/3] Extracting balance from portal...")
        extraction = self.extract_balance_from_portal(msisdn=msisdn, cedula=cedula)
        report["steps"].append({"step": "extraction", "result": {
            "balance": extraction.balance,
            "currency": extraction.currency,
            "expiry": extraction.expiry,
            "bonus": extraction.bonus,
            "phone": extraction.phone,
            "customer_id": extraction.customer_id,
            "plan": extraction.plan,
            "parsed": extraction.parsed,
            "source": extraction.source,
        }})
        print(f"  Balance: {extraction.balance}")
        print(f"  Currency: {extraction.currency}")
        print(f"  Parsed: {extraction.parsed}")

        print("[3/3] Storing token...")
        token_result = self.store_extraction_as_token(extraction)
        report["steps"].append({"step": "token", "result": token_result})
        print(f"  Token action: {token_result.get('action')}")
        print(f"  Token ID: {token_result.get('token_id')}")

        return report

    def get_status(self) -> Dict[str, Any]:
        """Get extractor status."""
        return {
            "device_serial": self.device_serial,
            "session_cookie_present": self.session_cookie is not None,
            "last_extraction": {
                "balance": self.last_extraction.balance if self.last_extraction else None,
                "currency": self.last_extraction.currency if self.last_extraction else None,
                "parsed": self.last_extraction.parsed if self.last_extraction else False,
                "timestamp": self.last_extraction.timestamp if self.last_extraction else None,
            } if self.last_extraction else None,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex WiFi Portal Balance Extractor")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--extract", action="store_true", help="Extract balance from portal")
    parser.add_argument("--msisdn", default="8094298821", help="Phone number")
    parser.add_argument("--cedula", default="00112345678", help="ID number")
    parser.add_argument("--status", action="store_true", help="Show extractor status")
    args = parser.parse_args()

    extractor = WiFiPortalBalanceExtractor(device_serial=args.serial)

    if args.extract:
        result = extractor.run_extraction_pipeline(msisdn=args.msisdn, cedula=args.cedula)
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        result = extractor.get_status()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
