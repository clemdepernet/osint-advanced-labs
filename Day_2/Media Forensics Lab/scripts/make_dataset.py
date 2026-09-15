#!/usr/bin/env python3
"""
make_dataset.py - Build the synthetic "Operation Riverbank" dataset for the
Media Forensics lab (Day 2). Everything is generated locally so that the
instructor knows the ground truth and no real person or copyrighted media
is involved.

Produces, under --out (default ./dataset):

  A_metadata/riverbank_report.jpg    forged EXIF (date, GPS, software) + mismatched embedded thumbnail
  B_signal/riverbank_spliced.jpg     copy-move splice saved at a different JPEG quality (ELA target)
  B_signal/riverbank_shadows.jpg     two objects with incompatible shadow directions
  B_signal/riverbank_original.jpg    the untouched scene (instructor only, copied to instructor/)
  C_provenance/README.md             pointers to public C2PA test files + the recontextualisation exercise
  D_video/riverbank_clip.mp4         generated clip with a hidden cut and a spliced still frame (needs ffmpeg)
  E_cib/accounts.csv, posts.csv, edges.csv   synthetic coordinated network hidden in organic traffic
  instructor/ground_truth.json       all answers (KEEP OUT OF THE STUDENT SHARE)

Requirements:
  pip install pillow numpy pandas
  exiftool on PATH (brew install exiftool / apt install libimage-exiftool-perl)
  ffmpeg on PATH, or pip install imageio-ffmpeg   (only for D_video)

Usage:
  python3 make_dataset.py --out dataset --seed 42
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("[!] pillow missing: pip install pillow")

W, H = 1280, 720
GT: dict = {}  # ground truth collected along the way


# ----------------------------------------------------------------------------- helpers
def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def iso(dt: datetime) -> str:
    """Consistent ISO-8601 to the second (mixed microseconds break strict pandas parsing)."""
    return dt.replace(microsecond=0).isoformat()


def have(cmd: str) -> str | None:
    return shutil.which(cmd)


def ffmpeg_bin() -> str | None:
    if have("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def font(size: int):
    for cand in ["/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "C:/Windows/Fonts/arial.ttf"]:
        if Path(cand).exists():
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


# ----------------------------------------------------------------------------- scene
def draw_scene(sun_azimuth_deg: float = 225.0, sun_elev_deg: float = 35.0, seed: int = 1) -> Image.Image:
    """A flat riverbank scene: sky gradient, river, bank, a warehouse, poles with consistent shadows.
    Shadows are drawn from the same light direction so students can test coherence."""
    import math
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # sky
    for y in range(0, 400):
        t = y / 400
        d.line([(0, y), (W, y)], fill=(int(120 + 80 * t), int(170 + 50 * t), int(230 - 20 * t)))
    # distant tree line
    for x in range(0, W, 18):
        h = rnd.randint(25, 60)
        d.ellipse([x - 20, 400 - h, x + 20, 410], fill=(40 + rnd.randint(0, 20), 90 + rnd.randint(0, 30), 40))
    # bank + river
    d.rectangle([0, 400, W, 520], fill=(96, 140, 70))
    d.rectangle([0, 520, W, H], fill=(70, 110, 150))
    for y in range(520, H, 9):
        d.line([(0, y), (W, y)], fill=(80 + (y % 3) * 10, 125, 165), width=1)

    # shadow vector on the ground (screen coords): opposite to sun azimuth, length ~ 1/tan(elev)
    L = 1.0 / max(math.tan(math.radians(sun_elev_deg)), 0.2)
    sx = -math.sin(math.radians(sun_azimuth_deg)) * L
    sy = math.cos(math.radians(sun_azimuth_deg)) * L * 0.35  # ground foreshortening

    def pole(x, base_y, height, width=8):
        # shadow first
        d.line([(x, base_y), (x + sx * height, base_y + sy * height)], fill=(60, 90, 45), width=width)
        d.rectangle([x - width // 2, base_y - height, x + width // 2, base_y], fill=(70, 70, 75))
        d.ellipse([x - 9, base_y - height - 9, x + 9, base_y - height + 9], fill=(200, 200, 60))

    def box(x, base_y, w, h, color):
        d.polygon([(x, base_y), (x + w, base_y), (x + w + sx * h, base_y + sy * h), (x + sx * h, base_y + sy * h)],
                  fill=(60, 90, 45))
        d.rectangle([x, base_y - h, x + w, base_y], fill=color)
        d.polygon([(x, base_y - h), (x + w, base_y - h), (x + w - 20, base_y - h - 30), (x + 20, base_y - h - 30)],
                  fill=tuple(max(c - 30, 0) for c in color))

    box(820, 470, 260, 110, (170, 90, 80))          # warehouse
    pole(180, 500, 170)
    pole(560, 495, 150)
    pole(1180, 480, 120)
    # small boat
    d.polygon([(300, 600), (420, 600), (400, 630), (320, 630)], fill=(230, 230, 220))
    return img


def burn_text(img: Image.Image, text: str, xy=(20, 20), size=28, fill=(255, 255, 255)):
    d = ImageDraw.Draw(img)
    d.rectangle([xy[0] - 6, xy[1] - 4, xy[0] + 12 * len(text) + 6, xy[1] + size + 6], fill=(0, 0, 0))
    d.text(xy, text, font=font(size), fill=fill)
    return img


# ----------------------------------------------------------------------------- A. metadata
def build_A(out: Path, original: Image.Image):
    a = out / "A_metadata"; a.mkdir(parents=True, exist_ok=True)
    target = a / "riverbank_report.jpg"
    # visible image = cropped/edited version (warehouse removed by cropping right part)
    edited = original.crop((0, 0, 800, 720)).resize((W, H))
    edited.save(target, "JPEG", quality=88)
    # thumbnail = generated from the UNCROPPED original -> mismatch
    thumb = original.copy(); thumb.thumbnail((160, 90)); tpath = a / "_thumb.jpg"; thumb.save(tpath, "JPEG", quality=70)

    claimed_date = "2026:03:14 17:42:10"          # claim: mid-March, late afternoon
    upload_date = "2026:03:12 09:00:00"           # "posted" 2 days BEFORE it was taken -> impossible
    gps = ("48.8566", "2.3522")                    # Paris, while the caption will say Rotterdam
    if have("exiftool"):
        subprocess.run(["exiftool", "-q", "-overwrite_original",
                        f"-DateTimeOriginal={claimed_date}", f"-CreateDate={claimed_date}",
                        "-Make=Canon", "-Model=Canon EOS R6", "-Software=Adobe Photoshop 25.5 (Windows)",
                        f"-GPSLatitude={gps[0]}", "-GPSLatitudeRef=N", f"-GPSLongitude={gps[1]}", "-GPSLongitudeRef=E",
                        "-Artist=riverwatch_press", "-ImageDescription=Flooded quay, Rotterdam Maashaven, this morning",
                        f"-ThumbnailImage<={tpath}", str(target)], check=False)
    else:
        print("[!] exiftool not found: A_metadata written WITHOUT forged EXIF (install exiftool and re-run)")
    tpath.unlink(missing_ok=True)
    (a / "caption.txt").write_text(
        "Posted by @riverwatch_press on 2026-03-12 09:00 UTC:\n"
        "\"BREAKING - Maashaven quay in Rotterdam under water this morning. Authorities silent.\"\n")
    GT["A_metadata"] = {
        "file": target.name,
        "forged": {"DateTimeOriginal": claimed_date, "posted_claim": upload_date,
                   "GPS": {"lat": gps[0], "lon": gps[1], "note": "Paris, contradicts Rotterdam caption"},
                   "Software": "Adobe Photoshop 25.5 (undeclared editing)", "Make/Model": "Canon EOS R6"},
        "thumbnail": "embedded thumbnail shows the UNCROPPED scene incl. warehouse on the right; visible image is cropped",
        "inconsistencies_expected": ["capture date AFTER posting date", "GPS != caption location",
                                     "Photoshop in Software", "thumbnail != visible image"],
        "sha256": sha256(target),
    }


# ----------------------------------------------------------------------------- B. signal
def build_B(out: Path, original: Image.Image):
    b = out / "B_signal"; b.mkdir(parents=True, exist_ok=True)
    orig_path = b / "riverbank_original.jpg"
    original.save(orig_path, "JPEG", quality=92)

    # Splice: copy the boat and paste it near the warehouse, from a re-saved q=60 version (different compression history)
    lowq = b / "_lowq.jpg"; original.save(lowq, "JPEG", quality=60)
    donor = Image.open(lowq)
    patch_box = (290, 590, 430, 640)
    patch = donor.crop(patch_box).filter(ImageFilter.GaussianBlur(0.4))
    spliced = Image.open(orig_path).copy()
    paste_at = (900, 600)
    spliced.paste(patch, paste_at)
    sp = b / "riverbank_spliced.jpg"; spliced.save(sp, "JPEG", quality=90)
    lowq.unlink()

    # Shadow inconsistency: redraw the scene but add one pole lit from the opposite side
    shadows = draw_scene(sun_azimuth_deg=225, sun_elev_deg=35, seed=1)
    d = ImageDraw.Draw(shadows)
    import math
    L = 1 / math.tan(math.radians(35)); sx = -math.sin(math.radians(45)) * L; sy = math.cos(math.radians(45)) * L * 0.35
    x, base_y, height = 700, 505, 160
    d.line([(x, base_y), (x + sx * height, base_y + sy * height)], fill=(60, 90, 45), width=8)
    d.rectangle([x - 4, base_y - height, x + 4, base_y], fill=(70, 70, 75))
    d.ellipse([x - 9, base_y - height - 9, x + 9, base_y - height + 9], fill=(200, 200, 60))
    shp = b / "riverbank_shadows.jpg"; shadows.save(shp, "JPEG", quality=90)

    GT["B_signal"] = {
        "spliced": {"file": sp.name, "pasted_region_xywh": [paste_at[0], paste_at[1], patch_box[2] - patch_box[0], patch_box[3] - patch_box[1]],
                    "source_region_xywh": [patch_box[0], patch_box[1], patch_box[2] - patch_box[0], patch_box[3] - patch_box[1]],
                    "method": "copy-move of the boat from a q=60 re-save into a q=92 image, saved q=90; ELA shows a brighter rectangle",
                    "sha256": sha256(sp)},
        "shadows": {"file": shp.name, "inconsistent_object": "pole at x~700 lit from azimuth 45 deg while the rest of the scene is lit from 225 deg",
                    "sha256": sha256(shp)},
        "original": {"file": orig_path.name, "sha256": sha256(orig_path)},
    }


# ----------------------------------------------------------------------------- C. provenance
def build_C(out: Path):
    c = out / "C_provenance"; c.mkdir(parents=True, exist_ok=True)
    (c / "README.md").write_text("""# C - Provenance & recontextualisation

