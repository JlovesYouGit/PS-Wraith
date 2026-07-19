"""
intake.py — Mana Ciel Connection Intake Engine
Awaits first ping, validates, sends credentials, logs all connections.
Coordinates entire codebase via synergy.
"""

import socket
import threading
import time
import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.coordinate import SynergyCoordinate
from mana_ciel.sequence import TimeCompressionSequence
from mana_ciel.narrative import NarrativeObserver
from mana_ciel.formula import cumulative_intelligence

logger = logging.getLogger("mana_ciel.intake")

DEFAULT_PORT = 19753
STORAGE_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel"
CONNECTIONS_FILE = STORAGE_DIR / "connections.json"


class ManaCielIntake:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = DEFAULT_PORT,
        coordinate: int | None = None,
        engine_graph: Any = None,
        engine_auth: Any = None,
    ):
        self.host = host
        self.port = port
        self.coordinate = SynergyCoordinate(coordinate)
        self.wallet = ManaCielWallet()
        self.sequence = TimeCompressionSequence(self.coordinate.value)
        self.narrative = NarrativeObserver(self.coordinate.value)
        self.engine_graph = engine_graph
        self.engine_auth = engine_auth

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        self._running = False
        self._thread: threading.Thread | None = None
        self._connections: list[dict] = self._load_connections()

        self.narrative.observe("intake_initialized", {"port": self.port, "coordinate": self.coordinate.to_dict()})

    def start(self) -> None:
        if self._running:
            logger.warning("Intake already running.")
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="mana_ciel_intake", daemon=True)
        self._thread.start()
        logger.info("ManaCielIntake listening on %s:%d", self.host, self.port)

    def stop(self) -> None:
        self._running = False
        try:
            self._sock.close()
        except Exception:
            pass
        logger.info("ManaCielIntake stopped.")

    def _loop(self) -> None:
        while self._running:
            try:
                self._sock.settimeout(1.0)
                try:
                    conn, addr = self._sock.accept()
                except socket.timeout:
                    continue
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        continue
                    decoded = data.decode("utf-8", errors="ignore").strip()
                    result = self.handle_ping(decoded, addr)
                    conn.sendall(json.dumps(result, default=str).encode("utf-8"))
            except Exception as e:
                if self._running:
                    logger.error("Intake loop error: %s", e)

    def handle_ping(self, payload: str, addr: tuple[str, int]) -> dict:
        first = len(self._connections) == 0
        connection_point = {
            "timestamp_unix": time.time(),
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "coordinate": self.coordinate.to_dict(),
            "peer_address": f"{addr[0]}:{addr[1]}",
            "payload": payload[:512],
            "first_ping": first,
            "status": "accepted",
        }

        if first:
            self.sequence.capture("first_ping", q=1, payload=payload)

        self.sequence.capture("connection_established", q=2, payload=payload)
        response = self.build_response(payload, connection_point)
        connection_point["response_sent"] = True
        connection_point["response_status"] = response.get("status")
        connection_point["response_formula_n"] = response.get("formula", {}).get("cumulative_intelligence")
        self._connections.append(connection_point)
        self._persist_connections()

        self.narrative.observe("connection_accepted", {
            "peer": connection_point["peer_address"],
            "first_ping": first,
            "cumulative_n": cumulative_intelligence(5),
        })

        if self.engine_graph:
            try:
                self.engine_graph.index_text(
                    payload,
                    metadata={
                        "source": "mana_ciel_intake",
                        "ip": addr[0],
                        "port": addr[1],
                        "world_net": True,
                    },
                )
            except Exception as e:
                logger.warning("Graph indexing failed: %s", e)

        return response

    def build_response(self, payload: str, connection_point: dict) -> dict:
        if not self.wallet.load_latest():
            self.wallet.generate(coord=self.coordinate.value)
        wallet = self.wallet.load_latest()

        wallet_creds = {
            "label": wallet.get("label", "ManaCiel"),
            "address": wallet["address"],
            "sha256_sum": wallet.get("sha256_sum", ""),
            "coordinate": wallet.get("coordinate", self.coordinate.to_dict()),
            "utxo_collective_value": wallet.get("utxo_collective_value", 0),
            "private_key_hex": wallet.get("private_key_hex"),
            "public_key_hex": wallet.get("public_key_hex"),
            "seed_phrase": wallet.get("seed_phrase"),
            "base58_p2pkh": wallet.get("base58_p2pkh"),
        }

        collective_utxo = self.wallet.collective_utxo()

        return {
            "status": "MANA_CIEL_ACCEPTED",
            "narrative_point": connection_point,
            "credentials": wallet_creds,
            "utxo_collective_value": collective_utxo,
            "formula": {
                "cumulative_intelligence": cumulative_intelligence(5),
                "final_form_n": 10,
                "q_model": "5^q",
            },
            "coordinate": self.coordinate.to_dict(),
        }

    def send_to_target(self, target: str, message: str) -> dict:
        try:
            host, port_str = target.split(":")
            port = int(port_str)
        except ValueError:
            return {"status": "error", "detail": "target must be host:port"}

        try:
            with socket.create_connection((host, port), timeout=5) as s:
                s.sendall(message.encode("utf-8"))
                resp = s.recv(65536).decode("utf-8", errors="ignore")
        except Exception as e:
            return {"status": "error", "detail": str(e)}

        connection_log = {
            "timestamp_unix": time.time(),
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "target": target,
            "direction": "outbound",
            "message": message[:512],
            "response": resp[:512],
            "coordinate": self.coordinate.to_dict(),
        }
        self._connections.append(connection_log)
        self._persist_connections()

        self.narrative.observe("outbound_transmission", {"target": target, "response_length": len(resp)})

        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            return {"status": "received", "raw_response": resp}

    def _persist_connections(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONNECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._connections, f, indent=2, default=str)

    def _load_connections(self) -> list[dict]:
        if not CONNECTIONS_FILE.exists():
            return []
        try:
            with open(CONNECTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_connections(self, limit: int = 100) -> list[dict]:
        return self._connections[-limit:]

    def status(self) -> dict:
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "coordinate": self.coordinate.to_dict(),
            "wallet": self.wallet.load_latest(),
            "connection_count": len(self._connections),
            "narrative_checksum": self.narrative.last_checksum,
        }
