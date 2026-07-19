"""
Quantum Merkle Listener
Detects errors via file change listener and derives 50.0 as the running fix value.
Optionally starts the UDP entropy receiver for the Bytecraft_AWAKE broadcast.
"""

import hashlib
import os
import re
import time
import json
import threading

BLOCK_TXIDS = [
    "fb6fd78b6ce1770644e820ce1b27547804f9a52ebb24dd07964b3262440a9239",
    "1fbbf28c19a5bd2034dff97ad55949f3c312f18f9bdd160494d650d754f2bd02",
    "66f2dc47f42eb408d2450a0b6b0ee27604b3eff079dfefff6d4693eebbad152c",
    "6c3b1b90c3c46b8ede703811aedf546eb869531276b82f181c25014799fd552e",
    "733d85cc13fbd42519309023b3f96ad91861abbae14e19c4d99d61f5cf01031f",
    "6e0d7e0cd0e62b6ec39a7260280bc8a330c44ff8fc71d5aa8acfe2ec20d944e0",
]

EXPECTED_MERKLE_ROOT = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
RUNNING_FIX_VALUE = 50.0
WATCH_DIRECTORY = r"C:\QuantumEnergyService\unified_cosmos"
SEQUENCE_PARSE_REGEX = r"integration_(\d+)\.dat"
ENTROPY_LISTEN_PORT = 18989


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compute_merkle_root(txids: list) -> str:
    hashes = [bytes.fromhex(txid)[::-1] for txid in txids]
    while len(hashes) > 1:
        new_hashes = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                combined = hashes[i] + hashes[i + 1]
            else:
                combined = hashes[i] + hashes[i]
            new_hashes.append(double_sha256(combined))
        hashes = new_hashes
    return hashes[0][::-1].hex()


class QuantumIntegrityError(Exception):
    def __init__(self, message: str, error_point: str, fix_value: float):
        super().__init__(message)
        self.error_point = error_point
        self.fix_value = fix_value


class MerkleListener:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.file_history: dict[str, float] = {}
        self.size_pattern: list[int] = []
        self.error_detected = False
        self._lock = threading.Lock()
        self._known_files: set[str] = set()
        self._entropy_receiver = None
        self._entropy_thread = None

    def _validate_merkle(self):
        root = compute_merkle_root(BLOCK_TXIDS)
        if root != EXPECTED_MERKLE_ROOT:
            raise QuantumIntegrityError(
                "Merkle root mismatch",
                error_point="block_header",
                fix_value=RUNNING_FIX_VALUE,
            )
        return True

    def _check_sequence_violation(self, filename: str, expected_next: int) -> bool:
        m = re.match(SEQUENCE_PARSE_REGEX, filename)
        if not m:
            return True
        seq = int(m.group(1))
        return seq != expected_next

    def _handle_change(self, filepath: str):
        if not filepath.endswith(".dat"):
            return

        filename = os.path.basename(filepath)
        try:
            with self._lock:
                if self.error_detected:
                    return
                self._validate_merkle()

            if not re.match(SEQUENCE_PARSE_REGEX, filename):
                print(f"[WARN] Non-seq file ignored: {filename}")
                return

            if self.size_pattern:
                expected_next = self.size_pattern[-1] + 1
            else:
                expected_next = 1

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if self._check_sequence_violation(filename, expected_next):
                with self._lock:
                    self.error_detected = True
                raise QuantumIntegrityError(
                    f"Sequence pattern violation at {filename}: expected integration_{expected_next}.dat",
                    error_point=filename,
                    fix_value=RUNNING_FIX_VALUE,
                )

            m = re.match(SEQUENCE_PARSE_REGEX, filename)
            actual_seq = int(m.group(1)) if m else 0
            self.size_pattern.append(actual_seq)
            self.file_history[filename] = time.time()
            print(f"[LISTEN] {filename} | seq={actual_seq} | pattern={self.size_pattern}")

        except QuantumIntegrityError as e:
            print(f"\n[ERROR] Merkle listener detected integrity failure: {e}")
            print(f"[FIX] Apply derived value: {e.fix_value} at error_point={e.error_point}")
            self._emit_fix_event(e.error_point, e.fix_value)

    def _emit_fix_event(self, error_point: str, fix_value: float):
        event = {
            "timestamp": time.time(),
            "error_point": error_point,
            "derived_fix_value": fix_value,
            "merkle_root": EXPECTED_MERKLE_ROOT,
            "action": "APPLY_50_0_CORRECTION",
        }
        out_path = os.path.join(os.path.dirname(WATCH_DIRECTORY), "merkle_fix_event.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(event, f, indent=2)
        print(f"[FIX EMITTED] {out_path}")

    def _load_entropy_receiver(self):
        try:
            from entropy_receiver import EntropyReceiver
            self._entropy_receiver = EntropyReceiver(port=ENTROPY_LISTEN_PORT)
            self._entropy_thread = threading.Thread(
                target=self._entropy_receiver.start, daemon=True
            )
            self._entropy_thread.start()
            print(f"[ENTROPY RECEIVER] Thread started on UDP {ENTROPY_LISTEN_PORT}")
        except Exception as e:
            print(f"[WARN] Could not start entropy receiver: {e}")

    def start(self):
        print("=" * 60)
        print("QUANTUM MERKLE LISTENER")
        print(f" Expected Merkle Root : {EXPECTED_MERKLE_ROOT}")
        print(f" Running Fix Value    : {RUNNING_FIX_VALUE}")
        print(f" Watch Directory      : {self.watch_dir}")
        print("=" * 60)

        if not os.path.isdir(self.watch_dir):
            os.makedirs(self.watch_dir)
            print(f"[INIT] Created watch directory: {self.watch_dir}")

        self._load_entropy_receiver()

        self._known_files = set(os.listdir(self.watch_dir))
        try:
            while True:
                current_files = set(os.listdir(self.watch_dir))
                for filename in current_files - self._known_files:
                    filepath = os.path.join(self.watch_dir, filename)
                    self._handle_change(filepath)
                for filename in current_files:
                    if filename not in self._known_files:
                        continue
                    filepath = os.path.join(self.watch_dir, filename)
                    try:
                        size = os.path.getsize(filepath)
                    except OSError:
                        continue
                    if self.size_pattern and size != self.size_pattern[-1]:
                        self._handle_change(filepath)
                self._known_files = current_files
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[LISTENER] Stopped.")
            if self._entropy_receiver:
                self._entropy_receiver.stop()


if __name__ == "__main__":
    listener = MerkleListener(WATCH_DIRECTORY)
    listener.start()
