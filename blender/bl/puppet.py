"""Cutout puppets.

A Puppet is a character design: a hierarchy of parts, each part one Grease Pencil
drawing with a pivot (joint). The drawings are built ONCE and shared by every shot.
A Rig is one instance of a puppet in one shot: an Empty (root) plus one GP object per
part, parented in a hierarchy, keyed like a cutout puppet in the timeline:

  * part rotations / root position+scale keyed on twos with CONSTANT interpolation
    (stepped, 12 drawings a second like TV anime);
  * face drawings (eyes / brows / mouth) are swapped with Time Offset modifiers in
    FIX mode whose frame is keyed - the standard Grease Pencil lip-sync setup;
  * costume layers are shown/hidden per shot with Opacity modifiers.

Authoring space: character-local px, ground point at (0, 0), y down.
"""
import math
import bpy
import numpy as np
from . import gp, geo

DZ = 0.004       # depth step between parts (BU); front parts sit closer to the camera


class Part:
    def __init__(self, name, parent, pivot, z, draw, swaps=None, layers=None):
        self.name, self.parent, self.pivot, self.z, self.draw = name, parent, np.asarray(pivot, float), z, draw
        self.swaps = swaps or {}       # layer -> {drawing name: draw fn}
        self.layers = layers or {}     # extra costume layers: layer -> draw fn (drawn at frame 1)


class Puppet:
    name = "puppet"
    lw = 6.0

    def __init__(self):
        self.parts = {}
        self.order = []
        self.define()
        self._data = None

    def part(self, name, parent, pivot, z, draw, swaps=None, layers=None):
        p = Part(name, parent, pivot, z, draw, swaps, layers)
        self.parts[name] = p
        self.order.append(name)
        return p

    def define(self):
        raise NotImplementedError

    # ------------------------------------------------------------ build shared drawings
    def data(self):
        if self._data is not None:
            return self._data
        out = {}
        for name in self.order:
            p = self.parts[name]
            dname = f"{self.name}.{name}"
            gpd = bpy.data.grease_pencils.get(dname)
            if gpd is None:
                gpd = gp.new_gp(dname)
                pen = gp.Pen(gpd, "art", 1, origin=p.pivot)
                p.draw(pen)
                for lname, fn in p.layers.items():
                    fn(gp.Pen(gpd, lname, 1, origin=p.pivot, depth=-0.0005))
                swap_index = {}
                for lname, lib in p.swaps.items():
                    idx = {}
                    for k, (dn, fn) in enumerate(lib.items()):
                        fn(gp.Pen(gpd, lname, k + 1, origin=p.pivot, depth=-0.001))
                        idx[dn] = k + 1
                    swap_index[lname] = idx
                gpd["swap_index"] = swap_index
            out[name] = gpd
        self._data = out
        return out


def _ensure_action(ob):
    if ob.animation_data is None:
        ob.animation_data_create()


def _step_all(ob):
    ad = ob.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


