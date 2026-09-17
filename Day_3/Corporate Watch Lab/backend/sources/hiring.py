"""Aggregate hiring-DEMAND signal by research domain, from PUBLIC job-posting
*counts* only. It never returns a person: it answers 'how much is the company
hiring in domain X', not 'who'. Uses Google News/careers mentions as a keyless
proxy; swap in an official jobs API (with a key) for production."""
from __future__ import annotations
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import common

UA = {"User-Agent": "corporate-watch/1.0"}
DOMAINS = ["composites", "avionics", "propulsion", "hypersonics", "autonomy",
           "sustainable aviation fuel", "cybersecurity", "additive manufacturing"]

def _count(company, domain):
    q = f'{company} hiring OR jobs OR careers "{domain}"'
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    try:
        root = ET.fromstring(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=25).read())
        return sum(1 for _ in root.iter("item"))
    except Exception:
        return 0

def collect(company="Boeing"):
    return [{"domain": d, "demand_signal": _count(company, d)} for d in DOMAINS]
