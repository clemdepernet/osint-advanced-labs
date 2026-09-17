# STIX 2.1 — Cheat Sheet

_Model intelligence as a shareable, machine-readable graph. For CTI / structured OSINT._

## What & why

**STIX** (Structured Threat Information eXpression) is an OASIS open standard (v2.1) that describes intelligence as a **graph** of typed JSON objects. **TAXII** is the protocol that moves STIX between tools. Your investigation stops being loose notes and becomes queryable, auditable and interoperable.

## The three families

| Family | Role | Examples |
|---|---|---|
| **SDO** — Domain Objects | the entities | `identity`, `threat-actor`, `intrusion-set`, `campaign`, `malware`, `tool`, `attack-pattern`, `indicator`, `vulnerability`, `infrastructure`, `report`, `note`, `opinion`, `location`, `course-of-action` |
| **SCO** — Cyber-observables | the technical facts | `domain-name`, `ipv4-addr`, `url`, `file`, `email-addr`, `email-message`, `user-account`, `x509-certificate`, `autonomous-system` |
| **SRO** — Relationship Objects | the links | `relationship` (source_ref → target_ref), `sighting` |

Common relationship types: `uses`, `targets`, `indicates`, `attributed-to`, `communicates-with`, `located-at`, `mitigates`.

## Every object carries

```
id            type--UUID           (e.g. indicator--<uuid>)
spec_version  "2.1"
created / modified   UTC timestamps
created_by_ref       identity--... (provenance)
confidence           0-100
object_marking_refs  [ TLP marking ]
external_references  [ links to CVE, MITRE ATT&CK, reports ]
```

## TLP (Traffic Light Protocol) — how far it travels

| Marking | Share with |
|---|---|
| TLP:CLEAR | anyone |
| TLP:GREEN | the community |
| TLP:AMBER | your organisation (+ clients, need-to-know) |
| TLP:RED | named recipients only |

> Never share above the TLP. Never state a fact above its confidence.

## Confidence ↔ Admiralty (Day 2)

Map source reliability (A–F) × info credibility (1–6) onto `confidence` + an `Opinion`:

| Admiralty | confidence | Opinion |
|---|---|---|
| A1 / A2 | 95 / 80 | strongly-agree / agree |
| B2 / C3 | 80 / 60 | agree / neutral |
| D4 / E5 | 40 / 20 | disagree / strongly-disagree |

Take the cautious value: `confidence = min(source, info)`.

## Indicator patterning

```
[domain-name:value = 'evil.example.com']
[ipv4-addr:value = '185.199.51.23']
[file:hashes.'SHA-256' = 'ab12...']
[email-addr:value = 'phish@evil.tld'] AND [domain-name:value = 'evil.tld']
```

## Build it in Python (stix2)

```python
from stix2 import Indicator, ThreatActor, Relationship, Bundle, TLP_AMBER
ind = Indicator(name="phish domain", pattern_type="stix",
                pattern="[domain-name:value = 'evil.tld']",
                valid_from="2026-01-01T00:00:00Z", confidence=80,
                object_marking_refs=[TLP_AMBER])
ta  = ThreatActor(name="UNC-Falcon", object_marking_refs=[TLP_AMBER])
rel = Relationship(ind, "indicates", ta)
bundle = Bundle(ind, ta, rel, TLP_AMBER)
open("bundle.json","w").write(bundle.serialize(indent=2))
```

```python
import stix2, pathlib
b = stix2.parse(pathlib.Path("bundle.json").read_text())   # strict parse = validation
```

```bash
pip install stix2 stix2-validator
stix2_validator bundle.json          # schema + best-practice checks
```

## MITRE ATT&CK

ATT&CK is published **as STIX**. Reference a technique by id (not by copying text):

```json
"external_references": [
  { "source_name": "mitre-attack", "external_id": "T1566.002",
    "url": "https://attack.mitre.org/techniques/T1566/002/" } ]
```

## Ecosystem

| Tool | Role |
|---|---|
| OpenCTI | team knowledge-graph platform (STIX-native); `pycti` to push |
| MISP | sharing platform; imports/exports STIX |
| TAXII 2.1 | transport: collections you POST bundles to / poll |
| MITRE ATT&CK | technique catalogue, distributed as STIX |
| n8n | orchestrate collectors → STIX writer → OpenCTI (see Docker & n8n Lab) |

## Minimal report object (group an investigation)

```json
{ "type":"report", "spec_version":"2.1", "id":"report--...",
  "name":"UNC-Falcon phishing", "published":"2026-01-01T09:00:00Z",
  "confidence":75, "object_refs":["threat-actor--...","indicator--..."],
  "object_marking_refs":["marking-definition--tlp-amber"] }
```

> **Golden rule**: nodes (SDO/SCO) + typed edges (SRO), each with provenance, TLP and confidence. Build, validate, share — the same finding, understood everywhere.
