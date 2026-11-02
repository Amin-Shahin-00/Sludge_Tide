"""IGGY SLATE (before the fall) and BARON RUST (after).

IGGY ~560 tall, thin, hunched: the long neck pushes the head forward. Tidy grey hair,
side part, tired eyes, grey-blue coveralls, a name tag nobody reads, a mop.

BARON RUST ~770 tall. Silhouette = a bent coat hanger: the neck rises and curls forward
like the hook, the shoulders are one straight sloped bar, and the patchwork hazmat coat
hangs from it to the ground and drags. Cracked gas-mask jaw, rusted skin, glowing
orange eyes, crooked crown of melted barrel rings, long dripping fingers.
"""
import math
import numpy as np
from .. import geo
from ..gp import TPen
from ..puppet import Puppet
from .. import face as F
from .common import add_arm, add_leg, eyes_lib, brows_lib, mouths_lib, STD_SWAPS, STD_POSABLE, hands_lib

IG = dict(skin="#e9c6a6", hair="#9da3ab", hair_dk="#6f757d", suit="#5d7187", suit_dk="#45566a", boot="#2c2a33",
          tag="#f4f1e6", mop="#d9c79a", stick="#8a6a44")
RU = dict(skin="#a9b6a2", rust="#b4521e", rust_lt="#e07a2c", coat1="#c9b43c", coat2="#8b9048", coat3="#c27a32",
          coat4="#8d9696", mask="#3e444c", mask_lt="#5b636d", crown="#5a4a3a", hair="#3c3a40", goo="#ff7a1a")
LW = 6.0


# ============================================================================ IGGY

IHC = np.array([44.0, -520.0])


def IH(pen):
    return TPen(pen, IHC[0], IHC[1], 1.1)


def _boot(g):
    g.shape(geo.blob([(-16, -22), (12, -24), (34, -10), (36, 0), (-18, 0)], n=3), IG["boot"], LW)


def _mop(pen, wrist, ang):
    w = np.asarray(wrist, float)
    top, end = w + (-14, -80), w + (70, 214)
    pen.line([top, end], LW * 2.2, col=IG["stick"])
    pen.line([top, end], LW * 0.4)
    g = TPen(pen, end[0], end[1], 1.0)
    g.shape(geo.rect(-16, -8, 16, 6), "#7a7f88", LW * 0.6, shade=0.3)
    for k in range(9):
        a = -0.7 + k * 0.17
        g.tube([(0, 2), (18 * math.sin(a) + 4, 20), (34 * math.sin(a), 30)], 9, IG["mop"], LW * 0.6, shade=0.5)
    F.hand(pen, w[0], w[1], ang, 1.0, "fist", IG["skin"], LW)


def _phone(pen, wrist, ang):
    w = np.asarray(wrist, float)
    g = TPen(pen, w[0], w[1], 1.0, ang - math.pi / 2)
    g.shape(geo.rrect(-12, 4, 12, 40, 4), "#3a3f4a", LW * 0.7, shade=0.3)
    g.shape(geo.rrect(-9, 8, 9, 22, 2), "#bfe6ff", LW * 0.3, shade=0, hi=0.5)
    F.hand(pen, w[0], w[1], ang, 1.0, "grab", IG["skin"], LW)


