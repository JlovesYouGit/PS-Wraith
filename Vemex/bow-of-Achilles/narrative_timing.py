"""
narrative_timing.py — Narrative Timing Quantum Layer
Bleeds the 4ns base quantum into Python execution timing,
making narrative time the reference clock for the pipeline.
"""

import time
from typing import Optional

# Base narrative quantum from instruction.md.txt:
# The remembrances starts at 1ns, 2ns, 3ns, 4ns, 5ns = five sequence order
BASE_QUANTUM_NS = 4  # 4 nanoseconds = narrative tick
NARRATIVE_ORIGIN_NS = time.perf_counter_ns()  # anchor point


def narrative_tick() -> int:
    """Return current narrative time in nanoseconds since module load."""
    return max(0, time.perf_counter_ns() - NARRATIVE_ORIGIN_NS)


def narrative_delay(q: int = 0) -> float:
    """
    Derive a Python sleep delay from narrative quantum.
    5^q scaling: higher q = faster narrative pulse.
    Base unit = BASE_QUANTUM_NS nanoseconds.
    """
    if q < 0:
        q = 0
    ticks = 5 ** q
    return (ticks * BASE_QUANTUM_NS) / 1e9  # convert to seconds


class NarrativeTimer:
    """Context manager that measures execution in narrative nanoseconds."""

    def __init__(self, label: str = ""):
        self.label = label
        self.start_ns: Optional[int] = None
        self.end_ns: Optional[int] = None

    def __enter__(self):
        self.start_ns = narrative_tick()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_ns = narrative_tick()
        return False

    @property
    def elapsed_ns(self) -> int:
        if self.start_ns is None or self.end_ns is None:
            return 0
        return self.end_ns - self.start_ns

    @property
    def elapsed_ticks(self) -> float:
        return self.elapsed_ns / BASE_QUANTUM_NS

    def __str__(self) -> str:
        return (
            f"NarrativeTimer[{self.label}] "
            f"{self.elapsed_ns}ns / {self.elapsed_ticks:.1f} ticks"
        )


def narrative_pulse(current_tick: int = 0) -> int:
    """
    Return narrative pulse count: 1ns, 2ns, 3ns, 4ns, 5ns -> 1, 2, 3, 4, 5.
    Wraps at 5, mapping physical ticks to the 5-sequence order.
    """
    return ((current_tick - 1) % 5) + 1


def narrative_sleep(q: int = 0) -> None:
    """Sleep for narrative-derived duration."""
    time.sleep(narrative_delay(q))


# Convenience: 4ns cadence reference
FOUR_NS = BASE_QUANTUM_NS  # 4ns anchor
FIVE_SEQUENCE = [1, 2, 3, 4, 5]  # ns sequence from instruction.md.txt


def get_narrative_state() -> dict:
    """Snapshot current narrative timing state."""
    tick = narrative_tick()
    return {
        "base_quantum_ns": BASE_QUANTUM_NS,
        "elapsed_ns": tick,
        "elapsed_ticks": tick / BASE_QUANTUM_NS,
        "pulse": narrative_pulse(tick // BASE_QUANTUM_NS),
        "q_factor": 5 ** max(0, (tick // BASE_QUANTUM_NS) % 16),
    }


if __name__ == "__main__":
    with NarrativeTimer("demo") as t:
        narrative_sleep(0)
    print(t)
    print(get_narrative_state())
