#!/usr/bin/env python3
"""Convert PNG icons to TrueType glyphs and add/replace in TTF fonts.

Usage: python scripts/png_to_ttf.py
"""
import os
import numpy as np
from PIL import Image
from skimage import measure
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

REPO      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(REPO, "icons")
FONTS_DIR = os.path.join(REPO, "Guition-ESP32", "fonts")

# (png filename, glyph name, codepoint, ttf file, replace-existing?)
ICONS = [
    ("270134_curtains-icon.png",
     "uniE945", 0xE945, "icons_v2.ttf", False),
    ("garage_icon_135562.png",
     "uniE946", 0xE946, "icons_v2.ttf", False),
    ("movie-clapper-tool-to-number-filming-scenes_icon-icons.com_56261.png",
     "uniE947", 0xE947, "icons_v2.ttf", False),
    # Replace existing fan glyphs (keep existing glyph names)
    ("ceiling_fan_icon_127013.png",
     "ceiling_fan", 0xE901, "fan_icons.ttf", True),
    ("fan_4094.png",
     "floor_fan",   0xE900, "fan_icons.ttf", True),
]


# ── Image loading ──────────────────────────────────────────────────────────────

def load_binary(png_path, size=512):
    """Load PNG → grayscale binary mask (True = ink)."""
    img = Image.open(png_path).convert("RGBA")
    # Flatten alpha onto white background
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    img = bg.convert("L").resize((size, size), Image.LANCZOS)
    arr = np.array(img)
    # Determine background colour from corners
    corners = np.mean([arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]])
    return arr < 128 if corners > 128 else arr > 128


# ── Contour simplification ─────────────────────────────────────────────────────

def rdp(pts, eps=3.0):
    """Douglas-Peucker polyline simplification."""
    if len(pts) <= 2:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    ab = b - a
    ab_len = np.linalg.norm(ab)
    if ab_len < 1e-9:
        dists = [np.linalg.norm(np.array(p) - a) for p in pts[1:-1]]
    else:
        dists = [abs(np.cross(ab / ab_len, np.array(p) - a)) for p in pts[1:-1]]
    mx_d = max(dists)
    mx_i = dists.index(mx_d) + 1
    if mx_d > eps:
        return rdp(pts[: mx_i + 1], eps)[:-1] + rdp(pts[mx_i:], eps)
    return [pts[0], pts[-1]]


def signed_area(pts):
    """Shoelace formula; positive = CCW."""
    n = len(pts)
    return sum(
        pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
        for i in range(n)
    ) / 2.0


# ── PNG → contours in em-units ─────────────────────────────────────────────────

def png_to_contours(png_path, em=1000, asc=800, desc=-200, pad=60):
    binary = load_binary(png_path)
    h, w = binary.shape
    raw_list = measure.find_contours(binary.astype(float), 0.5)

    draw_h = asc - desc - 2 * pad
    scale  = draw_h / max(h, w)
    x0     = (em - w * scale) / 2.0
    y0     = desc + pad

    result = []
    for raw in raw_list:
        if len(raw) < 4:
            continue
        # raw[:,0]=row (down), raw[:,1]=col (right)
        pts = [(col * scale + x0, (h - row) * scale + y0) for row, col in raw]
        pts = rdp(pts, eps=3.0)
        if len(pts) < 3:
            continue
        if abs(signed_area(pts)) < 500:   # drop tiny noise
            continue
        result.append(pts)

    return result


# ── Build TrueType glyph ───────────────────────────────────────────────────────

def build_glyph(contours):
    pen = TTGlyphPen(None)
    for pts in contours:
        # TrueType outer contour = clockwise (negative signed area)
        if signed_area(pts) > 0:
            pts = list(reversed(pts))
        ipts = [(round(x), round(y)) for x, y in pts]
        pen.moveTo(ipts[0])
        for p in ipts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


# ── Add / replace glyph in font ────────────────────────────────────────────────

def upsert_glyph(tt, glyph_name, codepoint, glyph_obj, advance=1000):
    # Glyph order
    order = list(tt.getGlyphOrder())
    if glyph_name not in order:
        order.append(glyph_name)
        tt.setGlyphOrder(order)

    # Glyph outline
    tt["glyf"][glyph_name] = glyph_obj

    # Horizontal metrics
    lsb = glyph_obj.xMin if hasattr(glyph_obj, "xMin") else 0
    tt["hmtx"].metrics[glyph_name] = (advance, lsb)

    # cmap
    for table in tt["cmap"].tables:
        if hasattr(table, "cmap"):
            table.cmap[codepoint] = glyph_name


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    fonts = {}

    for png_name, glyph_name, codepoint, ttf_name, replace in ICONS:
        png_path = os.path.join(ICONS_DIR, png_name)
        ttf_path = os.path.join(FONTS_DIR, ttf_name)

        if not os.path.exists(png_path):
            print(f"[SKIP] PNG not found: {png_name}")
            continue

        if ttf_name not in fonts:
            fonts[ttf_name] = TTFont(ttf_path)
        tt = fonts[ttf_name]

        print(f"[PROCESS] {png_name}")
        print(f"          -> U+{codepoint:04X} '{glyph_name}' in {ttf_name}")

        contours = png_to_contours(png_path)
        if not contours:
            print(f"  [ERROR] No contours extracted — skipping")
            continue

        print(f"  {len(contours)} contour(s) extracted")
        glyph_obj = build_glyph(contours)
        upsert_glyph(tt, glyph_name, codepoint, glyph_obj)
        print(f"  Glyph added OK")

    for ttf_name, tt in fonts.items():
        out = os.path.join(FONTS_DIR, ttf_name)
        tt.save(out)
        print(f"[SAVED] {out}")


if __name__ == "__main__":
    main()
