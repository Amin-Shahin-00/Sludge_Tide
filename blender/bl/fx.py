"""Effects animation, drawn frame by frame into Grease Pencil (on twos), the way
an effects animator would: speed lines, focus lines, impact bursts, dust, splashes,
bubbles, rain, rot webs, sludge clouds, smoke, sparks, move-name banners.

fxcard(sh, name, depth, drawers) makes a GP object whose drawing for scene frame f
is drawers[f](pen) - each effect builds that dict from its own timing.
Screen-space effects are parented to the camera.
"""
import math
import bpy
import numpy as np
from . import geo, gp, stage
from .gp import Pen, TPen, INK

LW = 5.0


def R(seed):
    return np.random.default_rng(seed)


def fxcard(sh, name, depth, drawers, screen=False, fx=None):
    gpd = gp.new_gp(f"{sh.sid}.fx.{name}")
    lay = gp.layer(gpd, "art")
    frames = sorted(drawers)
    for f in frames:
        pen = Pen(gpd, "art", f, origin=(960, 540))
        fn = drawers[f]
        if fn is not None:
            fn(pen)
    ob = bpy.data.objects.new(f"{sh.sid}.fx.{name}", gpd)
    sh.co.objects.link(ob)
    if screen:
        d = 2.0 + depth
        k = d / stage.CAM_DIST
        ob.parent = sh.cam.ob
        ob.location = (0, 0, -d)
        ob.rotation_euler = (-math.radians(90), 0, 0)
        ob.scale = (k, k, k)
    else:
        k = (stage.CAM_DIST + depth) / stage.CAM_DIST
        ob.location = (0, depth, 0)
        ob.scale = (k, k, k)
    if fx:
        for kind, kw in fx:
            e = ob.shader_effects.new(kind, kind)
            for a, v in kw.items():
                setattr(e, a, v)
    return ob


def blank_after(drawers, f):
    drawers[f] = None
    return drawers


def glow_fx(col, size=30, thr=0.0):
    return ("FX_GLOW", dict(mode="COLOR", select_color=gp.to_linear(gp.rgb(col)), threshold=0.2,
                            glow_color=gp.to_linear(gp.rgb(col)), size=(size, size), samples=8, opacity=1.0))


# ----------------------------------------------------------------------------- screen effects

def speedlines(sh, t0, t1, cx=960, cy=540, col="#ffffff", inner=380, n=70, seed=1, alpha=0.85, kind="focus", angle=0.0):
    """Anime focus lines (radial) or action lines (parallel, kind='parallel')."""
    d = {}
    f0, f1 = sh.f(t0), sh.f(t1)
    for i, f in enumerate(range(f0, f1, 2)):
        r = R(seed * 1000 + i)

        def draw(pen, r=r):
            if kind == "focus":
                for k in range(n):
                    a = r.uniform(0, math.tau)
                    r0 = inner * r.uniform(0.9, 1.5)
                    r1 = 1500
                    w = r.uniform(4, 14)
                    p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
                    pa = (cx + r1 * math.cos(a - w / 3000), cy + r1 * math.sin(a - w / 3000))
                    pb = (cx + r1 * math.cos(a + w / 3000), cy + r1 * math.sin(a + w / 3000))
                    pen.fill(np.array([p0, pa, pb]), col, alpha)
            else:
                ca, sa = math.cos(angle), math.sin(angle)
                for k in range(n):
                    off = r.uniform(-700, 700)
                    L = r.uniform(300, 900)
                    s0 = r.uniform(-1200, 600)
                    x0, y0 = cx + ca * s0 - sa * off, cy + sa * s0 + ca * off
                    pen.taper([(x0, y0), (x0 + ca * L, y0 + sa * L)], r.uniform(3, 10), col, alpha, 1.0, 0.1)
        d[f] = draw
    d[f1] = None
    return fxcard(sh, f"speed{seed}", 0.0, d, screen=True)


def flash(sh, t, col="#ffffff", frames=2, alpha=1.0, name="flash"):
    f = sh.f(t)
    d = {f: lambda pen: pen.fill(geo.rect(-200, -200, 2120, 1280), col, alpha), f + frames: None}
    return fxcard(sh, f"{name}{f}", 0.0, d, screen=True)


def impact_frame(sh, t, frames=3, col="#ff7a1a", ink="#120c18", seed=3, cx=960, cy=540):
    """Classic impact frame: the shot flips to ink + one accent colour with a radial burst."""
    f = sh.f(t)
    d = {}
    for i in range(frames):
        r = R(seed + i)

        def draw(pen, r=r, i=i):
            pen.fill(geo.rect(-200, -200, 2120, 1280), ink if i % 2 == 0 else col)
            for k in range(36):
                a = r.uniform(0, math.tau)
                w = r.uniform(0.02, 0.07)
                pen.fill(np.array([(cx, cy), (cx + 1600 * math.cos(a - w), cy + 1600 * math.sin(a - w)),
                                   (cx + 1600 * math.cos(a + w), cy + 1600 * math.sin(a + w))]), col if i % 2 == 0 else "#fff6e8")
            pen.fill(geo.star(cx, cy, 120, 300, 12, jitter=0.5, seed=seed + i), "#fff6e8")
        d[f + i] = draw
    d[f + frames] = None
    return fxcard(sh, f"impact{f}", 0.0, d, screen=True)


