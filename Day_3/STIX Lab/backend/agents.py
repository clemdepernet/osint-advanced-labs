#!/usr/bin/env python3
"""
agents.py - agentic, parallel OSINT->STIX pipeline (TP part 3b).

Several lightweight 'agents' run CONCURRENTLY, each responsible for one slice of
collection/enrichment, then a writer agent merges everything into ONE STIX bundle.
This is the shape of a modern CTI pipeline (n8n / OpenCTI connectors do the same
at scale). Here the collectors are stubbed/deterministic so the TP runs offline;
swap their bodies for real API calls (crt.sh, passive DNS, news) in production.

Run:  python3 backend/agents.py   ->  data/agentic_bundle.json
"""
from __future__ import annotations
import concurrent.futures as cf, json, pathlib, time
from stix2 import Identity, Indicator, DomainName, IPv4Address, Note, Report, Bundle, TLP_GREEN

TARGET = "AeroParts Supplier Ltd"

# --- collector agents (each returns a partial finding dict) -------------------
def agent_subdomains():
    time.sleep(0.2)  # pretend network
    return {"domains": ["aeroparts-hr-portal.com", "login-aeroparts.net", "vpn.aeroparts.io"]}

def agent_passive_dns():
    time.sleep(0.3)
    return {"ips": ["185.199.51.23", "45.67.89.10"]}

def agent_news():
    time.sleep(0.15)
    return {"notes": ["Supplier named in a 2026 phishing wave (source B2)."]}

AGENTS = [agent_subdomains, agent_passive_dns, agent_news]

# --- writer agent: merge partials -> STIX -------------------------------------
def to_stix(merged: dict) -> Bundle:
    target = Identity(name=TARGET, identity_class="organization", object_marking_refs=[TLP_GREEN])
    objs, refs = [target], [target.id]
    for d in merged.get("domains", []):
        dn = DomainName(value=d)
        ind = Indicator(name=f"domain {d}", pattern_type="stix",
                        pattern=f"[domain-name:value = '{d}']",
                        valid_from="2026-01-01T00:00:00Z", confidence=60,
                        object_marking_refs=[TLP_GREEN])
        objs += [dn, ind]; refs += [dn.id, ind.id]
    for ip in merged.get("ips", []):
        ipo = IPv4Address(value=ip); objs.append(ipo); refs.append(ipo.id)
    for n in merged.get("notes", []):
        note = Note(abstract="collector note", content=n, object_refs=[target.id],
                    object_marking_refs=[TLP_GREEN])
        objs.append(note); refs.append(note.id)
    rep = Report(name=f"Agentic collection: {TARGET}", report_types=["observed-data"],
                 published="2026-01-01T10:00:00Z", created_by_ref=target.id,
                 object_refs=refs, confidence=60, object_marking_refs=[TLP_GREEN])
    objs += [rep, TLP_GREEN]
    return Bundle(*objs, allow_custom=False)

def main():
    t0 = time.time()
    merged: dict = {}
    with cf.ThreadPoolExecutor(max_workers=len(AGENTS)) as ex:
        for fut in cf.as_completed([ex.submit(a) for a in AGENTS]):
            part = fut.result()
            for k, v in part.items():
                merged.setdefault(k, [])
                merged[k] += v
    b = to_stix(merged)
    pathlib.Path("data").mkdir(exist_ok=True)
    pathlib.Path("data/agentic_bundle.json").write_text(b.serialize(indent=2))
    print(f"[+] {len(AGENTS)} agents ran in parallel in {time.time()-t0:.2f}s")
    print(f"    merged: { {k: len(v) for k, v in merged.items()} }")
    print(f"    -> data/agentic_bundle.json ({len(b.objects)} STIX objects)")

if __name__ == "__main__":
    main()
