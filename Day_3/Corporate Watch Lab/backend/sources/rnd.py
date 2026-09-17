"""R&D capability map from OpenAlex (keyless). AGGREGATE ONLY: we keep counts by
research concept and by year, and deliberately DISCARD author identities."""
from __future__ import annotations
import urllib.request, urllib.parse, json
import common

BASE = "https://api.openalex.org"
MAIL = "osint-course@example.com"
# Boeing (United States) institution id on OpenAlex
BOEING = "I1295339012"

def _get(path, params):
    params = {**params, "mailto": MAIL}
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "corporate-watch/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def concepts(since="2023-01-01", top=14):
    d = _get("works", {"filter": f"authorships.institutions.lineage:{BOEING},from_publication_date:{since}",
                        "group_by": "concepts.id"})
    out = []
    for g in d.get("group_by", []):
        name = g.get("key_display_name", "")
        if name.lower() in ("engineering", "computer science", "materials science", "physics",
                            "mathematics", "business", "biology", "chemistry"):
            pass  # keep megaconcepts too; the analyst can filter. Comment out to drop.
        out.append({"domain": name, "works": g["count"]})
    out = [o for o in out if o["domain"]][:top]
    return out

def yearly(since_year=2019):
    d = _get("works", {"filter": f"authorships.institutions.lineage:{BOEING},from_publication_date:{since_year}-01-01",
                       "group_by": "publication_year"})
    series = sorted(({"year": int(g["key"]), "works": g["count"]}
                     for g in d.get("group_by", []) if g["key"].isdigit() and int(g["key"]) <= 2027),
                    key=lambda x: x["year"])
    return series

def collect():
    return {"concepts": concepts(), "yearly": yearly(),
            "note": "Aggregated Boeing-affiliated publication counts (OpenAlex). No author identities stored."}
