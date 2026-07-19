"""
persistence.py — Light-ASI LLM Gateway Phase 1
Disk backup and restore for nodes and the graph.

SLA targets from ruleset § 3:
  node_backup_disk : 800ms
  node_backup_mem  : 700ms  (in-memory snapshot)
  node_backup_cloud: 900ms  (stub — Phase 3)

Storage format: JSON per node, gzip compressed.
Index file: graph_index.json (node positions + metadata).
"""

import gzip
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

from engine.core.timing import enforce_sla

logger = logging.getLogger("light-asi.persistence")

DEFAULT_BACKUP_DIR = Path("data/backups")
INDEX_FILE         = "graph_index.json"
NODE_FILE_TEMPLATE = "node_{node_id}.json.gz"


class Persistence:
    """
    Handles disk serialization for NodeGraph and individual nodes.
    All paths are relative to backup_dir.
    """

    def __init__(self, backup_dir: Path = DEFAULT_BACKUP_DIR):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Persistence: backup dir = {self.backup_dir.resolve()}")

    # ── Node serialization ─────────────────────────────────────────────────

    def _node_to_dict(self, node) -> dict:
        return {
            "meta": node.meta.to_dict(),
            "store": {
                seq_hash: inner
                for seq_hash, inner in node.store._store.items()
            },
            "overflow_log": node.store._overflow_log,
            "conjunction": list(node.conjunction),
        }

    def _node_path(self, node_id: int) -> Path:
        return self.backup_dir / NODE_FILE_TEMPLATE.format(node_id=node_id)

    # ── Single Node Backup ─────────────────────────────────────────────────

    @enforce_sla("node_backup_disk")
    def backup_node(self, node) -> Path:
        """Serialize one node to a gzip-compressed JSON file."""
        data = self._node_to_dict(node)
        path = self._node_path(node.meta.node_id)
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f, default=str)
        logger.debug(f"Node backed up: {path}")
        return path

    def restore_node_store(self, node_id: int, store) -> bool:
        """Restore a NodeStore's contents from disk into an existing store object."""
        path = self._node_path(node_id)
        if not path.exists():
            logger.warning(f"No backup found for node {node_id}")
            return False
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        store._store = data.get("store", {})
        store._overflow_log = data.get("overflow_log", [])
        logger.info(f"Node {node_id} store restored from {path}")
        return True

    # ── Full Graph Backup ─────────────────────────────────────────────────

    @enforce_sla("node_backup_disk")
    def backup_graph(self, graph) -> dict:
        """
        Backup every node and write an index file.
        Returns a summary dict.
        """
        index = {
            "timestamp": time.time(),
            "node_count": len(graph._nodes),
            "nodes": [],
        }
        saved = 0
        for node in graph._nodes:
            try:
                path = self.backup_node(node)
                index["nodes"].append({
                    "position": node.meta.position,
                    "node_id": node.meta.node_id,
                    "file": path.name,
                })
                saved += 1
            except Exception as e:
                logger.error(f"Failed to backup node {node.meta.node_id}: {e}")

        index_path = self.backup_dir / INDEX_FILE
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

        summary = {
            "saved": saved,
            "total": len(graph._nodes),
            "index": str(index_path),
            "timestamp": index["timestamp"],
        }
        logger.info(f"Graph backup complete: {saved}/{len(graph._nodes)} nodes")
        return summary

    # ── In-Memory Snapshot ─────────────────────────────────────────────────

    @enforce_sla("node_backup_mem")
    def snapshot_graph(self, graph) -> dict:
        """
        Build a full in-memory snapshot dict (no disk I/O).
        Useful for fast rollback.
        """
        return {
            "timestamp": time.time(),
            "nodes": [self._node_to_dict(n) for n in graph._nodes],
        }

    # ── Index Loading ──────────────────────────────────────────────────────

    def load_index(self) -> Optional[dict]:
        """Load the graph index file if it exists."""
        path = self.backup_dir / INDEX_FILE
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def backup_dir_size_mb(self) -> float:
        total = sum(p.stat().st_size for p in self.backup_dir.rglob("*") if p.is_file())
        return round(total / (1024 * 1024), 3)

    def __repr__(self) -> str:
        return f"Persistence(dir={self.backup_dir}, size={self.backup_dir_size_mb()}MB)"
