"""
rf_neural_correlator.py
Live RF neural net correlator — maps surrounding WiFi/RF signatures
into "brain mesh" frequency space, detects entropy anomalies,
targets the highest-bound unique state, and bridges into the
broadcast/receiver system.
"""

from brain_mesh_chain import BrainMeshChain, RawRFEntry
import json
import math
import os
import re
import socket
import struct
import subprocess
import threading
import time
import hashlib
import zlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# Constants / shared across project
# ============================================================
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
BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 18989
LISTEN_PORT = 18989

# Neural brain-mesh frequency bands (Hz-like equivalents mapped from RF)
NEURAL_BANDS = {
    "delta":   (0.5, 4.0),
    "theta":   (4.0, 8.0),
    "alpha":   (8.0, 13.0),
    "beta":    (13.0, 30.0),
    "gamma":   (30.0, 100.0),
    "high_gamma": (100.0, 200.0),
}

# How each WiFi band maps to a "brain mesh" band
RF_TO_NEURAL_MAP = {
    2400: "beta",
    5000: "gamma",
    6000: "high_gamma",
}


# ============================================================
# Data structures
# ============================================================
@dataclass
class RFSignature:
    bssid: str
    ssid: str
    rssi_dbm: int
    channel: int
    frequency_mhz: float
    band: str
    vendor: str
    neural_band: str
    neural_frequency_hz: float
    signal_entropy: float
    timestamp: str
    attractor_score: float = 0.0


@dataclass
class NeuralNetState:
    band: str
    mean_entropy: float
    dominant_bssids: List[str]
    density_score: float
    unique_space_score: float = 0.0
    timestamp: str = ""


# ============================================================
# Helpers
# ============================================================
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


def build_entropy_payload(extra: Optional[bytes] = b"") -> bytes:
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
    body += bytes.fromhex(EXPECTED_MERKLE)
    return tag + body + extra


