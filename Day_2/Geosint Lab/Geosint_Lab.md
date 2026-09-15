# Geosint Lab

## Lab Assignment: Geolocation & Chronolocation — Operation Glass Eye

**Duration:** 75 min (15 min warm-up, 45 min main case, 15 min verification note)
**Position:** Day 2 afternoon, before the Media Forensics lab. Covers slide 24 (geolocate / chronolocate) and slide 9 (provenance, chain of custody).

### Learning Objectives

By the end of this lab, you will be able to:

- Extract visual clues from a single frame (infrastructure, vegetation, terrain, road furniture) and turn them into search hypotheses.
- Correlate clues with open references: OpenStreetMap and its Overpass API, satellite imagery, Street View, public infrastructure registers.
- Use shadows and the sun's position (SunCalc) to **chronolocate** and to check the coherence of a claimed time.
- Reconstruct an itinerary from several media and their metadata, and say what the metadata does *not* prove.
- Write a **verification note** in which every conclusion carries a confidence level and a source.

### Material

`material/` contains three files. Do not rename them (the hashes are part of the deliverable).

| File | Role |
|---|---|
| `MotoGP.jpg`, `food.jpg` | warm-up: two photos from the same traveller, same day |
| `last_frame.jpg` | main case: last frame transmitted by the drone |

Before anything else, in your case container or on your host:

```bash
sha256sum material/*            # or: shasum -a 256 material/*
exiftool -a -G1 material/*.jpg
```

Write the three hashes and the UTC time of collection at the top of your verification note. This is the chain of custody of slide 9.

---

## Part I — Warm-up: two photos, one day (15 min)

Both photos carry `DateTimeOriginal` 2025-10-05 (12:33 and 19:55). No GPS.

1.1 **MotoGP.jpg**. Identify the circuit, the country and the approximate coordinates of the sign. Which clue settled it, and in how many searches?

1.2 **food.jpg**. Identify the venue (name, town, country). List the clues in the order you used them: text on furniture, architecture, lighting, people, vegetation.

1.3 The two timestamps are 7h22 apart. Is the itinerary physically plausible (distance, transport)? What would make you doubt the metadata anyway (slide 19: an EXIF date is a claim, not proof)?

1.4 Rate each identification with the Admiralty scale (A1 → F6). Justify the *information* digit: what independent second source confirms it?

> **Trap.** The first candidate that "looks right" in a search engine is often in a neighbouring region with the same franchise, the same style or the same brand. Confirm on a second, independent axis (a satellite view, a second photo, a review with a matching detail).

---

## Part II — Main case: Operation Glass Eye (45 min)

### Scenario

You have just assembled and deployed a prototype tactical reconnaissance drone. It carries an encrypted digital video transmitter and a GPS module designed to compute the distance from the extraction point and fly back automatically (failsafe). Under time pressure you launched the first flight **without calibrating the failsafe**. Take-off happened from a temporary deployment zone at:

```
47.5988223, -1.1389015
```

Mid-flight the video feed cut out, probably jamming or a critical failure. Your headset recorder saved the whole flight, including the **last frame** transmitted before the black-out: `material/last_frame.jpg`.

**Objective:** from that last frame, deduce the approximate coordinates of the crash zone, to **three decimals**. Command needs the equipment recovered before hostile forces find it.

### Method (suggested, not imposed)

**Step 1 — Read the frame (5 min).** List every clue before opening a map: number and type of structures, their relative position, the horizon, vegetation, field boundaries, fences, road furniture, the apparent height of the camera. Write down what the frame *cannot* tell you.

**Step 2 — Bound the search area (5 min).** A small drone rarely flies more than a few kilometres from take-off. Draw a circle on a map around the launch point. Which radius do you choose, and why?

**Step 3 — Enumerate candidates (15 min).** The dominant clue in the frame is infrastructure that is mapped in open data. Query OpenStreetMap for every matching object in your circle, for example with the Overpass API:

