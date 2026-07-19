"""
balance_view.py — Mana Ciel Safe Balance Publisher
Publishes only the aggregate UTXO total with a commitment proof.
No private keys, addresses, or per-wallet data are exposed.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from mana_ciel.wallet import ManaCielWallet

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "public"
PUBLIC_FILE = PUBLIC_DIR / "balance_view.json"


def _commit(total_sats: int, salt: str, timestamp: float) -> str:
    return hashlib.sha256(f"{total_sats}:{salt}:{timestamp}".encode()).hexdigest()


def publish_balance() -> dict:
    wallet = ManaCielWallet()
    total = wallet.collective_utxo()
    salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    commitment = _commit(total, salt, time.time())

    entry = {
        "total_sats": total,
        "total_btc": total / 100_000_000,
        "commitment": commitment,
        "salt": salt,
        "timestamp_unix": time.time(),
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "wallet_count": len(wallet.load_all()),
    }

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    with open(PUBLIC_FILE, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)

    return entry


def verify_balance(expected_total_sats: int, salt: str, timestamp: float, commitment: str) -> bool:
    return _commit(expected_total_sats, salt, timestamp) == commitment


if __name__ == "__main__":
    entry = publish_balance()
    print(f"Published balance: {entry['total_btc']} BTC")
    print(f"Commitment: {entry['commitment']}")
    print(f"Wallets: {entry['wallet_count']}")
    print(f"File: {PUBLIC_FILE}")
