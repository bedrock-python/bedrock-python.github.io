#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0"]
# ///
"""Pull every generated illustration onto the site's exact background colour.

gpt-image renders "warm off-white" as cream: measured backgrounds come back between #F7EDDB
and #FFFBED, all of them short of blue against the #F8F6F1 the blog actually uses, and each
one different. That reads as a yellow cast in the card grid and as 49 slightly different
creams next to each other.

The fix is a white balance, not a repaint: measure the background the model produced, then
scale each channel so that colour lands exactly on #F8F6F1. Black stays black, so the slate
family is pulled the same distance and keeps its relationships instead of being replaced.

    uv run normalize.py                 # images/ -> images/normalized/
    uv run normalize.py --in-place      # overwrite, after you have looked at the copies
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
TARGET = (0xF8, 0xF6, 0xF1)


def measured_background(im: Image.Image) -> tuple[int, int, int]:
    """The median of the four corners: the flat field the subject sits on."""
    w, h = im.size
    corners = [im.getpixel((6, 6)), im.getpixel((w - 7, 6)),
               im.getpixel((6, h - 7)), im.getpixel((w - 7, h - 7))]
    return tuple(sorted(c[i] for c in corners)[1] for i in range(3))


def balance(im: Image.Image, bg: tuple[int, int, int]) -> Image.Image:
    """Scale each channel so `bg` maps to TARGET. Anchored at black, so darks stay dark."""
    tables = []
    for i in range(3):
        gain = TARGET[i] / max(bg[i], 1)
        tables += [min(255, round(v * gain)) for v in range(256)]
    return im.point(tables)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--images", type=Path, default=HERE / "images")
    p.add_argument("--out", type=Path, default=None, help="default: <images>/normalized")
    p.add_argument("--in-place", action="store_true", help="overwrite the originals")
    args = p.parse_args()

    out = args.images if args.in_place else (args.out or args.images / "normalized")
    out.mkdir(parents=True, exist_ok=True)

    for path in sorted(args.images.glob("*.png")):
        with Image.open(path) as raw:
            im = raw.convert("RGB")
        bg = measured_background(im)
        fixed = balance(im, bg)
        after = measured_background(fixed)
        fixed.save(out / path.name)
        drift = max(abs(bg[i] - TARGET[i]) for i in range(3))
        print(f"  {path.stem[:54]:54} #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X} "
              f"(off by {drift:2d}) -> #{after[0]:02X}{after[1]:02X}{after[2]:02X}")
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