def fade_card(sh, t0, t1, col="#000000", a0=0.0, a1=1.0, name="fade", clear_after=False, depth=0.0):
    d = {}
    for f in range(sh.f(t0), sh.f(t1) + 1):
        u = (f - sh.f(t0)) / max(1, sh.f(t1) - sh.f(t0))
        a = a0 + (a1 - a0) * u
        d[f] = (lambda aa: (lambda pen: pen.fill(geo.rect(-200, -200, 2120, 1280), col, max(0.0, min(1.0, aa)))))(a)
    if clear_after:
        d[sh.f(t1) + 1] = None
    return fxcard(sh, f"{name}{sh.f(t0)}", depth, d, screen=True)


def rain(sh, t0, t1, col="#cfe8ff", angle=0.25, n=160, seed=4, length=60, alpha=0.6, screen=True, sizzle=False):
    d = {}
    for i, f in enumerate(range(sh.f(t0), sh.f(t1), 2)):
        r = R(seed * 31 + i)

        def draw(pen, r=r):
            for k in range(n):
                x, y = r.uniform(-300, 2200), r.uniform(-200, 1200)
                L = length * r.uniform(0.6, 1.4)
                pen.line([(x, y), (x + math.sin(angle) * L, y + math.cos(angle) * L)], r.uniform(2, 4), col, alpha)
                if sizzle and r.random() < 0.08:
                    pen.fill(geo.star(x, y + 60, 6, 16, 5, seed=k), col, 0.9)
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"rain{seed}", 0.5, d, screen=screen)


# ----------------------------------------------------------------------------- world effects (home px)

def dust(sh, x, y, t0, n=14, col="#c8b8a0", dur=0.9, spread=160, rise=80, seed=5, depth=-0.3, size=1.0):
    d = {}
    r = R(seed)
    parts = [(r.uniform(-1, 1) * spread, -r.uniform(0.2, 1) * rise, r.uniform(18, 40) * size) for _ in range(n)]
    f0, f1 = sh.f(t0), sh.f(t0 + dur)
    for f in range(f0, f1, 2):
        u = (f - f0) / max(1, f1 - f0)

        def draw(pen, u=u):
            for (dx, dy, rr) in parts:
                e = 1 - (1 - u) ** 2
                pen.shape(geo.blob(geo.circle(x + dx * e, y + dy * e, rr * (0.6 + 0.8 * u) * (1 - u * 0.6), 10), n=2),
                          col, 3, shade=0.4, alpha=1 - u ** 1.5)
        d[f] = draw
    d[f1] = None
    return fxcard(sh, f"dust{f0}_{seed}", depth, d)


def splash(sh, x, y, t0, s=1.0, col="#e8fbff", dur=0.8, seed=6, depth=-0.3):
    d = {}
    r = R(seed)
    drops = [(r.uniform(-1, 1) * 220 * s, -r.uniform(200, 420) * s, r.uniform(8, 20) * s) for _ in range(18)]
    f0, f1 = sh.f(t0), sh.f(t0 + dur)
    for f in range(f0, f1, 2):
        u = (f - f0) / max(1, f1 - f0)

        def draw(pen, u=u):
            h = 260 * s * math.sin(min(1, u * 1.6) * math.pi * 0.5) * (1 - u)
            pen.shape(geo.blob([(x - 160 * s, y), (x - 90 * s, y - h * 0.7), (x - 30 * s, y - h), (x + 30 * s, y - h * 0.9),
                                (x + 100 * s, y - h * 0.6), (x + 170 * s, y)], n=3), col, 4, shade=0.3, hi=0.5)
            for dx, dy, rr in drops:
                px = x + dx * u
                py = y + dy * u * 2 + 900 * u * u * s
                pen.shape(geo.circle(px, py, rr * (1 - u * 0.5), 10), col, 3, shade=0.2)
            pen.line(geo.ellipse(x, y + 10, 200 * s * (0.5 + u), 30 * s * (0.5 + u), 30), 4, col, 1 - u, closed=True)
        d[f] = draw
    d[f1] = None
    return fxcard(sh, f"splash{f0}", depth, d)


