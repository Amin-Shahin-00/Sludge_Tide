"""Shared puppet-building helpers (standard limbs, hand libraries, face libraries)."""
import math
import numpy as np
from .. import geo
from ..gp import TPen
from .. import face as F


def hands_lib(wrist, d, skin, lw, size=1.0, extra=None):
    ang = math.atan2(d[1], d[0])
    lib = {}
    for k in F.HANDS:
        lib[k] = (lambda kk: (lambda pen: F.hand(pen, wrist[0], wrist[1], ang, size, kk, skin, lw)))(k)
    lib["hidden"] = lambda pen: None
    for k, fn in (extra or {}).items():
        lib[k] = (lambda f: (lambda pen: f(pen, wrist, ang)))(fn)
    return lib


def add_arm(P, side, sh, el, wr, z_up, z_lo, sleeve_col, skin, lw, w=(20, 19), sleeve=None, size=1.0, extra=None,
            parent="chest"):
    sh, el, wr = (np.asarray(v, float) for v in (sh, el, wr))

    def upper(p):
        if sleeve == "full":
            p.tube([sh, (sh + el) / 2, el], w[0] + 6, sleeve_col, lw)
        else:
            p.tube([sh, (sh + el) / 2, el], w[0], skin, lw)
            if sleeve_col:
                p.tube([sh, sh + (el - sh) * (sleeve or 0.3)], w[0] + 5, sleeve_col, lw)

    def lower(p):
        if sleeve == "full":
            p.tube([el, el + (wr - el) * 0.85], w[1] + 6, sleeve_col, lw)
        else:
            p.tube([el, (el + wr) / 2, wr], w[1], skin, lw)

    P.part(f"arm_{side}", parent, sh, z_up, upper)
    P.part(f"fore_{side}", f"arm_{side}", el, z_lo, lower, swaps=dict(hand=hands_lib(wr, wr - el, skin, lw, size, extra)))


def add_leg(P, side, hp, kn, an, z_up, z_lo, col, lw, w=(22, 20), shoe=None, parent="hips"):
    hp, kn, an = (np.asarray(v, float) for v in (hp, kn, an))
    P.part(f"leg_{side}", parent, hp, z_up, lambda p: p.tube([hp, kn], w[0], col, lw))

    def lower(p):
        p.tube([kn, an + (0, -10)], w[1], col, lw)
        if shoe:
            shoe(TPen(p, an[0], an[1] + 8, 1.0))
    P.part(f"shin_{side}", f"leg_{side}", kn, z_lo, lower)


def eyes_lib(HP, pts, r, lw, extra=()):
    lib = {}
    for k, look in (("dot", (0.3, 0)), ("up", (0.2, -0.8)), ("down", (0.2, 0.8)), ("back", (-0.8, 0)), ("ahead", (0.9, 0))):
        lib[k] = (lambda lk: (lambda pen: [F.eye(HP(pen), ex, ey, r, "dot", lk, lw) for ex, ey in pts]))(look)
    for k in ("half", "closed", "happy", "sad", "huge", "shock", "spiral", "x", "tired") + tuple(extra):
        lib[k] = (lambda kk: (lambda pen: [F.eye(HP(pen), ex, ey, r, kk, (0.3, 0), lw) for ex, ey in pts]))(k)
    return lib


def brows_lib(HP, pts, w, lw, col=F.INK, high=-24):
    lib = {}
    for k, ang in (("neutral", 0.0), ("angry", 0.5), ("worried", -0.4), ("up", -0.15)):
        dy = -8 if k == "up" else 0
        lib[k] = (lambda a, d: (lambda pen: [F.brow(HP(pen), x, y + d, w, a, lw, side=(-1 if i == 0 else 1), col=col)
                                             for i, (x, y) in enumerate(pts)]))(ang, dy)
    lib["high"] = lambda pen: [F.brow(HP(pen), x, y + high, w, -0.4, lw, side=(-1 if i == 0 else 1), col=col) for i, (x, y) in enumerate(pts)]
    lib["none"] = lambda pen: None
    return lib


def mouths_lib(HP, x, y, w, lw, teeth_grin="#ffffff"):
    lib = {}
    for k in ("smile", "smirk", "frown", "flat", "wobble", "o"):
        lib[k] = (lambda kk: (lambda pen: F.mouth(HP(pen), x, y, w, kk, 0.0, lw)))(k)
    lib["grin"] = lambda pen: F.mouth(HP(pen), x, y, w * 1.05, "grin", 0.3, lw, teeth=teeth_grin)
    lib["shout"] = lambda pen: F.mouth(HP(pen), x, y + 2, w * 1.05, "shout", 0.8, lw)
    lib["jaw"] = lambda pen: F.mouth(HP(pen), x, y + 2, w * 1.05, "jaw", 1.0, lw)
    F.talk_set(lib, lambda pen, o: F.mouth(HP(pen), x, y, w, "talk", o, lw))
    return lib


STD_SWAPS = {"eyes": ("head", "eyes"), "brows": ("head", "brows"), "mouth": ("head", "mouth"),
             "hf": ("fore_f", "hand"), "hb": ("fore_b", "hand")}
STD_POSABLE = ("hips", "chest", "head", "arm_f", "fore_f", "arm_b", "fore_b", "leg_f", "shin_f", "leg_b", "shin_b")
