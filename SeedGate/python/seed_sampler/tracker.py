"""JSON catalog: read/write and query helpers for tracker.json."""

from __future__ import annotations

import fnmatch
import json
import time
from pathlib import Path
from typing import Iterable

from . import TRACKER_PATH, SNAPSHOT_DIR
from .scanner import Seed
from .detector import Threat

SCHEMA_VERSION = 1


def build(seeds: Iterable[Seed], threats: Iterable[Threat]) -> dict:
    """Assemble the tracker document."""
    return {
        "schema": SCHEMA_VERSION,
        "generated_at": int(time.time()),
        "seeds": [s.to_dict() for s in seeds],
        "threats": [t.to_dict() for t in threats],
        "kernel_results": [],  # populated later by runner.py
    }


def save(doc: dict, path: Path = TRACKER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, sort_keys=False)
        f.write("\n")
    tmp.replace(path)


def load(path: Path = TRACKER_PATH) -> dict:
    if not path.exists():
        return {
            "schema": SCHEMA_VERSION,
            "generated_at": 0,
            "seeds": [],
            "threats": [],
            "kernel_results": [],
        }
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_snapshots(threats: Iterable[Threat]) -> int:
    """Write per-value snapshot JSON files. Returns count written."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for t in threats:
        snap_path = SNAPSHOT_DIR / f"{t.value_sha256}.json"
        with snap_path.open("w", encoding="utf-8") as f:
            json.dump(t.to_dict(), f, indent=2)
            f.write("\n")
        count += 1
    return count


# --- Queries ---------------------------------------------------------------

def q_by_value_prefix(doc: dict, prefix: str) -> list[dict]:
    prefix = prefix.lower()
    return [s for s in doc.get("seeds", [])
            if s["value_sha256"].startswith(prefix)]


def q_by_path_glob(doc: dict, glob: str) -> list[dict]:
    return [s for s in doc.get("seeds", [])
            if fnmatch.fnmatchcase(s["address"], glob)]


def q_by_origin(doc: dict, commit_prefix: str) -> list[dict]:
    commit_prefix = commit_prefix.lower()
    out = []
    for s in doc.get("seeds", []):
        origin = s.get("origin") or {}
        commit = (origin.get("commit") or "").lower()
        if commit.startswith(commit_prefix):
            out.append(s)
    return out


def q_by_kind(doc: dict, kind: str) -> list[dict]:
    return [s for s in doc.get("seeds", []) if s["kind"] == kind]


def q_duplicates(doc: dict) -> list[dict]:
    return list(doc.get("threats", []))


def summary(doc: dict) -> dict:
    seeds = doc.get("seeds", [])
    threats = doc.get("threats", [])
    kinds: dict[str, int] = {}
    repos: dict[str, int] = {}
    for s in seeds:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
        repo = (s.get("origin") or {}).get("repo") or "(untracked)"
        repos[repo] = repos.get(repo, 0) + 1
    return {
        "generated_at": doc.get("generated_at", 0),
        "seed_count": len(seeds),
        "threat_count": len(threats),
        "kinds": dict(sorted(kinds.items(), key=lambda kv: -kv[1])),
        "repos": dict(sorted(repos.items(), key=lambda kv: -kv[1])),
        "kernel_results": len(doc.get("kernel_results", [])),
    }
