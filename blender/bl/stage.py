"""Scenes, cameras, render settings, mesh-based gradients/glows and text.

Every shot is its own Blender scene with its own camera. The home framing: a
50 mm camera 26.667 BU in front of the subject plane (y=0) sees exactly the
19.2 x 10.8 BU of a 1920x1080 frame, so authoring px map 1:1 to the frame.
"""
import math
import bpy
import numpy as np
from . import gp

CAM_DIST = 26.6667
FPS = 24


def setup_render(sc, w=1920, h=1080):
    r = sc.render
    r.engine = "BLENDER_EEVEE_NEXT"
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.fps = FPS
    r.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.display_settings.display_device = "sRGB"
    ee = sc.eevee
    ee.taa_render_samples = 16
    try:
        ee.use_shadows = False
        ee.use_raytracing = False
    except Exception:
        pass
    sc.grease_pencil_settings.antialias_threshold = 1.0


def new_scene(name, f0, f1, world_col="#000000"):
    sc = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    sc.frame_start, sc.frame_end = f0, f1
    setup_render(sc)
    w = bpy.data.worlds.new(f"W_{name}")
    w.color = gp.to_linear(gp.rgb(world_col))
    sc.world = w
    return sc


def collection(sc, name):
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    return c


# ----------------------------------------------------------------------------- camera

class Camera:
    """Camera in px terms: (x, y) = frame centre in home px, zoom = 1 home framing."""

    def __init__(self, sc, name="cam", lens=50.0):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.clip_start, cd.clip_end = 0.1, 500
        self.ob = bpy.data.objects.new(name, cd)
        sc.collection.objects.link(self.ob)
        sc.camera = self.ob
        self.ob.rotation_euler = (math.radians(90), 0, 0)
        self.set(None, 960, 540, 1.0)

    def set(self, f, x=960.0, y=540.0, zoom=1.0, roll=0.0, interp=None):
        wx, _, wz = gp.px2w(x, y)
        self.ob.location = (wx, -CAM_DIST / zoom, wz)
        self.ob.rotation_euler = (math.radians(90), math.radians(roll), 0)
        if f is not None:
            self.ob.keyframe_insert("location", frame=f)
            self.ob.keyframe_insert("rotation_euler", frame=f)
            if interp:
                for fc in self.ob.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        if abs(kp.co[0] - f) < 0.5:
                            kp.interpolation = interp

    def move(self, keys, interp="BEZIER"):
        """keys: [(frame, x, y, zoom[, roll])]."""
        for k in keys:
            self.set(k[0], k[1], k[2], k[3], k[4] if len(k) > 4 else 0.0)
        for fc in self.ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = interp

    def shake(self, f0, f1, amp_px=12.0, freq=0.6, seed=1):
        """Camera shake with an F-curve Noise modifier, limited to [f0, f1]."""
        if self.ob.animation_data is None or self.ob.animation_data.action is None:
            self.set(f0, *self._cur())
        act = self.ob.animation_data.action
        for idx in (0, 2):
            fc = act.fcurves.find("location", index=idx)
            if fc is None:
                self.ob.keyframe_insert("location", index=idx, frame=f0)
                fc = act.fcurves.find("location", index=idx)
            m = fc.modifiers.new("NOISE")
            m.scale = 1.0 / max(freq, 0.01)
            m.strength = amp_px * gp.PX * 2
            m.phase = seed * 7 + idx
            m.use_restricted_range = True
            m.frame_start, m.frame_end = f0, f1
            m.blend_in, m.blend_out = 1, min(6, (f1 - f0) / 2)

    def _cur(self):
        x, y, z = self.ob.location
        return (x / gp.PX + 960, -z / gp.PX + 540, CAM_DIST / -y)


# ----------------------------------------------------------------------------- mesh helpers (gradients, glows)

