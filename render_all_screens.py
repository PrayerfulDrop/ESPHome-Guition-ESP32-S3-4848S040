#!/usr/bin/env python3
"""
Render mockups for every widget screen in the Guition ESP32-S3-4848S040 display.
All screens rendered in Dark theme (480×480 @ 2×).
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H  = 480 * SCALE, 480 * SCALE

# ── Fonts ─────────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    for p in [
        "C:/Windows/Fonts/NunitoSans-Bold.ttf"    if bold else "C:/Windows/Fonts/NunitoSans-Regular.ttf",
        "C:/Windows/Fonts/calibrib.ttf"            if bold else "C:/Windows/Fonts/calibril.ttf",
        "C:/Windows/Fonts/arialbd.ttf"             if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size * SCALE)
            except: pass
    return ImageFont.load_default()

Ftiny  = load_font(10)
Fsm    = load_font(13)
Fmed   = load_font(15)
Flg    = load_font(22, bold=True)
Fxl    = load_font(34, bold=True)
Fxxl   = load_font(52, bold=True)

# ── Colours (dark theme) ──────────────────────────────────────────────────────
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

BG      = hx('343645')
SURF    = hx('606682')
TEXT    = hx('9BA2BC')
DIM     = hx('606682')
ORANGE  = hx('FF6B2B')
SKYBLUE = hx('4FC3F7')
GREEN   = hx('5CA848')
RED     = hx('D32F2F')
WHITE   = hx('F5F5F5')
YELLOW  = hx('FFD740')
STEEL   = hx('607D8B')

OPA = 0.20   # standard panel opacity

def s(v): return v * SCALE

# ── Drawing primitives ────────────────────────────────────────────────────────
def panel(img, x, y, w, h, rgb=None, opa=OPA, r=10):
    if rgb is None: rgb = SURF
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rounded_rectangle(
        [s(x),s(y),s(x+w),s(y+h)], radius=s(r),
        fill=(*rgb, int(opa*255)))
    base = img.convert('RGBA')
    img.paste(Image.alpha_composite(base, ov).convert('RGB'))

def rect(img, x, y, w, h, rgb, r=0):
    ImageDraw.Draw(img).rounded_rectangle(
        [s(x),s(y),s(x+w),s(y+h)], radius=s(r), fill=rgb)

def circle(img, cx, cy, r, rgb):
    ImageDraw.Draw(img).ellipse(
        [s(cx-r),s(cy-r),s(cx+r),s(cy+r)], fill=rgb)

def arc_draw(img, cx, cy, r, start_a, end_a, rgb, width=8):
    d = ImageDraw.Draw(img)
    bx = [s(cx-r), s(cy-r), s(cx+r), s(cy+r)]
    d.arc(bx, start=start_a, end=end_a, fill=rgb, width=s(width))

def tc(img, text, box, font, color):
    d = ImageDraw.Draw(img)
    x0,y0,x1,y1 = [v*SCALE for v in box]
    bb = d.textbbox((0,0), text, font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((x0+(x1-x0-tw)//2, y0+(y1-y0-th)//2), text, font=font, fill=color)

def tl(img, text, x, y, font, color):
    ImageDraw.Draw(img).text((s(x),s(y)), text, font=font, fill=color)

def tr(img, text, rx, y, font, color):
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0,0),text,font=font)
    d.text((s(rx)-(bb[2]-bb[0]), s(y)), text, font=font, fill=color)

def hline(img, x0, y, x1, color=DIM, a=70):
    ov = Image.new('RGBA', img.size, (0,0,0,0))
    ImageDraw.Draw(ov).line([(s(x0),s(y)),(s(x1),s(y))], fill=(*color,a), width=SCALE)
    img.paste(Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB'))

def bezel(img):
    ImageDraw.Draw(img).rounded_rectangle(
        [SCALE,SCALE,W-SCALE,H-SCALE],
        radius=s(14), outline=(*hx('141420'),255), width=SCALE*2)

def nav_bar(img, active=0):
    """Draw the bottom navigation bar. active: 0=Home,1=Lights,2=Devices,3=Settings"""
    ny = 480 - 80
    panel(img, 20, ny, 440, 60, SURF, 0.25)
    items = [("⌂","Home"),("☼","Lights"),("⚙","Devices"),("≡","Settings")]
    sw = 440 // 4
    for i,(icon,name) in enumerate(items):
        bx = 20 + i*sw + (sw-58)//2
        by = ny + 5
        if i == active:
            panel(img, bx, by, 58, 50, BG, 0.90, 8)
        tc(img, icon, (bx,by,   bx+58,by+32), Flg, TEXT)
        tc(img, name, (bx,by+30,bx+58,by+50), Ftiny, DIM)

def back_btn(img, x=20, y=400):
    panel(img, x, y, 60, 60, SURF, OPA)
    tc(img, "←", (x,y,x+60,y+60), Flg, TEXT)

def title_bar(img, text, y=20, h=40):
    panel(img, 20, y, 440, h)
    tc(img, text, (20,y,460,y+h), Fmed, TEXT)

def name_bar(img, text, y=400):
    panel(img, 100, y, 360, 60)
    tl(img, text, 120, y+22, Fsm, TEXT)

def new_screen(label=None):
    img = Image.new('RGB', (W,H), BG)
    if label:
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), label, font=Fsm)
        lw = bb[2]-bb[0]
        d.text(((W-lw)//2, H-s(16)), label, font=Fsm, fill=(*DIM,140))
    return img

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def screen_lights():
    img = new_screen("Lights")
    lights = [
        ("ceiling_lamp","Main Lights",  True),
        ("night_lamp",  "Lamps",        False),
        ("night_lamp",  "Night Light",  True),
        ("bed",         "Bedtime",      False),
        ("",            "",             False),
        ("",            "",             False),
    ]
    cols = [(20,20),(170,20),(320,20),(20,200),(170,200),(320,200)]
    icons = {"ceiling_lamp":"⊙","night_lamp":"☽","bed":"⌂","":"-"}
    for i,((bx,by),(icon_key,name,on)) in enumerate(zip(cols,lights)):
        opa = 0.45 if on else OPA
        clr = TEXT if on else DIM
        panel(img, bx, by, 140, 150, SURF, opa)
        sym = icons.get(icon_key, "○")
        if name:
            tc(img, sym,  (bx,by+20,bx+140,by+100), Flg,  clr)
            tc(img, name, (bx,by+5, bx+140,by+35),  Ftiny, TEXT)
        else:
            tc(img, "—", (bx,by,bx+140,by+150), Fmed, DIM)
    nav_bar(img, active=1)
    bezel(img)
    return img

def screen_fans():
    img = new_screen("Fans")
    fans = [
        ("fan","Ceiling Fan", True),
        ("fan","Floor Fan",   False),
        ("","",               False),
        ("","",               False),
        ("","",               False),
        ("","",               False),
    ]
    cols = [(20,20),(170,20),(320,20),(20,200),(170,200),(320,200)]
    for i,((bx,by),(icon,name,on)) in enumerate(zip(cols,fans)):
        opa = 0.45 if on else OPA
        clr = TEXT if on else DIM
        panel(img, bx, by, 140, 150, SURF, opa)
        if name:
            tc(img, "⊛",  (bx,by+28,bx+140,by+110), Flg,  clr)
            tc(img, name, (bx,by+8, bx+140,by+32),   Ftiny, TEXT)
        else:
            tc(img, "—", (bx,by,bx+140,by+150), Fmed, DIM)
    nav_bar(img, active=1)
    bezel(img)
    return img

def screen_devices():
    img = new_screen("Devices")
    panel(img, 20, 20, 440, 340, SURF, OPA)

    # Row 1: Alarm | Media Player | Vacuum
    row1_btns = [(35,"⚑","Alarm"),(170,"♪","Media"),(305,"⊙","Vacuum")]
    for bx,icon,lbl in row1_btns:
        panel(img, bx, 30, 100, 100, BG, 0.60)
        tc(img, icon, (bx,30,bx+100,30+75), Flg, STEEL)
        tc(img, lbl,  (bx,30+72,bx+100,30+100), Ftiny, DIM)

    # Row 2: HVAC | Fans
    row2_btns = [(35,"⊘","HVAC"),(170,"⊛","Fans")]
    for bx,icon,lbl in row2_btns:
        panel(img, bx, 150, 100, 100, BG, 0.60)
        tc(img, icon, (bx,150,bx+100,150+75), Flg, STEEL)
        tc(img, lbl,  (bx,150+72,bx+100,150+100), Ftiny, DIM)

    nav_bar(img, active=2)
    bezel(img)
    return img

def screen_settings():
    img = new_screen("Settings")
    rows = [
        (20,  "Language",  "English (US)"),
        (110, "Theme",     "Dark Theme"),
        (200, "Backlight", None),       # slider
        (290, "Sleep mode (sec)", "120"),
    ]
    for y,label,value in rows:
        panel(img, 20, y, 440, 80)
        tl(img, label, 40, y+30, Fmed, TEXT)
        if value:
            tr(img, value, 450, y+30, Fmed, DIM)
        else:
            # Draw a slider
            sx, sy, sw, sh = 190, y+32, 240, 16
            rect(img, sx,   sy,   sw,  sh, DIM, r=4)
            rect(img, sx,   sy,   160, sh, hx('9BA2BC'), r=4)
            circle(img, sx+160, sy+sh//2, 10, TEXT)

    nav_bar(img, active=3)
    bezel(img)
    return img

def screen_hvac():
    img = new_screen("HVAC")

    # State bar
    panel(img, 20, 20, 400, 60)
    tl(img, "Heating", 40, 38, Fmed, ORANGE)

    # Mode buttons (left side)
    panel(img, 15, 100, 210, 90)
    for bx,clr,sym,lbl in [(25,ORANGE,"♨","Heat"),(95,SKYBLUE,"❄","Cool"),(165,DIM,"○","Off")]:
        circle(img, bx+30, 145, 30, clr if lbl!="Off" else hx('3A3C50'))
        tc(img, sym, (bx,120,bx+60,170), Fmed, WHITE if lbl!="Off" else DIM)

    # Name bar
    panel(img, 100, 400, 360, 60)
    tl(img, "Living Room Thermostat", 120, 418, Fsm, TEXT)

    # Back button
    back_btn(img)

    # Right arc area (offset right)
    cx, cy = 355, 240

    # Background circle
    circle(img, cx, cy, 200, hx('2D2F42'))

    # Gradient temperature background (simplified)
    for angle in range(100, 261, 3):
        t = (angle-100)/160.0
        r2 = int(255*t); g2 = int(200*(1-t)); b2 = 50
        arc_draw(img, cx, cy, 195, angle-90, angle-87, (r2,g2,b2), width=12)

    # Target temp arc (orange, ~70% filled)
    arc_draw(img, cx, cy, 195, 10-90, 122-90, ORANGE, width=18)

    # Current temp indicator (small arc)
    arc_draw(img, cx, cy, 183, 60-90, 63-90, TEXT, width=6)

    # Temperature display
    tc(img, "72", (cx-45, cy-50, cx+15, cy+20), Fxxl, ORANGE)
    tc(img, ".0", (cx+10, cy-20, cx+50, cy+10), Fmed, ORANGE)
    tc(img, "°F", (cx+10, cy-50, cx+50, cy-20), Fsm, ORANGE)

    # Current temp label
    tc(img, "69.5°", (cx-40, cy+60, cx+60, cy+85), Fsm, TEXT)

    # Mode icon (heating flame)
    tc(img, "♨", (cx+30, cy-100, cx+70, cy-60), Flg, ORANGE)

    bezel(img)
    return img

def screen_alarm():
    img = new_screen("Alarm Panel")

    # State bar
    panel(img, 20, 20, 440, 80)
    circle(img, 55, 60, 30, hx('3A3C50'))
    tc(img, "⚑", (25,30,85,90), Flg, GREEN)
    tl(img, "Disarmed", 110, 48, Fmed, GREEN)

    # Control area
    panel(img, 20, 120, 440, 260)

    # Central disarm button
    circle(img, 240, 250, 80, hx('2A4A2A'))
    tc(img, "⚑", (160,170,320,330), Fxl, GREEN)

    # Surrounding mode buttons
    for (cx2,cy2,clr,sym,lbl) in [
        (155,185, hx('2A3A50'), "⌂", "Home"),
        (325,185, hx('3A3020'), "→", "Away"),
        (155,315, hx('202A3A'), "☽", "Night"),
        (325,315, hx('2A2040'), "✈", "Vacation"),
    ]:
        circle(img, cx2, cy2, 40, clr)
        tc(img, sym, (cx2-40,cy2-40,cx2+40,cy2+40), Fmed, TEXT)

    back_btn(img)
    panel(img, 100, 400, 360, 60)
    tl(img, "Home Security System", 120, 418, Fsm, TEXT)
    bezel(img)
    return img

def screen_media():
    img = new_screen("Media Player")

    # Album art
    panel(img, 10, 10, 140, 140, hx('4A2060'), 1.0, r=20)
    tc(img, "♪", (10,10,150,150), Fxxl, hx('9060C0'))

    # Title / artist / slider  (right of art)
    panel(img, 160, 10, 310, 140)
    tl(img, "Blinding Lights",        170, 22,  Fmed, TEXT)
    tl(img, "The Weeknd",             170, 45,  Fsm,  DIM)
    tl(img, "Starboy (Album)",        170, 65,  Fsm,  DIM)
    # Progress bar
    rect(img, 170, 100, 280, 6,  DIM, r=3)
    rect(img, 170, 100, 120, 6,  TEXT, r=3)
    circle(img, 290, 103, 6, TEXT)
    tl(img, "2:04",   170, 112, Ftiny, DIM)
    tr(img, "3:22",   445, 112, Ftiny, DIM)

    # Control buttons row
    panel(img, 0, 155, 480, 120)
    ctrls = [(20,"⏻"),(100,"⏮"),(175,"⏸"),(335,"⏭"),(415,"↺")]
    for bx,sym in ctrls:
        if sym == "⏸":
            circle(img, bx+50, 215, 45, SURF)
        tc(img, sym, (bx,175,bx+100,255), Flg, TEXT if sym!="⏸" else WHITE)

    # Volume row
    panel(img, 0, 290, 480, 80)
    tc(img, "🔇", (10,290,60,370), Fmed, DIM)
    tc(img, "－", (60,290,110,370), Fmed, DIM)
    rect(img, 110, 325, 280, 8, DIM, r=4)
    rect(img, 110, 325, 185, 8, TEXT, r=4)
    circle(img, 295, 329, 7, TEXT)
    tc(img, "＋", (395,290,450,370), Fmed, DIM)

    back_btn(img)
    name_bar(img, "Living Room Speaker")
    bezel(img)
    return img

def screen_vacuum():
    img = new_screen("Vacuum")

    # Main display area
    panel(img, 0, 20, 480, 240)

    # Fan speed  (top-left of panel)
    tl(img, "⊙ Max", 18, 30, Fsm, DIM)

    # Battery (bottom-left)
    tl(img, "▮ 85%", 18, 220, Fsm, GREEN)

    # State (top-right)
    tr(img, "Cleaning", 462, 30, Fsm, TEXT)

    # Cleaned area (bottom-right)
    tr(img, "⊞ 12.5 m²", 462, 220, Fsm, DIM)

    # Vacuum body (animated image placeholder)
    vx, vy, vr = 240, 140, 90
    circle(img, vx, vy, vr, hx('2A2C40'))
    circle(img, vx, vy, vr-12, hx('1E2030'))
    circle(img, vx, vy, 18, hx('606682'))
    # Rotating brush indicator
    for angle in range(0, 360, 40):
        rad = math.radians(angle)
        bx2 = int(vx + (vr-24)*math.cos(rad))
        by2 = int(vy + (vr-24)*math.sin(rad))
        circle(img, bx2, by2, 4, hx('4FC3F7'))
    tc(img, "⊙", (vx-20, vy-20, vx+20, vy+20), Fmed, DIM)

    # Controls (docked state)
    panel(img, 20, 280, 440, 100)
    for bx,sym,lbl,clr in [(60,"▷","Start",GREEN),(220,"⊙","Locate",SKYBLUE)]:
        panel(img, bx, 290, 80, 80, clr, 0.25, r=40)
        tc(img, sym,  (bx,290,bx+80,350), Flg, clr)
        tc(img, lbl,  (bx,348,bx+80,370), Ftiny, DIM)

    back_btn(img)
    name_bar(img, "Roomba J7+")
    bezel(img)
    return img

def screen_weather():
    img = new_screen("Weather Forecast")

    # Title bar
    panel(img, 20, 20, 440, 40)
    tc(img, "5-Day Forecast", (20,20,460,60), Fmed, TEXT)

    # Today hero card
    panel(img, 20, 70, 440, 130)
    try:
        wi = Image.open('Guition-ESP32/img/weather/sunny.png').convert('RGBA')
        wi = wi.resize((s(70),s(70)), Image.LANCZOS)
        tmp = img.convert('RGBA')
        tmp.paste(wi, (s(30),s(90)), wi)
        img = tmp.convert('RGB')
    except:
        circle(img, 65, 135, 35, YELLOW)
    tl(img, "Today",     145, 90,  Fmed, TEXT)
    tl(img, "75°",       145, 112, Flg,  ORANGE)
    tl(img, "Low 62°",   230, 122, Fsm,  SKYBLUE)
    tr(img, "20%",       452, 90,  Fsm,  SKYBLUE)
    tr(img, "rain",      452, 110, Ftiny, DIM)
    tr(img, "Sunny",     452, 155, Fsm,  DIM)

    # 4 day forecast cards
    days = [
        ("Sun","sunny",    "78°","60°"),
        ("Mon","cloudy",   "70°","58°"),
        ("Tue","rainy",    "65°","54°"),
        ("Wed","sunny",    "72°","56°"),
    ]
    day_icons = {"sunny":YELLOW,"cloudy":DIM,"rainy":SKYBLUE,"snowy":WHITE}
    for i,(day,cond,hi,lo) in enumerate(days):
        cx2 = 20 + i*108
        panel(img, cx2, 210, 100, 170, SURF, OPA)
        tc(img, day,  (cx2,212,cx2+100,232), Fsm, DIM)
        # Weather circle
        clr = day_icons.get(cond, DIM)
        circle(img, cx2+50, 272, 28, clr if cond=="sunny" else hx('2D2F42'))
        sym = "☀" if cond=="sunny" else ("☁" if cond=="cloudy" else "🌧" if cond=="rainy" else "❄")
        tc(img, sym,  (cx2+20,250,cx2+80,300), Fmed, clr)
        tc(img, hi,   (cx2,320,cx2+100,345), Fsm, ORANGE)
        tc(img, lo,   (cx2,345,cx2+100,370), Fsm, SKYBLUE)

    # Buttons row
    panel(img, 20, 400, 200, 50)
    tc(img, "← Back", (20,400,220,450), Fmed, TEXT)
    panel(img, 260, 400, 200, 50)
    tc(img, "↻ Refresh", (260,400,460,450), Fmed, TEXT)

    bezel(img)
    return img

def screen_thermostat():
    img = new_screen("Thermostat")

    # State bar
    panel(img, 20, 20, 400, 60)
    tl(img, "Heating", 40, 38, Fmed, ORANGE)

    # Controls panel (left)
    panel(img, 100, 100, 260, 280)

    # Preset mode (home/away) — top-left inside controls
    circle(img, 155, 175, 35, hx('1A3A1A'))
    tc(img, "⌂", (120,140,190,210), Flg, GREEN)

    # Power toggle
    circle(img, 155, 265, 35, hx('3A1A0A'))
    tc(img, "⏻", (120,230,190,300), Flg, ORANGE)

    # + / - buttons (left of controls panel)
    panel(img, 5, 140, 90, 90)
    tc(img, "+", (5,140,95,230), Flg, TEXT)
    panel(img, 5, 260, 90, 90)
    tc(img, "−", (5,260,95,350), Flg, TEXT)

    # Name bar
    panel(img, 100, 400, 360, 60)
    tl(img, "Upstairs Thermostat", 120, 418, Fsm, TEXT)
    back_btn(img)

    # Right arc area
    cx, cy = 355, 240
    circle(img, cx, cy, 200, hx('2D2F42'))
    for angle in range(100, 261, 3):
        t = (angle-100)/160.0
        arc_draw(img, cx, cy, 195, angle-90, angle-87, (int(255*t),int(200*(1-t)),50), width=10)
    arc_draw(img, cx, cy, 195, 10-90, 110-90, ORANGE, width=18)
    arc_draw(img, cx, cy, 183, 65-90, 68-90, TEXT, width=6)
    tc(img, "71",   (cx-48,cy-50,cx+12,cy+20), Fxxl, ORANGE)
    tc(img, ".0°F", (cx+10,cy-30,cx+65,cy+10), Fsm,  ORANGE)
    tc(img, "69.2°", (cx-40,cy+60,cx+60,cy+85), Fsm, TEXT)
    tc(img, "♨",    (cx+30,cy-100,cx+75,cy-55), Flg, ORANGE)

    bezel(img)
    return img

def screen_ac():
    img = new_screen("Air Conditioner")

    # State bar
    panel(img, 20, 20, 400, 60)
    tl(img, "Cooling", 40, 38, Fmed, SKYBLUE)

    # Controls panel (left — + / - only for AC)
    panel(img, 20, 100, 360, 280)
    # + button
    panel(img, 30, 130, 80, 80, SURF, 0.4)
    tc(img, "+", (30,130,110,210), Flg, TEXT)
    # - button
    panel(img, 30, 260, 80, 80, SURF, 0.4)
    tc(img, "−", (30,260,110,340), Flg, TEXT)

    # Name bar
    panel(img, 100, 400, 360, 60)
    lbl2 = "Downstairs AC"
    tl(img, lbl2, 120, 418, Fsm, TEXT)
    back_btn(img)

    # Right arc area (blue palette)
    cx, cy = 355, 240
    circle(img, cx, cy, 200, hx('0D1A2D'))
    arc_draw(img, cx, cy, 195, 10-90, 155-90, SKYBLUE, width=18)
    arc_draw(img, cx, cy, 183, 80-90, 83-90, TEXT, width=6)
    tc(img, "76",   (cx-48,cy-50,cx+12,cy+20), Fxxl, SKYBLUE)
    tc(img, ".0°F", (cx+10,cy-30,cx+65,cy+10), Fsm,  SKYBLUE)
    tc(img, "78.0°", (cx-40,cy+60,cx+60,cy+85), Fsm, TEXT)
    tc(img, "❄",    (cx+30,cy-100,cx+75,cy-55), Flg, SKYBLUE)

    bezel(img)
    return img

# ══════════════════════════════════════════════════════════════════════════════
# RENDER + SAVE ALL
# ══════════════════════════════════════════════════════════════════════════════
SCREENS = [
    ("home",         "Home",           None),             # rendered separately
    ("lights",       "Lights",         screen_lights),
    ("fans",         "Fans",           screen_fans),
    ("devices",      "Devices",        screen_devices),
    ("settings",     "Settings",       screen_settings),
    ("hvac",         "HVAC",           screen_hvac),
    ("thermostat",   "Thermostat",     screen_thermostat),
    ("ac",           "Air Conditioner",screen_ac),
    ("alarm",        "Alarm Panel",    screen_alarm),
    ("media",        "Media Player",   screen_media),
    ("vacuum",       "Vacuum",         screen_vacuum),
    ("weather",      "Weather Forecast",screen_weather),
]

os.makedirs('mockups', exist_ok=True)

imgs = {}
for key, label, fn in SCREENS:
    if fn is None:
        # Load previously rendered home screen
        try:
            imgs[key] = Image.open('mockups/mockup_dark_2x.png')
            print(f"  {key:<18} (loaded existing)")
        except:
            print(f"  {key:<18} (not found — run render_mockup.py first)")
        continue
    imgs[key] = fn()
    imgs[key].save(f'mockups/screen_{key}_2x.png')
    # Also save 1× version
    imgs[key].resize((480,480), Image.LANCZOS).save(f'mockups/screen_{key}.png')
    print(f"  {key:<18} done")

# ── Master overview grid (4 columns) ─────────────────────────────────────────
THUMB = 240
PAD   = 8
keys = [k for k,_,_ in SCREENS]
ncols = 4
nrows = math.ceil(len(keys)/ncols)
gw = THUMB*ncols + PAD*(ncols+1)
gh = THUMB*nrows + PAD*(nrows+1) + 30
grid = Image.new('RGB', (gw, gh), hx('0D0D14'))
gd   = ImageDraw.Draw(grid)

for idx, key in enumerate(keys):
    if key not in imgs: continue
    thumb = imgs[key].resize((THUMB, THUMB), Image.LANCZOS)
    ci, ri = idx % ncols, idx // ncols
    gx = PAD + ci*(THUMB+PAD)
    gy = PAD + ri*(THUMB+PAD)
    grid.paste(thumb, (gx, gy))
    # Label overlay
    lbl = next(l for k,l,_ in SCREENS if k==key)
    gd.text((gx+4, gy+4), lbl, font=Fsm, fill=(*WHITE, 200))

grid.save('mockups/all_screens_overview.png')
print("\n  all_screens_overview.png  done")
print(f"\nDone — {len([k for k,_,f in SCREENS if f])} screens rendered to mockups/")
