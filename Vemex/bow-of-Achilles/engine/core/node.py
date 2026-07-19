"""
node.py — Light-ASI LLM Gateway
Core Node implementation: hash-map-of-hash-maps storage, lexical mode,
fraction-based sub-addressing, and collective resonance weight.
Ruleset reference: LLM_GATEWAY_RULESET.md § 2.
"""

import hashlib
import math
import logging
from dataclasses import dataclass, field
from typing import Any

from engine.core.constants import (
    ANCHOR_CONST, RANGE_MIN, RANGE_MAX,
    RESONANCE_BASE, NODE_IP_TIERS, NODE_FRACTIONS,
    SEQUENCE_OVERFLOW_MODULO, SEQUENCE_TARGET,
)
from engine.core.timing import enforce_sla

logger = logging.getLogger("light-asi.node")


# ─── Node Metadata ────────────────────────────────────────────────────────────

@dataclass
class NodeMeta:
    position: int
    node_id: int
    hash_hex: str
    virtual_ip_tier: int
    resonance_weight: float
    range_min: int = RANGE_MIN
    range_max: int = RANGE_MAX
    anchor: str = ANCHOR_CONST

    def to_dict(self) -> dict:
        return self.__dict__.copy()


# ─── Node Store (hash-map-of-hash-maps) ───────────────────────────────────────

class NodeStore:
    """
    Minimal → Minimal → Minimal / Maximal layered index.
    Outer key: sequence_hash (str)
    Inner key: sub-address key (str)
    Value:     any serialisable object

    Ruleset § 2.1 — 'hash map of hash maps within every node'
    """

    def __init__(self, node_id: int):
        self.node_id = node_id
        # outer: seq_hash → inner: key → value
        self._store: dict[str, dict[str, Any]] = {}
        # overflow log
        self._overflow_log: list[dict] = []
        # lexical index: ordered token list per sequence
        self._lexical_index: dict[str, list[str]] = {}

    # ── WRITE ──────────────────────────────────────────────────────────────

    @enforce_sla("node_write")
    def write(self, sequence_hash: str, key: str, value: Any) -> None:
        if sequence_hash not in self._store:
            self._store[sequence_hash] = {}
        self._store[sequence_hash][key] = value
        logger.debug(f"Node[{self.node_id}] write seq={sequence_hash[:8]}… key={key}")

    # ── READ ───────────────────────────────────────────────────────────────

    @enforce_sla("node_read")
    def read(self, sequence_hash: str, key: str) -> Any:
        return self._store.get(sequence_hash, {}).get(key)

    # ── UPDATE ─────────────────────────────────────────────────────────────

    @enforce_sla("node_update")
    def update(self, sequence_hash: str, key: str, value: Any) -> bool:
        if sequence_hash in self._store and key in self._store[sequence_hash]:
            self._store[sequence_hash][key] = value
            return True
        return False

    # ── DEHASH → sentence-coherent output ─────────────────────────────────

    @enforce_sla("node_read")
    def dehash(self, sequence_hash: str) -> list[str]:
        """
        Return all stored values under a sequence hash, sorted for
        sentence coherence (lexical order of keys).
        Ruleset § 4.2 — 'dehash → validate sentence coherence'
        """
        bucket = self._store.get(sequence_hash, {})
        tokens = [str(v) for _, v in sorted(bucket.items())]
        return tokens

    # ── REINDEX ────────────────────────────────────────────────────────────

    @enforce_sla("node_reindex")
    def reindex(self) -> None:
        """Rebuild the lexical index from scratch."""
        self._lexical_index = {}
        for seq_hash, inner in self._store.items():
            self._lexical_index[seq_hash] = [
                str(v) for _, v in sorted(inner.items())
            ]
        logger.info(f"Node[{self.node_id}] reindex complete — {len(self._store)} buckets")

    # ── SWAP ───────────────────────────────────────────────────────────────

    @enforce_sla("node_swap")
    def swap(self, seq_a: str, seq_b: str) -> None:
        """Swap two sequence buckets in-place."""
        a = self._store.pop(seq_a, {})
        b = self._store.pop(seq_b, {})
        if b:
            self._store[seq_a] = b
        if a:
            self._store[seq_b] = a

    # ── SUB-ADDRESS (fraction seek) ─────────────────────────────────────────

    def fraction_read(self, sequence_hash: str, fraction_name: str) -> Any:
        """
        Use a named node fraction as a precision cursor into the inner map.
        Ruleset § 2.2 — NODE_FRACTION_MAP.
        """
        frac = NODE_FRACTIONS.get(fraction_name)
        if frac is None:
            raise KeyError(f"Unknown fraction: {fraction_name}")
        bucket = self._store.get(sequence_hash, {})
        keys = sorted(bucket.keys())
        if not keys:
            return None
        # float seek: pick the key at fractional position
        idx = int(frac * (len(keys) - 1))
        return bucket[keys[idx]]

    # ── OVERFLOW GUARD ─────────────────────────────────────────────────────

    def safe_sequence(self, seq: int) -> int:
        """
        If seq > 10^3, apply modulo 1000 and log to overflow record.
        Ruleset § 4.3.
        """
        if seq > SEQUENCE_TARGET:
            self._overflow_log.append({"original": seq, "modulo": seq % SEQUENCE_OVERFLOW_MODULO})
            logger.warning(f"Node[{self.node_id}] overflow: {seq} → {seq % SEQUENCE_OVERFLOW_MODULO}")
            return seq % SEQUENCE_OVERFLOW_MODULO
        return seq

    # ── STATS ───────────────────────────────────────────────────────────────

    @property
    def bucket_count(self) -> int:
        return len(self._store)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self._store.values())

    def __repr__(self) -> str:
        return (
            f"NodeStore(id={self.node_id}, "
            f"buckets={self.bucket_count}, keys={self.total_keys})"
        )


