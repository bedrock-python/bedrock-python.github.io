#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0", "numpy>=2.0"]
# ///
"""Derive the dark-theme variant of each illustration from the light one.

The blog serves both schemes, and an opaque cream tile glares on the near-black card. The brand
already answers this for the mark: `logo.svg` and `logo-dark.svg` are the same five polygons with
the lightness ramp turned over -- the facet that is darkest on white is lightest on black. The
illustrations are flat fills in the same palette, so the dark variant is that same operation
applied per pixel, not a second render: identical composition, identical accent object, inverted
ramp.

    uv run dark_variant.py                      # images/v2/normalized -> images/v2/dark

Hue and saturation are preserved, so slate stays slate. Lightness is inverted and shifted so the
background lands on the dark card colour and the darkest slate lands where `logo-dark.svg` puts it.
The terracotta object keeps its hue and takes the site's dark-scheme accent lightness (#E8825A),
which is what the stylesheet already switches to under `[data-md-color-scheme="slate"]`.
"""

from __future__ import annotations

import argparse
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent

DARK_BG = (0x18, 0x18, 0x1B)      # --bdr-surface, the card the tile sits on
DARK_ACCENT = (0xE8, 0x82, 0x5A)  # --bdr-accent under the slate scheme


def rgb_to_hls(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mx, mn = arr.max(-1), arr.min(-1)
    light = (mx + mn) / 2
    delta = mx - mn
    sat = np.zeros_like(light)
    nz = delta > 1e-6
    denom = 1 - np.abs(2 * light - 1)
    sat[nz] = np.divide(delta[nz], np.maximum(denom[nz], 1e-6))
    hue = np.zeros_like(light)
    idx = nz & (mx == r)
    hue[idx] = ((g - b)[idx] / delta[idx]) % 6
    idx = nz & (mx == g)
    hue[idx] = ((b - r)[idx] / delta[idx]) + 2
    idx = nz & (mx == b)
    hue[idx] = ((r - g)[idx] / delta[idx]) + 4
    return hue / 6, light, sat


def hls_to_rgb(hue: np.ndarray, light: np.ndarray, sat: np.ndarray) -> np.ndarray:
    c = (1 - np.abs(2 * light - 1)) * sat
    h6 = hue * 6
    x = c * (1 - np.abs(h6 % 2 - 1))
    m = light - c / 2
    z = np.zeros_like(c)
    seg = np.floor(h6).astype(int) % 6
    table = np.stack([
        np.stack([c, x, z], -1), np.stack([x, c, z], -1), np.stack([z, c, x], -1),
        np.stack([z, x, c], -1), np.stack([x, z, c], -1), np.stack([c, z, x], -1),
    ])
    out = np.take_along_axis(table, seg[None, ..., None], 0)[0]
    return np.clip(out + m[..., None], 0, 1)


def to_dark(im: Image.Image) -> Image.Image:
    arr = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    hue, light, sat = rgb_to_hls(arr)
    # Work in chroma, not HSL saturation: near-white is barely coloured but scores a high
    # saturation because its denominator collapses, and inverting that paints the page brown.
    chroma = arr.max(-1) - arr.min(-1)

    # Terracotta: warm hue carrying real chroma, never the near-neutral fills.
    accent = (hue > 0.01) & (hue < 0.12) & (chroma > 0.18) & (light > 0.20) & (light < 0.85)

    target_bg = colorsys.rgb_to_hls(*[c / 255 for c in DARK_BG])[0:2][1]
    inverted = 1.0 - light
    # Anchor the inversion: the light background must land exactly on the dark card colour.
    bg_light = float(np.percentile(light, 97))
    shift = target_bg - (1.0 - bg_light)
    new_light = np.clip(inverted + shift, 0.0, 1.0)

    accent_light = colorsys.rgb_to_hls(*[c / 255 for c in DARK_ACCENT])[1]
    new_light = np.where(accent, accent_light, new_light)

    # Carry chroma across the inversion rather than saturation, and flatten what was only a warm
    # cast to true neutral, so the page ground becomes the card's grey instead of a brown.
    accent_chroma = (1 - abs(2 * accent_light - 1)) * colorsys.rgb_to_hls(
        *[c / 255 for c in DARK_ACCENT])[2]
    new_chroma = np.where(accent, accent_chroma, np.where(chroma < 0.06, 0.0, chroma * 0.95))
    denom = np.maximum(1 - np.abs(2 * new_light - 1), 1e-6)
    new_sat = np.clip(new_chroma / denom, 0, 1)

    return Image.fromarray((hls_to_rgb(hue, new_light, new_sat) * 255).round().astype(np.uint8))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--images", type=Path, default=HERE / "images/v2/normalized")
    p.add_argument("--out", type=Path, default=HERE / "images/v2/dark")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for path in sorted(args.images.glob("*.png")):
        with Image.open(path) as im:
            dark = to_dark(im)
        dark.save(args.out / path.name)
        corner = dark.getpixel((6, 6))
        print(f"  {path.stem[:56]:56} background -> #{corner[0]:02X}{corner[1]:02X}{corner[2]:02X}")
    print(f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