class Iggy(Puppet):
    name = "iggy"
    limbs = {"arm_f": ("arm_f", "fore_f", (22, -218), -1), "arm_b": ("arm_b", "fore_b", (-26, -218), -1),
             "leg_f": ("leg_f", "shin_f", (18, -10), 1), "leg_b": ("leg_b", "shin_b", (-18, -10), 1)}
    posable = STD_POSABLE
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        P("hips", None, (0, -255), 7, lambda p: p.shape(geo.blob([(-32, -270), (32, -270), (34, -232), (-34, -232)], n=3), IG["suit"], LW))
        P("chest", "hips", (0, -262), 8, self.d_chest)
        P("head", "chest", (6, -446), 9, self.d_head, swaps=dict(
            eyes=eyes_lib(IH, ((8, -14), (32, -12)), 5.6, LW),
            brows=brows_lib(IH, ((8, -32), (32, -30)), 9, LW * 0.8, col=IG["hair_dk"]),
            mouth=mouths_lib(IH, 30, 30, 11, LW * 0.9)),
          layers=dict(sweat=lambda p: F.sweat(IH(p), 50, -44, 1.0)))
        add_arm(self, "b", (-18, -440), (-22, -330), (-26, -218), 1, 2, IG["suit"], IG["skin"], LW, w=(22, 21), sleeve="full",
                extra=dict(mop=_mop, phone=_phone))
        add_leg(self, "b", (-10, -250), (-14, -128), (-18, -10), 3, 4, IG["suit"], LW, w=(30, 28), shoe=_boot)
        add_leg(self, "f", (10, -250), (14, -128), (18, -10), 5, 6, IG["suit"], LW, w=(30, 28), shoe=_boot)
        add_arm(self, "f", (14, -440), (18, -330), (22, -218), 10, 11, IG["suit"], IG["skin"], LW, w=(22, 21), sleeve="full",
                extra=dict(mop=_mop, phone=_phone))

    def d_chest(self, p):
        o = np.array([0, -255])
        p.shape(geo.blob(np.array([(-30, 0), (-34, -60), (-40, -150), (-34, -196), (34, -196), (36, -140), (30, -60), (32, 0)]) + o, n=4),
                IG["suit"], LW, depth=14)
        p.line(np.array([(0, -190), (2, -2)]) + o, LW * 0.4, col=IG["suit_dk"])
        p.shape(geo.rect(-28, -60, 28, -44) + o, IG["suit_dk"], LW * 0.6, shade=0.3)
        p.shape(geo.rect(8, -150, 32, -136) + o, IG["tag"], LW * 0.4, shade=0.2)
        p.line(np.array([(12, -143), (28, -143)]) + o, LW * 0.35, col="#8a8aa0")

    def d_head(self, p):
        p.tube([(4, -446), (30, -470), (38, -490)], 22, IG["skin"], LW)
        h = IH(p)
        h.shape(geo.blob([(-36, -30), (-30, -56), (0, -66), (30, -58), (40, -30), (42, 0), (44, 22), (30, 46), (6, 54),
                          (-20, 46), (-34, 20)], n=4), IG["skin"], LW, depth=8)
        h.shape(geo.ellipse(-30, 4, 9, 13, 18), IG["skin"], LW * 0.8, depth=3)
        h.shape(geo.blob([(-40, -6), (-44, -40), (-20, -70), (14, -72), (42, -50), (44, -30), (20, -42), (6, -50), (-18, -40),
                          (-30, -20)], n=3, tension=0.4), IG["hair"], LW, depth=8)
        h.line(geo.qbez((6, -50), (0, -62), (-8, -68), 6), LW * 0.4, col=IG["hair_dk"])
        h.line([(42, -6), (52, 14), (42, 16)], LW * 0.5)
        h.line(geo.qbez((-14, 10), (-10, 22), (-14, 32), 6), LW * 0.3, alpha=0.5)


# ============================================================================ BARON RUST

RHC = np.array([86.0, -664.0])


def RH(pen):
    return TPen(pen, RHC[0], RHC[1], 1.15)


