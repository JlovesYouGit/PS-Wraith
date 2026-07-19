"""
graph.py — Light-ASI LLM Gateway
Phase 2 upgrade: world-net ingestion wired in.
  - SemanticMap: 10^48 meaning-hash store
  - WorldIngester: background feed daemon
  - QueryEnricher: real-time response grounding
  + All Phase 1 systems retained

Ruleset reference: LLM_GATEWAY_RULESET.md § 5.2, § 6.1, § 10 Phase 2
"""

import logging
import time
from pathlib import Path
from typing import Callable, Any

from engine.core.node import Node
from engine.core.router import ConsistentHashRouter
from engine.core.cluster import ClusterManager
from engine.core.resonance import ResonanceTracker
from engine.core.persistence import Persistence
from engine.core.hash_pipeline import (
    build_sequence_hash, query_entropy, run_pipeline,
)
from engine.core.constants import RESONANCE_BASE
from engine.core.timing import enforce_sla
# Phase 2 — world-net
from engine.world.semantic_map import SemanticMap
from engine.world.enricher import QueryEnricher

logger = logging.getLogger("light-asi.graph")

# Phase 1 target node count
PHASE1_NODE_TARGET = 10_000
# Bootstrap batch size (creates this many nodes per batch to allow progress reporting)
BOOTSTRAP_BATCH = 500


