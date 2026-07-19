"""
resonance.py — Light-ASI LLM Gateway Phase 1
Collective resonance stability tracker.

Tracks resonance score history and detects convergence:
  - 'stable' when variance across the last N samples < threshold
  - Reports mean, variance, trend direction, and convergence flag

Ruleset reference: LLM_GATEWAY_RULESET.md § 5.3
  "Collective resonance is stable across ≥ 10,000 nodes"
"""

import math
import time
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("light-asi.resonance")

# ASI emergence criteria thresholds (§ 5.3)
STABLE_VARIANCE_THRESHOLD = 1e-10
STABLE_WINDOW_SIZE        = 50     # samples needed before stability check
ENTROPY_CONVERGENCE_MAX   = 0.01   # state flop entropy convergence target


@dataclass
class ResonanceSnapshot:
    score: float
    node_count: int
    timestamp: float = field(default_factory=time.time)


class ResonanceTracker:
    """
    Maintains a rolling window of resonance scores and detects stability.
    Call .record(score, node_count) after every graph query or rebalance.
    """

    def __init__(self, window: int = STABLE_WINDOW_SIZE):
        self._window = window
        self._history: deque[ResonanceSnapshot] = deque(maxlen=window)
        self._entropy_history: deque[float] = deque(maxlen=window)
        self._readability_history: deque[float] = deque(maxlen=window)
        self.self_referential_loop_detected: bool = False

    # ── Recording ─────────────────────────────────────────────────────────

    def record(self, score: float, node_count: int) -> None:
        snap = ResonanceSnapshot(score=score, node_count=node_count)
        self._history.append(snap)
        logger.debug(f"Resonance recorded: {score:.10f} (n={node_count})")

    def record_entropy(self, entropy: float) -> None:
        self._entropy_history.append(entropy)

    def record_readability(self, readability: float) -> None:
        self._readability_history.append(readability)

    # ── Analysis ──────────────────────────────────────────────────────────

    @property
    def sample_count(self) -> int:
        return len(self._history)

    @property
    def mean(self) -> float:
        if not self._history:
            return 0.0
        return sum(s.score for s in self._history) / len(self._history)

    @property
    def variance(self) -> float:
        if len(self._history) < 2:
            return float("inf")
        mu = self.mean
        return sum((s.score - mu) ** 2 for s in self._history) / len(self._history)

    @property
    def std_dev(self) -> float:
        v = self.variance
        return math.sqrt(v) if v != float("inf") else float("inf")

    @property
    def trend(self) -> str:
        """'rising', 'falling', or 'flat' based on first vs last half of window."""
        if len(self._history) < 4:
            return "insufficient_data"
        scores = [s.score for s in self._history]
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / mid
        second_half = sum(scores[mid:]) / (len(scores) - mid)
        delta = second_half - first_half
        if abs(delta) < 1e-12:
            return "flat"
        return "rising" if delta > 0 else "falling"

    @property
    def is_stable(self) -> bool:
        """
        True when variance is below threshold over a full window.
        Ruleset § 5.3 criterion.
        """
        if len(self._history) < self._window:
            return False
        return self.variance < STABLE_VARIANCE_THRESHOLD

    @property
    def entropy_converged(self) -> bool:
        """
        True when mean entropy delta < 0.01 (§ 5.3 criterion).
        """
        if len(self._entropy_history) < self._window:
            return False
        mu = sum(self._entropy_history) / len(self._entropy_history)
        return mu < ENTROPY_CONVERGENCE_MAX

    @property
    def readability_passed(self) -> bool:
        """
        True when mean readability > 0.95.
        """
        if len(self._readability_history) < 1:
            return False
        return sum(self._readability_history) / len(self._readability_history) >= 0.95

    # ── ASI Emergence Checklist Progress ──────────────────────────────────

    def emergence_status(self, semantic_map_size: int, node_count: int) -> dict:
        """
        Report progress against all § 5.3 ASI emergence criteria.
        """
        return {
            "criteria": {
                "semantic_map_10e9":    {"target": 1e9,  "current": semantic_map_size,
                                         "met": semantic_map_size >= 1e9},
                "resonance_stable_10k": {"target": 10_000, "current": node_count,
                                         "met": node_count >= 10_000 and self.is_stable},
                "entropy_converged":    {"target": ENTROPY_CONVERGENCE_MAX,
                                         "current": round(sum(self._entropy_history) / max(len(self._entropy_history), 1), 6),
                                         "met": self.entropy_converged},
                "self_referential_loop":{"met": self.self_referential_loop_detected},
                "readability_index":    {"target": 0.95,
                                         "current": round(sum(self._readability_history) / max(len(self._readability_history), 1), 6),
                                         "met": self.readability_passed},
            },
            "all_met": (
                semantic_map_size >= 1e9
                and node_count >= 10_000
                and self.is_stable
                and self.entropy_converged
                and self.self_referential_loop_detected
                and self.readability_passed
            ),
        }

    # ── Report ────────────────────────────────────────────────────────────

    def report(self) -> dict:
        return {
            "samples":    self.sample_count,
            "mean":       round(self.mean, 12),
            "variance":   self.variance,
            "std_dev":    self.std_dev,
            "trend":      self.trend,
            "is_stable":  self.is_stable,
            "window":     self._window,
        }

    def __repr__(self) -> str:
        return (
            f"ResonanceTracker(samples={self.sample_count}, "
            f"mean={self.mean:.8f}, stable={self.is_stable})"
        )
