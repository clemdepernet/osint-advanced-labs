# SecOps Lab — Investigator OPSEC (Day 1, afternoon)

| File | Audience | Content |
|---|---|---|
| `SecOps_Lab.md` / `SecOps_Lab.pdf` | students (EN) | full lab assignment: threat model, disposable container, persona, footprint, Hunchly, deliverables, grading |
| `WriteUp_FR_SecOps_Lab.md` | instructor (FR) | answers, expected outputs, pitfalls seen during preparation, grading signals |
| `scripts/` | both | Dockerfile + launcher + 3 checking/generation tools (see header of each file) |
| `templates/` | students | threat model, environment report, footprint reduction plan, Hunchly checklist |

Quick start (instructor, the day before):

```bash
cd scripts
docker build -t osint-lab:latest -f Dockerfile.osint .
docker save osint-lab:latest | gzip > osint-lab.tar.gz     # to distribute on USB if the Wi-Fi is slow
```
