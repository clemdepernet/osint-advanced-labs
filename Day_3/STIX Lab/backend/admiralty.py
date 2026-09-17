#!/usr/bin/env python3
"""admiralty.py - map the Admiralty scale (Day 2) onto STIX (TP part 4b).

Source reliability A-F and information credibility 1-6 are the analyst's rating.
STIX carries certainty as `confidence` (0-100) and analyst judgement as an
`Opinion` object. This module converts consistently, both ways, so a rating
travels with the finding across tools.
"""
from __future__ import annotations
from stix2 import Opinion, TLP_AMBER

# STIX 2.1 confidence scale <-> Admiralty (Appendix B of the spec uses ranges)
_SOURCE = {"A": 95, "B": 80, "C": 60, "D": 40, "E": 20, "F": 50}   # F = undetermined
_INFO   = {1: 95, 2: 80, 3: 60, 4: 40, 5: 20, 6: 50}
_OPINION = [(90, "strongly-agree"), (70, "agree"), (40, "neutral"),
            (20, "disagree"), (0, "strongly-disagree")]

def rating_to_confidence(rating: str) -> int:
    """'B2' -> a single 0-100 confidence (min of the two axes, the cautious choice)."""
    src, info = rating[0].upper(), int(rating[1])
    return min(_SOURCE[src], _INFO[info])

def rating_to_opinion(rating: str, target_id: str) -> Opinion:
    c = rating_to_confidence(rating)
    label = next(l for thresh, l in _OPINION if c >= thresh)
    return Opinion(explanation=f"Admiralty {rating} -> confidence {c}", opinion=label,
                   object_refs=[target_id], object_marking_refs=[TLP_AMBER])

def confidence_to_band(conf: int) -> str:
    """Reverse: a STIX confidence back to an Admiralty-style source band."""
    for band, val in _SOURCE.items():
        if band != "F" and conf >= val:
            return band
    return "E"

if __name__ == "__main__":
    for r in ["A1", "B2", "C3", "D4", "E5", "F6"]:
        print(f"{r} -> confidence {rating_to_confidence(r):3d} -> band {confidence_to_band(rating_to_confidence(r))}")
