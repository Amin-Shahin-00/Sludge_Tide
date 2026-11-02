"""Environments. Each set is built from Grease Pencil 'cards' placed at different
depths (y, BU behind the subject plane) so camera moves get real parallax. A card
is authored in HOME SCREEN px (1920x1080, y down) and scaled so that, in the home
framing, it lands exactly where it was drawn. Card drawings are shared datablocks:
a set used by ten shots is drawn once.
"""
import math
import bpy
import numpy as np
from . import geo, gp, stage
from .gp import Pen, TPen, INK

LW = 5.0


def card(coll, name, depth, draw, frames=None, loop=False):
    """GP card at depth; draw(pen) authors it in home px. frames: list of draw fns for an animated card."""
    gpd = bpy.data.grease_pencils.get(f"set.{name}")
    if gpd is None:
        gpd = gp.new_gp(f"set.{name}")
        if frames:
            for k, fn in enumerate(frames):
                fn(Pen(gpd, "art", k + 1, origin=(960, 540)))
        else:
            draw(Pen(gpd, "art", 1, origin=(960, 540)))
    ob = bpy.data.objects.new(f"{coll.name}.{name}", gpd)
    k = (stage.CAM_DIST + depth) / stage.CAM_DIST
    ob.location = (0, depth, 0)
    ob.scale = (k, k, k)
    coll.objects.link(ob)
    if frames and loop:
        md = ob.grease_pencil_modifiers.new("loop", "GP_TIME")
        md.mode = "NORMAL"
        md.use_keep_loop = True
    return ob


def R(seed):
    return np.random.default_rng(seed)


# ============================================================================ shared pieces

def sea_card(pen, y0, cols, waves=True, seed=1, w=4200, sparkle="#ffffff", lines_col=None):
    """Sea from y0 down: bands of colour + wave dashes."""
    x0, x1 = 960 - w / 2, 960 + w / 2
    n = len(cols)
    for i, c in enumerate(cols):
        ya = y0 + (1400 - y0) * (i / n) ** 1.6
        pen.fill(geo.rect(x0, ya, x1, 2400), c)
    if waves:
        r = R(seed)
        for k in range(160):
            yy = y0 + 10 + (r.random() ** 1.7) * 900
            xx = r.uniform(x0, x1)
            L = 20 + (yy - y0) * 0.12 * r.uniform(0.6, 1.4)
            pen.line(geo.qbez((xx - L, yy), (xx, yy - 4), (xx + L, yy), 6), 2 + (yy - y0) * 0.006, col=lines_col or sparkle, alpha=0.75)


def cloud(pen, x, y, s, col="#ffffff", shade="#c9d8f0", seed=0):
    r = R(seed)
    blobs = [(x + r.uniform(-120, 120) * s, y + r.uniform(-20, 30) * s, r.uniform(50, 90) * s) for _ in range(6)]
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    U = unary_union([Polygon(geo.circle(bx, by, br, 24)) for bx, by, br in blobs])
    U = U.union(Polygon(geo.rect(x - 160 * s, y + 10 * s, x + 160 * s, y + 50 * s)))
    pts = geo.poly_pts(U)
    pen.fill(pts, col)
    pen.fill(geo.poly_pts(Polygon(pts).intersection(Polygon(geo.rect(x - 400 * s, y + 18 * s, x + 400 * s, y + 200 * s)))), shade)
    pen.line(pts, 3.0, col=shade, closed=True, alpha=0.8)


def house(pen, x, y, w, h, col, roof, tilt=0.0, seed=0, door=True, lw=LW):
    """A crooked little house: box + roof + windows, origin bottom-centre."""
    g = TPen(pen, x, y, 1.0, tilt)
    r = R(seed)
    g.shape(geo.rect(-w / 2, -h, w / 2, 0), col, lw, depth=w * 0.08)
    g.shape(np.array([(-w / 2 - 14, -h), (w / 2 + 14, -h), (w * 0.1 * r.uniform(-1, 1), -h - h * 0.55)]), roof, lw, depth=8)
    for k in range(int(r.integers(1, 3))):
        wx = -w / 2 + w * (0.25 + 0.5 * k) - 12
        g.shape(geo.rect(wx, -h * 0.75, wx + 24, -h * 0.45), "#ffe9a8", lw * 0.6, shade=0.3)
        g.line([(wx + 12, -h * 0.75), (wx + 12, -h * 0.45)], lw * 0.4)
    if door:
        g.shape(geo.rect(w * 0.15, -h * 0.5, w * 0.15 + 22, 0), mix_dark(col), lw * 0.6, shade=0.3)
    if r.random() < 0.5:
        g.shape(geo.rect(-w * 0.35, -h * 0.4, -w * 0.05, -h * 0.15), "#b98a5a", lw * 0.4, shade=0.2)     # patch


def mix_dark(c, k=0.55):
    return gp.hexs(gp.multiply(c, "#3a2a4a", k))


def stilt(pen, x, y_top, y_bot, w=70, col="#6e6a72", rust=0.0):
    pen.shape(geo.rect(x - w / 2, y_top, x + w / 2, y_bot), col, LW, depth=w * 0.25)
    for yy in np.arange(y_top + 40, y_bot, 90):
        pen.line([(x - w / 2, yy), (x + w / 2, yy)], LW * 0.7)
        for sx in (-1, 1):
            pen.dot(x + sx * w * 0.32, yy - 12, 4, "#4a464e")
    pen.fill(geo.rect(x - w / 2 + 6, y_top + 6, x - w / 2 + 16, y_bot - 6), "#9a96a0", 0.6)


def tumble_stack(pen, cx, base_y, seed=3, scale=1.0, cols=None):
    """Tumble Island: houses stacked like toy blocks with ladders, rope bridges, flags."""
    r = R(seed)
    cols = cols or ["#ff7a5c", "#ffd23c", "#59c3e8", "#9be070", "#ff9ec9", "#f4f1e6", "#c79bff", "#ff9c3c"]
    roofs = ["#c8432f", "#3a6e8c", "#7a4a2a", "#2f8a6a", "#8c3a6e"]
    levels = []
    y = base_y
    width = 900 * scale
    rows = 6
    for row in range(rows):
        n = max(2, int(6 - row * 0.8))
        span = width * (1 - row * 0.14)
        xs = np.linspace(cx - span / 2, cx + span / 2, n)
        hrow = (90 + r.uniform(0, 40)) * scale
        row_items = []
        for i, xx in enumerate(xs):
            w = r.uniform(110, 170) * scale
            h = r.uniform(80, 130) * scale
            xx += r.uniform(-30, 30) * scale
            house(pen, xx, y, w, h, cols[r.integers(len(cols))], roofs[r.integers(len(roofs))], tilt=r.uniform(-0.08, 0.08),
                  seed=int(r.integers(1e6)), lw=LW * scale)
            row_items.append((xx, y - h, w))
        levels.append(row_items)
        y -= hrow + 40 * scale
    # ladders & rope bridges
    for row in levels[:-1]:
        for (xx, yy, w) in row[:-1]:
            nx = xx + w + 40
            pen.line(geo.qbez((xx + w * 0.45, yy + 30), ((xx + nx) / 2, yy + 70), (nx - w * 0.3, yy + 30), 10), 3 * scale, col="#7a5a3a")
            for u in np.linspace(0.1, 0.9, 6):
                q = geo.qbez((xx + w * 0.45, yy + 30), ((xx + nx) / 2, yy + 70), (nx - w * 0.3, yy + 30), 7)[int(u * 6)]
                pen.line([(q[0], q[1]), (q[0], q[1] + 10 * scale)], 2 * scale, col="#7a5a3a")
    top = levels[-1][0]
    pen.line([(top[0], top[1] - 40 * scale), (top[0], top[1] - 180 * scale)], 4 * scale)
    pen.shape(np.array([(top[0], top[1] - 180 * scale), (top[0] + 90 * scale, top[1] - 160 * scale), (top[0] + 70 * scale, top[1] - 150 * scale),
                        (top[0] + 86 * scale, top[1] - 132 * scale), (top[0], top[1] - 128 * scale)]), "#e8392f", 3 * scale, shade=0.3)


