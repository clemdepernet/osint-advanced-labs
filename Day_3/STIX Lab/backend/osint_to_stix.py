#!/usr/bin/env python3
"""
osint_to_stix.py - turn raw OSINT findings into a STIX 2.1 bundle (TP part 3a).

Input: findings.json  (a plain list the analyst or a collector produced), e.g.
  {"target":"AeroParts Supplier Ltd",
   "domains":["aeroparts-hr-portal.com","login-aeroparts.net"],
   "ips":["185.199.51.23"]}
Output: a bundle with Identity(target) + DomainName/IPv4 SCOs + one Indicator per
domain + an ObservedData + a Report, all TLP:GREEN, confidence carried through.

This is the bridge from 'notes' to a shareable, machine-readable knowledge graph.
"""
from __future__ import annotations
import json, sys, pathlib
from stix2 import (Identity, Indicator, DomainName, IPv4Address, ObservedData,
                   Report, Bundle, TLP_GREEN)

def to_bundle(findings: dict, confidence: int = 60) -> Bundle:
    target = Identity(name=findings.get("target", "unknown"),
                      identity_class="organization", object_marking_refs=[TLP_GREEN])
    scos, refs, objs = [], [], [target]
    for d in findings.get("domains", []):
        dn = DomainName(value=d); scos.append(dn)
        ind = Indicator(name=f"OSINT domain {d}", pattern_type="stix",
                        pattern=f"[domain-name:value = '{d}']",
                        valid_from="2026-01-01T00:00:00Z", confidence=confidence,
                        object_marking_refs=[TLP_GREEN])
        objs += [dn, ind]; refs += [dn.id, ind.id]
    for ip in findings.get("ips", []):
        ipo = IPv4Address(value=ip); objs.append(ipo); refs.append(ipo.id)
    if scos or findings.get("ips"):
        od = ObservedData(first_observed="2026-01-01T00:00:00Z",
                          last_observed="2026-01-01T00:00:00Z", number_observed=1,
                          object_refs=[s.id for s in scos] +
                                      [o.id for o in objs if o.type == "ipv4-addr"],
                          object_marking_refs=[TLP_GREEN])
        objs.append(od); refs.append(od.id)
    report = Report(name=f"OSINT footprint: {findings.get('target','')}",
                    report_types=["observed-data"], published="2026-01-01T09:00:00Z",
                    created_by_ref=target.id, object_refs=[target.id] + refs,
                    confidence=confidence, object_marking_refs=[TLP_GREEN])
    objs += [report, TLP_GREEN]
    return Bundle(*objs, allow_custom=False)

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/findings.json"
    findings = json.loads(pathlib.Path(src).read_text())
    b = to_bundle(findings)
    pathlib.Path("data").mkdir(exist_ok=True)
    pathlib.Path("data/osint_bundle.json").write_text(b.serialize(indent=2))
    print(f"[+] {len(b.objects)} STIX objects -> data/osint_bundle.json")

if __name__ == "__main__":
    main()
