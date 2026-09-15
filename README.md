# Forensics & OSINT Advanced — Hands-on Labs

Teaching material for a three-day advanced course on open-source intelligence and digital forensics: slide decks, lab assignments, scripts, templates and synthetic datasets. Everything a student needs to run the labs is here. Instructor answer keys are **not** published.

> Audience: intelligence analysts, security professionals, law-enforcement and corporate investigators with prior OSINT experience.
> Working language of the material: English. Some legacy exercises were translated from French.

## Course map

| Day | Morning (theory) | Afternoon (labs in this repo) |
|---|---|---|
| **Day 1** — Operational security & automation | Threat modelling, attribution postures, personas, fingerprinting, Python for OSINT, APIs, pipelines | [Who Am I?](Day_1/Who%20Am%20I%20Lab/) (opening challenge) · [SecOps Lab](Day_1/SecOps%20Lab/) |
| **Day 2** — Source reliability & media forensics | Admiralty Code, fact-checking, coordinated inauthentic behaviour, image/video forensics, C2PA, geolocation | [Geosint Lab](Day_2/Geosint%20Lab/) · [Media Forensics Lab](Day_2/Media%20Forensics%20Lab/) |
| **Day 3** — Dark web, crypto tracing & capstone | Tor and hidden services, sensitive groups, on-chain tracing, chokepoints, automated monitor | [Data Breach Analysis](Hand's%20on%20exercises/Databreach.pdf) · [Crypto Investigation](Hand's%20on%20exercises/Crypto%20Investigation.pdf) |

Slides for each day are in `Day_N/*.pptx`.

## The labs

### Day 1 · Who Am I? — opening challenge (75 min)
Students profile the instructor under signed rules of engagement, deliver an Admiralty-rated intel card, then discover who showed up in the target's profile-viewer list. Sets the tone for the OPSEC day.
`WhoAmI_Lab.md` · rules of engagement · intel card template.

### Day 1 · SecOps Lab — persona, footprint & disposable environment (3h30)
Threat model first, then a self-built **disposable OSINT container** (Debian + Tor + pivot tools), browser-fingerprint testing, a coherent research **persona** with collision checks, reduction of the analyst's own footprint, and a fully documented **Hunchly** browsing session.
Scripts: `Dockerfile.osint`, `osint_case.sh` (one container per case), `opsec_check.sh` (GO / NO-GO pre-flight), `persona_forge.py`, `footprint_audit.py`.

### Day 2 · Geosint Lab — Operation Glass Eye (75 min)
Two warm-up photos to geolocate and chronolocate, then a drone's last transmitted frame to place within three decimals using OpenStreetMap/Overpass, satellite imagery, Street View and SunCalc. Deliverable: a verification note with chain of custody.

### Day 2 · Media Forensics Lab — Operation Riverbank (3h)
Five workshops on one fabricated disinformation case: forged metadata and mismatched thumbnails, Error Level Analysis and shadow coherence, reverse image search and Content Credentials (C2PA), video cut and splice detection with ffmpeg, coordinated-behaviour detection with pandas and NetworkX. The dataset is **100 % synthetic** (no real person, place or copyrighted media) and regenerable with `scripts/make_dataset.py`.

### Day 3 · Data Breach Analysis & Crypto Investigation
Two assignments: exploring a leaked SQL dump with SQLAlchemy/pandas (GDPR impact, schema discovery, KPIs), and tracing a Solana memecoin from on-chain identifiers to Web2 footprints, deployer and liquidity analysis.

## Repository layout

```
Day_1/
  Day_1_Operational_Security_And_Automation.pptx
  Who Am I Lab/        subject (md + pdf), templates/
  SecOps Lab/          subject (md + pdf), scripts/, templates/
Day_2/
  Day_2_Source_Reliability_And_Media_Forensics.pptx
  Geosint Lab/         subject, material/ (3 images), templates/
  Media Forensics Lab/ subject, scripts/, templates/, dataset/ (generated, seed 42)
Day_3/
  Day_3_Dark_Web_Crypto_And_Capstone.pptx
Hand's on exercises/   Databreach.pdf, Crypto Investigation.pdf
```

Each lab folder has its own `README.md`. Every subject follows the same structure: learning objectives, scenario, numbered steps with questions, deliverables, grading grid, optional extensions.

## Quick start (students)

```bash
git clone https://github.com/<owner>/osint-advanced-labs.git
cd osint-advanced-labs

# Day 1 - build the disposable investigation container once (~2 GB)
cd "Day_1/SecOps Lab/scripts"
docker build -t osint-lab:latest -f Dockerfile.osint .
./osint_case.sh start CASE-042

# Day 2 - analysis tooling on the host
pip install pillow pandas numpy networkx imageio-ffmpeg faker requests
```

Tools referenced across the labs: Docker, Python 3.10+, `exiftool`, `ffmpeg`, `sherlock`, `holehe`, `maigret`, Tor, Hunchly (30-day trial), Google Lens / Yandex / TinEye, SunCalc, Overpass Turbo, Content Credentials Verify.

## Ground rules baked into every lab

- **Legal and ethical perimeter first.** Personas and infiltration are regulated; every lab states what is out of scope.
- **Passive collection only** on real people. The only real target in the course is the instructor, by written consent and under rules of engagement.
- **Nothing is proof by itself.** Metadata, ELA, geolocation, provenance and cross-checking converge or diverge; verdicts rest on the weight of evidence.
- **Chain of custody.** URL, UTC timestamp, SHA-256 and archive for everything that matters.
- **OPSEC applies to homework too.** Personal credentials, real IPs or unmasked personal data in a submission cost points.

## For instructors

Answer keys, French write-ups, ground-truth files and the generator seeds' outputs live outside this repository. If you teach with this material and want them, open an issue or contact the author.

## Contributing

Issues and pull requests are welcome: broken links, tools that changed their CLI, new warm-up material, translations. Please do not submit answer keys or real personal data.

## License

Course material © Clement Depernet. Text, slides and templates are released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/); scripts under the [MIT License](https://opensource.org/licenses/MIT). Third-party tools and sample files keep their own licenses.
