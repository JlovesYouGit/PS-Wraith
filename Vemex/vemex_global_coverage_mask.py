#!/usr/bin/env python3
"""
Vemex Global Coverage Mask
===========================
Multi-transport, multi-location network masking for cellular bypass.

Compatibility with uppi-m-ti patterns:
- Reuses Vemex route tracer for live connection keepalive
- Implements header masking based on uppi-m-ti proxy patterns
- Supports multi-APN fallback for global coverage
- No rate-limit patterns from uppi-m-ti traffic controller
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_route_tracer import VemexRouteTracer
    from vemex_captive_bypass import CaptivePortalBypass
    HAS_VEMEX = True
except ImportError:
    HAS_VEMEX = False


class GlobalCoverageMask:
    """Multi-transport network masking for cellular bypass."""

    DEFAULT_SERIAL = "1bbfce51"
    TRANSPORTS = ["rmnet_data1", "rmnet_data2", "rmnet_data4", "wlan0"]
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

    def __init__(self, device_serial: str = DEFAULT_SERIAL):
        self.device_serial = device_serial
        self.tracer = VemexRouteTracer(device_serial=device_serial) if HAS_VEMEX else None
        self.bypass = CaptivePortalBypass(device_serial=device_serial) if HAS_VEMEX else None
        self.active_transport: Optional[str] = None
        self.active_profile: Optional[str] = None
        self.keepalive_running: bool = False

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()

    def discover_transports(self) -> Dict[str, Any]:
        """Discover all available network transports."""
        transports = {}
        for iface in self.TRANSPORTS:
            state = self._adb(f"cat /sys/class/net/{iface}/operstate 2>/dev/null || echo unknown")
            ip = self._adb(f"ip addr show {iface} 2>/dev/null | grep 'inet ' | awk '{{print $2}}' | head -n 1")
            transports[iface] = {
                "state": state,
                "ip": ip,
                "available": bool(ip),
            }
        return transports

    def probe_apns(self) -> List[Dict[str, Any]]:
        """Probe all enabled APNs and test connectivity."""
        apns = []
        try:
            output = self._adb("content query --uri content://telephony/carriers --where \"carrier_enabled=1\" --projection _id:name:apn:type:current")
            for line in output.splitlines():
                if not line.startswith("Row:"):
                    continue
                apns.append(self._parse_apn_line(line))
        except Exception:
            pass
        return apns

    def _parse_apn_line(self, line: str) -> Dict[str, Any]:
        info = {"raw": line}
        m = re.search(r"_id=(\d+)", line)
        info["id"] = int(m.group(1)) if m else None
        m = re.search(r"name=([^,]+)", line)
        info["name"] = m.group(1) if m else None
        m = re.search(r"apn=([^,]+)", line)
        info["apn"] = m.group(1) if m else None
        m = re.search(r"type=([^,]+)", line)
        info["type"] = m.group(1) if m else None
        return info

    def mask_request(self, url: str, transport: Optional[str] = None, profile: Optional[str] = None) -> Dict[str, Any]:
        """Execute HTTP request with masked headers and transport binding."""
        transport = transport or self._select_best_transport()
        profile = profile or "android_download"
        headers = self.HEADER_PROFILES.get(profile, self.HEADER_PROFILES["android_download"])

        header_args = []
        for key, value in headers.items():
            header_args.append(f"-H '{key}: {value}'")

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
            http_code = parts[0] if parts else "000"
            time_total = parts[1] if len(parts) > 1 else "0"

            return {
                "success": http_code.startswith("2"),
                "http_code": http_code,
                "time_total": time_total,
                "transport": transport,
                "profile": profile,
                "url": url,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "url": url, "transport": transport}

    def _select_best_transport(self) -> str:
        """Select best available transport."""
        if self.bypass and self.bypass.validated_interface:
            return self.bypass.validated_interface
        if self.tracer:
            path = self.tracer.discover_device_routes()
            if path.get("adb_route"):
                return "rmnet_data1"
        return "rmnet_data4"

    def start_keepalive(self, interval: float = 15.0) -> None:
        """Start masked keepalive loop."""
        self.keepalive_running = True
        while self.keepalive_running:
            self.mask_request("http://claro.com.do")
            time.sleep(interval)

    def stop_keepalive(self) -> None:
        """Stop keepalive loop."""
        self.keepalive_running = False

    def get_status(self) -> Dict[str, Any]:
        """Get current mask status."""
        transports = self.discover_transports()
        return {
            "device_serial": self.device_serial,
            "active_transport": self.active_transport,
            "active_profile": self.active_profile,
            "keepalive_running": self.keepalive_running,
            "transports": transports,
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Vemex Global Coverage Mask")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--discover", action="store_true", help="Discover transports")
    parser.add_argument("--apns", action="store_true", help="List APNs")
    parser.add_argument("--test", default="http://claro.com.do", help="Test URL")
    parser.add_argument("--transport", default=None, help="Force transport")
    parser.add_argument("--profile", default="android_download", help="Header profile")
    parser.add_argument("--keepalive", action="store_true", help="Start keepalive")
    args = parser.parse_args()

    mask = GlobalCoverageMask(device_serial=args.serial)

    if args.discover:
        result = mask.discover_transports()
        print(json.dumps(result, indent=2))
    elif args.apns:
        result = mask.probe_apns()
        print(json.dumps(result, indent=2))
    elif args.keepalive:
        mask.start_keepalive()
    else:
        result = mask.mask_request(args.test, transport=args.transport, profile=args.profile)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
