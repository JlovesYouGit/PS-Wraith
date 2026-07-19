"""Git-origin resolution for scanned files.

For each file we ask the local git repo (if any) which commit first
introduced it (`git log --diff-filter=A --follow`). This is best-effort:
files not under version control just get `origin = None`.
"""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def _find_repo_root(start: Path) -> Path | None:
    """Walk upward from `start` looking for a `.git` directory."""
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


@lru_cache(maxsize=4096)
def origin_for(path_str: str) -> dict | None:
    """Return {commit, timestamp, repo} for the first commit that added `path`,
    or None if the file is not in a git repo or git isn't available.
    """
    path = Path(path_str)
    if not path.exists():
        return None
    repo = _find_repo_root(path)
    if repo is None:
        return None
    try:
        rel = path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return None

    try:
        # --diff-filter=A: only "added" commits. --follow: track renames.
        # --reverse + head -1 would work but --reverse with --follow can
        # be inconsistent; we take the last (oldest) line of a non-reverse log.
        result = subprocess.run(
            [
                "git", "-C", str(repo),
                "log", "--diff-filter=A", "--follow",
                "--format=%H %ct", "--", rel,
            ],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    if not lines:
        return None
    # Oldest add-commit is the last entry (git log is newest-first).
    commit_sha, _, ts = lines[-1].partition(" ")
    try:
        timestamp = int(ts)
    except ValueError:
        timestamp = 0
    return {
        "commit": commit_sha,
        "timestamp": timestamp,
        "repo": repo.name,
    }


def attach_origins(seeds, workspace_root: Path) -> None:
    """Populate `origin` on each seed in-place.

    Cached per absolute path, so repeated seeds from the same file only
    invoke git once.
    """
    for seed in seeds:
        abs_path = (workspace_root / seed.address).resolve()
        seed.origin = origin_for(str(abs_path))
