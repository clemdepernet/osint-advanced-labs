# Forensics & OSINT Advanced — Student Handbook

Welcome. This repository is your field manual for a three-day advanced course on **open-source intelligence** and **digital forensics**. Everything you need to run the labs lives here: slide decks, hands-on assignments, ready-to-run scripts, synthetic datasets and three printable cheat sheets.

> **Working language:** English. **Audience:** analysts, security professionals and investigators with prior OSINT experience.
> **Golden thread of the course:** collect rigorously, verify by convergence, and report so an auditor could reproduce you.

---

## The three days

| Day | Theme | You will practise |
|---|---|---|
| **Day 1** — Operational security & automation | Threat modelling, attribution, personas, fingerprinting, Python & APIs | [Who Am I?](Day_1/Who%20Am%20I%20Lab/) · [SecOps Lab](Day_1/SecOps%20Lab/) |
| **Day 2** — Source reliability & collection techniques | Admiralty Code, disinformation & CIB, media forensics, scraping | [Email Harvester](Day_2/Email%20Harvester%20Lab/) · [API Scraping](Day_2/API%20Scraping%20Lab/) · [Geosint](Day_2/Geosint%20Lab/) · [Media Forensics](Day_2/Media%20Forensics%20Lab/) |
| **Day 3** — Dark web, blockchain tracing & structured intelligence | Blockchain fundamentals, crypto tracing, STIX & MITRE ATT&CK, agentic automation | [Data Breach](Day_3/Databreach.pdf) · [Crypto Investigation](Day_3/Crypto%20Investigation.pdf) · [STIX Lab](Day_3/STIX%20Lab/) · [Corporate Watch](Day_3/Corporate%20Watch%20Lab/) |

Each day's slide deck is the `*.pptx` in its folder. Each lab folder has its own `README` and a step-by-step subject as both Markdown and PDF.

---

## All labs at a glance

| Lab | You build | Skills | Folder |
|---|---|---|---|
| **Who Am I?** | An Admiralty-rated intel card on a consenting target | Pivoting, sourcing, OPSEC awareness | [open](Day_1/Who%20Am%20I%20Lab/) |
| **SecOps Lab** | A disposable OSINT container, a research persona, a Hunchly case | OPSEC, personas, footprint reduction, chain of custody | [open](Day_1/SecOps%20Lab/) |
| **Email Harvester** | A recursive e-mail crawler in Bash | `curl`, regex, crawl logic | [open](Day_2/Email%20Harvester%20Lab/) |
| **API Scraping** | A product scraper from an intercepted session | Burp Suite, `requests`, pagination | [open](Day_2/API%20Scraping%20Lab/) |
| **Geosint** | A geolocation + chronolocation verification note | OSM/Overpass, Street View, SunCalc | [open](Day_2/Geosint%20Lab/) |
| **Data Breach** | An exposure analysis of a leaked SQL dump | SQLAlchemy, pandas, GDPR reasoning | [open](Day_3/Databreach.pdf) |
| **Media Forensics** | A verification note on a fabricated campaign | EXIF, ELA, C2PA, video, CIB | [open](Day_2/Media%20Forensics%20Lab/) |
| **Crypto Investigation** | An on-chain genealogy of a memecoin | Solscan, DexScreener, `requests` | [open](Day_3/Crypto%20Investigation.pdf) |
| **STIX Lab** | A STIX 2.1 threat graph, built and automated | `stix2`, parallel agents, team dashboard | [open](Day_3/STIX%20Lab/) |
| **Corporate Watch** | An aggregate competitive-intelligence monitor | OpenAlex, news RSS, dashboard | [open](Day_3/Corporate%20Watch%20Lab/) |

---

## Cheat sheets — keep these open

| Sheet | For |
|---|---|
| [Linux Basics](Cheatsheets/01_Linux_Basics_Cheatsheet.pdf) | moving around the terminal, files, pipes, permissions |
| [Bash Scripting](Cheatsheets/02_Bash_Scripting_Cheatsheet.pdf) | variables, conditions, loops, functions, good habits |
| [Kali & OSINT Tools](Cheatsheets/03_Kali_OSINT_Tools_Cheatsheet.pdf) | sherlock, maigret, holehe, curl, hashcat, ffuf, exiftool, nmap… |

---

## Quick start

```bash
git clone https://github.com/clemdepernet/osint-advanced-labs.git
cd osint-advanced-labs
```

**Host tooling (once):**
```bash
# macOS
brew install exiftool ffmpeg jq
# Debian / Kali
sudo apt install -y libimage-exiftool-perl ffmpeg jq

# Python analysis stack (Day 2 & 3)
pip install requests pandas numpy networkx pillow faker sqlalchemy pymysql

# Username / e-mail pivot tools
pipx install sherlock-project holehe maigret
```

**Day 1 — build the disposable investigation container (≈2 GB, once):**
```bash
cd "Day_1/SecOps Lab/scripts"
docker build -t osint-lab:latest -f Dockerfile.osint .
./osint_case.sh start CASE-042        # one container per case; Tor starts inside
```

---

## The investigator's five reminders

Print these on the inside of your eyelids.

1. **Threat model first.** OPSEC is *proportionate*, not maximal. Decide who you protect against before you collect.
2. **Passive on real people.** No contact, no login, no password-reset probes. The only real target in this course is the instructor, by written consent.
3. **Rate everything (Admiralty).** Separate the *source* (A–F) from the *information* (1–6). A `C3` that is true beats an `A1` that is false.
4. **Chain of custody.** For anything that matters: the **URL**, a **UTC timestamp**, and a **SHA-256** of the artefact. Archive a copy.
5. **Convergence, never one clue.** Metadata, signal, geo/chrono and cross-checking converge or diverge. The verdict lives in the *weight of evidence*.

