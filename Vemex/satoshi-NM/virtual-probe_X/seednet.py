import hashlib
import os
import re
from dataclasses import dataclass, field
from typing import Any


BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TEXT_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".cs", ".csproj", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".rs", ".go", ".java", ".kt", ".swift",
    ".json", ".toml", ".yaml", ".yml", ".xml", ".ini", ".cfg",
    ".md", ".txt", ".rst", ".sh", ".bat", ".ps1",
}
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__",
    "bin", "obj", ".venv", "venv", "env", "target",
    "build", "dist", ".next", ".cache",
}
MAX_FILE_BYTES = 2 * 1024 * 1024

_PATTERNS = [
    ("assign_int", re.compile(r"\b(?:seed|SEED)\s*[:=]\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\b")),
    ("random_seed_call", re.compile(r"(?:random|np\.random|rng)\.seed\s*\(\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\s*\)")),
    ("prng_ctor", re.compile(r"\b(?:new\s+)?(?:Random|srand)\s*\(\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\s*\)")),
    ("env_seed", re.compile(r"^\s*SEED\s*=\s*(?P<val>[A-Za-z0-9_\-\.]+)\s*$", re.MULTILINE)),
    ("hex_hash", re.compile(r"\b(?P<val>[0-9a-fA-F]{32,128})\b")),
    ("tagged_comment", re.compile(r"(?:#|//)\s*seed\s*:\s*(?P<val>[A-Za-z0-9_\-\.:/+=]+)")),
]


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _base36_encode(num: int, min_len: int = 13) -> str:
    if num == 0:
        encoded = "0"
    else:
        encoded = ""
        while num > 0:
            num, rem = divmod(num, 36)
            encoded = BASE36_ALPHABET[rem] + encoded
    return encoded.rjust(min_len, "0")


def derive_commitment(value: str) -> dict[str, Any]:
    block = hashlib.sha256(value.encode()).digest()
    block_sha256 = hashlib.sha256(value.encode()).hexdigest()
    uint64 = int.from_bytes(block[:8], byteorder="big")
    key = _base36_encode(uint64, 13)
    return {
        "key": key,
        "block_size": len(block),
        "block_sha256": block_sha256,
    }


@dataclass
class Seed:
    address: str
    line: int
    kind: str
    value: str
    value_sha256: str
    file_sha256: str
    origin: dict[str, Any] | None = None
    commitment: dict[str, Any] | None = None


@dataclass
class Threat:
    value_sha256: str
    value_preview: str
    occurrences: int
    canonical: dict[str, Any]
    forward_trace: list[dict[str, Any]] = field(default_factory=list)
    reverse_trace: list[dict[str, Any]] = field(default_factory=list)


def _is_candidate(path: str) -> bool:
    if os.path.basename(path) == "SEED":
        return True
    _, ext = os.path.splitext(path)
    return ext.lower() in TEXT_EXTS


def _walk(root: str):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            yield os.path.join(dirpath, fname)


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _extract_from_text(path: str, text: str) -> list[Seed]:
    seeds: list[Seed] = []
    seen_here: set[tuple[str, str, int]] = set()
    file_sha256 = _sha256_bytes(text.encode())

    for kind, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            val = m.group("val")
            line = _line_of(text, m.start())
            if len(val) > 512:
                continue
            key = (kind, val, line)
            if key in seen_here:
                continue
            seen_here.add(key)
            seeds.append(Seed(
                address=path,
                line=line,
                kind=kind,
                value=val,
                value_sha256=_sha256_str(val),
                file_sha256=file_sha256,
            ))

    return seeds


def _extract_seed_file(path: str, text: str) -> list[Seed]:
    val = text.strip()[:512]
    if not val:
        return []
    return [Seed(
        address=path,
        line=0,
        kind="seed_file",
        value=val,
        value_sha256=_sha256_str(val),
        file_sha256=_sha256_bytes(text.encode()),
    )]


def scan_dir(root: str) -> list[Seed]:
    seeds: list[Seed] = []
    for path in _walk(root):
        if not _is_candidate(path):
            continue
        try:
            st = os.stat(path)
        except OSError:
            continue
        if st.st_size > MAX_FILE_BYTES:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue

        if os.path.basename(path) == "SEED":
            seeds.extend(_extract_seed_file(path, text))
        else:
            seeds.extend(_extract_from_text(path, text))

    for seed in seeds:
        seed.commitment = derive_commitment(seed.value)

    return seeds


def detect_threats(seeds: list[Seed]) -> list[Threat]:
    groups: dict[str, list[Seed]] = {}
    for seed in seeds:
        groups.setdefault(seed.value_sha256, []).append(seed)

    threats: list[Threat] = []
    for sha, group in groups.items():
        if len(group) < 2:
            continue

        def sort_key(s: Seed):
            ts = s.origin.get("timestamp", 2**62) if s.origin else 2**62
            return (ts, s.address, s.line)

        ordered = sorted(group, key=sort_key)
        canonical_seed = ordered[0]
        canonical = {
            "address": canonical_seed.address,
            "line": canonical_seed.line,
            "kind": canonical_seed.kind,
            "value": canonical_seed.value[:64],
            "commitment": canonical_seed.commitment,
            "origin": canonical_seed.origin,
        }
        forward = [{"index": i, "address": s.address, "line": s.line, "kind": s.kind, "commitment": s.commitment} for i, s in enumerate(ordered)]
        reverse = [{"index": i, "address": s.address, "line": s.line, "kind": s.kind, "commitment": s.commitment} for i, s in enumerate(reversed(ordered))]
        threats.append(Threat(
            value_sha256=sha,
            value_preview=canonical_seed.value[:64],
            occurrences=len(ordered),
            canonical=canonical,
            forward_trace=forward,
            reverse_trace=reverse,
        ))

    threats.sort(key=lambda t: (-t.occurrences, t.canonical["address"]))
    return threats


def summary(seeds: list[Seed], threats: list[Threat]) -> dict[str, Any]:
    kinds: dict[str, int] = {}
    for s in seeds:
        kinds[s.kind] = kinds.get(s.kind, 0) + 1
    return {
        "seed_count": len(seeds),
        "threat_count": len(threats),
        "kinds": kinds,
    }
