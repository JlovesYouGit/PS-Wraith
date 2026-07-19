"""dispatcher

Central routing entrypoint for payload delivery to network transport.

Stubs removed. All payloads route through real network client with
device discovery on the local subnet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .network.client import DeviceFinder, NetworkClient, TransportDispatcher as NetworkDispatcher


Transport = Literal["network"]


@dataclass(frozen=True)
class ConnectionSpec:
    mac: str | None = None
    port: int | None = None
    established: bool = False
    ip: str | None = None
    hostname: str | None = None


class TransportDispatcher:
    def __init__(self) -> None:
        self.device_finder = DeviceFinder()
        self.network_dispatcher = NetworkDispatcher(self.device_finder)
        self.default_transport = "network"

    async def route(self, *, transport: str, snapshot_id: str,
                     payload: dict[str, Any],
                     connection_spec: ConnectionSpec) -> dict[str, Any]:
        """Route payload through network transport only.
        
        Stubs removed. Always uses real network discovery and delivery.
        """
        # Convert to network client ConnectionSpec
        network_spec = ConnectionSpec(
            mac=connection_spec.mac,
            port=connection_spec.port,
            established=True,
            ip=connection_spec.ip,
            hostname=connection_spec.hostname,
        )
        
        # Always route through network client
        result = await self.network_dispatcher.route(
            transport="network",
            snapshot_id=snapshot_id,
            payload=payload,
            connection_spec=network_spec
        )
        
        return result
    
    def get_discovered_devices(self) -> list[dict[str, Any]]:
        """Get all discovered devices on the local network."""
        return self.network_dispatcher.get_discovered_devices()
    
    def find_best_device(self, criteria: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Find the best device to connect to."""
        device = self.network_dispatcher.device_finder.find_best_device(criteria)
        if device:
            return {
                "mac": device.mac,
                "ip": device.ip,
                "port": device.port,
                "hostname": device.hostname,
                "established": device.established,
                "transport": device.transport
            }
        return None
