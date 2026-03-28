"""
Replaces the floor-fan glyph (U+E900) in fonts/fan_icons.ttf with a
detailed pedestal fan design:
  - Thick outer guard ring
  - 3 swept propeller blades (120° apart)
  - Central hub + small axle hole
  - Vertical pole
  - Wide rectangular base

CFF winding convention (y-up, non-zero rule):
  counter-clockwise (CCW) = filled
  clockwise        (CW)   = hole
"""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen

K = 4 * (math.sqrt(2) - 1) / 3   # ≈ 0.5523  cubic Bézier circle constant


def rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (round(cx + dx * math.cos(a) - dy * math.sin(a)),
            round(cy + dx * math.sin(a) + dy * math.cos(a)))


def circle_ccw(pen, cx, cy, r):
    """Counter-clockwise circle = filled (CFF)."""
    k = K * r
    pen.moveTo((cx + r, cy))
    pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx,     cy + r))
    pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy    ))
    pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx,     cy - r))
    pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy    ))
    pen.closePath()


def circle_cw(pen, cx, cy, r):
    """Clockwise circle = hole (CFF)."""
    k = K * r
    pen.moveTo((cx + r, cy))
    pen.curveTo((cx + r, cy - k), (cx + k, cy - r), (cx,     cy - r))
    pen.curveTo((cx - k, cy - r), (cx - r, cy - k), (cx - r, cy    ))
    pen.curveTo((cx - r, cy + k), (cx - k, cy + r), (cx,     cy + r))
    pen.curveTo((cx + k, cy + r), (cx + r, cy + k), (cx + r, cy    ))
    pen.closePath()


def blade_ccw(pen, cx, cy, angle_deg):
    """
    One swept fan blade as a CCW (filled) polygon, rotated by angle_deg.
    Local coords: origin = fan centre, +y = outward toward guard ring.
    Points are ordered CCW (right-hand rule, y-up).
    """
    # CCW winding: inner-right → hub-right shoulder → outer-right → apex
    #              → outer-left → hub-left shoulder → inner-left → back
    pts_local = [
        ( 28,  48),   # hub right shoulder
        ( 68,  90),   # inner-outer right
        ( 82, 145),   # outer right
        ( 38, 168),   # outer right edge
        ( -8, 172),   # outer apex
        (-58, 152),   # outer left
        (-72,  98),   # mid left
        (-35,  52),   # hub left shoulder
        (-10,  38),   # inner left
        ( 10,  38),   # inner right
    ]
    rotated = [rot(px + cx, py + cy, cx, cy, angle_deg) for px, py in pts_local]
    pen.moveTo(rotated[0])
    for p in rotated[1:]:
        pen.lineTo(p)
    pen.closePath()


def rect_ccw(pen, x1, y1, x2, y2):
    """CCW rectangle = filled (y-up: left→up→right→down)."""
    pen.moveTo((x1, y1))
    pen.lineTo((x1, y2))
    pen.lineTo((x2, y2))
    pen.lineTo((x2, y1))
    pen.closePath()


# ── Layout constants (1000 UPM) ───────────────────────────────────────────────
CX, CY   = 500, 650   # fan head centre
R_OUT    = 215        # guard ring outer  (glyph top = 865)
R_IN     = 178        # guard ring inner
R_HUB    = 45         # hub radius
R_AXLE   = 15         # axle hole
POLE_HALF = 23        # pole half-width  (total 46 px)
POLE_TOP  = CY - R_OUT  # 435 – flush with ring bottom
POLE_BOT  = 130
BASE_Y1  = 10
BASE_Y2  = 130
BASE_X1  = 215
BASE_X2  = 785

# ── Build glyph ───────────────────────────────────────────────────────────────
font = TTFont('fonts/fan_icons.ttf')
cff  = font['CFF '].cff
top  = cff.topDictIndex[0]

pen = T2CharStringPen(1000, None)

# 1. Guard ring: filled outer (CCW) + hole inner (CW)
circle_ccw(pen, CX, CY, R_OUT)
circle_cw (pen, CX, CY, R_IN )

# 2. Three swept blades at 90°, 210°, 330°
for angle in [90, 210, 330]:
    blade_ccw(pen, CX, CY, angle)

# 3. Hub (CCW filled) + axle hole (CW hole)
circle_ccw(pen, CX, CY, R_HUB )
circle_cw (pen, CX, CY, R_AXLE)

# 4. Pole
rect_ccw(pen, CX - POLE_HALF, POLE_BOT, CX + POLE_HALF, POLE_TOP)

# 5. Base
rect_ccw(pen, BASE_X1, BASE_Y1, BASE_X2, BASE_Y2)

# ── Assign charstring back to font ────────────────────────────────────────────
cs = pen.getCharString()
cs.private = top.Private            # required for bounds calculation
top.CharStrings['floor-fan'] = cs

font.save('fonts/fan_icons.ttf')
print("floor-fan glyph replaced successfully.")
