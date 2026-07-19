#!/usr/bin/env python3
"""
Vemex Cookie Cache Poison
=========================
Cookie/cache poisoning via transported request for captive portal bypass.

Techniques:
- Capture carrier portal cookies and replay them
- Poison WebView cache with fake 204 responses
- Multi-transport cookie rotation
- Header masking with uppi-m-ti patterns
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
    from vemex_captive_bypass import CaptivePortalBypass
    from vemex_global_coverage_mask import GlobalCoverageMask
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


class CookieCachePoison:
    """Cookie/cache poisoning for captive portal bypass."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    CONNECTIVITY_CHECK_URLS = [
        "http://connectivitycheck.android.com/generate_204",
        "http://clients3.google.com/generate_204",
        "http://www.google.com/generate_204",
    ]

    HEADER_PROFILES = {
        "android_download": {
            "User-Agent": "AndroidDownloadManager/Android 16 com.nothing.Launcher",
            "X-Requested-With": "com.android.providers.media",
        },
        "android_system": {
            "User-Agent": "Dalvik/2.1.0 Linux U Android 16 Nothing Phone 1",
            "X-Requested-With": "com.android.systemui",
        },
        "chrome_mobile": {
            "User-Agent": "Mozilla/5.0 Linux Android 16 Nothing Phone 1 AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "claro_app": {
            "User-Agent": "ClaroDominicana/1.0 Linux Android 16 Nothing Phone 1",
            "X-Requested-With": "com.claro.rd.autogestion",
        },
    }

    def __init__(self, device_serial: str = "1bbfce51"):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None
        self.bypass = CaptivePortalBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.mask = GlobalCoverageMask(device_serial=device_serial) if HAS_VEMEX else None
        self.captured_cookies: Dict[str, str] = {}
        self.poisoned: bool = False

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def capture_portal_cookies(self) -> Dict[str, str]:
        """Capture cookies from carrier portal via transported request."""
        cookies = {}
        cookie_file = "/data/local/tmp/portal_cookies.txt"

        # Step 1: GET portal to capture initial cookies
        self._adb(f"curl -s -k -L --interface rmnet_data1 --max-time 15 -c {cookie_file} {self.PORTAL_URL} > /dev/null 2>&1")

        # Step 2: Parse cookies from file
        try:
            output = self._adb(f"cat {cookie_file}")
            for line in output.splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    domain = parts[0].replace("#HttpOnly_", "")
                    name = parts[5]
                    value = parts[6]
                    cookies[name] = value
                    self.captured_cookies[name] = f"{domain}\t{value}"
        except Exception:
            pass

        # Step 3: POST with test credentials to capture session cookies
        post_cookie_file = "/data/local/tmp/portal_post_cookies.txt"
        self._adb(
            f"curl -s -k -L --interface rmnet_data1 --max-time 15 "
            f"-c {post_cookie_file} -b {cookie_file} "
            f"-X POST -d 'msisdn=8094298821&cedula=00112345678' "
            f"-H 'Content-Type: application/x-www-form-urlencoded' "
            f"-H 'User-Agent: Android/16' "
            f"{self.PORTAL_URL} > /dev/null 2>&1"
        )

        try:
            output = self._adb(f"cat {post_cookie_file}")
            for line in output.splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    cookies[name] = value
                    self.captured_cookies[name] = f"{parts[0]}\t{value}"
        except Exception:
            pass

        return cookies

    def poison_cache_with_204(self) -> Dict[str, Any]:
        """Poison WebView/cache with fake 204 responses for connectivity checks."""
        results = []

        # Create a fake 204 response file
        fake_204 = "HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n"

        # Try to inject via content providers
        cache_injections = [
            "content insert --uri content://cache --bind url:s:http://connectivitycheck.android.com/generate_204 --bind data:s:'HTTP/1.1 204 No Content' --bind mimetype:s:text/plain || true",
            "content insert --uri content://cache --bind url:s:http://clients3.google.com/generate_204 --bind data:s:'HTTP/1.1 204 No Content' --bind mimetype:s:text/plain || true",
            "content insert --uri content://browser/cache --bind url:s:http://connectivitycheck.android.com/generate_204 --bind data:s:'HTTP/1.1 204 No Content' || true",
        ]

        for cmd in cache_injections:
            try:
                r = self._adb(cmd)
                results.append({"command": cmd, "result": r})
            except Exception as e:
                results.append({"command": cmd, "error": str(e)})

        # Try to use curl to pre-cache responses
        for url in self.CONNECTIVITY_CHECK_URLS:
            try:
                # Save a fake 204 response locally
                r = self._adb(f"echo -e '{fake_204}' > /data/local/tmp/fake_204.txt")
                
                # Try to use content call to inject
                cmd = f"content call --uri content://cache --method put --arg '{url}' --extra 'data:s:{fake_204}' || true"
                r = self._adb(cmd)
                results.append({"cache_poison": url, "result": r})
            except Exception as e:
                results.append({"cache_poison": url, "error": str(e)})

        self.poisoned = True
        return {"success": self.poisoned, "results": results}

    def replay_cookies_across_transports(self) -> Dict[str, Any]:
        """Replay captured cookies across all transports."""
        if not self.captured_cookies:
            self.capture_portal_cookies()

        results = []
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.captured_cookies.items()])

        transports = ["rmnet_data1", "rmnet_data2", "rmnet_data4"]
        test_urls = [
            "http://claro.com.do",
            "http://connectivitycheck.android.com/generate_204",
            "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal",
        ]

        for transport in transports:
            for url in test_urls:
                cmd = (
                    f"adb -s {self.device_serial} shell "
                    f"\"curl -s -k -L --interface {transport} --max-time 15 "
                    f"-o /dev/null -w '%{{http_code}} %{{time_total}}' "
                    f"-H 'Cookie: {cookie_str}' "
                    f"-H 'User-Agent: Android/16' "
                    f"{url}\""
                )
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                    parts = result.stdout.strip().split()
                    results.append({
                        "transport": transport,
                        "url": url,
                        "http_code": parts[0] if parts else "000",
                        "time_total": parts[1] if len(parts) > 1 else "0",
                    })
                except Exception as e:
                    results.append({"transport": transport, "url": url, "error": str(e)})

        return {"success": True, "cookie_replay_results": results, "cookies_used": list(self.captured_cookies.keys())}

    def mask_with_cookies(self, url: str, transport: Optional[str] = None, profile: str = "android_download") -> Dict[str, Any]:
        """Execute masked request with captured cookies."""
        if not self.captured_cookies:
            self.capture_portal_cookies()

        transport = transport or self.mask._select_best_transport() if self.mask else "rmnet_data1"
        headers = self.HEADER_PROFILES.get(profile, self.HEADER_PROFILES["android_download"])
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.captured_cookies.items()])

        header_args = []
        for key, value in headers.items():
            header_args.append(f"-H '{key}: {value}'")
        header_args.append(f"-H 'Cookie: {cookie_str}'")

        header_str = " ".join(header_args)

        cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {transport} --max-time 15 "
            f"-o /dev/null -w '%{{http_code}} %{{time_total}}' "
            f"{header_str} {url}\""
        )

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            output = result.stdout.strip()
            parts = output.split()
            return {
                "success": parts[0].startswith("2") if parts else False,
                "http_code": parts[0] if parts else "000",
                "time_total": parts[1] if len(parts) > 1 else "0",
                "transport": transport,
                "profile": profile,
                "cookies_used": list(self.captured_cookies.keys()),
                "url": url,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    def get_status(self) -> Dict[str, Any]:
        """Get current poisoning status."""
        return {
            "device_serial": self.device_serial,
            "captured_cookies": list(self.captured_cookies.keys()),
            "poisoned": self.poisoned,
            "portal_url": self.PORTAL_URL,
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Vemex Cookie Cache Poison")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--capture", action="store_true", help="Capture portal cookies")
    parser.add_argument("--poison", action="store_true", help="Poison cache with 204 responses")
    parser.add_argument("--replay", action="store_true", help="Replay cookies across transports")
    parser.add_argument("--test", default="http://claro.com.do", help="Test URL with cookie poisoning")
    parser.add_argument("--profile", default="android_download", help="Header profile")
    args = parser.parse_args()

    poison = CookieCachePoison(device_serial=args.serial)

    if args.capture:
        result = poison.capture_portal_cookies()
        print(json.dumps(result, indent=2, default=str))
    elif args.poison:
        result = poison.poison_cache_with_204()
        print(json.dumps(result, indent=2, default=str))
    elif args.replay:
        result = poison.replay_cookies_across_transports()
        print(json.dumps(result, indent=2, default=str))
    else:
        result = poison.mask_with_cookies(args.test, profile=args.profile)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
