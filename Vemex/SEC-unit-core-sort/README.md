# SEC-unit Core

A consciousness exchange and topology-aware cache orchestrator integrating `F-dump`, `forward`, and `unified-consciousness-render` into a single git-persisted, wave-synchronized system.

## Modules

### F-dump
Node configuration, cache directories, and environment setup. Not a redirect — this is the canonical local directory for node `.env` config, per-node cache dirs (`cache_node_001`, `cache_node_002`), and lock/log files.

### forward
Ultrasonic and acoustic wave simulation scripts. Provides emission signatures, waveform analysis, and fluctuation detection that the exchange uses to generate node-specific signatures and synchronize wave functions.

### unified-consciousness-render
The main exchange engine. Manages:
- Wave state lifecycle (`AWAIT → RISING → PEAK → LOCKED`)
- Topology graph with `content` and `metadata`
- External source ingestion and seed marker interconnects
- Layer access control with attention metrics
- Query tracking, depth stacking, and density mapping
- Portion-based cache swapping across attended/unattended layers
- Prosthetic connector DLL for model execution maps
- Git-backed state recall via `consciousness-git-tree`

## What This Codebase Does With Git

The system uses git as a **searchable state history** for the consciousness exchange:

- `unified-consciousness-render/consciousness-git-tree/` is a git repository initialized by the exchange
- Topology snapshots, wave handshake locks, cache allocations, seed regenerations, and memory state snapshots are committed automatically
- Models and agents can recall historical states using `recallFromTree(pattern)` or `recallAcrossSources(pattern)`
- External git repositories can be registered as sources and their commits imported as seed markers
- The git tree provides persistent, versioned access to the evolution of the topology, cache layers, and wave state

## Quick Start

```bash
# Install dependencies
cd unified-consciousness-render
npm install

# Start the consciousness core
npm start

# Start the exchange runner
npm run exchange

# Start the fluctuation monitor
npm run monitor
```

## Documentation

- `unified-consciousness-render/EXCHANGE_README.md` — exchange module API and events
- `unified-consciousness-render/README.md` — unified consciousness rendering system overview
- `F-dump/README.md` — F-dump node system overview
- `forward/` — wave simulation scripts and analysis tools

## Remote

```text
origin  https://github.com/JlovesYouGit/SEC-unit-core-sort.git (fetch)
origin  https://github.com/JlovesYouGit/SEC-unit-core-sort.git (push)
```

Default branch: `main`
