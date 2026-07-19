"""
router.py — Light-ASI LLM Gateway Phase 1
O(1) hash-based node routing via consistent hashing ring.

Instead of scanning all nodes on every query, we maintain a sorted ring of
virtual node points. A sequence hash maps directly to the correct node in
O(log N) via bisect — effectively O(1) for practical purposes at 10k nodes.

Ruleset reference: LLM_GATEWAY_RULESET.md § 2.1, § 4.2
"""

import bisect
import hashlib
import logging
from typing import Optional

logger = logging.getLogger("light-asi.router")

# Number of virtual points per node on the ring (improves distribution)
VIRTUAL_POINTS_PER_NODE = 150


class ConsistentHashRouter:
    """
    Consistent hashing ring for O(log N) node routing.
    Each node occupies VIRTUAL_POINTS_PER_NODE positions on a 2^32 ring.
    """

    def __init__(self):
        self._ring: list[int] = []               # sorted ring positions
        self._ring_map: dict[int, int] = {}      # ring_pos → node_id
        self._nodes: dict[int, object] = {}      # node_id → Node

    def add_node(self, node: object) -> None:
        """Add a node and its virtual points to the ring."""
        node_id = node.meta.node_id
        self._nodes[node_id] = node
        for i in range(VIRTUAL_POINTS_PER_NODE):
            key = self._hash_key(f"{node_id}:{i}")
            bisect.insort(self._ring, key)
            self._ring_map[key] = node_id
        logger.debug(f"Router: added node {node_id} ({VIRTUAL_POINTS_PER_NODE} vpoints)")

    def remove_node(self, node_id: int) -> None:
        """Remove a node and clean up its ring positions."""
        if node_id not in self._nodes:
            return
        del self._nodes[node_id]
        to_remove = [pos for pos, nid in self._ring_map.items() if nid == node_id]
        for pos in to_remove:
            del self._ring_map[pos]
            idx = bisect.bisect_left(self._ring, pos)
            if idx < len(self._ring) and self._ring[idx] == pos:
                self._ring.pop(idx)
        logger.debug(f"Router: removed node {node_id}")

    def get_node(self, key: str) -> Optional[object]:
        """
        Route a string key to its responsible node in O(log N).
        Returns the Node object or None if the ring is empty.
        """
        if not self._ring:
            return None
        h = self._hash_key(key)
        idx = bisect.bisect_right(self._ring, h) % len(self._ring)
        node_id = self._ring_map[self._ring[idx]]
        return self._nodes.get(node_id)

    def get_n_nodes(self, key: str, n: int) -> list[object]:
        """
        Return up to n distinct nodes responsible for a key (for replication).
        Walks the ring clockwise from the key's position.
        """
        if not self._ring or n == 0:
            return []
        h = self._hash_key(key)
        start_idx = bisect.bisect_right(self._ring, h) % len(self._ring)

        seen_ids: set[int] = set()
        result: list[object] = []
        for i in range(len(self._ring)):
            pos = self._ring[(start_idx + i) % len(self._ring)]
            node_id = self._ring_map[pos]
            if node_id not in seen_ids:
                seen_ids.add(node_id)
                node = self._nodes.get(node_id)
                if node:
                    result.append(node)
                if len(result) == n:
                    break
        return result

    @staticmethod
    def _hash_key(key: str) -> int:
        """Map any string to a 32-bit ring position."""
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def ring_size(self) -> int:
        return len(self._ring)

    def __repr__(self) -> str:
        return f"ConsistentHashRouter(nodes={self.node_count}, ring_points={self.ring_size})"
