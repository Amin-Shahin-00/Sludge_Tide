"""2D geometry for authoring drawings (numpy point lists in 'px units':
x right, y DOWN, 100 px = 1 Blender unit). Outlines of tubes/limbs come from shapely."""
import math
import numpy as np
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely import affinity

TAU = math.tau


def ellipse(cx, cy, rx, ry, n=40, rot=0.0, a0=0.0, a1=TAU):
    full = abs((a1 - a0) - TAU) < 1e-6
    t = np.linspace(a0, a1, n, endpoint=not full)
    x, y = rx * np.cos(t), ry * np.sin(t)
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        x, y = c * x - s * y, s * x + c * y
    return np.stack([cx + x, cy + y], 1)


def circle(cx, cy, r, n=None):
    return ellipse(cx, cy, r, r, n or max(16, int(r * 0.9)))


def bez(p0, p1, p2, p3, n=20):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def qbez(p0, p1, p2, n=16):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = (np.asarray(p, float) for p in (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2


def spline(ctrl, closed=False, n=8, tension=0.5):
    """Catmull-Rom through control points."""
    P = np.asarray(ctrl, float)
    if len(P) < 3:
        return P
    P = np.vstack([P[-1:], P, P[:2]]) if closed else np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        m1, m2 = (p2 - p0) * tension, (p3 - p1) * tension
        t2, t3 = t * t, t * t * t
        out.append((2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
    if not closed:
        out.append(P[-2][None])
    return np.vstack(out)


def blob(ctrl, n=4, tension=0.5):
    return spline(ctrl, closed=True, n=n, tension=tension)


def rect(x0, y0, x1, y1):
    return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], float)


def rrect(x0, y0, x1, y1, r, n=5):
    r = min(r, abs(x1 - x0) / 2, abs(y1 - y0) / 2)
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for k in range(n + 1):
            aa = a + k / n * math.pi / 2
            pts.append((cx + r * math.cos(aa), cy + r * math.sin(aa)))
    return np.array(pts)


def xf(pts, x=0.0, y=0.0, a=0.0, sx=1.0, sy=None):
    sy = sx if sy is None else sy
    p = np.asarray(pts, float) * (sx, sy)
    if a:
        c, s = math.cos(a), math.sin(a)
        p = p @ np.array([[c, s], [-s, c]])
    return p + (x, y)


def tube(pts, w, cap="round"):
    """Outline polygon of a thick stroke (limbs, hoses, pipes)."""
    ls = LineString(np.asarray(pts, float))
    poly = ls.buffer(w / 2, cap_style=1 if cap == "round" else 2, join_style=1, quad_segs=6)
    return poly_pts(poly)


def poly_pts(poly):
    if isinstance(poly, MultiPolygon):
        poly = max(poly.geoms, key=lambda g: g.area)
    return np.asarray(poly.exterior.coords, float)[:-1]


def crescent(pts, d):
    """Part of the shape NOT covered by the shape shifted by d (cel shadow / highlight)."""
    P = Polygon(np.asarray(pts, float)).buffer(0)
    if P.is_empty:
        return []
    Q = affinity.translate(P, d[0], d[1])
    try:
        R = P.difference(Q)
    except Exception:
        return []
    geoms = R.geoms if hasattr(R, "geoms") else [R]
    out = []
    for g in geoms:
        if isinstance(g, Polygon) and g.area > 4.0:
            out.append(np.asarray(g.exterior.coords, float)[:-1])
    return out


def union_pts(*polys):
    from shapely.ops import unary_union
    U = unary_union([Polygon(np.asarray(p, float)).buffer(0) for p in polys])
    return poly_pts(U)


def star(cx, cy, r0, r1, n=8, rot=0.0, jitter=0.0, seed=0):
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(2 * n):
        a = rot + k * math.pi / n
        r = (r1 if k % 2 == 0 else r0) * (1 + jitter * (rng.random() - 0.5))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts)


def rot2(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def ik2(root, target, l1, l2, bend=1.0):
    """Two-bone IK in 2D (y down). Returns (angle1, angle2_relative) in radians,
    angles measured from +x, clockwise positive (y-down convention)."""
    root, target = np.asarray(root, float), np.asarray(target, float)
    d = target - root
    dist = float(np.hypot(*d))
    dist = min(max(dist, abs(l1 - l2) + 1e-3), (l1 + l2) * 0.999)
    base = math.atan2(d[1], d[0])
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    a = math.acos(max(-1, min(1, cos_a)))
    cos_b = (l1 * l1 + l2 * l2 - dist * dist) / (2 * l1 * l2)
    b = math.acos(max(-1, min(1, cos_b)))
    a1 = base - bend * a
    a2 = bend * (math.pi - b)
    return a1, a2
