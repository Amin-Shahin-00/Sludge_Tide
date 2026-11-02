"""Grease Pencil helpers: colour, material library, and a Pen that writes
anime-style drawings (flat fill + hard cel shadow + ink outline) into a GP frame.

Authoring units are px (x right, y down); a drawing's (x, y) lands at
Blender (x * PX, depth, -y * PX) in the object's local space.
"""
import math
import bpy
import numpy as np
from . import geo

PX = 0.01            # 1 px unit = 0.01 BU (the 1920x1080 frame is 19.2 x 10.8 BU at the subject plane)
LWF = 11.5           # GP line_width per px unit of ink width (world-space thickness)
INK = "#1b1424"
LIGHT = (-0.55, -0.83)
SHADE = "#4b3a78"
SHADE_A = 0.42


# ----------------------------------------------------------------------------- colour

def rgb(h):
    if isinstance(h, (tuple, list)):
        return tuple(float(v) for v in h[:3])
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def to_linear(c):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def multiply(base, tint, amt):
    b, t = rgb(base), rgb(tint)
    return tuple(b[i] * (1 - amt + amt * t[i]) for i in range(3))


def lighten(c, amt):
    return mix(c, "#ffffff", amt)


def hexs(c):
    c = rgb(c)
    return "#" + "".join(f"{int(round(max(0, min(1, v)) * 255)):02x}" for v in c)


# ----------------------------------------------------------------------------- materials

_MATS = {}


def mat_fill(col, alpha=1.0):
    key = ("F", hexs(col), round(alpha, 3))
    m = _MATS.get(key)
    if m is None:
        m = bpy.data.materials.new(f"F{hexs(col)[1:]}_{int(alpha * 100)}")
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        g.show_stroke = False
        g.show_fill = True
        g.fill_color = (*to_linear(rgb(col)), alpha)
        _MATS[key] = m
    return m


def mat_line(col=INK, alpha=1.0):
    key = ("L", hexs(col), round(alpha, 3))
    m = _MATS.get(key)
    if m is None:
        m = bpy.data.materials.new(f"L{hexs(col)[1:]}_{int(alpha * 100)}")
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        g.show_stroke = True
        g.show_fill = False
        g.color = (*to_linear(rgb(col)), alpha)
        _MATS[key] = m
    return m


def reset_cache():
    _MATS.clear()


def mat_index(gpd, m):
    for i, mm in enumerate(gpd.materials):
        if mm == m:
            return i
    gpd.materials.append(m)
    return len(gpd.materials) - 1


# ----------------------------------------------------------------------------- data

def new_gp(name):
    gpd = bpy.data.grease_pencils.new(name)
    gpd.stroke_thickness_space = "WORLDSPACE"
    gpd.pixel_factor = 1.0
    gpd.stroke_depth_order = "2D"
    return gpd


def layer(gpd, name):
    lay = gpd.layers.get(name)
    if lay is None:
        lay = gpd.layers.new(name, set_active=False)
        lay.use_lights = False
    return lay


def frame(lay, n=1):
    for f in lay.frames:
        if f.frame_number == n:
            return f
    return lay.frames.new(n)


