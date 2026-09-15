# Media Forensics Lab

## Lab Assignment: Authenticate & Dismantle — Operation Riverbank

**Duration:** 3h (five workshops of 30-40 min, then the verification note)
**Position:** Day 2 afternoon, after the Geosint lab. Covers slides 18 to 31.

### Learning Objectives

By the end of this lab, you will be able to:

- Read image metadata **for inconsistencies**, not for "proof", and compare an embedded thumbnail with the visible image.
- Run and interpret an **Error Level Analysis** and a **physical coherence** check (shadows, light).
- Trace a media back to its **first occurrence** and read **Content Credentials (C2PA)**.
- Dissect a video: container metadata, keyframes, hidden cuts, spliced frames.
- Detect **coordinated inauthentic behaviour** in a post dataset with pandas and NetworkX.
- Write a **verification note** whose verdict rests on the weight of evidence, never on one test.

### Scenario

On 12 March 2026 at 09:00 UTC, the account `@riverwatch_press` posts a photo and a short video: "BREAKING - Maashaven quay in Rotterdam under water this morning. Authorities silent. Share before it's deleted!" Within minutes the post is everywhere. A newsroom asks your team for a verification note before noon.

You receive a folder `dataset/` with five sub-folders, one per workshop. Every file in it is **synthetic**: no real person, no real place is depicted. The instructor holds the ground truth. The point is not to guess "fake" (you already suspect it); the point is to **prove what you can, grade what you cannot, and document both**.

### Setup (10 min)

```bash
# host or case container
pip install pillow pandas numpy networkx           # analysis
exiftool -ver ; ffprobe -version | head -1        # brew install exiftool ffmpeg  /  apt install libimage-exiftool-perl ffmpeg mediainfo
sha256sum dataset/*/* 2>/dev/null > hashes.txt    # chain of custody first (slide 9)
```

