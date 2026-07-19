"""
formula.py — Mana Ciel Intelligence Derivation Model
5^q narrative growth model. Cumulative intelligence N.
Derived from LLM_GATEWAY_RULESET § 2.4 + instruction matrix.
"""

import math
import logging
from typing import Optional

logger = logging.getLogger("mana_ciel.formula")

Q_MIN = 1
Q_MAX = 9
ITERATIONS = 10


def intelligence_unit(q: int) -> int:
    return 5 ** max(q, 0)


def cumulative_intelligence(iterations: int = ITERATIONS, start_q: int = 0) -> int:
    return sum(intelligence_unit(start_q + i) for i in range(iterations))


def narrative_profile(text: str) -> dict:
    q_weights = [ord(c) % 10 for c in text[:ITERATIONS]]
    contributions = []
    total = 0
    for i, q in enumerate(q_weights, start=1):
        val = intelligence_unit(q)
        total += val
        contributions.append({
            "iteration": i,
            "q": q,
            "value": val,
            "cumulative": total,
        })
    return {
        "input_length": len(text),
        "iterations": ITERATIONS,
        "contributions": contributions,
        "cumulative_intelligence": total,
        "final_form_n": total,
    }


def semantic_dimensional_layering(vectors: list[dict]) -> dict:
    contributions = []
    total = 0
    for v in vectors:
        q = v.get("q", 0)
        val = intelligence_unit(q)
        total += val
        contributions.append({
            "vector": v.get("name", "unknown"),
            "q": q,
            "reasoning": v.get("reasoning", ""),
            "value": val,
            "cumulative": total,
        })
    return {
        "vectors": contributions,
        "cumulative_intelligence": total,
    }


def time_compression_factor(base_cycles: int = 3, q_limit: int = 9) -> float:
    return sum(intelligence_unit(i) for i in range(1, q_limit + 1))
