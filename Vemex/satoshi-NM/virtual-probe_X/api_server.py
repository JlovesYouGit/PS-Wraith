import os
import json
import secrets
import time
from dataclasses import asdict
from typing import Any

from node_graph import NodeGraph
from ping_manager import PingManager
from hashgate import XSpace
from chainnet import validate_p2pkh_address, check_balance, cast_to_xpub, complete_cast
from seednet import scan_dir, detect_threats, summary, Seed, Threat


class AuthManager:
    def __init__(self) -> None:
        self.tokens: dict[str, dict[str, Any]] = {}
        self.admin_token = secrets.token_urlsafe(32)

    def login(self, password: str | None = None) -> str:
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "created_at": time.time(),
            "role": "admin" if (password or os.environ.get("ADMIN_PASSWORD")) == "admin" else "user",
        }
        return token

    def admin_login(self) -> str:
        return self.admin_token

    def validate(self, token: str | None) -> dict[str, Any]:
        if not token:
            return {"valid": False, "role": None}
        if token == self.admin_token:
            return {"valid": True, "role": "admin"}
        if token in self.tokens:
            return {"valid": True, "role": self.tokens[token]["role"]}
        return {"valid": False, "role": None}


class APIServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.graph = NodeGraph()
        self.pings = PingManager(self.graph)
        self.xspace = XSpace()
        self.auth = AuthManager()
        self.graph.bootstrap()
        self.seeds: list[Seed] = []
        self.threats: list[Threat] = []
        self.start_time = time.time()

    def handle_request(self, method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, str, str]:
        auth_header = headers.get("authorization", "")
        token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else None

        if path == "/auth/token" and method == "POST":
            token_resp = self.auth.login()
            body_data = json.loads(body.decode()) if body else {}
            pw = body_data.get("password")
            if pw == "admin":
                token_resp = self.auth.admin_login()
            return 200, "application/json", json.dumps({"token": token_resp, "role": "admin" if pw == "admin" else "user"})

        if path == "/health" and method == "GET":
            return 200, "application/json", json.dumps({"status": "ok", "uptime": round(time.time() - self.start_time, 2)})

        if path == "/stats" and method == "GET":
            return 200, "application/json", json.dumps(self.graph.get_stats())

        if path == "/emerge" and method == "GET":
            return 200, "application/json", json.dumps(self.graph.emerge_status())

        if method == "POST" and path == "/query":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            query = body_data.get("query", "")
            top_k = int(body_data.get("top_k", 5))
            results = self.graph.search(query, top_k=top_k)
            return 200, "application/json", json.dumps({"query": query, "results": results})

        if method == "POST" and path == "/index":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            text = body_data.get("text", "")
            if not text:
                return 400, "application/json", json.dumps({"error": "text is required"})
            node = self.graph.index_text(text)
            return 200, "application/json", json.dumps({"id": node.id, "label": node.label})

        if method == "POST" and path == "/search":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            query = body_data.get("query", "")
            top_k = int(body_data.get("top_k", 5))
            results = self.graph.search(query, top_k=top_k)
            return 200, "application/json", json.dumps({"query": query, "results": results})

        if method == "POST" and path == "/ingest":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            targets = body_data.get("targets", [])
            if not targets:
                return 400, "application/json", json.dumps({"error": "targets list is required"})
            result = self.pings.check_list(targets)
            self.pings.register_to_graph()
            return 200, "application/json", json.dumps({"ingested": len(targets), "active": len(result["active"]), "inactive": len(result["inactive"])})

        if path == "/ping/active" and method == "GET":
            return 200, "application/json", json.dumps({"active": [asdict(r) for r in self.pings.active_list]})

        if path == "/ping/inactive" and method == "GET":
            return 200, "application/json", json.dumps({"inactive": [asdict(r) for r in self.pings.inactive_list]})

        if path == "/xspace" and method == "GET":
            return 200, "application/json", json.dumps(self.xspace.get_x_space())

        if method == "POST" and path == "/xspace/gate":
            body_data = json.loads(body.decode()) if body else {}
            host = body_data.get("host", "")
            port = int(body_data.get("port", 0))
            protocol = body_data.get("protocol", "tcp")
            gate = self.xspace.add_gate(host, port, protocol)
            return 200, "application/json", json.dumps({"gate": asdict(gate)})

        if method == "POST" and path == "/xspace/mirror":
            body_data = json.loads(body.decode()) if body else {}
            host = body_data.get("host", "")
            port = int(body_data.get("port", 0))
            source_gate_id = body_data.get("source_gate_id", "")
            content_hash = body_data.get("content_hash", "")
            mirror = self.xspace.add_mirror(host, port, source_gate_id, content_hash)
            return 200, "application/json", json.dumps({"mirror": asdict(mirror)})

        if method == "POST" and path == "/xspace/query":
            body_data = json.loads(body.decode()) if body else {}
            query = body_data.get("query", "")
            results = self.xspace.git_like_query(query)
            return 200, "application/json", json.dumps(results)

        if method == "POST" and path == "/xspace/retrieve":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            content_hash = body_data.get("content_hash", "")
            threshold = float(body_data.get("threshold", 0.8))
            if not content_hash:
                return 400, "application/json", json.dumps({"error": "content_hash is required"})
            mirrors = self.xspace.retrieve_mirror(content_hash, threshold=threshold)
            return 200, "application/json", json.dumps({"query": content_hash, "threshold": threshold, "mirrors": mirrors})

        if method == "POST" and path == "/xspace/scan":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            target = body_data.get("target", "")
            if not target:
                return 400, "application/json", json.dumps({"error": "target host or CIDR is required"})
            from xspace_scanner import XSpaceScanner
            scanner = XSpaceScanner(self.xspace)
            if "/" in target:
                result = scanner.scan_network(target)
            else:
                items = scanner.scan_host(target)
                result = {"host": target, "discovered": len(items), "items": items}
            return 200, "application/json", json.dumps(result)

        if method == "POST" and path == "/chainnet/validate":
            body_data = json.loads(body.decode()) if body else {}
            address = body_data.get("address", "")
            if not address:
                return 400, "application/json", json.dumps({"error": "address is required"})
            result = validate_p2pkh_address(address)
            return 200, "application/json", json.dumps(result)

        if method == "POST" and path == "/chainnet/balance":
            body_data = json.loads(body.decode()) if body else {}
            address = body_data.get("address", "")
            if not address:
                return 400, "application/json", json.dumps({"error": "address is required"})
            result = check_balance(address)
            return 200, "application/json", json.dumps(result)

        if method == "POST" and path == "/chainnet/cast":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            sender = body_data.get("sender")  # optional, defaults to .env ADR
            xpub = body_data.get("xpub")      # optional, defaults to .env ADR2
            btc_amount = body_data.get("btc_amount")  # optional, defaults to .env BTC_AMOUNT
            if btc_amount is not None:
                btc_amount = float(btc_amount)
            derivation_count = int(body_data.get("derivation_count", 1))
            start_index = int(body_data.get("start_index", 0))
            result = cast_to_xpub(
                sender=sender,
                xpub=xpub,
                btc_amount=btc_amount,
                derivation_count=derivation_count,
                start_index=start_index,
            )
            return 200, "application/json", json.dumps(result)

        if method == "POST" and path == "/chainnet/cast/complete":
            auth = self.auth.validate(token)
            if not auth["valid"]:
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
            body_data = json.loads(body.decode()) if body else {}
            private_key_wif = body_data.get("key")  # optional, defaults to .env KEY
            fee_sat = int(body_data.get("fee_sat", 1000))
            derivation_count = int(body_data.get("derivation_count", 1))
            # Build cast first, then complete
            cast = cast_to_xpub(derivation_count=derivation_count)
            result = complete_cast(cast, private_key_wif=private_key_wif, fee_sat=fee_sat)
            return 200, "application/json", json.dumps(result)

        if method == "POST" and path == "/seednet/scan":
            body_data = json.loads(body.decode()) if body else {}
            root = body_data.get("root", ".")
            gate_threshold = int(body_data.get("gate_threshold", 1))
            self.seeds = scan_dir(root)
            self.threats = detect_threats(self.seeds)
            stats = summary(self.seeds, self.threats)
            commitments = [s.commitment for s in self.seeds if s.commitment]
            for seed in self.seeds:
                if not seed.commitment:
                    continue
                occurrences = sum(1 for s in self.seeds if s.value_sha256 == seed.value_sha256)
                if occurrences >= gate_threshold:
                    gate = self.xspace.add_gate(
                        host=f"seed:{seed.kind}",
                        port=0,
                        protocol="seednet",
                        metadata={
                            "kind": seed.kind,
                            "value_sha256": seed.value_sha256,
                            "file_sha256": seed.file_sha256,
                            "address": seed.address,
                            "line": seed.line,
                            "occurrences": occurrences,
                            "commitment": seed.commitment,
                        },
                    )
                    seed.commitment["gate_id"] = gate.id

            doc = {
                "schema": 1,
                "generated_at": int(time.time()),
                "root": os.path.abspath(root),
                "stats": stats,
                "commitments": commitments,
                "seeds": [asdict(s) for s in self.seeds],
                "threats": [asdict(t) for t in self.threats],
            }
            out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seednet_catalog.json")
            with open(out_path, "w") as f:
                json.dump(doc, f, indent=2)
            doc["saved_to"] = out_path
            return 200, "application/json", json.dumps(doc)

        if path == "/seednet/commitments" and method == "GET":
            commitments = [s.commitment for s in self.seeds if s.commitment]
            return 200, "application/json", json.dumps({"count": len(commitments), "commitments": commitments})

        if path == "/seednet/threats" and method == "GET":
            return 200, "application/json", json.dumps({"count": len(self.threats), "threats": [asdict(t) for t in self.threats]})

        if path == "/seednet/catalog" and method == "GET":
            catalog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seednet_catalog.json")
            if not os.path.exists(catalog_path):
                return 404, "application/json", json.dumps({"error": "No catalog found. Run POST /seednet/scan first."})
            with open(catalog_path, "r") as f:
                doc = json.load(f)
            return 200, "application/json", json.dumps(doc)

        return 404, "application/json", json.dumps({"error": "Not found"})

    def get_admin_token(self) -> str:
        return self.auth.admin_token

    async def __call__(self, scope: dict, receive, send) -> None:
        if scope["type"] != "http":
            await send({"type": "http.response.start", "status": 404, "headers": [[b"content-type", b"application/json"]]})
            await send({"type": "http.response.body", "body": b'{"error":"Not found"}'})
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        headers = {}
        for key, value in scope.get("headers", []):
            headers[key.decode()] = value.decode()

        body = b""
        if method == "POST":
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break

        status, content_type, response_body = self.handle_request(method, path, headers, body)

        await send({"type": "http.response.start", "status": status, "headers": [[b"content-type", content_type.encode()]]})
        await send({"type": "http.response.body", "body": response_body.encode()})
