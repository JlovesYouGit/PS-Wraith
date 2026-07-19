"""
probe_sequence.py
Scans the integration file probe-sequence in C:\\QuantumEnergyService\\unified_cosmos
for anomalies (breaks, size changes, missing steps) and broadcasts the 50.0
fix value via the entropy system when a deviation is found.

Intended use: continuous integrity monitoring of the integration stream.
"""

import os
import re
import struct
import socket
import json
import time
import hashlib
from datetime import datetime

# --- Configuration ---
WATCH_DIR = r"C:\QuantumEnergyService\unified_cosmos"
SEQUENCE_PATTERN = re.compile(r"integration_(\d+)\.dat")
FIX_VALUE = 50.0
ENTROPY_CURRENT = 15706319436.5
ENTROPY_PREV = 15706068788.0
ENTROPY_DELTA = ENTROPY_CURRENT - ENTROPY_PREV
MERKLE_ROOT = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
BROADCAST_IP = "10.43.46.109"
BROADCAST_PORT = 18989
EVENT_LOG = os.path.join(os.path.dirname(WATCH_DIR), "probe_sequence_event.json")
BLOCK_TXIDS = [
    "fb6fd78b6ce1770644e820ce1b27547804f9a52ebb24dd07964b3262440a9239",
    "1fbbf28c19a5bd2034dff97ad55949f3c312f18f9bdd160494d650d754f2bd02",
    "66f2dc47f42eb408d2450a0b6b0ee27604b3eff079dfefff6d4693eebbad152c",
    "6c3b1b90c3c46b8ede703811aedf546eb869531276b82f181c25014799fd552e",
    "733d85cc13fbd42519309023b3f96ad91861abbae14e19c4d99d61f5cf01031f",
    "6e0d7e0cd0e62b6ec39a7260280bc8a330c44ff8fc71d5aa8acfe2ec20d944e0",
]


def compute_merkle_root(txids):
    def double_sha256(data):
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()
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


def pack_double_be(d):
    import struct
    return struct.pack(">d", d)


def build_broadcast_payload(anomaly_seq, anomaly_file, anomaly_desc, anomaly_size):
    tag = b"BYTECRAFT_PROBE\x00"
    body = struct.pack(
        ">12d",
        ENTROPY_CURRENT,       # 0
        ENTROPY_PREV,          # 1
        ENTROPY_DELTA,         # 2
        float(anomaly_seq),    # 3: sequence number where anomaly occurred
        FIX_VALUE,             # 4: 50.0 fix value
        10.43,                 # 5: spatial offset
        46.179,                # 6: bound coordinate
        109.0,                 # 7: merged bound
        50.0,                  # 8: horizon index
        float(anomaly_size),   # 9: size at anomaly
        125321.0,              # 10: compression cycles
        time.time(),           # 11: timestamp
    )
    merkle = bytes.fromhex(MERKLE_ROOT)
    return tag + body + merkle


def broadcast_probe_alert(anomaly_seq, anomaly_file, anomaly_desc, anomaly_size):
    payload = build_broadcast_payload(anomaly_seq, anomaly_file, anomaly_desc, anomaly_size)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", 0))
    except OSError:
        pass
    addr = (BROADCAST_IP, BROADCAST_PORT)
    sock.sendto(payload, addr)
    print(f"[BROADCAST] Probe anomaly alert sent to {BROADCAST_IP}:{BROADCAST_PORT}")
    print(f"  seq={anomaly_seq}, file={anomaly_file}, size={anomaly_size}, desc={anomaly_desc}")
    sock.close()
    return payload


def scan_probe_sequence(directory=WATCH_DIR):
    if not os.path.isdir(directory):
        print(f"[ERROR] Directory not found: {directory}")
        return []

    files = [f for f in os.listdir(directory) if SEQUENCE_PATTERN.match(f)]
    if not files:
        print("[WARN] No integration files found")
        return []

    seqs = []
    for f in files:
        m = SEQUENCE_PATTERN.match(f)
        if m:
            seqs.append((int(m.group(1)), f, os.path.getsize(os.path.join(directory, f))))
    seqs.sort(key=lambda x: x[0])

    anomalies = []
    prev_seq = None
    prev_size = None

    for seq, fname, size in seqs:
        if prev_seq is not None:
            expected = prev_seq + 1
            if seq != expected:
                anomalies.append({
                    "type": "sequence_break",
                    "seq": seq,
                    "expected": expected,
                    "file": fname,
                    "size": size,
                    "prev_seq": prev_seq,
                    "prev_size": prev_size,
                    "timestamp": datetime.now().isoformat(),
                })
                print(f"[ANOMALY] Sequence break at {fname}: expected {expected}, got {seq}")

        if prev_size is not None and size != prev_size:
            anomalies.append({
                "type": "size_change",
                "seq": seq,
                "file": fname,
                "size": size,
                "prev_size": prev_size,
                "timestamp": datetime.now().isoformat(),
            })
            print(f"[ANOMALY] Size change at {fname}: prev={prev_size}, curr={size}")

        prev_seq = seq
        prev_size = size

    return anomalies


def write_event_log(anomalies, action_taken="SCAN_ONLY"):
    root = compute_merkle_root(BLOCK_TXIDS)
    event = {
        "timestamp": time.time(),
        "action": action_taken,
        "merkle_root": root,
        "entropy_current": ENTROPY_CURRENT,
        "entropy_delta": ENTROPY_DELTA,
        "fix_value": FIX_VALUE,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }
    os.makedirs(os.path.dirname(EVENT_LOG), exist_ok=True)
    with open(EVENT_LOG, "w") as f:
        json.dump(event, f, indent=2)
    print(f"[LOG] Event written to {EVENT_LOG}")
    return event


def main():
    print("=" * 60)
    print("PROBE SEQUENCE SCANNER")
    print(f" Directory        : {WATCH_DIR}")
    print(f" Fix value        : {FIX_VALUE}")
    print(f" Entropy delta    : {ENTROPY_DELTA}")
    print(f" Merkle root      : {MERKLE_ROOT}")
    print("=" * 60)

    anomalies = scan_probe_sequence()
    if not anomalies:
        print("[OK] Probe sequence is clean")
        write_event_log([], "SCAN_CLEAN")
        return

    print(f"\n[FOUND] {len(anomalies)} anomaly/anomalies")
    latest = anomalies[-1]
    seq = latest.get("seq", 0)
    fname = latest.get("file", "unknown")
    size = latest.get("size", 0)

    print(f"[ACTION] Broadcasting fix for anomaly at seq={seq}, file={fname}")
    payload = broadcast_probe_alert(seq, fname, latest.get("type", "unknown"), size)

    event = write_event_log(anomalies, "BROADCAST_FIX_APPLIED")
    event["broadcast_payload_hex"] = payload.hex()[:64] + "..."
    with open(EVENT_LOG, "w") as f:
        json.dump(event, f, indent=2)

    print("[DONE] Probe sequence scan complete")


if __name__ == "__main__":
    main()
