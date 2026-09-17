#!/usr/bin/env python3
"""
build_bundle.py - build a valid STIX 2.1 bundle from an investigation (TP part 2).

Models a small CTI case the way STIX is meant to be used: entities (SDOs),
technical observables (SCOs) and typed relationships (SROs), with TLP marking,
confidence, an ATT&CK-mapped attack pattern, a sighting and an analyst Opinion
(the Admiralty tie-in from Day 2).

Run:  python3 backend/build_bundle.py   ->  data/bundle.json + frontend/data.js
Requires: pip install stix2
"""
from __future__ import annotations
import json, pathlib
from stix2 import (Identity, ThreatActor, Infrastructure, Malware, AttackPattern,
                   Indicator, Relationship, Sighting, Report, Note, Opinion,
                   DomainName, IPv4Address, ObservedData, Bundle, ExternalReference,
                   TLP_AMBER)

ROOT = pathlib.Path(__file__).resolve().parents[1]

def build() -> Bundle:
    analyst = Identity(name="Ascent CTI Team", identity_class="organization",
                       sectors=["technology"], object_marking_refs=[TLP_AMBER])
    victim = Identity(name="AeroParts Supplier Ltd", identity_class="organization",
                      sectors=["aerospace"], object_marking_refs=[TLP_AMBER])

    actor = ThreatActor(name="UNC-Falcon", threat_actor_types=["spy"],
                        sophistication="advanced", resource_level="organization",
                        primary_motivation="organizational-gain", confidence=70,
                        object_marking_refs=[TLP_AMBER])

    # ATT&CK-mapped attack pattern (Spearphishing Link, T1566.002)
    ttp = AttackPattern(name="Spearphishing Link",
                        external_references=[ExternalReference(
                            source_name="mitre-attack", external_id="T1566.002",
                            url="https://attack.mitre.org/techniques/T1566/002/")],
                        object_marking_refs=[TLP_AMBER])

    malware = Malware(name="FalconDropper", is_family=False,
                      malware_types=["dropper"], object_marking_refs=[TLP_AMBER])

    # Observables (SCOs) + the Observed Data that records "we saw these"
    dom = DomainName(value="aeroparts-hr-portal.com")
    ip = IPv4Address(value="185.199.51.23")
    observed = ObservedData(first_observed="2026-09-10T08:00:00Z",
                            last_observed="2026-09-10T08:05:00Z",
                            number_observed=3, object_refs=[dom.id, ip.id],
                            object_marking_refs=[TLP_AMBER])

    # Indicator = a detection pattern (STIX patterning language)
    indicator = Indicator(name="Phishing domain for AeroParts",
                          pattern_type="stix",
                          pattern="[domain-name:value = 'aeroparts-hr-portal.com']",
                          valid_from="2026-09-10T00:00:00Z", confidence=80,
                          object_marking_refs=[TLP_AMBER])

    rels = [
        Relationship(actor, "uses", malware),
        Relationship(actor, "uses", ttp),
        Relationship(actor, "targets", victim),
        Relationship(indicator, "indicates", actor),
        Relationship(malware, "communicates-with", dom),
    ]
    sighting = Sighting(sighting_of_ref=indicator.id, count=3,
                        first_seen="2026-09-10T08:00:00Z",
                        where_sighted_refs=[victim.id],
                        object_marking_refs=[TLP_AMBER])

    # Analyst assessment -> Admiralty. Opinion encodes the credibility judgement.
    opinion = Opinion(explanation="Domain reuse + ATT&CK overlap; source B2 (usually "
                      "reliable, probably true).", opinion="strongly-agree",
                      object_refs=[indicator.id], object_marking_refs=[TLP_AMBER])
    note = Note(abstract="Provenance",
                content="Collected via crt.sh + passive DNS on 2026-09-10. "
                        "SHA-256 of evidence archived in the case file.",
                object_refs=[indicator.id, observed.id],
                object_marking_refs=[TLP_AMBER])

    report = Report(name="UNC-Falcon phishing against AeroParts",
                    report_types=["threat-actor"], published="2026-09-11T09:00:00Z",
                    created_by_ref=analyst.id, confidence=75,
                    object_refs=[actor.id, victim.id, ttp.id, malware.id,
                                 indicator.id, observed.id, sighting.id] +
                                 [r.id for r in rels],
                    object_marking_refs=[TLP_AMBER])

    return Bundle(analyst, victim, actor, ttp, malware, dom, ip, observed,
                  indicator, *rels, sighting, opinion, note, report,
                  TLP_AMBER, allow_custom=False)

def main():
    b = build()
    (ROOT / "data").mkdir(exist_ok=True)
    js = b.serialize(indent=2)
    (ROOT / "data" / "bundle.json").write_text(js)
    (ROOT / "frontend").mkdir(exist_ok=True)
    (ROOT / "frontend" / "data.js").write_text("window.BUNDLE = " + b.serialize() + ";")
    n = len(b.objects)
    print(f"[+] valid STIX 2.1 bundle: {n} objects -> data/bundle.json + frontend/data.js")
    types = {}
    for o in b.objects:
        types[o.type] = types.get(o.type, 0) + 1
    print("    " + ", ".join(f"{k}:{v}" for k, v in sorted(types.items())))

if __name__ == "__main__":
    main()