```bash
# All wind turbines within 8 km of the launch point, as CSV (lat, lon, name, operator)
curl -s "https://overpass-api.de/api/interpreter" --data-urlencode \
 'data=[out:csv(::lat,::lon,name,operator;true;",")][timeout:50];
  node["generator:source"="wind"](around:8000,47.5988223,-1.1389015);out;'
```

Alternatives if the API is slow: https://overpass-turbo.eu (same query, visual), The Wind Power database, the regional register of ICPE installations (wind farms are classified installations in France), or simply the "wind turbine" layer in OpenInfraMap.

**Step 4 — Discriminate (15 min).** For each candidate, check against the frame: how many turbines are visible from a road nearby, what is behind them (tree line, hedgerows, buildings), and from which direction they present this exact silhouette. Use satellite imagery and Street View. The frame is a ground-level view: find the road segment and the viewing direction.

**Step 5 — Conclude (5 min).** Give the crash zone coordinates to three decimals, the estimated viewing direction, your confidence level, and the one observation that would make you change your mind.

### Questions

2.1 How many candidate turbines did your enumeration return? How did you rank them?

2.2 Which candidate did you retain, and which **two** independent observations confirm it (not one)?

2.3 The frame is a road-level view. Where was the *camera* (the drone) and where is the *turbine*? Which of the two is the crash zone, and why?

2.4 **Chronolocation.** Estimate the time of day and the season from the frame (sun height, shadow direction if any, vegetation). Then use SunCalc at your candidate location: is the lighting compatible with a flight on the date of the mission? What if the frame carried an EXIF date that contradicted your estimate?

2.5 The frame contains no EXIF data. Is that evidence of manipulation? Refer to slide 19.

2.6 Distance from the launch point to your crash zone: compute it. Is it compatible with the drone's plausible range and with your Step 2 radius?

---

## Part III — Verification note (15 min)

Fill `templates/verification_note.md`. One page. It must contain:

1. **Chain of custody**: file names, SHA-256, UTC collection time, tools used.
2. **Warm-up**: the two locations with coordinates, ratings and sources.
3. **Main case**: crash zone coordinates (3 decimals), viewing direction, distance from launch, confidence level, alternative candidates rejected and why.
4. **Chronolocation**: estimated time window and its compatibility with the mission.
5. **What the evidence does not prove.**
6. **Graded verdict** for the geolocation: confirmed / probable / possible / unverifiable.

---

## Submission Deliverables

One zip `GEOSINT_<team>.zip` with:

1. `verification_note.md` (or PDF), completed.
2. One annotated screenshot per identification (warm-up ×2, main case ×1): the frame next to the matching satellite/Street View, clues circled.
3. The exact Overpass (or equivalent) query you used and its raw result.

### Grading grid (100 pts)

| Item | Points | What earns the points |
|---|---|---|
| Warm-up identifications | 20 | both venues correct, coordinates, second-source confirmation |
| Clue extraction | 10 | complete list before searching, including what the frame cannot tell |
| Candidate enumeration | 15 | reproducible query, sensible radius, all candidates listed |
| Discrimination | 25 | correct crash zone to 3 decimals, two independent confirmations, viewing direction |
| Chronolocation | 10 | sun/shadow reasoning, SunCalc used, coherence stated |
| Verification note | 15 | hashes, ratings, rejected alternatives, "does not prove" section |
| Malus | −5 each | a coordinate given without a source; a rating A1 without a second source |

---

## Optional Extensions (Bonus)

- **Automate the enumeration**: a Python script that takes (lat, lon, radius, OSM tag) and returns candidates sorted by distance, with a link to Street View for each.
- **Compute the viewing azimuth**: from the retained turbine and the road segment, compute the bearing and check it against the sun position at the estimated time.
- **Cross-check with the ICPE register**: find the official authorisation of the wind farm (operator, commissioning date, hub height). Does the hub height match the apparent size in the frame?
- **Reverse the warm-up**: starting from the venue coordinates, find a Google Maps or review photo that shows the same tables. Rate the confirmation.
