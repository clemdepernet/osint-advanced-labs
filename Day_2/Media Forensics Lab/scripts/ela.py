#!/usr/bin/env python3
"""
ela.py - Error Level Analysis (slide 20 / 29): re-save the JPEG at a known
quality, take the absolute difference with the original, amplify it.
Regions with a different compression history (pasted from another file,
re-saved at another quality) stand out as brighter or differently textured
rectangles. ELA is an INDICATOR, never a proof: uniform areas (sky) always
look dark, high-frequency areas (text, edges) always look bright.

Usage:
  python3 ela.py image.jpg                      # writes image_ela.png
  python3 ela.py image.jpg --quality 75 --scale 20 --grid
  python3 ela.py image.jpg --thumb              # also extract the embedded EXIF thumbnail (needs exiftool)

Requirements: pip install pillow ; exiftool for --thumb
"""
from __future__ import annotations

import argparse
import io
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance


def ela(img: Image.Image, quality: int, scale: float) -> Image.Image:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    buf.seek(0)
    resaved = Image.open(buf)
    diff = ImageChops.difference(img.convert("RGB"), resaved)
    extrema = diff.getextrema()
    max_diff = max(e[1] for e in extrema) or 1
    return ImageEnhance.Brightness(diff).enhance(scale * 255.0 / max_diff / 10)


def draw_grid(img: Image.Image, step: int = 8) -> Image.Image:
    """Overlay the 8x8 JPEG block grid: a pasted region whose blocks are misaligned shows a shifted texture."""
    out = img.copy()
    d = ImageDraw.Draw(out)
    for x in range(0, out.width, step * 8):
        d.line([(x, 0), (x, out.height)], fill=(60, 60, 60))
    for y in range(0, out.height, step * 8):
        d.line([(0, y), (out.width, y)], fill=(60, 60, 60))
    return out


def extract_thumb(path: Path) -> Path | None:
    if not shutil.which("exiftool"):
        print("[!] exiftool not found, cannot extract thumbnail")
        return None
    out = path.with_name(path.stem + "_thumb.jpg")
    res = subprocess.run(["exiftool", "-b", "-ThumbnailImage", str(path)], capture_output=True)
    if res.stdout:
        out.write_bytes(res.stdout)
        print(f"[+] embedded thumbnail -> {out}  (compare its framing with the visible image!)")
        return out
    print("[i] no embedded thumbnail")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--quality", type=int, default=90, help="re-save quality (try 75, 90, 95)")
    ap.add_argument("--scale", type=float, default=15, help="amplification factor")
    ap.add_argument("--grid", action="store_true", help="overlay the 64px block grid")
    ap.add_argument("--thumb", action="store_true", help="extract embedded EXIF thumbnail")
    args = ap.parse_args()

    p = Path(args.image)
    img = Image.open(p)
    result = ela(img, args.quality, args.scale)
    if args.grid:
        result = draw_grid(result)
    out = p.with_name(p.stem + f"_ela_q{args.quality}.png")
    result.save(out)
    print(f"[+] ELA -> {out}")
    print("    read it as: uniform bright rectangle = different compression history; bright edges everywhere = normal.")
    if args.thumb:
        extract_thumb(p)


if __name__ == "__main__":
    main()