# ============================================================================ GLOAMWORKS ISLE (night exterior)

def gloam_isle_night(sh):
    co = sh.co
    stage.gradient_bg(co, "sky", [(0.0, "#2a2350"), (0.55, "#151332"), (1.0, "#0a0a1c")], depth=80)

    def stars(pen):
        r = R(7)
        for k in range(160):
            x, y = r.uniform(-900, 2800), r.uniform(-500, 520)
            pen.dot(x, y, r.uniform(1, 2.6), "#fff6d8")
        pen.fill(geo.circle(1520, 150, 110, 40), "#fff4cf", 0.08)
        for cr in geo.crescent(geo.circle(1520, 150, 70, 48), (30, -14)):
            pen.fill(cr, "#fff4cf")
    card(co, "night_stars", 60, stars)

    def isle(pen):
        pen.shape(geo.blob([(300, 760), (420, 560), (700, 520), (1100, 500), (1500, 540), (1700, 620), (1800, 760)], n=6),
                  "#4a4a58", LW, depth=40)
        for k, (x, w, h) in enumerate(((560, 300, 200), (900, 380, 260), (1260, 320, 220))):
            pen.shape(geo.rect(x - w / 2, 560 - h, x + w / 2, 600), "#5c5c6c", LW, depth=30)
            for j in range(4):
                pen.fill(geo.rect(x - w / 2 + 30 + j * 70, 560 - h + 40, x - w / 2 + 70 + j * 70, 560 - h + 70), "#2f2f3a")
        for k, x in enumerate((520, 700, 860, 1040, 1220, 1380)):         # trumpet chimneys
            top = 120 + (k % 3) * 40
            pen.shape(np.array([(x - 16, 420), (x + 16, 420), (x + 18, top + 60), (x + 60, top), (x - 60, top), (x - 18, top + 60)]),
                      "#6e6a7a", LW, depth=10)
            pen.shape(geo.ellipse(x, top, 60, 14, 24), "#3a3846", LW * 0.8, shade=0.2)
        pen.fill(geo.rect(1100, 380, 1130, 400), "#ffe08a")
        pen.fill(geo.rect(640, 420, 664, 440), "#ffe08a")
    card(co, "gloam_isle", 30, isle)

    def water(pen):
        sea_card(pen, 740, ["#1c2a4a", "#16223e", "#101a30"], seed=2, sparkle="#6f86c0")
    card(co, "night_sea", 8, water)


# ============================================================================ FACTORY INTERIORS

def hallway(sh, door_light=True):
    co = sh.co

    def bg(pen):
        pen.fill(geo.rect(-1500, -800, 3500, 1800), "#3a3e52")
        pen.fill(geo.rect(-1500, 760, 3500, 1800), "#2a2c3c")                 # floor
        for k in range(30):                                                    # floor tiles
            x = -1500 + k * 180
            pen.line([(x, 760), (x - 120, 1800)], 2, col="#3a3e52")
        for y in (820, 920, 1060):
            pen.line([(-1500, y), (3500, y)], 2, col="#3a3e52")
        pen.line([(-1500, 760), (3500, 760)], LW)
        for k in range(10):                                                    # wall panels + pipes
            x = -1400 + k * 520
            pen.shape(geo.rect(x, 160, x + 440, 700), "#454a62", LW * 0.8, depth=10)
            pen.fill(geo.rect(x + 200, 180, x + 240, 210), "#ffe9a0", 0.6)
        pen.tube([(-1500, 110), (3500, 110)], 40, "#59607a", LW)
        pen.tube([(-1500, 60), (3500, 60)], 22, "#6d4a5a", LW)
        for k in range(14):
            pen.shape(geo.rect(-1450 + k * 380, 95, -1430 + k * 380, 125), "#2f3346", LW * 0.6, shade=0)
        # the always-locked door
        pen.shape(geo.rect(1380, 260, 1640, 760), "#5a5e78", LW, depth=16)
        pen.shape(geo.rect(1400, 290, 1620, 740), "#6a6f8c", LW * 0.8)
        pen.shape(geo.rect(1460, 330, 1560, 420), "#2a2c3c", LW * 0.6, shade=0)
        pen.shape(geo.rect(1430, 460, 1590, 500), "#e8c040", LW * 0.6, shade=0.2)
    card(co, "hall_bg", 0.6, bg)


def vat_room(sh, color_state="green"):
    co = sh.co
    stage.gradient_bg(co, "dark", [(0.0, "#100c18"), (1.0, "#1c1828")], depth=60)

    def back(pen):
        for k in range(6):
            x = -300 + k * 480
            pen.shape(geo.rect(x, -300, x + 60, 1400), "#2c2a3a", LW, depth=20)
            for yy in range(-200, 1400, 120):
                pen.line([(x, yy), (x + 60, yy + 60)], 3, col="#3a3850")
        pen.tube([(-800, 120), (2800, 120)], 50, "#3a3a50", LW)
        pen.tube([(-800, 220), (2800, 260)], 30, "#4a3a4a", LW)
        # crane
        pen.shape(geo.rect(1400, -100, 1440, 520), "#c8a030", LW, depth=10)
        pen.shape(geo.rect(1100, -100, 2200, -60), "#c8a030", LW, depth=10)
        pen.line([(1900, -60), (1900, 260)], 4)
    card(co, "vat_back", 12, back)


def vat(pen, cx=960, top=640, w=760, col_top="#5dff7a", col_bot="#ff8a1e", rusted=0.0):
    """The vat of Verdigloom: a giant steel tub with glowing goo (green on top, orange beneath)."""
    pen.shape(geo.blob([(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2 - 20, top + 360), (cx - w / 2 + 20, top + 360)], n=2, tension=0.1),
              "#5a5e6e", LW * 1.2, depth=30)
    pen.fill(geo.ellipse(cx, top, w / 2, 60, 60), col_bot)
    pen.fill(geo.ellipse(cx, top - 8, w / 2 - 20, 46, 60), col_top)
    for k in range(5):
        pen.line([(cx - w / 2 + 40 + k * (w - 80) / 4, top + 30), (cx - w / 2 + 40 + k * (w - 80) / 4, top + 340)], 3, col="#3e4250")
    pen.line(geo.ellipse(cx, top, w / 2, 60, 60), LW * 1.2, closed=True)


