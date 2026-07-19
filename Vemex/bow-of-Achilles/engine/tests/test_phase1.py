"""
test_phase1.py — Light-ASI Phase 1 Tests
Router, resonance tracker, cluster manager, persistence, and 10k-node graph.
"""

import sys, os, tempfile, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from pathlib import Path
import pytest

from engine.core.node import Node
from engine.core.router import ConsistentHashRouter
from engine.core.resonance import ResonanceTracker, STABLE_VARIANCE_THRESHOLD
from engine.core.cluster import NodeCluster, ClusterManager
from engine.core.persistence import Persistence
from engine.core.graph import NodeGraph, PHASE1_NODE_TARGET
from engine.core.constants import NODE_IP_TIERS


# ─── Consistent Hash Router ───────────────────────────────────────────────────

class TestRouter:
    def test_empty_router_returns_none(self):
        r = ConsistentHashRouter()
        assert r.get_node("any_key") is None

    def test_single_node_always_returned(self):
        r = ConsistentHashRouter()
        n = Node.create(0)
        r.add_node(n)
        for key in ["hello", "world", "test", "abc123"]:
            assert r.get_node(key) is not None

    def test_routing_is_deterministic(self):
        r = ConsistentHashRouter()
        for i in range(10):
            r.add_node(Node.create(i))
        node_a = r.get_node("consistent_key")
        node_b = r.get_node("consistent_key")
        assert node_a.meta.node_id == node_b.meta.node_id

    def test_get_n_nodes_distinct(self):
        r = ConsistentHashRouter()
        for i in range(20):
            r.add_node(Node.create(i))
        nodes = r.get_n_nodes("test_key", 5)
        ids = [n.meta.node_id for n in nodes]
        assert len(ids) == len(set(ids)), "get_n_nodes must return distinct nodes"

    def test_remove_node(self):
        r = ConsistentHashRouter()
        nodes = [Node.create(i) for i in range(5)]
        for n in nodes:
            r.add_node(n)
        target = nodes[2]
        r.remove_node(target.meta.node_id)
        assert r.node_count == 4
        # The removed node should never be returned
        for _ in range(50):
            routed = r.get_node(f"key_{_}")
            assert routed.meta.node_id != target.meta.node_id

    def test_ring_size(self):
        r = ConsistentHashRouter()
        from engine.core.router import VIRTUAL_POINTS_PER_NODE
        for i in range(10):
            r.add_node(Node.create(i))
        assert r.ring_size == 10 * VIRTUAL_POINTS_PER_NODE

    def test_distribution_reasonable(self):
        """Each of 100 nodes should handle at least 1 out of 1000 keys."""
        r = ConsistentHashRouter()
        n = 100
        for i in range(n):
            r.add_node(Node.create(i))
        counts: dict[int, int] = {}
        for i in range(1000):
            node = r.get_node(f"test_key_{i}")
            counts[node.meta.node_id] = counts.get(node.meta.node_id, 0) + 1
        # At least 80% of nodes should handle at least 1 key (good distribution)
        assert len(counts) >= n * 0.8


# ─── Resonance Tracker ────────────────────────────────────────────────────────

class TestResonanceTracker:
    def test_empty_tracker(self):
        t = ResonanceTracker()
        assert t.mean == 0.0
        assert t.is_stable is False

    def test_record_and_mean(self):
        t = ResonanceTracker(window=5)
        for v in [1.0, 2.0, 3.0, 4.0, 5.0]:
            t.record(v, 10)
        assert abs(t.mean - 3.0) < 1e-9

    def test_stability_detected(self):
        t = ResonanceTracker(window=10)
        # Feed identical values — variance = 0 → stable
        for _ in range(10):
            t.record(0.0000001234, 10_000)
        assert t.is_stable

    def test_not_stable_with_variance(self):
        t = ResonanceTracker(window=10)
        for i in range(10):
            t.record(float(i), 100)
        assert not t.is_stable

    def test_trend_rising(self):
        t = ResonanceTracker(window=10)
        for i in range(10):
            t.record(float(i), 10)
        assert t.trend == "rising"

    def test_trend_falling(self):
        t = ResonanceTracker(window=10)
        for i in range(10, 0, -1):
            t.record(float(i), 10)
        assert t.trend == "falling"

    def test_entropy_convergence(self):
        t = ResonanceTracker(window=5)
        for _ in range(5):
            t.record_entropy(0.005)
        assert t.entropy_converged

    def test_emergence_status_structure(self):
        t = ResonanceTracker()
        status = t.emergence_status(semantic_map_size=0, node_count=10)
        assert "criteria" in status
        assert "all_met" in status
        assert not status["all_met"]


