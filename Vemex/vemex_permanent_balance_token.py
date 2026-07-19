#!/usr/bin/env python3
"""
Vemex Permanent Balance Token
==============================
Non-expendable token storage for observed balance values.

Persists balance tokens to device storage so they survive across
sessions and can be used as stable reference values in the auth layer.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_ussd_auth_layer import USSDAuthLayer
    HAS_AUTH_LAYER = True
except ImportError:
    HAS_AUTH_LAYER = False


@dataclass
class BalanceToken:
    token_id: str
    balance: str
    currency: str
    interface: str
    source: str = "ussd"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "balance": self.balance,
            "currency": self.currency,
            "interface": self.interface,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceToken":
        return cls(
            token_id=data["token_id"],
            balance=data["balance"],
            currency=data["currency"],
            interface=data["interface"],
            source=data.get("source", "ussd"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {}),
        )


class PermanentBalanceToken:
    """Manage permanent non-expendable balance tokens."""

    TOKEN_STORE_PATH = "/data/local/tmp/vemex_balance_tokens.json"

    def __init__(self, device_serial: str = "1bbfce51", auth_layer: Optional[USSDAuthLayer] = None):
        self.device_serial = device_serial
        self.auth = auth_layer or (USSDAuthLayer(device_serial=device_serial) if HAS_AUTH_LAYER else None)
        self.tokens: List[BalanceToken] = []
        self._load_tokens()

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def _load_tokens(self) -> None:
        try:
            raw = self._adb(f"cat {self.TOKEN_STORE_PATH} 2>/dev/null || echo ''")
            if raw.strip():
                data = json.loads(raw)
                self.tokens = [BalanceToken.from_dict(t) for t in data.get("tokens", [])]
        except Exception:
            self.tokens = []

    def _save_tokens(self) -> None:
        payload = {
            "device_serial": self.device_serial,
            "tokens": [t.to_dict() for t in self.tokens],
            "updated_at": time.time(),
        }
        try:
            with open("/tmp/vemex_balance_tokens.json", "w") as f:
                json.dump(payload, f, indent=2)
            subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/vemex_balance_tokens.json", self.TOKEN_STORE_PATH],
                capture_output=True, text=True, timeout=10,
            )
            self._adb(f"chmod 644 {self.TOKEN_STORE_PATH}")
        except Exception:
            pass

    def create_token(self, balance: str, currency: str, interface: str, ttl_seconds: Optional[float] = None) -> BalanceToken:
        """Create a new permanent balance token."""
        token_id = f"bal_{int(time.time())}_{hash(balance + currency + interface) % 10000:04d}"
        expires_at = None
        if ttl_seconds is not None:
            expires_at = time.time() + ttl_seconds

        token = BalanceToken(
            token_id=token_id,
            balance=balance,
            currency=currency,
            interface=interface,
            expires_at=expires_at,
        )
        self.tokens.append(token)
        self._save_tokens()
        return token

    def get_token(self, token_id: str) -> Optional[BalanceToken]:
        for t in self.tokens:
            if t.token_id == token_id:
                return t
        return None

    def get_latest_token(self, interface: Optional[str] = None) -> Optional[BalanceToken]:
        valid = [t for t in self.tokens if not t.is_expired() and (interface is None or t.interface == interface)]
        if not valid:
            return None
        return max(valid, key=lambda t: t.updated_at)

    def update_token_balance(self, token_id: str, new_balance: str) -> Optional[BalanceToken]:
        token = self.get_token(token_id)
        if token is None:
            return None
        token.balance = new_balance
        token.updated_at = time.time()
        self._save_tokens()
        return token

    def refresh_from_ussd(self, interface: str = "interface_1") -> Dict[str, Any]:
        """Refresh balance from USSD and update/create token."""
        if self.auth is None:
            return {"success": False, "error": "no_auth_layer"}

        result = self.auth.run_authenticated_balance_check(interface)
        balance = result.get("ussd_result", {}).get("balance")
        currency = result.get("ussd_result", {}).get("currency", "DOP")

        if not balance:
            return {"success": False, "error": "no_balance_in_ussd", "ussd_result": result}

        latest = self.get_latest_token(interface)
        if latest:
            updated = self.update_token_balance(latest.token_id, balance)
            action = "updated"
            token_id = latest.token_id
        else:
            token = self.create_token(balance, currency, interface)
            action = "created"
            token_id = token.token_id

        # Cross-interface synchronization check
        other_interface = "interface_2" if interface == "interface_1" else "interface_1"
        other_token = self.get_latest_token(other_interface)
        cross_sync = None
        if other_token:
            try:
                this_val = float(balance)
                other_val = float(other_token.balance)
                if abs(this_val - other_val) > 0.01:
                    cross_sync = {
                        "synchronized": False,
                        "this_interface": interface,
                        "this_balance": balance,
                        "other_interface": other_interface,
                        "other_balance": other_token.balance,
                        "delta": round(this_val - other_val, 2),
                        "note": "Balances diverge; interface tokens may reflect different spend events or stale cache.",
                    }
                else:
                    cross_sync = {
                        "synchronized": True,
                        "this_interface": interface,
                        "this_balance": balance,
                        "other_interface": other_interface,
                        "other_balance": other_token.balance,
                    }
            except Exception:
                cross_sync = {"synchronized": None, "error": "parse_error"}

        return {
            "success": True,
            "action": action,
            "token_id": token_id,
            "balance": balance,
            "currency": currency,
            "interface": interface,
            "matched": result.get("match", {}).get("matched"),
            "cross_interface_sync": cross_sync,
        }

    def get_origin_layer_value(self) -> Dict[str, Any]:
        """Return the highest/current origin layer balance value."""
        latest = self.get_latest_token()
        if latest is None:
            return {"success": False, "error": "no_tokens", "tokens": len(self.tokens)}
        return {
            "success": True,
            "origin_token_id": latest.token_id,
            "origin_balance": latest.balance,
            "origin_currency": latest.currency,
            "origin_interface": latest.interface,
            "origin_updated_at": latest.updated_at,
            "token_count": len(self.tokens),
            "expired_tokens": sum(1 for t in self.tokens if t.is_expired()),
        }

    def list_tokens(self) -> Dict[str, Any]:
        """List all tokens."""
        return {
            "device_serial": self.device_serial,
            "token_count": len(self.tokens),
            "tokens": [t.to_dict() for t in sorted(self.tokens, key=lambda t: t.updated_at, reverse=True)],
        }

    def get_status(self) -> Dict[str, Any]:
        """Get permanent token status."""
        origin = self.get_origin_layer_value()
        return {
            "device_serial": self.device_serial,
            "token_store": self.TOKEN_STORE_PATH,
            "total_tokens": len(self.tokens),
            "valid_tokens": sum(1 for t in self.tokens if not t.is_expired()),
            "origin_layer": origin,
            "latest_balance": origin.get("origin_balance"),
            "latest_currency": origin.get("origin_currency"),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex Permanent Balance Token")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--refresh", action="store_true", help="Refresh balance from USSD and update token")
    parser.add_argument("--interface", default="interface_1", help="Balance interface")
    parser.add_argument("--origin", action="store_true", help="Show origin layer value")
    parser.add_argument("--list", action="store_true", help="List all tokens")
    parser.add_argument("--status", action="store_true", help="Show token status")
    args = parser.parse_args()

    token_mgr = PermanentBalanceToken(device_serial=args.serial)

    if args.refresh:
        result = token_mgr.refresh_from_ussd(args.interface)
        print(json.dumps(result, indent=2, default=str))
    elif args.origin:
        result = token_mgr.get_origin_layer_value()
        print(json.dumps(result, indent=2, default=str))
    elif args.list:
        result = token_mgr.list_tokens()
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        result = token_mgr.get_status()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
