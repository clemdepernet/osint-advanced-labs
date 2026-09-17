#!/usr/bin/env python3
"""diff_monitor.py - idempotent change monitoring between two STIX runs (TP part 4c).

A monitor must surface what is NEW, not re-report everything. Compare last run's
bundle with this run's and emit the added/removed objects as an alert. This is the
Day 1 pipeline discipline applied to a threat graph.
Usage: python3 backend/diff_monitor.py OLD.json NEW.json
"""
from __future__ import annotations
import sys, json, pathlib, stix2

def ids(path):
    b = stix2.parse(pathlib.Path(path).read_text(), allow_custom=False)
    return {o.id: o for o in b.objects}

def main():
    if len(sys.argv) < 3:
        print("usage: diff_monitor.py OLD.json NEW.json"); sys.exit(1)
    old, new = ids(sys.argv[1]), ids(sys.argv[2])
    added = [o for i, o in new.items() if i not in old]
    removed = [i for i in old if i not in new]
    print(f"[*] added: {len(added)}  removed: {len(removed)}")
    for o in added:
        label = getattr(o, "name", getattr(o, "value", o.type))
        print(f"    + {o.type}: {label}")
    for i in removed:
        print(f"    - {i}")
    if added:
        print("[!] ALERT: new intelligence since last run -> notify the team / push to OpenCTI")

if __name__ == "__main__":
    main()
