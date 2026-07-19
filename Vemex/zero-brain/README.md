# Zero Brain / Uriel Defense Core

A Node.js simulation and control framework built around the **Render Paradox** concept, paired with a real-time **Spectral Command Center** web dashboard. The project models self-authoritative “god nodes” that manage spectrum fields, network traffic, cryptographic lock states, and visual threat simulations.

This is a **software simulation and visualization system** — not hardware security. It uses real cryptography (SHA-256, SHA-512, AES-256-GCM) and networking primitives to model defensive state machines, then exposes them through HTTP APIs and a browser UI.

## What It Does

### Core library (`uriel-ultimate-defense/`)

The `GodLevelNodeControlUnit` orchestrates a network of nodes, each with:

| Module | Purpose |
|--------|---------|
| **Render Paradox** | Activates breach state, self-linking, and adaptive 100-step hash recalibration |
| **Field Distortion Engine** | M⁰ (zero mass/density) fields, space freezing, non-constant velocity |
| **Spectrum Field Lock** | Detects, registers, and locks Hz/weight/density signals |
| **GodNodeShield** | Pressure monitoring and node integrity |
| **RuleBookHash** | Enforces 10 core rules (e.g. zero-mass immunity) via SHA-512 |
| **Uriel Defense** | Adversarial annihilation and artifact locking |
| **Network Layer** | Packet routing, memory bank, secure channels, traffic control |
| **Device Hashing** | Device registry and natural-system hashing |
| **Propagation System** | Site/WiFi propagation simulation |
| **External Compute Link** | Spectrum Hz actuation and audio buffer generation |

### Command center (`server.js` + `public/`)

The HTTP server boots a primary node (`node_alpha`), runs continuous simulation loops, and serves:

- **Static dashboard** — cyber-themed HUD with LiDAR, mesh, brain, and sensor canvases
- **Server-Sent Events** (`/api/stream`) — live electron, particle, and threat telemetry
- **REST API** — lock/unlock particles, recalibrate, pulsate X-ray scans, brain-mesh sync, render security, Mamba weight/cache simulation, and more

On startup the server also initializes virtual sensors (CPU, memory, network, spectrum), brain-mesh detection, dual optimization cycles, and QBOM coherence balancers.

## Requirements

- **Node.js** 14 or later
- No external npm dependencies (uses built-in Node modules only)

## Quick Start

### 1. Run unit tests

```bash
cd uriel-ultimate-defense
npm test
```

Expected output: **118 passed, 0 failed** across 33 test suites covering nodes, networking, cryptography, spectrum locking, and field distortion.

### 2. Start the command center

```bash
# From project root
node server.js
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Optional: run core simulation CLI

```bash
cd uriel-ultimate-defense
npm start
```

Runs the standalone Render Paradox simulation (`src/simulate.js`).

## API Overview

All mutation endpoints use **POST** with JSON bodies where noted.

| Endpoint | Description |
|----------|-------------|
| `GET /` | Command center dashboard |
| `GET /api/stream` | SSE live simulation feed |
| `POST /api/pulsate` | Trigger X-ray pulse and spawn electrons |
| `POST /api/lock` | Lock a particle by `particleId` |
| `POST /api/unlock-all` | Release all locked particles |
| `POST /api/recalibrate` | Run 100-step adaptive hash recalibration |
| `POST /api/pair-transmit` | Toggle translation gate (`{ "active": true }`) |
| `POST /api/sensor-status` | Virtual sensor readings (CPU, memory, spectrum) |
| `POST /api/brain-mesh-status` | External/internal brain mesh state |
| `POST /api/enable-bidirectional-sync` | Enable mesh sync |
| `POST /api/render-security-status` | Render security and scale state |
| `POST /api/mamba-weights-status` | Mamba layer weight simulation status |

Example:

```bash
curl -X POST http://localhost:3000/api/recalibrate
curl -X POST http://localhost:3000/api/sensor-status
```

## Project Structure

```
ecridiamcore/
├── server.js                 # HTTP server, simulation engine, REST/SSE APIs
├── public/
│   ├── index.html            # Spectral Command Center UI
│   ├── app.js                # Canvas rendering, SSE client, controls
│   └── style.css             # HUD styling
└── uriel-ultimate-defense/
    ├── src/
    │   ├── core.js           # GodLevelNodeControlUnit and node primitives
    │   ├── test.js           # 118 assertion-based unit tests
    │   ├── simulate.js       # CLI simulation runner
    │   └── ...               # Network, spectrum, defense, crypto modules
    ├── package.json
    └── README.md             # Core library deep-dive
```

## Test Results (verified)

| Suite | Result |
|-------|--------|
| Unit tests (`npm test`) | ✅ 118/118 passed |
| Static assets (`/`, `/app.js`, `/style.css`) | ✅ HTTP 200 |
| `POST /api/recalibrate` | ✅ Returns lock hash |
| `POST /api/pulsate` | ✅ `{ "status": "pulsated" }` |
| `POST /api/sensor-status` | ✅ Sensor telemetry JSON |
| `POST /api/brain-mesh-status` | ✅ Mesh state JSON |
| `GET /api/stream` | ✅ SSE data events |

## Dashboard Controls

The web UI provides buttons for:

- **Pulsate / Pair Transmit / Recalibrate / Unlock** — core node operations
- **Layer toggles** — show/hide top and bottom simulation layers
- **Sensor panel** — force lock, release lock, sensor status
- **Brain mesh** — enable/disable bidirectional sync, redetect mesh
- **Optimization** — enable cycle, sync cortex, hardware optimize
- **Render security** — set security level, secure scale, emergency reset

Live metrics (Variable W, locked count, threat level) update via the SSE stream.

## Cortex–Uriel Latch

Routes external cortex and brain-mesh writes through Uriel before they touch neurons. Stores capability profiles (transpass payload, spectrum lock, render paradox state) and replays them when cortex patterns match.

| Endpoint | Description |
|----------|-------------|
| `POST /api/latch-status` | Latch count, dispatch stats, stored profiles |
| `POST /api/latch-create` | Snapshot current Uriel config into a new latch |
| `POST /api/latch-dispatch` | Auto-match cortex pattern or dispatch by `{ "latchId" }` |
| `POST /api/latch-train` | Reinforce latch: `{ "latchId", "success": true }` |
| `POST /api/latch-save-coordinates` | Save home/external coords: `{ "particleId", "home": {x,y}, "external": {x,y}, "externalCoordinatePermit": true }` |

- **Locked particles** reject external cortex/mesh overwrites unless the latch allows it
- **Coordinate permits** — `homeCoordinatePermit` (internal neural path) and `externalCoordinatePermit` (cortex/mesh path) saved per particle; writes allowed when path allocation matches
- **Auto-latch** on particle lock and recalibrate
- **Persistence** in `.cortex_latch_store.json`
- **Tests:** `node test-cortex-latch.js`

## License / Notes

This repository is published as **zero-brain** on GitHub. The core library README in `uriel-ultimate-defense/` contains additional technical detail on the Render Paradox model and cryptographic lock semantics.
