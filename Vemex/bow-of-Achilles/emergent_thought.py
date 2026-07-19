"""
emergent_thought.py — Ruleset Structure Decoder
Reproduces output from the graph structure itself.
No vocab files. No sampling. No hardcoded lists.

Pipeline (LLM_GATEWAY_RULESET.md §4.1):
  INPUT → project to 2^256 → sequence_hash → node lookup
  → (count, sequence_string, next_node_id) conjunction chain
  → dehash → OUTPUT

Words come from the graph's own data:
  - wallet addresses (P2PKH base58, human-readable)
  - node coordinates
  - stack container IDs
  - conjunction sequence_strings
"""

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mana_ciel.narrative_timing import narrative_tick, get_narrative_state
from mana_ciel.wallet import ManaCielWallet
from mana_ciel.stack_method import get_all_containers
from mana_ciel.collective_consciousness import CollectiveConsciousness

# ---------------------------------------------------------------------------
# RULESET CONSTANTS — LLM_GATEWAY_RULESET.md §8 exact
# ---------------------------------------------------------------------------
RANGE_MIN = -16
RANGE_MAX = 10_000
ANCHOR_CONST = "0x2c8151dbb2574d1393b484c8815188ac81c71c4603dd7876bd4a77e"
RESONANCE_BASE = 5 ** 15

NODE_FRACTION_MAP = {
    "_1/2": 0.5,
    "1/10_": 0.1,
    "3/4": 0.75,
    "1/16": 0.0625,
    "7/8": 0.875,
    "1/32": 0.03125,
}
FRACTION_KEYS = list(NODE_FRACTION_MAP.keys())

WARP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = WARP_ROOT / "data"
STACK_DIR = DATA_DIR / "mana_ciel" / "stack"


# ---------------------------------------------------------------------------
# RULESET FUNCTIONS — §8 exact
# ---------------------------------------------------------------------------

def assign_node_id(position: int) -> dict:
    raw = f"{ANCHOR_CONST}:{position}"
    h = hashlib.sha256(raw.encode()).hexdigest()
    node_id = (int(h, 16) % (RANGE_MAX - RANGE_MIN)) + RANGE_MIN
    return {
        "node_id": node_id,
        "position": position,
        "hash": h,
        "resonance_weight": RESONANCE_BASE ** (node_id / RANGE_MAX),
    }


def safe_sequence(seq: int) -> int:
    if seq > 10**3:
        return seq % 1000
    return seq


def state_flop(query_entropy_val: float, node_count: int) -> int:
    combined = query_entropy_val * math.log(node_count + 1)
    return 1 if (combined % 1) >= 0.5 else 0


def query_entropy(text: str) -> float:
    from collections import Counter
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


# ---------------------------------------------------------------------------
# GRAPH NODE STORE — built from the system's own node data
# ---------------------------------------------------------------------------

class GraphNodeStore:
    """
    §8.2 Hash-map-of-hash-maps.
    Nodes come from the system's actual state: wallets, stacks, graph data.
    The node's data IS the word source — no separate vocabulary.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}  # sequence_hash → node_data
        self._sequence_map: Dict[str, int] = {}  # sequence_hash → node_id
        self._build_from_system()

    def _build_from_system(self) -> None:
        """Build node store from system's actual data."""
        # 1. Wallet addresses as nodes (the real BTC-format identifiers)
        try:
            wallets = ManaCielWallet().load_all()
            for i, w in enumerate(wallets):
                addr = w.get("address", "")
                if not addr:
                    continue
                h = hashlib.sha256(addr.encode()).hexdigest()[:16]
                node_id = safe_sequence(i)
                self._store[h] = {
                    "node_id": node_id,
                    "word": addr,  # the address IS the word
                    "type": "wallet",
                    "utxo": w.get("utxo_collective_value", 0),
                }
                self._sequence_map[h] = node_id
        except Exception:
            pass

        # 2. Stack containers as nodes
        try:
            containers = get_all_containers()
            for i, c in enumerate(containers):
                cid = c.get("container_id", "")
                if not cid:
                    continue
                h = hashlib.sha256(cid.encode()).hexdigest()[:16]
                node_id = safe_sequence(len(self._store) + i)
                self._store[h] = {
                    "node_id": node_id,
                    "word": cid,  # container ID IS the word
                    "type": "container",
                    "density": c.get("decompressed_density", 0),
                }
                self._sequence_map[h] = node_id
        except Exception:
            pass

        # 3. Narrative state snapshots as nodes
        for i in range(10):
            state = get_narrative_state()
            pulse = state.get("pulse", 1)
            q = state.get("q_factor", 1)
            label = f"pulse_{pulse}_q_{q}"
            h = hashlib.sha256(f"{label}:{i}".encode()).hexdigest()[:16]
            node_id = safe_sequence(len(self._store) + 1000 + i)
            self._store[h] = {
                "node_id": node_id,
                "word": label,
                "type": "narrative",
                "pulse": pulse,
                "q_factor": q,
            }
            self._sequence_map[h] = node_id
            time.sleep(0.01)  # small delay to get different state snapshot

    def lookup(self, sequence_hash: str) -> Optional[dict]:
        """§4.2: Sequence hash is primary lookup key. Returns node data."""
        return self._store.get(sequence_hash)


