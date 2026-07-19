"""dispatcher

Central routing entrypoint for payload delivery to external transports.

Important:
- Stubs only. No real device/network/Bluetooth/USB/serial I/O.
- Routing is allowed only when `connection_spec.established` is True.

No attempt is made to “enforce” beyond existing zero-brain logic gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .network.guard_stub import NetworkClientStub, ConnectionSpec as NetworkSpec
from .Bluetooth.guard_stub import BluetoothClientStub, ConnectionSpec as BluetoothSpec
from .serial.guard_stub import SerialClientStub, ConnectionSpec as SerialSpec
from .USB_IO.guard_stub import UsbClientStub, ConnectionSpec as UsbSpec


Transport = Literal["network", "Bluetooth", "serial", "USB_IO"]


@dataclass(frozen=True)
class ConnectionSpec:
    mac: str | None = None
    port: int | None = None
    established: bool = False


class TransportDispatcher:
    def __init__(self) -> None:
        self.network = NetworkClientStub()
        self.bluetooth = BluetoothClientStub()
        self.serial = SerialClientStub()
        self.usb = UsbClientStub()

    async def route(self, *, transport: Transport, snapshot_id: str,
                     payload: dict[str, Any],
                     connection_spec: ConnectionSpec) -> dict[str, Any]:
        # Convert shared ConnectionSpec into each stub's ConnectionSpec.
        if transport == "network":
            spec = NetworkSpec(mac=connection_spec.mac, port=connection_spec.port,
                               established=connection_spec.established)
            return await self.network.send_payload(snapshot_id, payload, spec)
        if transport == "Bluetooth":
            spec = BluetoothSpec(mac=connection_spec.mac, port=connection_spec.port,
                                 established=connection_spec.established)
            return await self.bluetooth.send_payload(snapshot_id, payload, spec)
        if transport == "serial":
            spec = SerialSpec(mac=connection_spec.mac, port=connection_spec.port,
                               established=connection_spec.established)
            return await self.serial.send_payload(snapshot_id, payload, spec)
        if transport == "USB_IO":
            spec = UsbSpec(mac=connection_spec.mac, port=connection_spec.port,
                            established=connection_spec.established)
            return await self.usb.send_payload(snapshot_id, payload, spec)
        raise ValueError(f"unknown transport: {transport}")
