"""Macro-corporate news + aviation press via keyless RSS. Organisation-level only."""
from __future__ import annotations
import urllib.request, urllib.parse, re, xml.etree.ElementTree as ET
import common

UA = {"User-Agent": "corporate-watch/1.0 (OSINT training)"}

def _get(url: str, timeout=25) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

def _items(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        t = it.findtext("title") or ""
        link = it.findtext("link") or ""
        pub = it.findtext("pubDate") or ""
        # Google News wraps the real source as "Title - Source"
        yield t, link, pub

def google_news(company: str, extra_terms: str, limit=40):
    q = f'{company} ({extra_terms})'
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    rows = []
    try:
        for t, link, pub in _items(_get(url)):
            rows.append(common.event_row("Google News", t, link, pub))
            if len(rows) >= limit: break
    except Exception as e:
        print(f"[news] google_news failed: {e}")
    return rows

# Keyless aviation-press RSS feeds (organisation/market level).
PRESS = {
    "The Air Current": "https://theaircurrent.com/feed/",
    "Leeham News": "https://leehamnews.com/feed/",
    "AviationWeek": "https://aviationweek.com/rss.xml",
}
def aviation_press(company: str, limit_per_feed=15):
    rows = []
    for name, url in PRESS.items():
        try:
            for t, link, pub in _items(_get(url)):
                if company.lower() in t.lower():
                    rows.append(common.event_row(name, t, link, pub))
                if len([r for r in rows if r["source"] == name]) >= limit_per_feed:
                    break
        except Exception as e:
            print(f"[news] {name} failed: {e}")
    return rows

def collect(company="Boeing"):
    terms = "contract OR acquisition OR divestiture OR order OR layoffs OR partnership OR halt OR FAA OR earnings"
    rows = google_news(company, terms) + aviation_press(company)
    return common.drop_personal(rows)
