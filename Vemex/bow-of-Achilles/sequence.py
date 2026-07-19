"""
sequence.py — Mana Ciel Time Compression Sequence
Extracts sequential temporal intelligence from 1ns to current calendar.
Coordinate: -16 to 1000.
"""

import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

logger = logging.getLogger("mana_ciel.sequence")

STORAGE = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "sequences.json"


class TimeCompressionSequence:
    def __init__(self, coordinate: int | None = None):
        self.coordinate = coordinate
        self.created_at = time.time()
        self.created_iso = datetime.now(timezone.utc).isoformat()
        self.entries: list[dict] = []

    def capture(self, label: str, q: int, payload: str = "") -> dict:
        entry = {
            "timestamp_ns": int(time.time() * 1_000_000),
            "label": label,
            "q": q,
            "intelligence_value": 5 ** q,
            "payload": payload,
            "coordinate": self.coordinate,
        }
        self.entries.append(entry)
        logger.debug("sequence entry: %s", entry)
        return entry

    def seal(self) -> dict:
        from mana_ciel.formula import cumulative_intelligence
        seq = {
            "coordinate": self.coordinate,
            "created_at_iso": self.created_iso,
            "created_at_unix": self.created_at,
            "sealed_at_iso": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(self.entries),
            "entries": self.entries,
            "cumulative_intelligence": cumulative_intelligence(len(self.entries)),
        }
        self._persist(seq)
        return seq

    def _persist(self, seq: dict) -> None:
        STORAGE.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if STORAGE.exists():
            try:
                with open(STORAGE, "r", encoding="utf-8") as f:
                    existing = __import__("json").load(f)
            except Exception:
                existing = []
        existing.append(seq)
        with open(STORAGE, "w", encoding="utf-8") as f:
            __import__("json").dump(existing, f, indent=2, default=str)
        logger.info("Sequence sealed and persisted.")

    @classmethod
    def load_last(cls) -> Optional[dict]:
        if not STORAGE.exists():
            return None
        try:
            with open(STORAGE, "r", encoding="utf-8") as f:
                data = __import__("json").load(f)
                return data[-1] if data else None
        except Exception:
            return None
