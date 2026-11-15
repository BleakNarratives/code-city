# Code City Architecture Specification

## Overview
Code City is a local-first, zero-overhead microservice mesh and autonomous event-driven processing engine running across Termux and local runtime environments.

## Districts & Components
- **`core/`**: Contains foundational services including the District Registry (`registry.py`), SQLite Event Indexer (`indexer.py`), and Inter-District Dispatcher (`dispatcher.py`).
- **`engine/`**: Manages operational infrastructure including the District Spawner (`spawner.py`), Operational Dashboard (`dashboard.py`), Background Event Worker (`worker.py`), and Autonomous Daemon Loop (`daemon.py`).
- **`manifests/`**: Houses system specifications (`city_spec.json`).
- **`logs/`**: Persistent state ledger (`city_state.db`), flat JSON event logs (`events.log`), and node registry state (`registry.json`).

## Event Processing Pipeline
1. **Emission**: Nodes emit IPC events via `core.dispatcher.emit_event()`.
2. **Dual-Write**: Events are simultaneously appended to `logs/events.log` (JSONL) and committed to the SQLite state ledger (`logs/city_state.db`) with `processed = 0`.
3. **Worker Daemons**: `engine/worker.py` polls unprocessed events, executes district handlers, and marks them resolved (`processed = 1`).
4. **Daemon Loop**: `engine/daemon.py` orchestrates continuous background polling at defined intervals.
