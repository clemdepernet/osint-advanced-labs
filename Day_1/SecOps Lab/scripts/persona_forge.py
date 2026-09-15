#!/usr/bin/env python3
"""
persona_forge.py - Generate a coherent, compartmentalised research persona sheet.

A persona is NOT a fake name. It is a consistent identity: locale, timezone,
age, job, interests and, above all, a strict compartmentalisation plan
(1 persona = 1 email / 1 phone / 1 browser profile / 1 VM / 1 network exit).

Usage:
    python3 persona_forge.py --locale fr_FR --case CASE-042
    python3 persona_forge.py --locale en_GB --gender F --min-age 30 --max-age 45 --check
    python3 persona_forge.py --list-locales

Options:
    --check      run `sherlock` on the generated username to detect collisions
                 (someone else already using the handle = attribution risk)
    --out DIR    where to write <username>.md and <username>.json (default: ./personas)

Requirements:
    pip install faker
    (optional) pipx install sherlock-project
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    from faker import Faker
except ImportError:  # pragma: no cover
    sys.exit("[!] Faker is missing. Install it with:  pip install faker")

# Locale -> (timezone, country, default UI language, plausible email providers)
LOCALES: dict[str, dict] = {
    "fr_FR": {"tz": "Europe/Paris", "country": "France", "lang": "fr-FR",
              "mail": ["proton.me", "tuta.com", "laposte.net"]},
    "en_GB": {"tz": "Europe/London", "country": "United Kingdom", "lang": "en-GB",
              "mail": ["proton.me", "tuta.com", "outlook.com"]},
    "en_US": {"tz": "America/New_York", "country": "United States", "lang": "en-US",
              "mail": ["proton.me", "tuta.com", "outlook.com"]},
    "de_DE": {"tz": "Europe/Berlin", "country": "Germany", "lang": "de-DE",
              "mail": ["proton.me", "tuta.com", "gmx.de", "web.de"]},
    "es_ES": {"tz": "Europe/Madrid", "country": "Spain", "lang": "es-ES",
              "mail": ["proton.me", "tuta.com", "outlook.es"]},
    "it_IT": {"tz": "Europe/Rome", "country": "Italy", "lang": "it-IT",
              "mail": ["proton.me", "tuta.com", "libero.it"]},
    "nl_NL": {"tz": "Europe/Amsterdam", "country": "Netherlands", "lang": "nl-NL",
              "mail": ["proton.me", "tuta.com", "outlook.com"]},
    "pl_PL": {"tz": "Europe/Warsaw", "country": "Poland", "lang": "pl-PL",
              "mail": ["proton.me", "tuta.com", "wp.pl", "o2.pl"]},
    "pt_BR": {"tz": "America/Sao_Paulo", "country": "Brazil", "lang": "pt-BR",
              "mail": ["proton.me", "tuta.com", "outlook.com"]},
}

INTERESTS = [
    "trail running", "board games", "vintage synthesizers", "urban photography",
    "home brewing", "bouldering", "sci-fi novels", "retro gaming", "cycling",
    "houseplants", "amateur astronomy", "3D printing", "chess", "fishing",
    "electronic music", "hiking", "cooking", "football", "motorbikes", "sewing",
]

JOBS = [
    "logistics coordinator", "junior accountant", "web designer", "nurse",
    "sales representative", "warehouse team lead", "primary school teacher",
    "HR assistant", "IT support technician", "graphic designer", "real estate agent",
    "delivery driver", "customer support agent", "civil engineering technician",
]


def build_username(first: str, last: str, birth_year: int) -> str:
    """Realistic handle: people mix name fragments with a number (year, day...)."""
    f = "".join(c for c in first.lower() if c.isalnum())
    l = "".join(c for c in last.lower() if c.isalnum())
    patterns = [
        f"{f}.{l}{str(birth_year)[2:]}",
        f"{f[0]}{l}{random.randint(10, 99)}",
        f"{f}{l[:3]}_{str(birth_year)[2:]}",
        f"{l}.{f}",
        f"{f}_{l}{random.randint(1, 9)}",
    ]
    return random.choice(patterns)


def forge(locale: str, gender: str | None, min_age: int, max_age: int, case: str) -> dict:
    meta = LOCALES[locale]
    fake = Faker(locale)
    Faker.seed()  # fresh randomness each run

    if gender is None:
        gender = random.choice(["M", "F"])
    first = fake.first_name_male() if gender == "M" else fake.first_name_female()
    last = fake.last_name()

    today = date.today()
    age = random.randint(min_age, max_age)
    dob = today - timedelta(days=age * 365 + random.randint(0, 364))
    username = build_username(first, last, dob.year)
    city = fake.city()
    interests = random.sample(INTERESTS, 3)

    # Ageing plan: an account created yesterday looks suspicious. Spread activity.
    ageing_start = today - timedelta(days=random.randint(45, 120))

    return {
        "case": case,
        "created_on": today.isoformat(),
        "identity": {
            "first_name": first,
            "last_name": last,
            "gender": gender,
            "date_of_birth": dob.isoformat(),
            "age": age,
            "city": city,
            "country": meta["country"],
            "job": random.choice(JOBS),
            "interests": interests,
            "writing_style": random.choice([
                "short sentences, few capitals, no emojis",
                "polite, full sentences, occasional typo",
                "casual, uses '...' a lot, one emoji max",
            ]),
        },
        "digital": {
            "username": username,
            "email_hint": f"{username}@{random.choice(meta['mail'])}",
            "ui_language": meta["lang"],
            "timezone": meta["tz"],
            "active_hours_local": random.choice(["07:00-09:00 & 19:00-23:00",
                                                 "12:00-14:00 & 21:00-00:00",
                                                 "06:30-08:00 & 18:00-22:00"]),
            "device_story": random.choice(["Android mid-range phone + Windows laptop",
                                           "iPhone + Windows laptop",
                                           "Android phone only"]),
        },
        "compartmentalisation": {
            "email": "dedicated mailbox, created FROM the persona VM/exit, never opened elsewhere",
            "phone": "dedicated prepaid SIM or virtual number, never used by another persona",
            "password": "unique, generated, stored in a dedicated vault entry",
            "browser": f"dedicated browser profile / container named '{username}'",
            "vm_or_container": f"disposable container 'osint-{case.lower()}' (osint_case.sh)",
            "network_exit": "one exit only (VPN X or Tor). Never log in from the real IP.",
            "photo": "NEVER a real photo, NEVER a stock photo (reverse image search). "
                     "Use a generated face or no photo.",
        },
        "ageing_plan": {
            "start": ageing_start.isoformat(),
            "rules": [
                "week 1-2: create accounts, fill profile, follow 10-20 mainstream pages",
                "week 3-6: like/comment 2-3 times a week, in the persona's language and hours",
                "never touch the target before the persona is at least 4-6 weeks old",
                "log every action (date, platform, action) in the persona log",
            ],
        },
    }


def to_markdown(p: dict) -> str:
    i, d, c = p["identity"], p["digital"], p["compartmentalisation"]
    lines = [
        f"# Persona sheet - {i['first_name']} {i['last_name']} ({p['case']})",
        "",
        f"_Generated {p['created_on']}. Classification: CASE-RESTRICTED. Never store next to your real identity._",
        "",
        "## 1. Identity (the legend)",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Name | {i['first_name']} {i['last_name']} |",
        f"| Gender | {i['gender']} |",
        f"| Date of birth | {i['date_of_birth']} ({i['age']} y/o) |",
        f"| Lives in | {i['city']}, {i['country']} |",
        f"| Job | {i['job']} |",
        f"| Interests | {', '.join(i['interests'])} |",
        f"| Writing style | {i['writing_style']} |",
        "",
        "## 2. Digital footprint (must all be consistent)",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Username | `{d['username']}` |",
        f"| Email (to create) | `{d['email_hint']}` |",
        f"| UI language | {d['ui_language']} |",
        f"| Timezone | {d['timezone']} |",
        f"| Active hours (local) | {d['active_hours_local']} |",
        f"| Device story | {d['device_story']} |",
        "",
        "## 3. Compartmentalisation plan",
        "",
    ]
    lines += [f"- **{k}**: {v}" for k, v in c.items()]
    lines += [
        "",
        "## 4. Ageing plan",
        "",
        f"Start: {p['ageing_plan']['start']}",
        "",
    ]
    lines += [f"- {r}" for r in p["ageing_plan"]["rules"]]
    lines += [
        "",
        "## 5. Persona log",
        "",
        "| Date (UTC) | Platform | Action | Exit IP / country | Notes |",
        "|---|---|---|---|---|",
        "| | | | | |",
        "",
        "## 6. Anti-correlation checklist (tick before first use)",
        "",
        "- [ ] Username collision check done (`footprint_audit.py --username`)",
        "- [ ] Email created from the persona environment only",
        "- [ ] Password unique and not in Pwned Passwords",
        "- [ ] Browser fingerprint tested (coveryourtracks / amiunique) from the persona browser",
        "- [ ] Timezone & language of the VM match the persona",
        "- [ ] No real photo, no stock photo",
        "- [ ] Legal perimeter validated (who authorised the persona, for what case)",
    ]
    return "\n".join(lines) + "\n"


def sherlock_check(username: str) -> list[str]:
    if not shutil.which("sherlock"):
        print("[!] sherlock not found (pipx install sherlock-project). Skipping collision check.")
        return []
    print(f"[*] Checking handle collisions for '{username}' with sherlock (this takes ~1 min)...")
    res = subprocess.run(
        ["sherlock", username, "--print-found", "--timeout", "10", "--no-color", "--no-txt"],
        capture_output=True, text=True,
    )
    found = [l.split()[-1] for l in res.stdout.splitlines() if l.startswith("[+]")]
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", default="fr_FR", choices=sorted(LOCALES))
    ap.add_argument("--gender", choices=["M", "F"])
    ap.add_argument("--min-age", type=int, default=24)
    ap.add_argument("--max-age", type=int, default=52)
    ap.add_argument("--case", default="CASE-001", help="case identifier (used for container name)")
    ap.add_argument("--out", default="personas")
    ap.add_argument("--check", action="store_true", help="run sherlock collision check on the username")
    ap.add_argument("--list-locales", action="store_true")
    args = ap.parse_args()

    if args.list_locales:
        for k, v in LOCALES.items():
            print(f"{k:6}  {v['country']:15} {v['tz']}")
        return

    persona = forge(args.locale, args.gender, args.min_age, args.max_age, args.case)
    username = persona["digital"]["username"]

    if args.check:
        hits = sherlock_check(username)
        persona["collision_check"] = {"tool": "sherlock", "found_on": hits}
        if hits:
            print(f"[!] Handle '{username}' already exists on {len(hits)} site(s): {', '.join(hits[:8])}")
            print("    -> re-run the generator or change the handle. A colliding handle = confusion + attribution risk.")
        else:
            print(f"[+] Handle '{username}' has no collision on the sherlock site list.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{username}.json").write_text(json.dumps(persona, indent=2, ensure_ascii=False))
    (out / f"{username}.md").write_text(to_markdown(persona))
    print(f"[+] Persona written to {out / (username + '.md')} and .json")
    print(f"    {persona['identity']['first_name']} {persona['identity']['last_name']}, "
          f"{persona['identity']['age']} y/o, {persona['identity']['city']} ({persona['digital']['timezone']}) "
          f"-> @{username}")


if __name__ == "__main__":
    main()
