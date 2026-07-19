"""
probe_sequence_analyzer.py
Integrates probe-sequence scanning with entropy broadcast/receiver.
Detects breaks, size anomalies, missing sequences.
Targets unique space: highest found bound + entropy anomaly state.
"""

import os
import re
import time
import struct
import hashlib
import json
import socket
import threading
import zlib
import math
import csv
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Reuse Merkle root constants from project
BLOCK_TXIDS = [
    "fb6fd78b6ce1770644e820ce1b27547804f9a52ebb24dd07964b3262440a9239",
    "1fbbf28c19a5bd2034dff97ad55949f3c312f18f9bdd160494d650d754f2bd02",
    "66f2dc47f42eb408d2450a0b6b0ee27604b3eff079dfefff6d4693eebbad152c",
    "6c3b1b90c3c46b8ede703811aedf546eb869531276b82f181c25014799fd552e",
    "733d85cc13fbd42519309023b3f96ad91861abbae14e19c4d99d61f5cf01031f",
    "6e0d7e0cd0e62b6ec39a7260280bc8a330c44ff8fc71d5aa8acfe2ec20d944e0",
]
EXPECTED_MERKLE = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
RUNNING_FIX = 50.0
LISTEN_PORT = 18989
BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 18989


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compute_merkle_root(txids: list) -> str:
    hashes = [bytes.fromhex(txid)[::-1] for txid in txids]
    while len(hashes) > 1:
        new = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + (hashes[i + 1] if i + 1 < len(hashes) else hashes[i])
            new.append(double_sha256(combined))
        hashes = new
    return hashes[0][::-1].hex()


def pack_double_be(d: float) -> bytes:
    return struct.pack(">d", d)


def build_entropy_payload() -> bytes:
    tag = b"BYTECRAFT_AWAKE\x00"
    body = pack_double_be(15706319436.5)
    body += pack_double_be(15706068788.0)
    body += pack_double_be(15706319436.5 - 15706068788.0)
    body += pack_double_be(125321.0)
    body += pack_double_be(50.0)
    body += pack_double_be(10.43)
    body += pack_double_be(46.179)
    body += pack_double_be(109.0)
    body += pack_double_be(50.0)
    body += bytes.fromhex("662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325")
    return tag + body


@dataclass
class IntegrationProbe:
    file_path: str
    sequence: int
    size: int
    mtime: float
    checksum: str
    layer: int
    entropy_delta: float
    anomalies: List[str] = field(default_factory=list)