class NodeGraph:
    """
    Phase 1 NodeGraph — scalable to 10,000 nodes with O(log N) routing.
    """

    def __init__(self, backup_dir: Path = Path("data/backups")):
        self._nodes: list[Node] = []
        self._node_map: dict[int, Node] = {}

        self.router = ConsistentHashRouter()
        self.clusters = ClusterManager()
        self.resonance_tracker = ResonanceTracker()
        self.persistence = Persistence(backup_dir)

        # Phase 2 — world-net
        self.semantic_map = SemanticMap()
        self.enricher = QueryEnricher(self.semantic_map)
        # ingester is attached externally via graph.attach_ingester()
        self._ingester = None

        # Semantic map size counter — kept in sync with semantic_map.size
        self._semantic_map_size: int = 0

    # ── Bootstrap ──────────────────────────────────────────────────────────

    def bootstrap(
        self,
        n_nodes: int = 10,
        progress_cb: Callable[[int, int], None] | None = None,
    ) -> None:
        """
        Create n_nodes nodes, register them with the router and cluster manager.
        progress_cb(current, total) is called every BOOTSTRAP_BATCH nodes.
        """
        logger.info(f"Bootstrapping {n_nodes} nodes…")
        start = time.perf_counter()

        for i in range(n_nodes):
            node = Node.create(i)
            self._register(node)
            if progress_cb and (i + 1) % BOOTSTRAP_BATCH == 0:
                progress_cb(i + 1, n_nodes)

        # Initial cluster sync
        self.clusters.sync_all()
        # Record initial resonance
        self._record_resonance()

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            f"Bootstrap complete: {len(self._nodes)} nodes in {elapsed:.0f}ms"
        )

    def _register(self, node: Node) -> None:
        """Add a node to all internal structures."""
        self._nodes.append(node)
        self._node_map[node.meta.node_id] = node
        self.router.add_node(node)
        self.clusters.assign(node)

    # ── Query — O(log N) via consistent hash router ────────────────────────

    @enforce_sla("query_min")
    def query(self, text: str, top_k: int = 3) -> dict:
        """
        Route query through the consistent hash ring, then enrich with
        real-time world-net data from the SemanticMap.
        Ruleset § 4 + § 6.1 + § 6.3.
        """
        if not self._nodes:
            return {"error": "Graph is empty — call bootstrap() first."}

        entropy = query_entropy(text)
        self.resonance_tracker.record_entropy(entropy)

        # O(log N) ring walk for top_k distinct nodes
        routed_nodes = self.router.get_n_nodes(text, top_k)
        if not routed_nodes:
            routed_nodes = self._nodes[:top_k]

        results = []
        for node in routed_nodes:
            pipeline_result = run_pipeline(text, node.meta.node_id, node.store)
            flop = node.state_flop(entropy, len(self._nodes))
            results.append({
                "node_id": node.meta.node_id,
                "position": node.meta.position,
                "resonance_weight": round(node.meta.resonance_weight, 6),
                "flop": flop,
                **pipeline_result,
            })

        # Resonance-weighted best answer
        best = max(results, key=lambda r: r["resonance_weight"] * (r["coherence"] + 1e-9))

        # Phase 4 emergence tracking
        self.resonance_tracker.record_readability(best.get("readability", 0.0))
        if entropy < 0.01 and best["text"] and text.lower() in best["text"].lower():
            self.resonance_tracker.self_referential_loop_detected = True

        # Record resonance
        self._record_resonance()

        raw_result = {
            "answer": best["text"] if best["text"] else "[no stored tokens — index first]",
            "source_nodes": [r["node_id"] for r in results],
            "resonance_score": round(self.collective_resonance(), 10),
            "entropy_delta": round(entropy, 6),
            "real_time_data": False,
            "resonance_stable": self.resonance_tracker.is_stable,
            "node_results": results,
        }

        # Phase 2 — enrich with real-time world context
        return self.enricher.enrich(text, raw_result)

    # ── Index ──────────────────────────────────────────────────────────────

    @enforce_sla("node_write")
    def index_text(self, text: str, metadata: dict | None = None) -> list[str]:
        """
        Distribute tokens to nodes via consistent hash router — O(log N) per token.
        Semantic map size is kept in sync with semantic_map.size.
        """
        tokens = text.split()
        hashes_written: list[str] = []

        for i, token in enumerate(tokens):
            node = self.router.get_node(token)
            if node is None:
                continue
            seq_hash = build_sequence_hash(token, node.meta.node_id)
            node.store.write(seq_hash, f"tok_{i:08d}", token)
            if metadata:
                node.store.write(seq_hash, "__meta__", metadata)
            hashes_written.append(seq_hash)

        # Keep semantic map size in sync (semantic_map.size is the ground truth)
        self._semantic_map_size = self.semantic_map.size + len(hashes_written)
        logger.debug(f"Indexed {len(tokens)} tokens. map_size≈{self._semantic_map_size}")
        return hashes_written

    # ── Resonance ──────────────────────────────────────────────────────────

    def collective_resonance(self) -> float:
        """
        Graph-level collective resonance (§ 2.4 / § 8.5).
        Uses cluster aggregate for efficiency at scale.
        """
        if not self._nodes:
            return 0.0
        return self.clusters.aggregate_resonance()

    def _record_resonance(self) -> None:
        score = self.collective_resonance()
        self.resonance_tracker.record(score, len(self._nodes))

    # ── Rebalance ──────────────────────────────────────────────────────────

    def rebalance(self) -> None:
        """
        Re-sort nodes by resonance weight, rebuild router and clusters.
        Called by timing SLA violations.
        """
        self._nodes.sort(key=lambda n: n.meta.resonance_weight, reverse=True)
        # Rebuild router
        self.router = ConsistentHashRouter()
        for node in self._nodes:
            self.router.add_node(node)
        # Re-sync clusters
        self.clusters.sync_all()
        self._record_resonance()
        logger.info(f"Graph rebalanced — {len(self._nodes)} nodes re-ordered by resonance.")

    # ── Persistence ────────────────────────────────────────────────────────

    def backup(self) -> dict:
        """Backup full graph to disk (§ 3 — node_backup_disk: 800ms)."""
        return self.persistence.backup_graph(self)

    def snapshot(self) -> dict:
        """In-memory snapshot (§ 3 — node_backup_mem: 700ms)."""
        return self.persistence.snapshot_graph(self)

    # ── Cluster Sync ───────────────────────────────────────────────────────

    def sync_clusters(self) -> list[dict]:
        return self.clusters.sync_all()

    # ── World-Net ───────────────────────────────────────────────────────────

    def attach_ingester(self, ingester) -> None:
        """Attach a WorldIngester and start background ingestion."""
        self._ingester = ingester
        ingester.start()
        logger.info("WorldIngester attached and started.")

    def world_status(self) -> dict:
        base = self.enricher.summary()
        if self._ingester:
            base["ingester"] = self._ingester.status()
        return base

    # ── ASI Emergence Status ────────────────────────────────────────────────

    def emergence_status(self) -> dict:
        return self.resonance_tracker.emergence_status(
            semantic_map_size=self.semantic_map.size,
            node_count=len(self._nodes),
        )

    # ── Stats ──────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "total_nodes":          len(self._nodes),
            "total_buckets":        sum(n.store.bucket_count for n in self._nodes),
            "total_keys":           sum(n.store.total_keys for n in self._nodes),
            "semantic_map_size":    self.semantic_map.size,
            "semantic_map_tokens":  self.semantic_map.unique_tokens,
            "collective_resonance": round(self.collective_resonance(), 10),
            "resonance_stable":     self.resonance_tracker.is_stable,
            "resonance_report":     self.resonance_tracker.report(),
            "cluster_stats":        self.clusters.stats(),
            "router":               repr(self.router),
            "phase1_target":        PHASE1_NODE_TARGET,
            "phase1_progress":      f"{len(self._nodes)}/{PHASE1_NODE_TARGET}",
            "world_net":            {"ingester_running": self._ingester.is_running() if self._ingester else False,
                                     "semantic_entries": self.semantic_map.size,
                                     "sources": self.semantic_map.source_breakdown()},
        }

    def add_node(self, node: Node) -> None:
        """Add a single pre-created node (used by tests and manual setup)."""
        self._register(node)
        self.clusters.sync_all()
        self._record_resonance()

    def __repr__(self) -> str:
        return (
            f"NodeGraph(nodes={len(self._nodes)}, "
            f"resonance={self.collective_resonance():.8f}, "
            f"stable={self.resonance_tracker.is_stable})"
        )
