# STIX Lab — from an investigation to a shared threat graph (Day 3)

Turn OSINT findings into a **STIX 2.1** knowledge graph, automate it with parallel
agents, and explore it on a team dashboard. Beginner → advanced.

| Path | What |
|---|---|
| `STIX_Lab.md` / `.pdf` | the guided lab (Part 1 read · Part 2 build · Part 3 automate) |
| `backend/build_bundle.py` | build a valid STIX 2.1 bundle with `stix2` |
| `backend/osint_to_stix.py` | convert a findings file into STIX |
| `backend/agents.py` | parallel collector agents → one merged bundle (agentic) |
| `backend/n8n_workflow.json` | import-ready n8n workflow mirroring the pipeline |
| `frontend/index.html` | team dashboard: force-graph of the bundle, TLP colours, filters |
| `data/` | generated bundles |

```bash
pip install stix2
python3 backend/build_bundle.py     # then open frontend/index.html
python3 backend/agents.py           # parallel OSINT -> STIX
```

Ties into the course: provenance + confidence + TLP are native; the Admiralty scale
(Day 2) maps onto `confidence` + `Opinion`; OpenCTI / MISP / MITRE ATT&CK / TAXII are
the team ecosystem.

## Advanced modules (Part 4)

| Script | What |
|---|---|
| `backend/validate.py` | strict STIX 2.1 validation (stix2 parse; + OASIS validator note) |
| `backend/admiralty.py` | map Admiralty A-F/1-6 ↔ STIX confidence + Opinion |
| `backend/diff_monitor.py` | diff two runs → alert on new intelligence (idempotent monitoring) |
| `backend/enrich_attack.py` | pull a MITRE ATT&CK technique (published as STIX) |
| `backend/push_opencti.py` | reference: load a bundle into OpenCTI via pycti / TAXII |
