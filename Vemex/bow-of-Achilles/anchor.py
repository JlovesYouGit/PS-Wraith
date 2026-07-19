"""
anchor.py — Mana Ciel Public Chain Anchor
Fetches UTXOs by address via public APIs and builds an unsigned
BTC transaction with an OP_RETURN output containing the commitment.
Private keys never leave your machine.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.error

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.balance_view import publish_balance

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "public"
TEMPLATE_FILE = PUBLIC_DIR / "anchor_tx_template.json"

API_BASE = "https://blockstream.info/api"


def fetch_utxos(address: str) -> list[dict]:
    url = f"{API_BASE}/address/{address}/utxo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ManaCiel/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        raise RuntimeError(f"Failed to fetch UTXOs for {address}: {e}")


def build_op_return_script(data_hex: str) -> str:
    if len(data_hex) > 80:
        raise ValueError("OP_RETURN data too large (max 80 bytes)")
    return f"6a{data_hex}"


def build_raw_tx(
    utxos: list[dict],
    destination_address: str,
    commitment_hex: str,
    fee_sats_per_byte: int = 10,
) -> dict:
    if not utxos:
        raise ValueError("No UTXOs available")

    script_pubkey = build_op_return_script(commitment_hex)
    input_value = sum(u.get("value", 0) for u in utxos)

    tx = {
        "version": 2,
        "locktime": 0,
        "inputs": [
            {
                "txid": u["txid"],
                "vout": u["vout"],
                "sequence": 0xffffff,
            }
            for u in utxos
        ],
        "outputs": [
            {
                "script_pubkey": script_pubkey,
                "value": 0,
                "type": "op_return",
            },
            {
                "address": destination_address,
                "value": input_value,
                "type": "p2pkh",
            },
        ],
        "metadata": {
            "input_value_sats": input_value,
            "fee_estimate_sats": max(546, len(utxos) * 150 + 2 * 34 + 10 + 100),
            "fee_rate_used": fee_sats_per_byte,
        },
    }
    return tx


def prepare_anchor(address: str, change_address: Optional[str] = None) -> dict:
    balance = publish_balance()
    commitment_hex = balance["commitment"]

    utxos = fetch_utxos(address)
    if not utxos:
        raise RuntimeError(f"No UTXOs found for {address}")

    change_address = change_address or address
    tx = build_raw_tx(utxos, change_address, commitment_hex)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    out = {
        "commitment_hex": commitment_hex,
        "source_address": address,
        "change_address": change_address,
        "utxo_count": len(utxos),
        "total_input_sats": sum(u["value"] for u in utxos),
        "raw_tx_template": tx,
        "utxos": utxos,
        "prepared_at_iso": datetime.now(timezone.utc).isoformat(),
        "note": "Sign this template with your private key/wallet and broadcast. Do not expose private keys.",
    }

    with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m mana_ciel.anchor <your_btc_address> [change_address]")
        sys.exit(1)
    addr = sys.argv[1]
    change = sys.argv[2] if len(sys.argv) > 2 else addr
    out = prepare_anchor(addr, change)
    print(f"Prepared anchor template for {addr}")
    print(f"Commitment: {out['commitment_hex']}")
    print(f"UTXOs: {out['utxo_count']}")
    print(f"Template: {TEMPLATE_FILE}")
