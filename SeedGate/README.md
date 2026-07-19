# seed-sampler

A local, read-only indexer + async runner for the `zero-brain/`,
`The-Crown/`, and `SEC-unit-core-sort/` trees. Finds "seeds" in source via
regex, resolves each seed's git-commit origin, detects duplicates across the
trees ("threat events"), and streams events through a long-running C# kernel
that derives an alphanumeric key from the seed's binary form.

Also includes a Python-version manager that detects the required interpreter
per directory (from `.python-version`, `pyproject.toml`, shebangs) and
dispatches simulation runs under the correct `python3.x` subprocess.

## Hard constraints

The tool is intentionally scoped:

- **Read-only** against source dirs. Nothing writes into them.
- **Never `exec`s scanned content.** Scanned files are treated as bytes; the
  only thing that runs is code under `seed-sampler/`.
- **No network, Bluetooth, serial, or USB I/O.** No sockets are opened.
- **C# kernel talks over stdin/stdout JSONL only.** No sockets, no P/Invoke.
- Snapshots capped at 64 KB per file.

## Layout

```
seed-sampler/
├── python/
│   ├── requirements.txt
│   └── seed_sampler/
│       ├── scanner.py       # regex seed extraction
│       ├── tracer.py        # git-origin resolution
│       ├── detector.py      # duplicate detection + reverse-sequence algo
│       ├── tracker.py       # JSON catalog r/w + query
│       ├── pyversion.py     # per-dir Python version detection + dispatch
│       ├── runner.py        # asyncio pipeline → kernel
│       ├── kernel_stub.py   # pure-Python fallback kernel
│       └── cli.py           # scan / query / run / versions
├── csharp/
│   ├── SeedKernel.csproj
│   ├── Program.cs           # stdin JSONL loop
│   ├── Kernel.cs            # async processor, binary blocks
│   └── KeyDerivation.cs     # base36 alphanumeric key
└── data/
    ├── tracker.json         # generated
    └── snapshots/           # generated
```

## Quickstart

```bash
cd seed-sampler/python
pip install -r requirements.txt

# Index all three source trees into data/tracker.json
python -m seed_sampler.cli scan

# Query
python -m seed_sampler.cli query --duplicates
python -m seed_sampler.cli query --value <sha256_prefix>
python -m seed_sampler.cli query --path 'The-Crown/**/QNT-Blue/**'
python -m seed_sampler.cli query --origin <commit_sha>

# List Python versions required per source dir
python -m seed_sampler.cli versions

# Run the async pipeline (uses C# kernel if `dotnet` is on PATH,
# else falls back to the pure-Python kernel stub)
python -m seed_sampler.cli run
```

## What counts as a seed

Text-only regex matches against files with common source extensions
(`.py .js .ts .cs .cpp .c .h .rs .go .json .toml .yaml .yml .md .txt`) plus
any file named `SEED`. Patterns:

- `seed = <int>` / `SEED = <int>`
- `random.seed(<int>)`, `np.random.seed(<int>)`
- `Random(<int>)`, `srand(<int>)`, `new Random(<int>)`
- `SEED=<value>` in env-style lines
- Hex strings ≥ 32 chars (SHA-ish)
- Files literally named `SEED` (whole-file content)
- Lines starting with `# seed:` or `// seed:` prefix

Each match becomes a `Seed` record:

```json
{
  "address": "The-Crown/QuantumEnergyService/foo.py",
  "line": 42,
  "kind": "random_seed_call",
  "value": "1337",
  "value_sha256": "e5b7e9…",
  "origin": {"commit": "a1b2c3…", "timestamp": 1720000000, "repo": "The-Crown"}
}
```

## Reverse-sequence / threat detection

When the same `value_sha256` appears in ≥2 records:

1. All records for that value are grouped as a **threat event**.
2. The ordered list of `(address, line)` occurrences is captured.
3. The list is reversed and re-indexed — this reversed order is the
   "trace" written into `tracker.threats[].reverse_trace`.
4. Canonical origin = record with the earliest `origin.timestamp`
   (fallback: lexicographically smallest address).
5. A per-value snapshot is written to `data/snapshots/<value_sha256>.json`.

## Async pipeline
yes, you provide the destination device identity (MAC + link/port-ish value) to activate routing, but the code under seed-sampler/internal/seed-sampler-integration/*_stub.py is still stub-only—it does not create a real network connection.

for con you need to swap 
network/device I/O would require replacing the stub transport code in seed-sampler/internal/seed-sampler-integration/*/guard_stub.py.
So with the CLI you can choose the transport and route in the stub dispatcher, e.g.:



`runner.py` drives an asyncio loop that:

1. Loads seeds from `tracker.json`.
2. Spawns the kernel subprocess (C# if available, Python stub otherwise).
3. For each seed, writes one JSONL event to the kernel's stdin.
4. Reads one JSONL result per event from the kernel's stdout.
5. Merges results into `tracker.seeds[i].kernel` and rewrites `tracker.json`.

The kernel derives a base36 alphanumeric key from the seed value's binary
form. It runs continuously until stdin is closed.
