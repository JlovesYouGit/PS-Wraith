"""xpub.guard_stub

xpub address routing transport. Derives sequential child addresses from
an extended public key (xpub loaded from .env ADR2) and routes kernel
payloads to each derived address.

Unlike other stubs, this performs REAL BIP32 derivation — the addresses
are cryptographically correct. The "routing" itself is still local
(no network broadcast), but the address mapping is genuine.

Flow:
  1. Sender = ADR from .env (P2PKH wallet address)
  2. Destination derivation source = ADR2 from .env (xpub)
  3. Each routed payload gets the next child address at m/0/<index>
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure seed_sampler package is importable for xpub_derivation
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_python_pkg = _project_root / "python"
if str(_python_pkg) not in sys.path:
    sys.path.insert(0, str(_python_pkg))

from seed_sampler.xpub_derivation import (
    parse_xpub,
    derive_single,
    validate_xpub,
)


@dataclass(frozen=True)
class XpubConnectionSpec:
    """Connection spec for xpub routing."""
    sender_address: str | None = None   # ADR from .env
    xpub: str | None = None             # ADR2 from .env
    established: bool = False


@dataclass
class XpubRoutingClient:
    """Routes payloads to sequentially derived xpub child addresses.

    Each call to send_payload increments the derivation index, producing
    the next address in the m/0/<index> path from the xpub.
    """
    current_index: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    derived_addresses: list[dict[str, Any]] = field(default_factory=list)

    async def send_payload(self, snapshot_id: str, payload: dict[str, Any],
                           connection_spec: XpubConnectionSpec) -> dict[str, Any]:
        """Route payload to the next derived child address."""
        if not connection_spec.established:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "connection_not_established",
            }

        if not connection_spec.xpub:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "missing_xpub (ADR2 not set in .env)",
            }

        if not connection_spec.sender_address:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": "missing_sender (ADR not set in .env)",
            }

        # Validate xpub
        xpub_info = validate_xpub(connection_spec.xpub)
        if not xpub_info["valid"]:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": f"invalid_xpub: {xpub_info['error']}",
            }

        # Derive the next child address
        try:
            derived = derive_single(connection_spec.xpub, index=self.current_index, chain=0)
        except Exception as e:
            return {
                "snapshotId": snapshot_id,
                "routed": False,
                "reason": f"derivation_error: {e}",
            }

        route_entry = {
            "snapshotId": snapshot_id,
            "routed": True,
            "transport": "xpub-derivation",
            "sender": connection_spec.sender_address,
            "destination": derived["address"],
            "derivation_path": derived["path"],
            "derivation_index": self.current_index,
            "destination_pubkey": derived["pubkey_hex"],
            "payloadKeys": sorted(list(payload.keys())),
        }

        self.history.append(route_entry)
        self.derived_addresses.append(derived)
        self.current_index += 1

        return route_entry
