#!/usr/bin/env python3
"""
Vemex Portal Debug Measure
==========================
Capture portal request/response details for debugging and analysis.

Stores measured data as JSON to understand what is actually being
transferred, which helps fix interpreter/parser issues.
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
class PortalRequest:
    url: str
    method: str
    headers: Dict[str, str]
    body: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    interface: str = "rmnet_data4"
    duration_ms: Optional[float] = None


@dataclass
class PortalResponse:
    status_code: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    redirect_url: Optional[str] = None
    cookies: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    raw: str = ""


@dataclass
class PortalMeasurement:
    measurement_id: str
    request: PortalRequest
    response: PortalResponse
    success: bool = False
    error: Optional[str] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PortalDebugMeasure:
    """Measure and store portal traffic for debugging."""

    PORTAL_URL = "https://prepagoenlinea2.claro.com.do/autogestionprepago/LimitPortal"
    DEFAULT_SERIAL = "1bbfce51"
    DEBUG_DIR = "/data/local/tmp/vemex_portal_debug"

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

    def __init__(self, device_serial: str = DEFAULT_SERIAL):
        self.device_serial = device_serial
        self.measurements: List[PortalMeasurement] = []
        self._ensure_debug_dir()

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def _ensure_debug_dir(self) -> None:
        self._adb(f"mkdir -p {self.DEBUG_DIR}")

    def measure_request(
        self,
        url: str = PORTAL_URL,
        method: str = "POST",
        body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        interface: Optional[str] = None,
        save_body: bool = True,
    ) -> PortalMeasurement:
        """Send request and capture full details."""
        measurement_id = f"portal_meas_{int(time.time() * 1000)}"
        header_file = f"{self.DEBUG_DIR}/{measurement_id}_headers.txt"
        body_file = f"{self.DEBUG_DIR}/{measurement_id}_body.txt"
        cookie_file = f"{self.DEBUG_DIR}/{measurement_id}_cookies.txt"

        if interface is None:
            interface = self._select_interface()

        request = PortalRequest(
            url=url,
            method=method,
            headers=headers or {},
            body=body,
            interface=interface,
            timestamp=time.time(),
        )

        curl_cmd = (
            f"adb -s {self.device_serial} shell "
            f"\"curl -s -k -L --interface {interface} --max-time 20 "
            f"-D {header_file} "
        )
        if save_body:
            curl_cmd += f"-o {body_file} "
        else:
            curl_cmd += "-o /dev/null "

        curl_cmd += f"-w '%{{http_code}} %{{time_total}} %{{redirect_url}}' "

        if method == "POST" and body:
            curl_cmd += f"-X POST -d '{body}' "
            curl_cmd += "-H 'Content-Type: application/x-www-form-urlencoded' "

        for key, value in (headers or {}).items():
            curl_cmd += f"-H '{key}: {value}' "

        curl_cmd += f"-c {cookie_file} {url}\""

        response = PortalResponse()
        start = time.time()
        try:
            result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True, timeout=25)
            duration = (time.time() - start) * 1000
            request.duration_ms = duration

            parts = result.stdout.strip().split()
            response.status_code = int(parts[0]) if parts and parts[0].isdigit() else None
            if len(parts) > 1:
                try:
                    request.duration_ms = float(parts[1]) * 1000
                except ValueError:
                    pass
            if len(parts) > 2 and parts[2].startswith("http"):
                response.redirect_url = parts[2]

            response.raw = self._read_device_file(header_file)
            response.headers = self._parse_headers(response.raw)
            if save_body:
                response.body = self._read_device_file(body_file)
            response.cookies = self._parse_cookies(self._read_device_file(cookie_file))
            response.timestamp = time.time()

            for key, value in response.headers.items():
                if key.lower() == "location":
                    response.redirect_url = value
                    break
        except Exception as e:
            measurement = PortalMeasurement(
                measurement_id=measurement_id,
                request=request,
                response=response,
                success=False,
                error=str(e),
            )
            self.measurements.append(measurement)
            return measurement

        success = response.status_code is not None and 200 <= response.status_code < 400
        measurement = PortalMeasurement(
            measurement_id=measurement_id,
            request=request,
            response=response,
            success=success,
            notes=self._generate_notes(response),
        )
        self.measurements.append(measurement)
        return measurement

    def _read_device_file(self, path: str) -> str:
        return self._adb(f"cat {path} 2>/dev/null || echo ''")

    def _parse_headers(self, raw: str) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        for line in raw.splitlines():
            if ":" in line and not line.startswith("{"):
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        return headers

    def _parse_cookies(self, raw: str) -> List[str]:
        cookies: List[str] = []
        for line in raw.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies.append(f"{parts[5]}={parts[6]}")
        return cookies

    def _generate_notes(self, response: PortalResponse) -> str:
        notes = []
        if response.redirect_url:
            notes.append(f"redirects to {response.redirect_url}")
        if response.status_code == 302:
            notes.append("302 redirect")
        if "captive" in (response.body or "").lower():
            notes.append("captive portal detected")
        if "el documento es incorrecto" in (response.body or "").lower():
            notes.append("carrier returned error page")
        return "; ".join(notes) if notes else "ok"

    def save_measurements(self, filename: str = "portal_measurements.json") -> str:
        """Save all measurements to JSON."""
        payload = {
            "device_serial": self.device_serial,
            "portal_url": self.PORTAL_URL,
            "measurement_count": len(self.measurements),
            "measurements": [
                {
                    "measurement_id": m.measurement_id,
                    "success": m.success,
                    "error": m.error,
                    "notes": m.notes,
                    "request": {
                        "url": m.request.url,
                        "method": m.request.method,
                        "headers": m.request.headers,
                        "body": m.request.body,
                        "timestamp": m.request.timestamp,
                        "interface": m.request.interface,
                        "duration_ms": m.request.duration_ms,
                    },
                    "response": {
                        "status_code": m.response.status_code,
                        "headers": m.response.headers,
                        "body_preview": (m.response.body or "")[:2000],
                        "redirect_url": m.response.redirect_url,
                        "cookies": m.response.cookies,
                        "timestamp": m.response.timestamp,
                    },
                    "metadata": m.metadata,
                }
                for m in self.measurements
            ],
        }

        local_path = f"/tmp/{filename}"
        with open(local_path, "w") as f:
            json.dump(payload, f, indent=2)

        remote_path = f"{self.DEBUG_DIR}/{filename}"
        subprocess.run(
            ["adb", "-s", self.device_serial, "push", local_path, remote_path],
            capture_output=True, text=True, timeout=10,
        )
        self._adb(f"chmod 644 {remote_path}")
        return remote_path

    def get_summary(self) -> Dict[str, Any]:
        """Get measurement summary."""
        if not self.measurements:
            return {"measurement_count": 0}
        latest = self.measurements[-1]
        return {
            "measurement_count": len(self.measurements),
            "latest_success": latest.success,
            "latest_status": latest.response.status_code,
            "latest_redirect": latest.response.redirect_url,
            "latest_duration_ms": latest.request.duration_ms,
            "latest_error": latest.error,
            "latest_notes": latest.notes,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex Portal Debug Measure")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--measure", action="store_true", help="Measure portal request")
    parser.add_argument("--save", default="portal_measurements.json", help="Save measurements to JSON")
    parser.add_argument("--summary", action="store_true", help="Show measurement summary")
    parser.add_argument("--method", default="POST", help="HTTP method")
    parser.add_argument("--body", default="msisdn=8094298821&cedula=00112345678", help="Request body")
    args = parser.parse_args()

    measure = PortalDebugMeasure(device_serial=args.serial)

    if args.measure:
        result = measure.measure_request(
            method=args.method,
            body=args.body if args.method == "POST" else None,
        )
        print(json.dumps({
            "measurement_id": result.measurement_id,
            "success": result.success,
            "request": {
                "url": result.request.url,
                "method": result.request.method,
                "interface": result.request.interface,
                "duration_ms": result.request.duration_ms,
            },
            "response": {
                "status_code": result.response.status_code,
                "redirect_url": result.response.redirect_url,
                "cookies": result.response.cookies,
                "body_preview": result.response.body[:500] if result.response.body else "",
            },
            "notes": result.notes,
        }, indent=2, default=str))
    elif args.summary:
        print(json.dumps(measure.get_summary(), indent=2))
    else:
        result = measure.save_measurements(args.save)
        print(json.dumps({"saved_to": result, "count": len(measure.measurements)}, indent=2))


if __name__ == "__main__":
    main()
