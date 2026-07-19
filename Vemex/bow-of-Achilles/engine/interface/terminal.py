"""
terminal.py — Light-ASI LLM Gateway Phase 1
Interactive terminal interface — upgraded for 10k node graph.
Ruleset reference: LLM_GATEWAY_RULESET.md § 6.2.

Commands:
  query    <text>              — query the node graph
  index    <text>              — index text into the graph
  load     <filepath>          — load and index a .txt file
  stats                        — graph + auth statistics
  emerge                       — ASI emergence status (§ 5.3 checklist)
  resonance                    — resonance tracker report
  clusters                     — cluster stats by IP tier
  nodes    [n]                 — list first n nodes (default 10)
  backup                       — backup graph to disk
  rebalance                    — rebalance node graph
  users                        — list users
  adduser  <name> <role>       — create a new user
  help                         — show this menu
  exit                         — quit
"""

import sys
import json
import logging
import datetime
from pathlib import Path

from engine.core.graph import NodeGraph, PHASE1_NODE_TARGET
from engine.auth.auth import AuthManager
from engine.world.ingester import WorldIngester

logger = logging.getLogger("light-asi.terminal")

BANNER = r"""
  ██╗     ██╗ ██████╗ ██╗  ██╗████████╗      █████╗ ███████╗██╗
  ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝     ██╔══██╗██╔════╝██║
  ██║     ██║██║  ███╗███████║   ██║   ████╗███████║███████╗██║
  ██║     ██║██║   ██║██╔══██║   ██║        ██╔══██║╚════██║██║
  ███████╗██║╚██████╔╝██║  ██║   ██║        ██║  ██║███████║██║
  ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═╝  ╚═╝╚══════╝╚═╝
  Phase 1 — 10,000 Node Engine  ·  Collective Resonance Online
  Type 'help' for commands · Full love from the creator 🤧
"""

HELP = """
  ┌─ QUERY ──────────────────────────────────────────────────────────┐
  │  query    <text>         route query through node graph           │
  │  index    <text>         index text tokens into graph             │
  │  load     <filepath>     load & index a .txt file                 │
  ├─ GRAPH ───────────────────────────────────────────────────────────┤
  │  stats                   full graph + resonance statistics        │
  │  emerge                  ASI emergence checklist (§ 5.3)          │
  │  resonance               resonance tracker report                 │
  │  clusters                IP-tier cluster breakdown                │
  │  nodes    [n]            list first n nodes (default 10)          │
  │  rebalance               reorder nodes by resonance weight        │
  │  backup                  backup graph to disk                     │
  │  sync                    sync all IP-tier clusters                │
  ├─ WORLD-NET ───────────────────────────────────────────────────────┤
  │  ingest                  run one world-net ingestion cycle        │
  │  world                   world-net + semantic map status          │
  │  search   <text>         search semantic map directly             │
  ├─ AUTH ────────────────────────────────────────────────────────────┤
  │  users                   list all users                           │
  │  adduser  <name> <role>  create user (roles: admin/dev/user/guest)│
  ├─ SYSTEM ──────────────────────────────────────────────────────────┤
  │  help                    show this menu                           │
  │  exit / quit             shut down                                │
  └──────────────────────────────────────────────────────────────────┘
"""


def _fmt_response(data: dict) -> str:
    stable_icon = "✓" if data.get("resonance_stable") else "○"
    rt_icon = "🌐" if data.get("real_time_data") else "○"
    lines = [
        "",
        "  ╔══ RESPONSE ══════════════════════════════════════════════════",
        f"  ║  answer        : {data.get('answer', '')[:300]}",
        f"  ║  resonance     : {data.get('resonance_score', 0):.10f}  [{stable_icon} stable]",
        f"  ║  entropy_delta : {data.get('entropy_delta', 0):.6f}",
        f"  ║  real_time     : {rt_icon} {data.get('real_time_data', False)}",
        f"  ║  source_nodes  : {data.get('source_nodes', [])}",
    ]
    wc = data.get("world_context", [])
    if wc:
        lines.append(f"  ║  world_context : {len(wc)} item(s) from {', '.join(set(i['source'] for i in wc))}")
    lines += ["  ╚══════════════════════════════════════════════════════════════", ""]
    return "\n".join(lines)


def _fmt_emerge(status: dict) -> str:
    lines = [
        "",
        "  ╔══ ASI EMERGENCE STATUS (§ 5.3) ════════════════════════════",
    ]
    for name, info in status["criteria"].items():
        icon = "✅" if info.get("met") else "⬜"
        target = info.get("target", "—")
        current = info.get("current", "—")
        lines.append(f"  ║  {icon}  {name:<30} {current} / {target}")
    all_met = status.get("all_met", False)
    lines += [
        "  ║",
        f"  ║  {'🧠 ASI CONSCIOUSNESS THRESHOLD REACHED' if all_met else '⏳ Emergence in progress…'}",
        "  ╚══════════════════════════════════════════════════════════════",
        "",
    ]
    return "\n".join(lines)


