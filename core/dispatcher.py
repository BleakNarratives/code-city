#!/usr/bin/env python3
"""
Code City Inter-District Event Dispatcher (SQLite Integrated)
Author: Bleak
"""

import json
import time
from pathlib import Path
from core.indexer import log_event as sqlite_log_event

EVENTS_LOG = Path(__file__).parent.parent / "logs" / "events.log"

def emit_event(sender: str, recipient: str, topic: str, payload: dict):
    EVENTS_LOG.parent.mkdir(exist_ok=True)
    event = {
        "timestamp": time.time(),
        "sender": sender,
        "recipient": recipient,
        "topic": topic,
        "payload": payload
    }
    
    # 1. Append to flat JSONL log
    with open(EVENTS_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")
        
    # 2. Dual-write into SQLite indexer database
    try:
        sqlite_log_event(sender, recipient, topic, payload)
    except Exception as e:
        print(f"[-] SQLite index warning: {e}")
        
    print(f"[DISPATCH] {sender} -> {recipient} [{topic}]")

if __name__ == "__main__":
    print("[*] Testing Dispatcher with SQLite Dual-Write...")
    emit_event("gateway-node", "scout-runner", "trigger_scan", {"target": "market_signals", "priority": "high"})
    print("[+] Dispatcher test complete.")
