import hashlib
import json
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Node:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    label: str = ""
    vector: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    connections: list[str] = field(default_factory=list)
    importance: float = 0.5
    phase: int = 0


class NodeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.adjacency: dict[str, set[str]] = {}
        self.semantic_index: dict[str, str] = {}
        self._lock = False

    def _acquire(self) -> bool:
        while self._lock:
            time.sleep(0.001)
        self._lock = True
        return True

    def _release(self) -> None:
        self._lock = False

    def add_node(self, label: str, metadata: dict[str, Any] | None = None) -> Node:
        self._acquire()
        try:
            node = Node(label=label, metadata=metadata or {})
            self.nodes[node.id] = node
            self.adjacency[node.id] = set()
            self._update_index()
            return node
        finally:
            self._release()

    def connect(self, source_id: str, target_id: str) -> bool:
        self._acquire()
        try:
            if source_id not in self.nodes or target_id not in self.nodes:
                return False
            self.adjacency[source_id].add(target_id)
            self.adjacency[target_id].add(source_id)
            self.nodes[source_id].connections.append(target_id)
            self.nodes[target_id].connections.append(source_id)
            self.nodes[source_id].updated_at = time.time()
            self.nodes[target_id].updated_at = time.time()
            return True
        finally:
            self._release()

    def index_text(self, text: str) -> Node:
        self._acquire()
        try:
            tokens = self._tokenize(text)
            vector = self._embed(tokens)
            node = Node(label=text[:64], vector=vector, metadata={"text": text, "tokens": tokens})
            self.nodes[node.id] = node
            self.adjacency[node.id] = set()
            for token in tokens:
                key = self._hash_token(token)
                if key not in self.semantic_index:
                    self.semantic_index[key] = node.id
                else:
                    existing = self.semantic_index[key]
                    if existing in self.nodes:
                        self.connect(existing, node.id)
            return node
        finally:
            self._release()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        self._acquire()
        try:
            tokens = self._tokenize(query)
            query_vec = self._embed(tokens)
            scores: list[tuple[float, Node]] = []
            for node in self.nodes.values():
                if not node.vector:
                    continue
                score = self._cosine_similarity(query_vec, node.vector)
                scores.append((score, node))
            scores.sort(key=lambda x: x[0], reverse=True)
            results = []
            for score, node in scores[:top_k]:
                results.append({
                    "id": node.id,
                    "label": node.label,
                    "score": round(score, 4),
                    "metadata": node.metadata,
                    "phase": node.phase,
                })
            return results
        finally:
            self._release()

    def get_stats(self) -> dict[str, Any]:
        self._acquire()
        try:
            total_connections = sum(len(v) for v in self.adjacency.values()) // 2
            phases = {}
            for node in self.nodes.values():
                phases[node.phase] = phases.get(node.phase, 0) + 1
            return {
                "total_nodes": len(self.nodes),
                "total_connections": total_connections,
                "semantic_index_size": len(self.semantic_index),
                "phases": phases,
                "avg_importance": round(sum(n.importance for n in self.nodes.values()) / max(1, len(self.nodes)), 3),
            }
        finally:
            self._release()

    def emerge_status(self) -> dict[str, Any]:
        stats = self.get_stats()
        phase_nodes = stats.get("phases", {})
        return {
            "phase_0_bootstrap": phase_nodes.get(0, 0) > 0,
            "phase_1_propagation": phase_nodes.get(1, 0) > 0,
            "phase_2_consolidation": phase_nodes.get(2, 0) > 0,
            "total_nodes": stats["total_nodes"],
            "graph_density": round(stats["total_connections"] / max(1, stats["total_nodes"]), 4),
        }

    def bootstrap(self, count: int = 10) -> list[Node]:
        concepts = [
            "consciousness", "semantic web", "distributed systems", "knowledge graph",
            "neural pathway", "semantic memory", "world net", "reasoning engine",
            "latent space", "information retrieval", "cognitive map", "signal processing",
            "emergence", "complex systems", "data fusion", "pattern recognition",
        ]
        created: list[Node] = []
        for _ in range(count):
            label = random.choice(concepts)
            node = self.add_node(label=label)
            created.append(node)
        for i in range(len(created) - 1):
            self.connect(created[i].id, created[i + 1].id)
        return created

    def _update_index(self) -> None:
        self.semantic_index.clear()
        for node in self.nodes.values():
            text = node.label + " " + json.dumps(node.metadata)
            tokens = self._tokenize(text)
            for token in tokens:
                key = self._hash_token(token)
                if key not in self.semantic_index:
                    self.semantic_index[key] = node.id

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        text = text.lower()
        tokens = []
        current = ""
        for ch in text:
            if ch.isalnum():
                current += ch
            else:
                if current:
                    tokens.append(current)
                    current = ""
        if current:
            tokens.append(current)
        return tokens

    @staticmethod
    def _embed(tokens: list[str]) -> list[float]:
        vec = [0.0] * 64
        for token in tokens:
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            for i in range(64):
                if (h >> i) & 1:
                    vec[i] += 1.0
        mag = sum(v * v for v in vec) ** 0.5
        if mag > 0:
            vec = [v / mag for v in vec]
        return vec

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(y * y for y in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.md5(token.encode()).hexdigest()[:12]