class ProbeSequenceAnalyzer:
    def __init__(self, watch_dir: str):
        self.watch_dir = Path(watch_dir)
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.seq_pattern = re.compile(r"integration_(\d+)\.dat")
        self.known_files: set = set()
        self.sequence_log: List[int] = []
        self.size_history: Dict[int, int] = {}
        self.entropy_history: List[float] = []
        self.highest_bound: Optional[Dict] = None
        self.anomaly_events: List[Dict] = []
        self._lock = threading.Lock()

    def _checksum(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()[:16]

    def _entropy_delta(self, path: Path) -> float:
        try:
            raw = path.read_bytes()
            freqs = []
            for b in raw[:1024]:
                v = b / 255.0
                if v > 1e-12:
                    freqs.append(-v * math.log(v, 2))
            ent = sum(freqs) if freqs else 0.0
            return round(ent, 6)
        except Exception:
            return 0.0

    def _layer_from_size(self, size: int) -> int:
        if size < 1024:
            return 1
        if size < 4096:
            return 2
        if size < 16384:
            return 3
        if size < 65536:
            return 4
        return 5

    def ingest(self, path: Path) -> IntegrationProbe:
        seq = 0
        m = self.seq_pattern.match(path.name)
        if m:
            seq = int(m.group(1))
        size = path.stat().st_size
        mtime = path.stat().st_mtime
        checksum = self._checksum(path)
        ent = self._entropy_delta(path)
        layer = self._layer_from_size(size)
        probe = IntegrationProbe(
            file_path=str(path),
            sequence=seq,
            size=size,
            mtime=mtime,
            checksum=checksum,
            layer=layer,
            entropy_delta=ent,
        )
        with self._lock:
            self.size_history[seq] = size
            self.entropy_history.append(ent)
            self._detect_anomalies(probe)
            self._update_highest_bound(probe)
        return probe

    def _detect_anomalies(self, probe: IntegrationProbe):
        expected = (self.sequence_log[-1] + 1) if self.sequence_log else 1
        if probe.sequence and probe.sequence != expected:
            probe.anomalies.append("SEQUENCE_BREAK")
        if len(self.size_history) > 2:
            sizes = list(self.size_history.values())
            avg = sum(sizes) / len(sizes)
            if avg > 0 and abs(probe.size - avg) / avg > 0.5:
                probe.anomalies.append("SIZE_ANOMALY")
        if len(self.entropy_history) > 3:
            recent = self.entropy_history[-4:]
            mean_e = sum(recent[:-1]) / (len(recent) - 1)
            if mean_e > 0 and abs(probe.entropy_delta - mean_e) / mean_e > 0.8:
                probe.anomalies.append("ENTROPY_ANOMALY")
        if not probe.anomalies:
            probe.anomalies.append("NOMINAL")
            if probe.sequence:
                self.sequence_log.append(probe.sequence)

    def _update_highest_bound(self, probe: IntegrationProbe):
        score = self._state_score(probe)
        if self.highest_bound is None or score > self.highest_bound.get("score", 0):
            self.highest_bound = {
                "file": probe.file_path,
                "sequence": probe.sequence,
                "score": score,
                "size": probe.size,
                "entropy_delta": probe.entropy_delta,
                "layer": probe.layer,
                "checksum": probe.checksum,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _state_score(self, probe: IntegrationProbe) -> float:
        return (
            probe.layer * 10
            + probe.entropy_delta * 5
            + math.log(max(probe.size, 1), 2) * 0.1
            + (len(probe.anomalies) * 2)
        )

    def find_missing_sequences(self) -> List[int]:
        if not self.sequence_log:
            return []
        s = sorted(set(self.sequence_log))
        missing = []
        for i in range(min(s), max(s) + 1):
            if i not in s:
                missing.append(i)
        return missing

    def scan_existing(self):
        for p in sorted(self.watch_dir.glob("integration_*.dat")):
            self.ingest(p)
            self.known_files.add(p.name)

    def watch(self):
        print(f"[PROBE] Watching {self.watch_dir}")
        self.scan_existing()
        while True:
            current = set(p.name for p in self.watch_dir.glob("integration_*.dat"))
            for name in sorted(current - self.known_files):
                path = self.watch_dir / name
                probe = self.ingest(path)
                self.known_files.add(name)
                print(f"[PROBE] {name} seq={probe.sequence} size={probe.size} layer={probe.layer} anomalies={probe.anomalies}")
                if probe.anomalies != ["NOMINAL"]:
                    self.emit_anomaly_event(probe)
                    self.broadcast_state(probe)
            time.sleep(1)

    def emit_anomaly_event(self, probe: IntegrationProbe):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file": probe.file_path,
            "sequence": probe.sequence,
            "size": probe.size,
            "layer": probe.layer,
            "entropy_delta": probe.entropy_delta,
            "anomalies": probe.anomalies,
            "merkle_root": EXPECTED_MERKLE,
            "action": "PROBE_ANOMALY_DETECTED",
            "highest_bound": self.highest_bound,
        }
        out = self.watch_dir / "probe_anomaly_event.json"
        out.write_text(json.dumps(event, indent=2))
        print(f"[EVENT] Anomaly written to {out}")

    def broadcast_state(self, probe: IntegrationProbe):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            payload = build_entropy_payload()
            header = json.dumps({
                "source": "probe_sequence_analyzer",
                "file": probe.file_path,
                "sequence": probe.sequence,
                "anomalies": probe.anomalies,
                "layer": probe.layer,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }).encode("utf-8")
            packet = header + b"|" + payload
            sock.sendto(packet, (BROADCAST_IP, BROADCAST_PORT))
            sock.close()
        except Exception as e:
            print(f"[BROADCAST] Failed: {e}")


class EntropyReceiver:
    def __init__(self, port: int = LISTEN_PORT):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("0.0.0.0", self.port))
        except OSError as e:
            print(f"[RECEIVER] Bind failed: {e}")
            raise
        self.running = False
        self.last_event: Dict = {}

    def _parse(self, data: bytes) -> Optional[Dict]:
        try:
            header, payload = data.split(b"|", 1)
            meta = json.loads(header)
            if not payload.startswith(b"BYTECRAFT_AWAKE\x00"):
                return None
            offset = 15
            fields = {}
            names = ["entropy_current", "entropy_prev", "entropy_delta", "compression_cycles", "fix_50_0",
                     "spatial_offset", "bound_coord", "merged_bound", "horizon_index"]
            for name in names:
                fields[name] = struct.unpack_from(">d", payload, offset)[0]
                offset += 8
            fields["merkle_root"] = payload[offset:offset + 32].hex()
            if fields.get("fix_50_0") != RUNNING_FIX:
                return None
            if fields.get("merkle_root") != EXPECTED_MERKLE:
                return None
            meta.update(fields)
            return meta
        except Exception:
            return None

    def start(self):
        self.running = True
        print(f"[RECEIVER] Listening on UDP {self.port}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                pkt = self._parse(data)
                if pkt:
                    self.last_event = pkt
                    print(f"[ACCEPT] {addr} seq={pkt.get('sequence')} layer={pkt.get('layer')} anomalies={pkt.get('anomalies')}")
                    out = Path("entropy_awake_event.json")
                    out.write_text(json.dumps(pkt, indent=2))
            except OSError:
                break
            except Exception as e:
                print(f"[RECEIVER] {e}")

    def stop(self):
        self.running = False
        self.sock.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Probe-sequence analyzer / broadcast / receiver")
    parser.add_argument("--dir", default="spectrum_data", help="Watch directory for integration_*.dat")
    parser.add_argument("--receive", action="store_true", help="Run receiver only")
    parser.add_argument("--broadcast", action="store_true", help="Run analyzer with broadcast only")
    args = parser.parse_args()

    if args.receive:
        rx = EntropyReceiver()
        try:
            rx.start()
        except KeyboardInterrupt:
            rx.stop()
        return

    analyzer = ProbeSequenceAnalyzer(args.dir)
    rx = EntropyReceiver()
    t = threading.Thread(target=rx.start, daemon=True)
    t.start()
    try:
        analyzer.watch()
    except KeyboardInterrupt:
        print("\n[STOP] Halted.")
        rx.stop()


if __name__ == "__main__":
    main()
