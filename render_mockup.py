#!/usr/bin/env python3
"""
Render home-screen mockups for the Guition ESP32-S3-4848S040 (480x480).
Renders at 2x (960x960) for clarity, saves both sizes.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

SCALE = 2          # render at 2× then downscale for the 1× copy
W, H  = 480 * SCALE, 480 * SCALE

def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/NunitoSans-Bold.ttf"    if bold else "C:/Windows/Fonts/NunitoSans-Regular.ttf",
        "C:/Windows/Fonts/calibrib.ttf"            if bold else "C:/Windows/Fonts/calibril.ttf",
        "C:/Windows/Fonts/arialbd.ttf"             if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size * SCALE)
            except: pass
    return ImageFont.load_default()

F_TINY  = load_font(11)
F_SMALL = load_font(13)
F_MED   = load_font(15)
F_LARGE = load_font(26, bold=True)
F_XL    = load_font(36, bold=True)

def s(v): return v * SCALE   # scale a pixel value

def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

THEMES = {
    'dark': {
        'label':   'Dark Theme',
        'bg':       hx('343645'),
        'surface':  hx('606682'),
        'surf_opa': 0.30,
        'text':     hx('9BA2BC'),
        'dim':      hx('6A72A0'),
        'bg_image': None,
    },
    'ocean': {
        'label':   'Ocean Theme',
        'bg':       hx('0A2235'),
        'surface':  hx('174B70'),
        'surf_opa': 0.80,
        'text':     hx('88CCE8'),
        'dim':      hx('4A7A9A'),
        'bg_image': None,
    },
    'cherry': {
        'label':   'Cherry Blossom',
        'bg':       hx('1A0610'),
        'surface':  hx('8B2252'),
        'surf_opa': 0.75,
        'text':     hx('FFD6E8'),
        'dim':      hx('C07898'),
        'bg_image': 'Guition-ESP32/img/cherry_bg.png',
    },
    'patriotic': {
        'label':   'Patriotic',
        'bg':       hx('0A1628'),
        'surface':  hx('7B1113'),
        'surf_opa': 0.75,
        'text':     hx('F5F5F0'),
        'dim':      hx('6A99BB'),
        'bg_image': 'Guition-ESP32/img/patriotic_bg.png',
    },
}

def draw_panel(img, x, y, w, h, rgb, alpha, r=10):
    """Alpha-composite a rounded-rect panel onto img (RGB)."""
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rounded_rectangle(
        [s(x), s(y), s(x+w), s(y+h)], radius=s(r),
        fill=(*rgb, int(alpha*255)))
    base = img.convert('RGBA')
    img.paste(Image.alpha_composite(base, ov).convert('RGB'))

def tc(img, text, box, font, color):
    d = ImageDraw.Draw(img)
    x0,y0,x1,y1 = [v*SCALE for v in box]
    bb = d.textbbox((0,0), text, font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((x0+(x1-x0-tw)//2, y0+(y1-y0-th)//2), text, font=font, fill=color)

def tl(img, text, x, y, font, color):
    ImageDraw.Draw(img).text((s(x), s(y)), text, font=font, fill=color)

def tr(img, text, rx, y, font, color):
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0,0), text, font=font)
    d.text((s(rx)-(bb[2]-bb[0]), s(y)), text, font=font, fill=color)

def hline(img, x0, y, x1, color, alpha=80):
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).line([(s(x0),s(y)),(s(x1),s(y))], fill=(*color, alpha), width=SCALE)
    img.paste(Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB'))


def render(key):
    t      = THEMES[key]
    bg     = t['bg']
    surf   = t['surface']
    opa    = t['surf_opa']
    col    = t['text']
    dim    = t['dim']

    img = Image.new('RGB', (W, H), bg)

    # ── Background image ──────────────────────────────────────────────────────
    if t['bg_image'] and os.path.exists(t['bg_image']):
        raw = Image.open(t['bg_image']).convert('RGBA')
        raw = raw.resize((W, H), Image.LANCZOS)
        base = Image.new('RGBA', (W, H), (*bg, 255))
        img  = Image.alpha_composite(base, raw).convert('RGB')

    r = 10  # panel corner radius

    # ── Indicators bar  (y:20, 440×40) ───────────────────────────────────────
    draw_panel(img, 20, 20, 440, 40, surf, opa, r)
    tl(img, "Saturday, 3/28/2026", 33, 32, F_SMALL, dim)
    # Right-side status icons
    for sym, ox in [("⚑",140),("≈",100),("●",60),("▲",20)]:
        tr(img, sym, 460-ox+22, 31, F_SMALL, dim)

    # ── Time panel  (x:20, y:80, 220×110) ────────────────────────────────────
    draw_panel(img, 20, 80, 220, 110, surf, opa, r)
    tc(img, "3:45 PM", (20, 80, 240, 190), F_XL, col)

    # ── Weather panel  (x:250, y:80, 210×110) ────────────────────────────────
    draw_panel(img, 250, 80, 210, 110, surf, opa, r)
    # Weather icon
    try:
        wi = Image.open('Guition-ESP32/img/weather/sunny.png').convert('RGBA')
        wi = wi.resize((s(64), s(64)), Image.LANCZOS)
        tmp = img.convert('RGBA')
        tmp.paste(wi, (s(258), s(103)), wi)
        img = tmp.convert('RGB')
    except:
        ImageDraw.Draw(img).ellipse(
            [s(260),s(102),s(318),s(160)], fill=(255,200,50))
    tr(img, "72°",   458, 90,  F_LARGE, col)
    tr(img, "Sunny", 458, 160, F_SMALL, dim)

    # ── Calendar panel  (x:20, y:200, 440×175) ───────────────────────────────
    draw_panel(img, 20, 200, 440, 175, surf, opa, r)
    tl(img, "▦  Next Events", 32, 209, F_MED, dim)
    hline(img, 28, 230, 452, dim, 80)

    events = [
        ("Mar 29   10:00AM – 11:00AM", "Team standup"),
        ("Mar 30   all day",            "Spring Break"),
        ("Apr 01    2:00PM –  3:30PM",  "Doctor appointment"),
    ]
    for i, (dt, title) in enumerate(events):
        ey = 237 + i*43
        tl(img, dt,    28, ey,    F_TINY, dim)
        tl(img, title, 28, ey+14, F_MED,  col)

    # ── Bottom nav bar  (440×60, 20px from bottom) ───────────────────────────
    nav_y = 480 - 80
    draw_panel(img, 20, nav_y, 440, 60, surf, 0.25, r)
    nav_items = [("⌂","Home"),("☼","Lights"),("⚙","Devices"),("≡","Settings")]
    sw = 440 // 4
    for i,(icon,name) in enumerate(nav_items):
        bx = 20 + i*sw + (sw-58)//2
        by = nav_y + 5
        if i == 0:
            draw_panel(img, bx, by, 58, 50, bg, 0.90, 8)
        tc(img, icon, (bx, by,   bx+58, by+32), F_LARGE, col)
        tc(img, name, (bx, by+30, bx+58, by+50), F_TINY,  dim)

    # ── Bezel ─────────────────────────────────────────────────────────────────
    ImageDraw.Draw(img).rounded_rectangle(
        [SCALE,SCALE, W-SCALE, H-SCALE],
        radius=s(14), outline=(*hx('141420'),255), width=SCALE*2)

    # ── Theme label ───────────────────────────────────────────────────────────
    d   = ImageDraw.Draw(img)
    lbl = t['label']
    bb  = d.textbbox((0,0), lbl, font=F_SMALL)
    lw  = bb[2]-bb[0]
    d.text(((W-lw)//2, H - s(16)), lbl, font=F_SMALL, fill=(*dim, 140))

    return img


os.makedirs('mockups', exist_ok=True)

imgs = {}
for key in THEMES:
    hi_res = render(key)
    hi_res.save(f'mockups/mockup_{key}_2x.png')
    lo_res = hi_res.resize((480, 480), Image.LANCZOS)
    lo_res.save(f'mockups/mockup_{key}.png')
    imgs[key] = hi_res
    print(f"  mockup_{key}  ({480}×{480} + 2x)")

# 2×2 overview grid at 1× size
THUMB = 480
PAD   = 12
gw = THUMB*2 + PAD*3
gh = THUMB*2 + PAD*3
grid = Image.new('RGB', (gw, gh), hx('0D0D14'))
for idx, key in enumerate(THEMES):
    thumb = imgs[key].resize((THUMB, THUMB), Image.LANCZOS)
    ci, ri = idx % 2, idx // 2
    grid.paste(thumb, (PAD + ci*(THUMB+PAD), PAD + ri*(THUMB+PAD)))
grid.save('mockups/mockup_all_themes.png')
print("  mockup_all_themes")
print("\nDone — mockups/ directory")