def _emit_mat(name, col_fn, additive=False, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    col_fn(nt, em)
    if additive:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        add = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(em.outputs[0], add.inputs[0])
        nt.links.new(tr.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], out.inputs[0])
        m.surface_render_method = "BLENDED"
    elif alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        m.surface_render_method = "BLENDED"
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    return m


def _ramp(nt, em, stops, kind="LINEAR", axis="z", radial=False):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = None
    if radial:
        g = nt.nodes.new("ShaderNodeTexGradient")
        g.gradient_type = "SPHERICAL"
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Location"].default_value = (0, 0, 0)
        nt.links.new(tc.outputs["Object"], mp.inputs[0])
        nt.links.new(mp.outputs[0], g.inputs[0])
        fac = g.outputs["Fac"]
    else:
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        fac = sep.outputs[{"x": 0, "y": 1, "z": 2}[axis]]
    cr = nt.nodes.new("ShaderNodeValToRGB")
    els = cr.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    for i, (pos, col, a) in enumerate(stops):
        e = els[0] if i == 0 else els.new(pos)
        e.position = pos
        e.color = (*gp.to_linear(gp.rgb(col)), a)
    nt.links.new(fac, cr.inputs[0])
    nt.links.new(cr.outputs[0], em.inputs[0])
    return cr


def plane(coll, name, x0, y0, x1, y1, depth=0.0):
    """Rectangle in home px at a given depth (BU, +y away from the camera)."""
    me = bpy.data.meshes.new(name)
    a = gp.px2w(x0, y0, depth)
    b = gp.px2w(x1, y1, depth)
    verts = [(a[0], depth, b[2]), (b[0], depth, b[2]), (b[0], depth, a[2]), (a[0], depth, a[2])]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def scaled_px(x, y, depth):
    """Home px position for something at `depth` so it lands at (x, y) on screen in the home framing."""
    k = (CAM_DIST + depth) / CAM_DIST
    return 960 + (x - 960) * k, 540 + (y - 540) * k, k


def gradient_bg(coll, name, stops, depth=40.0, margin=1.6, y0=None, y1=None):
    """Full-frame vertical gradient backdrop at `depth`, oversized for camera moves.
    stops: [(pos 0=bottom..1=top, colour)]."""
    k = (CAM_DIST + depth) / CAM_DIST * margin
    hw, hh = 960 * k, 540 * k
    ob = plane(coll, name, 960 - hw, 540 - hh, 960 + hw, 540 + hh, depth)
    m = _emit_mat(f"M_{name}", lambda nt, em: _ramp(nt, em, [(p, c, 1.0) for p, c in stops], axis="z"))
    ob.data.materials.append(m)
    return ob


