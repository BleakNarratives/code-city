#!/usr/bin/env python3
"""
Code City Operational Dashboard & Health Inspector
Author: Bleak
"""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent
REGISTRY_PATH = ROOT / "logs" / "registry.json"
EVENTS_LOG = ROOT / "logs" / "events.log"
DB_PATH = ROOT / "logs" / "city_state.db"

def main():
    print("=" * 60)
    print(" CITY OF CODE — OPERATIONAL DASHBOARD")
    print("=" * 60)
    
    # 1. Manifest info
    manifest_path = ROOT / "manifests" / "city_spec.json"
    if manifest_path.exists():
        spec = json.loads(manifest_path.read_text())
        print(f"[*] City Name     : {spec.get('city')} (v{spec.get('version')})")
        print(f"[*] Architecture  : {spec.get('architecture')}")
    
    # 2. Registry nodes
    print("-" * 60)
    print("[*] Active Node Registry:")
    if REGISTRY_PATH.exists():
        reg = json.loads(REGISTRY_PATH.read_text())
        for node, info in reg.items():
            print(f"    - {node} (District: {info.get('district')}, Port: {info.get('port')})")
    else:
        print("    No active nodes registered.")
        
    # 3. SQLite Event DB Stats
    print("-" * 60)
    print("[*] SQLite State Ledger:")
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM events")
        db_count = cursor.fetchone()[0]
        cursor.execute("SELECT topic, sender, recipient FROM events ORDER BY id DESC LIMIT 3")
        recent = cursor.fetchall()
        conn.close()
        print(f"    Total Indexed Events: {db_count}")
        print("    Recent IPC Traffic:")
        for r in recent:
            print(f"      [{r[0]}] {r[1]} -> {r[2]}")
    else:
        print("    SQLite database not initialized.")
        
    # 4. JSONL Event Log Stats
    print("-" * 60)
    print("[*] Flat Log Status:")
    if EVENTS_LOG.exists():
        lines = EVENTS_LOG.read_text().strip().split("\n")
        print(f"    Total Flat Events Logged: {len([l for l in lines if l])}")
    else:
        print("    events.log is empty.")
    print("=" * 60)

if __name__ == "__main__":
    main()
