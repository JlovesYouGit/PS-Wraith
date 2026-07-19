"""Python-version detection + dispatch.

Given a directory, work out which Python interpreter should run scripts
under it, and (separately) which interpreters are available on the host.

Detection order (first hit wins):
  1. `.python-version`                 (pyenv-style, e.g. "3.11.7")
  2. `pyproject.toml` `requires-python` (PEP 621, e.g. ">=3.10,<3.13")
  3. Shebangs in `*.py` files          (e.g. "#!/usr/bin/env python3.11")
  4. `sys.version_info >= (…)` guards  (best-effort, weak signal)

Then `pick_interpreter(spec)` walks candidate binaries on PATH
(`python3.13`, `python3.12`, …, `python3`, `python`), calls each with
`--version`, and returns the newest match that satisfies `spec`.

Nothing installs anything. If no match is available, we return None and
the caller decides whether to fall back to `sys.executable`.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

# ---- Version tuple helpers ------------------------------------------------

_VER_RE = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")


def _parse_version(text: str) -> tuple[int, int, int] | None:
    m = _VER_RE.search(text or "")
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


# ---- Spec matching --------------------------------------------------------

@dataclass
class VersionSpec:
    """A resolved constraint. `exact` wins; otherwise (min, max) range.

    Both bounds are inclusive of major.minor (patch ignored for matching).
    """
    exact: tuple[int, int, int] | None = None
    min: tuple[int, int, int] | None = None
    max: tuple[int, int, int] | None = None
    source: str = "default"   # where the constraint came from

    def matches(self, v: tuple[int, int, int]) -> bool:
        if self.exact:
            return v[:2] == self.exact[:2]
        if self.min and v < (self.min[0], self.min[1], 0):
            return False
        if self.max and v > (self.max[0], self.max[1], 99):
            return False
        return True

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_requires_python(expr: str) -> VersionSpec:
    """Parse a PEP 440-lite requires-python string.

    Supported: `>=X.Y`, `>X.Y`, `<X.Y`, `<=X.Y`, `==X.Y`, comma-separated.
    Unsupported operators are ignored.
    """
    spec = VersionSpec(source="pyproject.requires-python")
    for part in (p.strip() for p in expr.split(",") if p.strip()):
        m = re.match(r"(==|>=|<=|>|<|~=)\s*(\d+)\.(\d+)(?:\.(\d+))?", part)
        if not m:
            continue
        op, mj, mn, pt = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4) or 0)
        v = (mj, mn, pt)
        if op == "==":
            spec.exact = v
        elif op in (">=", ">"):
            if spec.min is None or v > spec.min:
                spec.min = v
        elif op in ("<=", "<"):
            if spec.max is None or v < spec.max:
                spec.max = v
        elif op == "~=":
            spec.min = v
            spec.max = (mj, mn, 99)
    return spec


# ---- Detection ------------------------------------------------------------

_SHEBANG_RE = re.compile(rb"^#!.*?python(3(?:\.\d+)?)")


def detect_spec(directory: Path) -> VersionSpec:
    """Determine the required Python version for `directory`.

    Returns a `VersionSpec`; if nothing constrains it, spec is empty
    (matches any version) with source="default".
    """
    directory = directory.resolve()

    # 1) .python-version
    pv = directory / ".python-version"
    if pv.is_file():
        try:
            text = pv.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        except OSError:
            text = ""
        v = _parse_version(text)
        if v:
            return VersionSpec(exact=v, source=".python-version")

    # 2) pyproject.toml requires-python
    py = directory / "pyproject.toml"
    if py.is_file():
        try:
            content = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            content = ""
        m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if m:
            return _parse_requires_python(m.group(1))

    # 3) Shebangs (first .py file at any depth up to 3 levels)
    for path in _iter_py_files(directory, max_depth=3, limit=32):
        try:
            with path.open("rb") as f:
                first = f.readline()
        except OSError:
            continue
        m = _SHEBANG_RE.match(first)
        if m:
            v = _parse_version(m.group(1).decode())
            if v:
                # A shebang like "python3" without a minor pins nothing
                # specific; only accept if there's a minor.
                if v[1] != 0 or first.count(b".") >= 1:
                    return VersionSpec(exact=v, source=f"shebang:{path.name}")

    # 4) sys.version_info guard (weak) — look for `sys.version_info >= (3, N)`
    for path in _iter_py_files(directory, max_depth=3, limit=16):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"sys\.version_info\s*>=\s*\(\s*(\d+)\s*,\s*(\d+)", text)
        if m:
            v = (int(m.group(1)), int(m.group(2)), 0)
            return VersionSpec(min=v, source=f"guard:{path.name}")

    return VersionSpec(source="default")


def _iter_py_files(root: Path, max_depth: int, limit: int):
    """Yield up to `limit` .py files within `max_depth` levels."""
    yielded = 0
    stack = [(root, 0)]
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    while stack and yielded < limit:
        d, depth = stack.pop()
        if depth > max_depth:
            continue
        try:
            entries = list(d.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name in skip:
                    continue
                stack.append((e, depth + 1))
            elif e.is_file() and e.suffix == ".py":
                yield e
                yielded += 1
                if yielded >= limit:
                    return


# ---- Interpreter discovery ------------------------------------------------

# Candidate binary names, newest-first.
_CANDIDATES = (
    "python3.13", "python3.12", "python3.11", "python3.10",
    "python3.9", "python3.8", "python3", "python",
)


@dataclass
class Interpreter:
    binary: str
    path: str
    version: tuple[int, int, int]

    def to_dict(self) -> dict:
        return {"binary": self.binary, "path": self.path,
                "version": list(self.version),
                "version_str": ".".join(str(x) for x in self.version)}


def discover_interpreters() -> list[Interpreter]:
    """Return interpreters found on PATH, deduplicated by resolved path."""
    seen: dict[str, Interpreter] = {}
    for name in _CANDIDATES:
        binary = shutil.which(name)
        if not binary:
            continue
        resolved = str(Path(binary).resolve())
        if resolved in seen:
            continue
        try:
            r = subprocess.run(
                [binary, "--version"],
                capture_output=True, text=True, timeout=5, check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        version = _parse_version(r.stdout or r.stderr or "")
        if version is None:
            continue
        seen[resolved] = Interpreter(binary=name, path=resolved, version=version)
    # Sort newest-first.
    return sorted(seen.values(), key=lambda i: i.version, reverse=True)


def pick_interpreter(spec: VersionSpec,
                     interpreters: list[Interpreter] | None = None
                     ) -> Interpreter | None:
    """Return the newest interpreter satisfying `spec`, or None."""
    if interpreters is None:
        interpreters = discover_interpreters()
    for interp in interpreters:
        if spec.matches(interp.version):
            return interp
    return None


def current_interpreter() -> Interpreter:
    """The interpreter running this code — always available as a fallback."""
    v = sys.version_info
    return Interpreter(
        binary=Path(sys.executable).name,
        path=sys.executable,
        version=(v.major, v.minor, v.micro),
    )