## C1. Recontextualisation (reverse image search)
The instructor gives you ONE real photo (a public-domain image from Wikimedia Commons, chosen the day before)
with a FALSE caption: `recontext/claim.txt`. Your job: find the first occurrence online (date, place, author),
and write the graded verdict. Tools: Google Lens, Yandex Images, TinEye (sort by oldest), Bing Visual Search.

Instructor: pick an image with a documented upload history, save it as `recontext/photo.jpg`, strip its EXIF
(`exiftool -all= photo.jpg`), and write a caption placing it in another city and year.

## C2. Content Credentials (C2PA)
Public test files with valid, tampered and missing manifests:
  https://c2pa.org/public-testfiles/image/
Verify them with https://contentcredentials.org/verify or the CLI `c2patool file.jpg`.
Questions: which file has a valid manifest? which one was edited after signing? what does the ABSENCE of a
manifest prove (slide 23)?
""")
    (c / "recontext").mkdir(exist_ok=True)
    (c / "recontext" / "claim.txt").write_text("Instructor: paste the false caption here (city, date, event).\n")
    GT["C_provenance"] = {"note": "instructor-chosen public-domain image; record its true source URL, author and first-seen date here",
                          "true_source": None}


# ----------------------------------------------------------------------------- D. video
def build_D(out: Path, original: Image.Image, report_img_path: Path):
    d = out / "D_video"; d.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_bin()
    if not ff:
        (d / "MISSING_FFMPEG.txt").write_text("ffmpeg not found at build time. Install ffmpeg (or pip install imageio-ffmpeg) and re-run make_dataset.py\n")
        print("[!] ffmpeg not found: D_video skipped")
        GT["D_video"] = {"status": "skipped (no ffmpeg)"}
        return
    frames = d / "_frames"; frames.mkdir(exist_ok=True)
    fps = 10
    total = 0
    # Segment 1: 0-6 s, boat drifts left->right, clock 14:02:00 ->
    base = original.copy()
    t0 = datetime(2026, 3, 14, 14, 2, 0)
    n1 = 6 * fps
    for i in range(n1):
        f = base.copy(); dr = ImageDraw.Draw(f)
        x = 300 + i * 6
        dr.polygon([(x, 600), (x + 120, 600), (x + 100, 630), (x + 20, 630)], fill=(230, 230, 220))
        burn_text(f, (t0 + timedelta(seconds=i / fps)).strftime("CAM-02  %H:%M:%S"), size=26)
        f.save(frames / f"f_{total:04d}.png"); total += 1
    # Hidden cut: 90 seconds are missing, boat jumps back, clock jumps, light changed (cloud passed)
    from PIL import ImageEnhance
    cut_frame = total
    t1 = t0 + timedelta(seconds=6 + 90)
    base = ImageEnhance.Brightness(base).enhance(0.82)
    n2 = 5 * fps
    for i in range(n2):
        f = base.copy(); dr = ImageDraw.Draw(f)
        x = 200 + i * 6
        dr.polygon([(x, 600), (x + 120, 600), (x + 100, 630), (x + 20, 630)], fill=(230, 230, 220))
        burn_text(f, (t1 + timedelta(seconds=i / fps)).strftime("CAM-02  %H:%M:%S"), size=26)
        f.save(frames / f"f_{total:04d}.png"); total += 1
    # Spliced still: 1 s of the A_metadata report photo inserted (different scene framing)
    splice_frame = total
    # different camera: zoomed crop + warmer, darker colour balance
    still = Image.open(report_img_path).convert("RGB").crop((160, 90, 1120, 630)).resize((W, H))
    still = ImageEnhance.Color(ImageEnhance.Brightness(still).enhance(0.7)).enhance(1.6)
    for i in range(fps):
        burn_text(still.copy(), (t1 + timedelta(seconds=5 + i / fps)).strftime("CAM-02  %H:%M:%S"), size=26).save(frames / f"f_{total:04d}.png"); total += 1
    # Tail
    for i in range(3 * fps):
        f = base.copy(); dr = ImageDraw.Draw(f)
        x = 230 + i * 6
        dr.polygon([(x, 600), (x + 120, 600), (x + 100, 630), (x + 20, 630)], fill=(230, 230, 220))
        burn_text(f, (t1 + timedelta(seconds=6 + i / fps)).strftime("CAM-02  %H:%M:%S"), size=26)
        f.save(frames / f"f_{total:04d}.png"); total += 1

    clip = d / "riverbank_clip.mp4"
    subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "f_%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "30",
                    "-metadata", "title=CAM-02 export", "-metadata", "comment=exported with RiverWatch Editor 3.1",
                    "-metadata", "creation_time=2026-03-12T09:00:00Z", str(clip)], check=True)
    shutil.rmtree(frames)
    GT["D_video"] = {"file": clip.name, "fps": fps, "frames_total": total,
                     "hidden_cut": {"frame": cut_frame, "time_s": cut_frame / fps, "clock_jump_s": 90,
                                    "hint": "boat jumps back ~100 px, burned-in clock jumps 14:02:06 -> 14:03:36"},
                     "spliced_still": {"frame": splice_frame, "time_s": splice_frame / fps, "duration_s": 1,
                                       "source": "A_metadata/riverbank_report.jpg (cropped framing, no boat)"},
                     "container_metadata": {"creation_time": "2026-03-12T09:00:00Z (before the burned-in clock date)",
                                            "comment": "RiverWatch Editor 3.1 (editing software declared in container)"},
                     "sha256": sha256(clip)}


# ----------------------------------------------------------------------------- E. CIB
def build_E(out: Path, seed: int):
    e = out / "E_cib"; e.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(seed)
    first_names = ["alex", "maria", "jan", "priya", "lucas", "emma", "noah", "sofia", "leon", "aisha", "tom", "lena",
                   "arjun", "nina", "paul", "ines", "omar", "julia", "max", "sara"]
    topics = ["Rotterdam quay flooding", "port authority statement", "ferry delays", "harbour cam footage",
              "insurance claims", "weather warning", "canal traffic", "council meeting"]
    organic_templates = [
        "Anyone else see the water level at {t}? looked normal to me this morning",
        "Photos from {t} are circulating, waiting for an official word",
        "{t}: my cousin works there, says nothing unusual",
        "Not sure about the {t} story, the timestamps don't add up",
        "Went past the Maashaven today, all dry. Where is this {t} thing from?",
        "Local news on {t} says the video is from 2021",
        "{t} - can someone verify before sharing?",
    ]
    cib_seed_text = "BREAKING: Maashaven quay in Rotterdam under water this morning. Authorities silent. Share before it's deleted! #RotterdamFlood"
    cib_variants = [
        cib_seed_text,
        "BREAKING: Maashaven quay Rotterdam under water this morning!! Authorities silent. Share before it is deleted #RotterdamFlood",
        "BREAKING - Maashaven quay in Rotterdam under water this morning. Authorities are silent. Share before its deleted! #RotterdamFlood",
        "Breaking: Maashaven quay (Rotterdam) under water this morning. Authorities silent... share before it's deleted #RotterdamFlood",
        "BREAKING: Maashaven quay in Rotterdam underwater this morning. Authorities silent. SHARE before it's deleted! #RotterdamFlood",
    ]

    accounts, posts, edges = [], [], []
    base = datetime(2026, 3, 12, tzinfo=timezone.utc)

    # organic accounts: created over years, post spread over the day, unique-ish texts
    n_org = 300
    for i in range(n_org):
        uid = f"u{i:04d}"
        created = base - timedelta(days=rnd.randint(200, 3000))
        handle = f"{rnd.choice(first_names)}{rnd.choice(['', '_', '.'])}{rnd.choice(['', str(rnd.randint(1, 99)), rnd.choice(first_names)])}"
        accounts.append({"user_id": uid, "handle": handle, "creation_date": created.date().isoformat(),
                         "followers": rnd.randint(20, 5000), "following": rnd.randint(30, 900),
                         "posts_total": rnd.randint(50, 20000), "has_photo": 1, "bio_len": rnd.randint(10, 160),
                         "utc_offset": rnd.choice([1, 1, 1, 0, 2, -5, 5])})
        for _ in range(rnd.randint(0, 3)):
            ts = base + timedelta(hours=rnd.uniform(6, 23), seconds=rnd.uniform(0, 3600))
            txt = rnd.choice(organic_templates).format(t=rnd.choice(topics))
            posts.append({"post_id": f"p{len(posts):05d}", "user_id": uid, "timestamp": iso(ts),
                          "text": txt, "type": "post", "reposted_user_id": ""})

    # seed account + 40 coordinated amplifiers
    seed_uid = "u9000"
    accounts.append({"user_id": seed_uid, "handle": "riverwatch_press", "creation_date": (base - timedelta(days=41)).date().isoformat(),
                     "followers": 1800, "following": 12, "posts_total": 37, "has_photo": 1, "bio_len": 120, "utc_offset": 3})
    seed_ts = base + timedelta(hours=9)
    posts.append({"post_id": f"p{len(posts):05d}", "user_id": seed_uid, "timestamp": iso(seed_ts),
                  "text": cib_seed_text, "type": "post", "reposted_user_id": ""})
    cib_ids = []
    creation_burst_day = base - timedelta(days=39)
    for i in range(40):
        uid = f"u9{i + 1:03d}"
        cib_ids.append(uid)
        created = creation_burst_day + timedelta(days=rnd.randint(0, 2))
        handle = f"{rnd.choice(first_names)}{rnd.randint(10000, 99999)}"
        accounts.append({"user_id": uid, "handle": handle, "creation_date": created.date().isoformat(),
                         "followers": rnd.randint(0, 15), "following": rnd.randint(300, 1200),
                         "posts_total": rnd.randint(3, 40), "has_photo": rnd.choice([0, 0, 1]), "bio_len": rnd.choice([0, 0, 8]),
                         "utc_offset": 3})
        # burst: within 4 minutes of the seed, near-duplicate text, plus a repost
        ts = seed_ts + timedelta(seconds=rnd.randint(30, 240))
        posts.append({"post_id": f"p{len(posts):05d}", "user_id": uid, "timestamp": iso(ts),
                      "text": rnd.choice(cib_variants), "type": "post", "reposted_user_id": ""})
        posts.append({"post_id": f"p{len(posts):05d}", "user_id": uid, "timestamp": iso(ts + timedelta(seconds=rnd.randint(5, 60))),
                      "text": cib_seed_text, "type": "repost", "reposted_user_id": seed_uid})
        edges.append({"source": uid, "target": seed_uid, "type": "repost"})
        # they also repost each other (dense cluster)
        for other in rnd.sample(cib_ids, min(3, len(cib_ids))):
            if other != uid:
                edges.append({"source": uid, "target": other, "type": "repost"})
    # a few organic users repost the seed later (contamination)
    for uid in rnd.sample([a["user_id"] for a in accounts[:n_org]], 25):
        ts = seed_ts + timedelta(minutes=rnd.randint(20, 600))
        posts.append({"post_id": f"p{len(posts):05d}", "user_id": uid, "timestamp": iso(ts),
                      "text": cib_seed_text, "type": "repost", "reposted_user_id": seed_uid})
        edges.append({"source": uid, "target": seed_uid, "type": "repost"})
    # organic repost noise
    org_ids = [a["user_id"] for a in accounts[:n_org]]
    for _ in range(200):
        s, t = rnd.sample(org_ids, 2)
        edges.append({"source": s, "target": t, "type": "repost"})

    rnd.shuffle(posts)
    for name, rows in [("accounts.csv", accounts), ("posts.csv", posts), ("edges.csv", edges)]:
        with open(e / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    GT["E_cib"] = {"seed_account": seed_uid, "coordinated_accounts": cib_ids, "n_coordinated": len(cib_ids),
                   "creation_burst_window": [creation_burst_day.date().isoformat(), (creation_burst_day + timedelta(days=2)).date().isoformat()],
                   "post_burst_window_utc": [seed_ts.isoformat(), (seed_ts + timedelta(minutes=5)).isoformat()],
                   "signals": ["creation burst (3 days)", "posts within 4 min of seed", "near-duplicate text > 0.85",
                               "followers < 20, following > 300, no bio/photo", "same utc_offset=3", "dense repost cluster to seed"],
                   "contamination": "25 organic accounts reposted the seed later: NOT coordinated, do not flag them"}


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="dataset")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    original = draw_scene(seed=1)
    print("[*] A_metadata"); build_A(out, original)
    print("[*] B_signal"); build_B(out, original)
    print("[*] C_provenance"); build_C(out)
    print("[*] D_video"); build_D(out, original, out / "A_metadata" / "riverbank_report.jpg")
    print("[*] E_cib"); build_E(out, args.seed)

    inst = out / "instructor"; inst.mkdir(exist_ok=True)
    shutil.move(str(out / "B_signal" / "riverbank_original.jpg"), inst / "riverbank_original.jpg")
    GT["generated_utc"] = datetime.now(timezone.utc).isoformat()
    GT["seed"] = args.seed
    (inst / "ground_truth.json").write_text(json.dumps(GT, indent=2))
    print(f"[+] dataset in {out}/ ; answers in {inst}/ground_truth.json  -> move 'instructor/' OUT of the student share")


if __name__ == "__main__":
    main()