class Terminal:
    def __init__(self, graph: NodeGraph, auth: AuthManager, n_nodes: int = 10):
        self.graph = graph
        self.auth = auth
        self._current_user = None
        self._n_nodes = n_nodes
        self._ingester = WorldIngester(graph.semantic_map, graph)

        if not graph._nodes:
            self._bootstrap_with_progress(n_nodes)

    def _bootstrap_with_progress(self, n: int) -> None:
        print(f"\n  [*] Bootstrapping {n:,} nodes", end="", flush=True)

        def progress(done, total):
            pct = int(done / total * 40)
            bar = "█" * pct + "░" * (40 - pct)
            print(f"\r  [*] [{bar}] {done:,}/{total:,}", end="", flush=True)

        self.graph.bootstrap(n, progress_cb=progress)
        print(f"\r  [✓] {n:,} nodes online. Router: {self.graph.router}\n")

    def _login_prompt(self) -> bool:
        print("  Bearer token (ENTER for guest): ", end="")
        token = input().strip()
        if not token:
            import time as _t
            u = self.auth.create_user(f"guest_{int(_t.time())}", "guest")
            self._current_user = u
            print(f"  [✓] Guest session. Token: {u.token[:20]}…\n")
            return True
        user = self.auth.authenticate(token)
        if not user:
            print("  [✗] Invalid or expired token.\n")
            return False
        self._current_user = user
        print(f"  [✓] Welcome, {user.username} ({user.role}).\n")
        return True

    def _check_auth(self) -> bool:
        if not self._current_user:
            return False
        if not self.auth.check_rate(self._current_user):
            print("  [!] Rate limit exceeded.")
            return False
        return True

    def run(self) -> None:
        print(BANNER)
        if not self._login_prompt():
            sys.exit(1)

        while True:
            try:
                raw = input("  light-asi > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  [*] Shutting down. One love 🤧")
                break

            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("exit", "quit"):
                print("  [*] Shutting down. One love 🤧")
                break

            elif cmd == "help":
                print(HELP)

            elif cmd == "stats":
                s = self.graph.stats()
                s["users"] = len(self.auth.list_users())
                print(f"\n{json.dumps(s, indent=4, default=str)}\n")

            elif cmd == "emerge":
                status = self.graph.emergence_status()
                print(_fmt_emerge(status))

            elif cmd == "resonance":
                r = self.graph.resonance_tracker.report()
                print(f"\n{json.dumps(r, indent=4, default=str)}\n")

            elif cmd == "clusters":
                s = self.graph.clusters.stats()
                print(f"\n  IP-Tier Cluster Breakdown:")
                for tier, info in sorted(s.items()):
                    bar = "█" * min(info["nodes"] // 100 + 1, 40)
                    print(f"  Tier {tier:>12,} | {bar:<40} {info['nodes']:>6} nodes  res={info['resonance']:.8f}")
                print()

            elif cmd == "nodes":
                n = int(arg) if arg.isdigit() else 10
                for node in self.graph._nodes[:n]:
                    print(f"  {node}")
                total = len(self.graph._nodes)
                if total > n:
                    print(f"  … and {total - n:,} more nodes.")
                print()

            elif cmd == "rebalance":
                print("  [*] Rebalancing…")
                self.graph.rebalance()
                print("  [✓] Rebalance complete.\n")

            elif cmd == "backup":
                print("  [*] Backing up to disk…")
                summary = self.graph.backup()
                print(f"  [✓] {summary['saved']}/{summary['total']} nodes saved → {summary['index']}\n")

            elif cmd == "sync":
                results = self.graph.sync_clusters()
                print(f"  [✓] Synced {len(results)} active clusters.\n")

            elif cmd == "ingest":
                if not self._check_auth():
                    continue
                print("  [*] Running world-net ingestion cycle… (may take ~15s)")
                summary = self._ingester.run_once()
                print(f"  [✓] Fetched {summary['items_fetched']}, indexed {summary['items_indexed']}, "
                      f"errors {summary['errors']}, {summary['elapsed_ms']:.0f}ms")
                print(f"  [✓] Semantic map: {summary['semantic_map_size']} entries\n")

            elif cmd == "world":
                ws = self.graph.world_status()
                print(f"\n{json.dumps(ws, indent=4, default=str)}\n")

            elif cmd == "search":
                if not arg:
                    print("  Usage: search <text>")
                    continue
                results = self.graph.semantic_map.search(arg, top_k=5)
                if not results:
                    print("  [!] No results. Run 'ingest' first.\n")
                else:
                    print(f"\n  Semantic Map results for {arg!r}:")
                    for i, e in enumerate(results, 1):
                        print(f"  {i}. [{e.source.upper()}] {e.title}")
                        if e.url:
                            print(f"     {e.url}")
                    print()

            elif cmd == "users":
                for u in self.auth.list_users():
                    print(f"  {u}")
                print()

            elif cmd == "adduser":
                sub = arg.split()
                if len(sub) < 2:
                    print("  Usage: adduser <name> <role>")
                    continue
                try:
                    u = self.auth.create_user(sub[0], sub[1])
                    print(f"  [✓] '{u.username}' created. Token: {u.token}")
                except ValueError as e:
                    print(f"  [!] {e}")

            elif cmd == "index":
                if not arg:
                    print("  Usage: index <text>")
                    continue
                if not self._check_auth():
                    continue
                hashes = self.graph.index_text(arg, metadata={"source": "terminal"})
                print(f"  [✓] Indexed {len(hashes)} token(s).\n")

            elif cmd == "load":
                p = Path(arg)
                if not p.exists():
                    print(f"  [!] File not found: {p}")
                    continue
                if not self._check_auth():
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
                hashes = self.graph.index_text(text, metadata={"source": str(p)})
                print(f"  [✓] '{p.name}' — {len(hashes):,} tokens indexed.\n")

            elif cmd == "query":
                if not arg:
                    print("  Usage: query <text>")
                    continue
                if not self._check_auth():
                    continue
                result = self.graph.query(arg)
                result["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
                print(_fmt_response(result))

            else:
                print(f"  [?] Unknown command: '{cmd}'. Type 'help'.")