def office(sh):
    co = sh.co

    def bg(pen):
        pen.fill(geo.rect(-1500, -800, 3500, 1800), "#4a2f3a")
        pen.fill(geo.rect(-1500, 820, 3500, 1800), "#2c1c24")
        for k in range(12):
            x = -1400 + k * 400
            pen.line([(x, -800), (x, 820)], 6, col="#5a3a48")
        pen.shape(geo.rect(300, 200, 760, 560), "#d6a640", LW, depth=10)              # gold portrait frame
        pen.shape(geo.rect(330, 230, 730, 530), "#3a3040", LW * 0.6)
        pen.fill(geo.circle(530, 400, 110), "#e2b33c")
        pen.fill(geo.circle(530, 290, 54), "#f2b8a0")
        pen.shape(geo.rect(-400, 700, 800, 880), "#5a3020", LW, depth=12)               # desk
        pen.shape(geo.rrect(1240, 360, 1560, 760, 16), "#5c6270", LW, depth=20)         # the safe
        pen.shape(geo.circle(1400, 540, 70), "#8a909c", LW, hi=0.4)
        pen.shape(geo.circle(1400, 540, 22), "#3a3e48", LW * 0.6)
        for a in range(8):
            pen.line([(1400 + 48 * math.cos(a * math.pi / 4), 540 + 48 * math.sin(a * math.pi / 4)),
                      (1400 + 62 * math.cos(a * math.pi / 4), 540 + 62 * math.sin(a * math.pi / 4))], 3)
    card(co, "office_bg", 0.6, bg)


# ============================================================================ TUMBLE ISLAND / BARNACLE BAY

MOODS = {
    "day": dict(sky=[(0.0, "#bfefff"), (0.6, "#6fd0ff"), (1.0, "#2fa8f0")], sea=["#2fd6d0", "#1fbfc4", "#14a3b4"], tint=None),
    "sunset": dict(sky=[(0.0, "#ffd27a"), (0.35, "#ff9a5a"), (0.7, "#c8507a"), (1.0, "#5a3a8a")],
                   sea=["#ff9a6a", "#c86a7a", "#6a4a8a"], tint=None),
    "fog": dict(sky=[(0.0, "#c8d0d4"), (1.0, "#8f9ca4")], sea=["#7fa6a8", "#6a9294", "#58807e"], tint=None),
    "night": dict(sky=[(0.0, "#3a3a6a"), (0.6, "#1a1a3c"), (1.0, "#0c0c22")], sea=["#1c3a5a", "#16304e", "#102440"], tint=None),
    "purple": dict(sky=[(0.0, "#c25a8a"), (0.5, "#6a2a8a"), (1.0, "#2a1440")], sea=["#6a3a7a", "#4a2a5a", "#301a40"], tint=None),
}


def harbor(sh, mood="day", stilts=False, lighthouse=True, island=True, boats=True, horizon=600):
    co = sh.co
    M = MOODS[mood]
    stage.gradient_bg(co, f"sky_{mood}", M["sky"], depth=90)
    if mood == "day" or mood == "sunset":
        card(co, f"clouds_{mood}", 70, lambda pen: [cloud(pen, x, y, s, "#ffffff" if mood == "day" else "#ffd0a0",
                                                           "#c9e4ff" if mood == "day" else "#e88a7a", seed=i)
                                                     for i, (x, y, s) in enumerate(((200, 180, 1.2), (900, 110, 0.9), (1600, 220, 1.4), (2400, 140, 1.0), (-500, 120, 1.0)))])
    if mood == "sunset":
        card(co, "sun", 75, lambda pen: (pen.fill(geo.circle(1300, 520, 140), "#fff0b0"), pen.fill(geo.circle(1300, 520, 200), "#ffd27a", 0.4)))
    if island:
        def isl(pen):
            pen.shape(geo.blob([(150, horizon + 20), (300, horizon - 60), (1600, horizon - 70), (1800, horizon + 20)], n=4),
                      "#7a6a5a", LW, depth=20)
            tumble_stack(pen, 960, horizon - 40, seed=3, scale=0.85)
            if stilts:
                for x in (420, 640, 860, 1060, 1280, 1500):
                    stilt(pen, x, horizon - 30, horizon + 240, 54)
        card(co, f"tumble_{mood}_{int(stilts)}", 24, isl)
    card(co, f"sea_{mood}", 6, lambda pen: sea_card(pen, horizon, M["sea"], seed=4, sparkle="#ffffff" if mood == "day" else "#ffd8c0"))
    if lighthouse:
        card(co, f"lighthouse", 14, lambda pen: lighthouse_draw(pen, 1700, horizon + 40))
    if boats:
        def bts(pen):
            r = R(9)
            for k in range(7):
                x = -300 + k * 420 + r.uniform(-60, 60)
                boat(pen, x, horizon + 170 + r.uniform(0, 40), r.uniform(0.8, 1.1), seed=k)
        card(co, f"boats", 4, bts)


def lighthouse_draw(pen, x, base, sag=0.0):
    pen.shape(geo.blob([(x - 60, base), (x - 36, base - 420), (x + 36, base - 420), (x + 60, base)], n=2, tension=0.1), "#f4f1e6", LW, depth=16)
    for k in range(3):
        y = base - 70 - k * 120
        pen.shape(np.array([(x - 56 + k * 7, y), (x + 56 - k * 7, y), (x + 52 - k * 7, y - 50), (x - 52 + k * 7, y - 50)]), "#e8392f", LW * 0.7, shade=0.4)
    pen.shape(geo.rect(x - 44, base - 500, x + 44, base - 420), "#3a3a46", LW, depth=6)
    pen.fill(geo.rect(x - 32, base - 490, x + 32, base - 430), "#ffe9a0")
    pen.shape(np.array([(x - 54, base - 500), (x + 54, base - 500), (x, base - 560)]), "#c8432f", LW, depth=8)


def boat(pen, x, y, s=1.0, seed=0, col=None):
    r = R(seed)
    cols = ["#ff7a5c", "#ffd23c", "#59c3e8", "#9be070", "#f4f1e6", "#ff9ec9"]
    col = col or cols[r.integers(len(cols))]
    g = TPen(pen, x, y, s, r.uniform(-0.05, 0.05))
    g.shape(geo.blob([(-110, -30), (110, -30), (90, 20), (-80, 24)], n=3, tension=0.3), col, LW, depth=10)
    g.shape(geo.rect(-60, -30, -40, -14), "#b98a5a", LW * 0.5, shade=0.2)
    g.line([(0, -30), (0, -170)], LW * 0.8)
    g.shape(np.array([(4, -164), (80, -60), (4, -50)]), "#f4f1e6", LW * 0.8, shade=0.3)
    g.shape(np.array([(4, -150), (40, -110), (30, -100), (44, -88), (4, -84)]), "#59c3e8" if col != "#59c3e8" else "#ff7a5c", LW * 0.4, shade=0)


