"""Pure-Python fallback kernel.

Same protocol as csharp/SeedKernel: JSONL in on stdin, JSONL out on stdout.
Used when `dotnet` is not available on PATH.

Each input line:
    {"id": <int>, "value": "<raw seed value>"}

Each output line:
    {"id": <int>, "key": "<base36 upper>", "block_size": <int>,
     "block_sha256": "<hex>", "engine": "python-stub"}
"""

from __future__ import annotations

import hashlib
import json
import sys

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _binary_block(value: str) -> bytes:
    """Deterministic 32-byte block: SHA-256 of the UTF-8 encoded value."""
    return hashlib.sha256(value.encode("utf-8", errors="replace")).digest()


def _base36(n: int, min_len: int = 13) -> str:
    if n == 0:
        return "0".rjust(min_len, "0")
    out: list[str] = []
    while n > 0:
        n, r = divmod(n, 36)
        out.append(_ALPHABET[r])
    key = "".join(reversed(out))
    return key.rjust(min_len, "0")


def _derive_key(block: bytes) -> str:
    """Reduce block bytes to a 13-char base36 alphanumeric key."""
    # Use the first 8 bytes as a big-endian unsigned int → base36.
    n = int.from_bytes(block[:8], "big", signed=False)
    return _base36(n, min_len=13)


def process(event: dict) -> dict:
    value = str(event.get("value", ""))
    block = _binary_block(value)
    return {
        "id": event.get("id"),
        "key": _derive_key(block),
        "block_size": len(block),
        "block_sha256": block.hex(),
        "engine": "python-stub",
    }


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({"error": "bad_json"}) + "\n")
            sys.stdout.flush()
            continue
        result = process(event)
        sys.stdout.write(json.dumps(result) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
