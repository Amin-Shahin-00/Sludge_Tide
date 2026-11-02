"""Face and hand drawings shared by the cast: small bold round eyes, brows,
mouths (incl. lip-sync talk shapes), cartoon hands, comedy marks."""
import math
import numpy as np
from shapely.geometry import Polygon
from . import geo
from .gp import INK

MOUTH_IN = "#5a1626"
TONGUE = "#e0576b"


# ----------------------------------------------------------------------------- eyes

def eye(pen, x, y, r, kind="dot", look=(0.3, 0.0), lw=6.0, glow_col="#ff8a1e"):
    lx, ly = look
    if kind in ("dot", "half", "tired"):
        ry = r * 1.35 * (0.45 if kind == "half" else 1.0)
        cx, cy = x + lx * r * 0.35, y + ly * r * 0.35
        pen.fill(geo.ellipse(cx, cy, r, ry, 22), INK)
        pen.fill(geo.circle(cx - r * 0.33, cy - ry * 0.42, r * 0.3, 10), "#ffffff")
        if kind in ("half", "tired"):
            pen.line([(x - r * 1.5, y - ry * 0.5), (x + r * 1.5, y - ry * 0.8)], lw * 0.6)
        return
    if kind == "closed":
        pen.line([(x - r * 1.25, y + 1), (x + r * 1.25, y + 2)], lw * 0.75)
        return
    if kind == "happy":
        pen.line(geo.qbez((x - r * 1.3, y + r * 0.4), (x, y - r * 1.4), (x + r * 1.3, y + r * 0.4), 10), lw * 0.75)
        return
    if kind == "sad":
        pen.line(geo.qbez((x - r * 1.3, y - r * 0.2), (x, y + r * 0.9), (x + r * 1.3, y - r * 0.2), 10), lw * 0.75)
        return
    if kind in ("huge", "shock"):
        R = r * (2.6 if kind == "huge" else 3.1)
        pen.shape(geo.ellipse(x, y - R * 0.2, R, R * 1.25, 30), "#ffffff", lw * 0.8, shade=0.25)
        pr = r * (0.75 if kind == "huge" else 0.42)
        pen.fill(geo.circle(x + lx * R * 0.35, y - R * 0.2 + ly * R * 0.35, pr, 12), INK)
        return
    if kind == "glow":
        pen.fill(geo.ellipse(x, y, r * 2.6, r * 2.0, 20), glow_col, 0.25)
        pen.fill(geo.ellipse(x, y, r * 1.15, r * 0.8, 18), glow_col)
        pen.fill(geo.circle(x, y, r * 0.38, 10), "#fff3c0")
        return
    if kind == "x":
        pen.line([(x - r, y - r), (x + r, y + r)], lw * 0.7)
        pen.line([(x - r, y + r), (x + r, y - r)], lw * 0.7)
        return
    if kind == "spiral":
        th = np.linspace(0, 4 * math.pi, 40)
        pen.line(np.stack([x + th / (4 * math.pi) * r * 1.6 * np.cos(th), y + th / (4 * math.pi) * r * 1.6 * np.sin(th)], 1), lw * 0.45)
        return


def brow(pen, x, y, w=12.0, ang=0.0, lw=6.0, side=1, thick=1.0, col=INK):
    """ang > 0 angry (inner end down), ang < 0 worried."""
    a = -ang * side
    dx, dy = math.cos(a) * w, math.sin(a) * w
    pen.taper([(x - dx * side, y - dy * side), (x, y - 1.5), (x + dx * side, y + dy * side)], lw * 1.1 * thick, col, w0=1.0, w1=0.45)


# ----------------------------------------------------------------------------- mouths

def _clip(poly, region):
    try:
        g = Polygon(poly).buffer(0).intersection(Polygon(region).buffer(0))
    except Exception:
        return []
    gs = g.geoms if hasattr(g, "geoms") else [g]
    return [np.asarray(q.exterior.coords)[:-1] for q in gs if isinstance(q, Polygon) and q.area > 2]


