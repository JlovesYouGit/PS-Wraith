"""seed_sampler package.

Read-only indexer + async runner for the sibling source trees.
See the top-level README for scope and constraints.
"""

__version__ = "0.1.0"

# Absolute path to <workspace>/seed-sampler (parent of this package's parent).
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent  # .../seed-sampler
WORKSPACE_ROOT = PROJECT_ROOT.parent       # .../superseedsampler
DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
TRACKER_PATH = DATA_DIR / "tracker.json"

# The three source trees this tool observes. Paths are read-only.
SOURCE_DIRS = (
    WORKSPACE_ROOT / "zero-brain",
    WORKSPACE_ROOT / "The-Crown",
    WORKSPACE_ROOT / "SEC-unit-core-sort",
)

__all__ = [
    "PACKAGE_ROOT",
    "PROJECT_ROOT",
    "WORKSPACE_ROOT",
    "DATA_DIR",
    "SNAPSHOT_DIR",
    "TRACKER_PATH",
    "SOURCE_DIRS",
    "__version__",
]
