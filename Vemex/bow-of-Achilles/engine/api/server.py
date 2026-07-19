"""
server.py — Light-ASI LLM Gateway Phase 3
HTTP API server using stdlib http.server only — no external dependencies.

Endpoints:
  GET  /health            — liveness check (no auth)
  POST /auth/token        — create user + get Bearer token
  GET  /auth/users        — list users (admin/dev)
  POST /query             — query node graph (auth required)
  POST /index             — index text (auth required)
  POST /search            — search semantic map (auth required)
  POST /ingest            — trigger world-net cycle (admin/dev)
  GET  /stats             — graph statistics (auth required)
  GET  /emerge            — ASI emergence checklist (auth required)
  GET  /resonance         — resonance report (auth required)
  GET  /world             — world-net status (auth required)
  POST /backup            — disk backup (admin only)

Ruleset reference: LLM_GATEWAY_RULESET.md § 6.2-6.3, § 7
"""

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import urlparse

from engine.api.middleware import authenticate_request
from engine.api.handlers import (
    handle_health, handle_create_token, handle_list_users,
    handle_query, handle_index, handle_search, handle_ingest,
    handle_stats, handle_emerge, handle_resonance, handle_world,
    handle_backup,
    handle_mana_status, handle_mana_start_intake, handle_mana_stop_intake,
    handle_mana_wallet, handle_mana_wallet_generate, handle_mana_formula,
    handle_mana_connections, handle_mana_send, handle_mana_narrative,
)
from engine.auth.auth import AuthManager
from engine.core.graph import NodeGraph

logger = logging.getLogger("light-asi.api.server")

# ─── Route table ──────────────────────────────────────────────────────────────
# (method, path) → (handler_fn, requires_auth)
ROUTES: dict[tuple[str, str], tuple] = {
    ("GET",  "/health"):      (handle_health,       False),
    ("POST", "/auth/token"):  (handle_create_token, False),
    ("GET",  "/auth/users"):  (handle_list_users,   True),
    ("POST", "/query"):       (handle_query,         True),
    ("POST", "/index"):       (handle_index,         True),
    ("POST", "/search"):      (handle_search,        True),
    ("POST", "/ingest"):      (handle_ingest,        True),
    ("GET",  "/stats"):       (handle_stats,         True),
    ("GET",  "/emerge"):      (handle_emerge,        True),
    ("GET",  "/resonance"):   (handle_resonance,     True),
    ("GET",  "/world"):       (handle_world,         True),
    ("POST", "/backup"):      (handle_backup,            True),
    ("GET",  "/mana/status"): (handle_mana_status,       True),
    ("POST", "/mana/start"):  (handle_mana_start_intake, True),
    ("POST", "/mana/stop"):   (handle_mana_stop_intake,  True),
    ("GET",  "/mana/wallet"): (handle_mana_wallet,       True),
    ("POST", "/mana/wallet/generate"): (handle_mana_wallet_generate, True),
    ("POST", "/mana/formula"): (handle_mana_formula,    True),
    ("GET",  "/mana/connections"): (handle_mana_connections, True),
    ("POST", "/mana/send"):   (handle_mana_send,         True),
    ("POST", "/mana/narrate"): (handle_mana_narrative,   True),
}

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
}


# ─── Request Handler ──────────────────────────────────────────────────────────

def _make_handler(graph: NodeGraph, auth: AuthManager, ingester):
    """Factory to inject dependencies into the handler class."""

    class LightASIHandler(BaseHTTPRequestHandler):
        log_message = lambda self, fmt, *args: logger.debug(fmt % args)

        # ── Routing ────────────────────────────────────────────────────────

        def _route(self, method: str):
            path = urlparse(self.path).path.rstrip("/") or "/"
            route_key = (method, path)
            entry = ROUTES.get(route_key)

            if not entry:
                self._send(404, {"error": f"No route: {method} {path}"})
                return

            handler_fn, requires_auth = entry
            user = None

            # Auth gate
            if requires_auth:
                user, err = authenticate_request(dict(self.headers), auth)
                if not user:
                    self._send(401, {"error": err})
                    return

            # Parse body for POST
            body = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0))
                if length:
                    try:
                        body = json.loads(self.rfile.read(length))
                    except json.JSONDecodeError:
                        self._send(400, {"error": "Invalid JSON body"})
                        return

            # Call handler
            try:
                status, response = handler_fn(body, user, graph, auth, ingester)
                self._send(status, response)
            except Exception as e:
                logger.error(f"Handler error [{route_key}]: {e}", exc_info=True)
                self._send(500, {"error": "Internal server error", "detail": str(e)})

        # ── HTTP verbs ─────────────────────────────────────────────────────

        def do_GET(self):    self._route("GET")
        def do_POST(self):   self._route("POST")

        def do_OPTIONS(self):
            """CORS preflight."""
            self.send_response(204)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()

        # ── Response helper ────────────────────────────────────────────────

        def _send(self, status: int, data: dict):
            body = json.dumps(data, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

    return LightASIHandler


# ─── Server class ─────────────────────────────────────────────────────────────

class APIServer:
    """
    Wraps HTTPServer with lifecycle management and background thread support.
    """

    def __init__(
        self,
        graph: NodeGraph,
        auth: AuthManager,
        ingester=None,
        host: str = "0.0.0.0",
        port: int = 8000,
    ):
        self.host     = host
        self.port     = port
        self.graph    = graph
        self.auth     = auth
        self.ingester = ingester
        handler_class = _make_handler(graph, auth, ingester)
        self._server  = HTTPServer((host, port), handler_class)
        self._thread: Optional[threading.Thread] = None

    def start_background(self) -> None:
        """Run the server in a daemon thread (non-blocking)."""
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="api-server",
            daemon=True,
        )
        self._thread.start()
        logger.info(f"API server running on http://{self.host}:{self.port}")

    def serve_forever(self) -> None:
        """Run the server in the foreground (blocking)."""
        logger.info(f"API server running on http://{self.host}:{self.port}")
        self._server.serve_forever()

    def stop(self) -> None:
        self._server.shutdown()
        logger.info("API server stopped.")

    @property
    def base_url(self) -> str:
        host = "localhost" if self.host == "0.0.0.0" else self.host
        return f"http://{host}:{self.port}"
