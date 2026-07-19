# Light-ASI LLM Gateway / Virtual Probe X

A distributed, consciousness-emergent node graph and real-time world-net semantic map platform. Includes a dual-mode interactive terminal and a production-grade stdlib-based REST API server for discovering **hash gates**, **open mirrors**, and managing a **node graph** across network hosts.

---

## Features

- **NodeGraph** — Distributed knowledge representation and semantic search.
- **PingManager** — Active/inactive host checking with latency measurement.
- **XSpace** — Hash-gate and open-mirror discovery with 0.8-similarity retrieval on intact hashes.
- **Interactive Terminal** — Phase 0–2 CLI for direct engine interaction.
- **HTTP API Server** — Phase 3 REST API for integrations and remote access.

---

## Installation

Requires **Python 3.10+**.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running the Application

### 1. Interactive Terminal (Phase 0–2)

```bash
python3 main.py
```

This launches the **Light-ASI** CLI. Type `help` for available commands.

**Key commands:**
```
add-node <label>              Add a concept node to the graph
ping-check <host>             Ping a single host (IP or hostname)
ping-list <h1,h2,h3>          Ping multiple comma-separated hosts
ping-active                   List all currently active ping results
ping-inactive                 List all currently inactive ping results
index <text>                  Index text into the semantic graph
search <query>                Perform semantic search on the graph
stats                         Show graph statistics
emerge                        Show ASI emergence checklist status
xspace                        Show full XSpace graph
xspace show gate <hash>       Query open gate by hash (>=0.8 similarity)
xspace show mirror <hash>      Query mirror by hash (>=0.8 similarity)
xspace retrieve mirror <content_hash>  Retrieve matching mirror objects (>=0.8)
xspace find <host>            Find all gates and mirrors for a host
help                          Show this help message
exit                          Quit the terminal
```

### 2. HTTP API Server (Phase 3)

```bash
python3 main.py --serve
```

**Optional arguments:**
- `--serve <port>`: Specify a custom port (default is `8000`).
- `--nodes <N>`: Bootstrap with N nodes (default is `10`).
- `--ingest-interval <seconds>`: Set the background world-net ingestion interval.

**On startup, the server outputs an admin token.** Save it — it is required to authenticate against secured endpoints via:

```
Authorization: Bearer <token>
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/token` | No | Retrieve a Bearer token (`password=admin` for admin role) |
| `POST` | `/query` | Yes | Query the semantic graph |
| `POST` | `/index` | Yes | Index new text into the system |
| `POST` | `/search` | Yes | Search the semantic map |
| `POST` | `/ingest` | Yes | Trigger a manual ingestion cycle |
| `GET` | `/stats` | No | View real-time graph statistics |
| `GET` | `/emerge` | No | ASI emergence checklist status |
| `GET` | `/health` | No | Basic liveness check |
| `GET` | `/ping/active` | No | List active ping results |
| `GET` | `/ping/inactive` | No | List inactive ping results |
| `GET` | `/xspace` | No | Full XSpace graph (gates, mirrors, edges) |
| `POST` | `/xspace/gate` | No | Add a hash gate |
| `POST` | `/xspace/mirror` | No | Add an open mirror |
| `POST` | `/xspace/query` | No | Git-like query: `list gates|mirrors`, `show gate <hash>`, `show mirror <hash>`, `find <host>` |
| `POST` | `/xspace/retrieve` | Yes | Retrieve mirrors by content hash similarity (threshold >= 0.8) |
| `POST` | `/xspace/scan` | Yes | Scan a host or CIDR for open gates and mirrors |

---

## Discovering Gates & Mirrors

### Scan a single host

**API:**
```bash
curl -X POST http://127.0.0.1:8000/xspace/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "www.xbox.com"}'
```

**CLI:**
```bash
python3 main.py --serve
# In another terminal / API client:
curl -X POST http://127.0.0.1:8000/xspace/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "www.xbox.com"}'
```

