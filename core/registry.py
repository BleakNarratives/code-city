#!/usr/bin/env python3
"""
Code City District Registry & Heartbeat Daemon
Author: Bleak
"""

import time
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "logs" / "registry.json"

def register_node(node_name: str, district: str, port: int = 8000):
    REGISTRY_PATH.parent.mkdir(exist_ok=True)
    registry = {}
    if REGISTRY_PATH.exists():
        try:
            registry = json.loads(REGISTRY_PATH.read_text())
        except Exception:
            registry = {}
            
    registry[node_name] = {
        "district": district,
        "port": port,
        "status": "active",
        "last_seen": time.time()
    }
    
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))
    print(f"[+] Node registered: {node_name} in district [{district}] on port {port}")

if __name__ == "__main__":
    print("[*] Initializing Code City District Registry...")
    register_node("gateway-node", "core", 8080)
    register_node("scout-runner", "engine", 8081)
    print(f"[+] Registry state saved to {REGISTRY_PATH}")