def bubbles(sh, x0, x1, y0, y1, t0, t1, n=24, col="#dff8ff", seed=7, depth=-0.4, rise=300, size=1.0, glow=None):
    r = R(seed)
    bs = [(r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(5, 16) * size, r.uniform(0.6, 1.4), r.uniform(0, 1)) for _ in range(n)]
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        t = (f - sh.f(t0)) / 24

        def draw(pen, t=t):
            for (bx, by, rr, sp, ph) in bs:
                u = (t * sp * 0.6 + ph) % 1.0
                px = bx + 12 * math.sin(t * 3 + ph * 9)
                py = by - u * rise
                pen.line(geo.circle(px, py, rr, 12), 2.5, col, 1 - u, closed=True)
                pen.fill(geo.circle(px - rr * 0.35, py - rr * 0.35, rr * 0.25, 8), "#ffffff", 0.8 * (1 - u))
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"bub{seed}", depth, d, fx=[glow_fx(glow, 20)] if glow else None)


def rot_web(sh, x, y, t0, t1, radius=200, col="#ff7a1a", dark="#7a2a10", seed=8, depth=-0.2, crumble=None):
    """Rot Touch: orange corrosion races out from a fingertip like a spider web, then (optionally) crumbles."""
    r = R(seed)
    branches = []
    for k in range(12):
        a = k / 12 * math.tau + r.uniform(-0.2, 0.2)
        pts = [(0.0, 0.0)]
        for j in range(1, 7):
            rr = radius * j / 6
            a += r.uniform(-0.35, 0.35)
            pts.append((rr * math.cos(a), rr * math.sin(a)))
        branches.append(np.array(pts))
    d = {}
    f0, f1 = sh.f(t0), sh.f(t1)
    for f in range(f0, f1 + 1, 2):
        u = (f - f0) / max(1, f1 - f0)

        def draw(pen, u=u):
            pen.fill(geo.circle(x, y, radius * 0.25 * u + 6, 20), dark, 0.8)
            for b in branches:
                m = max(2, int(len(b) * u + 0.999))
                seg = b[:m] + (x, y)
                pen.line(seg, 6, col)
                pen.line(seg, 2, "#ffd0a0")
            for k in range(int(10 * u)):
                a = k * 2.4
                rr = radius * 0.8 * ((k * 0.37) % 1) * u
                pen.fill(geo.circle(x + rr * math.cos(a), y + rr * math.sin(a), 8, 8), col)
        d[f] = draw
    if crumble is None:
        d[f1 + 2] = None
    return fxcard(sh, f"rot{f0}_{seed}", depth, d, fx=[glow_fx(col, 25)])


def crumble(sh, x, y, t0, w=300, h=300, col="#c8641e", seed=9, dur=1.2, depth=-0.25, wind=(260, -60)):
    """Something rots to orange dust and blows away."""
    r = R(seed)
    bits = [(r.uniform(-w / 2, w / 2), r.uniform(-h / 2, h / 2), r.uniform(5, 18), r.uniform(0.5, 1.5)) for _ in range(90)]
    d = {}
    f0, f1 = sh.f(t0), sh.f(t0 + dur)
    for f in range(f0, f1, 2):
        u = (f - f0) / max(1, f1 - f0)

        def draw(pen, u=u):
            for bx, by, rr, sp in bits:
                e = u ** 1.3 * sp
                px = x + bx + wind[0] * e + 30 * math.sin(by)
                py = y + by + wind[1] * e + 200 * e * e
                pen.fill(geo.circle(px, py, rr * (1 - u * 0.7), 6), col if (bx + by) % 3 > 1 else "#8a3a14", 1 - u ** 2)
        d[f] = draw
    d[f1] = None
    return fxcard(sh, f"crumble{f0}", depth, d)


def sludge_cloud(sh, x, y, t0, t1, r0=60, r1=520, col="#5dff7a", core="#ff8a1e", seed=10, depth=-0.1, rise=-200, alpha=0.75):
    """Verdigloom spreading through the water like ink: lumpy blobs growing and drifting."""
    r = R(seed)
    lumps = [(r.uniform(-1, 1), r.uniform(-1, 0.4), r.uniform(0.4, 1.0), r.uniform(0, 6)) for _ in range(14)]
    d = {}
    f0, f1 = sh.f(t0), sh.f(t1)
    for f in range(f0, f1 + 1, 2):
        u = (f - f0) / max(1, f1 - f0)
        R_ = r0 + (r1 - r0) * (1 - (1 - u) ** 2)

        def draw(pen, R_=R_, u=u):
            from shapely.geometry import Polygon
            from shapely.ops import unary_union
            polys = []
            for (lx, ly, ls, ph) in lumps:
                cx = x + lx * R_ * 0.8 + 14 * math.sin(u * 8 + ph)
                cy = y + ly * R_ * 0.7 + rise * u
                polys.append(Polygon(geo.circle(cx, cy, R_ * 0.45 * ls, 20)))
            U = unary_union(polys)
            gs = U.geoms if hasattr(U, "geoms") else [U]
            for g in gs:
                pts = np.asarray(g.exterior.coords)[:-1]
                pen.fill(pts, col, alpha)
                pen.line(pts, 4, gp.hexs(gp.mix(col, "#ffffff", 0.5)), alpha, closed=True)
            for (lx, ly, ls, ph) in lumps[:5]:
                pen.fill(geo.circle(x + lx * R_ * 0.4, y + ly * R_ * 0.3 + rise * u, R_ * 0.18 * ls, 14), core, alpha * 0.9)
        d[f] = draw
    return fxcard(sh, f"cloud{f0}", depth, d, fx=[glow_fx(col, 40)])


