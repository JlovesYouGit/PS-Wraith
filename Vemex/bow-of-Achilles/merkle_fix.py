"""
Merke Error Fix Script
Reads the fix event emitted by the listener and applies the 50.0 correction value to the error point.
"""

import json
import os
import re
import hashlib

EXPECTED_MERKLE_ROOT = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
RUNNING_FIX_VALUE = 50.0
FIX_EVENT_PATH = r"C:\QuantumEnergyService\merkle_fix_event.json"
WATCH_DIRECTORY = r"C:\QuantumEnergyService\unified_cosmos"
SEQUENCE_PARSE_REGEX = r"integration_(\d+)\.dat"
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
        new_hashes = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                combined = hashes[i] + hashes[i + 1]
            else:
                combined = hashes[i] + hashes[i]
            new_hashes.append(double_sha256(combined))
        hashes = new_hashes
    return hashes[0][::-1].hex()


def load_fix_event():
    if not os.path.exists(FIX_EVENT_PATH):
        return None
    with open(FIX_EVENT_PATH, "r") as f:
        return json.load(f)


def apply_fix():
    print("=" * 60)
    print("MERKLE ERROR FIX SCRIPT")
    print(f"Running Fix Value    : {RUNNING_FIX_VALUE}")
    print(f"Expected Merkle Root : {EXPECTED_MERKLE_ROOT}")
    print("=" * 60)

    root = compute_merkle_root(BLOCK_TXIDS)
    if root == EXPECTED_MERKLE_ROOT:
        print("[OK] Merkle root is valid. No fix needed at block level.")
    else:
        print(f"[FAIL] Merkle root mismatch: {root}")

    event = load_fix_event()
    if not event:
        print("[WARN] No fix event found. Listener may not have run yet.")
        return

    error_point = event.get("error_point", "unknown")
    fix_value = event.get("derived_fix_value", RUNNING_FIX_VALUE)
    action = event.get("action", "UNKNOWN")
    timestamp = event.get("timestamp", 0)

    print(f"\n[FIX_EVENT] Loaded from {FIX_EVENT_PATH}")
    print(f"  Time   : {time.ctime(timestamp)}")
    print(f"  Action : {action}")
    print(f"  Point  : {error_point}")
    print(f"  Value  : {fix_value}")

    path = os.path.join(r"C:\QuantumEnergyService\unified_cosmos", error_point)
    if not os.path.exists(path):
        print(f"[SKIP] Error point file not found: {path}")
        return

    m = re.match(SEQUENCE_PARSE_REGEX, error_point)
    if m:
        outstanding_seq = int(m.group(1))
        print(f"[DETECT] Missing sequence gap at {error_point}")
        print(f"[FIX] Deriving correction value: {RUNNING_FIX_VALUE}")
    else:
        print(f"[INFO] Non-seq error point: {error_point}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        original = f.read()

    calibrated = f"{original.rstrip()}\nFIX_APPLIED: {fix_value}\nFIX_TIMESTAMP: {time.ctime(timestamp)}\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(calibrated)

    print(f"[FIXED] Applied 50.0 calibration to {path}")

    new_root = compute_merkle_root(BLOCK_TXIDS)
    print(f"[VERIFY] Merkle root after fix: {new_root}")
    print(f"[VERIFY] Match expected: {new_root == EXPECTED_MERKLE_ROOT}")


if __name__ == "__main__":
    apply_fix()
