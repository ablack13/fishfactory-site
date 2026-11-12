#!/usr/bin/env python3
"""Derive every raster brand asset from the single supplied logo file.

The source logo (requirements/signal-*.png) is an opaque image: black fish,
lime circle, white background. Each pixel is unmixed into black / lime / white
weights, so variants can be recomposed with clean anti-aliased edges and a
transparent background. Nothing is redrawn - geometry comes from the source.

Usage:
    python3 tools/build_assets.py [--fonts DIR]

--fonts DIR  folder with SpaceGrotesk.ttf and PlexMono.ttf (only needed to
             re-render the social preview image, assets/img/og-image.png).
Requires: Pillow, numpy.
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")

SRC_LIME = np.array([189, 239, 0], dtype=np.float64)   # lime as exported in the source file
BRAND_LIME = (168, 240, 90)                            # Signal Lime  #A8F05A
BRAND_DARK = (23, 26, 29)                              # Factory Black #171A1D
WHITE = (255, 255, 255)


def unmix(src):
    """Return per-pixel weights (black, lime) in 0..1; the remainder is white."""
    px = np.asarray(src.convert("RGB"), dtype=np.float64)
    white = np.array([255.0, 255.0, 255.0])
    # px = wl*LIME + ww*WHITE (+ wb*BLACK, which contributes nothing)
    a = np.stack([SRC_LIME, white], axis=1)             # 3x2
    pinv = np.linalg.pinv(a)                            # 2x3
    w = px.reshape(-1, 3) @ pinv.T
    wl = np.clip(w[:, 0], 0, 1)
    ww = np.clip(w[:, 1], 0, 1)
    wb = np.clip(1 - wl - ww, 0, 1)
    h, wd = px.shape[:2]
    return wb.reshape(h, wd), wl.reshape(h, wd)


def compose(wb, wl, fish_rgb, lime_rgb=BRAND_LIME):
    """Recolour: black areas -> fish_rgb, lime -> lime_rgb, white -> transparent."""
    alpha = np.clip(wb + wl, 0, 1)
    safe = np.where(alpha > 0, alpha, 1)
    rgb = (wb[..., None] * np.array(fish_rgb) + wl[..., None] * np.array(lime_rgb)) / safe[..., None]
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def fit(img, width):
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


def icon(logo, size, scale, radius=0.0, bg=BRAND_DARK):
    """Square icon: brand-dark tile with the logo centred at `scale` of the width."""
    ss = 4 if size < 256 else 2
    big = size * ss
    tile = Image.new("RGBA", (big, big), bg + (255,))
    mark = fit(logo, round(big * scale))
    tile.alpha_composite(mark, ((big - mark.width) // 2, (big - mark.height) // 2))
    if radius:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], round(big * radius), fill=255)
        tile.putalpha(mask)
    return tile.resize((size, size), Image.LANCZOS)


def og_image(logo, fonts):
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), BRAND_DARK + (255,))
    mark = fit(logo, 700)
    img.alpha_composite(mark, (w - 560, (h - mark.height) // 2 + 20))
    d = ImageDraw.Draw(img)
    head = ImageFont.truetype(os.path.join(fonts, "SpaceGrotesk.ttf"), 96)
    try:
        head.set_variation_by_axes([700])
    except Exception:
        pass
    mono = ImageFont.truetype(os.path.join(fonts, "PlexMono.ttf"), 26)
    small = ImageFont.truetype(os.path.join(fonts, "PlexMono.ttf"), 20)
    brand = ImageFont.truetype(os.path.join(fonts, "SpaceGrotesk.ttf"), 34)
    try:
        brand.set_variation_by_axes([700])
    except Exception:
        pass
    d.text((72, 64), "FISH FACTORY", font=brand, fill=WHITE)
    d.text((72, 228), "Ideas into", font=head, fill=WHITE)
    d.text((72, 328), "products.", font=head, fill=WHITE)
    d.text((72, 462), "Mobile engineering for", font=mono, fill=(200, 205, 211))
    d.text((72, 498), "real world solutions.", font=mono, fill=(200, 205, 211))
    d.text((72, 562), "FISHFACTORY.DEV", font=small, fill=BRAND_LIME)
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts")
    args = ap.parse_args()

    src_path = sorted(glob.glob(os.path.join(ROOT, "requirements", "*.png")))[0]
    src = Image.open(src_path)
    os.makedirs(OUT, exist_ok=True)

    wb, wl = unmix(src)
    on_dark = compose(wb, wl, WHITE)        # white fish + lime, for dark backgrounds
    on_light = compose(wb, wl, BRAND_DARK)  # dark fish + lime, for light backgrounds

    # Hero graphic (dark background)
    fit(on_dark, 1400).save(os.path.join(OUT, "logo-hero.webp"), quality=90, method=6)
    fit(on_dark, 700).save(os.path.join(OUT, "logo-hero-700.webp"), quality=90, method=6)
    fit(on_dark, 1400).save(os.path.join(OUT, "logo-hero.png"), optimize=True)

    # Small marks for header / footer / documents
    fit(on_dark, 240).save(os.path.join(OUT, "logo-mark-dark.png"), optimize=True)
    fit(on_light, 240).save(os.path.join(OUT, "logo-mark-light.png"), optimize=True)

    # Favicons and app icons (brandbook: dark tile, white fish, lime circle)
    icon(on_dark, 512, 0.74, radius=0.22).save(os.path.join(ROOT, "favicon.png"), optimize=True)
    ico_sizes = [16, 32, 48]
    frames = [icon(on_dark, s, 0.86, radius=0.2) for s in ico_sizes]
    frames[-1].save(os.path.join(ROOT, "favicon.ico"), format="ICO",
                    sizes=[(s, s) for s in ico_sizes], append_images=frames[:-1])
    icon(on_dark, 180, 0.72).convert("RGB").save(os.path.join(ROOT, "apple-touch-icon.png"), optimize=True)
    icon(on_dark, 192, 0.74, radius=0.22).save(os.path.join(OUT, "icon-192.png"), optimize=True)
    icon(on_dark, 512, 0.74, radius=0.22).save(os.path.join(OUT, "icon-512.png"), optimize=True)
    icon(on_dark, 512, 0.58).convert("RGB").save(os.path.join(OUT, "icon-maskable-512.png"), optimize=True)

    if args.fonts:
        og_image(on_dark, args.fonts).save(os.path.join(OUT, "og-image.png"), optimize=True)
    else:
        print("--fonts not given: keeping existing assets/img/og-image.png")

    for f in sorted(os.listdir(OUT)):
        print(f"{os.path.getsize(os.path.join(OUT, f)):>8}  assets/img/{f}")


if __name__ == "__main__":
    main()