# ─── Node Factory ─────────────────────────────────────────────────────────────

class Node:
    """
    A fully initialised node: metadata + store + resonance weight.
    Created via Node.create(position) — never instantiate directly.
    """

    def __init__(self, meta: NodeMeta, store: NodeStore):
        self.meta = meta
        self.store = store
        # Wrapped string connection: (count, sequence_string, next_node_id)
        self.conjunction: tuple[int, str, int | None] = (0, "", None)

    @classmethod
    def create(cls, position: int) -> "Node":
        """
        Assign node ID by Python env via integer-position hash map.
        Ruleset § 2.1.
        """
        raw = f"{ANCHOR_CONST}:{position}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        node_id = (int(h, 16) % (RANGE_MAX - RANGE_MIN)) + RANGE_MIN

        # Virtual IP tier
        tier = NODE_IP_TIERS[-1]
        for t in NODE_IP_TIERS:
            if position <= t:
                tier = t
                break

        # Resonance weight: 5^15 ^ (node_id / RANGE_MAX)
        norm = node_id / RANGE_MAX if RANGE_MAX != 0 else 0
        resonance = RESONANCE_BASE ** norm

        meta = NodeMeta(
            position=position,
            node_id=node_id,
            hash_hex=h,
            virtual_ip_tier=tier,
            resonance_weight=resonance,
        )
        store = NodeStore(node_id)
        node = cls(meta, store)
        logger.debug(f"Node created: pos={position} id={node_id} tier={tier}")
        return node

    # ── State Flop (entropy-driven 0→1) ────────────────────────────────────

    def state_flop(self, query_entropy: float, node_count: int) -> int:
        """
        Returns 0 or 1 based on entropy of query × log(node_count).
        Ruleset § 2.5 / § 8.4.
        """
        combined = query_entropy * math.log(node_count + 1)
        return 1 if (combined % 1) >= 0.5 else 0

    # ── Conjunction update ─────────────────────────────────────────────────

    def set_conjunction(self, count: int, sequence: str, next_id: int | None) -> None:
        """3-value conjunction: (count, sequence_string, next_node_id)."""
        self.conjunction = (count, sequence, next_id)

    def __repr__(self) -> str:
        return (
            f"Node(pos={self.meta.position}, "
            f"id={self.meta.node_id}, "
            f"tier={self.meta.virtual_ip_tier}, "
            f"res={self.meta.resonance_weight:.4f})"
        )