class Rig:
    """One puppet instance in one shot."""

    def __init__(self, puppet, coll, tag, depth=0.0, x=960.0, y=900.0, s=1.0, face=1):
        self.p = puppet
        self.tag = tag
        data = puppet.data()
        self.root = bpy.data.objects.new(f"{tag}", None)
        self.root.empty_display_type = "ARROWS"
        self.root.empty_display_size = 0.5
        coll.objects.link(self.root)
        self.obs = {}
        order, seen = [], set()

        def visit(n):
            if n in seen:
                return
            par = puppet.parts[n].parent
            if par:
                visit(par)
            seen.add(n)
            order.append(n)
        for n in puppet.order:
            visit(n)
        for name in order:
            pt = puppet.parts[name]
            ob = bpy.data.objects.new(f"{tag}.{name}", data[name])
            coll.objects.link(ob)
            par = self.obs[pt.parent] if pt.parent else self.root
            ob.parent = par
            ppiv = puppet.parts[pt.parent].pivot if pt.parent else np.zeros(2)
            pz = puppet.parts[pt.parent].z if pt.parent else 0
            rel = pt.pivot - ppiv
            ob.location = (rel[0] * gp.PX, -(pt.z - pz) * DZ, -rel[1] * gp.PX)
            ob.rotation_mode = "XYZ"
            self.obs[name] = ob
            # face drawing swaps
            sw = data[name].get("swap_index")
            if sw:
                for lname in sw.keys():
                    md = ob.grease_pencil_modifiers.new(f"swap_{lname}", "GP_TIME")
                    md.layer = lname
                    md.mode = "FIX"
                    md.offset = 1
            for lname in pt.layers:
                md = ob.grease_pencil_modifiers.new(f"show_{lname}", "GP_OPACITY")
                md.layer = lname
                md.factor = 1.0 if lname in getattr(puppet, "default_on", ()) else 0.0
        self.depth = depth
        self.base = dict(x=x, y=y, s=s, face=face)
        self.set_root(1, x, y, s, face)
        self.sw = {name: dict(data[name].get("swap_index", {})) for name in puppet.order}
        self._keyed = set()

    # ------------------------------------------------------------ keys
    def set_root(self, f, x=None, y=None, s=None, face=None, sq=1.0):
        b = self.base
        x = b["x"] if x is None else x
        y = b["y"] if y is None else y
        s = b["s"] if s is None else s
        face = b["face"] if face is None else face
        self.root.location = gp.px2w(x, y, self.depth)
        self.root.scale = (face * s / math.sqrt(sq), s, s * sq)
        self.root.keyframe_insert("location", frame=f)
        self.root.keyframe_insert("scale", frame=f)

    def rot(self, f, part, deg):
        ob = self.obs[part]
        ob.rotation_euler = (0.0, math.radians(deg), 0.0)
        ob.keyframe_insert("rotation_euler", index=1, frame=f)

    def offset(self, f, part, dx, dy):
        """Move a part off its joint (squash / stretch / slide) - px."""
        pt = self.p.parts[part]
        ppiv = self.p.parts[pt.parent].pivot if pt.parent else np.zeros(2)
        pz = self.p.parts[pt.parent].z if pt.parent else 0
        rel = pt.pivot - ppiv + (dx, dy)
        ob = self.obs[part]
        ob.location = (rel[0] * gp.PX, -(pt.z - pz) * DZ, -rel[1] * gp.PX)
        ob.keyframe_insert("location", frame=f)

    def scale(self, f, part, sx, sy=None):
        ob = self.obs[part]
        ob.scale = (sx, 1.0, sx if sy is None else sy)
        ob.keyframe_insert("scale", frame=f)

    def swap(self, f, part, layer, drawing):
        ob = self.obs[part]
        md = ob.grease_pencil_modifiers[f"swap_{layer}"]
        idx = self.sw[part][layer].get(drawing)
        if idx is None:
            if layer == "hand" or drawing in ("t1", "t2", "t3"):
                raise KeyError(f"{self.p.name}.{part}.{layer} has no drawing '{drawing}' ({list(self.sw[part][layer])})")
            return
        md.offset = idx
        ob.keyframe_insert(f'grease_pencil_modifiers["swap_{layer}"].offset', frame=f)

    def show(self, f, part, layer, on=True):
        ob = self.obs[part]
        md = ob.grease_pencil_modifiers[f"show_{layer}"]
        md.factor = 1.0 if on else 0.0
        ob.keyframe_insert(f'grease_pencil_modifiers["show_{layer}"].factor', frame=f)

    def finish(self):
        """All character keys are stepped (constant interpolation)."""
        for ob in [self.root] + list(self.obs.values()):
            _step_all(ob)

    def tint(self, col, factor, f=None):
        for ob in self.obs.values():
            md = ob.grease_pencil_modifiers.get("light") or ob.grease_pencil_modifiers.new("light", "GP_TINT")
            md.color = gp.to_linear(gp.rgb(col))
            md.factor = factor
            if f is not None:
                ob.keyframe_insert('grease_pencil_modifiers["light"].factor', frame=f)
                ob.keyframe_insert('grease_pencil_modifiers["light"].color', frame=f)

    def fx(self, kind, **kw):
        out = []
        for ob in self.obs.values():
            e = ob.shader_effects.new(kind, kind)
            for k, v in kw.items():
                setattr(e, k, v)
            out.append(e)
        return out

    def hide(self, f, hidden=True):
        for ob in [self.root] + list(self.obs.values()):
            ad = ob.animation_data
            if hidden and not (ad and ad.action and ad.action.fcurves.find("hide_render")):
                ob.hide_render = False
                ob.keyframe_insert("hide_render", frame=f - 1)
                ob.hide_viewport = False
                ob.keyframe_insert("hide_viewport", frame=f - 1)
            ob.hide_render = hidden
            ob.keyframe_insert("hide_render", frame=f)
            ob.hide_viewport = hidden
            ob.keyframe_insert("hide_viewport", frame=f)


