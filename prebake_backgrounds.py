#!/usr/bin/env python3
"""
Pre-blend theme background images against their respective page background colours
and save as opaque RGB PNGs.  This removes the alpha channel so ESPHome can store
them as plain rgb565 (461 KB) instead of rgb565 + alpha (691 KB), reducing flash
cache pressure and eliminating the LCD vsync-miss flicker.

Backgrounds processed:
  cherry_bg.png    → bg 0x1A0610
  espeon_bg.png    → bg 0x180D2E
  patriotic_bg.png → bg 0x0A1628

paris_tower.png is intentionally skipped — it is a decorative overlay that relies
on per-pixel alpha to composite correctly and is much smaller.
"""
from PIL import Image
import os

BASE = "Guition-ESP32/img"

TARGETS = [
    ("cherry_bg.png",    (0x1A, 0x06, 0x10)),
    ("espeon_bg.png",    (0x18, 0x0D, 0x2E)),
    ("patriotic_bg.png", (0x0A, 0x16, 0x28)),
]

for fname, bg_rgb in TARGETS:
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"  SKIP  {fname}  (not found)")
        continue

    src = Image.open(path).convert("RGBA")
    bg  = Image.new("RGBA", src.size, (*bg_rgb, 255))
    out = Image.alpha_composite(bg, src).convert("RGB")
    out.save(path)

    kb_before = os.path.getsize(path) // 1024
    # rgb565 binary size comparison
    px = src.width * src.height
    was_bytes = px * 3   # rgb565 + alpha  = 2+1 bytes
    now_bytes = px * 2   # rgb565 only     = 2 bytes
    print(f"  OK    {fname}  saved ~{(was_bytes - now_bytes)//1024} KB in compiled binary")

print("\nDone — re-flash to pick up changes.")
