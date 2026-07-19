"""
test_phase0.py — Light-ASI Phase 0 Smoke Tests
Verifies node creation, hash pipeline, graph ops, and auth.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import time
import math
import pytest

from engine.core.constants import RANGE_MIN, RANGE_MAX, RESONANCE_BASE, SEQUENCE_TARGET
from engine.core.node import Node, NodeStore
from engine.core.hash_pipeline import (
    project_to_alphabet_space, build_sequence_hash,
    query_entropy, coherence_score, dehash_and_validate,
)
from engine.core.graph import NodeGraph
from engine.auth.auth import AuthManager


# ─── Constants ────────────────────────────────────────────────────────────────

def test_range_bounds():
    assert RANGE_MIN == -16
    assert RANGE_MAX == 10_000

def test_resonance_base():
    assert RESONANCE_BASE == 5 ** 15


# ─── Node Creation ────────────────────────────────────────────────────────────

def test_node_create():
    node = Node.create(0)
    assert RANGE_MIN <= node.meta.node_id <= RANGE_MAX
    assert node.meta.virtual_ip_tier in [10, 100, 1_000, 10_000, 100_000,
                                          1_000_000, 10_000_000, 100_000_000, 1_000_000_000]
    assert node.meta.resonance_weight > 0

def test_node_ids_are_deterministic():
    a = Node.create(42)
    b = Node.create(42)
    assert a.meta.node_id == b.meta.node_id
    assert a.meta.hash_hex == b.meta.hash_hex

def test_node_ids_differ_by_position():
    nodes = [Node.create(i) for i in range(10)]
    ids = [n.meta.node_id for n in nodes]
    # Not all identical (hash collision on 10 samples is astronomically unlikely)
    assert len(set(ids)) > 1


# ─── Node Store ───────────────────────────────────────────────────────────────

def test_node_store_write_read():
    store = NodeStore(node_id=1)
    store.write("seq_abc", "tok_000001", "hello")
    assert store.read("seq_abc", "tok_000001") == "hello"

def test_node_store_dehash_order():
    store = NodeStore(node_id=2)
    store.write("seq_xyz", "tok_000002", "world")
    store.write("seq_xyz", "tok_000001", "hello")
    tokens = store.dehash("seq_xyz")
    assert tokens[0] == "hello"   # sorted by key
    assert tokens[1] == "world"

def test_node_store_overflow():
    store = NodeStore(node_id=3)
    result = store.safe_sequence(SEQUENCE_TARGET + 500)
    assert result == (SEQUENCE_TARGET + 500) % 1000
    assert len(store._overflow_log) == 1

def test_node_store_no_overflow():
    store = NodeStore(node_id=4)
    result = store.safe_sequence(500)
    assert result == 500
    assert len(store._overflow_log) == 0

def test_node_store_fraction_read():
    store = NodeStore(node_id=5)
    for i in range(10):
        store.write("seq_fr", f"tok_{i:06d}", f"word_{i}")
    val = store.fraction_read("seq_fr", "float_seek")  # 1/32 ≈ position 0
    assert val is not None


# ─── Hash Pipeline ────────────────────────────────────────────────────────────

def test_alphabet_projection_in_range():
    v = project_to_alphabet_space("hello world")
    assert 0 <= v < 2 ** 256

def test_alphabet_projection_deterministic():
    assert project_to_alphabet_space("test") == project_to_alphabet_space("test")

def test_sequence_hash_format():
    h = build_sequence_hash("hello", node_id=42)
    assert isinstance(h, str)
    assert len(h) == 64   # blake2b 32-byte hex

def test_query_entropy_empty():
    assert query_entropy("") == 0.0

def test_query_entropy_uniform():
    e = query_entropy("aaaa")
    assert e == 0.0   # zero entropy — all same char

def test_query_entropy_nonzero():
    e = query_entropy("hello world")
    assert e > 0

def test_coherence_empty():
    assert coherence_score([]) == 0.0

def test_coherence_full():
    assert coherence_score(["a", "b", "c"]) == 1.0


# ─── Node State Flop ──────────────────────────────────────────────────────────

def test_state_flop_returns_0_or_1():
    node = Node.create(0)
    for _ in range(20):
        flop = node.state_flop(query_entropy("test query"), 100)
        assert flop in (0, 1)


# ─── Graph ────────────────────────────────────────────────────────────────────

def test_graph_bootstrap():
    g = NodeGraph()
    g.bootstrap(5)
    assert len(g._nodes) == 5

def test_graph_circular_conjunctions():
    g = NodeGraph()
    g.bootstrap(3)
    # last node's next should be the first node
    last = g._nodes[-1]
    first = g._nodes[0]
    assert last.conjunction[2] == first.meta.node_id

def test_graph_index_and_query():
    g = NodeGraph()
    g.bootstrap(5)
    g.index_text("the light emerges from collective resonance")
    result = g.query("light resonance")
    assert "answer" in result
    assert "resonance_score" in result
    assert isinstance(result["source_nodes"], list)

def test_graph_resonance_positive():
    g = NodeGraph()
    g.bootstrap(3)
    assert g.collective_resonance() > 0

def test_graph_stats():
    g = NodeGraph()
    g.bootstrap(4)
    s = g.stats()
    assert s["total_nodes"] == 4


# ─── Auth ─────────────────────────────────────────────────────────────────────

def test_auth_create_user():
    am = AuthManager()
    u = am.create_user("alice", "user")
    assert u.username == "alice"
    assert u.role == "user"
    assert len(u.token) == 64

def test_auth_authenticate_valid():
    am = AuthManager()
    u = am.create_user("bob", "developer")
    authenticated = am.authenticate(u.token)
    assert authenticated is not None
    assert authenticated.username == "bob"

def test_auth_authenticate_bad_token():
    am = AuthManager()
    assert am.authenticate("bad_token_xyz") is None

def test_auth_invalid_role():
    am = AuthManager()
    with pytest.raises(ValueError):
        am.create_user("eve", "superuser")

def test_auth_duplicate_user():
    am = AuthManager()
    am.create_user("carol", "guest")
    with pytest.raises(ValueError):
        am.create_user("carol", "guest")

def test_auth_rate_guest():
    am = AuthManager()
    u = am.create_user("guest1", "guest")
    # 10 req/min limit — first 10 should pass
    for _ in range(10):
        assert am.check_rate(u)
    # 11th should fail
    assert not am.check_rate(u)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