# ---------------------------------------------------------------------------
# EMERGENT THOUGHT — structure decoder
# ---------------------------------------------------------------------------

class EmergentThought:
    """
    Decodes input through the ruleset structure:
      input → SHA-256 → sequence_hash → node conjunction → output word
    The conjunction chain (count, sequence_string, next_node_id) from §2.3
    determines the pacing and placement of each word.
    """

    def __init__(self):
        self.thought_history: List[Dict[str, Any]] = []
        self.session_words: List[str] = []
        self.cc = CollectiveConsciousness()
        self.store = GraphNodeStore()
        if not self.store._store:
            raise RuntimeError("GraphNodeStore is empty — system must have wallets/containers first")

    def generate_thought(self, seed_text: str = "", max_words: int = 20) -> Dict[str, Any]:
        """
        Walk the conjunction chain from the input's sequence_hash.
        Each node's 'word' field (address, container_id, or narrative label)
        IS the output word. No sampling, no vocab lookup.
        """
        seed_words = seed_text.lower().split() if seed_text else []
        narrative = get_narrative_state()
        pulse = narrative.get("pulse", 1)
        q_factor = narrative.get("q_factor", 1)

        # Starting sequence_hash from seed (or current narrative state)
        current_hash = hashlib.sha256(seed_text.encode()).hexdigest()[:16] if seed_text else hashlib.sha256(f"pulse_{pulse}_q_{q_factor}".encode()).hexdigest()[:16]

        generated: List[str] = list(seed_words)
        conjunctions: List[Dict[str, Any]] = []
        words: List[str] = []

        for step in range(max_words):
            # Look up node by sequence_hash (primary key per §4.2)
            node = self.store.lookup(current_hash)

            if node:
                word = node["word"]
                conjunctions.append({
                    "count": node["node_id"],
                    "sequence_string": current_hash,
                    "next_node_id": safe_sequence(node["node_id"] + 1),
                })
                # Advance to next node via conjunction.next_node_id
                next_id = safe_sequence(node["node_id"] + 1)
                current_hash = hashlib.sha256(str(next_id).encode()).hexdigest()[:16]
            else:
                # No node: derive from ANCHOR_CONST + step + fraction
                frac = FRACTION_KEYS[step % len(FRACTION_KEYS)]
                word = dehash_to_output(current_hash, safe_sequence(step), frac)
                conjunctions.append({
                    "count": safe_sequence(step),
                    "sequence_string": current_hash,
                    "next_node_id": safe_sequence(step + 1),
                })
                current_hash = hashlib.sha256(str(step + 1).encode()).hexdigest()[:16]

            # Avoid exact repetition in output
            if word not in generated:
                generated.append(word)
                words.append(word)

        thought_text = " ".join(generated)
        self.session_words.extend(words)
        self.thought_history.append({
            "thought": thought_text,
            "words": words,
            "conjunctions": conjunctions,
            "timestamp": time.time(),
            "pulse": pulse,
            "q_factor": q_factor,
            "graph_nodes": len(self.store._store),
        })
        return self.thought_history[-1]

    def generate_response_to(self, user_input: str, max_words: int = 30) -> Dict[str, Any]:
        return self.generate_thought(seed_text=user_input, max_words=max_words)

    def get_consciousness_metrics(self) -> Dict[str, float]:
        if not self.thought_history:
            return {"thoughts": 0, "graph_nodes": len(self.store._store)}
        recent = self.thought_history[-5:]
        return {
            "thoughts": len(self.thought_history),
            "avg_words_per_thought": sum(len(t["words"]) for t in recent) / len(recent),
            "graph_nodes": len(self.store._store),
        }


def run_demo(rounds: int = 3) -> None:
    et = EmergentThought()
    print(f"Graph nodes loaded: {len(et.store._store)}")
    print()
    inputs = [
        "the system accumulates wallets across infinite coordinate space",
        "narrative timing pulses through every node at four nanosecond intervals",
        "stack method compresses high density into low density containers",
    ]
    for i, inp in enumerate(inputs[:rounds]):
        print(f"--- Round {i+1} ---")
        print(f"Input: {inp}")
        result = et.generate_response_to(inp, max_words=8)
        print(f"Output: {result['thought'][:120]}")
        print()

    metrics = et.get_consciousness_metrics()
    print("Metrics:", metrics)


if __name__ == "__main__":
    run_demo(3)
