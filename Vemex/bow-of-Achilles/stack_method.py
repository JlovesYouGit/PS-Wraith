"""
stack_method.py — Stack Method for AI Velocity Increase
Stops node momentum by ID, logs imprint as JSON, recalls with higher density.
Stacks matches on existing containers instead of replicating.
Compresses high density into low density state via Ultimate Pi formula (5^q).
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.narrative_timing import narrative_tick, get_narrative_state

STACK_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "stack"
STACK_INDEX = STACK_DIR / "stack_index.json"
STOP_LOG = STACK_DIR / "stopper_log.json"
RECALL_LOG = STACK_DIR / "recall_log.json"


def _ensure_dirs() -> None:
    STACK_DIR.mkdir(parents=True, exist_ok=True)


def _load_index() -> dict:
    if not STACK_INDEX.exists():
        return {"containers": {}, "next_id": 1}
    try:
        return json.load(open(STACK_INDEX, "r", encoding="utf-8"))
    except Exception:
        return {"containers": {}, "next_id": 1}


def _save_index(index: dict) -> None:
    _ensure_dirs()
    with open(STACK_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, default=str)


def _load_json(path: Path) -> Any:
    if not path.exists():
        return [] if path.name.endswith(".json") else {}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") else {}


def _save_json(path: Path, data: Any) -> None:
    _ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def ultimate_pi_compress(density: float, q: Optional[int] = None) -> dict:
    """
    Compress a density value using Ultimate Pi formula (5^q).
    Higher q = more compression, lower output density.
    Returns compressed signal + decompression key.
    """
    if q is None:
        state = get_narrative_state()
        q = state["q_factor"] if state["q_factor"] > 0 else 1
    q = max(0, min(q, 15))
    power = 5 ** q
    compressed_signal = {
        "q": q,
        "power": power,
        "input_density": density,
        "compressed_density": density / power if power > 0 else density,
        "compression_ratio": power,
        "signal_hash": hashlib.sha256(f"{density}:{q}:{power}".encode()).hexdigest()[:16],
    }
    return compressed_signal


def ultimate_pi_decompress(compressed: dict) -> float:
    """Restore full density from compressed signal."""
    return compressed.get("compressed_density", 0.0) * compressed.get("compression_ratio", 1)


def stopper(node_id: str, momentum: float = 0.0, metadata: Optional[dict] = None) -> dict:
    _ensure_dirs()
    nodes_refresh_path = STACK_DIR.parent / "nodes_refresh.json"
    target = None
    try:
        nr = json.load(open(nodes_refresh_path, "r", encoding="utf-8")) if nodes_refresh_path.exists() else {}
        nodes = nr.get("nodes", []) if isinstance(nr, dict) else []
        for n in nodes:
            if n.get("address") == node_id or n.get("address_hash160") == node_id:
                target = n
                break
    except Exception:
        target = None

    narrative = get_narrative_state()
    ts = time.time()
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)) + f".{int((ts % 1) * 1e6):06d}Z"
    imprint = {
        "node_id": node_id,
        "stopped_at_iso": iso,
        "narrative_tick": narrative_tick(),
        "pulse": narrative["pulse"],
        "q_factor": narrative["q_factor"],
        "momentum": momentum,
        "original_density": target.get("utxo", target.get("utxo_collective_value", 0)) if target else 0,
        "compressed": ultimate_pi_compress(target.get("utxo", target.get("utxo_collective_value", 0)) if target else 0),
        "wallet_found": target is not None,
        "metadata": metadata or {},
    }

    log = _load_json(STOP_LOG)
    if isinstance(log, dict):
        log.setdefault("stops", []).append(imprint)
        _save_json(STOP_LOG, log)
    else:
        _save_json(STOP_LOG, {"stops": [imprint]})

    return imprint


def log_imprint(node_id: str, data: dict) -> dict:
    """Alias for stopper — save imprint explicitly."""
    return stopper(node_id, metadata=data)


def recall(node_id: str, expected_density_boost: float = 1.0) -> dict:
    """
    RECALL a stopped node. Load imprint, restore with higher density.
    Routes across multiple points for speed.
    Returns recalled state.
    """
    _ensure_dirs()
    log = _load_json(STOP_LOG)
    stops = log.get("stops", []) if isinstance(log, dict) else []
    target_imprint = None
    for s in stops:
        if s.get("node_id") == node_id:
            target_imprint = s
            break

    if not target_imprint:
        return {"status": "not_found", "node_id": node_id}

    base_density = ultimate_pi_decompress(target_imprint.get("compressed", {}))
    recalled_density = base_density * expected_density_boost

    narrative = get_narrative_state()
    ts = time.time()
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)) + f".{int((ts % 1) * 1e6):06d}Z"
    recall_entry = {
        "node_id": node_id,
        "recalled_at_iso": iso,
        "narrative_tick": narrative_tick(),
        "pulse": narrative["pulse"],
        "base_density": base_density,
        "density_boost": expected_density_boost,
        "recalled_density": recalled_density,
        "source_imprint": target_imprint,
        "route_points": _route_recall(node_id, target_imprint),
    }

    recall_log = _load_json(RECALL_LOG)
    if isinstance(recall_log, dict):
        recall_log.setdefault("recalls", []).append(recall_entry)
        _save_json(RECALL_LOG, recall_log)
    else:
        _save_json(RECALL_LOG, {"recalls": [recall_entry]})

    return recall_entry


def _route_recall(node_id: str, imprint: dict) -> list[dict]:
    """
    Route recall across multiple points (simulated destinations).
    Returns list of route points with timing.
    """
    routes = [
        {"point": "local_memory", "delay_ns": 0, "density_factor": 1.0},
        {"point": "narrative_tick", "delay_ns": narrative_tick() % 1000, "density_factor": 1.2},
        {"point": "wallet_store", "delay_ns": 400, "density_factor": 1.5},
        {"point": "stack_container", "delay_ns": 800, "density_factor": 2.0},
    ]
    for r in routes:
        r["arrival_density"] = imprint.get("original_density", 0) * r["density_factor"]
    return routes


def stack_on_match(container_id: str, new_density: float, match_key: str) -> dict:
    """
    STACK new density on top of existing container instead of replicating.
    If container doesn't exist, create it.
    Returns updated container.
    """
    _ensure_dirs()
    index = _load_index()
    containers = index.get("containers", {})

    ts = time.time()
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)) + f".{int((ts % 1) * 1e6):06d}Z"
    if container_id in containers:
        existing = containers[container_id]
        existing_density = existing.get("stacked_density", 0.0)
        existing["stacked_density"] = existing_density + new_density
        existing["match_count"] = existing.get("match_count", 0) + 1
        existing["last_match_key"] = match_key
        existing["last_updated"] = iso
        existing["compressed"] = ultimate_pi_compress(existing["stacked_density"])
        containers[container_id] = existing
    else:
        created_iso = iso
        containers[container_id] = {
            "container_id": container_id,
            "stacked_density": new_density,
            "match_count": 1,
            "first_match_key": match_key,
            "last_match_key": match_key,
            "created_at": created_iso,
            "last_updated": iso,
            "compressed": ultimate_pi_compress(new_density),
        }

    index["containers"] = containers
    _save_index(index)
    return containers[container_id]


def get_stack_density(container_id: str) -> float:
    """Get current stacked density for a container."""
    index = _load_index()
    container = index.get("containers", {}).get(container_id)
    if not container:
        return 0.0
    return ultimate_pi_decompress(container.get("compressed", {}))


def get_all_containers() -> list[dict]:
    """Return all stack containers with decompressed density."""
    index = _load_index()
    containers = []
    for cid, data in index.get("containers", {}).items():
        data["decompressed_density"] = ultimate_pi_decompress(data.get("compressed", {}))
        containers.append(data)
    return containers


def stop_recall_stack(node_id: str, density_boost: float = 1.5, match_key: Optional[str] = None) -> dict:
    """
    Full cycle: STOP → LOG → RECALL → STACK.
    1. Stop node momentum
    2. Recall with density boost
    3. Stack result on container
    Returns final stacked state.
    """
    match_key = match_key or hashlib.sha256(node_id.encode()).hexdigest()[:12]

    stop_record = stopper(node_id)
    recall_entry = recall(node_id, expected_density_boost=density_boost)
    container = stack_on_match(
        container_id=recall_entry.get("route_points", [{}])[-1].get("point", "default"),
        new_density=recall_entry.get("recalled_density", 0),
        match_key=match_key,
    )

    return {
        "status": "complete",
        "node_id": node_id,
        "stop": stop_record,
        "recall": recall_entry,
        "stack": container,
        "total_density": get_stack_density(container["container_id"]),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m mana_ciel.stack_method <node_id> [density_boost] [match_key]")
        sys.exit(1)
    node = sys.argv[1]
    boost = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    key = sys.argv[3] if len(sys.argv) > 3 else None
    result = stop_recall_stack(node, density_boost=boost, match_key=key)
    print(json.dumps(result, indent=2, default=str))