def noodle_boat(pen, x, y, s=1.0, lit=True):
    """Granny's Hot Pot: a floating noodle boat with a red awning and lanterns."""
    g = TPen(pen, x, y, s)
    g.shape(geo.blob([(-300, -60), (300, -60), (260, 30), (-250, 36)], n=3, tension=0.3), "#8a5a3a", LW, depth=16)
    g.shape(geo.rect(-260, -260, 240, -60), "#f3ead6", LW, depth=14)
    g.shape(np.array([(-300, -260), (300, -260), (260, -330), (-270, -330)]), "#d8432f", LW, depth=10)
    for k in range(6):
        g.shape(np.array([(-300 + k * 100, -260), (-250 + k * 100, -230), (-200 + k * 100, -260)]), "#d8432f", LW * 0.7, shade=0.3)
    g.shape(geo.rect(-200, -200, 0, -100), "#ffe9a8" if lit else "#5a4a3a", LW * 0.7, shade=0.2)
    g.shape(geo.rect(-160, -60, -40, -100), "#5a3a2a", LW * 0.6, shade=0.2)
    for xx in (-280, 280):
        g.line([(xx, -260), (xx, -200)], 2)
        g.shape(geo.ellipse(xx, -180, 22, 28, 18), "#ff5a3a", LW * 0.6, hi=0.4)
        if lit:
            g.fill(geo.circle(xx, -180, 50), "#ffb060", 0.25)
    g.shape(geo.rrect(40, -230, 220, -170, 8), "#2a2a2a", LW * 0.6, shade=0)
    g.line([(60, -200), (200, -200)], 3, col="#ffd23c")


# ============================================================================ UNDERWATER: THE GRAVEYARD SHELF

def underwater(sh, murk=0.0):
    co = sh.co
    stage.gradient_bg(co, "uw_sky", [(0.0, "#0b5a78"), (0.6, "#1fa8c4"), (1.0, "#7fe4e8")], depth=80)

    def rays(pen):
        for k in range(9):
            x = -200 + k * 300
            pen.fill(np.array([(x, -400), (x + 90, -400), (x + 260, 1400), (x + 120, 1400)]), "#c8fbff", 0.10)
    card(co, "uw_rays", 50, rays)

    def far(pen):
        pen.fill(geo.blob([(-1200, 700), (-600, 560), (0, 620), (500, 520), (1200, 600), (1800, 540), (2600, 620), (3200, 700), (3200, 1600), (-1200, 1600)], n=6),
                 "#2a7a8c")
        for k, (x, y) in enumerate(((100, 560), (700, 520), (1500, 560), (2200, 540))):          # shipwreck silhouettes
            pen.fill(geo.blob([(x - 220, y + 40), (x + 200, y + 10), (x + 160, y - 50), (x - 120, y - 70)], n=3), "#226a7c")
            pen.fill(geo.rect(x - 10, y - 220, x + 6, y - 50), "#226a7c")
    card(co, "uw_far", 30, far)

    def mid(pen):
        r = R(21)
        pen.fill(geo.blob([(-1000, 820), (-300, 760), (400, 800), (1100, 740), (1900, 800), (2900, 760), (2900, 1600), (-1000, 1600)], n=6), "#5a8a7a")
        for k in range(26):
            x, y = r.uniform(-900, 2800), r.uniform(760, 980)
            scrap_piece(pen, x, y, r.uniform(0.6, 1.3), kind=int(r.integers(0, 8)), seed=k, col_shift="#2a7a8c")
    card(co, "uw_mid", 10, mid)

    def near(pen):
        r = R(5)
        pen.fill(geo.rect(-1500, 980, 3500, 1800), "#c9b48a")
        for k in range(30):
            x = r.uniform(-1200, 3100)
            pen.tube([(x, 1000), (x + r.uniform(-30, 30), 900), (x + r.uniform(-40, 40), 800 - r.uniform(0, 120))], 12, "#3aa86a", 3)
        for k in range(12):
            x = r.uniform(-1000, 2900)
            pen.shape(geo.ellipse(x, 1000, 40, 18, 16), "#ff8a8a", 3, shade=0.4)
    card(co, "uw_near", 1.5, near)


def barrels(pen, x, y, n=7, cracked=True, seed=3, glow="#5dff7a"):
    r = R(seed)
    for k in range(n):
        bx, by = x + (k - n / 2) * 110 + r.uniform(-20, 20), y + r.uniform(-20, 30)
        a = r.uniform(-0.6, 0.6)
        g = TPen(pen, bx, by, 1.0, a)
        g.shape(geo.rrect(-40, -100, 40, 0, 10), "#7a7a3a", LW, depth=10)
        g.shape(geo.rect(-40, -80, 40, -70), "#4a4a2a", LW * 0.6, shade=0)
        g.shape(geo.rect(-40, -30, 40, -20), "#4a4a2a", LW * 0.6, shade=0)
        g.fill(geo.circle(0, -50, 16), "#ffd23c")
        g.line([(-10, -58), (10, -42)], 3)
        if cracked:
            g.fill(np.array([(-20, -100), (0, -80), (14, -100), (6, -112), (-14, -112)]), glow)
            g.line([(-20, -100), (0, -80), (14, -100)], 3)


