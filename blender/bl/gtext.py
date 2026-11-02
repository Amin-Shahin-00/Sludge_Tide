"""Text as Grease Pencil drawings (so it layers correctly with every other GP drawing).

Blender lays the glyphs out (font curve -> evaluated mesh); the glyph boundary loops
become GP strokes: a thick ink outline, the fill, and holdout fills for letter holes.
"""
import math
from pathlib import Path
import bpy
import bmesh
import numpy as np
from . import gp
from .gp import Pen

_FONTS = {}
FONT_FILES = {"bangers": "Bangers-Regular.ttf", "lucky": "LuckiestGuy-Regular.ttf", "anton": "Anton-Regular.ttf",
              "hand": "PatrickHand-Regular.ttf"}


def font(name):
    if name not in _FONTS:
        _FONTS[name] = bpy.data.fonts.load(str(Path(__file__).resolve().parents[2] / "assets" / "fonts" / FONT_FILES[name]))
    return _FONTS[name]


def mat_holdout():
    key = ("H",)
    m = gp._MATS.get(key)
    if m is None:
        m = bpy.data.materials.new("HOLDOUT")
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        g.show_stroke = False
        g.show_fill = True
        g.fill_color = (0, 0, 0, 1)
        g.use_fill_holdout = True
        gp._MATS[key] = m
    return m


_LOOPS = {}


def _bez_poly(spline, n=6):
    bp = spline.bezier_points
    pts = []
    m = len(bp)
    for k in range(m):
        a, b = bp[k], bp[(k + 1) % m]
        p0, p1, p2, p3 = (np.array(v[:2]) for v in (a.co, a.handle_right, b.handle_left, b.co))
        for t in np.linspace(0, 1, n, endpoint=False):
            pts.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3)
    return np.array(pts)


def glyph_loops(s, fname, size_px, align="CENTER", spacing=1.0):
    """Outline loops of the laid-out text in px (y down), baseline at y=0, as (points, is_hole).
    Contours are resolved with the font's winding (nonzero): outers unioned, holes subtracted."""
    key = (s, fname, round(size_px, 2), align, spacing)
    if key in _LOOPS:
        return _LOOPS[key]
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import unary_union
    cu = bpy.data.curves.new("_txt", "FONT")
    cu.body = s
    cu.font = font(fname)
    cu.size = size_px * gp.PX
    cu.align_x = align
    cu.space_character = spacing
    ob = bpy.data.objects.new("_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    curve = oe.to_curve(dg)
    polys = []
    for sp in curve.splines:
        if sp.type == "BEZIER" and len(sp.bezier_points) > 1:
            P = _bez_poly(sp)
        elif len(sp.points) > 2:
            P = np.array([p.co[:2] for p in sp.points])
        else:
            continue
        P = np.stack([P[:, 0] / gp.PX, -P[:, 1] / gp.PX], 1)
        x, y = P[:, 0], P[:, 1]
        area = 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
        if abs(area) > 1e-3:
            polys.append((P, area))
    oe.to_curve_clear()
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    out = []
    if polys:
        big = max(polys, key=lambda q: abs(q[1]))
        outer_sign = 1 if big[1] > 0 else -1
        outers = [Polygon(P).buffer(0) for P, a in polys if a * outer_sign > 0]
        holes = [Polygon(P).buffer(0) for P, a in polys if a * outer_sign < 0]
        G = unary_union(outers)
        if holes:
            G = G.difference(unary_union(holes))
        geoms = G.geoms if isinstance(G, MultiPolygon) else [G]
        for g in geoms:
            if g.is_empty or not hasattr(g, "exterior"):
                continue
            out.append((np.asarray(g.exterior.coords)[:-1], False))
            for it in g.interiors:
                out.append((np.asarray(it.coords)[:-1], True))
    _LOOPS[key] = out
    return out

def draw_text(pen, s, x, y, size, col="#ffffff", ink=gp.INK, ow=0.08, fname="bangers", align="CENTER", spacing=1.0,
              shadow=None, alpha=1.0):
    loops = glyph_loops(s, fname, size, align, spacing)
    if shadow:
        for l, hole in loops:
            if not hole:
                pen.fill(l + (x + shadow[0], y + shadow[1]), shadow[2], alpha)
    if ink:
        for l, hole in loops:
            if not hole:
                pen.line(l + (x, y), size * ow * 2, ink, alpha, closed=True)
    for l, hole in loops:
        if not hole:
            pen.fill(l + (x, y), col, alpha)
    for l, hole in loops:
        if hole:
            pen.stroke(l + (x, y), mat_holdout(), 1, cyclic=True)
            if ink:
                pen.line(l + (x, y), max(2.0, size * ow * 0.5), ink, alpha, closed=True)


def gp_text(coll, name, s, x, y, size, col="#ffffff", ink=gp.INK, ow=0.08, fname="bangers", depth=-0.2, align="CENTER",
            spacing=1.0, shadow=None):
    """A GP object holding the text, origin at (x, y) on the plane `depth` (home px; not depth-scaled)."""
    gpd = gp.new_gp(f"txt.{name}")
    pen = Pen(gpd, "art", 1, origin=(0, 0))
    draw_text(pen, s, 0, 0, size, col, ink, ow, fname, align, spacing, shadow)
    ob = bpy.data.objects.new(name, gpd)
    ob.location = gp.px2w(x, y, depth)
    coll.objects.link(ob)
    return ob
