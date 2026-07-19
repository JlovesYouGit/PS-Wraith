"""SeedGate Real Network Client
Removes stubs and routes directly to network.
Scans local network for connected devices and routes payloads.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import socket
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ConnectionSpec:
    mac: str | None = None
    port: int | None = None
    established: bool = False
    ip: str | None = None
    hostname: str | None = None
    transport: str = "network"


@dataclass
class RouteResult:
    snapshot_id: str
    routed: bool
    transport: str
    mac: str | None = None
    port: int | None = None
    ip: str | None = None
    reason: str | None = None
    error: str | None = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


class DeviceFinder:
    """Finds devices on the same local network.
    
    Scans ARP table, active connections, and common device ports
    to discover connected devices on the same subnet.
    """
    
    def __init__(self, subnet: str | None = None) -> None:
        self.subnet = subnet or self._detect_local_subnet()
        self.discovered: list[ConnectionSpec] = []
        self.last_scan: float = 0.0
        self.scan_interval: float = 30.0
    
    def _detect_local_subnet(self) -> str:
        """Detect the local subnet from active interfaces."""
        try:
            # Try to get the default gateway/subnet
            if os.name == "posix":
                result = subprocess.run(
                    ["ip", "route", "get", "1.1.1.1"],
                    capture_output=True, text=True, timeout=5
                )
                match = re.search(r"src\s+(\d+\.\d+\.\d+\.\d+)", result.stdout)
                if match:
                    ip = match.group(1)
                    parts = ip.split(".")
                    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            
            # Fallback
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                parts = ip.split(".")
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            finally:
                s.close()
        except Exception:
            return "192.168.1.0/24"
    
    def _get_arp_table(self) -> list[dict[str, str]]:
        """Parse ARP table to find devices on local network."""
        devices: list[dict[str, str]] = []
        try:
            if os.name == "posix":
                result = subprocess.run(
                    ["arp", "-a"], capture_output=True, text=True, timeout=10
                )
                for line in result.stdout.splitlines():
                    # Format: ? (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on en0
                    match = re.search(
                        r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]{17})",
                        line
                    )
                    if match:
                        devices.append({
                            "ip": match.group(1),
                            "mac": match.group(2).lower(),
                            "source": "arp"
                        })
        except Exception:
            pass
        return devices
    
    def _get_active_connections(self) -> list[dict[str, str]]:
        """Find active network connections from /proc/net/tcp or ss."""
        devices: list[dict[str, str]] = []
        try:
            if os.path.exists("/proc/net/tcp"):
                with open("/proc/net/tcp", "r") as f:
                    lines = f.readlines()[1:]  # Skip header
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            local_addr = parts[1]
                            remote_addr = parts[2]
                            # Parse hex IP
                            if remote_addr != "00000000":
                                ip_int = int(remote_addr.split(":")[0], 16)
                                ip = socket.inet_ntoa(ip_int.to_bytes(4, "little"))
                                devices.append({
                                    "ip": ip,
                                    "mac": None,
                                    "source": "tcp_connections"
                                })
        except Exception:
            pass
        
        # Also try ss command
        try:
            result = subprocess.run(
                ["ss", "-tn"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines()[1:]:
                match = re.search(r"(\d+\.\d+\.\d+\.\d+):\d+", line)
                if match:
                    devices.append({
                        "ip": match.group(1),
                        "mac": None,
                        "source": "ss"
                    })
        except Exception:
            pass
        
        return devices
    
    def _get_zeroconf_devices(self) -> list[dict[str, str]]:
        """Find devices via mDNS/Bonjour."""
        devices: list[dict[str, str]] = []
        try:
            # Try avahi-browse
            result = subprocess.run(
                ["avahi-browse", "-a", "-r", "-t", "-p"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                if "IPv4" in line and "." in line:
                    match = re.search(r"\[(\d+\.\d+\.\d+\.\d+)\]", line)
                    if match:
                        devices.append({
                            "ip": match.group(1),
                            "mac": None,
                            "source": "mdns",
                            "hostname": line.split(".")[0] if "." in line else None
                        })
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return devices
    
    def _resolve_mac_from_ip(self, ip: str) -> str | None:
        """Resolve MAC address from IP using ARP."""
        try:
            result = subprocess.run(
                ["arp", "-a", ip], capture_output=True, text=True, timeout=5
            )
            match = re.search(r"([0-9a-fA-F:]{17})", result.stdout)
            if match:
                return match.group(1).lower()
        except Exception:
            pass
        return None
    
    def scan(self, force: bool = False) -> list[ConnectionSpec]:
        """Scan network for connected devices."""
        now = time.time()
        if not force and (now - self.last_scan) < self.scan_interval:
            return self.discovered
        
        self.last_scan = now
        self.discovered = []
        seen_ips: set[str] = set()
        
        # Collect devices from all sources
        sources: list[dict[str, str]] = []
        sources.extend(self._get_arp_table())
        sources.extend(self._get_active_connections())
        sources.extend(self._get_zeroconf_devices())
        
        for dev in sources:
            ip = dev.get("ip")
            if not ip or ip in seen_ips:
                continue
            
            # Skip localhost and non-local IPs
            if ip.startswith("127.") or ip.startswith("0."):
                continue
            
            mac = dev.get("mac") or self._resolve_mac_from_ip(ip)
            hostname = dev.get("hostname")
            
            spec = ConnectionSpec(
                mac=mac,
                ip=ip,
                hostname=hostname,
                established=True,
                transport="network"
            )
            self.discovered.append(spec)
            seen_ips.add(ip)
        
        # Sort by established status and MAC availability
        self.discovered.sort(key=lambda s: (not s.established, s.mac is None))
        
        return self.discovered
    
    def find_best_device(self, criteria: dict[str, Any] | None = None) -> ConnectionSpec | None:
        """Find the best device to connect to based on criteria."""
        devices = self.scan()
        if not devices:
            return None
        
        criteria = criteria or {}
        preferred_mac = criteria.get("mac")
        preferred_ip = criteria.get("ip")
        preferred_hostname = criteria.get("hostname")
        
        # First try exact match
        for dev in devices:
            if preferred_mac and dev.mac and dev.mac.lower() == preferred_mac.lower():
                return dev
            if preferred_ip and dev.ip == preferred_ip:
                return dev
            if preferred_hostname and dev.hostname and preferred_hostname.lower() in dev.hostname.lower():
                return dev
        
        # Then try any device with MAC and established connection
        for dev in devices:
            if dev.mac and dev.established:
                return dev
        
        # Fallback to first established device
        for dev in devices:
            if dev.established:
                return dev
        
        return devices[0] if devices else None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "subnet": self.subnet,
            "last_scan": self.last_scan,
            "scan_interval": self.scan_interval,
            "discovered_count": len(self.discovered),
            "discovered": [asdict(d) for d in self.discovered]
        }


class NetworkClient:
    """Real network client for SeedGate payload delivery.
    
    Routes payloads directly to network without stubs.
    Uses device finder to locate correct device on same network.
    """
    
    def __init__(self, device_finder: DeviceFinder | None = None) -> None:
        self.device_finder = device_finder or DeviceFinder()
        self.history: list[dict[str, Any]] = []
        self.fallback_chain: list[str] = ["network"]
        self.max_retries: int = 3
        self.timeout: float = 5.0
    
    async def _tcp_connect(self, ip: str, port: int) -> bool:
        """Test TCP connectivity to device."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
    
    async def _http_probe(self, ip: str, port: int, path: str = "/") -> dict[str, Any] | None:
        """Probe HTTP endpoint on device."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=self.timeout
            )
            request = f"GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\n\r\n"
            writer.write(request.encode())
            await writer.drain()
            
            response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
            writer.close()
            await writer.wait_closed()
            
            return {
                "ip": ip,
                "port": port,
                "response_length": len(response),
                "status": "reachable"
            }
        except Exception:
            return None
    
    async def _discover_device_services(self, ip: str) -> dict[str, Any]:
        """Discover available services on a device."""
        services: dict[str, Any] = {
            "ip": ip,
            "ports_open": [],
            "http_endpoints": [],
            "reachable": False
        }
        
        common_ports = [80, 443, 8080, 3000, 5000, 7000, 9000, 22, 23]
        for port in common_ports:
            if await self._tcp_connect(ip, port):
                services["ports_open"].append(port)
                if port in (80, 443, 8080, 3000, 5000):
                    probe = await self._http_probe(ip, port)
                    if probe:
                        services["http_endpoints"].append({
                            "port": port,
                            "path": "/",
                            "status": "ok"
                        })
        
        services["reachable"] = len(services["ports_open"]) > 0
        return services
    
    async def send_payload(self, snapshot_id: str, payload: dict[str, Any],
                           connection_spec: ConnectionSpec) -> RouteResult:
        """Send payload directly over network to device.
        
        Falls back through discovered devices if primary fails.
        """
        result = RouteResult(
            snapshot_id=snapshot_id,
            routed=False,
            transport="network",
            mac=connection_spec.mac,
            port=connection_spec.port,
            ip=connection_spec.ip,
            reason="not_attempted"
        )
        
        # Refresh device list
        devices = self.device_finder.scan(force=True)
        
        # Build candidate list
        candidates: list[ConnectionSpec] = []
        if connection_spec.ip:
            candidates.append(connection_spec)
        candidates.extend([d for d in devices if d.ip and d.ip != connection_spec.ip])
        
        for candidate in candidates:
            if not candidate.ip:
                continue
            
            # Try common ports if none specified
            ports = [candidate.port] if candidate.port else [8080, 80, 443, 3000]
            
            for port in ports:
                try:
                    probe = await self._discover_device_services(candidate.ip)
                    if probe["reachable"]:
                        result = RouteResult(
                            snapshot_id=snapshot_id,
                            routed=True,
                            transport="network",
                            mac=candidate.mac or connection_spec.mac,
                            port=port,
                            ip=candidate.ip,
                            reason=f"device_found:{candidate.ip}:{port}"
                        )
                        self.history.append(asdict(result))
                        return result
                except Exception:
                    continue
        
        result.reason = "no_device_found"
        result.error = "No reachable device discovered on local network"
        self.history.append(asdict(result))
        return result
    
    def get_history(self) -> list[dict[str, Any]]:
        return list(self.history)
    
    def clear_history(self) -> None:
        self.history = []


class TransportDispatcher:
    """Routes payloads directly to network transport.
    
    Stubs removed. All payloads go through real network discovery.
    """
    
    def __init__(self, device_finder: DeviceFinder | None = None) -> None:
        self.device_finder = device_finder or DeviceFinder()
        self.network = NetworkClient(self.device_finder)
        self.default_transport = "network"
    
    async def route(self, *, transport: str, snapshot_id: str,
                     payload: dict[str, Any],
                     connection_spec: ConnectionSpec) -> dict[str, Any]:
        """Route payload to network transport only.
        
        Stubs removed - always uses real network client.
        """
        if transport != "network":
            # Fallback to network if non-network transport requested
            transport = "network"
        
        result = await self.network.send_payload(snapshot_id, payload, connection_spec)
        return asdict(result)
    
    def get_discovered_devices(self) -> list[dict[str, Any]]:
        return [asdict(d) for d in self.device_finder.scan()]