def scrap_piece(pen, x, y, s=1.0, kind=0, seed=0, col_shift=None, lw=LW):
    """Library of scrap: 0 hubcap, 1 gear, 2 pipe, 3 pot, 4 spring, 5 wheel, 6 manhole, 7 toaster, 8 robot arm, 9 kettle."""
    r = R(seed)
    g = TPen(pen, x, y, s, r.uniform(-0.8, 0.8))
    m = (lambda c: gp.hexs(gp.mix(c, col_shift, 0.35))) if col_shift else (lambda c: c)
    if kind == 0:
        g.shape(geo.circle(0, 0, 36), m("#c8ccd4"), lw, hi=0.5)
        g.shape(geo.circle(0, 0, 14), m("#8a909c"), lw * 0.6)
        for a in range(5):
            g.line([(16 * math.cos(a * 1.256), 16 * math.sin(a * 1.256)), (32 * math.cos(a * 1.256), 32 * math.sin(a * 1.256))], lw * 0.4)
    elif kind == 1:
        g.shape(geo.star(0, 0, 26, 36, 10), m("#b8a070"), lw, depth=5)
        g.shape(geo.circle(0, 0, 10), m("#5a4a3a"), lw * 0.6, shade=0)
    elif kind == 2:
        g.tube([(-60, 0), (60, 0)], 22, m("#8a7a9a"), lw)
        g.shape(geo.rect(-66, -16, -50, 16), m("#6a5a7a"), lw * 0.6, shade=0.2)
    elif kind == 3:
        g.shape(geo.blob([(-40, -30), (40, -30), (34, 20), (-34, 20)], n=3), m("#a8b0bc"), lw, hi=0.4)
        g.line([(40, -20), (66, -26)], lw * 1.4)
    elif kind == 4:
        pts = [(math.cos(t) * 16, -t * 4) for t in np.linspace(0, 6 * math.pi, 40)]
        g.line(pts, lw * 0.9, col=m("#c8ccd4"))
    elif kind == 5:
        g.line(geo.circle(0, 0, 44), lw * 1.4, closed=True)
        for a in range(8):
            g.line([(0, 0), (44 * math.cos(a * 0.785), 44 * math.sin(a * 0.785))], lw * 0.3)
    elif kind == 6:
        g.shape(geo.circle(0, 0, 44), m("#5a5e68"), lw, depth=6)
        for k in range(-2, 3):
            g.line([(-30, k * 12), (30, k * 12)], lw * 0.4)
    elif kind == 7:
        g.shape(geo.rrect(-40, -30, 40, 30, 10), m("#d0d4dc"), lw, hi=0.4)
        g.fill(geo.rect(-26, -30, -10, -24), "#3a3a3a")
        g.fill(geo.rect(8, -30, 24, -24), "#3a3a3a")
    elif kind == 8:
        g.tube([(-60, 10), (0, -10), (50, 20)], 26, m("#c87a3a"), lw)
        g.shape(geo.circle(0, -10, 16), m("#8a5a2a"), lw * 0.7)
        g.shape(geo.blob([(50, 0), (80, -10), (84, 20), (60, 34)], n=3), m("#8a909c"), lw * 0.8)
    else:
        g.shape(geo.blob([(-34, -30), (30, -30), (40, 10), (0, 30), (-40, 10)], n=3), m("#4ab0a0"), lw, hi=0.4)
        g.line([(36, -10), (60, -30)], lw * 1.3)


# ============================================================================ NOODLE BOAT INTERIOR

def noodle_interior(sh, night=False):
    co = sh.co

    def bg(pen):
        pen.fill(geo.rect(-1500, -800, 3500, 1800), "#c8844a" if not night else "#5a3a2a")
        for k in range(16):
            x = -1400 + k * 300
            pen.line([(x, -800), (x + 20, 1800)], 6, col="#a86a3a" if not night else "#4a2e22")
        pen.fill(geo.rect(-1500, -800, 3500, 60), "#8a5a3a")                   # ceiling beams
        for k in range(10):
            pen.shape(geo.rect(-1400 + k * 480, 0, -1340 + k * 480, 70), "#6a4028", LW, depth=8)
        pen.fill(geo.rect(-1500, 860, 3500, 1800), "#7a5034")                  # floor
        pen.shape(geo.rect(200, 560, 1700, 860), "#8a5a3a", LW, depth=14)      # counter
        pen.shape(geo.rect(180, 540, 1720, 580), "#b07a4a", LW, depth=6)
        for k, x in enumerate((420, 760, 1100, 1440)):                        # pots
            pen.shape(geo.blob([(x - 80, 540), (x + 80, 540), (x + 70, 440), (x - 70, 440)], n=2, tension=0.2), "#8a909c", LW, hi=0.4)
            pen.fill(geo.ellipse(x, 440, 70, 14, 20), "#e8c070")
            for j in range(3):
                pen.line(geo.qbez((x - 30 + j * 30, 420), (x - 40 + j * 30, 360), (x - 20 + j * 30, 300), 8), 3, col="#ffffff", alpha=0.6)
        pen.shape(geo.rect(-200, 180, 160, 420), "#ffe9a8" if not night else "#2a3a6a", LW, depth=10)   # window
        pen.line([(-20, 180), (-20, 420)], LW * 0.6)
        for k in range(5):                                                    # hanging lanterns / bowls
            pen.shape(geo.ellipse(400 + k * 300, 120, 26, 32, 18), "#ff5a3a", LW * 0.6, hi=0.4)
    card(co, "noodle_in_n" if night else "noodle_in", 0.6, bg)


# ============================================================================ STILTS UNDER TUMBLE ISLAND

def stilts_view(sh, mood="sunset", scrap_mountain=False, people=False):
    co = sh.co
    M = MOODS[mood]
    stage.gradient_bg(co, f"sky2_{mood}", M["sky"], depth=90)

    def under(pen):
        pen.shape(geo.blob([(-600, -200), (2500, -200), (2400, 120), (1600, 170), (300, 160), (-500, 120)], n=4), "#6a5a4a", LW, depth=40)
        tumble_stack(pen, 960, -120, seed=8, scale=1.0)
        for i, x in enumerate((-200, 260, 720, 1180, 1640, 2100)):
            stilt(pen, x, 130, 1200, 90)
    card(co, f"stilts_under_{mood}", 18, under)
    card(co, f"sea2_{mood}", 4, lambda pen: sea_card(pen, 820, M["sea"], seed=11))
    if scrap_mountain:
        card(co, "scrap_mtn", 1.0, lambda pen: scrap_mountain_draw(pen, 520, 900))


def scrap_mountain_draw(pen, cx, base, w=900, h=420, seed=12):
    r = R(seed)
    pen.shape(geo.blob([(cx - w / 2, base), (cx - w / 4, base - h * 0.6), (cx, base - h), (cx + w / 4, base - h * 0.55), (cx + w / 2, base)], n=4),
              "#7a7068", LW, depth=30)
    for k in range(90):
        u = r.random()
        x = cx + (u - 0.5) * w * 0.9
        top = base - h * (1 - abs(u - 0.5) * 2) ** 0.8
        y = r.uniform(min(top + 20, base - 5), base)
        scrap_piece(pen, x, y, r.uniform(0.6, 1.2), kind=int(r.integers(0, 10)), seed=100 + k)
    g = TPen(pen, cx + 120, base - 140, 1.0, -0.2)                  # the piano
    g.shape(geo.rect(-90, -70, 90, 40), "#1e1a22", LW, hi=0.4)
    g.shape(geo.rect(-80, -10, 80, 10), "#f4f1e6", LW * 0.6, shade=0)
    for k in range(10):
        g.line([(-80 + k * 16, -10), (-80 + k * 16, 10)], 2)


# ============================================================================ CLIFF / RATTLECROWN / DEEP SEA / NEWSPAPER

def cliff(sh):
    co = sh.co
    M = MOODS["sunset"]
    stage.gradient_bg(co, "sky_cliff", M["sky"], depth=90)
    card(co, "sun_cliff", 75, lambda pen: (pen.fill(geo.circle(1400, 560, 160), "#fff0b0"), pen.fill(geo.circle(1400, 560, 240), "#ffd27a", 0.35)))
    card(co, "sea_cliff", 30, lambda pen: sea_card(pen, 640, M["sea"], seed=13))
    card(co, "rock_far", 50, lambda pen: pen.fill(geo.blob([(1680, 660), (1720, 610), (1760, 600), (1800, 640), (1820, 662)], n=3), "#4a2a4a"))

    def cl(pen):
        pen.shape(geo.blob([(-800, 1300), (-600, 820), (200, 780), (900, 800), (1240, 860), (1300, 1300)], n=4), "#7a5a4a", LW, depth=30)
        pen.fill(geo.blob([(-700, 830), (200, 790), (900, 808), (1200, 860), (1200, 880), (-700, 860)], n=4), "#6fae4a")
        ship_skeleton(pen, 380, 790)
    card(co, "cliff_fg", 0.0, cl)


