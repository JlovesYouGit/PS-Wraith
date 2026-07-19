"""
repeater.py — Mana Ciel UTXO Repeater
Generates wallets deterministically and stacks them as separate JSON files
until collective UTXO reaches or exceeds 76 BTC (7_600_000_000 satoshis).
"""

import time
from pathlib import Path

from mana_ciel.wallet import ManaCielWallet

TARGET_BTC = 76.0
TARGET_SATS = int(TARGET_BTC * 100_000_000)


def utxo_sats(wallet: dict) -> int:
    return int(wallet.get("utxo_collective_value", 0) or 0)


def run(target_sats: int = TARGET_SATS) -> dict:
    wallet = ManaCielWallet()
    start_count = len(wallet.load_all())
    start_total = wallet.collective_utxo()

    count = 0
    while wallet.collective_utxo() < target_sats:
        wallet.generate()
        count += 1

    end_count = len(wallet.load_all())
    end_total = wallet.collective_utxo()

    return {
        "target_btc": target_sats / 100_000_000,
        "wallets_added": end_count - start_count,
        "total_wallets": end_count,
        "start_total_sats": start_total,
        "end_total_sats": end_total,
        "reached": end_total >= target_sats,
    }


if __name__ == "__main__":
    res = run()
    print(f"Target: {res['target_btc']} BTC")
    print(f"Wallets added: {res['wallets_added']}")
    print(f"Total wallets: {res['total_wallets']}")
    print(f"Final UTXO: {res['end_total_sats']} sats ({res['end_total_sats']/100_000_000} BTC)")
    print(f"Reached: {res['reached']}")
