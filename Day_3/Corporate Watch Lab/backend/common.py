"""Shared schema, source-reliability (Admiralty) map, and the personal-data guard.

DESIGN RULE (compliance): this monitor is ORGANISATION-LEVEL and AGGREGATE only.
Collectors must never emit rows that identify a private individual (a named
employee, a personal profile, a CV). They emit company-level events and
aggregated counts by research domain. `drop_personal` is the last-line guard.
"""
from __future__ import annotations
import hashlib, re
from datetime import datetime, timezone

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]

# Admiralty SOURCE reliability (A-F) by domain. The INFORMATION credibility
# digit (1-6) is deliberately left to the analyst: the machine proposes, the
# human rates. See Day 2, source reliability.
RELIABILITY = {
    "reuters.com": "B", "apnews.com": "B", "bloomberg.com": "B", "wsj.com": "B",
    "ft.com": "B", "theaircurrent.com": "B", "leehamnews.com": "B",
    "flightglobal.com": "B", "aviationweek.com": "B", "janes.com": "B",
    "yahoo.com": "C", "seekingalpha.com": "C", "fool.com": "C", "simpleflying.com": "C",
    "reddit.com": "D", "x.com": "E", "twitter.com": "E", "4chan.org": "E",
}
def reliability_for(url: str) -> str:
    m = re.search(r"https?://([^/]+)/?", url or "")
    host = (m.group(1) if m else "").lower().replace("www.", "")
    for dom, letter in RELIABILITY.items():
        if host.endswith(dom):
            return letter
    return "F"  # undetermined

# Macro-corporate event taxonomy (buy / sell / stop / etc.)
EVENT_RULES = [
    ("M&A / ownership", r"\b(acqui|merg|buyback|buy-back|takeover|stake|majority|controlling)\b"),
    ("Divestiture",     r"\b(divest|spin-?off|sell|sold|exit|offload)\b"),
    ("Contract / order",r"\b(contract|order|deal|award|agreement|selects?|wins?)\b"),
    ("Service / production stop", r"\b(halt|suspend|ground|discontinu|end production|cease|pause|stop)\b"),
    ("Restructuring",   r"\b(layoff|job cut|restructur|reorganis|downsiz)\b"),
    ("Partnership",     r"\b(partnership|joint venture|\bJV\b|MoU|collaborat|team up)\b"),
    ("Financial",       r"\b(earnings|guidance|forecast|revenue|loss|profit|downgrade|upgrade)\b"),
    ("Regulatory / safety", r"\b(FAA|EASA|recall|investigation|inquiry|safety|incident|crash)\b"),
]
def classify_event(text: str) -> str:
    t = (text or "").lower()
    for label, pat in EVENT_RULES:
        if re.search(pat, t):
            return label
    return "General"

# Last-line guard: refuse rows that look like they profile an individual.
PERSONAL_HINT = re.compile(r"(linkedin\.com/in/|/profile/|curriculum vitae|\bCV\b)", re.I)
def drop_personal(rows: list[dict]) -> list[dict]:
    return [r for r in rows if not PERSONAL_HINT.search(" ".join(str(v) for v in r.values()))]

def event_row(source, title, url, published, domain="-", extra=None):
    return {
        "source": source, "title": title.strip(), "url": url,
        "published": published, "event_type": classify_event(title),
        "domain": domain, "reliability": reliability_for(url),
        "info_rating": "-",           # analyst fills 1-6 (Admiralty)
        "id": sha256(url or title), "collected": now_utc(),
        **(extra or {}),
    }
