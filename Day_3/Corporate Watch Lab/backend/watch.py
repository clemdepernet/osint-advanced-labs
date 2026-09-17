#!/usr/bin/env python3
"""
Corporate Watch - aggregate competitive-intelligence monitor (Day 3 capstone example).

Organisation-level, public-source, AGGREGATE monitoring of a target COMPANY:
  - R&D capability map + trend (OpenAlex, keyless)
  - Macro-corporate events: contracts, M&A, divestiture, service/production stops (news RSS)
  - Aggregate hiring-demand signal by research domain (job-posting counts, no individuals)

It deliberately does NOT profile individuals. See backend/common.py (drop_personal).

Usage:
  python3 backend/watch.py --company Boeing
Writes: data/aggregate.json  and  frontend/data.js  (so the dashboard opens from file://)
"""
from __future__ import annotations
import argparse, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "sources"))
import common
from sources import news, rnd, hiring   # noqa

ROOT = pathlib.Path(__file__).resolve().parents[1]

def run(company: str) -> dict:
    print(f"[*] R&D capability map (OpenAlex) ...")
    rnd_data = rnd.collect()
    print(f"    {len(rnd_data['concepts'])} domains, {len(rnd_data['yearly'])} years")
    print(f"[*] Macro-corporate news ...")
    events = news.collect(company)
    print(f"    {len(events)} events")
    print(f"[*] Aggregate hiring-demand signal ...")
    demand = hiring.collect(company)
    # event breakdown
    breakdown = {}
    for e in events:
        breakdown[e["event_type"]] = breakdown.get(e["event_type"], 0) + 1
    return {
        "company": company,
        "generated": common.now_utc(),
        "rnd": rnd_data,
        "events": sorted(events, key=lambda e: e.get("published", ""), reverse=True),
        "event_breakdown": [{"type": k, "count": v} for k, v in
                            sorted(breakdown.items(), key=lambda kv: -kv[1])],
        "hiring_demand": demand,
        "compliance": "Organisation-level, aggregate, public sources. No individual is profiled.",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", default="Boeing")
    args = ap.parse_args()
    data = run(args.company)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "aggregate.json").write_text(json.dumps(data, indent=2))
    (ROOT / "frontend" / "data.js").write_text("window.DATA = " + json.dumps(data) + ";")
    print(f"[+] wrote data/aggregate.json and frontend/data.js")
    print(f"    open frontend/index.html in a browser to view the dashboard")

if __name__ == "__main__":
    main()
