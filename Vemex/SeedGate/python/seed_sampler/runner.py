"""Async pipeline: feeds seeds through the always-running kernel subprocess.

Kernel selection:
  * If `dotnet` is on PATH and `csharp/SeedKernel.csproj` builds/runs, use it.
  * Otherwise, spawn `python -m seed_sampler.kernel_stub`.

Communication is JSONL over the child's stdin/stdout. No sockets. No env
passthrough beyond what's needed.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path
from typing import Iterable

from . import PROJECT_ROOT, TRACKER_PATH
from . import tracker as tracker_mod

# Optional transport stubs (no real device/network I/O).
# Loaded lazily inside `run` so the default compute pipeline stays minimal.



CSHARP_PROJECT = PROJECT_ROOT / "csharp" / "SeedKernel.csproj"


def _select_kernel_cmd() -> list[str]:
    """Return argv for the kernel subprocess.

    Prefers the C# kernel when `dotnet` is available AND the project exists.
    """
    dotnet = shutil.which("dotnet")
    if dotnet and CSHARP_PROJECT.is_file():
        return [dotnet, "run", "--project", str(CSHARP_PROJECT),
                "--configuration", "Release", "--nologo", "--verbosity", "quiet"]
    return [sys.executable, "-m", "seed_sampler.kernel_stub"]


async def _run_pipeline(events: list[dict], cmd: list[str]) -> list[dict]:
    """Spawn kernel, feed events, collect results (one-per-event, in order)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )
    assert proc.stdin is not None and proc.stdout is not None

    results: list[dict] = []

    async def _writer() -> None:
        try:
            for ev in events:
                line = json.dumps(ev, ensure_ascii=False) + "\n"
                proc.stdin.write(line.encode("utf-8"))
                await proc.stdin.drain()
        finally:
            try:
                proc.stdin.close()
                await proc.stdin.wait_closed()
            except (BrokenPipeError, ConnectionResetError):
                pass

    async def _reader() -> None:
        while True:
            raw = await proc.stdout.readline()
            if not raw:
                return
            try:
                results.append(json.loads(raw.decode("utf-8").strip()))
            except json.JSONDecodeError:
                results.append({"error": "bad_kernel_output",
                                "raw": raw.decode("utf-8", errors="replace")})

    await asyncio.gather(_writer(), _reader())
    stderr = (await proc.stderr.read()).decode("utf-8", errors="replace") if proc.stderr else ""
    rc = await proc.wait()
    if rc != 0 and stderr:
        # Surface kernel stderr in an out-of-band record.
        results.append({"error": "kernel_exit", "code": rc, "stderr": stderr[-2000:]})
    return results


def _build_events(seeds: Iterable[dict], limit: int | None) -> list[dict]:
    events: list[dict] = []
    for i, s in enumerate(seeds):
        if limit is not None and i >= limit:
            break
        events.append({
            "id": i,
            "value": s.get("value", ""),
            "value_sha256": s.get("value_sha256"),
            "kind": s.get("kind"),
            "address": s.get("address"),
        })
    return events


def run(limit: int | None = None,
        connection_mac: str | None = None,
        connection_port: int | None = None,
        connection_established: bool = False,
        transport: str | None = None) -> dict:
    """Synchronous entry point. Loads tracker, runs pipeline, saves results.

    Optional routing parameters are used for *stub-only* transport delivery
    inside `seed-sampler-integration/`.

    Returns a small summary dict.
    """
    doc = tracker_mod.load(TRACKER_PATH)

    seeds = doc.get("seeds", [])
    if not seeds:
        return {"kernel": None, "processed": 0, "message": "no seeds; run `scan` first"}

    events = _build_events(seeds, limit)
    cmd = _select_kernel_cmd()
    engine_label = "csharp" if cmd[0].endswith("dotnet") else "python-stub"

    results = asyncio.run(_run_pipeline(events, cmd))

    # ---- Optional stub routing (no real I/O) -----------------------------
    # Routing happens only when:
    #   - connection_established is True
    #   - mac + port are present (as required by some transports)
    #   - transport is explicitly specified
    routing_log: dict[str, object] = {
        "enabled": bool(connection_established and connection_mac and connection_port is not None),
        "connection": {
            "mac": connection_mac,
            "port": connection_port,
            "established": connection_established,
        },
        "transport": transport,
        "attempts": [],
        "routed_any": False,
    }

    if connection_established and connection_mac and connection_port is not None and transport:

        # Lazy import so the default compute-only path has no dependency.
        try:
            # Local absolute import by path is avoided; instead rely on
            # package-relative import by creating a module shim via sys.path.
            import sys as _sys

            # Import from the *importable* package mirror:
            #   seed-sampler/internal/seed_sampler_integration/
            integration_pkg_root = PROJECT_ROOT / "internal" / "seed_sampler_integration"

            if integration_pkg_root.exists():
                # Add .../seed-sampler/internal to sys.path so we can import
                #   seed_sampler_integration.*
                _sys.path.insert(0, str(integration_pkg_root.parent))
                from seed_sampler_integration.dispatcher import TransportDispatcher, ConnectionSpec  # type: ignore




                dispatcher = TransportDispatcher()

                async def _route_all() -> None:
                    # Keep snapshot-like identity stable: one snapshot per event
                    # index. Payload is the merged kernel result.
                    by_id = {r.get("id"): r for r in results if isinstance(r, dict)}
                    for ev in events:
                        idx = ev["id"]
                        snap = f"snapshot_{idx}"
                        payload = by_id.get(idx) or {"id": idx}
                        res = await dispatcher.route(
                            transport=transport,  # type: ignore[arg-type]
                            snapshot_id=snap,
                            payload=payload,
                            connection_spec=ConnectionSpec(
                                mac=connection_mac,
                                port=connection_port,
                                established=connection_established,
                            ),
                        )





                        routing_log["attempts"].append(res)  # type: ignore[union-attr]

                        if isinstance(res, dict) and res.get("routed") is True:
                            routing_log["routed_any"] = True

                asyncio.run(_route_all())
        except Exception as e:
            routing_log["error"] = f"routing_failed: {e!r}"

    doc["routing_log"] = routing_log


    # Merge results back onto seeds by id, and also keep a flat log.
    by_id = {r.get("id"): r for r in results if isinstance(r, dict) and "id" in r}
    for ev in events:
        idx = ev["id"]
        r = by_id.get(idx)
        if r is not None:
            seeds[idx].setdefault("kernel", {}).update({
                k: v for k, v in r.items() if k != "id"
            })
    doc["seeds"] = seeds
    doc["kernel_results"] = results
    tracker_mod.save(doc, TRACKER_PATH)

    errors = [r for r in results if isinstance(r, dict) and "error" in r]
    out = {
        "kernel": engine_label,
        "cmd": cmd,
        "processed": len(events),
        "results": len(results),
        "errors": len(errors),
    }
    # Surface routing_log for CLI consumption.
    out["routing_log"] = routing_log
    return out
