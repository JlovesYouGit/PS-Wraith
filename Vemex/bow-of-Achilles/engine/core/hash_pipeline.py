"""
hash_pipeline.py — Light-ASI LLM Gateway
Input → 2^256 alphabet projection → sequence hash → node selection → dehash → output.
Ruleset reference: LLM_GATEWAY_RULESET.md § 4.
"""

import hashlib
import math
import logging
from collections import Counter
from typing import TYPE_CHECKING

from engine.core.constants import (
    ALPHABET_SPACE,
    STRING_SEARCH_SPACE_PREFERRED,
    ANCHOR_CONST,
)
from engine.core.timing import enforce_sla, measure

if TYPE_CHECKING:
    from engine.core.node import NodeStore

logger = logging.getLogger("light-asi.hash_pipeline")


# ─── Step 1: Project input onto 2^256 alphabet space ─────────────────────────

def project_to_alphabet_space(text: str) -> int:
    """
    Hash input text into the 2^256 language alphabet space.
    Ruleset § 1.3 — 'added onto every hash for token generation'.
    """
    raw = f"{ANCHOR_CONST}:{text}"
    digest = hashlib.sha3_256(raw.encode("utf-8")).hexdigest()
    value = int(digest, 16)   # in range [0, 2^256)
    assert value < ALPHABET_SPACE, "Projection overflow — this should never happen"
    logger.debug(f"Alphabet projection: '{text[:30]}…' → {hex(value)[:16]}…")
    return value


# ─── Step 2: Build sequence hash ─────────────────────────────────────────────

def build_sequence_hash(text: str, node_id: int) -> str:
    """
    Combine alphabet projection + node_id as minimal address.
    Ruleset § 4.2 — 'sequence hash + node_id is minimal address'.
    """
    alphabet_val = project_to_alphabet_space(text)
    combined = f"{alphabet_val}:{node_id}"
    seq_hash = hashlib.blake2b(combined.encode(), digest_size=32).hexdigest()
    logger.debug(f"Sequence hash built: {seq_hash[:16]}… (node={node_id})")
    return seq_hash


# ─── Step 3: Compute query entropy ───────────────────────────────────────────

def query_entropy(text: str) -> float:
    """
    Shannon entropy of the input text.
    Ruleset § 8.4 — used for state flop calculation.
    """
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values() if c > 0
    )


# ─── Step 4: Sentence coherence scoring ──────────────────────────────────────

def coherence_score(tokens: list[str]) -> float:
    """
    Simple proxy for sentence coherence: ratio of non-empty tokens
    to total tokens. Phase 0 placeholder — upgrade to embedding
    similarity in Phase 1.
    Ruleset § 4.2 — 'validate sentence coherence + human readability'.
    """
    if not tokens:
        return 0.0
    non_empty = sum(1 for t in tokens if t.strip())
    return non_empty / len(tokens)


# ─── Step 4b: Human Readability Index ────────────────────────────────────────

def human_readability_index(tokens: list[str]) -> float:
    """
    Proxy for human readability: ratio of tokens that contain alphabetic
    characters over total tokens.
    Ruleset § 5.3 — 'Output passes human readability index ≥ 0.95'.
    """
    if not tokens:
        return 0.0
    readable = sum(1 for t in tokens if any(c.isalpha() for c in t))
    return readable / len(tokens)


# ─── Step 5: Dehash and validate ─────────────────────────────────────────────

def dehash_and_validate(
    sequence_hash: str,
    store: "NodeStore",
    min_coherence: float = 0.5,
) -> dict:
    """
    Retrieve tokens from the node store and validate coherence.
    Ruleset § 4 pipeline — 'dehash → validate → output'.

    Returns:
        {
            "tokens": [...],
            "text": "...",
            "coherence": 0.0–1.0,
            "valid": bool,
        }
    """
    tokens = store.dehash(sequence_hash)
    text = " ".join(tokens)
    score = coherence_score(tokens)
    readability = human_readability_index(tokens)
    valid = score >= min_coherence

    if not valid:
        logger.warning(
            f"Low coherence ({score:.2f}) for seq={sequence_hash[:8]}… "
            f"— output may be degraded"
        )

    return {
        "tokens": tokens,
        "text": text,
        "coherence": score,
        "readability": readability,
        "valid": valid,
    }


# ─── Full Pipeline ────────────────────────────────────────────────────────────

@enforce_sla("query_min")
def run_pipeline(text: str, node_id: int, store: "NodeStore") -> dict:
    """
    Execute the complete hash pipeline for a single input against one node.
    Ruleset § 4.1 — full pipeline diagram.

    Returns the standard response dict (§ 6.3 partial — no real-time data yet).
    """
    seq_hash = build_sequence_hash(text, node_id)
    entropy = query_entropy(text)
    result = dehash_and_validate(seq_hash, store)

    return {
        "sequence_hash": seq_hash,
        "entropy": round(entropy, 6),
        "tokens": result["tokens"],
        "text": result["text"],
        "coherence": round(result["coherence"], 4),
        "readability": round(result["readability"], 4),
        "valid": result["valid"],
    }