def smoke(sh, x, y, t0, t1, col="#8a5ab4", every=0.5, seed=11, depth=-0.1, rise=220, size=1.0):
    r = R(seed)
    d = {}
    f0, f1 = sh.f(t0), sh.f(t1)
    puffs = [(t0 + k * every, r.uniform(-20, 20)) for k in range(int((t1 - t0) / every) + 1)]
    for f in range(f0, f1 + 1, 2):
        t = sh.t(f)

        def draw(pen, t=t):
            for j, (pt, dx) in enumerate(puffs):
                u = (t - pt) / 1.8
                if 0 <= u <= 1:
                    rr = (10 + 46 * u ** 0.7) * size
                    px = x + dx * u + 50 * size * u + 18 * size * math.sin(u * 5 + j)
                    py = y - rise * (1 - (1 - u) ** 1.6)
                    pen.shape(geo.blob(geo.circle(px, py, rr, 12) + np.array([[3 * math.sin(k * 1.7 + j), 3 * math.cos(k * 2.3 + j)] for k in range(12)]) * size, n=2),
                              col, 3, shade=0.5, hi=0.3, alpha=(1 - u) ** 1.2)
        d[f] = draw
    d[f1 + 2] = None
    return fxcard(sh, f"smoke{f0}_{seed}", depth, d)


def sparks(sh, x, y, t0, col="#2cfff0", n=16, dur=0.5, seed=12, depth=-0.3, spread=220):
    r = R(seed)
    sp = [(r.uniform(0, math.tau), r.uniform(0.4, 1.0)) for _ in range(n)]
    d = {}
    f0, f1 = sh.f(t0), sh.f(t0 + dur)
    for f in range(f0, f1, 1):
        u = (f - f0) / max(1, f1 - f0)

        def draw(pen, u=u):
            for a, v in sp:
                p0 = (x + math.cos(a) * spread * v * u, y + math.sin(a) * spread * v * u + 120 * u * u)
                p1 = (x + math.cos(a) * spread * v * max(0, u - 0.15), y + math.sin(a) * spread * v * max(0, u - 0.15))
                pen.taper([p1, p0], 6, col, 1 - u, 0.2, 1.0)
        d[f] = draw
    d[f1] = None
    return fxcard(sh, f"spark{f0}_{seed}", depth, d, fx=[glow_fx(col, 20)])


def burst(sh, x, y, t0, col="#ffffff", dur=0.25, r0=40, r1=260, n=12, seed=13, depth=-0.4, screen=False):
    """Hit spark: a jagged star that pops and vanishes."""
    d = {}
    f0 = sh.f(t0)
    k = max(2, int(dur * 24))
    for i in range(k):
        u = i / k
        d[f0 + i] = (lambda uu, ii: (lambda pen: (pen.shape(geo.star(x, y, (r0 + (r1 - r0) * uu) * 0.45, r0 + (r1 - r0) * uu, n, jitter=0.5, seed=seed + ii),
                                                             col, 4, shade=0.0),
                                                   pen.fill(geo.star(x, y, (r0 + (r1 - r0) * uu) * 0.2, (r0 + (r1 - r0) * uu) * 0.55, n, seed=seed + ii + 7), "#fffbe8"))))(u, i)
    d[f0 + k] = None
    return fxcard(sh, f"burst{f0}_{seed}", depth, d, screen=screen)


# ----------------------------------------------------------------------------- text

def banner(sh, text, t0, t1, col="#2cfff0", accent="#ffd23c", y=860, size=150, name="banner", slant=-0.06, ink=INK):
    """Shouted move name: a colour slash wipes in, the name slams on, then it all flies off."""
    f0, f1 = sh.f(t0), sh.f(t1)
    d = {}
    for f in range(f0, f1 + 1, 1):
        u = (f - f0) / max(1, f1 - f0)
        a = min(1.0, (f - f0) / 4)
        out = max(0.0, (f - (f1 - 4)) / 4)

        def draw(pen, a=a, out=out):
            w = 2200 * a
            dx = -2400 * out
            pen.fill(np.array([(-100 + dx, y - size * 0.8), (-100 + w + dx, y - size * 0.8 - 40), (-100 + w + dx, y + size * 0.35 - 40),
                               (-100 + dx, y + size * 0.35)]), ink, 0.9)
            pen.fill(np.array([(-100 + dx, y + size * 0.28), (-100 + w + dx, y + size * 0.28 - 40), (-100 + w + dx, y + size * 0.4 - 40),
                               (-100 + dx, y + size * 0.4)]), accent)
        d[f] = draw
    d[f1 + 1] = None
    card = fxcard(sh, f"{name}{f0}", 0.2, d, screen=True)
    root = _screen_text(sh, f"{name}{f0}", text, 960, y + size * 0.3, size, col, ink, 0.06, "bangers", dist=2.1)
    k = root["k"]
    ob = root["ob"]
    ob.scale = (0, 0, 0)
    ob.keyframe_insert("scale", frame=f0)
    for ff, sc in ((f0 + 2, 1.35), (f0 + 4, 1.0), (f1 - 3, 1.0)):
        ob.scale = (k * sc,) * 3
        ob.keyframe_insert("scale", frame=ff)
    x0 = ob.location.x
    ob.keyframe_insert("location", frame=f1 - 3)
    ob.location.x = x0 - 2400 * gp.PX * k
    ob.keyframe_insert("location", frame=f1 + 1)
    ob.scale = (0, 0, 0)
    ob.keyframe_insert("scale", frame=f1 + 2)
    return card, ob