def ship_skeleton(pen, cx, base):
    """The half-built scrap airship: a keel and ribs, two propellers instead of sails."""
    pen.tube(geo.qbez((cx - 300, base - 60), (cx, base + 10), (cx + 320, base - 80), 20), 26, "#8a6a4a", LW)
    for k in range(7):
        x = cx - 240 + k * 80
        pen.tube(geo.qbez((x, base - 40), (x - 30, base - 180), (x + 10, base - 260 + abs(k - 3) * 20), 10), 14, "#9a7a5a", LW * 0.8)
    pen.tube([(cx - 260, base - 230), (cx + 260, base - 250)], 12, "#8a6a4a", LW * 0.8)
    for px in (cx - 120, cx + 140):
        pen.line([(px, base - 250), (px, base - 360)], LW * 1.2)
        for a in (0.3, 0.3 + math.pi):
            pen.shape(geo.ellipse(px + 60 * math.cos(a), base - 360 + 14 * math.sin(a), 64, 12, 20, rot=a), "#c8ccd4", LW * 0.7, hi=0.4)


def rattlecrown(sh):
    co = sh.co
    stage.gradient_bg(co, "sky_rc", [(0.0, "#6a3a5a"), (0.5, "#3a2040"), (1.0, "#160c22")], depth=90)
    card(co, "sea_rc", 30, lambda pen: sea_card(pen, 700, ["#3a2a4a", "#2a1e3a", "#1a1428"], seed=14, sparkle="#c08060"))

    def rock(pen):
        pen.shape(geo.blob([(300, 760), (420, 480), (640, 300), (900, 240), (1180, 320), (1420, 520), (1560, 760)], n=4), "#6a3a2a", LW, depth=40)
        for k in range(14):
            x = 420 + k * 80
            pen.fill(geo.circle(x, 460 + (k % 4) * 60, 18 + (k % 3) * 8), "#b4521e")
        for x in (700, 1020, 1240):
            pen.shape(geo.rect(x - 14, 200 + (x % 7) * 10, x + 14, 420), "#4a2a22", LW, depth=6)
        # the rusted throne
        pen.shape(geo.rect(860, 120, 1060, 360), "#7a3a1e", LW, depth=16)
        for k in range(5):
            pen.shape(np.array([(870 + k * 40, 120), (890 + k * 40, 60 - (k % 2) * 30), (910 + k * 40, 120)]), "#b4521e", LW * 0.7, shade=0.3)
    card(co, "rattle_rock", 14, rock)


def deepsea(sh):
    co = sh.co
    stage.gradient_bg(co, "deep", [(0.0, "#020408"), (1.0, "#06142a")], depth=80)

    def floor(pen):
        pen.fill(geo.blob([(-1200, 880), (0, 820), (1000, 860), (2000, 820), (3200, 880), (3200, 1600), (-1200, 1600)], n=5), "#0c1626")
        r = R(30)
        for k in range(40):
            scrap_piece(pen, r.uniform(-900, 2800), r.uniform(840, 980), r.uniform(0.5, 1.0), kind=int(r.integers(0, 10)), seed=300 + k,
                        col_shift="#0a1222")
    card(co, "deep_floor", 6, floor)


def newspaper(pen, headline, sub, photo="tiny", x=960, y=540, s=1.0, rot=0.0):
    """The Barnacle Bay Bugle front page."""
    g = TPen(pen, x, y, s, rot)
    g.shape(geo.rect(-520, -680, 520, 680), "#f1ead8", LW, shade=0.25)
    g.fill(geo.rect(-500, -660, 500, -540), "#f1ead8")
    g.line([(-500, -530), (500, -530)], 4)
    g.line([(-500, -520), (500, -520)], 2)
    for k in range(14):
        yy = -120 + k * 34
        g.line([(-480, yy), (-40 if photo == "big" and k < 9 else 480, yy)], 4, col="#9a948a")
    if photo == "tiny":
        g.shape(geo.rect(330, 300, 470, 440), "#c8c2b2", 3, shade=0)
        g.fill(geo.circle(400, 360, 26), "#9a948a")
        g.fill(geo.ellipse(400, 430, 50, 30, 16), "#9a948a")
    else:
        g.shape(geo.rect(0, -120, 480, 300), "#c8c2b2", 4, shade=0)
        g.fill(geo.ellipse(240, 40, 80, 100, 30), "#9a948a")
        g.fill(geo.ellipse(240, 270, 150, 90, 30), "#9a948a")
        g.fill(geo.blob([(170, -40), (200, -80), (280, -84), (320, -40), (300, -20), (200, -20)], n=3), "#7a766c")


# ============================================================================ crowds & props

FOLK_COLS = ["#ff7a5c", "#ffd23c", "#59c3e8", "#9be070", "#ff9ec9", "#c79bff", "#ff9c3c", "#f4f1e6", "#4ab0a0"]
SKINS = ["#f4c79d", "#c98a5e", "#e9b48a", "#8a5a3a", "#f2d0b0"]


def folk(pen, x, y, s=1.0, seed=0, arms_up=False, shade=None):
    """One townsperson: a simple shape body + round head (silhouette variety: tall / wide / small)."""
    r = R(seed)
    kind = int(r.integers(0, 3))
    col = FOLK_COLS[r.integers(len(FOLK_COLS))]
    skin = SKINS[r.integers(len(SKINS))]
    hair = ["#2a1a14", "#6a3a1a", "#d8c8a0", "#1a1a2a", "#a83a2a"][r.integers(5)]
    if shade:
        col, skin, hair = (gp.hexs(gp.mix(c, shade[0], shade[1])) for c in (col, skin, hair))
    g = TPen(pen, x, y, s)
    w, h = [(46, 120), (70, 90), (36, 80)][kind]
    for sx in (-1, 1):
        a = (-0.5 if arms_up else 0.35) * sx
        end = (sx * w * 0.9 + sx * 30 * (1 if arms_up else 0.2), -h * 0.9 - (90 if arms_up else -30))
        g.tube([(sx * w * 0.7, -h * 0.8), end], 16, skin if arms_up else col, 4)
    g.shape(geo.blob([(-w, 0), (-w * 0.9, -h * 0.8), (0, -h), (w * 0.9, -h * 0.8), (w, 0)], n=3), col, 4, depth=8)
    g.shape(geo.circle(0, -h - 34, 32), skin, 4, depth=5)
    g.shape(geo.blob([(-34, -h - 34), (-30, -h - 64), (0, -h - 74), (30, -h - 64), (34, -h - 40), (10, -h - 52), (-14, -h - 50)], n=3), hair, 4, depth=3)
    for ex in (-10, 12):
        g.fill(geo.ellipse(ex, -h - 30, 4, 5, 8), INK)
    g.line(geo.qbez((-8, -h - 14), (2, -h - (4 if arms_up else 12)), (12, -h - 14), 6), 3)


