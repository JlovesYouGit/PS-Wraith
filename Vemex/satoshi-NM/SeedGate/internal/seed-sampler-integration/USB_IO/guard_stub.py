"""USB_IO.guard_stub

Guard + stub only. No real USB I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectionSpec:
    mac: str | None = None
    port: int | None = None
    established: bool = False


class UsbClientStub:
    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    async def send_payload(self, snapshot_id: str, payload: dict[str, Any],
                             connection_spec: ConnectionSpec) -> dict[str, Any]:
        if not connection_spec.established:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "connection_not_established",
            }
        # For USB, treat port as an abstract identifier.
        if connection_spec.port is None:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "missing_port",
            }

        self.history.append({
            "snapshotId": snapshot_id,
            "payloadKeys": sorted(list(payload.keys())),
            "port": connection_spec.port,
        })

        return {
            "snapshotId": snapshot_id,
            "routed": True,
            "transport": "usb-stub",
            "port": connection_spec.port,
        }