def _screen_text(sh, name, text, x, y, size, col, ink, ow, fname, dist=2.05):
    from .gtext import gp_text
    ob = gp_text(sh.co, f"{sh.sid}.{name}", text, 0, 0, size, col, ink, ow, fname, depth=0.0)
    k = dist / stage.CAM_DIST
    ob.parent = sh.cam.ob
    ob.location = ((x - 960) * gp.PX * k, -(y - 540) * gp.PX * k, -dist)
    ob.rotation_euler = (-math.radians(90), 0, 0)
    ob.scale = (k, k, k)
    return dict(ob=ob, k=k)


def caption(sh, text, t0, t1, x=960, y=980, size=64, col="#ffffff", fname="bangers", name="cap", ink=INK):
    """Screen caption (location cards, ROUND ONE...) that pops in and out."""
    r = _screen_text(sh, f"{name}{sh.f(t0)}", text, x, y, size, col, ink, 0.07, fname)
    ob, k = r["ob"], r["k"]
    f0, f1 = sh.f(t0), sh.f(t1)
    ob.scale = (0, 0, 0)
    ob.keyframe_insert("scale", frame=f0 - 1)
    for ff, sc in ((f0 + 2, 1.15), (f0 + 4, 1.0), (f1 - 2, 1.0)):
        ob.scale = (k * sc,) * 3
        ob.keyframe_insert("scale", frame=ff)
    ob.scale = (0, 0, 0)
    ob.keyframe_insert("scale", frame=f1)
    return ob


def world_text(sh, text, x, y, size, t0=None, t1=None, col="#ffffff", fname="bangers", depth=-0.5, rot=0.0, ink=INK, ow=0.07):
    """Text in the set (sound effects, signs). (x, y) = where it lands on screen in the home framing."""
    from .gtext import gp_text
    X, Y, k = stage.scaled_px(x, y, depth)
    ob = gp_text(sh.co, f"{sh.sid}.wt{abs(hash((text, x, y, t0))) % 1000000}", text, X, Y, size, col, ink, ow, fname, depth=depth)
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0, rot, 0)
    ob.scale = (k, k, k)
    if t0 is not None:
        f0 = sh.f(t0)
        ob.scale = (0, 0, 0)
        ob.keyframe_insert("scale", frame=f0 - 1)
        for ff, sc in ((f0 + 2, 1.3), (f0 + 4, 1.0)):
            ob.scale = (k * sc,) * 3
            ob.keyframe_insert("scale", frame=ff)
        if t1 is not None:
            ob.keyframe_insert("scale", frame=sh.f(t1) - 1)
            ob.scale = (0, 0, 0)
            ob.keyframe_insert("scale", frame=sh.f(t1))
    return ob

def timer_hud(sh, t0, t1, start=30):
    """Big Shell Time countdown in the corner."""
    d = {}
    f0, f1 = sh.f(t0), sh.f(t1)
    for f in range(f0, f1):
        secs = max(0, start - int((f - f0) / 24))

        def draw(pen, s=secs):
            pen.shape(geo.rrect(1560, 40, 1880, 170, 30), "#1b1424", 6, shade=0, alpha=0.85)
            pen.shape(geo.circle(1630, 105, 44), "#ff8a5c", 5, shade=0.3)
            pen.line([(1630, 105), (1630, 75)], 6)
            pen.line([(1630, 105), (1652, 118)], 6)
        d[f] = draw
    d[f1] = None
    fxcard(sh, "timer", 0.0, d, screen=True)
    # digits as text keyed per second
    for i in range(int((t1 - t0)) + 1):
        ta = t0 + i
        tb = min(t1, ta + 1)
        if ta >= t1:
            break
        caption(sh, f"0:{max(0, start - i):02d}", ta, tb, x=1770, y=135, size=78, col="#ffd23c", name=f"tm{i}_")


