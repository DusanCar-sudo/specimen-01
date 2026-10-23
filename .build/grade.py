#!/usr/bin/env python3
"""Grade raw SDXS plates into one coherent technical duotone look.

Outputs:
  .build/plates/<name>-1920.png   film masters
  dist/assets/ar/<name>.webp      site plates (1600x900)
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path("/home/dusan/preview-demo")
RAW = ROOT / ".build/raw"
PLATES = ROOT / ".build/plates"
WEB = ROOT / "dist/assets/ar"
PLATES.mkdir(parents=True, exist_ok=True)
WEB.mkdir(parents=True, exist_ok=True)

# name: (source, focus_x, focus_y, zoom, invert, exposure)
# focus is the centre of the crop in 0..1 of the source frame.
SHOTS = {
    "hand":    ("hand-307.png",        0.50, 0.55, 1.22, False, 1.6),
    "joint":   ("joint-101.png",       0.50, 0.52, 1.28, False, 1.02),
    "servo":   ("servo-101.png",       0.52, 0.52, 1.34, False, 1.06),
    "gantry":  ("gantry-307.png",      0.50, 0.55, 1.06, False, 1.02),
    "lab":     ("lab-211.png",         0.50, 0.60, 1.08, False, 0.94),
    "arm":     ("arm-211.png",         0.58, 0.50, 1.12, False, 0.98),
    "mocap":   ("mocap-211.png",       0.50, 0.50, 1.10, False, 1.95),
    "blueprint": ("blueprint-307.png", 0.50, 0.50, 1.10, True,  1.10),
    "chamber": ("hero-211.png",        0.50, 0.55, 1.05, False, 1.30),
    "void":    ("silhouette-211.png",  0.50, 0.50, 1.05, False, 1.45),
}

# Duotone ramp: shadow -> mid -> highlight (warm bone, graphite base).
STOPS = [
    (0.00, (7, 9, 10)),
    (0.20, (16, 19, 19)),
    (0.46, (58, 57, 50)),
    (0.74, (150, 144, 124)),
    (0.90, (214, 206, 184)),
    (1.00, (247, 242, 226)),
]


def lut() -> np.ndarray:
    xs = np.array([s[0] for s in STOPS], dtype=np.float64)
    rgb = np.stack([np.array([s[1][c] for s in STOPS], dtype=np.float64) for c in range(3)], axis=1)
    t = np.linspace(0.0, 1.0, 4096)
    out = np.stack([np.interp(t, xs, rgb[:, c]) for c in range(3)], axis=1)
    return out  # (4096, 3)


def crop(im: Image.Image, fx: float, fy: float, zoom: float) -> Image.Image:
    w, h = im.size
    target = 16 / 9
    cw, ch = (w / zoom, w / zoom / target) if w / h > target else (h * target / zoom, h / zoom)
    cw, ch = min(cw, w), min(ch, h)
    cx, cy = fx * w, fy * h
    x0 = min(max(0.0, cx - cw / 2), w - cw)
    y0 = min(max(0.0, cy - ch / 2), h - ch)
    return im.crop((int(round(x0)), int(round(y0)), int(round(x0 + cw)), int(round(y0 + ch))))


def grade(src: pathlib.Path, invert: bool, exposure: float) -> Image.Image:
    im = Image.open(src).convert("L")
    a = np.asarray(im, dtype=np.float32) / 255.0
    if invert:
        a = 1.0 - a
    lo, hi = np.percentile(a, 1.5), np.percentile(a, 99.0)
    a = np.clip((a - lo) / max(hi - lo, 1e-4), 0, 1)

    # soft S-curve, then exposure
    a = a * a * (3 - 2 * a) * 0.55 + a * 0.45
    a = np.clip(a * exposure, 0, 1) ** 0.9

    # highlight bloom (helps upscaled plates feel photographic)
    hi_mask = np.clip((a - 0.68) / 0.32, 0, 1)
    bloom = np.asarray(
        Image.fromarray((hi_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)),
        dtype=np.float32,
    ) / 255.0
    a = np.clip(a + bloom * 0.16, 0, 1)

    # vignette
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    a = a * (1 - 0.30 * np.clip(r, 0, 1) ** 2.1)

    # final anchor so every plate lands on the same tonal range
    lo2, hi2 = np.percentile(a, 1), np.percentile(a, 97)
    a = np.clip((a - lo2) / max(hi2 - lo2, 1e-4), 0, 1) * 0.985 + 0.015

    table = lut() / 255.0
    idx = np.clip((a * (len(table) - 1)).astype(np.int32), 0, len(table) - 1)
    rgb = table[idx]

    # film grain, seeded
    rng = np.random.default_rng(20261022)
    grain = rng.normal(0, 0.011, size=(h, w, 1)).astype(np.float32)
    rgb = np.clip(rgb + grain, 0, 1)
    return Image.fromarray((rgb * 255).astype(np.uint8), "RGB")


def main() -> None:
    stats = {}
    for name, (src, fx, fy, zoom, invert, exposure) in SHOTS.items():
        raw = Image.open(RAW / src).convert("L")
        cropped = crop(raw, fx, fy, zoom)
        big = cropped.resize((1920, 1080), Image.LANCZOS)
        big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=58, threshold=3))
        tmp = PLATES / f".tmp-{name}.png"
        big.save(tmp)
        master = grade(tmp, invert, exposure)
        master.save(PLATES / f"{name}-1920.png", optimize=True)
        master.resize((1600, 900), Image.LANCZOS).save(WEB / f"{name}.webp", quality=82, method=6)
        tmp.unlink()

        arr = np.asarray(master, dtype=np.float32) / 255.0
        stats[name] = {
            "source": src,
            "mean": round(float(arr.mean()), 3),
            "p01": round(float(np.percentile(arr, 1)), 3),
            "p99": round(float(np.percentile(arr, 99)), 3),
            "bytes_webp": (WEB / f"{name}.webp").stat().st_size,
        }
        print(name, stats[name], flush=True)
    (PLATES / "stats.json").write_text(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
