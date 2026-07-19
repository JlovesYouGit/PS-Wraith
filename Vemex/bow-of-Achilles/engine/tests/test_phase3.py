"""
test_phase3.py — Light-ASI Phase 3 Tests
API server, middleware, handlers — all tested via real HTTP against a live server.
"""

import sys, os, json, time, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from engine.core.graph import NodeGraph
from engine.auth.auth import AuthManager
from engine.world.ingester import WorldIngester
from engine.api.server import APIServer
from engine.api.middleware import extract_bearer, authenticate_request


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    """Shared engine for all Phase 3 tests."""
    graph = NodeGraph()
    graph.bootstrap(10)
    auth = AuthManager()
    admin = auth.create_user("admin", "admin")
    dev   = auth.create_user("dev1", "developer")
    user  = auth.create_user("user1", "user")
    guest = auth.create_user("guest1", "guest")
    ingester = WorldIngester(graph.semantic_map, graph, interval=300)
    return graph, auth, ingester, admin, dev, user, guest


@pytest.fixture(scope="module")
def server(engine):
    """Start API server on a random-ish port for testing."""
    graph, auth, ingester, *_ = engine
    port = 18321
    srv = APIServer(graph=graph, auth=auth, ingester=ingester,
                    host="127.0.0.1", port=port)
    srv.start_background()
    time.sleep(0.3)  # let server bind
    yield srv
    srv.stop()


def _url(server, path):
    return f"{server.base_url}{path}"


def _get(server, path, token=None):
    req = Request(_url(server, path))
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())


def _post(server, path, body=None, token=None):
    data = json.dumps(body or {}).encode()
    req = Request(_url(server, path), data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())


# ─── Middleware Unit Tests ────────────────────────────────────────────────────

class TestMiddleware:
    def test_extract_bearer_valid(self):
        assert extract_bearer("Bearer abc123") == "abc123"

    def test_extract_bearer_missing(self):
        assert extract_bearer("") is None
        assert extract_bearer("Basic xyz") is None

    def test_authenticate_valid(self, engine):
        _, auth, _, admin, *_ = engine
        user, err = authenticate_request(
            {"Authorization": f"Bearer {admin.token}"}, auth
        )
        assert user is not None
        assert user.username == "admin"
        assert err == ""

    def test_authenticate_bad_token(self, engine):
        _, auth, *_ = engine
        user, err = authenticate_request(
            {"Authorization": "Bearer invalid_token_xyz"}, auth
        )
        assert user is None
        assert "Invalid" in err

    def test_authenticate_missing_header(self, engine):
        _, auth, *_ = engine
        user, err = authenticate_request({}, auth)
        assert user is None
        assert "Missing" in err


# ─── Health (no auth) ─────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_no_auth(self, server):
        status, body = _get(server, "/health")
        assert status == 200
        assert body["status"] == "ok"
        assert "nodes" in body
        assert "timestamp" in body


# ─── Auth Endpoints ──────────────────────────────────────────────────────────

class TestAuthEndpoints:
    def test_create_token(self, server):
        status, body = _post(server, "/auth/token",
                             {"username": "api_test_user", "role": "guest"})
        assert status == 201
        assert "token" in body
        assert body["role"] == "guest"

    def test_create_duplicate_user(self, server):
        _post(server, "/auth/token", {"username": "dupe_test", "role": "guest"})
        status, body = _post(server, "/auth/token",
                             {"username": "dupe_test", "role": "guest"})
        assert status == 409

    def test_create_missing_username(self, server):
        status, body = _post(server, "/auth/token", {"role": "guest"})
        assert status == 400

    def test_list_users_admin(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _get(server, "/auth/users", token=admin.token)
        assert status == 200
        assert "users" in body

    def test_list_users_no_auth(self, server):
        status, _ = _get(server, "/auth/users")
        assert status == 401


# ─── Query Endpoint ──────────────────────────────────────────────────────────

class TestQueryEndpoint:
    def test_query_requires_auth(self, server):
        status, _ = _post(server, "/query", {"text": "hello"})
        assert status == 401

    def test_query_success(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _post(server, "/query",
                             {"text": "neural networks"},
                             token=admin.token)
        assert status == 200
        assert "answer" in body
        assert "resonance_score" in body
        assert "source_nodes" in body
        assert "entropy_delta" in body
        assert "timestamp" in body

    def test_query_empty_text(self, server, engine):
        _, _, _, admin, *_ = engine
        status, _ = _post(server, "/query", {"text": ""}, token=admin.token)
        assert status == 400


# ─── Index Endpoint ──────────────────────────────────────────────────────────

class TestIndexEndpoint:
    def test_index_text(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _post(server, "/index",
                             {"text": "the light emerges from resonance"},
                             token=admin.token)
        assert status == 200
        assert body["indexed_tokens"] == 5

    def test_index_no_auth(self, server):
        status, _ = _post(server, "/index", {"text": "test"})
        assert status == 401


# ─── Search Endpoint ─────────────────────────────────────────────────────────

class TestSearchEndpoint:
    def test_search_empty_map(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _post(server, "/search",
                             {"text": "nonexistent_gibberish_xyz"},
                             token=admin.token)
        assert status == 200
        assert body["count"] == 0


# ─── Stats / Emerge / Resonance / World ──────────────────────────────────────

class TestInfoEndpoints:
    def test_stats(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _get(server, "/stats", token=admin.token)
        assert status == 200
        assert "total_nodes" in body
        assert "world_net" in body

    def test_emerge(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _get(server, "/emerge", token=admin.token)
        assert status == 200
        assert "criteria" in body

    def test_resonance(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _get(server, "/resonance", token=admin.token)
        assert status == 200
        assert "mean" in body

    def test_world(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _get(server, "/world", token=admin.token)
        assert status == 200
        assert "semantic_map_size" in body


# ─── Backup Endpoint ─────────────────────────────────────────────────────────

class TestBackupEndpoint:
    def test_backup_admin_only(self, server, engine):
        _, _, _, _, dev, user, guest = engine
        status, _ = _post(server, "/backup", {}, token=user.token)
        assert status == 403

    def test_backup_admin(self, server, engine):
        _, _, _, admin, *_ = engine
        status, body = _post(server, "/backup", {}, token=admin.token)
        assert status == 200
        assert "saved" in body


# ─── 404 ──────────────────────────────────────────────────────────────────────

class TestNotFound:
    def test_unknown_route(self, server):
        status, body = _get(server, "/nonexistent")
        assert status == 404
        assert "error" in body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