def fish_school(sh, t0, t1, x0, y0, x1, y1, n=9, col="#ffb03a", seed=14, depth=1.0, s=1.0):
    r = R(seed)
    offs = [(r.uniform(-120, 120), r.uniform(-80, 80), r.uniform(0.8, 1.2)) for _ in range(n)]
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        u = (f - sh.f(t0)) / max(1, sh.f(t1) - sh.f(t0))

        def draw(pen, u=u):
            dirx = 1 if x1 > x0 else -1
            for k, (dx, dy, sp) in enumerate(offs):
                uu = min(1.0, u * sp)
                x = x0 + (x1 - x0) * uu + dx
                y = y0 + (y1 - y0) * uu + dy + 8 * math.sin(u * 20 + k)
                g = TPen(pen, x, y, s, flip=dirx)
                g.shape(geo.blob([(-30, 0), (0, -16), (26, -4), (30, 0), (26, 4), (0, 16)], n=3), col, 3, shade=0.5)
                g.shape(np.array([(-28, 0), (-48, -14 + 6 * math.sin(u * 40 + k)), (-48, 14 + 6 * math.sin(u * 40 + k))]), col, 3, shade=0.3)
                g.fill(geo.circle(16, -4, 3, 8), INK)
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"fish{seed}", depth, d)


def gulls(sh, t0, t1, n=4, seed=15, depth=20, y=200):
    r = R(seed)
    gs = [(r.uniform(-200, 1600), y + r.uniform(-80, 80), r.uniform(60, 140), r.uniform(0, 6)) for _ in range(n)]
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        t = sh.t(f)

        def draw(pen, t=t):
            for x, yy, v, ph in gs:
                px = x + v * t
                fl = math.sin(t * 9 + ph) * 14
                pen.line([(px - 30, yy - fl), (px - 10, yy), (px, yy + 4), (px + 10, yy), (px + 30, yy - fl)], 5, col="#ffffff")
                pen.line([(px - 30, yy - fl), (px - 10, yy), (px, yy + 4), (px + 10, yy), (px + 30, yy - fl)], 2)
        d[f] = draw
    return fxcard(sh, f"gulls{seed}", depth, d)


def prop(sh, name, draw, keys, depth=0.0, stepped=True, shared=False, fx=None):
    """A drawn prop (boat, bowl, logs...) authored around (0, 0) px and moved with object keys.
    keys: [(t, x, y, rot_deg, scale)] in home px. Stepped = on twos like the characters."""
    gname = f"prop.{name}" if shared else f"{sh.sid}.prop.{name}"
    gpd = bpy.data.grease_pencils.get(gname)
    if gpd is None:
        gpd = gp.new_gp(gname)
        draw(Pen(gpd, "art", 1, origin=(0, 0)))
    ob = bpy.data.objects.new(f"{sh.sid}.{name}", gpd)
    sh.co.objects.link(ob)
    ob.rotation_mode = "XYZ"
    for k in keys:
        t, x, y = k[0], k[1], k[2]
        rot = k[3] if len(k) > 3 else 0.0
        s = k[4] if len(k) > 4 else 1.0
        ob.location = gp.px2w(x, y, depth)
        ob.rotation_euler = (0, math.radians(rot), 0)
        ob.scale = (s, s, s)
        f = sh.f(t)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", frame=f)
        ob.keyframe_insert("scale", frame=f)
    if stepped and ob.animation_data:
        # in-betweens on twos, then hold each drawing for two frames
        act = ob.animation_data.action
        t0, t1 = keys[0][0], keys[-1][0]
        for f in range(sh.f(t0), sh.f(t1) + 1, 2):
            sh.sc.frame_set(f)
            vals = [(fc.data_path, fc.array_index, fc.evaluate(f)) for fc in act.fcurves]
            for dp, ix, v in vals:
                getattr(ob, dp)[ix] = v
                ob.keyframe_insert(dp, index=ix, frame=f)
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    if fx:
        for kind, kw in fx:
            e = ob.shader_effects.new(kind, kind)
            for a, v in kw.items():
                setattr(e, a, v)
    return ob


def vis(ob, t_on=None, t_off=None, sh=None):
    """Show an object only between t_on and t_off (render visibility keys)."""
    ob.hide_render = t_on is not None
    ob.keyframe_insert("hide_render", frame=0)
    if t_on is not None:
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=sh.f(t_on))
    if t_off is not None:
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=sh.f(t_off))
    for fc in ob.animation_data.action.fcurves:
        if fc.data_path == "hide_render":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    return ob