def mouth(pen, x, y, w=14.0, kind="smile", open_=0.0, lw=6.0, teeth=None, tongue=True):
    if kind == "smile":
        pen.line(geo.qbez((x - w, y - w * 0.15), (x, y + w * 0.55), (x + w, y - w * 0.15), 12), lw * 0.7)
        return
    if kind == "smirk":
        pen.line(geo.qbez((x - w * 0.8, y + w * 0.05), (x + w * 0.2, y + w * 0.25), (x + w, y - w * 0.35), 12), lw * 0.7)
        return
    if kind == "frown":
        pen.line(geo.qbez((x - w * 0.9, y + w * 0.25), (x, y - w * 0.35), (x + w * 0.9, y + w * 0.25), 12), lw * 0.7)
        return
    if kind == "flat":
        pen.line([(x - w * 0.6, y), (x + w * 0.6, y + 1)], lw * 0.7)
        return
    if kind == "wobble":
        xs = np.linspace(x - w * 0.8, x + w * 0.8, 14)
        pen.line(np.stack([xs, y + np.sin(np.linspace(0, 4 * math.pi, 14)) * w * 0.12], 1), lw * 0.6)
        return
    if kind == "o":
        pen.shape(geo.ellipse(x, y, w * 0.32, w * 0.42, 18), MOUTH_IN, lw * 0.7, shade=0)
        return
    if kind == "talk":
        h = w * (0.18 + 0.75 * open_)
        top = geo.qbez((x - w * 0.85, y - h * 0.15), (x, y - h * 0.35), (x + w * 0.85, y - h * 0.15), 10)
        bot = geo.qbez((x + w * 0.85, y - h * 0.15), (x, y + h * 1.25), (x - w * 0.85, y - h * 0.15), 12)
    elif kind == "grin":
        h = w * (0.55 + 0.4 * open_)
        top = geo.qbez((x - w * 1.1, y - w * 0.3), (x, y - w * 0.05), (x + w * 1.1, y - w * 0.3), 12)
        bot = geo.qbez((x + w * 1.1, y - w * 0.3), (x, y + h * 1.4), (x - w * 1.1, y - w * 0.3), 14)
    elif kind == "shout":
        h = w * (1.0 + 0.4 * open_)
        top = geo.qbez((x - w, y - h * 0.3), (x, y - h * 0.5), (x + w, y - h * 0.3), 10)
        bot = geo.qbez((x + w, y - h * 0.3), (x + w * 0.2, y + h * 1.3), (x - w, y - h * 0.3), 12)
    elif kind == "jaw":
        h = w * 4.0
        top = geo.qbez((x - w, y - w * 0.2), (x, y - w * 0.4), (x + w, y - w * 0.2), 10)
        bot = geo.spline(np.array([(x + w, y - w * 0.2), (x + w * 0.9, y + h * 0.9), (x, y + h), (x - w * 0.9, y + h * 0.9),
                                   (x - w, y - w * 0.2)]), n=5)
    else:
        return
    pts = np.vstack([top, bot[1:]])
    pen.fill(pts, MOUTH_IN)
    x0, x1 = pts[:, 0].min(), pts[:, 0].max()
    y0, y1 = pts[:, 1].min(), pts[:, 1].max()
    if tongue:
        for q in _clip(geo.ellipse((x0 + x1) / 2, y1 - (y1 - y0) * 0.1, (x1 - x0) * 0.32, (y1 - y0) * 0.33, 20), pts):
            pen.fill(q, TONGUE)
    if teeth:
        th = min((y1 - y0) * 0.32, w * 0.32)
        for q in _clip(geo.rect(x0, y0 - 3, x1, y0 + th), pts):
            pen.fill(q, teeth)
        if teeth != "#ffffff":
            for k in range(1, 7):
                xx = x0 + (x1 - x0) * k / 7
                pen.line([(xx, y0 + 1), (xx, y0 + th)], lw * 0.3, col="#7a5a10")
    pen.line(pts, lw * 0.7, closed=True)


