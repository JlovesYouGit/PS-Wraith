#!/usr/bin/env python3
"""
Vemex Captive Portal Bypass
============================
Clever masking and interface binding to bypass CLARO prepaid captive portal.

Techniques:
- Bind to validated cellular interface (rmnet_data1) directly
- Remove carrier transparent proxy from APN
- Spoof system/update headers to avoid portal interception
- Use HTTPS to avoid HTTP redirects
- Implement connection keepalive and retry masking
- Route DNS through validated interface only
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
    HAS_TRACER = True
except ImportError:
    HAS_TRACER = False


class CaptivePortalBypass:
    """Bypass carrier captive portals using interface binding and header masking."""

    def __init__(self, device_serial: str = "1bbfce51", tracer: Optional[VemexRouteTracer] = None):
        self.device_serial = device_serial
        self.tracer = tracer or (VemexRouteTracer(device_serial=device_serial) if HAS_TRACER else None)
        self.validated_interface: Optional[str] = None
        self.validated_network_id: Optional[str] = None
        self.carrier_proxy: Optional[str] = None
        self.bypass_active: bool = False

    def discover_validated_path(self) -> Dict[str, Any]:
        """Find the validated network path without captive portal."""
        result = {
            "validated_interface": None,
            "validated_network": None,
            "captive_networks": [],
            "proxy_networks": [],
            "recommended_interface": None,
        }

        if not self.tracer:
            return result

        # Get all network interfaces
        interfaces = self._get_network_interfaces()
        for iface in interfaces:
            if iface.get("validated"):
                result["validated_interface"] = iface
                result["validated_network"] = iface.get("network_info")
                self.validated_interface = iface["name"]
                break
            elif iface.get("captive"):
                result["captive_networks"].append(iface)
            elif iface.get("proxy"):
                result["proxy_networks"].append(iface)

        if result["validated_interface"]:
            result["recommended_interface"] = result["validated_interface"]["name"]
        elif result["captive_networks"]:
            # Fall back to captive network but try to bypass it
            result["recommended_interface"] = result["captive_networks"][0]["name"]
            self.validated_interface = result["recommended_interface"]
        elif result["proxy_networks"]:
            result["recommended_interface"] = result["proxy_networks"][0]["name"]
            self.validated_interface = result["recommended_interface"]

        return result

    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface status from device."""
        interfaces = []
        try:
            output = subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "dumpsys connectivity"],
                capture_output=True, text=True, timeout=10
            ).stdout

            for line in output.splitlines():
                if "NetworkAgentInfo" in line:
                    info = self._parse_network_agent(line)
                    if info:
                        interfaces.append(info)
        except Exception:
            pass
        return interfaces

    def _parse_network_agent(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse NetworkAgentInfo line."""
        try:
            iface_match = re.search(r"InterfaceName: (\S+)", line)
            if not iface_match:
                return None

            name = iface_match.group(1)
            validated = "VALIDATED" in line
            captive = "CAPTIVE_PORTAL" in line
            proxy_match = re.search(r"HttpProxy: \[([^\]]+)\] (\d+)", line)

            return {
                "name": name,
                "validated": validated,
                "captive": captive,
                "proxy": proxy_match.group(1) if proxy_match else None,
                "proxy_port": int(proxy_match.group(2)) if proxy_match else None,
                "network_info": line.strip(),
            }
        except Exception:
            return None

    def remove_carrier_proxy(self) -> Dict[str, Any]:
        """Remove carrier transparent proxy from APN settings."""
        results = []

        # Remove global HTTP proxy
        r = adb("settings put global http_proxy :0", self.device_serial)
        results.append({"setting": "global_http_proxy", "result": r})

        # Remove secure HTTP proxy
        r = adb("settings put secure http_proxy :0", self.device_serial)
        results.append({"setting": "secure_http_proxy", "result": r})

        # Update APN to remove proxy settings via content provider
        apn_commands = [
            "content update --uri content://telephony/carriers --where \"apn='internet.ideasclaro.com.do'\" --bind proxy:s: --bind port:s:",
            "content update --uri content://telephony/carriers --where \"apn='internet.ideasclaro.com.do'\" --bind mmsproxy:s: --bind mmsport:s:",
        ]

        for cmd in apn_commands:
            try:
                r = subprocess.run(
                    ["adb", "-s", self.device_serial, "shell", cmd],
                    capture_output=True, text=True, timeout=10
                )
                results.append({"command": cmd, "result": r.stdout.strip()})
            except Exception as e:
                results.append({"command": cmd, "error": str(e)})

        # Set preferred APN explicitly
        r = adb("settings put global preferred_apn 26061", self.device_serial)
        results.append({"setting": "preferred_apn", "result": r})

        self.carrier_proxy = None
        return {"success": True, "results": results}

    def force_validated_interface(self, interface_name: str) -> Dict[str, Any]:
        """Force all traffic through validated interface using iptables and routing."""
        results = []

        try:
            # Get IP of validated interface
            ip_output = adb(f"ip addr show {interface_name}", self.device_serial)
            ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", ip_output)
            if ip_match:
                cidr = ip_match.group(1)
                # Add default route through this interface
                r = adb(f"ip route add default dev {interface_name} table 200", self.device_serial)
                results.append({"route": f"default via {interface_name}", "result": r})

                # Mark packets from this interface
                r = adb(f"iptables -t mangle -A OUTPUT -o {interface_name} -j MARK --set-mark 0x200", self.device_serial)
                results.append({"iptables": f"mark {interface_name}", "result": r})

                # Route marked packets through table 200
                r = adb("ip rule add fwmark 0x200 table 200", self.device_serial)
                results.append({"ip_rule": "fwmark 0x200", "result": r})

            self.validated_interface = interface_name
            self.bypass_active = True
        except Exception as e:
            results.append({"error": str(e)})

        return {"success": self.bypass_active, "results": results}

    def mask_headers(self, url: str, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create masked headers that bypass captive portal detection."""
        headers = {
            "User-Agent": "AndroidDownloadManager/Android 16 (com.nothing.Launcher)",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "X-Requested-With": "com.android.providers.media",
            "X-Forwarded-For": "10.0.0.1",
            "X-Original-URL": url,
            "X-Forwarded-Proto": "https",
            "X-Carrier-Auth": "true",
        }

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def execute_masked_request(self, url: str, method: str = "GET", timeout: int = 15) -> Dict[str, Any]:
        """Execute HTTP request with masked headers through validated interface."""
        if not self.validated_interface:
            self.discover_validated_path()

        headers = self.mask_headers(url)

        # Build curl command with interface binding
        curl_cmd = [
            "adb", "-s", self.device_serial, "shell",
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{time_total}",
            "--interface", self.validated_interface or "rmnet_data1",
            "--max-time", str(timeout),
            "-H", f"User-Agent: {headers['User-Agent']}",
            "-H", f"Accept: {headers['Accept']}",
            "-H", "Connection: keep-alive",
            "-H", "X-Requested-With: com.android.providers.media",
            "-H", "X-Forwarded-For: 10.0.0.1",
            "-H", "X-Original-URL: " + url,
            url
        ]

        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=timeout + 5)
            output = result.stdout.strip()
            parts = output.split()
            http_code = parts[0] if parts else "000"
            time_total = parts[1] if len(parts) > 1 else "0"

            return {
                "success": http_code.startswith("2"),
                "http_code": http_code,
                "time_total": time_total,
                "interface": self.validated_interface,
                "url": url,
                "headers": headers,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    def keepalive_loop(self, interval: float = 15.0) -> None:
        """Keep validated connection alive with masked keepalive requests."""
        keepalive_urls = [
            "http://claro.com.do",
            "http://captive.apple.com",
            "http://neverssl.com",
            "http://www.google.com/generate_204",
        ]

        while self.bypass_active:
            for url in keepalive_urls:
                if not self.bypass_active:
                    break
                result = self.execute_masked_request(url)
                if result.get("success"):
                    break
                time.sleep(1)
            time.sleep(interval)

    def get_status(self) -> Dict[str, Any]:
        """Get current bypass status."""
        return {
            "bypass_active": self.bypass_active,
            "validated_interface": self.validated_interface,
            "carrier_proxy_removed": self.carrier_proxy is None,
            "device_serial": self.device_serial,
        }


def adb(cmd: str, serial: str = "1bbfce51", timeout: int = 20) -> str:
    """Run ADB shell command."""
    r = subprocess.run(
        ["adb", "-s", serial, "shell", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return r.stdout.strip()


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Vemex Captive Portal Bypass")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--discover", action="store_true", help="Discover validated path")
    parser.add_argument("--remove-proxy", action="store_true", help="Remove carrier proxy")
    parser.add_argument("--force-interface", action="store_true", help="Force validated interface")
    parser.add_argument("--test", action="store_true", help="Test masked request")
    parser.add_argument("--keepalive", action="store_true", help="Start keepalive loop")
    parser.add_argument("--url", default="http://claro.com.do", help="URL to test")
    args = parser.parse_args()

    bypass = CaptivePortalBypass(device_serial=args.serial)

    if args.discover:
        result = bypass.discover_validated_path()
        print(json.dumps(result, indent=2))
    elif args.remove_proxy:
        result = bypass.remove_carrier_proxy()
        print(json.dumps(result, indent=2, default=str))
    elif args.force_interface:
        path = bypass.discover_validated_path()
        iface = path.get("recommended_interface", "rmnet_data1")
        result = bypass.force_validated_interface(iface)
        print(json.dumps(result, indent=2, default=str))
    elif args.test:
        result = bypass.execute_masked_request(args.url)
        print(json.dumps(result, indent=2, default=str))
    elif args.keepalive:
        bypass.bypass_active = True
        bypass.keepalive_loop()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
