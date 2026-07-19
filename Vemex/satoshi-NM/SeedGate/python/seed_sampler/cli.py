"""CLI: scan / query / run / versions.

Usage:
    python -m seed_sampler.cli scan
    python -m seed_sampler.cli query --duplicates
    python -m seed_sampler.cli query --value <sha256_prefix>
    python -m seed_sampler.cli query --path '<fnmatch glob>'
    python -m seed_sampler.cli query --origin <commit_prefix>
    python -m seed_sampler.cli query --kind <kind>
    python -m seed_sampler.cli query --summary
    python -m seed_sampler.cli versions [--dir <path>]
    python -m seed_sampler.cli run [--limit N]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import SOURCE_DIRS, TRACKER_PATH, WORKSPACE_ROOT
from . import scanner, tracer, detector, tracker as tracker_mod, pyversion, runner


def _cmd_scan(args: argparse.Namespace) -> int:
    roots = [Path(p) for p in args.root] if args.root else list(SOURCE_DIRS)
    missing = [str(r) for r in roots if not r.exists()]
    if missing:
        print(f"warning: missing roots: {missing}", file=sys.stderr)

    print(f"scanning {len(roots)} root(s)...", file=sys.stderr)
    seeds = scanner.scan(roots, WORKSPACE_ROOT)
    print(f"  found {len(seeds)} seed record(s)", file=sys.stderr)

    if not args.no_git:
        print("resolving git origins...", file=sys.stderr)
        tracer.attach_origins(seeds, WORKSPACE_ROOT)

    print("detecting duplicates...", file=sys.stderr)
    threats = detector.detect(seeds)
    print(f"  {len(threats)} threat group(s)", file=sys.stderr)

    doc = tracker_mod.build(seeds, threats)
    tracker_mod.save(doc, TRACKER_PATH)
    snap_count = tracker_mod.write_snapshots(threats)
    print(f"wrote {TRACKER_PATH} ({len(seeds)} seeds, {len(threats)} threats)")
    print(f"wrote {snap_count} snapshot(s)")
    return 0


def _print_seeds(seeds: list[dict], limit: int) -> None:
    for s in seeds[:limit]:
        origin = s.get("origin") or {}
        commit = (origin.get("commit") or "")[:8] or "-"
        print(f"  [{s['kind']:20s}] {s['value_sha256'][:12]}  "
              f"{s['address']}:{s['line']}  ({commit})")
    if len(seeds) > limit:
        print(f"  ... and {len(seeds) - limit} more (use --limit)")


def _cmd_query(args: argparse.Namespace) -> int:
    doc = tracker_mod.load(TRACKER_PATH)
    if not doc.get("seeds") and not doc.get("threats"):
        print("tracker is empty; run `scan` first.", file=sys.stderr)
        return 1

    if args.summary:
        s = tracker_mod.summary(doc)
        print(json.dumps(s, indent=2))
        return 0

    if args.duplicates:
        threats = tracker_mod.q_duplicates(doc)
        print(f"{len(threats)} threat group(s)")
        for t in threats[:args.limit]:
            print(f"  {t['value_sha256'][:12]}  occurrences={t['occurrences']}  "
                  f"canonical={t['canonical'].get('address')}:{t['canonical'].get('line')}")
        if args.verbose and threats:
            print(json.dumps(threats[:args.limit], indent=2))
        return 0

    hits: list[dict] = []
    if args.value:
        hits = tracker_mod.q_by_value_prefix(doc, args.value)
    elif args.path:
        hits = tracker_mod.q_by_path_glob(doc, args.path)
    elif args.origin:
        hits = tracker_mod.q_by_origin(doc, args.origin)
    elif args.kind:
        hits = tracker_mod.q_by_kind(doc, args.kind)
    else:
        print("specify one of: --duplicates, --summary, --value, --path, --origin, --kind",
              file=sys.stderr)
        return 2

    print(f"{len(hits)} hit(s)")
    _print_seeds(hits, args.limit)
    if args.verbose:
        print(json.dumps(hits[:args.limit], indent=2))
    return 0


def _cmd_versions(args: argparse.Namespace) -> int:
    interps = pyversion.discover_interpreters()
    print("Available interpreters:")
    if not interps:
        print("  (none discovered; falling back to sys.executable)")
        cur = pyversion.current_interpreter()
        print(f"  * {cur.binary}  {cur.path}  {'.'.join(str(x) for x in cur.version)}")
    for i in interps:
        v = ".".join(str(x) for x in i.version)
        print(f"  * {i.binary:14s}  {v:8s}  {i.path}")

    print()

    dirs: list[Path]
    if args.dir:
        dirs = [Path(args.dir)]
    else:
        dirs = [Path(p) for p in SOURCE_DIRS if p.exists()]
        # Also scan direct subdirectories one level down.
        for root in list(dirs):
            for child in sorted(root.iterdir()):
                if child.is_dir() and (
                    (child / ".python-version").is_file()
                    or (child / "pyproject.toml").is_file()
                ):
                    dirs.append(child)

    print("Per-directory Python version detection:")
    for d in dirs:
        spec = pyversion.detect_spec(d)
        picked = pyversion.pick_interpreter(spec, interps)
        picked_str = (f"{picked.binary} ({'.'.join(str(x) for x in picked.version)})"
                      if picked else "NO MATCH")
        rel = _try_relative(d)
        print(f"  {rel}")
        print(f"    spec:   {spec.to_dict()}")
        print(f"    picked: {picked_str}")
    return 0


def _try_relative(p: Path) -> str:
    try:
        return p.resolve().relative_to(WORKSPACE_ROOT.resolve()).as_posix()
    except ValueError:
        return str(p)


def _cmd_run(args: argparse.Namespace) -> int:
    # For xpub transport, auto-enable connection (reads ADR/ADR2 from .env)
    connection_established = args.connection_established
    if args.transport == "xpub":
        connection_established = True

    result = runner.run(
        limit=args.limit,
        connection_mac=args.connection_mac,
        connection_port=args.connection_port,
        connection_established=connection_established,
        transport=args.transport,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("errors", 0) == 0 else 1



def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="seed_sampler",
                                description="Local seed indexer + async kernel pipeline.")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("scan", help="Walk source dirs and build tracker.json")
    ps.add_argument("--root", action="append",
                    help="Override root(s); repeatable. Default: the three source dirs.")
    ps.add_argument("--no-git", action="store_true",
                    help="Skip git-origin resolution (much faster).")
    ps.set_defaults(func=_cmd_scan)

    pq = sub.add_parser("query", help="Query the tracker")
    pq.add_argument("--summary", action="store_true")
    pq.add_argument("--duplicates", action="store_true")
    pq.add_argument("--value", help="value_sha256 prefix")
    pq.add_argument("--path", help="fnmatch glob against address")
    pq.add_argument("--origin", help="commit SHA prefix")
    pq.add_argument("--kind", help="filter by seed kind")
    pq.add_argument("--limit", type=int, default=25)
    pq.add_argument("-v", "--verbose", action="store_true",
                    help="Print full JSON of matched records.")
    pq.set_defaults(func=_cmd_query)

    pv = sub.add_parser("versions", help="Show detected Python versions per dir")
    pv.add_argument("--dir", help="Inspect just this directory")
    pv.set_defaults(func=_cmd_versions)

    pr = sub.add_parser("run", help="Run async pipeline through the kernel")
    pr.add_argument("--limit", type=int, default=None,
                    help="Process only first N seeds (default: all).")
    # Optional stub routing params (no real device/network I/O).
    pr.add_argument("--connection-mac", dest="connection_mac", default=None,
                    help="Optional MAC used by stub transports.")
    pr.add_argument("--connection-port", dest="connection_port", type=int, default=None,
                    help="Optional transport port used by stub transports.")
    pr.add_argument("--connection-established", dest="connection_established",
                    action="store_true", default=False,
                    help="If set, stub routing is permitted when MAC/port are present.")
    pr.add_argument("--transport", dest="transport", default=None,
                    choices=["network", "Bluetooth", "serial", "USB_IO", "xpub"],
                    help="Transport name for routing (xpub reads ADR/ADR2 from .env).")
    pr.set_defaults(func=_cmd_run)


    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