Optional GUI helpers: Forensically (https://29a.ch/photo-forensics), FotoForensics, InVID/WeVerify browser extension.

---

## Workshop A — Metadata & structure (30 min)

Files: `A_metadata/riverbank_report.jpg`, `A_metadata/caption.txt`

```bash
exiftool -a -G1 A_metadata/riverbank_report.jpg
exiftool -GPS:All -DateTimeOriginal -CreateDate -Software -Make -Model -Artist -ImageDescription A_metadata/riverbank_report.jpg
python3 scripts/ela.py A_metadata/riverbank_report.jpg --thumb     # extracts the embedded thumbnail
```

A.1 List every metadata field that **contradicts** the caption or another field. There are at least four. For each: which two elements disagree, and what does the disagreement suggest?

A.2 Open the extracted thumbnail next to the visible image. What differs? What does an embedded thumbnail record, and when is it generated?

A.3 Convert the GPS coordinates to a place. Does it match "Rotterdam"? Rate this finding (Admiralty) and say what it does **not** prove (slide 19: metadata is forgeable).

A.4 If the platform had stripped all EXIF (as most social networks do), which of your four findings would survive? What would you do instead?

---

## Workshop B — Signal & physical coherence (40 min)

Files: `B_signal/riverbank_spliced.jpg`, `B_signal/riverbank_shadows.jpg`

### B1. Error Level Analysis

```bash
python3 scripts/ela.py B_signal/riverbank_spliced.jpg --quality 90
python3 scripts/ela.py B_signal/riverbank_spliced.jpg --quality 75 --grid
```

B.1 Describe what you see in the ELA output. Which region has a different compression history? Give its approximate pixel coordinates (x, y, width, height).

B.2 Now run ELA on the sky region mentally: why do uniform areas always look dark and edges always look bright? Give one example of a *false positive* ELA would produce on a genuine photo.

B.3 Copy-move: the pasted region exists twice in the image. Find its source. Which simple test (visual or computational) confirms a copy-move?

### B2. Shadows and light

B.4 In `riverbank_shadows.jpg`, every object casts a shadow. One object is inconsistent. Which one, and how did you determine the light direction of the rest of the scene?

B.5 Explain why this kind of inconsistency is often **more telling than pixel analysis** (slide 21), and why a skilled forger could still defeat your ELA but not this test easily.

B.6 If the scene were real and geolocated, how would you use SunCalc to turn the shadow direction into a time window? (You will do this on real material in the Geosint lab.)

---

## Workshop C — Recontextualisation & provenance (35 min)

Files: `C_provenance/README.md`, `C_provenance/recontext/photo.jpg` + `claim.txt` (given by the instructor)

### C1. Reverse image search

C.1 Find the **first occurrence** of `photo.jpg` online: date, place, author, original context. Use at least three engines (Google Lens, Yandex, TinEye sorted by oldest, Bing). Which one found it, and which ones failed?

C.2 Compare with `claim.txt`. Is the image fake, or **real but recontextualised** (slide 25)? Write the graded verdict: authentic / misleading / manipulated / synthetic / unverifiable.

C.3 Archive your proof: URL of the first occurrence, Wayback Machine snapshot, SHA-256 of your local copy, UTC time. This is the provenance block of your note.

### C2. Content Credentials (C2PA)

Open https://c2pa.org/public-testfiles/image/ and pick three files (one signed, one edited after signing, one without manifest). Verify each on https://contentcredentials.org/verify (or with `c2patool`).

C.4 For each file: is the manifest valid? What does the manifest record (device, software, edits)?

C.5 Slide 23: "Absence ≠ fake." Write in one sentence what the *absence* of a manifest allows you to conclude, and what it does not.

---

## Workshop D — Video forensics (35 min)

File: `D_video/riverbank_clip.mp4`

```bash
ffprobe -hide_banner D_video/riverbank_clip.mp4
ffprobe -v quiet -print_format json -show_format -show_streams D_video/riverbank_clip.mp4 | head -60
mkdir -p frames && ffmpeg -i D_video/riverbank_clip.mp4 -vf fps=2 frames/kf_%03d.png
# scene-change score of EVERY frame (a cut = a spike). Start with the raw scores, then choose your threshold.
ffmpeg -i D_video/riverbank_clip.mp4 -vf "select='gte(scene,0)',metadata=print:file=-" -f null - 2>/dev/null | grep -E "pts_time|scene_score" | paste - -
ffmpeg -i D_video/riverbank_clip.mp4 -vf "select=gt(scene,0.1),showinfo" -f null - 2>&1 | grep pts_time
```

> The slide uses `gt(scene,0.4)`, the usual value for real footage. Fixed-camera footage with small changes needs a lower threshold: read the score distribution before picking one, and say in your note which threshold you used and why.

D.1 Container metadata: which fields are suspicious (creation time vs the burned-in clock, editing software)? Rate them.

D.2 The clip contains a **hidden cut**. Find it: at which second, and how do you know (scene-change score, burned-in clock, object position)? How much time is missing?

D.3 The clip also contains a **spliced still frame** from another file. Which frames, and from which file of the dataset? Prove it (hash of the frame vs a resized source, or a visual diff).

D.4 Slide 25: there is no reliable video reverse search. Extract the keyframes and describe how you would reverse-search them. Which keyframes would you pick, and why not all of them?

---

## Workshop E — Coordinated inauthentic behaviour (40 min)

Files: `E_cib/accounts.csv`, `E_cib/posts.csv`, `E_cib/edges.csv`

Starter (slide 30):

```python
import pandas as pd, difflib, networkx as nx
acc = pd.read_csv("E_cib/accounts.csv")
posts = pd.read_csv("E_cib/posts.csv"); posts["ts"] = pd.to_datetime(posts["timestamp"], utc=True)

acc["creation_date"].value_counts().head()                                   # creation burst
posts.groupby(posts["ts"].dt.floor("min")).size().sort_values(ascending=False).head()   # post synchronisation
seed = posts.loc[posts.user_id == "u9000", "text"].iloc[0]
posts["sim"] = posts["text"].apply(lambda t: difflib.SequenceMatcher(None, seed, t).ratio())   # near-duplicates

G = nx.from_pandas_edgelist(pd.read_csv("E_cib/edges.csv"), "source", "target", create_using=nx.DiGraph)
nx.in_degree_centrality(G)                                                   # who gets amplified
```

E.1 **Timing.** Find the creation burst (which days, how many accounts) and the posting burst (which minutes). How do they relate to the seed post at 09:00 UTC?

E.2 **Content.** Flag every post with similarity > 0.85 to the seed text that is not the seed itself. How many accounts? Are they the same accounts as in E.1?

E.3 **Profile signature.** Build a simple score from `followers`, `following`, `bio_len`, `has_photo`, `utc_offset`, `posts_total`. Which threshold separates the cluster? What is the false-positive rate on organic accounts?

E.4 **Network.** Draw (or describe) the amplification graph: who is the origin, who relays, who amplifies? Export a Gephi-readable file (`nx.write_gexf`) and identify the dense cluster.

E.5 **Contamination.** Some organic accounts also reposted the seed. Why must they **not** be flagged as coordinated? What distinguishes them in the data?

E.6 Give the final list of coordinated account IDs with your confidence per signal. The instructor will score precision and recall.

---

## Verification note (20 min)

Fill `templates/verification_note.md`. It must contain, for the whole "Riverbank" claim:

1. Chain of custody (files, hashes, UTC, tools).
2. One paragraph per axis: **metadata**, **signal**, **physical coherence**, **provenance**, **video**, **coordination**, each with its findings and an Admiralty rating.
3. **Divergences**: where did the axes disagree, or where did a test fail?
4. **Graded verdict** for the photo, for the video, and for the campaign: authentic / misleading / manipulated / synthetic / unverifiable.
5. **Weight of evidence**: one sentence explaining why the verdict does not rest on a single test (slide 16).
6. What you would need to move the verdict one step up or down.

---

## Submission Deliverables

One zip `RIVERBANK_<team>.zip` with:

1. `verification_note.md` (or PDF).
2. `hashes.txt` and the ELA outputs you relied on.
3. `cib_analysis.py` (or notebook) producing your flagged account list, plus the `.gexf` graph.
4. Keyframes you selected for reverse search (max 6) with one line each on why.

### Grading grid (100 pts)

| Item | Points | What earns the points |
|---|---|---|
| A. Metadata | 15 | four inconsistencies found, thumbnail comparison, "does not prove" stated |
| B. Signal & shadows | 20 | ELA region located, copy-move source found, inconsistent object identified, false-positive reasoning |
| C. Provenance & C2PA | 15 | first occurrence with date, archived proof, three C2PA cases read correctly |
| D. Video | 15 | cut located to the second, missing time estimated, splice traced to its source file |
| E. CIB | 20 | precision and recall on flagged accounts, contamination not flagged, graph delivered |
| Verification note | 15 | one paragraph per axis, ratings, divergences, graded verdicts, weight of evidence |
| Malus | −5 each | a verdict stated without the supporting axis; a rating with no source |

---

## Optional Extensions (Bonus)

- **JPEG ghosts**: re-save the spliced image at every quality from 50 to 100 and plot the mean ELA per region. The pasted region shows a minimum at its original quality.
- **PRNU-lite**: compute the noise residual (image minus a denoised copy) and compare the local variance inside and outside the pasted region.
- **Automated cut detection**: write a Python script that computes frame-to-frame histogram distance and flags outliers, then compare with ffmpeg's scene score.
- **Timeline**: put every dated fact of the case (EXIF date, caption date, video creation time, burned-in clock, account creation, posting burst) on one timeline. Which dates are mutually impossible?
- **Narrative analysis** (slide 15): from `posts.csv`, describe the narrative pushed, the intended audience, the channels. Who benefits?
