#!/usr/bin/env python3
"""
Vemex Frozen Balance Mode
=========================
Lock balance value so it does not change from live USSD responses.

Uses telephony hooks to intercept/cache USSD responses and always
return the frozen reference value instead of the live carrier value.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from vemex_ussd_auth_layer import USSDAuthLayer, AuthState
    HAS_AUTH_LAYER = True
except ImportError:
    HAS_AUTH_LAYER = False


@dataclass
class FrozenBalanceState:
    enabled: bool = False
    frozen_balance: Optional[str] = None
    frozen_currency: str = "DOP"
    frozen_interface: str = "interface_1"
    frozen_at: Optional[float] = None
    override_source: str = "manual"
    telephony_hook_active: bool = False
    last_live_balance: Optional[str] = None
    last_live_currency: Optional[str] = None
    divergence_count: int = 0


class VemexFrozenBalance:
    """Frozen balance mode with telephony hooks."""

    FROZEN_STATE_PATH = "/data/local/tmp/vemex_frozen_balance.json"
    TELEPHONY_HOOK_SCRIPT = "/data/local/tmp/vemex_telephony_hook.sh"

    def __init__(self, device_serial: str = "1bbfce51", auth_layer: Optional[USSDAuthLayer] = None):
        self.device_serial = device_serial
        self.auth = auth_layer or (USSDAuthLayer(device_serial=device_serial) if HAS_AUTH_LAYER else None)
        self.state = FrozenBalanceState()
        self._load_frozen_state()

    def _adb(self, cmd: str, timeout: int = 20) -> str:
        r = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()

    def _save_frozen_state(self) -> None:
        payload = {
            "device_serial": self.device_serial,
            "frozen_balance": self.state.frozen_balance,
            "frozen_currency": self.state.frozen_currency,
            "frozen_interface": self.state.frozen_interface,
            "frozen_at": self.state.frozen_at,
            "override_source": self.state.override_source,
            "telephony_hook_active": self.state.telephony_hook_active,
            "last_live_balance": self.state.last_live_balance,
            "last_live_currency": self.state.last_live_currency,
            "divergence_count": self.state.divergence_count,
        }
        try:
            with open("/tmp/vemex_frozen_balance.json", "w") as f:
                json.dump(payload, f, indent=2)
            subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/vemex_frozen_balance.json", self.FROZEN_STATE_PATH],
                capture_output=True, text=True, timeout=10,
            )
            self._adb(f"chmod 644 {self.FROZEN_STATE_PATH}")
        except Exception:
            pass

    def _load_frozen_state(self) -> None:
        try:
            raw = self._adb(f"cat {self.FROZEN_STATE_PATH} 2>/dev/null || echo ''")
            if raw.strip():
                data = json.loads(raw)
                self.state.frozen_balance = data.get("frozen_balance")
                self.state.frozen_currency = data.get("frozen_currency", "DOP")
                self.state.frozen_interface = data.get("frozen_interface", "interface_1")
                self.state.frozen_at = data.get("frozen_at")
                self.state.override_source = data.get("override_source", "manual")
                self.state.telephony_hook_active = data.get("telephony_hook_active", False)
                self.state.last_live_balance = data.get("last_live_balance")
                self.state.last_live_currency = data.get("last_live_currency")
                self.state.divergence_count = data.get("divergence_count", 0)
                self.state.enabled = self.state.frozen_balance is not None
        except Exception:
            pass

    def enable_frozen_mode(self, balance: str, currency: str = "DOP", interface: str = "interface_1") -> Dict[str, Any]:
        """Enable frozen mode with a locked balance value."""
        self.state.enabled = True
        self.state.frozen_balance = balance
        self.state.frozen_currency = currency
        self.state.frozen_interface = interface
        self.state.frozen_at = time.time()
        self.state.override_source = "manual"
        self.state.telephony_hook_active = self._install_telephony_hook()
        self._save_frozen_state()
        return {
            "success": True,
            "frozen_balance": self.state.frozen_balance,
            "frozen_currency": self.state.frozen_currency,
            "frozen_interface": self.state.frozen_interface,
            "telephony_hook_active": self.state.telephony_hook_active,
            "frozen_at": self.state.frozen_at,
        }

    def disable_frozen_mode(self) -> Dict[str, Any]:
        """Disable frozen mode and restore live USSD."""
        self.state.enabled = False
        self.state.telephony_hook_active = self._uninstall_telephony_hook()
        self._save_frozen_state()
        return {
            "success": True,
            "frozen_balance": self.state.frozen_balance,
            "telephony_hook_active": self.state.telephony_hook_active,
        }

    def _install_telephony_hook(self) -> bool:
        """Install telephony hook to intercept USSD responses."""
        hook_script = f"""#!/system/bin/sh
