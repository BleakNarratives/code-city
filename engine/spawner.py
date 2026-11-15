#!/usr/bin/env python3
"""
Code City District Agent Spawner
Author: Bleak
"""

import sys
import json
from pathlib import Path

DISTRICTS = ["core", "engine", "manifests", "dist", "logs", "tests"]

def spawn_district(district_name: str):
    target = Path(__file__).parent.parent / district_name
    target.mkdir(parents=True, exist_ok=True)
    print(f"[+] District verified/spawned: {district_name} -> {target}")

def main():
    print("[*] Initializing Code City District Spawner...")
    for d in DISTRICTS:
        spawn_district(d)
    print("[+] All districts successfully spawned and mounted.")

if __name__ == "__main__":
    main()