### The Admiralty scale

| Source | Reliability | | Info | Credibility |
|---|---|---|---|---|
| **A** | Completely reliable | | **1** | Confirmed by other sources |
| **B** | Usually reliable | | **2** | Probably true |
| **C** | Fairly reliable | | **3** | Possibly true |
| **D** | Not usually reliable | | **4** | Doubtful |
| **E** | Unreliable | | **5** | Improbable |
| **F** | Cannot be judged | | **6** | Cannot be judged |

---

## Snippet grab-bag

The greatest hits you will reach for daily. Full versions are in the cheat sheets.

```bash
# --- Chain of custody on any file
sha256sum evidence.jpg ; date -u +%FT%TZ
exiftool -a -G1 evidence.jpg                 # all metadata
exiftool -all= -overwrite_original clean.jpg # STRIP metadata before sharing

# --- Username & e-mail pivots
sherlock johndoe --print-found
maigret johndoe --html
holehe target@example.com --only-used

# --- curl for APIs & recon
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" "$URL" | jq '.'
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u

# --- Recursive e-mail harvest (Day 2, TP1)
EMAIL='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
curl -sL "$URL" | grep -oE "$EMAIL" | sort -u

# --- Encoding
printf 'OSINT' | base64            # T1NJTlQ=
echo 'T1NJTlQ=' | base64 -d        # OSINT

# --- Geosint: candidates near a point (OpenStreetMap / Overpass)
curl -s https://overpass-api.de/api/interpreter --data-urlencode \
  'data=[out:csv(::lat,::lon)];node["generator:source"="wind"](around:8000,47.5988,-1.1389);out;'

# --- Anonymity check (inside the container)
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

```python
# --- API replay & paginate (Day 2, TP2)
s = requests.Session(); s.headers["Authorization"] = f"Bearer {token}"
hits = []
while start < total:
    hits += s.get(url, params={"c_start": start, "c_sz": 48}).json()["hits"]
    start += 48
pd.json_normalize(hits).to_csv("products.csv", index=False)
```

---

## Useful URLs

**Usernames & e-mail**
- WhatsMyName — https://whatsmyname.app
- Have I Been Pwned — https://haveibeenpwned.com
- Pwned Passwords (k-anonymity) — https://api.pwnedpasswords.com

**Images & media forensics**
- Google Lens · Yandex Images · TinEye — reverse image search
- FotoForensics — https://fotoforensics.com · Forensically — https://29a.ch/photo-forensics
- InVID/WeVerify — browser extension for video
- Content Credentials (C2PA) verify — https://contentcredentials.org/verify

**Geolocation**
- OpenStreetMap — https://www.openstreetmap.org · Overpass Turbo — https://overpass-turbo.eu
- SunCalc — https://www.suncalc.org · OpenInfraMap — https://openinframap.org

**Infrastructure & archives**
- crt.sh (certificate transparency) — https://crt.sh
- Wayback Machine — https://web.archive.org · Shodan — https://www.shodan.io

**OPSEC & tooling**
- Tor Browser — https://www.torproject.org · Cover Your Tracks — https://coveryourtracks.eff.org
- amiunique — https://amiunique.org · Hunchly — https://www.hunch.ly
- CyberChef — https://gchq.github.io/CyberChef

---

## Ground rules (non-negotiable)

- **Authorisation before action.** Recon, content discovery and hash cracking are legal only on assets you own or a written engagement scope. When in doubt, stop.
- **Minimise & protect data.** Collect only what the task needs. Anonymise personal data in your deliverables (GDPR).
- **Your homework has OPSEC too.** A real IP, a personal credential or unmasked personal data left in a submission costs points.
- **Tools are neutral; authorisation is what makes their use legitimate.**

---

## Repository layout

```
Cheatsheets/            Linux · Bash · Kali/OSINT (md + pdf)
Day_1/                  OPSEC & automation
  Who Am I Lab/         opening challenge (subject + templates)
  SecOps Lab/           container, persona, footprint, Hunchly (scripts + templates)
Day_2/                  reliability & collection techniques
  Email Harvester Lab/  bash/curl/regex recursive scraper
  API Scraping Lab/     Burp + Python
  Geosint Lab/          geolocation & chronolocation (+ material)
  Media Forensics Lab/  synthetic disinformation case (+ generated dataset)
Day_3/                  dark web, blockchain tracing & structured intelligence
  Databreach.pdf             leaked SQL dump analysis (read-only, GDPR)
  Crypto Investigation.pdf   on-chain genealogy of a memecoin
  STIX Lab/                  build + automate a STIX 2.1 threat graph (stix2, agents, dashboard)
  Corporate Watch Lab/       aggregate competitive-intelligence monitor (public sources only)
```

Every lab subject follows the same shape: **learning objectives → scenario → numbered steps with questions → deliverables → grading grid → optional extensions**.

---

## For instructors

Answer keys, French write-ups (`WriteUp_FR_*`), ground-truth files and dataset seeds are **not** in this repository. If you teach with this material and need them, open an issue.

## License

Course content (slides, subjects, templates, cheat sheets) — **CC BY-NC-SA 4.0**. Scripts (`*.py`, `*.sh`, `Dockerfile*`) — **MIT**. Third-party tools and sample files keep their own licenses. © Clement Depernet.
