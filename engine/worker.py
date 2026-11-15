#!/usr/bin/env python3
"""
Code City Background Event Worker Daemon
Author: Bleak
"""

import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "logs" / "city_state.db"

def process_event(event_id: int, topic: str, payload: dict):
    print(f"[WORKER] Processing event #{event_id} -> Topic: [{topic}]")
    if topic == "trigger_scan":
        target = payload.get("target", "unknown")
        print(f"  -> Executing background scan on target: {target}")
    elif topic == "node_heartbeat":
        print(f"  -> Acknowledged heartbeat from node.")
    else:
        print(f"  -> Generic task handler executed for {topic}.")
    
    time.sleep(0.2) # Simulate work

def run_worker_poll():
    if not DB_PATH.exists():
        print("[-] SQLite event database not found. Run dispatcher first.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch unprocessed events
    cursor.execute("SELECT id, topic, payload FROM events WHERE processed = 0 ORDER BY id ASC")
    pending = cursor.fetchall()
    
    if not pending:
        print("[WORKER] No pending events in queue.")
        conn.close()
        return
        
    print(f"[WORKER] Found {len(pending)} pending event(s) to process.")
    for event_id, topic, raw_payload in pending:
        try:
            payload = json.loads(raw_payload) if raw_payload else {}
            process_event(event_id, topic, payload)
            
            # Mark processed
            cursor.execute("UPDATE events SET processed = 1 WHERE id = ?", (event_id,))
            conn.commit()
        except Exception as e:
            print(f"[-] Error processing event #{event_id}: {e}")
            
    conn.close()
    print("[WORKER] Batch processing complete.")

if __name__ == "__main__":
    print("[*] Booting Code City Worker Daemon...")
    run_worker_poll()