def _claw(kind, skin=RU["skin"]):
    def fn(pen, wrist, ang):
        g = TPen(pen, wrist[0], wrist[1], 1.0, ang)
        g.shape(geo.ellipse(0, 0, 17, 15, 20), skin, LW)
        if kind == "point":
            g.tube([(8, -4), (40, -8), (72, -10)], 9, skin, LW * 0.8)
            for k in range(3):
                g.tube([(6, 2 + k * 4), (16, 14 + k * 4), (10, 20 + k * 3)], 8, skin, LW * 0.7)
            tips = [(72, -10)]
        else:
            spread = {"claw": 0.45, "open": 0.5, "flat": 0.12}[kind]
            curl = {"claw": 0.6, "open": 0.1, "flat": 0.0}[kind]
            tips = []
            for k in range(4):
                fa = -spread + k * spread * 2 / 3
                L = 60 - abs(k - 1.5) * 6
                p0 = np.array([10 * math.cos(fa), 10 * math.sin(fa)])
                p1 = p0 + 0.6 * L * np.array([math.cos(fa), math.sin(fa)])
                p2 = p1 + 0.4 * L * np.array([math.cos(fa + curl), math.sin(fa + curl)])
                g.tube([p0, p1, p2], 8, skin, LW * 0.7)
                tips.append(p2)
            g.tube([(-4, -10), (6, -26), (20, -32)], 8, skin, LW * 0.7)
        g.fill(geo.circle(-4, 4, 7), RU["rust"])
        for tp in tips:
            g.tube([tp, np.asarray(tp) + (2, 18)], 6, RU["goo"], 0, shade=0)
            g.fill(geo.circle(tp[0] + 2, tp[1] + 24, 5), RU["goo"])
    return fn


def _coat_lower(p):
    hem = []
    n = 11
    for k in range(n + 1):
        u = k / n
        hem.append((160 + (-200 - 160) * u, 6 + (14 if k % 2 else -4) + 8 * math.sin(u * 9)))
    pts = np.array([(118, -300), (112, -260), (134, -90)] + hem + [(-170, -90), (-112, -260), (-118, -300)])
    poly = geo.spline(pts, closed=True, n=2, tension=0.2)
    p.shape(poly, RU["coat1"], LW, depth=24)
    from shapely.geometry import Polygon
    base = Polygon(poly).buffer(0)
    for patch, col in (([(-230, -220), (-20, -250), (0, 60), (-230, 60)], RU["coat2"]),
                       ([(60, -100), (230, -80), (230, 60), (80, 60)], RU["coat2"]),
                       ([(40, -300), (200, -300), (200, -140), (60, -170)], RU["coat3"])):
        g = base.intersection(Polygon(patch))
        gs = g.geoms if hasattr(g, "geoms") else [g]
        for q in gs:
            if q.area > 50 and hasattr(q, "exterior"):
                qp = np.asarray(q.exterior.coords)[:-1]
                p.shape(qp, col, LW * 0.45, shade=0.5)
                for a, b in zip(qp, np.roll(qp, -1, 0)):
                    L = np.hypot(*(b - a))
                    for u in np.linspace(0.1, 0.9, max(2, int(L / 26))):
                        qq = a + (b - a) * u
                        dd = (b - a) / (L + 1e-9)
                        nn = np.array([-dd[1], dd[0]]) * 6
                        p.line([qq - nn, qq + nn], LW * 0.3, col="#2a2018", alpha=0.8)
    p.line([(6, -300), (8, -30)], LW * 0.5, col="#2a2018", alpha=0.6)


def _coat_upper(p):
    pts = np.array([(150, -515), (116, -410), (118, -290), (-118, -290), (-118, -410), (-150, -515)])
    p.shape(geo.spline(pts, closed=True, n=2, tension=0.15), RU["coat1"], LW, depth=18)
    p.shape(np.array([(-118, -470), (-60, -500), (-70, -360), (-118, -330)]), RU["coat4"], LW * 0.45, shade=0.5)
    p.fill(geo.circle(70, -400, 26), "#2a2018", 0.5)
    p.fill(geo.circle(70, -400, 9), RU["coat1"])
    p.line([(4, -510), (6, -292)], LW * 0.5, col="#2a2018", alpha=0.6)
    # the hanger bar + collar
    p.shape(np.array([(-168, -505), (0, -584), (168, -505), (152, -482), (0, -550), (-152, -482)]), RU["coat4"], LW, depth=10)
    p.shape(geo.blob([(-34, -548), (-40, -600), (0, -592), (40, -600), (34, -548)], n=3), RU["coat1"], LW * 0.9, shade=0.6)