def mite_swarm(sh, name, keys, n=30, w=900, h=160, s=0.9, seed=16, depth=0.0, eye="open", rows=3):
    """A marching / swarming crowd of Rustmites: 8 hopping drawings looped, the whole swarm moved with keys
    [(t, x, y)] (home px, centre-bottom)."""
    from .cast.others import draw_mite
    r = R(seed)
    mites = [(r.uniform(-w / 2, w / 2), r.uniform(-h, 0), r.uniform(0.8, 1.2), r.uniform(0, 1)) for _ in range(n)]
    mites.sort(key=lambda m: m[1])
    gpd = gp.new_gp(f"{sh.sid}.mites.{name}")
    for k in range(8):
        pen = Pen(gpd, "art", 1 + k * 2, origin=(0, 0))
        for (mx, my, ms, ph) in mites:
            u = (k / 8 + ph) % 1.0
            hop = abs(math.sin(u * math.pi)) * 26
            sq = 1.0 + 0.18 * math.cos(u * math.tau)
            draw_mite(pen, mx, my - hop, s * ms, eye if (k + int(ph * 8)) % 7 else "happy", squash=sq, lw=4)
    ob = bpy.data.objects.new(f"{sh.sid}.mites.{name}", gpd)
    sh.co.objects.link(ob)
    md = ob.grease_pencil_modifiers.new("loop", "GP_TIME")
    md.mode = "NORMAL"
    md.use_keep_loop = True
    md.use_custom_frame_range = True
    md.frame_start, md.frame_end = 1, 16
    for k in keys:
        t, x, y = k[:3]
        sc = k[3] if len(k) > 3 else 1.0
        ob.location = gp.px2w(x, y, depth)
        ob.scale = (sc, sc, sc)
        ob.keyframe_insert("location", frame=sh.f(t))
        ob.keyframe_insert("scale", frame=sh.f(t))
    ob.shader_effects.new("glow", "FX_GLOW")
    e = ob.shader_effects["glow"]
    e.mode = "COLOR"
    e.select_color = gp.to_linear(gp.rgb("#ff7a1a"))
    e.glow_color = gp.to_linear(gp.rgb("#ff7a1a"))
    e.size = (18, 18)
    return ob


def fog(sh, name, y0, y1, depth, col="#d8dee2", alpha=0.45, drift=120, seed=17, puffs=10):
    """Soft fog bank (GP fill blobs) drifting sideways across the shot."""
    r = R(seed)

    def draw(pen):
        for k in range(puffs):
            x = r.uniform(-1200, 3000)
            y = r.uniform(y0, y1)
            pen.fill(geo.blob(geo.ellipse(x, y, r.uniform(300, 600), r.uniform(60, 140), 16), n=2), col, alpha)
    gpd = gp.new_gp(f"{sh.sid}.fog.{name}")
    draw(Pen(gpd, "art", 1, origin=(960, 540)))
    ob = bpy.data.objects.new(f"{sh.sid}.fog.{name}", gpd)
    sh.co.objects.link(ob)
    k = (stage.CAM_DIST + depth) / stage.CAM_DIST
    ob.scale = (k, k, k)
    ob.location = (0, depth, 0)
    ob.keyframe_insert("location", frame=sh.f(0))
    ob.location = (drift * gp.PX, depth, 0)
    ob.keyframe_insert("location", frame=sh.f(sh.end))
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    return ob


def tornado(sh, cx, cy, t0, t1, n=60, r0=900, r1=120, seed=18, depth=-0.3, h=900):
    """Scrap hurricane: everything spirals in and up around (cx, cy)."""
    from .sets import scrap_piece
    r = R(seed)
    items = [(r.uniform(0, math.tau), r.uniform(0, 1), int(r.integers(0, 10)), r.uniform(0.8, 2.0)) for _ in range(n)]
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        u = (f - sh.f(t0)) / max(1, sh.f(t1) - sh.f(t0))

        def draw(pen, u=u):
            for k, (a0, hh, kind, sc) in enumerate(items):
                a = a0 + u * (6 + 6 * u) * math.pi
                rad = r0 + (r1 - r0) * min(1, u * 1.2) * (0.7 + 0.3 * hh)
                x = cx + rad * math.cos(a)
                y = cy - hh * h * (0.3 + 0.7 * u) + rad * 0.18 * math.sin(a)
                scrap_piece(pen, x, y, sc * (0.7 + 0.5 * u), kind=kind, seed=k + int(u * 20) % 3, lw=4)
            for k in range(14):
                a = k * 0.45 + u * 20
                pen.taper(geo.ellipse(cx, cy - 200 - k * 50, r0 * (1 - u * 0.6) * (0.4 + k * 0.05), 60, 20, a0=a, a1=a + 2.2), 6, "#2cfff0", 0.6, 1.0, 0.1)
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"tornado{seed}", depth, d, fx=[glow_fx("#2cfff0", 25)])


def radio_waves(sh, x, y, t0, t1, col="#ffd23c", every=0.35, depth=-0.2, rmax=1400, seed=19):
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        t = sh.t(f) - t0

        def draw(pen, t=t):
            k = 0
            while k * every <= t:
                u = (t - k * every) / 2.4
                if 0 <= u <= 1:
                    rr = 30 + rmax * u
                    pen.line(geo.ellipse(x, y, rr, rr * 0.55, 60), 8 * (1 - u) + 2, col, 1 - u, closed=True)
                k += 1
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"radio{seed}", depth, d, fx=[glow_fx(col, 18)])