# ============================================================
# Live RF capture (uses Windows netsh, falls back to synthetic)
# ============================================================
class LiveRFCapture:
    """
    Captures surrounding RF / WiFi signatures from the local adapter.
    Falls back to synthetic data if no adapter is available.
    """

    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.vendor_database = {
            'c8:70:23': 'Netgear', '80:69:1a': 'Linksys',
            '00:1b:63': 'Apple', '00:26:bb': 'Apple',
            'ac:87:a3': 'Apple', '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox', '00:0c:29': 'VMware',
            '00:15:5d': 'Microsoft Hyper-V',
            '6e:03:bc': 'Broadcom', 'bc:23:47': 'Broadcom',
        }

    def _get_vendor(self, bssid: str) -> str:
        if not bssid or len(bssid) < 8:
            return "Unknown"
        oui = bssid[:8].lower()
        return self.vendor_database.get(oui, "Unknown")

    def _rssi_to_entropy(self, rssi_dbm: int) -> float:
        # Map dBm (usually -90..-30) to a 0..1 "neural entropy" value
        v = max(0.0, min(1.0, (rssi_dbm + 100) / 70.0))
        # Apply a non-linear transform to make adjacent signals distinct
        return round(math.log(v + 1e-9) * -0.5 + 0.5, 6)

    def _map_to_neural_band(self, freq_mhz: float) -> Tuple[str, float]:
        base = min(RF_TO_NEURAL_MAP.keys(), key=lambda f: abs(f - freq_mhz))
        band_name = RF_TO_NEURAL_MAP[base]
        low, high = NEURAL_BANDS[band_name]
        # Normalize position inside the RF band into the neural Hz band
        ratio = min(max((freq_mhz - base) / 1000.0, 0.0), 1.0)
        neural_hz = low + ratio * (high - low)
        return band_name, round(neural_hz, 3)

    def scan_windows(self) -> List[RFSignature]:
        try:
            cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
            if self.interface:
                cmd.extend([f'interface="{self.interface}"'])
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
            return self._parse_netsh(result.stdout)
        except Exception as e:
            print(f"[RF] netsh capture failed: {e}")
            return []

    def _parse_netsh(self, output: str) -> List[RFSignature]:
        sigs: List[RFSignature] = []
        lines = output.split("\n")
        current_ssid = ""
        current_bssid = ""
        block: Dict[str, str] = {}
        timestamp = datetime.now(timezone.utc).isoformat()

        flush = lambda: (
            sigs.append(self._build_sig(current_ssid, current_bssid, block, timestamp))
            if current_bssid else None
        )

        for raw in lines:
            line = raw.strip()
            if line.startswith("SSID") and ":" in line:
                flush()
                current_ssid = line.split(":", 1)[1].strip() or "<Hidden>"
                current_bssid = ""
                block = {}
            elif line.startswith("BSSID") and ":" in line:
                flush()
                current_bssid = line.split(":", 1)[1].strip()
                block = {}
            elif line and ":" in line and current_bssid:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip()
                if k == "signal" and "%" in v:
                    block["signal"] = re.search(r"(\d+)%", v)
                    block["signal"] = int(block["signal"].group(1)) if block["signal"] else 0
                elif k == "channel":
                    block["channel"] = int(re.search(r"\d+", v).group()) if re.search(r"\d+", v) else 1
                elif k == "authentication":
                    block["auth"] = v
                elif k == "encryption":
                    block["cipher"] = v

        flush()
        return [s for s in sigs if s is not None]

    def _build_sig(self, ssid: str, bssid: str, block: Dict[str, str], timestamp: str) -> Optional[RFSignature]:
        if not bssid:
            return None
        channel = block.get("channel", 1)
        freq = 2407 + channel * 5 if channel <= 14 else 5170 + (channel - 36) * 5
        band = "2.4GHz" if freq < 3000 else ("5GHz" if freq < 6000 else "6GHz+")
        neural_band, neural_hz = self._map_to_neural_band(freq)
        rssi = block.get("signal", 0)
        ent = self._rssi_to_entropy(-90 + int(rssi * 0.6))
        return RFSignature(
            bssid=bssid,
            ssid=ssid,
            rssi_dbm=int(-90 + rssi * 0.6),
            channel=channel,
            frequency_mhz=round(freq, 1),
            band=band,
            vendor=self._get_vendor(bssid),
            neural_band=neural_band,
            neural_frequency_hz=neural_hz,
            signal_entropy=ent,
            timestamp=timestamp,
        )

    def capture(self) -> List[RFSignature]:
        sigs = self.scan_windows()
        if not sigs:
            # synthetic fallback — mirrors existing project behavior
            sigs = self._synthetic()
        return sigs

    def _synthetic(self) -> List[RFSignature]:
        now = datetime.now(timezone.utc).isoformat()
        sigs = []
        import random as _r
        _r.seed(int(time.time()) // 5)
        for ch in [1, 6, 11, 36, 40, 44, 48, 149, 153]:
            freq = 2407 + ch * 5 if ch <= 14 else 5170 + (ch - 36) * 5
            band = "2.4GHz" if freq < 3000 else "5GHz"
            neural_band, neural_hz = self._map_to_neural_band(freq)
            rssi = -30 - _r.randint(0, 50)
            ent = self._rssi_to_entropy(rssi)
            bssid = f"XX:XX:{ch:02x}:{abs(rssi):02x}:{ch:02x}:{abs(rssi):02x}"
            sigs.append(RFSignature(
                bssid=bssid, ssid=f"syn_{ch}", rssi_dbm=rssi, channel=ch,
                frequency_mhz=round(freq, 1), band=band,
                vendor="Synthetic", neural_band=neural_band,
                neural_frequency_hz=neural_hz,
                signal_entropy=ent, timestamp=now,
            ))
        return sigs


# ============================================================
# Neural mesh correlator
# ============================================================
class NeuralMeshCorrelator:
    """
    Correlates live RF signatures into 'brain mesh' bands and
    identifies the unique space with the highest bound.
    """

    def __init__(self):
        self.rf_signatures: List[RFSignature] = []
        self.neural_nets: Dict[str, NeuralNetState] = {}
        self.highest_bound: Optional[Dict] = None
        self.anomaly_events: List[Dict] = []
        self._lock = threading.Lock()
        self.entropy_history: List[float] = []
        self.size_history: List[int] = []

    def process_signatures(self, sigs: List[RFSignature]):
        self.rf_signatures = sigs
        nets: Dict[str, List[RFSignature]] = {}
        for s in sigs:
            nets.setdefault(s.neural_band, []).append(s)

        now = datetime.now(timezone.utc).isoformat()
        scored: List[Tuple[str, NeuralNetState, float]] = []
        for band, members in nets.items():
            ents = [m.signal_entropy for m in members]
            mean_e = sum(ents) / len(ents) if ents else 0.0
            dom = sorted(members, key=lambda m: m.rssi_dbm, reverse=True)[:3]
            state = NeuralNetState(
                band=band,
                mean_entropy=round(mean_e, 6),
                dominant_bssids=[m.bssid for m in dom],
                density_score=round(mean_e * len(members), 6),
                timestamp=now,
            )
            self.neural_nets[band] = state
            scored.append((band, state, self._unique_space_score(state)))

        scored.sort(key=lambda x: x[2], reverse=True)
        if scored:
            best_band, best_state, best_score = scored[0]
            with self._lock:
                self.highest_bound = {
                    "band": best_band,
                    "neural_frequency_hz": best_band,
                    "density_score": best_state.density_score,
                    "unique_space_score": best_score,
                    "dominant_bssids": best_state.dominant_bssids,
                    "mean_entropy": best_state.mean_entropy,
                    "timestamp": now,
                    "merkle_root": EXPECTED_MERKLE,
                }

        # Entropy + size bookkeeping (for anomaly detection on "probe-like" streams)
        for s in sigs:
            self.entropy_history.append(s.signal_entropy)
        self.entropy_history = self.entropy_history[-512:]
        self._detect_anomalies()

    def _unique_space_score(self, state: NeuralNetState) -> float:
        """
        Score = entropy payload + member count + dominant dominance.
        Highest score = highest bound in unique space + entropy anomaly state.
        """
        ent = state.mean_entropy or 1e-9
        count = len(state.dominant_bssids) + 1
        return round(math.log(ent + 1e-9) * -0.5 + count * 2.0, 6)

    def _detect_anomalies(self):
        if len(self.entropy_history) < 5:
            return
        window = self.entropy_history[-20:]
        mean_e = sum(window) / len(window)
        if mean_e < 1e-6:
            return
        variance = sum((e - mean_e) ** 2 for e in window) / len(window)
        std = math.sqrt(variance)
        latest = window[-1]
        # z-score spike + minimum std guard
        if std > 1e-4 and abs(latest - mean_e) / std > 2.5:
            ev = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "ENTROPY_ANOMALY",
                "latest": round(latest, 6),
                "mean": round(mean_e, 6),
                "std": round(std, 6),
                "z_score": round(abs(latest - mean_e) / std, 4),
                "highest_bound": self.highest_bound,
                "merkle_root": EXPECTED_MERKLE,
                "fix_value": RUNNING_FIX,
            }
            with self._lock:
                self.anomaly_events.append(ev)
            print(f"[NEURAL_ANOMALY] z={ev['z_score']:.2f} latest={latest:.4f} mean={mean_e:.4f}")
            return True
        return False

    def report(self) -> Dict:
        with self._lock:
            return {
                "highest_bound": self.highest_bound,
                "neural_nets": {k: asdict(v) for k, v in self.neural_nets.items()},
                "rf_count": len(self.rf_signatures),
                "recent_anomalies": len(self.anomaly_events[-20:]),
            }