class Pen:
    """Writes strokes into one GP frame. Coordinates in px (y down), offset by origin."""

    def __init__(self, gpd, layer_name="art", frame_no=1, origin=(0.0, 0.0), depth=0.0, lw_scale=1.0):
        self.gpd = gpd
        self.layer = layer(gpd, layer_name)
        self.frame = frame(self.layer, frame_no)
        self.ox, self.oy = origin
        self.depth = depth
        self.lws = lw_scale

    # -- raw stroke
    def stroke(self, pts, m, width_px, cyclic=False, pressure=None):
        pts = np.asarray(pts, float)
        if len(pts) < 2:
            return None
        s = self.frame.strokes.new()
        s.display_mode = "3DSPACE"
        s.points.add(len(pts))
        co = np.zeros((len(pts), 3), np.float32)
        co[:, 0] = (pts[:, 0] - self.ox) * PX
        co[:, 1] = self.depth
        co[:, 2] = -(pts[:, 1] - self.oy) * PX
        s.points.foreach_set("co", co.ravel())
        pr = np.ones(len(pts), np.float32) if pressure is None else np.asarray(pressure, np.float32)
        s.points.foreach_set("pressure", pr)
        s.points.foreach_set("strength", np.ones(len(pts), np.float32))
        s.line_width = int(max(1, min(1000, round(width_px * LWF))))
        s.use_cyclic = cyclic
        s.material_index = mat_index(self.gpd, m)
        s.start_cap_mode = "ROUND"
        s.end_cap_mode = "ROUND"
        s.points.update()
        return s

    # -- building blocks
    def fill(self, pts, col, alpha=1.0):
        return self.stroke(pts, mat_fill(col, alpha), 1, cyclic=True)

    def line(self, pts, lw=6.0, col=INK, alpha=1.0, closed=False, pressure=None):
        return self.stroke(pts, mat_line(col, alpha), lw * self.lws, cyclic=closed, pressure=pressure)

    def taper(self, pts, lw=6.0, col=INK, alpha=1.0, w0=1.0, w1=0.15):
        pts = np.asarray(pts, float)
        pr = np.linspace(w0, w1, len(pts))
        return self.line(pts, lw, col, alpha, pressure=pr)

    def shape(self, pts, col, lw=6.0, shade=1.0, depth=None, hi=0.0, outline=True, shade_col=SHADE,
              line_col=INK, alpha=1.0, light=LIGHT):
        pts = np.asarray(pts, float)
        self.fill(pts, col, alpha)
        if shade > 0:
            size = 0.5 * (np.ptp(pts[:, 0]) + np.ptp(pts[:, 1]))
            d = depth if depth is not None else max(3.0, size * 0.14)
            sc = multiply(col, shade_col, SHADE_A * shade)
            for cr in geo.crescent(pts, (light[0] * d, light[1] * d)):
                self.fill(cr, sc, alpha)
        if hi > 0:
            size = 0.5 * (np.ptp(pts[:, 0]) + np.ptp(pts[:, 1]))
            dd = max(2.0, size * 0.07)
            for cr in geo.crescent(pts, (-light[0] * dd, -light[1] * dd)):
                self.fill(cr, lighten(col, 0.55 * hi), alpha)
        if outline and lw > 0:
            self.line(pts, lw, line_col, alpha, closed=True)
        return pts

    def tube(self, pts, w, col, lw=6.0, shade=1.0, cap="round"):
        return self.shape(geo.tube(pts, w, cap), col, lw, shade=shade, depth=w * 0.3)

    def circle(self, x, y, r, col, lw=6.0, **kw):
        return self.shape(geo.circle(x, y, r), col, lw, **kw)

    def oval(self, x, y, rx, ry, col, lw=6.0, rot=0.0, **kw):
        return self.shape(geo.ellipse(x, y, rx, ry, max(20, int((rx + ry) * 0.45)), rot=rot), col, lw, **kw)

    def dot(self, x, y, r, col):
        return self.fill(geo.circle(x, y, r, 14), col)


def recalc(gpd):
    """Re-triangulate every fill (strokes made through the API keep a naive fan fill otherwise)."""
    tmp = bpy.data.objects.new("_recalc", gpd)
    sc = bpy.context.scene
    sc.collection.objects.link(tmp)
    vl = bpy.context.view_layer
    prev = vl.objects.active
    vl.objects.active = tmp
    try:
        with bpy.context.temp_override(active_object=tmp, object=tmp, selected_objects=[tmp], selected_editable_objects=[tmp],
                                       gpencil_data=gpd, editable_gpencil_strokes=None):
            bpy.ops.gpencil.recalc_geometry()
    finally:
        vl.objects.active = prev
        bpy.data.objects.remove(tmp)


# ----------------------------------------------------------------------------- objects

def gp_object(name, gpd, coll, loc=(0, 0, 0)):
    ob = bpy.data.objects.new(name, gpd)
    ob.location = loc
    coll.objects.link(ob)
    return ob


def px2w(x, y, depth=0.0):
    """Home-frame screen px (1920x1080, y down) -> world point on the plane y=depth."""
    return ((x - 960) * PX, depth, -(y - 540) * PX)


class TPen:
    """A Pen seen through a transform (offset + uniform scale + rotation), so shared
    part drawings (faces, hands) can be authored in their own local space."""

    def __init__(self, pen, ox=0.0, oy=0.0, s=1.0, a=0.0, flip=1):
        self.pen, self.ox, self.oy, self.s, self.a, self.flip = pen, ox, oy, s, a, flip

    def T(self, pts):
        p = np.asarray(pts, float).copy()
        p[:, 0] *= self.flip
        return geo.xf(p, self.ox, self.oy, self.a, self.s)

    def fill(self, pts, col, alpha=1.0):
        return self.pen.fill(self.T(pts), col, alpha)

    def line(self, pts, lw=6.0, col=INK, alpha=1.0, closed=False, pressure=None):
        return self.pen.line(self.T(pts), lw * self.s, col, alpha, closed, pressure)

    def taper(self, pts, lw=6.0, col=INK, alpha=1.0, w0=1.0, w1=0.15):
        return self.pen.taper(self.T(pts), lw * self.s, col, alpha, w0, w1)

    def shape(self, pts, col, lw=6.0, depth=None, **kw):
        return self.pen.shape(self.T(pts), col, lw * self.s, depth=None if depth is None else depth * self.s, **kw)

    def tube(self, pts, w, col, lw=6.0, shade=1.0, cap="round"):
        return self.pen.tube(self.T(pts), w * self.s, col, lw * self.s, shade, cap)

    def circle(self, x, y, r, col, lw=6.0, **kw):
        return self.shape(geo.circle(x, y, r), col, lw, **kw)

    def oval(self, x, y, rx, ry, col, lw=6.0, rot=0.0, **kw):
        return self.shape(geo.ellipse(x, y, rx, ry, max(20, int((rx + ry) * 0.45)), rot=rot), col, lw, **kw)

    def dot(self, x, y, r, col):
        return self.fill(geo.circle(x, y, r, 14), col)
