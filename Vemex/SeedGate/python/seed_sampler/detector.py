"""Duplicate detection + reverse-sequence algorithm.

A "threat event" fires when the same `value_sha256` is seen in ≥2 seed
records. For each such group:

  1. Gather all records for that value (the forward trace).
  2. Sort by (origin.timestamp, address, line) for a deterministic order.
  3. Reverse the ordered list. The reversed list is the "reverse trace"
     — the trace back to the earliest observed instance.
  4. Pick the canonical origin (earliest timestamp; ties → smallest path).
  5. Emit a Threat record.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Sequence

from .scanner import Seed


@dataclass
class TraceStep:
    index: int          # 0-based position in the reversed sequence
    address: str
    line: int
    kind: str


@dataclass
class Threat:
    value_sha256: str
    value_preview: str          # first 64 chars of the raw value
    occurrences: int
    canonical: dict             # {address, line, commit, timestamp}
    forward_trace: list[TraceStep] = field(default_factory=list)
    reverse_trace: list[TraceStep] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "value_sha256": self.value_sha256,
            "value_preview": self.value_preview,
            "occurrences": self.occurrences,
            "canonical": self.canonical,
            "forward_trace": [asdict(s) for s in self.forward_trace],
            "reverse_trace": [asdict(s) for s in self.reverse_trace],
        }


def _sort_key(seed: Seed) -> tuple:
    ts = (seed.origin or {}).get("timestamp", 2**62)
    return (ts, seed.address, seed.line)


def detect(seeds: Sequence[Seed]) -> list[Threat]:
    """Group seeds by value_sha256 and emit Threat records for duplicates."""
    groups: dict[str, list[Seed]] = {}
    for s in seeds:
        groups.setdefault(s.value_sha256, []).append(s)

    threats: list[Threat] = []
    for sha, group in groups.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=_sort_key)

        forward = [
            TraceStep(index=i, address=s.address, line=s.line, kind=s.kind)
            for i, s in enumerate(ordered)
        ]
        # Reverse-sequence: same steps, reversed, and re-indexed so
        # index 0 is the newest occurrence and the final index points at
        # the canonical (earliest) instance.
        reverse = [
            TraceStep(index=i, address=s.address, line=s.line, kind=s.kind)
            for i, s in enumerate(reversed(ordered))
        ]

        earliest = ordered[0]
        canonical = {
            "address": earliest.address,
            "line": earliest.line,
            "commit": (earliest.origin or {}).get("commit"),
            "timestamp": (earliest.origin or {}).get("timestamp"),
        }

        preview = ordered[0].value[:64]
        threats.append(Threat(
            value_sha256=sha,
            value_preview=preview,
            occurrences=len(group),
            canonical=canonical,
            forward_trace=forward,
            reverse_trace=reverse,
        ))

    # Sort threats by occurrence count desc, then by canonical address.
    threats.sort(key=lambda t: (-t.occurrences, t.canonical.get("address") or ""))
    return threats
