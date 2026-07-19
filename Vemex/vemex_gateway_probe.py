#!/usr/bin/env python3
"""
Vemex Gateway Probe
===================
Professional active-watchdog gateway probing with age-counter analysis.

Probes from the active carrier gateway interface (rmnet_data4 / 3n4o5p6:8080)
and analyzes response vectors, timing, and session state to extract credentials
or determine bypass viability.
"""

from __future__ import annotations

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


class GatewayProbe:
    """Professional gateway probe with age-counter and watchdog analysis."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    GATEWAY_INTERFACE = "rmnet_data4"
    GATEWAY_PROXY = "3n4o5p6:8080"

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
    }

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None
        self.bypass = CaptivePortalBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.mask = GlobalCoverageMask(device_serial=device_serial) if HAS_VEMEX else None

        self.session_cookies: Dict[str, str] = {}
        self.response_vectors: List[Dict[str, Any]] = []
        self.age_counters: Dict[str, float] = {}
        self.watchdog_counters: Dict[str, int] = {}
        self.proxy_behavior: Dict[str, Any] = {}
        self.transport = self.GATEWAY_INTERFACE

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
        header_file: str = "/data/local/tmp/gateway_probe_headers.txt",
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

    def analyze_response_vectors(self, response_body: str, response_headers: str, url: str, elapsed: float) -> Dict[str, Any]:
        """Analyze response vectors with age-counter and timing data."""
        vectors: Dict[str, Any] = {
            "url": url,
            "timestamp": time.time(),
            "age_counter": elapsed,
            "forms": [],
            "inputs": [],
            "tokens": [],
            "cookies": [],
            "redirects": [],
            "states": [],
            "headers": [],
            "timing_markers": [],
        }

        # Parse response headers
        for line in response_headers.splitlines():
            if line.lower().startswith("set-cookie:"):
                cookie_part = line.split(":", 1)[1].strip()
                name_value = cookie_part.split(";")[0].strip()
                vectors["cookies"].append(name_value)
            if line.lower().startswith("location:"):
                vectors["redirects"].append(line.split(":", 1)[1].strip())
            vectors["headers"].append(line)

        # Extract forms and inputs
        for match in re.finditer(r"<form[^>]*>(.*?)</form>", response_body, re.IGNORECASE | re.DOTALL):
            vectors["forms"].append(match.group(0)[:500])

        for match in re.finditer(r"<input[^>]*name=['\"]([^'\"]+)['\"][^>]*>", response_body, re.IGNORECASE):
            vectors["inputs"].append(match.group(1))

        # Extract tokens
        for pattern in [
            r"name=['\"](_csrf|csrf_token|authenticity_token)['\"][^>]*value=['\"]([^'\"]+)['\"]",
            r"value=['\"]([a-f0-9]{32,})['\"][^>]*name=['\"](_csrf|csrf_token)['\"]",
            r"(session[id|token|key])[\":= ]+([a-f0-9]{16,})",
        ]:
            for match in re.finditer(pattern, response_body, re.IGNORECASE):
                vectors["tokens"].append({"type": match.group(1), "value": match.group(2)})

        # Detect states
        if "El documento es incorrecto" in response_body:
            vectors["states"].append("document_error")
        if "Autenticación" in response_body and "msisdn" in response_body:
            vectors["states"].append("login_form_present")
        if "Continuar" in response_body and "Autenticación" not in response_body:
            vectors["states"].append("auth_success")
        if "feedbackPanel" in response_body and "error" in response_body:
            vectors["states"].append("validation_error")

        # Age-counter analysis
        vectors["timing_markers"].append({
            "event": "response_received",
            "elapsed": elapsed,
            "size": len(response_body),
        })

        return vectors

    def probe_gateway(self, probe_count: int = 5) -> Dict[str, Any]:
        """Probe the active gateway with age-counter analysis."""
        probe_results = []
        session_timeline: List[Dict[str, Any]] = []

        for i in range(probe_count):
            start = time.time()
            header_file = f"/data/local/tmp/gateway_probe_{i}_headers.txt"
            body_file = f"/data/local/tmp/gateway_probe_{i}_body.txt"

            cmd = self._build_curl_cmd(
                self.PORTAL_URL,
                profile="android_download",
                save_headers=True,
                header_file=header_file,
            )
            result = self._execute_curl(cmd)

            elapsed = time.time() - start
            headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
            body = self._adb(f"cat {body_file} 2>/dev/null || echo ''")

            if not body:
                body = self._adb(
                    f"curl -s -k -L --interface {self.transport} --max-time 15 "
                    f"-H 'User-Agent: Android/16' {self.PORTAL_URL} 2>/dev/null"
                )

            vectors = self.analyze_response_vectors(body, headers, self.PORTAL_URL, elapsed)

            probe_id = f"gateway_probe_{i}_{int(start)}"
            self.watchdog_counters[probe_id] = self.watchdog_counters.get(probe_id, 0) + 1
            self.age_counters[probe_id] = start

            probe_results.append({
                "probe_id": probe_id,
                "watchdog_counter": self.watchdog_counters[probe_id],
                "age_counter": start,
                "elapsed": elapsed,
                "http_code": result.get("http_code"),
                "time_total": result.get("time_total"),
                "vectors": vectors,
            })

            session_timeline.append({
                "timestamp": start,
                "probe_id": probe_id,
                "http_code": result.get("http_code"),
                "states": vectors.get("states", []),
                "cookies_captured": len(vectors.get("cookies", [])),
                "tokens_captured": len(vectors.get("tokens", [])),
            })

            if i < probe_count - 1:
                time.sleep(0.5)

        return {
            "gateway_interface": self.transport,
            "gateway_proxy": self.GATEWAY_PROXY,
            "portal_url": self.PORTAL_URL,
            "probe_count": len(probe_results),
            "probe_results": probe_results,
            "session_timeline": session_timeline,
            "watchdog_counters": dict(self.watchdog_counters),
            "age_counters": {k: time.time() - v for k, v in self.age_counters.items()},
        }

    def extract_credentials_from_vectors(self, vectors: Dict[str, Any]) -> Dict[str, Any]:
        """Extract credentials from response vectors."""
        credentials: Dict[str, Any] = {
            "cookies": {},
            "tokens": {},
            "forms": [],
            "potential_msisdn": None,
            "potential_cedula": None,
        }

        # Extract cookies
        for cookie in vectors.get("cookies", []):
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                credentials["cookies"][name.strip()] = value.strip()

        # Extract tokens
        for token in vectors.get("tokens", []):
            credentials["tokens"][token["type"]] = token["value"]

        # Extract form fields
        for form in vectors.get("forms", []):
            credentials["forms"].append(form[:200])

        return credentials

    def feed_payload_with_age_counter(self, payload: str, age_counter: float) -> Dict[str, Any]:
        """Feed payload with age-counter timing."""
        ts = int(age_counter)
        aged_payload = f"{payload}&_ts={ts}&_wc={self.watchdog_counters.get('active', 0)}"

        header_file = "/data/local/tmp/aged_payload_headers.txt"
        cmd = self._build_curl_cmd(
            self.PORTAL_URL,
            method="POST",
            data=aged_payload,
            profile="claro_app",
            save_headers=True,
            header_file=header_file,
        )
        result = self._execute_curl(cmd)

        headers = self._adb(f"cat {header_file} 2>/dev/null || echo ''")
        body = self._adb(
            f"curl -s -k -L --interface {self.transport} --max-time 15 "
            f"-X POST -d '{aged_payload}' "
            f"-H 'Content-Type: application/x-www-form-urlencoded' "
            f"-H 'User-Agent: ClaroDominicana/1.0' {self.PORTAL_URL} 2>/dev/null"
        )

        vectors = self.analyze_response_vectors(body, headers, self.PORTAL_URL, float(result.get("time_total", 0)))
        credentials = self.extract_credentials_from_vectors(vectors)

        return {
            "payload_length": len(aged_payload),
            "age_counter": ts,
            "watchdog_counter": self.watchdog_counters.get("active", 0),
            "result": result,
            "vectors": vectors,
            "credentials_extracted": credentials,
            "body_preview": body[:500],
        }

    def get_status(self) -> Dict[str, Any]:
        """Get gateway probe status."""
        return {
            "device_serial": self.device_serial,
            "gateway_interface": self.transport,
            "gateway_proxy": self.GATEWAY_PROXY,
            "portal_url": self.PORTAL_URL,
            "session_cookies": list(self.session_cookies.keys()),
            "watchdog_counters": dict(self.watchdog_counters),
            "age_counters": {k: time.time() - v for k, v in self.age_counters.items()},
            "response_vectors_count": len(self.response_vectors),
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Vemex Gateway Probe")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--probe", action="store_true", help="Probe gateway with age-counter analysis")
    parser.add_argument("--feed", default="msisdn=8094298821&cedula=00112345678", help="Payload to feed with age counter")
    parser.add_argument("--status", action="store_true", help="Show gateway probe status")
    args = parser.parse_args()

    probe = GatewayProbe(device_serial=args.serial)

    if args.probe:
        result = probe.probe_gateway()
        print(json.dumps(result, indent=2, default=str))
    elif args.feed:
        result = probe.feed_payload_with_age_counter(args.feed, time.time())
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        result = probe.get_status()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