def goo_column(sh, x, base, t0, t1, top, w=220, col="#ff7a1a", seed=20, depth=0.05):
    """Sludge Throne: a tower of bubbling goo rising under him."""
    r = R(seed)
    d = {}
    for f in range(sh.f(t0), sh.f(t1) + 1, 2):
        u = min(1.0, (f - sh.f(t0)) / max(1, sh.f(t1) - sh.f(t0)))
        tt = sh.t(f)

        def draw(pen, u=u, tt=tt):
            yt = base + (top - base) * (1 - (1 - u) ** 2)
            pts = [(x - w * 1.4, base + 40)]
            for k in range(10):
                yy = base + (yt - base) * k / 9
                pts.append((x - w * (0.6 + 0.15 * math.sin(k * 1.7 + tt * 4)), yy))
            for k in range(10):
                yy = yt + (base - yt) * k / 9
                pts.append((x + w * (0.6 + 0.15 * math.sin(k * 2.3 + tt * 5)), yy))
            pts.append((x + w * 1.4, base + 40))
            P = geo.spline(pts, closed=True, n=3)
            pen.shape(P, col, 6, shade=0.6, hi=0.5)
            for k in range(8):
                by = yt + (base - yt) * ((k * 0.13 + tt * 0.5) % 1)
                pen.line(geo.circle(x + r.uniform(-w * 0.4, w * 0.4), by, 10 + (k % 3) * 6, 12), 3, "#ffd0a0", 0.8, closed=True)
        d[f] = draw
    return fxcard(sh, f"goo{seed}", depth, d, fx=[glow_fx(col, 30)])


def hose_flow(sh, pts, t0, t1, col="#2cfff0", speed=1.2, depth=-0.1, seed=21, w=26):
    """Glowing power blobs sucked along a hose path (list of px points)."""
    P = geo.spline(pts, n=10)
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    L = s[-1]
    d = {}
    for f in range(sh.f(t0), sh.f(t1), 2):
        t = sh.t(f) - t0

        def draw(pen, t=t):
            for k in range(10):
                u = ((t * speed + k / 10) % 1.0) * L
                i = np.searchsorted(s, u)
                i = min(max(i, 1), len(P) - 1)
                q = P[i]
                pen.fill(geo.circle(q[0], q[1], w * (0.6 + 0.4 * math.sin(k)), 12), col, 0.9)
        d[f] = draw
    d[sh.f(t1)] = None
    return fxcard(sh, f"flow{seed}", depth, d, fx=[glow_fx(col, 20)])


def hose(sh, name, pts, depth=0.0, t_on=None):
    """A Leviathan vacuum hose drawn along a path."""
    P = geo.spline(pts, n=10)

    def draw(pen):
        pen.line(P, 70, col="#1b1424")
        pen.line(P, 54, col="#6a6e7e")
        for k in range(0, len(P), 4):
            pen.line([P[k] + (0, -26), P[k] + (0, 26)], 4, col="#3a3e4a")
        e = P[-1]
        pen.shape(geo.ellipse(e[0], e[1], 70, 46, 24), "#c8a030", 6, hi=0.4)
    o = fxcard(sh, f"hose_{name}", depth, {sh.f(t_on if t_on is not None else 0): draw})
    return o


def rot_climb(sh, x, top, base, t0, t1, w=110, depth=0.02, seed=22, beats=None):
    """Round two: orange corrosion climbing a Stilt while teal patches slam on - rot, patch, rot, patch."""
    beats = beats or []
    d = {}
    for f in range(sh.f(t0), sh.f(t1) + 1, 1):
        t = sh.t(f)
        nb = sum(1 for b in beats if b <= t)
        rot_turn = nb % 2 == 0

        def draw(pen, nb=nb, rot_turn=rot_turn, t=t):
            lvl = base - (base - top) * (0.3 + 0.6 * ((nb * 0.17) % 1))
            if rot_turn:
                pen.fill(geo.rect(x - w / 2 - 4, lvl, x + w / 2 + 4, base), "#c8501a", 0.92)
                for k in range(8):
                    yy = lvl + k * 30
                    pen.line([(x - w / 2, yy), (x - w / 4, yy - 20), (x, yy + 10), (x + w / 2, yy - 15)], 5, "#ffb05a")
            else:
                for k in range(int((base - lvl) / 70) + 1):
                    yy = lvl + k * 70
                    pen.shape(geo.rect(x - w / 2 - 14, yy, x + w / 2 + 14, yy + 60), "#8a909c", 5, hi=0.4)
                    pen.fill(geo.rect(x - w / 2 - 14, yy, x + w / 2 + 14, yy + 6), "#2cfff0")
        d[f] = draw
    return fxcard(sh, f"rotclimb{seed}", depth, d, fx=[glow_fx("#ff7a1a", 20), glow_fx("#2cfff0", 20)])