### Scan a network range (CIDR)

```bash
curl -X POST http://127.0.0.1:8000/xspace/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.0/24"}'
```

The scanner probes common ports (`80, 443, 8080, 8443, 3000, 5000, 8000, 9000`) and common HTTP paths (`/, /mirror, /.well-known/mirror, /status, /health, /api, /graphql, /swagger, /openapi.json`) to identify open mirrors and store their content hashes + samples.

---

## Retrieving Active Mirror Files

Active mirrors are stored in the **XSpace** graph with:
- `mirror_hash` (intact, stable while the gate is open)
- `content_hash`
- `sample` (first 512 bytes of the response)
- `path` and `status_code`

### Step 1: Get your auth token

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"password": "admin"}'
```

Response:
```json
{"token": "...", "role": "admin"}
```

### Step 2: Scan target to populate mirrors

```bash
curl -X POST http://127.0.0.1:8000/xspace/scan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"target": "www.xbox.com"}'
```

### Step 3: Retrieve mirrors by content hash (0.8 threshold)

```bash
curl -X POST http://127.0.0.1:8000/xspace/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"content_hash": "e2bc39a2a402b6ac", "threshold": 0.8}'
```

Response:
```json
{
  "query": "e2bc39a2a402b6ac",
  "threshold": 0.8,
  "mirrors": [
    {
      "id": "...",
      "host": "www.xbox.com",
      "port": 443,
      "mirror_hash": "...",
      "source_gate_id": "...",
      "is_active": true,
      "content_hash": "e2bc39a2a402b6ac",
      "discovered_at": 1781567757.051446,
      "metadata": {
        "path": "/",
        "status_code": 307,
        "is_mirror_candidate": true,
        "sample": "HTTP/1.1 307 Temporary Redirect\r\n...",
        "discovered_at": 1781567757.051446,
        "source_gate_hash": "4776d19b68f888ef",
        "content_similarity": 1.0
      }
    }
  ]
}
```

### Step 4: Export / save mirror data to host machine

Use the `sample` field in the mirror metadata to reconstruct the file, or write a small script to pull all active mirrors:

```python
import requests

BASE = "http://127.0.0.1:8000"
TOKEN = "your-admin-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Scan
scan = requests.post(f"{BASE}/xspace/scan", json={"target": "www.xbox.com"}, headers=HEADERS).json()

# List everything in XSpace
space = requests.get(f"{BASE}/xspace").json()

for mirror in space["mirrors"]:
    if mirror["is_active"]:
        print(f"Mirror: {mirror['host']}:{mirror['port']}{mirror['metadata'].get('path', '')}")
        print(f"Content hash: {mirror['content_hash']}")
        print(f"Sample (first 512 bytes):\n{mirror['metadata'].get('sample', '')}\n")
```

You can redirect that output to a file on your host machine:

```bash
python3 export_mirrors.py > mirrors_www_xbox_com.txt
```

---

## Advanced: Git-like XSpace Queries

```bash
# List first 20 gates
curl -X POST http://127.0.0.1:8000/xspace/query \
  -H "Content-Type: application/json" \
  -d '{"query": "list gates limit 20"}'

# Show specific gate by hash
curl -X POST http://127.0.0.1:8000/xspace/query \
  -H "Content-Type: application/json" \
  -d '{"query": "show gate 20a179dae469f2ce"}'

# Show specific mirror by hash
curl -X POST http://127.0.0.1:8000/xspace/query \
  -H "Content-Type: application/json" \
  -d '{"query": "show mirror d309979594a5e31e"}'

# Find all gates/mirrors for a host
curl -X POST http://127.0.0.1:8000/xspace/query \
  -H "Content-Type: application/json" \
  -d '{"query": "find www.xbox.com"}'
