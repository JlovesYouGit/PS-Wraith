# Light-ASI Phase 3 API Server

This module provides a fully functional HTTP REST API for the Light-ASI engine. It is built entirely on the Python standard library (`http.server`) and has no external dependencies.

## Features
- **RESTful Endpoints**: Full suite of endpoints for querying, indexing, and monitoring the graph.
- **Auth Middleware**: Bearer token authentication required for most endpoints.
- **Role-Based Access Control**: Differentiates between `admin`, `developer`, `user`, and `guest`.
- **CORS Support**: Preconfigured with permissive CORS headers.
- **Dual-Mode Operation**: Run as an interactive terminal or a background/foreground API server.

## Quickstart

Start the server on port 8000:
```bash
python3 main.py --serve 8000
```

## Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/health` | Liveness check | No |
| POST | `/auth/token` | Create user + get Bearer token | No (Admin required for non-guest roles) |
| GET | `/auth/users` | List users | Yes (Admin/Dev only) |
| POST | `/query` | Query the node graph | Yes |
| POST | `/index` | Index text into the graph | Yes |
| POST | `/search` | Search the semantic map | Yes |
| POST | `/ingest` | Trigger world-net cycle | Yes (Admin/Dev only) |
| GET | `/stats` | Graph statistics | Yes |
| GET | `/emerge` | ASI emergence checklist | Yes |
| GET | `/resonance` | Resonance report | Yes |
| GET | `/world` | World-net status | Yes |
| POST | `/backup` | Backup graph to disk | Yes (Admin only) |
