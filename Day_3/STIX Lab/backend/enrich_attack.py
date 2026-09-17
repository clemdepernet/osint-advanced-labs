#!/usr/bin/env python3
"""enrich_attack.py - enrich an attack-pattern with live MITRE ATT&CK data (TP part 4d).

ATT&CK is published AS STIX. Given a technique id (e.g. T1566), fetch its object
from the public ATT&CK STIX bundle and print name + description, so your local
attack-pattern links to the authoritative source.
Usage: python3 backend/enrich_attack.py T1566.002
Needs network + `requests`. Falls back gracefully offline.
"""
from __future__ import annotations
import sys
try:
    import requests
except ImportError:
    sys.exit("pip install requests")

ATTACK = ("https://raw.githubusercontent.com/mitre/cti/master/"
          "enterprise-attack/enterprise-attack.json")

def lookup(tid: str):
    print(f"[*] fetching ATT&CK enterprise bundle (large, ~40MB)...")
    try:
        data = requests.get(ATTACK, timeout=60).json()
    except Exception as e:
        print(f"[!] offline or fetch failed ({e}). In class, cache the bundle locally."); return
    for o in data["objects"]:
        if o.get("type") != "attack-pattern":
            continue
        for ref in o.get("external_references", []):
            if ref.get("source_name") == "mitre-attack" and ref.get("external_id") == tid:
                print(f"[+] {tid}  {o['name']}")
                print(f"    {o.get('description','')[:300]}...")
                print(f"    url: {ref.get('url')}")
                return
    print(f"[!] {tid} not found")

if __name__ == "__main__":
    lookup(sys.argv[1] if len(sys.argv) > 1 else "T1566.002")
