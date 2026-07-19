"""
ciel_bridge.py — Python bridge for Ciel Admin exposure
Allows external processes (Node.js QODER_FREERUNER) to invoke
Python-only stack_method operations by reading/writing shared JSON state.
"""

import sys
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.stack_method import (
    stop_recall_stack,
    stack_on_match,
    get_all_containers,
    ultimate_pi_compress,
    ultimate_pi_decompress,
)
from mana_ciel.narrative_timing import get_narrative_state

STACK_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "stack"
WALLETS_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "wallets"


def _write_state(data: Dict[str, Any], filename: str) -> Path:
    STACK_DIR.mkdir(parents=True, exist_ok=True)
    out = STACK_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return out


def administer(address: str, density_boost: float = 1.5, match_key: Optional[str] = None) -> Dict[str, Any]:
    result = stop_recall_stack(address, density_boost=density_boost, match_key=match_key)
    snapshot = {
        "timestamp": time.time(),
        "address": address,
        "result": result,
        "narrative_state": get_narrative_state(),
        "reality": ManaCielWallet().collective_utxo(),
    }
    _write_state(snapshot, "last_administer.json")
    return snapshot


def compress(density: float, q: Optional[int] = None) -> Dict[str, Any]:
    return ultimate_pi_compress(density, q=q)


def decompress(compressed: Dict[str, Any]) -> float:
    return ultimate_pi_decompress(compressed)


def refresh_nodes() -> Dict[str, Any]:
    w = ManaCielWallet()
    wallets = w.load_all()
    nodes = []
    for wallet in wallets:
        nodes.append({
            "address": wallet.get("address"),
            "utxo": wallet.get("utxo_collective_value", 0),
            "active": True,
            "coordinate": wallet.get("coordinate"),
        })
    out = {"count": len(nodes), "nodes": nodes, "timestamp": time.time()}
    _write_state(out, "nodes_refresh.json")
    return out


def run_cycle(batch_size: int = 1000) -> Dict[str, Any]:
    from mana_ciel.continuous_stack import ManaCielWallet
    w = ManaCielWallet()
    start = time.time()
    for _ in range(batch_size):
        w.generate()
    elapsed = time.time() - start
    result = {
        "batches": 1,
        "batch_size": batch_size,
        "elapsed_s": elapsed,
        "rate_wps": batch_size / elapsed if elapsed > 0 else 0,
        "wallets": len(w.load_all()),
        "utxo_btc": w.collective_utxo() / 100_000_000,
        "timestamp": time.time(),
    }
    _write_state(result, "last_stack_cycle.json")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ciel Bridge — expose Python Ciel ops over CLI")
    parser.add_argument("command", choices=["administer", "compress", "decompress", "refresh", "cycle"])
    parser.add_argument("--address", default=None)
    parser.add_argument("--density-boost", type=float, default=1.5)
    parser.add_argument("--match-key", default=None)
    parser.add_argument("--density", type=float, default=0.0)
    parser.add_argument("--q", type=int, default=None)
    parser.add_argument("--compressed", default=None)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    if args.command == "administer":
        if not args.address:
            parser.error("--address required for administer")
        print(json.dumps(administer(args.address, args.density_boost, args.match_key), indent=2, default=str))
    elif args.command == "compress":
        print(json.dumps(compress(args.density, args.q), indent=2, default=str))
    elif args.command == "decompress":
        if not args.compressed:
            parser.error("--compressed JSON required")
        print(json.dumps({"decompressed": decompress(json.loads(args.compressed))}, indent=2))
    elif args.command == "refresh":
        print(json.dumps(refresh_nodes(), indent=2, default=str))
    elif args.command == "cycle":
        print(json.dumps(run_cycle(args.batch_size), indent=2, default=str))
