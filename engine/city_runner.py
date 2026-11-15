#!/usr/bin/env python3
"""
Code City District Runner & Engine
Author: Bleak
"""

import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent.parent / "manifests" / "city_spec.json"

def load_manifest():
    if not MANIFEST_PATH.exists():
        print("[-] Manifest not found at:", MANIFEST_PATH)
        return None
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)

def main():
    print("[*] Booting Code City Engine...")
    spec = load_manifest()
    if spec:
        print(f"[+] Loaded City: {spec.get('city')} (v{spec.get('version')})")
        print(f"[+] Architecture: {spec.get('architecture')}")
        print("[+] Status: All districts operational.")
    else:
        print("[-] Failed to load city specifications.")

if __name__ == "__main__":
    main()
