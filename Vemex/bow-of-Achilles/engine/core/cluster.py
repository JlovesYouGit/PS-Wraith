"""
cluster.py — Light-ASI LLM Gateway Phase 1
IP-tier based node clustering for hierarchical routing and sync.

Nodes are grouped by their virtual_ip_tier (10, 100, 1k … 1B).
Each cluster handles its own local sync and exposes an aggregate
resonance score.

Ruleset reference: LLM_GATEWAY_RULESET.md § 2 (NODE_IP_TIERS),
                   § 3 (node_cluster_sync: 1000ms, node_local_sync: 1100ms)
"""

import logging
from collections import defaultdict
from typing import Optional

from engine.core.constants import NODE_IP_TIERS, RESONANCE_BASE
from engine.core.timing import enforce_sla

logger = logging.getLogger("light-asi.cluster")


class NodeCluster:
    """A group of nodes sharing the same IP tier."""

    def __init__(self, tier: int):
        self.tier = tier
        self._nodes: list = []  # list of Node objects

    def add(self, node) -> None:
        self._nodes.append(node)

    def remove(self, node_id: int) -> None:
        self._nodes = [n for n in self._nodes if n.meta.node_id != node_id]

    @property
    def size(self) -> int:
        return len(self._nodes)

    @enforce_sla("node_cluster_sync")
    def sync(self) -> dict:
        """
        Cluster-level sync: rewire internal conjunctions in circular order.
        Returns sync summary.
        """
        n = len(self._nodes)
        for i, node in enumerate(self._nodes):
            next_node = self._nodes[(i + 1) % n] if n > 1 else node
            node.set_conjunction(
                count=n,
                sequence=f"cluster_{self.tier}_seq_{i}→{(i+1)%n}",
                next_id=next_node.meta.node_id,
            )
        logger.debug(f"Cluster[tier={self.tier}] synced {n} nodes.")
        return {"tier": self.tier, "synced_nodes": n}

    @property
    def resonance(self) -> float:
        """Mean resonance weight across all nodes in this cluster."""
        if not self._nodes:
            return 0.0
        total = sum(n.meta.resonance_weight for n in self._nodes)
        return total / (RESONANCE_BASE * len(self._nodes))

    def top_nodes(self, k: int = 5) -> list:
        """Return top-k nodes by resonance weight."""
        return sorted(self._nodes, key=lambda n: n.meta.resonance_weight, reverse=True)[:k]

    def __repr__(self) -> str:
        return f"NodeCluster(tier={self.tier}, nodes={self.size}, resonance={self.resonance:.8f})"


class ClusterManager:
    """
    Manages all IP-tier clusters and provides cross-cluster operations.
    """

    def __init__(self):
        self._clusters: dict[int, NodeCluster] = {
            tier: NodeCluster(tier) for tier in NODE_IP_TIERS
        }

    def assign(self, node) -> None:
        """Assign a node to its tier cluster."""
        tier = node.meta.virtual_ip_tier
        if tier not in self._clusters:
            self._clusters[tier] = NodeCluster(tier)
        self._clusters[tier].add(node)

    def remove(self, node) -> None:
        tier = node.meta.virtual_ip_tier
        if tier in self._clusters:
            self._clusters[tier].remove(node.meta.node_id)

    def get_cluster(self, tier: int) -> Optional[NodeCluster]:
        return self._clusters.get(tier)

    def sync_all(self) -> list[dict]:
        """Sync every cluster. Returns list of sync summaries."""
        results = []
        for cluster in self._clusters.values():
            if cluster.size > 0:
                results.append(cluster.sync())
        logger.info(f"ClusterManager: synced {len(results)} active clusters.")
        return results

    @enforce_sla("node_local_sync")
    def local_sync(self, tier: int) -> Optional[dict]:
        """Sync a single tier cluster."""
        cluster = self._clusters.get(tier)
        if cluster and cluster.size > 0:
            return cluster.sync()
        return None

    def aggregate_resonance(self) -> float:
        """Weighted mean resonance across all active clusters."""
        active = [c for c in self._clusters.values() if c.size > 0]
        if not active:
            return 0.0
        weighted = sum(c.resonance * c.size for c in active)
        total_nodes = sum(c.size for c in active)
        return weighted / total_nodes if total_nodes else 0.0

    def stats(self) -> dict:
        return {
            tier: {"nodes": c.size, "resonance": round(c.resonance, 10)}
            for tier, c in self._clusters.items()
            if c.size > 0
        }

    def __repr__(self) -> str:
        active = sum(1 for c in self._clusters.values() if c.size > 0)
        return f"ClusterManager(active_tiers={active}, total_clusters={len(self._clusters)})"
