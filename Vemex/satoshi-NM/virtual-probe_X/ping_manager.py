import ipaddress
import json
import os
import platform
import re
import subprocess
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class PingResult:
    host: str
    ip: str
    is_active: bool
    latency_ms: float | None
    status: str
    checked_at: float = field(default_factory=time.time)


class PingManager:
    def __init__(self, node_graph: Any) -> None:
        self.node_graph = node_graph
        self.results: dict[str, PingResult] = {}
        self.active_list: list[PingResult] = []
        self.inactive_list: list[PingResult] = []
        self._lock = False

    def _acquire(self) -> bool:
        while self._lock:
            time.sleep(0.001)
        self._lock = True
        return True

    def _release(self) -> None:
        self._lock = False

    def check_host(self, host: str) -> PingResult:
        host = host.strip()
        if not host:
            return PingResult(host=host, ip="", is_active=False, latency_ms=None, status="invalid")

        ip = self._resolve(host)
        if not ip:
            return PingResult(host=host, ip="", is_active=False, latency_ms=None, status="unresolved")

        is_active, latency = self._ping(host)
        status = "active" if is_active else "inactive"
        result = PingResult(host=host, ip=ip, is_active=is_active, latency_ms=latency, status=status)
        return result

    def check_list(self, hosts: list[str]) -> dict[str, list[dict[str, Any]]]:
        with ThreadPoolExecutor(max_workers=min(32, len(hosts) if hosts else 1)) as executor:
            future_map = {executor.submit(self.check_host, h): h for h in hosts}
            for future in as_completed(future_map):
                result = future.result()
                self._acquire()
                try:
                    self.results[result.host] = result
                finally:
                    self._release()

        return self.get_lists()

    def get_lists(self) -> dict[str, list[dict[str, Any]]]:
        self._acquire()
        try:
            active = [asdict(r) for r in self.results.values() if r.is_active]
            inactive = [asdict(r) for r in self.results.values() if not r.is_active]
            self.active_list = [r for r in self.results.values() if r.is_active]
            self.inactive_list = [r for r in self.results.values() if not r.is_active]
            return {"active": active, "inactive": inactive}
        finally:
            self._release()

    def register_to_graph(self) -> None:
        self._acquire()
        try:
            for result in self.results.values():
                label = f"ping:{result.host}"
                existing = None
                for nid, node in self.node_graph.nodes.items():
                    if node.label == label:
                        existing = node
                        break
                if existing is None:
                    node = self.node_graph.add_node(
                        label=label,
                        metadata={
                            "host": result.host,
                            "ip": result.ip,
                            "status": result.status,
                            "latency_ms": result.latency_ms,
                            "checked_at": result.checked_at,
                            "type": "ping_unit",
                        },
                    )
                else:
                    existing.metadata.update({
                        "status": result.status,
                        "latency_ms": result.latency_ms,
                        "checked_at": result.checked_at,
                    })
                    existing.updated_at = time.time()
        finally:
            self._release()

    @staticmethod
    def _resolve(host: str) -> str:
        try:
            if ipaddress.ip_address(host):
                return str(ipaddress.ip_address(host))
        except ValueError:
            pass
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            return ""

    def _ping(self, host: str) -> tuple[bool, float | None]:
        system = platform.system().lower()
        try:
            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", "1000", host]
            elif system == "darwin":
                cmd = ["ping", "-c", "1", "-W", "1000", host]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", host]

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            output = proc.stdout + proc.stderr
            if proc.returncode == 0:
                latency = self._parse_latency(output)
                return True, latency
            return False, None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False, None

    @staticmethod
    def _parse_latency(output: str) -> float | None:
        patterns = [
            r"time[=<]([0-9]+\.[0-9]+)\s*ms",
            r"time[=<]([0-9]+)\s*ms",
            r"Average\s*=\s*([0-9]+)ms",
            r"平均\s*=\s*([0-9]+)ms",
        ]
        for pat in patterns:
            m = re.search(pat, output, re.IGNORECASE)
            if m:
                return float(m.group(1))
        return None

    def to_json(self) -> str:
        data = {
            "active": [asdict(r) for r in self.active_list],
            "inactive": [asdict(r) for r in self.inactive_list],
        }
        return json.dumps(data, indent=2)
