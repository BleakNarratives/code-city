#!/usr/bin/env python3
"""
Code City SQLite Event Indexer & State Ledger (Queue Enabled)
Author: Bleak
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "logs" / "city_state.db"

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            sender TEXT,
            recipient TEXT,
            topic TEXT,
            payload TEXT,
            processed INTEGER DEFAULT 0
        )
    """)
    # Ensure processed column exists if upgrading older DB
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN processed INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    conn.close()

def log_event(sender: str, recipient: str, topic: str, payload: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    import time
    cursor.execute(
        "INSERT INTO events (timestamp, sender, recipient, topic, payload, processed) VALUES (?, ?, ?, ?, ?, 0)",
        (time.time(), sender, recipient, topic, json.dumps(payload))
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[+] SQLite event database verified with queue support.")
