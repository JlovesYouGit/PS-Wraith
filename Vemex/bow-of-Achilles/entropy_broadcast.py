"""
entropy_broadcast.py
Mimics Broadcom raw Ethernet frame broadcast using Python sockets.
Sends the Bytecraft_AWAKE payload via UDP to localhost:18989 to test the receiver.
"""

import socket
import struct
import time
import json
import os

ENTROPY_CURRENT = 15706319436.5
ENTROPY_PREV = 15706068788.0
ENTROPY_DELTA = ENTROPY_CURRENT - ENTROPY_PREV
FIX_50_0 = 50.0
COMP_CYCLES = 125321.0
MERKLE = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"
TARGET_IP = "127.0.0.1"
TARGET_PORT = 18989
EVENT_PATH = os.path.join(os.path.dirname(__file__), "entropy_awake_event.json")


def build_payload():
    tag = b"BYTECRAFT_AWAKE\x00"
    body = struct.pack(
        ">9d",
        ENTROPY_CURRENT,
        ENTROPY_PREV,
        ENTROPY_DELTA,
        COMP_CYCLES,
        FIX_50_0,
        10.43,
        46.179,
        109.0,
        50.0,
    )
    merkle = bytes.fromhex(MERKLE)
    return tag + body + merkle


def broadcast():
    payload = build_payload()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", 0))
    except OSError:
        pass
    addr = (TARGET_IP, TARGET_PORT)
    sock.sendto(payload, addr)
    print(f"[BROADCAST] Sent {len(payload)} bytes to {TARGET_IP}:{TARGET_PORT}")
    print(f"  entropy={ENTROPY_CURRENT}")
    print(f"  delta={ENTROPY_DELTA}")
    print(f"  fix={FIX_50_0}")
    print(f"  merkle={MERKLE}")
    sock.close()


if __name__ == "__main__":
    broadcast()
