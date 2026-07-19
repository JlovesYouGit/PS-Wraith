"""
mana_ciel/validate_mainnet.py — Mainnet UTXO Validation
Samples addresses and checks actual Bitcoin mainnet UTXO against
the internal deterministic tally via Blockstream API.

Usage:
    python mana_ciel/validate_mainnet.py --sample 50 --delay 0.2
    python mana_ciel/validate_mainnet.py --address 1abc...  (validate single address)
"""

import hashlib
import json
import random
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mana_ciel.wallet import ManaCielWallet

API_BASE = "https://blockstream.info/api"
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "public"


def fetch_utxos(address: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/address/{address}/utxo"
    req = urllib.request.Request(url, headers={"User-Agent": "ManaCiel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for {address}") from e
    except Exception as e:
        raise RuntimeError(f"Fetch failed for {address}: {e}") from e


def real_utxo_total(address: str) -> int:
    utxos = fetch_utxos(address)
    return sum(int(u.get("value", 0)) for u in utxos)


def validate_address(address: str, expected_sats: int) -> dict[str, Any]:
    actual = 0
    utxo_count = 0
    error = None
    try:
        utxos = fetch_utxos(address)
        actual = sum(int(u.get("value", 0)) for u in utxos)
        utxo_count = len(utxos)
    except Exception as e:
        error = str(e)

    return {
        "address": address,
        "expected_sats": expected_sats,
        "actual_sats": actual,
        "utxo_count": utxo_count,
        "match": actual == expected_sats,
        "error": error,
    }


def validate_sample(
    sample_size: int = 100,
    delay_seconds: float = 0.1,
    seed: int | None = None,
) -> dict[str, Any]:
    if seed is not None:
        random.seed(seed)

    wallet_mgr = ManaCielWallet()
    all_wallets = wallet_mgr.load_all()

    if not all_wallets:
        return {"status": "empty", "message": "No wallets loaded"}

    sample = random.sample(all_wallets, min(sample_size, len(all_wallets)))

    results: list[dict[str, Any]] = []
    matched = 0
    total_expected = 0
    total_actual = 0
    errors = 0
    matched_addresses: list[str] = []
    mismatched_addresses: list[dict[str, Any]] = []
    error_addresses: list[dict[str, Any]] = []

    for i, w in enumerate(sample):
        addr = w.get("address", "")
        expected = int(w.get("utxo_collective_value", 0))

        record = validate_address(addr, expected)
        record["index"] = i
        results.append(record)

        total_expected += expected
        total_actual += record["actual_sats"]

        if record["match"]:
            matched += 1
            matched_addresses.append(addr)
        elif record["error"]:
            errors += 1
            error_addresses.append(record)
        else:
            mismatched_addresses.append(record)

        if i < len(sample) - 1:
            time.sleep(delay_seconds)

    status = (
        "valid_mainnet_match"
        if matched == len(sample) and not errors
        else "partial_match"
        if matched > 0 or not errors
        else "fetch_errors"
    )

    return {
        "status": status,
        "validated_at_iso": datetime.now(timezone.utc).isoformat(),
        "sample_size": len(sample),
        "matched": matched,
        "mismatched": len(mismatched_addresses),
        "errors": errors,
        "total_expected_sats": total_expected,
        "total_actual_sats": total_actual,
        "difference_sats": total_actual - total_expected,
        "matched_addresses": matched_addresses,
        "mismatched_addresses": mismatched_addresses,
        "error_addresses": error_addresses,
        "results": results,
    }


def validate_single(address: str) -> dict[str, Any]:
    wallet_mgr = ManaCielWallet()
    candidates = [w for w in wallet_mgr.load_all() if w.get("address") == address]
    expected = int(candidates[0].get("utxo_collective_value", 0)) if candidates else 0

    result = validate_address(address, expected)
    result["validated_at_iso"] = datetime.now(timezone.utc).isoformat()
    result["expected_source"] = "wallet_store" if candidates else "deterministic"

    if not candidates:
        actual_utxos = []
        actual_total = 0
        try:
            actual_utxos = fetch_utxos(address)
            actual_total = sum(int(u.get("value", 0)) for u in actual_utxos)
        except Exception as e:
            actual_utxos = []
            actual_total = 0
            result.setdefault("error", str(e))
        result["expected_sats"] = expected
        result["actual_sats"] = actual_total
        result["utxo_count"] = len(actual_utxos)
        result["match"] = actual_total == expected

    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate ManaCiel internal values against Bitcoin mainnet UTXO set"
    )
    parser.add_argument(
        "-n", "--sample", type=int, default=100, help="Number of wallets to sample (default: 100)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.1, help="Delay between API requests in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducible sampling"
    )
    parser.add_argument(
        "--address", type=str, default=None, help="Validate a single address only"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output JSON path (default: data/mana_ciel/public/mainnet_validation.json)"
    )
    args = parser.parse_args()

    if args.address:
        report = validate_single(args.address)
        print(f"Address: {args.address}")
    else:
        print(f"Validating {args.sample} wallets against mainnet...")
        report = validate_sample(args.sample, args.delay, args.seed)
        matched = report["matched"]
        total = report["sample_size"]
        pct = (matched / total * 100) if total else 0
        print(f"\nValidation complete: {report['status']}")
        print(f"  Sample:   {total}")
        print(f"  Matched:  {matched} ({pct:.1f}%)")
        print(f"  Mismatch: {report['mismatched']}")
        print(f"  Errors:   {report['errors']}")
        print(f"  Expected: {report['total_expected_sats']} sats")
        print(f"  Actual:   {report['total_actual_sats']} sats")
        print(f"  Delta:    {report['difference_sats']} sats")

    out_path = Path(args.output) if args.output else PUBLIC_DIR / "mainnet_validation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"Report saved: {out_path}")


if __name__ == "__main__":
    main()
