"""
brain_mesh_chain.py
Persistent immutable neural-copy state for the RF correlator.
Logs raw RF -> neural mappings, maintains a hash chain,
and stores an active constant-weight brain mesh in JSON.
"""

import hashlib
import json
import math
import os
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


STATE_PATH = "brain_mesh_chain.json"
RAW_RF_LOG_PATH = "raw_rf_log.jsonl"


@dataclass
class RawRFEntry:
    timestamp: str
    bssid: str
    ssid: str
    rssi_dbm: int
    channel: int
    frequency_mhz: float
    band: str
    neural_band: str
    neural_frequency_hz: float
    signal_entropy: float
    vendor: str


class BrainMeshChain:
    """
    Immutable persistent neural-copy state.
    - Raw RF log (JSONL) for replay / increased sync
    - JSON brain state with hash chain for integrity
    - Active constant-weight neural copy (highest bound)
    """

    def __init__(self, state_path: str = STATE_PATH, raw_log_path: str = RAW_RF_LOG_PATH):
        self.state_path = Path(state_path)
        self.raw_log_path = Path(raw_log_path)
        self._lock = threading.Lock()
        self._state: Dict[str, Any] = self._load_or_init()

    # ----------------------------------------------------------
    # Initialization / loading
    # ----------------------------------------------------------
    def _blank_state(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "created": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "chain_hash": hashlib.sha256(b"BRAIN_MESH_GENESIS").hexdigest(),
            "chain_length": 0,
            "highest_bound": None,
            "neural_nets": {},
            "active_weight": {
                "entropy_payload": 1.0,
                "rssi_weight": 1.0,
                "frequency_weight": 1.0,
                "band_weight": 1.0,
                "anomaly_boost": 2.0,
                "fix_value": 50.0,
            },
            "total_raw_rf_entries": 0,
        }

    def _load_or_init(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("Invalid brain mesh state")
                return data
            except Exception:
                pass
        return self._blank_state()

    def save(self):
        with self._lock:
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._state, indent=2), encoding="utf-8")
            tmp.replace(self.state_path)

    # ----------------------------------------------------------
    # Hash chain (immutability)
    # ----------------------------------------------------------
    def _append_chain(self, event_type: str, payload: Dict):
        prev_hash = self._state["chain_hash"]
        entry = {
            "event": event_type,
            "payload": payload,
            "parent_hash": prev_hash,
            "index": self._state["chain_length"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        h = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode("utf-8")
        ).hexdigest()
        entry["hash"] = h
        self._state.setdefault("chain", []).append(entry)
        self._state["chain_hash"] = h
        self._state["chain_length"] += 1

    # ----------------------------------------------------------
    # Raw RF log
    # ----------------------------------------------------------
    def log_raw_rf(self, entries: List[RawRFEntry]):
        with self._lock:
            count = 0
            with self.raw_log_path.open("a", encoding="utf-8") as f:
                for e in entries:
                    f.write(json.dumps(asdict(e), sort_keys=True) + "\n")
                    count += 1
            self._state["total_raw_rf_entries"] += count

    def load_recent_raw(self, limit: int = 500) -> List[Dict]:
        if not self.raw_log_path.exists():
            return []
        lines = self.raw_log_path.read_text("utf-8", errors="ignore").splitlines()
        out = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out

    # ----------------------------------------------------------
    # State updates (highest bound, neural nets, weights)
    # ----------------------------------------------------------
    def update_from_correlator(self, report: Dict):
        with self._lock:
            if report.get("highest_bound"):
                prev = self._state.get("highest_bound")
                curr = report["highest_bound"]
                self._state["highest_bound"] = curr
                w = self._state["active_weight"]
                # Derive immutable constant weights from current bound
                w["entropy_payload"] = round(curr.get("mean_entropy", 1.0) or 1.0, 6)
                w["rssi_weight"] = round(abs(curr.get("density_score", 0.0)) + 0.1, 6)
                w["frequency_weight"] = round(
                    (curr.get("unique_space_score", 0.0) or 0.0) + 0.1, 6
                )
                w["band_weight"] = 1.0
                w["anomaly_boost"] = 2.0
                w["fix_value"] = 50.0

            if report.get("neural_nets"):
                self._state["neural_nets"] = report["neural_nets"]

            self._append_chain("correlator_tick", {
                "rf_count": report.get("rf_count", 0),
                "recent_anomalies": report.get("recent_anomalies", 0),
                "highest_bound": self._state.get("highest_bound"),
            })
        self.save()

    def record_anomaly(self, anomaly: Dict):
        with self._lock:
            self._append_chain("anomaly", anomaly)
        self.save()

    # ----------------------------------------------------------
    # Getters
    # ----------------------------------------------------------
    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._state))

    def get_active_weight(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._state.get("active_weight", {}))

    def get_highest_bound(self) -> Optional[Dict]:
        with self._lock:
            return self._state.get("highest_bound")