# ============================================================
# Brain mesh simulator (geometric protocol)
# ============================================================
class BrainMeshSimulator:
    """
    Turns the highest-bound RF signature into a brain-mesh style
    geometric protocol, applies wave attraction, and emits a
    binary instruction compatible with the quantum framework outputs.
    """

    def __init__(self, output_dir: str = "spectrum_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_protocol(self, bound: Dict) -> Optional[bytes]:
        if not bound:
            return None
        x, y, z = 0.0, 0.0, 0.0
        try:
            raw = (bound.get("band") or "").encode("utf-8")
            h = hashlib.sha256(raw).digest()
            x = struct.unpack(">d", h[:8])[0] % 1000
            y = struct.unpack(">d", h[8:16])[0] % 1000
            z = struct.unpack(">d", h[16:24])[0] % 1000
        except Exception:
            pass

        instruction = bytearray()
        instruction.extend([0x51, 0x4E, 0x45, 0x55])  # "QNEU" magic
        instruction.extend(struct.pack(">d", x))
        instruction.extend(struct.pack(">d", y))
        instruction.extend(struct.pack(">d", z))
        instruction.extend(struct.pack(">d", bound.get("unique_space_score", 0.0)))
        instruction.extend(struct.pack(">d", bound.get("density_score", 0.0)))
        instruction.extend(struct.pack(">I", len(bound.get("dominant_bssids", []))))
        for b in bound.get("dominant_bssids", []):
            instruction.extend(b.encode("utf-8")[:64].ljust(64, b"\x00"))
        instruction.append(sum(instruction) % 256)

        out = self.output_dir / "brain_mesh_instruction.bin"
        out.write_bytes(bytes(instruction))
        print(f"[BRAIN_MESH] Protocol written -> {out}")
        return bytes(instruction)


# ============================================================
# Bridge into broadcast/receiver
# ============================================================
class ReceiverBridge:
    """
    Listens for BYTECRAFT_AWAKE broadcasts, decodes them, and feeds
    them back into the neural correlator as live entropy states.
    """

    def __init__(self, port: int = LISTEN_PORT, on_event=None):
        self.port = port
        self.on_event = on_event
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("0.0.0.0", self.port))
        except OSError as e:
            print(f"[BRIDGE] Bind failed: {e}")
            raise
        self.running = False

    def _parse(self, data: bytes) -> Optional[Dict]:
        try:
            header, payload = data.split(b"|", 1)
            meta = json.loads(header)
            if not payload.startswith(b"BYTECRAFT_AWAKE\x00"):
                return None
            offset = 15
            fields = {}
            names = ["entropy_current", "entropy_prev", "entropy_delta",
                     "compression_cycles", "fix_50_0",
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
        print(f"[BRIDGE] Receiving UDP on {self.port}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                pkt = self._parse(data)
                if pkt:
                    print(f"[BRIDGE] Accepted from {addr} -> seq={pkt.get('sequence')} layer={pkt.get('layer')}")
                    if callable(self.on_event):
                        self.on_event(pkt)
            except OSError:
                break
            except Exception as e:
                print(f"[BRIDGE] {e}")

    def stop(self):
        self.running = False
        self.sock.close()


# ============================================================
# Controller / main loop
# ============================================================
class RFNeuralCorrelator:
    """
    Main controller: live RF -> neural mesh -> highest bound -> brain mesh protocol -> broadcast.
    """

    def __init__(self, watch_dir: str = "probe-sequence/spectrum_data"):
        self.capture = LiveRFCapture()
        self.correlator = NeuralMeshCorrelator()
        self.simulator = BrainMeshSimulator(watch_dir)
        self.bridge = ReceiverBridge(on_event=self._on_receiver_event)
        self.chain = BrainMeshChain()
        self._loop_interval = 2.0
        self.running = False

    def _on_receiver_event(self, pkt: Dict):
        # Feed received entropy state back into correlator
        delta = pkt.get("entropy_delta", 0.0)
        with self.correlator._lock:
            self.correlator.entropy_history.append(delta)
            self.correlator.entropy_history = self.correlator.entropy_history[-512:]
        print(f"[FEEDBACK] Receiver entropy_delta={delta:.4f} injected")

    def _broadcast_state(self, bound: Dict, anomaly: bool = False):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            payload = build_entropy_payload()
            header = json.dumps({
                "source": "rf_neural_correlator",
                "highest_bound": bound,
                "anomaly": anomaly,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }).encode("utf-8")
            sock.sendto(header + b"|" + payload, (BROADCAST_IP, BROADCAST_PORT))
            sock.close()
        except Exception as e:
            print(f"[BROADCAST] Failed: {e}")

    def _emit_anomaly(self, event: Dict):
        out = Path("rf_neural_anomaly_event.json")
        out.write_text(json.dumps(event, indent=2))
        print(f"[EVENT] Anomaly written to {out}")

    def tick(self):
        sigs = self.capture.capture()
        # Log raw RF -> neural mappings for sync
        entries = [
            RawRFEntry(
                timestamp=s.timestamp,
                bssid=s.bssid,
                ssid=s.ssid,
                rssi_dbm=s.rssi_dbm,
                channel=s.channel,
                frequency_mhz=s.frequency_mhz,
                band=s.band,
                neural_band=s.neural_band,
                neural_frequency_hz=s.neural_frequency_hz,
                signal_entropy=s.signal_entropy,
                vendor=s.vendor,
            )
            for s in sigs
        ]
        self.chain.log_raw_rf(entries)
        self.correlator.process_signatures(sigs)
        rep = self.correlator.report()
        self.chain.update_from_correlator(rep)
        bound = rep.get("highest_bound")
        if bound:
            print(f"[BOUND] band={bound.get('band')} score={bound.get('unique_space_score')} density={bound.get('density_score')}")
            proto = self.simulator.build_protocol(bound)
            self._broadcast_state(bound, anomaly=False)
            if rep.get("recent_anomalies", 0) > len(self.correlator.anomaly_events) - 1:
                last = self.correlator.anomaly_events[-1] if self.correlator.anomaly_events else {}
                self.chain.record_anomaly(last)
                self._emit_anomaly(last)
                self._broadcast_state(bound, anomaly=True)
        else:
            print("[BOUND] No RF signatures — no bound")

    def start(self):
        self.running = True
        print("[RF_NEURAL] Correlator started")
        rx = threading.Thread(target=self.bridge.start, daemon=True)
        rx.start()
        try:
            while self.running:
                self.tick()
                time.sleep(self._loop_interval)
        except KeyboardInterrupt:
            print("\n[STOP] Halted.")
            self.bridge.stop()


def main():
    c = RFNeuralCorrelator()
    c.start()


if __name__ == "__main__":
    main()
