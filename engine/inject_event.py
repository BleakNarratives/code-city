#!/usr/bin/env python3
"""
Code City Live Event Injector
Author: Bleak
"""

import sys
from core.dispatcher import emit_event

def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "market_sync"
    target = sys.argv[2] if len(sys.argv) > 2 else "scout-runner"
    
    print(f"[*] Injecting live event [{topic}] to {target}...")
    emit_event("cityctl-cli", target, topic, {"action": "execute", "priority": "normal"})
    print("[+] Event successfully injected into SQLite queue. Check daemon output.")

if __name__ == "__main__":
    main()