def crowd(pen, x0, x1, y, n=12, s=1.0, seed=0, arms_up=False, rows=2, shade=None):
    r = R(seed)
    for row in range(rows):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + 0.5 * (row % 2)) / n + r.uniform(-15, 15)
            folk(pen, x, y + row * 50 * s, s * (1 - 0.1 * (rows - 1 - row)), seed=seed * 100 + row * 40 + k,
                 arms_up=arms_up and r.random() < 0.85, shade=shade)


def crowd_card(sh, name, depth, x0, x1, y, n=12, s=1.0, seed=0, cheer=False, rows=2, shade=None):
    """Crowd as a two-drawing loop (arms down/up) when cheering."""
    if not cheer:
        return card(sh.co, f"crowd_{name}", depth, lambda pen: crowd(pen, x0, x1, y, n, s, seed, False, rows, shade))
    frames = [lambda pen: crowd(pen, x0, x1, y, n, s, seed, False, rows, shade),
              lambda pen: crowd(pen, x0, x1, y - 6 * s, n, s, seed, True, rows, shade)]
    gpd = bpy.data.grease_pencils.get(f"set.crowdc_{name}")
    if gpd is None:
        gpd = gp.new_gp(f"set.crowdc_{name}")
        for k in range(8):
            frames[k % 2](Pen(gpd, "art", 1 + k * 4, origin=(960, 540)))
    ob = bpy.data.objects.new(f"{sh.sid}.crowd_{name}", gpd)
    kk = (stage.CAM_DIST + depth) / stage.CAM_DIST
    ob.location = (0, depth, 0)
    ob.scale = (kk, kk, kk)
    sh.co.objects.link(ob)
    md = ob.grease_pencil_modifiers.new("loop", "GP_TIME")
    md.mode = "NORMAL"
    md.use_keep_loop = True
    md.use_custom_frame_range = True
    md.frame_start, md.frame_end = 1, 32
    return ob


def fruit_boat(pen, x=0, y=0, s=1.0):
    g = TPen(pen, x, y, s)
    g.shape(geo.blob([(-120, -20), (120, -20), (96, 24), (-100, 26)], n=3, tension=0.3), "#ff9c3c", 5, depth=8)
    for k, c in enumerate(("#e8392f", "#ffd23c", "#9be070", "#ff7a5c", "#c79bff")):
        g.shape(geo.circle(-70 + k * 34, -34 + (k % 2) * 6, 18), c, 4, shade=0.5, hi=0.5)
    g.line([(60, -20), (150, -110)], 6, col="#8a6a44")


def net_bag(pen, x, y, s=1.0):
    g = TPen(pen, x, y, s)
    out = geo.blob([(-150, -200), (150, -200), (180, -40), (110, 60), (-110, 60), (-180, -40)], n=4)
    for kind, (px, py) in zip((1, 2, 7, 0, 3, 5), ((-90, -60), (60, -120), (-20, -10), (100, -20), (-110, -150), (20, -150))):
        scrap_piece(g, px, py, 1.1, kind=kind, seed=kind + 40)
    for k in range(12):
        g.line([(-180 + k * 32, -210), (-120 + k * 22, 70)], 3, col="#d8c8a0")
        g.line([(-190, -200 + k * 24), (190, -200 + k * 24)], 3, col="#d8c8a0")
    g.line(out, 5, col="#8a6a44", closed=True)


def raft(pen, x, y, s=1.0, seed=50):
    g = TPen(pen, x, y, s)
    r = R(seed)
    g.shape(geo.blob([(-320, -30), (320, -40), (300, 40), (-300, 44)], n=3, tension=0.3), "#8a909c", 6, depth=14, hi=0.3)
    for k in range(22):
        scrap_piece(g, r.uniform(-280, 280), r.uniform(-50, 20), r.uniform(0.7, 1.2), kind=int(r.integers(0, 10)), seed=seed + k)


def bike(pen, x=0, y=0, s=1.0, col="#e8392f"):
    g = TPen(pen, x, y, s)
    for wx in (-70, 70):
        g.line(geo.circle(wx, -40, 40, 30), 7, closed=True)
        for a in range(6):
            g.line([(wx, -40), (wx + 38 * math.cos(a * 1.05), -40 + 38 * math.sin(a * 1.05))], 2)
    g.line([(-70, -40), (-10, -100), (50, -100), (70, -40)], 9, col=col)
    g.line([(-10, -100), (0, -40), (-70, -40)], 9, col=col)
    g.line([(50, -100), (40, -130), (60, -132)], 6)
    g.shape(geo.rect(-30, -116, 4, -104), "#2a2a2a", 4, shade=0)


def crate(pen, x, y, w=120, col="#c8925a", seed=0):
    g = TPen(pen, x, y, 1.0, R(seed).uniform(-0.05, 0.05))
    g.shape(geo.rect(-w / 2, -w, w / 2, 0), col, 5, depth=w * 0.1)
    g.line([(-w / 2, -w), (w / 2, 0)], 4, col="#8a5a2a")
    g.line([(-w / 2, -w / 2), (w / 2, -w / 2)], 4, col="#8a5a2a")


def hubcap_fist(pen, x=0, y=0, s=1.0):
    """Hubcap Haymaker: a giant fist assembled from hubcaps and pipes."""
    g = TPen(pen, x, y, s)
    g.tube([(-260, 20), (-60, 0)], 70, "#8a7a9a", 6)
    for k in range(3):
        g.shape(geo.rect(-240 + k * 70, -30, -220 + k * 70, 50), "#6a5a7a", 4, shade=0.3)
    g.shape(geo.blob([(-80, -90), (60, -110), (130, -70), (140, 40), (90, 100), (-60, 100), (-90, 20)], n=4), "#b8bec8", 7, depth=20, hi=0.5)
    for k, (px, py) in enumerate(((-30, -70), (30, -80), (90, -60), (110, 10))):
        g.shape(geo.circle(px, py, 34), "#d0d4dc", 5, hi=0.5)
        g.shape(geo.circle(px, py, 12), "#8a909c", 4, shade=0.2)
    g.shape(geo.circle(-20, 40, 46), "#c8ccd4", 5, hi=0.4)


def drone(pen, x=0, y=0, s=1.0, light="#ff3a3a"):
    """Sela's clipboard drone: the clipboard unfolds rotors and a little scanner eye."""
    g = TPen(pen, x, y, s)
    for sx in (-1, 1):
        g.line([(sx * 30, -30), (sx * 70, -60)], 5)
        g.shape(geo.ellipse(sx * 70, -64, 46, 8, 20), "#c8ccd4", 4, shade=0.2)
    g.shape(geo.rrect(-46, -40, 46, 40, 6), "#c89a5a", 5)
    g.shape(geo.rect(-36, -30, 36, 30), "#ffffff", 3, shade=0.2)
    for k in range(3):
        g.line([(-26, -16 + k * 14), (26, -16 + k * 14)], 3, col="#8a8aa0")
    g.shape(geo.circle(0, 46, 12), "#3a3a44", 4)
    g.fill(geo.circle(0, 46, 6), light)