def talk_set(lib, fn):
    """Add the three lip-sync drawings t1/t2/t3 using fn(pen, open_)."""
    for k, o in (("t1", 0.3), ("t2", 0.65), ("t3", 1.0)):
        lib[k] = (lambda oo: (lambda pen: fn(pen, oo)))(o)


# ----------------------------------------------------------------------------- hands

def hand(pen, x, y, ang=math.pi / 2, size=1.0, kind="open", col="#f4c79d", lw=6.0):
    def T(p):
        return geo.xf(np.asarray(p, float) * size, x, y, ang)
    if kind == "fist":
        pen.shape(T(geo.blob([(-10, -13), (8, -15), (17, -6), (17, 7), (6, 14), (-10, 13), (-14, 0)], n=5)), col, lw)
        for a, b in (((4, -9), (12, -8)), ((5, -1), (13, 0)), ((4, 7), (11, 7))):
            pen.line(T([a, b]), lw * 0.5)
    elif kind == "point":
        pen.shape(T(geo.blob([(-10, -12), (6, -12), (14, -6), (14, 8), (2, 13), (-10, 11), (-13, 0)], n=5)), col, lw)
        pen.shape(T([(8, -9), (36, -8), (38, -3), (35, 1), (8, 0)]), col, lw * 0.9, shade=0.5)
    elif kind == "grab":
        pen.shape(T(geo.blob([(-12, -12), (2, -16), (8, -24), (16, -22), (14, -12), (26, -12), (30, -4), (22, 0), (28, 6),
                              (24, 13), (12, 15), (-12, 12)], n=3, tension=0.35)), col, lw)
    elif kind == "flat":
        pen.shape(T(geo.blob([(-10, -10), (24, -9), (30, -2), (24, 6), (-10, 9)], n=5)), col, lw)
    elif kind == "thumb":
        pen.shape(T(geo.blob([(-10, -13), (8, -15), (17, -6), (17, 7), (6, 14), (-10, 13), (-14, 0)], n=5)), col, lw)
        pen.shape(T([(2, -12), (0, -34), (8, -38), (12, -12)]), col, lw * 0.9, shade=0.5)
    else:
        pen.shape(T(geo.blob([(-12, -12), (2, -15), (8, -27), (17, -26), (15, -13), (28, -13), (36, -9), (35, -4), (27, -3),
                              (37, 1), (37, 7), (27, 7), (34, 11), (31, 16), (20, 15), (8, 16), (-12, 12)], n=3, tension=0.3)), col, lw)


HANDS = ("open", "fist", "point", "grab", "flat", "thumb")


# ----------------------------------------------------------------------------- comedy marks

def sweat(pen, x, y, s=1.0, lw=5.0):
    pts = geo.blob([(0, -16), (8, 0), (6, 9), (0, 12), (-6, 9), (-8, 0)], n=4) * s + (x, y)
    pen.shape(pts, "#bfe9ff", lw * 0.6, shade=0.3, hi=0.6)


def vein(pen, x, y, s=1.0, lw=5.0, col="#e23a3a"):
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        p0 = np.array([x, y]) + s * 6 * np.array([math.cos(ang), math.sin(ang)])
        p1 = np.array([x, y]) + s * 16 * np.array([math.cos(ang), math.sin(ang)])
        mid = (p0 + p1) / 2 + s * 4 * np.array([-math.sin(ang), math.cos(ang)])
        pen.line(geo.qbez(p0, mid, p1, 6), lw * 0.9, col=col)


def tears(pen, x, y, s=1.0, lw=5.0, spread=1.0):
    """Fire-hose tears: two fat arcs of water from the eyes."""
    for sd in (1, -1):
        p0 = np.array([x + sd * 6 * s, y])
        pts = np.array([p0 + (sd * u * 150 * s * spread, -50 * s * u + 170 * s * u * u) for u in np.linspace(0, 1, 16)])
        pen.tube(pts, 14 * s, "#9fdcff", lw * 0.6, shade=0.3)


def blush(pen, x, y, s=1.0):
    pen.fill(geo.ellipse(x, y, 12 * s, 5 * s, 16), "#ff6f7d", 0.45)
