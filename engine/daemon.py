#!/usr/bin/env python3
"""
Code City Autonomous Background Daemon
Author: Bleak
"""

import time
import sys
from pathlib import Path

# Add parent to sys.path to import local engine modules
sys.path.append(str(Path(__file__).parent.parent))

from engine.worker import run_worker_poll

POLL_INTERVAL = 5.0 # seconds

def main():
    print(f"[*] Starting Code City Daemon Loop (Polling every {POLL_INTERVAL}s)...")
    print("[*] Press Ctrl+C to halt daemon.")
    try:
        while True:
            run_worker_poll()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Code City Daemon halted by operator.")

if __name__ == "__main__":
    main()