# ============================================================================ biped posing

class BipedRig(Rig):
    """Pose a biped by intent: root place, lean, head tilt, hand / foot targets (IK).

    Puppet must provide: limbs = {"arm_f": ("arm_f", "fore_f", wrist_rest_xy, bend), ...}
    with the chain parented to 'chest' (arms) or 'hips' (legs)."""

    def _abs_rot(self, name, rots):
        a, p = 0.0, self.p.parts[name].parent
        while p:
            a += rots.get(p, 0.0)
            p = self.p.parts[p].parent
        return a

    def _world(self, name, rots, offs):
        """Char-local position of a part's pivot under the current rotations."""
        chain = []
        n = name
        while n:
            chain.append(n)
            n = self.p.parts[n].parent
        chain.reverse()
        pos = np.zeros(2)
        ang = 0.0
        prev = np.zeros(2)
        for n in chain:
            piv = self.p.parts[n].pivot + offs.get(n, np.zeros(2))
            pos = pos + geo.rot2(piv - prev, ang)
            prev = self.p.parts[n].pivot
            ang += rots.get(n, 0.0)
        return pos, ang

    def pose(self, f, x=None, y=None, s=None, face=None, sq=1.0, lean=0.0, chest=0.0, head=0.0, bob=0.0,
             hand_f=None, hand_b=None, foot_f=None, foot_b=None, arm_f=None, arm_b=None, leg_f=None, leg_b=None,
             extra=None, **face_swaps):
        P = self.p
        rots = {"hips": math.radians(lean), "chest": math.radians(chest), "head": math.radians(head)}
        offs = {"hips": np.array([0.0, bob])}
        targets = dict(arm_f=hand_f, arm_b=hand_b, leg_f=foot_f, leg_b=foot_b)
        fk = dict(arm_f=arm_f, arm_b=arm_b, leg_f=leg_f, leg_b=leg_b)
        for key, (up, lo, wrist, bend) in P.limbs.items():
            if up not in P.parts:
                continue
            if fk.get(key) is not None:
                rots[up] = math.radians(fk[key][0])
                rots[lo] = math.radians(fk[key][1])
                continue
            tgt = targets.get(key)
            if tgt is None:
                rots[up] = rots[lo] = 0.0
                continue
            root, par_ang = self._world(up, {k: v for k, v in rots.items() if k != up}, offs)
            par_ang -= rots.get(up, 0.0) if up in rots else 0.0
            par_ang = self._abs_rot(up, rots)
            sh, el, wr = P.parts[up].pivot, P.parts[lo].pivot, np.asarray(wrist, float)
            l1, l2 = float(np.hypot(*(el - sh))), float(np.hypot(*(wr - el)))
            a1, a2 = geo.ik2(root, tgt, l1, l2, bend)
            r1 = math.atan2(*(el - sh)[::-1])
            r2 = math.atan2(*(wr - el)[::-1])
            rots[up] = a1 - r1 - par_ang
            rots[lo] = (a1 + a2) - r2 - (par_ang + rots[up])
        if extra:
            rots.update({k: math.radians(v) for k, v in extra.items()})
        self.set_root(f, x, y, s, face, sq)
        for name in P.order:
            if name in rots or name in P.posable:
                self.rot(f, name, math.degrees(rots.get(name, 0.0)))
        self.offset(f, "hips", 0.0, bob)
        for k, v in face_swaps.items():
            part, lay = P.swap_keys[k]
            self.swap(f, part, lay, v)