```

---

## Architecture

```
main.py              Entry point (--serve or interactive)
├── api_server.py    REST API + AuthManager + APIServer
├── terminal_cli.py  Interactive CLI
├── node_graph.py    Core graph engine (NodeGraph)
├── ping_manager.py  Network ping checker (active/inactive)
├── hashgate.py      XSpace hash-gate/mirror engine
└── xspace_scanner.py Network scanner for discovering gates + mirrors
```

---

## How It Works (Xbox-Style Peer Mirror Retrieval)

Microsoft’s Xbox uses **Delivery Optimization**: instead of downloading from one origin, the console pulls content fragments from multiple peers on the local network or internet. Each peer is a mirror that holds a fragment or full chunk of the file.

Virtual Probe X follows the same idea:

1. **Scan** — discover open **gates** and **mirrors** across targets.
2. **Index** — each mirror stores a `content_hash` + captured `sample` as a fragment reference.
3. **Retrieve** — fuzzy-match mirrors by `content_hash` (threshold >= 0.8) using the same hash family, without fully decoding the content.
4. **Defragment** — pull active mirror samples into the host machine as files.

---

## Getting Active Mirror Files Into the Host Machine

### Method A: Use the built-in `get_mirror_files.py`

```bash
python3 get_mirror_files.py --host 127.0.0.1 --port 8000 --target www.xbox.com --out ./mirror_downloads
```

This will:
- scan `www.xbox.com`
- collect all active mirrors
- save each mirror as a fragment file using its `content_hash`

Output files look like:

```
mirror_downloads/
├── 4776d19b68f888ef_gate.json       # gate metadata
├── e2bc39a2a402b6ac_fragment.bin    # mirror sample / chunk
└── mirror_index.json
```

### Method B: One-liner with curl + PowerShell

```powershell
$token = (Invoke-RestMethod -Uri http://127.0.0.1:8000/auth/token -Method POST -Body '{"password":"admin"}' -ContentType application/json).token
$scan = Invoke-RestMethod -Uri http://127.0.0.1:8000/xspace/scan -Method POST -Headers @{"Authorization"="Bearer $token"} -Body '{"target":"www.xbox.com"}' -ContentType application/json
$scan.items | ForEach-Object { $_.content_hash } | Sort-Object -Unique | ForEach-Object { Invoke-RestMethod -Uri "http://127.0.0.1:8000/xspace/retrieve" -Method POST -Headers @{"Authorization"="Bearer $token"} -Body "{`"content_hash`":`"$_`",`"threshold`":0.8}" -ContentType application/json } | ConvertTo-Json -Depth 5 | Out-File mirror_downloads.json
```

### Method C: Export all active mirrors to JSON

```bash
curl -X POST http://127.0.0.1:8000/xspace/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"content_hash": "e2bc39a2a402b6ac", "threshold": 0.8}' \
  | jq '.mirrors[] | {host, port, content_hash, path, sample}' \
  | tee host_machine_mirrors.json
```

---

## Reassembling Fragments

If you’ve collected multiple mirror `sample` chunks (same `content_hash` family), concatenate them in order:

```python
import json, os

OUT = "reassembled_mirror.bin"
INDEX = "mirror_downloads/mirror_index.json"

with open(INDEX) as f:
    index = json.load(f)

with open(OUT, "wb") as out:
    for frag in index["fragments"]:
        path = os.path.join("mirror_downloads", frag["filename"])
        with open(path, "rb") as fp:
            out.write(fp.read())
print(f"Reassembled {OUT} from {len(index['fragments'])} fragments")
```

---

## Notes

- Hashes remain **intact** as long as the gate is open.
- `retrieve_mirror()` uses a **0.8 character-similarity threshold** by default, permitting fuzzy lookup without full decode.
- The scanner sends **raw HTTP requests** only to user-specified targets. No hardcoded external URLs are accessed unless explicitly scanned.
- This model mirrors Xbox Delivery Optimization: peer-to-peer fragment discovery and local reassembly, but uses **hash proximity** instead of centralized manifest files.