# ─── Cluster Manager ──────────────────────────────────────────────────────────

class TestClusterManager:
    def test_assign_and_stats(self):
        cm = ClusterManager()
        for i in range(20):
            cm.assign(Node.create(i))
        stats = cm.stats()
        total = sum(v["nodes"] for v in stats.values())
        assert total == 20

    def test_cluster_sync(self):
        cm = ClusterManager()
        nodes = [Node.create(i) for i in range(5)]
        for n in nodes:
            cm.assign(n)
        results = cm.sync_all()
        assert len(results) > 0

    def test_aggregate_resonance(self):
        cm = ClusterManager()
        for i in range(10):
            cm.assign(Node.create(i))
        r = cm.aggregate_resonance()
        assert r > 0

    def test_local_sync_specific_tier(self):
        cm = ClusterManager()
        n = Node.create(0)
        cm.assign(n)
        tier = n.meta.virtual_ip_tier
        result = cm.local_sync(tier)
        assert result is not None


# ─── Persistence ──────────────────────────────────────────────────────────────

class TestPersistence:
    def test_backup_and_restore_node(self, tmp_path):
        p = Persistence(tmp_path)
        node = Node.create(0)
        node.store.write("seq_test", "tok_000000", "hello")
        path = p.backup_node(node)
        assert path.exists()
        # Restore into a fresh store
        from engine.core.node import NodeStore
        fresh = NodeStore(node.meta.node_id)
        ok = p.restore_node_store(node.meta.node_id, fresh)
        assert ok
        assert fresh.read("seq_test", "tok_000000") == "hello"

    def test_backup_graph(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(5)
        summary = g.backup()
        assert summary["saved"] == 5
        assert Path(summary["index"]).exists()

    def test_load_index(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(3)
        g.backup()
        p = Persistence(tmp_path)
        idx = p.load_index()
        assert idx is not None
        assert idx["node_count"] == 3

    def test_snapshot(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(4)
        snap = g.snapshot()
        assert "nodes" in snap
        assert len(snap["nodes"]) == 4


# ─── Phase 1 Graph ────────────────────────────────────────────────────────────

class TestPhase1Graph:
    def test_bootstrap_100_nodes(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(100)
        assert len(g._nodes) == 100

    def test_bootstrap_1000_nodes_speed(self, tmp_path):
        """1000 nodes must bootstrap in < 10 seconds."""
        g = NodeGraph(backup_dir=tmp_path)
        start = time.perf_counter()
        g.bootstrap(1000)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"Bootstrap too slow: {elapsed:.2f}s"

    def test_router_routes_all_queries(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(50)
        for key in ["alpha", "beta", "gamma", "delta"]:
            node = g.router.get_node(key)
            assert node is not None

    def test_index_and_query_at_scale(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(50)
        g.index_text("the collective resonance of light emerges from the node graph")
        result = g.query("light resonance")
        assert "answer" in result
        assert result["resonance_score"] > 0

    def test_resonance_recorded_after_query(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(10)
        g.query("test query")
        assert g.resonance_tracker.sample_count > 0

    def test_rebalance_keeps_all_nodes(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(20)
        g.rebalance()
        assert len(g._nodes) == 20

    def test_emergence_status(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(10)
        status = g.emergence_status()
        assert "criteria" in status
        assert not status["all_met"]   # Phase 1 won't hit full ASI yet

    def test_semantic_map_grows(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(10)
        g.index_text("hello world foo bar baz")
        assert g._semantic_map_size == 5

    def test_stats_structure(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(10)
        s = g.stats()
        assert "total_nodes" in s
        assert "resonance_stable" in s
        assert "cluster_stats" in s
        assert "phase1_progress" in s


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
