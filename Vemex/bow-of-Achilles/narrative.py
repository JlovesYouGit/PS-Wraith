"""
narrative.py — Mana Ciel Narrative Observation
Writer AGI viewpoint. Logs events as narrative checksum points.
"""

import time
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mana_ciel.coordinate import SynergyCoordinate

STORAGE = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "narrative.json"
logger = logging.getLogger("mana_ciel.narrative")


class NarrativeObserver:
    def __init__(self, coordinate: int | None = None):
        self.coordinate = SynergyCoordinate(coordinate)
        self.narrative_state = "OBSERVER"
        self.last_checksum = ""

    def observe(self, event: str, data: dict[str, Any] | None = None) -> dict:
        point = {
            "timestamp_unix": time.time(),
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "coordinate": self.coordinate.to_dict(),
            "narrative_state": self.narrative_state,
            "event": event,
            "data": data or {},
        }
        raw = json.dumps(point, sort_keys=True, default=str).encode()
        checksum = hashlib.sha256(raw).hexdigest()
        point["checksum"] = checksum
        self.last_checksum = checksum
        self._persist(point)
        logger.debug("Narrative observed: %s", event)
        return point

    def crystallize(self, label: str = "Finalized Form") -> dict:
        crystal = {
            "label": label,
            "coordinate": self.coordinate.to_dict(),
            "final_form_n": 10,
            "checksum_history_length": len(self.load_all()),
            "last_checksum": self.last_checksum,
        }
        self.observe("crystalline_cache_finalized", crystal)
        return crystal

    def _persist(self, point: dict) -> None:
        STORAGE.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if STORAGE.exists():
            try:
                with open(STORAGE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        existing.append(point)
        with open(STORAGE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, default=str)

    def load_all(self) -> list[dict]:
        if not STORAGE.exists():
            return []
        try:
            with open(STORAGE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def __repr__(self) -> str:
        return f"NarrativeObserver(state={self.narrative_state}, coord={self.coordinate.value})"
