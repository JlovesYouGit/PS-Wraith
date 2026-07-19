import ipaddress
import json
import re
import socket
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from hashgate import XSpace
from seednet import _extract_from_text, derive_commitment


class XSpaceScanner:
    def __init__(self, xspace: XSpace) -> None:
        self.xspace = xspace

    def scan_host(self, host: str, ports: list[int] | None = None) -> list[dict[str, Any]]:
        if ports is None:
            ports = [22, 80, 443, 8080, 8443, 3000, 5000, 8000, 9000]

        resolved = self._resolve(host)
        if not resolved:
            return []

        discovered_gates: list[dict[str, Any]] = []
        discovered_mirrors: list[dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=min(len(ports), 20)) as executor:
            future_map = {executor.submit(self._probe_port, host, p): p for p in ports}
            for future in as_completed(future_map):
                result = future.result()
                if result:
                    discovered_gates.append(result)

        gate_map: dict[str, str] = {}
        for gate_info in discovered_gates:
            gate_hash = gate_info["gate_hash"]
            gate = self.xspace.add_gate(host, gate_info["port"], gate_info["protocol"], metadata=gate_info)
            gate_map[gate_hash] = gate.id
            if gate_info.get("is_open"):
                mirrors = self._probe_mirrors(host, gate_info)
                for mirror in mirrors:
                    mirror["source_gate_hash"] = gate_hash
                    discovered_mirrors.append(mirror)
                    self.xspace.add_mirror(
                        mirror["host"],
                        mirror["port"],
                        gate.id,
                        mirror.get("content_hash", ""),
                        metadata=mirror,
                    )

        return discovered_gates + discovered_mirrors

    def scan_network(self, cidr: str) -> dict[str, Any]:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            return {"error": f"Invalid CIDR: {cidr}"}

        hosts = [str(ip) for ip in network.hosts()]
        results: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=min(len(hosts), 50)) as executor:
            future_map = {executor.submit(self.scan_host, h): h for h in hosts}
            for future in as_completed(future_map):
                host_results = future.result()
                if host_results:
                    results.extend(host_results)

        return {
            "cidr": cidr,
            "scanned": len(hosts),
            "discovered": len(results),
            "items": results,
        }

    def _probe_port(self, host: str, port: int) -> dict[str, Any] | None:
        protocol = "tcp"
        try:
            with socket.create_connection((host, port), timeout=2):
                pass
            banner = self._grab_banner(host, port)
            return {
                "host": host,
                "port": port,
                "protocol": protocol,
                "is_open": True,
                "banner": banner,
                "gate_hash": XSpace._compute_hash(host, port, protocol),
                "discovered_at": time.time(),
            }
        except (socket.timeout, ConnectionRefusedError, OSError):
            return None

    def _probe_mirrors(self, host: str, gate_info: dict[str, Any]) -> list[dict[str, Any]]:
        mirrors: list[dict[str, Any]] = []
        port = gate_info["port"]
        paths = ["/", "/mirror", "/.well-known/mirror", "/status", "/health", "/api", "/graphql", "/swagger", "/openapi.json"]

        for path in paths:
            try:
                conn = socket.create_connection((host, port), timeout=2)
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                if port in (443, 8443):
                    sock = context.wrap_socket(conn, server_hostname=host)
                else:
                    sock = conn
                request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                sock.sendall(request.encode())
                response = sock.recv(4096).decode(errors="ignore")
                sock.close()

                if response.startswith("HTTP/1.") or response.startswith("HTTP/2"):
                    status_match = re.match(r"HTTP/\d\.\d\s+(\d{3})", response)
                    if status_match and int(status_match.group(1)) < 400:
                        content_hash = XSpace._compute_hash(response)
                        body = response.split("\r\n\r\n", 1)[-1] if "\r\n\r\n" in response else response
                        seed_gates = self._extract_seed_gates(host, port, body)
                        mirrors.append({
                            "host": host,
                            "port": port,
                            "path": path,
                            "status_code": int(status_match.group(1)),
                            "content_hash": content_hash,
                            "is_mirror_candidate": True,
                            "sample": response[:512],
                            "seed_gates": seed_gates,
                            "discovered_at": time.time(),
                        })
            except Exception:
                continue
        return mirrors

    def _extract_seed_gates(self, host: str, port: int, content: str) -> list[dict[str, Any]]:
        gates: list[dict[str, Any]] = []
        try:
            seeds = _extract_from_text(f"{host}:{port}", content)
            for seed in seeds:
                commitment = derive_commitment(seed.value)
                gate = self.xspace.add_gate(
                    host=f"commitment:{commitment['key']}",
                    port=0,
                    protocol="seednet",
                    metadata={
                        "source_host": host,
                        "source_port": port,
                        "kind": seed.kind,
                        "value_sha256": seed.value_sha256,
                        "file_sha256": seed.file_sha256,
                        "line": seed.line,
                        "commitment": commitment,
                    },
                )
                gates.append({
                    "gate_id": gate.id,
                    "kind": seed.kind,
                    "value_sha256": seed.value_sha256,
                    "commitment": commitment,
                })
        except Exception:
            pass
        return gates

    def _grab_banner(self, host: str, port: int) -> str:
        try:
            with socket.create_connection((host, port), timeout=2) as sock:
                sock.sendall(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                return sock.recv(256).decode(errors="ignore")[:256]
        except Exception:
            return ""

    @staticmethod
    def _resolve(host: str) -> str:
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            return ""
