"""Scanner: walks source directories and extracts seed records via regex.

Scanned files are treated as bytes. Nothing here imports, evaluates, or
executes scanned content — it is decoded as text and matched against a
fixed set of patterns.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable, Iterator

# Extensions we consider "text source". Everything else is skipped except
# files literally named SEED.
TEXT_EXTS = frozenset({
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".cs", ".csproj",
    ".cpp", ".cc", ".c", ".h", ".hpp",
    ".rs", ".go", ".java", ".kt", ".swift",
    ".json", ".toml", ".yaml", ".yml", ".xml", ".ini", ".cfg",
    ".md", ".txt", ".rst",
    ".sh", ".bat", ".ps1",
})

# Skip these directories entirely.
SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", "node_modules", "__pycache__",
    "bin", "obj", ".venv", "venv", "env", "target",
    "build", "dist", ".next", ".cache",
})

# Skip files larger than this (bytes). Snapshots are capped separately.
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB

# Regex patterns. Each yields (kind, value).
# Named groups: `val` = the seed value we care about.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # `seed = 1234` / `SEED = 0xabcd`
    ("assign_int",
     re.compile(r"\b(?:seed|SEED)\s*[:=]\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\b")),
    # `random.seed(1234)` / `np.random.seed(1234)` / `rng.seed(1234)`
    ("random_seed_call",
     re.compile(r"(?:random|np\.random|rng)\.seed\s*\(\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\s*\)")),
    # `Random(1234)` / `new Random(1234)` / `srand(1234)`
    ("prng_ctor",
     re.compile(r"\b(?:new\s+)?(?:Random|srand)\s*\(\s*(?P<val>-?\d+|0x[0-9a-fA-F]+)\s*\)")),
    # `SEED=abc123` env-style
    ("env_seed",
     re.compile(r"^\s*SEED\s*=\s*(?P<val>[A-Za-z0-9_\-\.]+)\s*$", re.MULTILINE)),
    # Standalone SHA-ish hex string (>=32 chars). Word-bounded to avoid
    # long non-hex runs.
    ("hex_hash",
     re.compile(r"\b(?P<val>[0-9a-fA-F]{32,128})\b")),
    # Tagged seed comments: `# seed: value` or `// seed: value`
    ("tagged_comment",
     re.compile(r"(?:#|//)\s*seed\s*:\s*(?P<val>[A-Za-z0-9_\-\.:/+=]+)")),
)


@dataclass
class Seed:
    """One seed occurrence in the source trees."""

    address: str            # workspace-relative path, forward slashes
    line: int               # 1-based line number; 0 for whole-file (SEED files)
    kind: str               # pattern name
    value: str              # raw matched value, capped
    value_sha256: str       # sha256(value.encode())
    file_sha256: str        # sha256 of the containing file (for provenance)
    origin: dict | None = field(default=None)  # populated by tracer

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _iter_source_files(roots: Iterable[Path]) -> Iterator[Path]:
    """Yield candidate files under each root, skipping SKIP_DIRS."""
    for root in roots:
        if not root.exists():
            continue
        for path in _walk(root):
            yield path


def _walk(root: Path) -> Iterator[Path]:
    # Manual walk so we can prune SKIP_DIRS efficiently.
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except (PermissionError, OSError):
            continue
        for entry in entries:
            name = entry.name
            if entry.is_dir():
                if name in SKIP_DIRS:
                    continue
                stack.append(entry)
            elif entry.is_file():
                yield entry


def _is_candidate(path: Path) -> bool:
    if path.name == "SEED":
        return True
    if path.suffix.lower() in TEXT_EXTS:
        return True
    return False


def _read_text(path: Path) -> str | None:
    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size > MAX_FILE_BYTES:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _line_of(text: str, offset: int) -> int:
    """1-based line number for a byte offset into `text`."""
    return text.count("\n", 0, offset) + 1


def _extract_from_text(text: str) -> Iterator[tuple[str, str, int]]:
    """Yield (kind, value, line) for each pattern hit in `text`."""
    for kind, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            value = m.group("val")
            if not value:
                continue
            # Sanity clamp: values longer than 512 chars are ignored to
            # avoid pathological matches.
            if len(value) > 512:
                continue
            yield kind, value, _line_of(text, m.start("val"))


def scan(roots: Iterable[Path], workspace_root: Path) -> list[Seed]:
    """Scan `roots` and return a list of seed records.

    `workspace_root` is used only to compute display-friendly relative
    addresses. It never affects which files are read.
    """
    seeds: list[Seed] = []
    for path in _iter_source_files(roots):
        if not _is_candidate(path):
            continue

        try:
            raw = path.read_bytes() if path.name == "SEED" else None
        except OSError:
            raw = None

        if path.name == "SEED":
            # Whole-file SEED files: value = file contents (capped).
            if raw is None or len(raw) > MAX_FILE_BYTES:
                continue
            value = raw.decode("utf-8", errors="replace").strip()
            if not value:
                continue
            if len(value) > 512:
                value = value[:512]
            address = _rel(path, workspace_root)
            seeds.append(Seed(
                address=address,
                line=0,
                kind="seed_file",
                value=value,
                value_sha256=_sha256_str(value),
                file_sha256=_sha256_bytes(raw),
            ))
            continue

        text = _read_text(path)
        if text is None:
            continue
        file_sha = _sha256_str(text)
        address = _rel(path, workspace_root)

        seen_here: set[tuple[str, str, int]] = set()
        for kind, value, line in _extract_from_text(text):
            key = (kind, value, line)
            if key in seen_here:
                continue
            seen_here.add(key)
            seeds.append(Seed(
                address=address,
                line=line,
                kind=kind,
                value=value,
                value_sha256=_sha256_str(value),
                file_sha256=file_sha,
            ))

    return seeds


def _rel(path: Path, workspace_root: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
