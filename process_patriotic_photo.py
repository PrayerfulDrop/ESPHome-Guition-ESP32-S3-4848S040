#!/usr/bin/env python3
"""
Process patriotic.jpg -> Guition-ESP32/img/patriotic_bg.png  (480x480 RGBA)

Treatment:
  1. Scale to fill 480x480, centre-crop
  2. Patriotic colour grade -- boost red/blue, pull green to deepen
     saturation toward the red/white/blue flag aesthetic
  3. Diagonal flag-wave gradient -- navy wash upper-left, crimson lower-right
  4. Navy-blue unifying tint (12%) ties image to deep-navy theme background
  5. Darken to 68%  -- background must not compete with UI widgets
  6. Radial vignette  -- pull edges darker so panels float cleanly
  7. Top-edge fade  -- smooth header area for clock / indicators row
  8. RGBA alpha=195 base (76%)  -- blends with page bg without disappearing
"""
import numpy as np
from PIL import Image, ImageFilter
import os, sys

SRC = 'patriotic.jpg'
OUT = 'Guition-ESP32/img/patriotic_bg.png'
W, H = 480, 480

NAVY    = np.array([ 10,  22,  40], dtype=float)   # #0A1628  deep navy
CRIMSON = np.array([178,  34,  34], dtype=float)   # #B22222  American flag red

if not os.path.exists(SRC):
    print(f"ERROR: source not found at '{SRC}'")
    sys.exit(1)

# -- Load & convert ----------------------------------------------------------
src = Image.open(SRC).convert('RGB')
ow, oh = src.size
print(f"Source: {ow}x{oh}  ({SRC})")

# -- Scale to fill 480x480, centre-crop -------------------------------------
scale = max(W / ow, H / oh)
nw    = round(ow * scale)
nh    = round(oh * scale)
src   = src.resize((nw, nh), Image.LANCZOS)
cx    = (nw - W) // 2
cy    = (nh - H) // 2
src   = src.crop((cx, cy, cx + W, cy + H))
print(f"Scaled to {nw}x{nh}, cropped to {W}x{H}  (offset {cx},{cy})")

arr = np.array(src, dtype=float)   # H x W x 3

# -- Patriotic colour grade -------------------------------------------------
arr[..., 0] = np.clip(arr[..., 0] * 1.18, 0, 255)   # R +18%
arr[..., 1] = np.clip(arr[..., 1] * 0.85, 0, 255)   # G -15%  (removes yellow cast)
arr[..., 2] = np.clip(arr[..., 2] * 1.12, 0, 255)   # B +12%

# -- Diagonal flag-wave gradient overlay ------------------------------------
# Navy washes from upper-left; crimson warms lower-right
Y_g, X_g = np.ogrid[:H, :W]
diag = np.clip((X_g + Y_g) / (W + H - 2), 0.0, 1.0)
tint = NAVY * (1.0 - diag)[..., np.newaxis] + CRIMSON * diag[..., np.newaxis]
arr  = np.clip(arr * 0.82 + tint * 0.18, 0, 255)

# -- Navy unifying tint -----------------------------------------------------
arr = np.clip(arr * 0.88 + NAVY * 0.12, 0, 255)

# -- Global darken ----------------------------------------------------------
arr *= 0.68

# -- Radial vignette --------------------------------------------------------
dx   = (X_g - W / 2) / (W / 2)
dy   = (Y_g - H / 2) / (H / 2)
dist = np.sqrt(dx ** 2 + dy ** 2)
vig  = np.clip(1.0 - 0.44 * dist ** 1.5, 0.25, 1.0)
arr  = np.clip(arr * vig[..., np.newaxis], 0, 255)

# -- Alpha channel ----------------------------------------------------------
alpha    = np.full((H, W), 195, dtype=float)
top_fade = np.clip(np.arange(H, dtype=float) / 50.0, 0.55, 1.0)
alpha   *= top_fade[:, np.newaxis]
alpha    = np.clip(alpha, 0, 255)

# -- Assemble RGBA ----------------------------------------------------------
out_arr = np.concatenate([arr, alpha[..., np.newaxis]], axis=-1).astype(np.uint8)
result  = Image.fromarray(out_arr, 'RGBA')
result  = result.filter(ImageFilter.GaussianBlur(radius=0.6))

# -- Save -------------------------------------------------------------------
os.makedirs('Guition-ESP32/img', exist_ok=True)
result.save(OUT, 'PNG')
print(f"\nSaved  {OUT}  ({os.path.getsize(OUT) // 1024} KB)")
print(f"Canvas: {result.size}, mode: {result.mode}")
