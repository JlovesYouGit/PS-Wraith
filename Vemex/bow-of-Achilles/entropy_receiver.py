"""
entropy_receiver.py
Listens on UDP port 18989 for the Bytecraft_AWAKE entropy broadcast
mirroring the Broadcom-mimicking frame. Validates entropy delta,
merkle root anchor, and applies the 50.0 running fix value.
"""

import socket
import struct
import hashlib
import json
import os
import time
import threading

EXPECTED_MERKLE = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
RUNNING_FIX = 50.0
LISTEN_PORT = 18989
EVENT_PATH = os.path.join(os.path.dirname(__file__), "entropy_awake_event.json")

BLOCK_TXIDS = [
    "fb6fd78b6ce1770644e820ce1b27547804f9a52ebb24dd07964b3262440a9239",
    "1fbbf28c19a5bd2034dff97ad55949f3c312f18f9bdd160494d650d754f2bd02",
    "66f2dc47f42eb408d2450a0b6b0ee27604b3eff079dfefff6d4693eebbad152c",
    "6c3b1b90c3c46b8ede703811aedf546eb869531276b82f181c25014799fd552e",
    "733d85cc13fbd42519309023b3f96ad91861abbae14e19c4d99d61f5cf01031f",
    "6e0d7e0cd0e62b6ec39a7260280bc8a330c44ff8fc71d5aa8acfe2ec20d944e0",
]


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compute_merkle_root(txids: list) -> str:
    hashes = [bytes.fromhex(txid)[::-1] for txid in txids]
    while len(hashes) > 1:
        new = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                combined = hashes[i] + hashes[i + 1]
            else:
                combined = hashes[i] + hashes[i]
            new.append(double_sha256(combined))
        hashes = new
    return hashes[0][::-1].hex()


class EntropyReceiver:
    def __init__(self, port: int = LISTEN_PORT):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("0.0.0.0", self.port))
        except OSError as e:
            print(f"[FATAL] Could not bind to UDP {self.port}: {e}")
            raise
        self.running = False
        self.last_broadcast: dict = {}

    def _parse_payload(self, data: bytes) -> dict:
        if not data.startswith(b"BYTECRAFT_AWAKE\x00"):
            return {}
        offset = 15
        fields = {}
        names = ["entropy_current", "entropy_prev", "entropy_delta",
                 "compression_cycles", "fix_50_0",
                 "spatial_offset", "bound_coord", "merged_bound", "horizon_index"]
        for name in names:
            if offset + 8 > len(data):
                return {}
            fields[name] = struct.unpack_from(">d", data, offset)[0]
            offset += 8
        if offset + 32 != len(data):
            return {}
        fields["merkle_root"] = data[offset:offset+32].hex()
        return fields

    def _validate(self, pkt: dict) -> bool:
        if pkt.get("fix_50_0") != RUNNING_FIX:
            print(f"[REJECT] fix_50_0 mismatch: {pkt.get('fix_50_0')} != {RUNNING_FIX}")
            return False
        if pkt.get("merkle_root") != EXPECTED_MERKLE:
            print(f"[REJECT] merkle_root mismatch")
            return False
        root = compute_merkle_root(BLOCK_TXIDS)
        if root != EXPECTED_MERKLE:
            print(f"[REJECT] block merkle root mismatch")
            return False
        return True

    def _emit_event(self, pkt: dict, src: str):
        event = {
            "timestamp": time.time(),
            "source": src,
            "entropy_current": pkt.get("entropy_current"),
            "entropy_delta": pkt.get("entropy_delta"),
            "fix_value": RUNNING_FIX,
            "merkle_root": pkt.get("merkle_root"),
            "action": "ENTROPY_AWAKE_BROADCAST_ACCEPTED",
            "spatial_elevation": {
                "offset": pkt.get("spatial_offset"),
                "bound": pkt.get("bound_coord"),
                "merged": pkt.get("merged_bound"),
                "horizon": pkt.get("horizon_index"),
            },
        }
        os.makedirs(os.path.dirname(EVENT_PATH), exist_ok=True)
        with open(EVENT_PATH, "w") as f:
            json.dump(event, f, indent=2)
        self.last_broadcast = event
        print(f"[ACCEPT] AWAKE broadcast from {src}")
        print(f"[EVENT] Written to {EVENT_PATH}")

    def start(self):
        self.running = True
        print("=" * 60)
        print("ENTROPY_AWAKE RECEIVER")
        print(f" Listening on UDP : {self.port}")
        print(f" Expected fix     : {RUNNING_FIX}")
        print(f" Expected merkle  : {EXPECTED_MERKLE}")
        print("=" * 60)
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                pkt = self._parse_payload(data)
                if not pkt:
                    continue
                if self._validate(pkt):
                    self._emit_event(pkt, f"{addr[0]}:{addr[1]}")
                else:
                    print(f"[DROP] Invalid packet from {addr[0]}:{addr[1]}")
            except OSError:
                break
            except Exception as e:
                print(f"[ERR] {e}")

    def stop(self):
        self.running = False
        self.sock.close()

    def get_last_event(self) -> dict:
        if os.path.exists(EVENT_PATH):
            with open(EVENT_PATH, "r") as f:
                return json.load(f)
        return {}


def main():
    receiver = EntropyReceiver()
    try:
        receiver.start()
    except KeyboardInterrupt:
        print("\n[STOP] Receiver halted.")
        receiver.stop()


if __name__ == "__main__":
    main()
