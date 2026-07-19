"""Bluetooth.guard_stub

Guard + stub only. No real Bluetooth I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectionSpec:
    mac: str | None = None
    port: int | None = None
    established: bool = False


class BluetoothClientStub:
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
        if not connection_spec.mac:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "missing_mac",
            }

        self.history.append({
            "snapshotId": snapshot_id,
            "payloadKeys": sorted(list(payload.keys())),
            "mac": connection_spec.mac,
        })

        return {
            "snapshotId": snapshot_id,
            "routed": True,
            "transport": "bluetooth-stub",
            "mac": connection_spec.mac,
        }
