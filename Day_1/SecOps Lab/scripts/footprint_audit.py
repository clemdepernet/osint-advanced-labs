#!/usr/bin/env python3
"""
footprint_audit.py - Audit the digital footprint of an identifier set.

Two use cases in the lab:
  1. YOUR real footprint (what to reduce before you start investigating).
  2. The PERSONA footprint, before first use (collision check) and after
     ageing (does the persona look like we planned?).

Checks performed:
  --username  -> sherlock        : where does this handle already exist?
  --email     -> holehe          : which services is this email registered on?
  --email     -> HIBP breaches   : only if HIBP_API_KEY is set (paid API)
  --password  -> Pwned Passwords : k-anonymity API (only 5 chars of the SHA-1
                                   hash leave your machine). Free, no key.

Usage:
  python3 footprint_audit.py --username jdupont78 --email jdupont78@proton.me --password-prompt
  python3 footprint_audit.py --username jdupont78 --proxy socks5h://127.0.0.1:9050   # via Tor
  python3 footprint_audit.py --email me@example.com --out reports/me.md

Requirements:
  pip install requests
  pipx install sherlock-project holehe
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("[!] requests is missing. Install it with:  pip install requests")

UA = "footprint-audit/1.0 (OSINT training lab)"


def run(cmd: list[str], env: dict | None = None, timeout: int = 600) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return res.stdout + res.stderr
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return "[timeout]"


# ------------------------------------------------------------------ username
def check_username(username: str, proxy: str | None) -> list[str]:
    if not shutil.which("sherlock"):
        print("[!] sherlock not installed (pipx install sherlock-project) - skipping")
        return []
    print(f"[*] sherlock: looking for '{username}' on ~400 sites...")
    cmd = ["sherlock", username, "--print-found", "--timeout", "10", "--no-color", "--no-txt"]
    if proxy:
        cmd += ["--proxy", proxy]
    out = run(cmd)
    return [line.split()[-1] for line in out.splitlines() if line.startswith("[+]")]


# ------------------------------------------------------------------ email
def check_email_holehe(email: str, proxy: str | None) -> list[str]:
    if not shutil.which("holehe"):
        print("[!] holehe not installed (pipx install holehe) - skipping")
        return []
    print(f"[*] holehe: checking which services know '{email}'...")
    env = os.environ.copy()
    if proxy:  # holehe uses httpx, which honours proxy env vars
        env["HTTPS_PROXY"] = proxy
        env["HTTP_PROXY"] = proxy
    out = run(["holehe", email, "--only-used", "--no-color"], env=env)
    return [line.split()[1] for line in out.splitlines() if line.startswith("[+]")]


def check_email_hibp(email: str, proxy: str | None) -> list[str] | None:
    key = os.getenv("HIBP_API_KEY")
    if not key:
        print("[i] HIBP_API_KEY not set - skipping breach lookup (paid API, https://haveibeenpwned.com/API/Key)")
        return None
    print("[*] Have I Been Pwned: breach lookup...")
    r = requests.get(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
        headers={"hibp-api-key": key, "user-agent": UA},
        params={"truncateResponse": "true"},
        proxies={"https": proxy} if proxy else None,
        timeout=20,
    )
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return [b["Name"] for b in r.json()]


# ------------------------------------------------------------------ password
def check_password_pwned(password: str, proxy: str | None) -> int:
    """k-anonymity: send only the first 5 hex chars of SHA-1, match the suffix locally."""
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    print(f"[*] Pwned Passwords: querying range {prefix}***** (suffix never leaves this machine)")
    r = requests.get(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        headers={"user-agent": UA, "Add-Padding": "true"},
        proxies={"https": proxy} if proxy else None,
        timeout=20,
    )
    r.raise_for_status()
    for line in r.text.splitlines():
        h, _, count = line.partition(":")
        if h == suffix:
            return int(count)
    return 0


# ------------------------------------------------------------------ report
def build_report(args, sites, services, breaches, pwned) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [f"# Footprint audit - {now}", ""]
    md += [f"- Mode: **{args.mode}**", f"- Proxy: `{args.proxy or 'none (direct)'}`", ""]

    if args.username:
        md += [f"## Username `{args.username}`", ""]
        if sites:
            md += [f"Found on **{len(sites)}** site(s):", ""] + [f"- {s}" for s in sites]
            if args.mode == "persona":
                md += ["", "> **Collision.** Someone already uses this handle. Change it: confusion with a real "
                       "person is both an ethical problem and an attribution risk."]
            else:
                md += ["", "> Each hit is a place where an adversary can pivot. Decide: delete, rename, or private."]
        else:
            md += ["No hit on the sherlock site list." + (" Good: handle is free." if args.mode == "persona" else "")]
        md += [""]

    if args.email:
        md += [f"## Email `{args.email}`", ""]
        if services:
            md += [f"Registered on **{len(services)}** service(s) (holehe):", ""] + [f"- {s}" for s in services]
        else:
            md += ["holehe: no registered service detected (or tool skipped)."]
        if breaches is not None:
            md += ["", f"Breaches (HIBP): **{len(breaches)}**"] + [f"- {b}" for b in breaches]
        md += [""]

    if pwned is not None:
        md += ["## Password", ""]
        if pwned:
            md += [f"**Seen {pwned:,} times** in known breaches. NEVER use it for a persona (nor for yourself)."]
        else:
            md += ["Not present in Pwned Passwords. (Still: unique per persona, stored in a vault.)"]
        md += [""]

    md += ["## What to do with this", ""]
    if args.mode == "persona":
        md += ["- Zero collision on the handle before creating accounts.",
               "- Email must return nothing on holehe before first use, then ONLY the platforms you created.",
               "- Re-run after the ageing period and compare."]
    else:
        md += ["- List every hit in your reduction plan: delete / rename / lock down / accept.",
               "- Old forum accounts and reused handles are the #1 pivot from persona to real identity.",
               "- Re-run in 30 days and measure the delta."]
    return "\n".join(md) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--username")
    ap.add_argument("--email")
    ap.add_argument("--password-prompt", action="store_true", help="prompt for a password to test (never passed as argument)")
    ap.add_argument("--mode", choices=["real", "persona"], default="persona",
                    help="'real' = your own footprint to reduce, 'persona' = collision check")
    ap.add_argument("--proxy", help="e.g. socks5h://127.0.0.1:9050 to route through Tor")
    ap.add_argument("--out", help="write the Markdown report here")
    args = ap.parse_args()

    if not (args.username or args.email or args.password_prompt):
        ap.error("give at least --username, --email or --password-prompt")

    sites = check_username(args.username, args.proxy) if args.username else []
    services = check_email_holehe(args.email, args.proxy) if args.email else []
    breaches = check_email_hibp(args.email, args.proxy) if args.email else None
    pwned = None
    if args.password_prompt:
        pwd = getpass.getpass("Password to test (hidden): ")
        pwned = check_password_pwned(pwd, args.proxy)

    report = build_report(args, sites, services, breaches, pwned)
    print("\n" + report)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report)
        print(f"[+] report written to {args.out}")


if __name__ == "__main__":
    main()