class BaronRust(Puppet):
    name = "rust"
    limbs = {"arm_f": ("arm_f", "fore_f", (160, -215), 1), "arm_b": ("arm_b", "fore_b", (-160, -215), -1)}
    posable = ("hips", "chest", "head", "arm_f", "fore_f", "arm_b", "fore_b")
    default_on = ("crown",)
    swap_keys = dict(STD_SWAPS)

    def define(self):
        P = self.part
        P("hips", None, (0, -300), 5, _coat_lower)
        P("chest", "hips", (0, -300), 6, _coat_upper)
        P("head", "chest", (0, -560), 7, self.d_head, swaps=dict(
            eyes=self.eyes(), brows=brows_lib(RH, ((6, -38), (30, -36)), 11, LW * 1.1, col="#2a2830"),
            mouth=self.mask_mouths()),
          layers=dict(tears=self.d_tears, human=self.d_human, crown=self.d_crown))
        skin = RU["skin"]
        for side, sx, z0 in (("b", -1, 1), ("f", 1, 8)):
            sh, el, wr = np.array([135.0 * sx, -515]), np.array([148.0 * sx, -365]), np.array([160.0 * sx, -215])
            P(f"arm_{side}", "chest", sh, z0, (lambda a, b: lambda p: (p.tube([a, b], 26, skin, LW),
                                                                       p.tube([a, a + (b - a) * 0.95], 46, RU["coat4"], LW)))(sh, el))
            lib = {k: (lambda kk, w: (lambda pen: _claw(kk)(pen, w, math.pi / 2 + 0.08 * sx)))(k, wr) for k in ("claw", "point", "open", "flat")}
            lib["hidden"] = lambda pen: None
            P(f"fore_{side}", f"arm_{side}", el, z0 + 1, (lambda a, b: lambda p: (
                p.tube([a, b], 24, skin, LW),
                p.tube([a, a + (b - a) * 0.45], 44, RU["coat4"], LW),
                p.shape(np.array([a + (b - a) * 0.45 + (-30, -8), a + (b - a) * 0.45 + (30, -8),
                                  a + (b - a) * 0.6 + (34, 4), a + (b - a) * 0.5, a + (b - a) * 0.6 + (-34, 6)]), RU["coat1"], LW * 0.8, shade=0.5)))(el, wr),
              swaps=dict(hand=lib))

    def d_head(self, p):
        p.tube(geo.spline([(0, -560), (-16, -640), (6, -704), (50, -716), (72, -692)], n=5), 24, RU["skin"], LW)
        h = RH(p)
        outline = geo.blob([(-34, -36), (-26, -60), (4, -68), (32, -56), (40, -28), (40, 4), (34, 30), (10, 42), (-18, 36), (-34, 14)], n=4)
        h.shape(outline, RU["skin"], LW, depth=8)
        from shapely.geometry import Polygon
        base = Polygon(outline).buffer(0)
        for (px, py, r) in ((-18, -40, 14), (24, -50, 9), (-26, 2, 11)):
            g = base.intersection(Polygon(geo.circle(px, py, r)))
            if not g.is_empty and hasattr(g, "exterior"):
                h.fill(np.asarray(g.exterior.coords)[:-1], RU["rust"])
        for k, (x0, y0) in enumerate(((-30, -50), (-20, -62), (-6, -66), (8, -66))):
            h.taper(geo.qbez((x0, y0), (x0 - 18, y0 + 10), (x0 - 14 - k * 2, y0 + 50 + k * 4), 8), LW * 1.6, RU["hair"])

    def d_crown(self, p):
        c = TPen(p, *(RHC + np.array([4, -64]) * 1.15), 1.15, -0.24)
        for k in range(3):
            c.shape(geo.ellipse(0, -k * 9, 40 - k * 4, 9, 24), RU["crown"] if k % 2 == 0 else RU["rust"], LW * 0.7, shade=0.4)
        for sx in (-26, -6, 18):
            c.shape(np.array([(sx - 6, -22), (sx, -46 - (sx % 7)), (sx + 6, -22)]), RU["rust"], LW * 0.6, shade=0.3)

    def _mask(self, h, drop):
        m = geo.blob(np.array([(-34, -6), (0, -12), (44, -6), (48, 18), (34, 44), (8, 54), (-20, 48), (-36, 26)]) + (0, drop), n=4)
        h.shape(m, RU["mask"], LW, hi=0.35)
        for k in range(4):
            h.line([(4 + k * 8, 18 + drop), (4 + k * 8, 38 + drop)], LW * 0.45, col="#1a1d22")
        h.shape(geo.ellipse(-30, 30 + drop, 16, 20, 20, rot=0.5), RU["mask_lt"], LW * 0.8)
        h.shape(geo.ellipse(48, 28 + drop, 12, 16, 20, rot=-0.4), RU["mask_lt"], LW * 0.8)
        h.line([(18, -8 + drop), (12, 6 + drop), (20, 14 + drop), (14, 26 + drop)], LW * 0.35, col="#c9d0d8")

    def mask_mouths(self):
        lib = {}
        for k, d in (("closed", 0), ("t1", 3), ("t2", 6), ("t3", 9)):
            lib[k] = (lambda dd: (lambda pen: self._mask(RH(pen), dd)))(d)
        lib["frown"] = lambda pen: F.mouth(RH(pen), 22, 30, 10, "frown", 0, LW * 0.9)
        lib["flat"] = lambda pen: F.mouth(RH(pen), 22, 30, 10, "flat", 0, LW * 0.9)
        lib["h1"] = lambda pen: F.mouth(RH(pen), 22, 30, 10, "talk", 0.4, LW * 0.9)
        lib["none"] = lambda pen: None
        return lib
    def eyes(self):
        lib = {}
        for k, look in (("glow", (0.3, 0)), ("glow_down", (0.2, 0.7))):
            lib[k] = lambda pen: [F.eye(RH(pen), ex, ey, 6.0, "glow", (0.3, 0), LW, glow_col="#ff8a1e") for ex, ey in ((6, -22), (30, -20))]
        lib["none"] = lambda pen: None
        lib["wide"] = lambda pen: [F.eye(RH(pen), ex, ey, 8.0, "glow", (0.3, 0), LW, glow_col="#ffb04a") for ex, ey in ((6, -24), (30, -22))]
        lib["narrow"] = lambda pen: [(F.eye(RH(pen), ex, ey, 6.0, "glow", (0.3, 0), LW), RH(pen).line([(ex - 9, ey - 4), (ex + 9, ey - 6)], LW))
                                     for ex, ey in ((6, -22), (30, -20))]
        for k in ("closed", "tired", "sad", "dot"):
            lib[k] = (lambda kk: (lambda pen: [F.eye(RH(pen), ex, ey, 5.6, kk, (0.3, 0), LW) for ex, ey in ((6, -22), (30, -20))]))(k)
        return lib

    def d_tears(self, p):
        h = RH(p)
        for ex in (6, 30):
            h.tube([(ex, -12), (ex - 1, 2), (ex - 3, 10)], 5, "#bfe9ff", 0, shade=0)

    def d_human(self, p):
        """Iggy's tired face over Rust's (cross-faded with the layer's opacity in the finale)."""
        h = RH(p)
        h.shape(geo.blob([(-34, -36), (-26, -60), (4, -68), (32, -56), (40, -28), (40, 4), (34, 30), (10, 42), (-18, 36), (-34, 14)], n=4),
                IG["skin"], LW, depth=8)
        h.shape(geo.blob([(-40, -6), (-44, -40), (-20, -70), (14, -72), (42, -50), (44, -30), (20, -42), (6, -50), (-18, -40),
                          (-30, -20)], n=3, tension=0.4), IG["hair"], LW, depth=8)
        for ex, ey in ((6, -22), (30, -20)):
            F.eye(h, ex, ey, 5.0, "tired", (0.3, 0), LW)
        h.line([(38, -10), (46, 8), (38, 10)], LW * 0.5)
        F.mouth(h, 22, 26, 9, "frown", 0, LW * 0.9)
