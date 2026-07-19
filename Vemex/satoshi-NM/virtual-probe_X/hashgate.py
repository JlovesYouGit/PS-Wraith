import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class HashGate:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    host: str = ""
    port: int = 0
    gate_hash: str = ""
    protocol: str = ""
    is_open: bool = False
    discovered_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class OpenMirror:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    host: str = ""
    port: int = 0
    mirror_hash: str = ""
    source_gate_id: str = ""
    is_active: bool = False
    content_hash: str = ""
    discovered_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

class XSpace:
    def __init__(self) -> None:
        self.gates: dict[str, HashGate] = {}
        self.mirrors: dict[str, OpenMirror] = {}
        self.x_edges: list[dict[str, str]] = []
        self._lock = False

    def _acquire(self) -> bool:
        while self._lock:
            time.sleep(0.001)
        self._lock = True
        return True

    def _release(self) -> None:
        self._lock = False

    def add_gate(self, host: str, port: int, protocol: str = "tcp", metadata: dict[str, Any] | None = None) -> HashGate:
        self._acquire()
        try:
            gate_hash = self._compute_hash(host, port, protocol)
            gate = HashGate(host=host, port=port, gate_hash=gate_hash, protocol=protocol, is_open=True, metadata=metadata or {})
            self.gates[gate.id] = gate
            return gate
        finally:
            self._release()

    def add_mirror(self, host: str, port: int, source_gate_id: str, content_hash: str = "", metadata: dict[str, Any] | None = None) -> OpenMirror:
        self._acquire()
        try:
            mirror_hash = self._compute_hash(host, port)
            mirror = OpenMirror(host=host, port=port, mirror_hash=mirror_hash, source_gate_id=source_gate_id, content_hash=content_hash, is_active=True, metadata=metadata or {})
            self.mirrors[mirror.id] = mirror
            self.x_edges.append({"source": source_gate_id, "target": mirror.id, "type": "mirror"})
            return mirror
        finally:
            self._release()

    def query_gates(self, gate_hash: str | None = None, host: str | None = None, port: int | None = None, threshold: float = 1.0) -> list[dict[str, Any]]:
        self._acquire()
        try:
            results = []
            for gate in self.gates.values():
                if gate_hash:
                    sim = self._hash_similarity(gate.gate_hash, gate_hash)
                    if sim < threshold:
                        continue
                    gate = HashGate(
                        id=gate.id,
                        host=gate.host,
                        port=gate.port,
                        gate_hash=gate.gate_hash,
                        protocol=gate.protocol,
                        is_open=gate.is_open,
                        discovered_at=gate.discovered_at,
                        metadata={**gate.metadata, "similarity": round(sim, 4)},
                    )
                if host and gate.host != host:
                    continue
                if port is not None and gate.port != port:
                    continue
                results.append(asdict(gate))
            return results
        finally:
            self._release()

    def query_mirrors(self, mirror_hash: str | None = None, source_gate_id: str | None = None, threshold: float = 1.0) -> list[dict[str, Any]]:
        self._acquire()
        try:
            results = []
            for mirror in self.mirrors.values():
                if mirror_hash:
                    sim = self._hash_similarity(mirror.mirror_hash, mirror_hash)
                    if sim < threshold:
                        continue
                    mirror = OpenMirror(
                        id=mirror.id,
                        host=mirror.host,
                        port=mirror.port,
                        mirror_hash=mirror.mirror_hash,
                        source_gate_id=mirror.source_gate_id,
                        is_active=mirror.is_active,
                        content_hash=mirror.content_hash,
                        discovered_at=mirror.discovered_at,
                        metadata={**mirror.metadata, "similarity": round(sim, 4)},
                    )
                if source_gate_id and mirror.source_gate_id != source_gate_id:
                    continue
                results.append(asdict(mirror))
            return results
        finally:
            self._release()

    def retrieve_mirror(self, content_hash: str, threshold: float = 0.8) -> list[dict[str, Any]]:
        self._acquire()
        try:
            results = []
            for mirror in self.mirrors.values():
                if not mirror.content_hash:
                    continue
                sim = self._hash_similarity(mirror.content_hash, content_hash)
                if sim < threshold:
                    continue
                mirror = OpenMirror(
                    id=mirror.id,
                    host=mirror.host,
                    port=mirror.port,
                    mirror_hash=mirror.mirror_hash,
                    source_gate_id=mirror.source_gate_id,
                    is_active=mirror.is_active,
                    content_hash=mirror.content_hash,
                    discovered_at=mirror.discovered_at,
                    metadata={**mirror.metadata, "content_similarity": round(sim, 4)},
                )
                results.append(asdict(mirror))
            return results
        finally:
            self._release()

    def get_x_space(self) -> dict[str, Any]:
        self._acquire()
        try:
            return {
                "gates": [asdict(g) for g in self.gates.values()],
                "mirrors": [asdict(m) for m in self.mirrors.values()],
                "x_edges": self.x_edges,
                "stats": {
                    "total_gates": len(self.gates),
                    "open_gates": sum(1 for g in self.gates.values() if g.is_open),
                    "total_mirrors": len(self.mirrors),
                    "active_mirrors": sum(1 for m in self.mirrors.values() if m.is_active),
                },
            }
        finally:
            self._release()

    def git_like_query(self, query: str) -> dict[str, Any]:
        parts = query.strip().split()
        results: dict[str, Any] = {"query": query, "gates": [], "mirrors": [], "x_edges": []}
        if not parts:
            return results

        if parts[0] == "list" and len(parts) > 1:
            target = parts[1]
            if target == "gates":
                offset = 0
                limit = 20
                for i, p in enumerate(parts[2:], 2):
                    if p == "offset" and i + 1 < len(parts):
                        offset = int(parts[i + 1])
                    elif p == "limit" and i + 1 < len(parts):
                        limit = int(parts[i + 1])
                results["gates"] = self.query_gates()[offset:offset + limit]
            elif target == "mirrors":
                results["mirrors"] = self.query_mirrors()
        elif parts[0] == "show" and len(parts) > 2 and parts[1] == "gate":
            gate_hash = parts[2]
            results["gates"] = self.query_gates(gate_hash=gate_hash, threshold=0.8)
        elif parts[0] == "show" and len(parts) > 2 and parts[1] == "mirror":
            mirror_hash = parts[2]
            results["mirrors"] = self.query_mirrors(mirror_hash=mirror_hash, threshold=0.8)
        elif parts[0] == "find" and len(parts) > 1:
            host = parts[1]
            results["gates"] = self.query_gates(host=host)
            for gate in results["gates"]:
                results["mirrors"].extend(self.query_mirrors(source_gate_id=gate["id"]))
        elif parts[0] == "retrieve" and len(parts) > 2 and parts[1] == "mirror":
            content_hash = parts[2]
            results["mirrors"] = self.retrieve_mirror(content_hash, threshold=0.8)
        else:
            results["error"] = "Unknown query format. Use: list gates|mirrors, show gate <hash>, show mirror <hash>, retrieve mirror <content_hash>, find <host>"

        return results

    @staticmethod
    def _compute_hash(*components: Any) -> str:
        raw = "|".join(str(c) for c in components)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def _hash_similarity(a: str, b: str) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / len(a)