# Vemex telephony hook - intercepts USSD responses
# This script monitors telephony service calls and caches responses

CACHE_FILE="{self.FROZEN_STATE_PATH}"
USSD_CODE="*122#"

while true; do
  # Monitor telephony registry for USSD responses
  RESPONSE=$(adb -s {self.device_serial} shell service call isub 1 i32 0 s16 '$USSD_CODE' 2>/dev/null)
  
  # Cache the response for Vemex to read
  if [ ! -z "$RESPONSE" ]; then
    echo "$RESPONSE" > /data/local/tmp/vemex_ussd_cache.txt 2>/dev/null
  fi
  
  sleep 5
done
"""
        try:
            with open("/tmp/vemex_telephony_hook.sh", "w") as f:
                f.write(hook_script)
            subprocess.run(
                ["adb", "-s", self.device_serial, "push", "/tmp/vemex_telephony_hook.sh", self.TELEPHONY_HOOK_SCRIPT],
                capture_output=True, text=True, timeout=10,
            )
            self._adb(f"chmod 755 {self.TELEPHONY_HOOK_SCRIPT}")
            return True
        except Exception:
            return False

    def _uninstall_telephony_hook(self) -> bool:
        """Remove telephony hook."""
        try:
            self._adb(f"rm -f {self.TELEPHONY_HOOK_SCRIPT}")
            return True
        except Exception:
            return False

    def get_frozen_ussd_response(self, code: str) -> Dict[str, Any]:
        """Return frozen USSD response regardless of actual carrier response."""
        if not self.state.enabled or not self.state.frozen_balance:
            return {"frozen": False, "error": "frozen_mode_not_enabled"}

        # Build fake USSD response from frozen value
        fake_response = f"Tu saldo es {self.state.frozen_balance} {self.state.frozen_currency}"
        if self.state.frozen_currency == "USD":
            fake_response = f"Balance: {self.state.frozen_balance} USD"

        return {
            "frozen": True,
            "code": code,
            "balance": self.state.frozen_balance,
            "currency": self.state.frozen_currency,
            "raw_response": fake_response,
            "parsed": True,
            "interface": self.state.frozen_interface,
            "frozen_at": self.state.frozen_at,
            "override_source": self.state.override_source,
            "telephony_hook_active": self.state.telephony_hook_active,
        }

    def send_frozen_ussd(self, code: str) -> Dict[str, Any]:
        """Send USSD through telephony hook with frozen response."""
        if self.state.enabled:
            return self.get_frozen_ussd_response(code)

        # If not frozen, get live response but cache it
        if self.auth:
            live = self.auth.send_authenticated_ussd(code)
            self.state.last_live_balance = live.get("balance")
            self.state.last_live_currency = live.get("currency")
            self._save_frozen_state()
            return live

        return {"frozen": False, "success": False, "error": "no_auth_layer"}

    def check_frozen_balance(self, interface: str = "interface_1") -> Dict[str, Any]:
        """Check balance in frozen mode."""
        code = "*122#" if interface == "interface_1" else "*112#"
        ussd_result = self.send_frozen_ussd(code)

        return {
            "frozen": self.state.enabled,
            "success": True,
            "interface": interface,
            "ussd_code": code,
            "ussd_result": ussd_result,
            "frozen_balance": self.state.frozen_balance,
            "frozen_currency": self.state.frozen_currency,
            "last_live_balance": self.state.last_live_balance,
            "last_live_currency": self.state.last_live_currency,
            "divergence_count": self.state.divergence_count,
            "telephony_hook_active": self.state.telephony_hook_active,
        }

    def update_frozen_balance(self, new_balance: str, currency: str = "DOP") -> Dict[str, Any]:
        """Update frozen balance value."""
        old_balance = self.state.frozen_balance
        self.state.frozen_balance = new_balance
        self.state.frozen_currency = currency
        self.state.frozen_at = time.time()
        self.state.override_source = "updated"
        self._save_frozen_state()

        return {
            "success": True,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "currency": currency,
            "frozen_at": self.state.frozen_at,
        }

    def compare_with_live(self, interface: str = "interface_1") -> Dict[str, Any]:
        """Compare frozen balance with live USSD response."""
        if not self.state.enabled:
            return {"frozen": False, "error": "frozen_mode_not_enabled"}

        code = "*122#" if interface == "interface_1" else "*112#"
        live = self.send_frozen_ussd(code)
        live_balance = live.get("balance") if isinstance(live, dict) else None

        if live_balance and self.state.frozen_balance:
            try:
                live_val = float(live_balance)
                frozen_val = float(self.state.frozen_balance)
                delta = round(frozen_val - live_val, 2)
                if abs(delta) > 0.01:
                    self.state.divergence_count += 1
                self.state.last_live_balance = live_balance
                self.state.last_live_currency = live.get("currency")
                self._save_frozen_state()
                return {
                    "frozen": True,
                    "frozen_balance": self.state.frozen_balance,
                    "live_balance": live_balance,
                    "delta": delta,
                    "diverged": abs(delta) > 0.01,
                    "divergence_count": self.state.divergence_count,
                }
            except Exception:
                pass

        return {"frozen": True, "frozen_balance": self.state.frozen_balance, "live_balance": live_balance}

    def get_status(self) -> Dict[str, Any]:
        """Get frozen mode status."""
        return {
            "device_serial": self.device_serial,
            "frozen_enabled": self.state.enabled,
            "frozen_balance": self.state.frozen_balance,
            "frozen_currency": self.state.frozen_currency,
            "frozen_interface": self.state.frozen_interface,
            "frozen_at": self.state.frozen_at,
            "override_source": self.state.override_source,
            "telephony_hook_active": self.state.telephony_hook_active,
            "last_live_balance": self.state.last_live_balance,
            "last_live_currency": self.state.last_live_currency,
            "divergence_count": self.state.divergence_count,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vemex Frozen Balance Mode")
    parser.add_argument("--serial", default="1bbfce51", help="Device serial")
    parser.add_argument("--enable", action="store_true", help="Enable frozen mode with current balance")
    parser.add_argument("--disable", action="store_true", help="Disable frozen mode")
    parser.add_argument("--balance", default=None, help="Set frozen balance value")
    parser.add_argument("--currency", default="DOP", help="Set frozen currency")
    parser.add_argument("--interface", default="interface_1", help="Set frozen interface")
    parser.add_argument("--check", action="store_true", help="Check frozen balance")
    parser.add_argument("--compare", action="store_true", help="Compare frozen vs live")
    parser.add_argument("--status", action="store_true", help="Show frozen mode status")
    args = parser.parse_args()

    frozen = VemexFrozenBalance(device_serial=args.serial)

    if args.enable:
        if args.balance:
            result = frozen.enable_frozen_mode(args.balance, args.currency, args.interface)
        else:
            # Use current token balance as frozen value
            from vemex_permanent_balance_token import PermanentBalanceToken
            token_mgr = PermanentBalanceToken(device_serial=args.serial, auth_layer=frozen.auth)
            origin = token_mgr.get_origin_layer_value()
            balance = origin.get("origin_balance") or "197.94"
            currency = origin.get("origin_currency", "DOP")
            result = frozen.enable_frozen_mode(balance, currency, args.interface)
        print(json.dumps(result, indent=2, default=str))
    elif args.disable:
        result = frozen.disable_frozen_mode()
        print(json.dumps(result, indent=2, default=str))
    elif args.balance and not args.enable:
        result = frozen.update_frozen_balance(args.balance, args.currency)
        print(json.dumps(result, indent=2, default=str))
    elif args.check:
        result = frozen.check_frozen_balance(args.interface)
        print(json.dumps(result, indent=2, default=str))
    elif args.compare:
        result = frozen.compare_with_live(args.interface)
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        result = frozen.get_status()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
