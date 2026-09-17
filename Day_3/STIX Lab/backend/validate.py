#!/usr/bin/env python3
"""validate.py - strict STIX 2.1 validation (TP part 4a).

Two levels:
  1) stix2.parse(strict) - the library enforces required properties, types and
     vocabularies at parse time. If it parses, the objects are spec-conformant.
  2) (optional) the OASIS `stix2-validator` CLI adds schema + best-practice checks:
       stix2_validator data/bundle.json
     It needs its bundled JSON schemas; if your install lacks them, rely on (1).
Usage: python3 backend/validate.py data/bundle.json
"""
from __future__ import annotations
import sys, pathlib, stix2

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/bundle.json"
    text = pathlib.Path(path).read_text()
    try:
        bundle = stix2.parse(text, allow_custom=False)
    except Exception as e:
        print(f"[X] INVALID: {e}"); sys.exit(1)
    types = {}
    for o in bundle.objects:
        types[o.type] = types.get(o.type, 0) + 1
    print(f"[+] VALID STIX 2.1 - {len(bundle.objects)} objects")
    for t, n in sorted(types.items()):
        print(f"    {t}: {n}")

if __name__ == "__main__":
    main()
