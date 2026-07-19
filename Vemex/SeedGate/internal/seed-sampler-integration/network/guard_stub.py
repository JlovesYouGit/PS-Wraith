"""network.guard_stub

Guard + stub only. No real network I/O.

Design intent:
- Provide a single entrypoint for pipeline routing.
- Refuse to do anything unless `connection_spec` indicates an established
  connection (simulated/placeholder).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectionSpec:
    # Placeholder fields; keep aligned with routing expectations.
    mac: str | None = None
    port: int | None = None
    established: bool = False


class NetworkClientStub:
    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    async def send_payload(self, snapshot_id: str, payload: dict[str, Any],
                             connection_spec: ConnectionSpec) -> dict[str, Any]:
        """Pretend-send payload.

        Returns a structured result; never performs real I/O.
        """
        if not connection_spec.established:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "connection_not_established",
            }
        if not connection_spec.mac or connection_spec.port is None:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "missing_mac_or_port",
            }

        self.history.append({
            "snapshotId": snapshot_id,
            "payloadKeys": sorted(list(payload.keys())),
            "mac": connection_spec.mac,
            "port": connection_spec.port,
        })

        return {
            "snapshotId": snapshot_id,
            "routed": True,
            "transport": "network-stub",
            "mac": connection_spec.mac,
            "port": connection_spec.port,
        }