def glow_disc(coll, name, x, y, r, col, strength=1.0, depth=-0.05):
    """Additive radial glow (neon sludge light, lamps). Returns object (scale/strength keyable)."""
    me = bpy.data.meshes.new(name)
    n = 32
    verts = [(0, 0, 0)] + [(math.cos(i / n * math.tau), 0, math.sin(i / n * math.tau)) for i in range(n)]
    faces = [(0, i + 1, (i + 1) % n + 1) for i in range(n)]
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = gp.px2w(x, y, depth)
    ob.scale = (r * gp.PX, 1, r * gp.PX)
    coll.objects.link(ob)

    def fn(nt, em):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        ln = nt.nodes.new("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        nt.links.new(tc.outputs["Object"], ln.inputs[0])
        cr = nt.nodes.new("ShaderNodeValToRGB")
        e = cr.color_ramp.elements
        e[0].position, e[0].color = 0.0, (*gp.to_linear(gp.rgb(col)), 1)
        e[1].position, e[1].color = 1.0, (0, 0, 0, 1)
        mid = e.new(0.35)
        mid.color = tuple(v * 0.35 for v in gp.to_linear(gp.rgb(col))) + (1,)
        nt.links.new(ln.outputs["Value"], cr.inputs[0])
        nt.links.new(cr.outputs[0], em.inputs[0])
        em.inputs[1].default_value = strength

    ob.data.materials.append(_emit_mat(f"M_{name}", fn, additive=True))
    return ob


def key_strength(ob, f, value):
    em = next(n for n in ob.active_material.node_tree.nodes if n.type == "EMISSION")
    em.inputs[1].default_value = value
    em.inputs[1].keyframe_insert("default_value", frame=f)


# ----------------------------------------------------------------------------- text

_FONTS = {}


def font(name):
    if name not in _FONTS:
        path = {"bangers": "Bangers-Regular.ttf", "lucky": "LuckiestGuy-Regular.ttf", "anton": "Anton-Regular.ttf",
                "hand": "PatrickHand-Regular.ttf"}[name]
        from pathlib import Path
        _FONTS[name] = bpy.data.fonts.load(str(Path(__file__).resolve().parents[2] / "assets" / "fonts" / path))
    return _FONTS[name]


def flat_mat(name, col, alpha=1.0):
    return _emit_mat(name, lambda nt, em: setattr(em.inputs[0], "default_value", (*gp.to_linear(gp.rgb(col)), 1)), alpha=alpha)


def text3d(coll, name, s, x, y, size_px, col="#ffffff", outline="#1b1424", ow=0.08, fname="bangers", depth=-0.2,
           align="CENTER", spacing=1.0):
    """Comic text (font object) with an ink outline copy behind. Returns (front, back) objects."""
    root = bpy.data.objects.new(name, None)
    root.location = gp.px2w(x, y, depth)
    coll.objects.link(root)
    obs = [root]
    for k, (c, off, dy) in enumerate(((outline, ow * size_px * gp.PX, 0.01), (col, 0.0, 0.0))):
        if c is None:
            continue
        cu = bpy.data.curves.new(f"{name}_{k}", "FONT")
        cu.body = s
        cu.font = font(fname)
        cu.size = size_px * gp.PX
        cu.align_x = align
        cu.offset = off
        cu.space_character = spacing
        ob = bpy.data.objects.new(f"{name}_{k}", cu)
        ob.parent = root
        ob.location = (0, dy, 0)
        ob.rotation_euler = (math.radians(90), 0, 0)
        ob.data.materials.append(flat_mat(f"M_{name}_{k}", c))
        coll.objects.link(ob)
        obs.append(ob)
    return obs


def comp_glare(sc, size=7, threshold=0.75, mix=-0.6, vignette=True):
    """Compositor: fog-glow bloom for the neon sludge + soft vignette."""
    sc.use_nodes = True
    try:
        sc.render.compositor_device = "GPU"
    except Exception:
        pass
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.scene = sc
    comp = nt.nodes.new("CompositorNodeComposite")
    g = nt.nodes.new("CompositorNodeGlare")
    g.glare_type = "FOG_GLOW"
    g.quality = "LOW"
    g.threshold = threshold
    g.mix = mix
    g.size = size
    nt.links.new(rl.outputs["Image"], g.inputs[0])
    last = g.outputs[0]
    if vignette:
        em = nt.nodes.new("CompositorNodeEllipseMask")
        em.width, em.height = 0.95, 0.9
        bl = nt.nodes.new("CompositorNodeBlur")
        bl.size_x = bl.size_y = 260
        bl.filter_type = "FAST_GAUSS"
        nt.links.new(em.outputs[0], bl.inputs[1])
        mx = nt.nodes.new("CompositorNodeMixRGB")
        mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = 0.35
        inv = nt.nodes.new("CompositorNodeMath")
        inv.operation = "ADD"
        inv.inputs[1].default_value = 0.0
        nt.links.new(bl.outputs[0], inv.inputs[0])
        nt.links.new(last, mx.inputs[1])
        nt.links.new(inv.outputs[0], mx.inputs[2])
        last = mx.outputs[0]
    nt.links.new(last, comp.inputs[0])
    return nt
