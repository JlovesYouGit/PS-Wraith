#!/usr/bin/env python3
"""
Vemex CLARO Captive Portal Authenticator
=========================================
Authenticate through CLARO prepaid captive portal with masked headers.

Portal: https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal
Required fields: msisdn (phone number), cedula (ID number)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_captive_bypass import CaptivePortalBypass
    HAS_BYPASS = True
except ImportError:
    HAS_BYPASS = False


class ClaroPortalAuth:
    """Authenticate through CLARO prepaid portal with masked headers."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    DEFAULT_MSISDN = "8094298821"
    DEFAULT_CEDULA = "00112345678"

    MASKED_HEADERS = {
        "User-Agent": "AndroidDownloadManager/Android 16 (com.nothing.Launcher)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-DO,es-419;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Requested-With": "com.android.providers.media",
        "X-Forwarded-For": "10.0.0.1",
        "X-Original-URL": PORTAL_URL,
        "X-Carrier-Auth": "true",
        "Referer": "https://prepagoenlinea2.claro.com.do/",
    }

    def __init__(self, device_serial: str = "1bbfce51", bypass: Optional[CaptivePortalBypass] = None):
        self.device_serial = device_serial
        self.bypass = bypass or (CaptivePortalBypass(device_serial=device_serial) if HAS_BYPASS else None)
        self.auth_cookie: Optional[str] = None
        self.auth_token: Optional[str] = None

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def _build_curl_cmd(self, url: str, method: str = "GET", data: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> list:
        headers = dict(self.MASKED_HEADERS)
        if extra_headers:
            headers.update(extra_headers)

        cmd = [
            "adb", "-s", self.device_serial, "shell",
            "curl", "-s", "-k", "-L",
            "--interface", "rmnet_data1",
            "--max-time", "15",
            "-X", method,
        ]

        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

        if self.auth_cookie:
            cmd.extend(["-H", f"Cookie: {self.auth_cookie}"])

        if data:
            cmd.extend(["-d", data, "-H", "Content-Type: application/x-www-form-urlencoded"])

        cmd.append(url)
        return cmd

    def _execute_curl(self, url: str, method: str = "GET", data: Optional[str] = None) -> Dict[str, Any]:
        cmd = self._build_curl_cmd(url, method=method, data=data)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_portal_status(self) -> Dict[str, Any]:
        """Check if we're behind the captive portal."""
        result = self._execute_curl(self.PORTAL_URL)
        body = result.get("stdout", "")

        if "Autenticación" in body and "msisdn" in body:
            return {
                "behind_portal": True,
                "portal_url": self.PORTAL_URL,
                "action_required": "login",
                "fields": ["msisdn", "cedula"],
                "response_preview": body[:500],
            }

        if "Continuar" in body and "Autenticación" not in body:
            return {
                "behind_portal": False,
                "authenticated": True,
                "response_preview": body[:500],
            }

        return {
            "behind_portal": False,
            "authenticated": False,
            "response_preview": body[:500],
        }

    def authenticate(self, msisdn: str = DEFAULT_MSISDN, cedula: str = DEFAULT_CEDULA) -> Dict[str, Any]:
        """Authenticate with portal credentials."""
        data = f"msisdn={msisdn}&cedula={cedula}"

        result = self._execute_curl(self.PORTAL_URL, method="POST", data=data)
        body = result.get("stdout", "")

        # Look for session cookies or tokens
        cookie_match = re.search(r"Set-Cookie:\s*([^;]+)", body, re.IGNORECASE)
        if cookie_match:
            self.auth_cookie = cookie_match.group(1)

        token_match = re.search(r"name=\"(_csrf|csrf_token|authenticity_token)\"\s+value=\"([^\"]+)\"", body)
        if token_match:
            self.auth_token = token_match.group(2)

        authenticated = "Autenticación" not in body and "Continuar" in body

        return {
            "success": authenticated or result.get("success", False),
            "msisdn": msisdn,
            "cedula": cedula,
            "auth_cookie": self.auth_cookie,
            "auth_token": self.auth_token,
            "response_preview": body[:500],
            "raw_result": result,
        }

    def test_internet_access(self) -> Dict[str, Any]:
        """Test internet access after authentication."""
        test_urls = [
            "http://claro.com.do",
            "https://www.claro.com.do",
            "http://captive.apple.com",
            "https://neverssl.com",
        ]

        results = []
        for url in test_urls:
            r = self._execute_curl(url)
            results.append({
                "url": url,
                "success": r.get("success", False),
                "preview": r.get("stdout", "")[:200],
            })
            time.sleep(0.5)

        return {
            "device_serial": self.device_serial,
            "auth_cookie_present": self.auth_cookie is not None,
            "test_results": results,
        }

    def keepalive_loop(self, interval: float = 15.0) -> None:
        """Keep portal session alive."""
        while self.auth_cookie:
            self._execute_curl("http://claro.com.do")
            time.sleep(interval)

    def get_status(self) -> Dict[str, Any]:
        """Get current authentication status."""
        return {
            "device_serial": self.device_serial,
            "portal_url": self.PORTAL_URL,
            "authenticated": self.auth_cookie is not None,
            "auth_cookie_present": self.auth_cookie is not None,
            "auth_token_present": self.auth_token is not None,
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="CLARO Captive Portal Authenticator")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--check", action="store_true", help="Check portal status")
    parser.add_argument("--auth", action="store_true", help="Authenticate with default credentials")
    parser.add_argument("--msisdn", default=ClaroPortalAuth.DEFAULT_MSISDN, help="Phone number")
    parser.add_argument("--cedula", default=ClaroPortalAuth.DEFAULT_CEDULA, help="ID number")
    parser.add_argument("--test", action="store_true", help="Test internet access after auth")
    parser.add_argument("--keepalive", action="store_true", help="Start keepalive loop")
    args = parser.parse_args()

    auth = ClaroPortalAuth(device_serial=args.serial)

    if args.check:
        result = auth.check_portal_status()
        print(json.dumps(result, indent=2, default=str))
    elif args.auth:
        result = auth.authenticate(msisdn=args.msisdn, cedula=args.cedula)
        print(json.dumps(result, indent=2, default=str))
    elif args.test:
        result = auth.test_internet_access()
        print(json.dumps(result, indent=2, default=str))
    elif args.keepalive:
        auth.keepalive_loop()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
