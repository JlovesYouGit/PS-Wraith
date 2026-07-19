#!/usr/bin/env python3
"""
Formula String Calibrator
Chains formulas through a network-like string to derive emergent meaning,
following the user's pattern of calibrating and re-adjusting word interpretations.

This script connects formulas that share variables, building a graph,
then generates derived word-strings that bridge across formulas.
"""

import json
import itertools
from pathlib import Path
from collections import defaultdict

TABLE_PATH = Path(__file__).parent / "formula_table.json"


def load_table(path: Path) -> list:
    with open(path, "r") as f:
        return json.load(f)


def tokenize(text: str) -> set:
    return {w.lower() for w in text.replace("/", " ").replace("-", " ").split()}


def extract_vars(formula: str) -> set:
    """Extract variable-like tokens from a formula string."""
    import re
    tokens = re.findall(r"[A-Za-zα-ωΑ-ΩΔΣ∫√π∞_]+", formula)
    return {t.lower() for t in tokens}


def build_graph(table: list) -> dict:
    """Build adjacency: formula_id -> list of (other_id, shared_vars)."""
    entries = {e["id"]: e for e in table}
    var_map = defaultdict(list)
    for eid, entry in entries.items():
        for v in extract_vars(entry["formula"]):
            var_map[v].append(eid)

    graph = {}
    for eid, entry in entries.items():
        neighbors = []
        entry_vars = extract_vars(entry["formula"])
        for v in entry_vars:
            for nid in var_map.get(v, []):
                if nid != eid:
                    neighbors.append((nid, v))
        graph[eid] = neighbors
    return graph


def chain_interpretations(entry_a: dict, entry_b: dict, shared_var: str) -> str:
    """Create a bridge word-string between two formulas via a shared variable."""
    interp_a = entry_a["word_interpretation"]
    interp_b = entry_b["word_interpretation"]
    bridge = f"via {shared_var}"
    return f"{interp_a} | {bridge} | {interp_b}"


def calibrate(table: list) -> dict:
    """Network calibration: find all shared-variable chains and derive meanings."""
    entries = {e["id"]: e for e in table}
    graph = build_graph(table)
    chains = []

    seen = set()
    for eid, neighbors in graph.items():
        for nid, var in neighbors:
            key = tuple(sorted([eid, nid]))
            if key not in seen:
                seen.add(key)
                chains.append({
                    "from_id": eid,
                    "from_formula": entries[eid]["formula"],
                    "to_id": nid,
                    "to_formula": entries[nid]["formula"],
                    "shared_var": var,
                    "derived_meaning": chain_interpretations(entries[eid], entries[nid], var),
                })

    return {
        "total_formulas": len(table),
        "total_chains": len(chains),
        "calibration_chains": chains,
    }


def generate_calibration_string(table: list) -> str:
    """Produce one long calibrated string across all linked formulas."""
    entries = {e["id"]: e for e in table}
    graph = build_graph(table)

    visited = set()
    parts = []

    # Traverse starting from formulas with most connections
    start_ids = sorted(graph.keys(), key=lambda x: len(graph[x]), reverse=True)
    for sid in start_ids:
        if sid in visited:
            continue
        chain = [sid]
        visited.add(sid)
        current = sid
        while graph[current]:
            next_id, var = graph[current][0]
            if next_id not in visited:
                chain.append(next_id)
                visited.add(next_id)
                current = next_id
            else:
                break
        parts.append(" => ".join(
            f"[{entries[i]['formula']}] = \"{entries[i]['word_interpretation']}\""
            for i in chain
        ))

    return "\n\n".join(parts)


def main():
    table = load_table(TABLE_PATH)

    print("=== Formula String Calibration ===\n")

    cal = calibrate(table)
    print(f"Total formulas       : {cal['total_formulas']}")
    print(f"Calibration chains   : {cal['total_chains']}")
    print()

    print("Sample calibration chains (first 10):")
    for ch in cal["calibration_chains"][:10]:
        print(f"  {ch['from_formula']}  <--{ch['shared_var']}-->  {ch['to_formula']}")
        print(f"    => {ch['derived_meaning']}")
    print()

    print("=== Full Calibrated String ===\n")
    full_string = generate_calibration_string(table)
    print(full_string)

    out_path = Path(__file__).parent / "calibrated_string.txt"
    out_path.write_text(full_string)
    print(f"\nSaved calibrated string to {out_path}")


if __name__ == "__main__":
    main()