def leviathan(pen, x, y, s=1.0, blue=False, legs_phase=0.0):
    """The Leviathan Rig: a walking factory - six legs, a forest of chimneys, a control dome, two vacuum hoses."""
    g = TPen(pen, x, y, s)
    ink = "#e8f4ff" if blue else INK
    c1, c2, c3 = ("#1c4a8a", "#1c4a8a", "#1c4a8a") if blue else ("#8a7a5a", "#5a5e6e", "#c8a030")
    lw = 4 if blue else 7

    def sh_(pts, col, w=lw, **kw):
        if blue:
            g.line(pts, w, col=ink, closed=True)
        else:
            g.shape(pts, col, w, **kw)
    for k in range(6):
        bx = -420 + k * 168
        ph = math.sin(legs_phase + k * 1.3) * 40
        knee = (bx + (60 if k >= 3 else -60), 120 + ph)
        foot = (bx + (110 if k >= 3 else -110), 420)
        g.line([(bx, 0), knee, foot], 34, col=ink if blue else "#3a3a44")
        if not blue:
            g.line([(bx, 0), knee, foot], 22, col=c2)
        sh_(geo.ellipse(foot[0], foot[1], 46, 16, 20), c2)
    sh_(geo.blob([(-520, 40), (-560, -220), (-420, -360), (420, -360), (560, -220), (520, 40)], n=3, tension=0.2), c1, depth=40)
    for k in range(12):
        cx = -440 + k * 80
        top = -520 - (k % 3) * 70
        sh_(np.array([(cx - 16, -340), (cx + 16, -340), (cx + 18, top + 40), (cx + 40, top), (cx - 40, top), (cx - 18, top + 40)]), c2)
    sh_(geo.ellipse(0, -380, 150, 110, 40, a0=math.pi, a1=math.tau), "#a8e8ff" if not blue else c1)
    g.line(geo.ellipse(0, -380, 150, 110, 40, a0=math.pi, a1=math.tau), lw, col=ink)
    for sx in (-1, 1):
        g.line(geo.qbez((sx * 480, -120), (sx * 780, -300), (sx * 900, -60), 16), 60, col=ink if blue else "#2a2a30")
        if not blue:
            g.line(geo.qbez((sx * 480, -120), (sx * 780, -300), (sx * 900, -60), 16), 44, col="#6a6e7e")
        sh_(geo.ellipse(sx * 910, -40, 60, 40, 20), c3)
    for k in range(5):
        g.fill(geo.circle(-300 + k * 150, -150, 26), "#ffd23c" if not blue else "#5a8ad8")
    if blue:
        for k in range(-12, 13):
            g.line([(k * 100, -800), (k * 100, 600)], 1.5, col="#3a6ab0")
        for k in range(-8, 7):
            g.line([(-1200, k * 100), (1200, k * 100)], 1.5, col="#3a6ab0")


def titan(pen, x=0, y=0, s=1.0, seed=90, arms="umbrella"):
    """JUNKYARD TITAN: a ten-storey giant of a whole town's scrap, glowing teal heart in its chest."""
    g = TPen(pen, x, y, s)
    r = R(seed)
    body = geo.blob([(-260, 0), (-300, -500), (-420, -760), (-260, -900), (0, -940), (260, -900), (420, -760), (300, -500), (260, 0)], n=3, tension=0.3)
    for lx in (-170, 170):
        g.shape(geo.blob([(lx - 110, 0), (lx - 90, -420), (lx + 90, -420), (lx + 110, 0)], n=2, tension=0.2), "#7a7068", 8, depth=30)
    g.shape(body, "#8a8078", 9, depth=60)
    for k in range(70):
        u = r.random()
        px, py = r.uniform(-300, 300), r.uniform(-900, -100)
        scrap_piece(g, px, py, r.uniform(1.0, 2.2), kind=int(r.integers(0, 10)), seed=seed + k)
    for side in (-1, 1):
        if arms == "umbrella":
            pts = [(side * 330, -800), (side * 520, -1080), (side * 300, -1260), (side * 60, -1300)]
        else:
            pts = [(side * 330, -800), (side * 560, -600), (side * 620, -380)]
        g.tube(pts, 150, "#7a7068", 9)
        for q in pts[1:]:
            scrap_piece(g, q[0], q[1], 2.4, kind=0, seed=int(q[0]) % 97)
    g.shape(geo.blob([(-140, -1090), (-120, -1220), (0, -1250), (120, -1220), (140, -1090), (0, -1050)], n=3), "#8a909c", 8, depth=20, hi=0.3)
    for ex in (-50, 50):
        g.fill(geo.circle(ex, -1150, 22), "#2cfff0")
    g.fill(geo.circle(0, -640, 120), "#2cfff0", 0.35)
    g.shape(geo.blob([(0, -560), (-80, -650), (-60, -720), (0, -690), (60, -720), (80, -650)], n=3), "#2cfff0", 7, shade=0.2, hi=0.8)


def transmitter(pen, x=0, y=0, s=1.0, on=False):
    g = TPen(pen, x, y, s)
    g.shape(geo.rrect(-90, -110, 90, 0, 10), "#5a6070", 6, hi=0.3)
    g.line([(40, -110), (70, -330)], 7)
    g.shape(geo.circle(70, -340, 16), "#e8392f" if on else "#7a3a3a", 5, hi=0.5)
    for k in range(3):
        g.shape(geo.circle(-50 + k * 40, -60, 14), "#d6a640", 4, hi=0.4)
    g.shape(geo.rect(-60, -100, 60, -84), "#2cfff0" if on else "#1a3a3a", 3, shade=0)


def rooftops(pen, y=420, seed=5):
    r = R(seed)
    for k in range(9):
        x = -500 + k * 380 + r.uniform(-40, 40)
        w = r.uniform(240, 330)
        h = r.uniform(80, 140)
        pen.shape(np.array([(x - w / 2, y + 200), (x - w / 2, y), (x, y - h), (x + w / 2, y), (x + w / 2, y + 200)]),
                  ["#c8432f", "#3a6e8c", "#7a4a2a", "#2f8a6a"][k % 4], 6, depth=12)


def coastguard(pen, x=0, y=0, s=1.0):
    g = TPen(pen, x, y, s)
    g.shape(geo.blob([(-200, -40), (220, -40), (180, 30), (-180, 34)], n=3, tension=0.3), "#f4f1e6", 6, depth=10)
    g.shape(geo.rect(-200, -10, 220, 6), "#e8392f", 4, shade=0)
    g.shape(geo.rect(-60, -130, 80, -40), "#f4f1e6", 5, depth=8)
    g.fill(geo.rect(-40, -110, 60, -80), "#59c3e8")
    g.line([(20, -130), (20, -200)], 4)
    g.fill(geo.rect(20, -200, 70, -170), "#e8392f")
