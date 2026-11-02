"""GRANNY KETTLE, SELA GLOAM, MAGNUS GLOAM, BOLT (small + giant), PIP, GUARD, RUSTMITE.

Silhouettes: Granny = a wide teapot (handle arm on the hip, spout arm out, bun lid);
Sela = neat bob + big round glasses + lab coat; Magnus = a gold bowling ball with a
chimney top hat; Bolt = soup can with googly eyes; Rustmite = one-eyed orange drip.
"""
import math
import numpy as np
from .. import geo
from ..gp import TPen
from ..puppet import Puppet
from .. import face as F
from .common import add_arm, add_leg, eyes_lib, brows_lib, mouths_lib, STD_SWAPS, STD_POSABLE

LW = 6.0


# ============================================================================ props held in hands

def p_ladle(pen, w, ang):
    g = TPen(pen, w[0], w[1], 1.0, ang - math.pi / 2)
    g.line([(0, -60), (0, 150)], LW * 2.4, col="#8a5a32")
    g.line([(0, -60), (0, 150)], LW * 0.45)
    g.shape(geo.ellipse(0, 172, 30, 22, 24), "#b9c0c8", LW * 0.9, hi=0.5)
    F.hand(pen, w[0], w[1], ang, 1.3, "fist", "#f0c9a4", LW)


def p_bowl(pen, w, ang, skin="#f0c9a4", size=1.3):
    g = TPen(pen, w[0], w[1] - 22, 1.0)
    g.shape(geo.blob([(-46, -10), (46, -10), (36, 22), (0, 32), (-36, 22)], n=4), "#f3ead6", LW, hi=0.3)
    g.line(geo.qbez((-40, 4), (0, 16), (40, 4), 10), LW * 0.5, col="#d84a3a")
    g.fill(geo.ellipse(0, -10, 44, 9, 20), "#e8c070")
    g.line(geo.qbez((-20, -14), (0, -30), (24, -40), 8), LW * 0.4)
    F.hand(pen, w[0], w[1], ang, size, "grab", skin, LW)


def p_paper(pen, w, ang, skin="#f0c9a4"):
    g = TPen(pen, w[0], w[1], 1.0)
    g.shape(geo.rect(-90, -150, 90, 40), "#efe9da", LW * 0.8, shade=0.4)
    for k in range(6):
        g.line([(-70, -110 + k * 22), (70, -110 + k * 22)], LW * 0.6, col="#9a948a")
    F.hand(pen, w[0], w[1], ang, 1.3, "grab", skin, LW)


def p_clipboard(pen, w, ang, skin="#f6d2b5"):
    g = TPen(pen, w[0], w[1], 1.0, -0.15)
    g.shape(geo.rrect(-34, -70, 34, 20, 4), "#c89a5a", LW * 0.8)
    g.shape(geo.rect(-26, -58, 26, 12), "#ffffff", LW * 0.4, shade=0.2)
    for k in range(4):
        g.line([(-18, -46 + k * 14), (18, -46 + k * 14)], LW * 0.35, col="#8a8aa0")
    g.shape(geo.rect(-12, -76, 12, -64), "#9aa0aa", LW * 0.5, shade=0.3)
    F.hand(pen, w[0], w[1], ang, 1.0, "grab", skin, LW)


def p_logs(pen, w, ang, skin="#f6d2b5"):
    g = TPen(pen, w[0], w[1], 1.0, 0.1)
    g.shape(geo.rect(-30, -80, 40, 10), "#f2e6b8", LW * 0.7, shade=0.3)
    g.shape(geo.rect(-38, -70, 32, 18), "#efe9da", LW * 0.7, shade=0.3)
    g.line([(-26, -50), (20, -50)], LW * 0.4, col="#b03030")
    F.hand(pen, w[0], w[1], ang, 1.0, "grab", skin, LW)


def p_bandage(pen, w, ang):
    g = TPen(pen, w[0], w[1], 1.0)
    g.shape(geo.ellipse(0, -10, 20, 16, 20), "#ffffff", LW * 0.7, shade=0.4)
    g.line(geo.qbez((10, -10), (60, 20), (90, -10), 10), LW * 2.6, col="#ffffff")
    F.hand(pen, w[0], w[1], ang, 1.3, "grab", "#f0c9a4", LW)


# ============================================================================ GRANNY

GR = dict(skin="#f0c9a4", top="#c8432f", apron="#f3ead6", sash="#3a6e8c", hair="#f6f4ee", stick="#7a4a2a", slip="#3a2a2a")
GHC = np.array([10.0, -262.0])


def GH(pen):
    return TPen(pen, GHC[0], GHC[1], 1.0)


class Granny(Puppet):
    name = "granny"
    limbs = {"arm_f": ("arm_f", "fore_f", (180, -160), 1), "arm_b": ("arm_b", "fore_b", (-110, -80), -1)}
    posable = ("hips", "head", "arm_f", "fore_f", "arm_b", "fore_b")
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        P("hips", None, (0, -110), 5, self.d_body)
        P("head", "hips", (4, -210), 6, self.d_head, swaps=dict(
            eyes=eyes_lib(GH, ((-2, -6), (26, -4)), 5.0, LW),
            brows=brows_lib(GH, ((-2, -22), (26, -20)), 9, LW * 1.1, col="#c9c4bc"),
            mouth=mouths_lib(GH, 14, 22, 12, LW)),
          layers=dict(blush=lambda p: F.blush(GH(p), 22, 10, 0.9), vein=lambda p: F.vein(GH(p), 40, -30, 1.0)))
        extra = dict(ladle=p_ladle, bowl=p_bowl, paper=p_paper, bandage=p_bandage)
        add_arm(self, "b", (-86, -172), (-142, -122), (-110, -80), 1, 2, GR["top"], GR["skin"], LW, w=(42, 54), sleeve=0.45,
                size=1.3, extra=extra, parent="hips")
        add_arm(self, "f", (86, -172), (140, -130), (180, -160), 8, 9, GR["top"], GR["skin"], LW, w=(42, 54), sleeve=0.45,
                size=1.3, extra=extra, parent="hips")

    def d_body(self, p):
        for sx in (-1, 1):                                    # tiny legs + slippers
            p.tube([(sx * 36, -40), (sx * 38, -10)], 22, GR["skin"], LW)
            p.shape(geo.blob([(sx * 38 - 22, -14), (sx * 38 + 26, -16), (sx * 38 + 30, 0), (sx * 38 - 24, 0)], n=3), GR["slip"], LW)
        body = geo.ellipse(0, -122, 120, 98, 60)
        p.shape(body, GR["top"], LW, depth=22)
        p.shape(geo.blob([(-70, -150), (70, -150), (84, -80), (60, -36), (0, -26), (-60, -36), (-84, -80)], n=4), GR["apron"], LW, depth=12)
        p.shape(geo.rect(-112, -164, 112, -140), GR["sash"], LW * 0.8, shade=0.3)
        p.line(geo.qbez((-40, -180), (0, -150), (40, -180), 10), LW * 0.6)
        for k in range(3):
            p.line([(-60 + k * 50, -110), (-50 + k * 50, -96)], LW * 0.3, col="#c9bfa8")

    def d_head(self, p):
        h = GH(p)
        h.shape(geo.circle(-22, -66, 52), GR["hair"], LW, depth=8)                 # the bun (teapot lid)
        h.shape(geo.circle(-18, -110, 18), GR["hair"], LW * 0.8, depth=4)
        h.line([(-80, -96), (30, -40)], LW * 1.3, col=GR["stick"])
        h.line([(-70, -40), (20, -110)], LW * 1.3, col=GR["stick"])
        h.shape(geo.blob([(-42, -14), (-36, -40), (-4, -50), (30, -42), (44, -14), (42, 18), (24, 38), (-6, 42), (-32, 30)], n=4),
                GR["skin"], LW, depth=8)
        h.shape(geo.blob([(-44, -10), (-40, -40), (-6, -52), (30, -46), (40, -28), (10, -34), (-20, -26), (-36, -6)], n=3), GR["hair"], LW, depth=6)
        h.shape(geo.ellipse(-34, 6, 8, 11, 16), GR["skin"], LW * 0.7, depth=3)
        h.line([(40, 2), (48, 10), (40, 13)], LW * 0.5)
        for (x0, y0) in ((-12, 14), (34, 16)):
            h.line(geo.qbez((x0 - 6, y0), (x0, y0 + 4), (x0 + 6, y0), 6), LW * 0.3, alpha=0.6)
        h.line(geo.qbez((-2, -32), (8, -34), (18, -32), 6), LW * 0.3, alpha=0.5)


# ============================================================================ SELA

SE = dict(skin="#f6d2b5", hair="#7b4bc4", hair_dk="#53308f", rim="#2a2a38", lens="#e3f4ff", coat="#f6f8fb",
          shirt="#5b3d8a", legs="#3b2a5a", shoe="#2a2030")
SHC = np.array([10.0, -372.0])


def SH(pen):
    return TPen(pen, SHC[0], SHC[1], 1.12)


def _sela_shoe(g):
    g.shape(geo.blob([(-12, -14), (10, -16), (26, -6), (26, 0), (-14, 0)], n=3), SE["shoe"], LW)


class Sela(Puppet):
    name = "sela"
    limbs = {"arm_f": ("arm_f", "fore_f", (24, -118), -1), "arm_b": ("arm_b", "fore_b", (-26, -118), -1),
             "leg_f": ("leg_f", "shin_f", (14, -8), 1), "leg_b": ("leg_b", "shin_b", (-14, -8), 1)}
    posable = STD_POSABLE
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        P("hips", None, (0, -175), 7, self.d_skirt)
        P("chest", "hips", (0, -182), 8, self.d_chest)
        P("head", "chest", (4, -300), 9, self.d_head, swaps=dict(
            eyes=eyes_lib(SH, ((8, -2), (40, 0)), 5.6, LW), brows=brows_lib(SH, ((8, -30), (40, -28)), 10, LW, col=SE["hair_dk"]),
            mouth=mouths_lib(SH, 30, 34, 11, LW)),
          layers=dict(glasses=self.d_glasses, lenses=self.d_lenses, blush=lambda p: F.blush(SH(p), 30, 18, 0.9),
                      sweat=lambda p: F.sweat(SH(p), 64, -30, 1.0)))
        extra = dict(clipboard=p_clipboard, logs=p_logs)
        add_arm(self, "b", (-18, -296), (-22, -206), (-26, -118), 1, 2, SE["coat"], SE["skin"], LW, w=(18, 17), sleeve="full", extra=extra)
        add_leg(self, "b", (-10, -170), (-12, -88), (-14, -8), 3, 4, SE["legs"], LW, w=(18, 16), shoe=_sela_shoe)
        add_leg(self, "f", (10, -170), (12, -88), (14, -8), 5, 6, SE["legs"], LW, w=(18, 16), shoe=_sela_shoe)
        add_arm(self, "f", (16, -296), (20, -206), (24, -118), 10, 11, SE["coat"], SE["skin"], LW, w=(18, 17), sleeve="full", extra=extra)

    default_on = ("glasses",)

    def d_skirt(self, p):
        p.shape(geo.blob([(-36, -196), (36, -196), (52, -100), (60, -64), (-60, -64), (-52, -100)], n=3, tension=0.3), SE["coat"], LW, depth=12)
        p.line([(0, -190), (0, -66)], LW * 0.5, col="#b8c2d0")

    def d_chest(self, p):
        p.shape(geo.blob([(-34, -176), (-38, -240), (-36, -300), (34, -300), (38, -240), (34, -176)], n=3), SE["coat"], LW, depth=12)
        p.shape(np.array([(-12, -300), (12, -300), (0, -262)]), SE["shirt"], LW * 0.6, shade=0.2)
        p.line([(-12, -300), (-4, -250), (-2, -180)], LW * 0.5)
        p.line([(12, -300), (4, -250)], LW * 0.5)
        for (x, y, c) in ((-26, -240, "#e8392f"), (-20, -244, "#ffc928"), (22, -236, "#3cc8c8")):
            p.line([(x, y), (x, y - 22)], LW * 0.9, col=c)
        p.shape(geo.rect(-32, -240, -8, -214), SE["coat"], LW * 0.5, shade=0.2)
        p.shape(geo.rect(10, -234, 32, -210), SE["coat"], LW * 0.5, shade=0.2)

    def d_head(self, p):
        h = SH(p)
        h.shape(geo.blob([(-58, -20), (-52, -62), (-10, -84), (34, -80), (66, -50), (70, 0), (64, 40), (40, 46), (30, 0),
                          (-40, 10), (-60, 44), (-70, 30)], n=4), SE["hair"], LW, depth=10)
        h.shape(geo.blob([(-44, -10), (-40, -40), (-10, -54), (30, -52), (54, -28), (56, 10), (44, 40), (20, 54), (-10, 50), (-36, 30)], n=4),
                SE["skin"], LW, depth=8)
        h.shape(geo.blob([(-50, -14), (-46, -60), (0, -78), (44, -70), (64, -36), (60, -14), (40, -30), (10, -24), (-20, -30), (-40, -8)],
                         n=3, tension=0.35), SE["hair"], LW, depth=8)
        h.line([(54, 12), (58, 18), (54, 20)], LW * 0.4)

    def d_glasses(self, p):
        h = SH(p)
        for x in (8, 40):
            h.fill(geo.circle(x, 0, 17), SE["lens"], 0.35)
            h.line(geo.circle(x, 0, 17), LW * 0.9, col=SE["rim"], closed=True)
            h.line(geo.qbez((x - 10, -10), (x - 4, -14), (x + 2, -12), 6), LW * 0.5, col="#ffffff")
        h.line([(25, -2), (23, -2)], LW * 0.8, col=SE["rim"])
        h.line([(-9, -2), (-36, -6)], LW * 0.8, col=SE["rim"])

    def d_lenses(self, p):
        h = SH(p)
        for x in (8, 40):
            h.line([(x, -17), (x, -26)], LW * 0.5, col=SE["rim"])
            h.fill(geo.circle(x, 4, 12), "#bff0ff", 0.6)
            h.line(geo.circle(x, 4, 12), LW * 0.7, col="#d6a640", closed=True)


# ============================================================================ MAGNUS

MG = dict(skin="#f2b8a0", suit="#e2b33c", suit_dk="#b8861f", shirt="#fff8e6", tie="#6a2c8c", hat="#202028", band="#d6a640",
          legs="#2a2a30", shoe="#121216")
MHC = np.array([10.0, -380.0])


def MH(pen):
    return TPen(pen, MHC[0], MHC[1], 1.0)


def _mag_shoe(g):
    g.shape(geo.blob([(-18, -16), (14, -18), (32, -6), (32, 0), (-20, 0)], n=3), MG["shoe"], LW, hi=0.6)


class Magnus(Puppet):
    name = "magnus"
    limbs = {"arm_f": ("arm_f", "fore_f", (196, -150), 1), "arm_b": ("arm_b", "fore_b", (-196, -150), -1),
             "leg_f": ("leg_f", "shin_f", (40, -8), 1), "leg_b": ("leg_b", "shin_b", (-40, -8), 1)}
    posable = STD_POSABLE
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        add_leg(self, "b", (-44, -70), (-42, -40), (-40, -8), 1, 2, MG["legs"], LW, w=(30, 28), shoe=_mag_shoe, parent=None)
        add_leg(self, "f", (44, -70), (42, -40), (40, -8), 3, 4, MG["legs"], LW, w=(30, 28), shoe=_mag_shoe, parent=None)
        self.parts["leg_b"].parent = "hips"
        self.parts["leg_f"].parent = "hips"
        P("hips", None, (0, -70), 6, lambda p: None)
        self.order.remove("hips")
        self.order.insert(0, "hips")
        P("chest", "hips", (0, -70), 7, self.d_body)
        P("head", "chest", (6, -318), 9, self.d_head, swaps=dict(
            eyes=eyes_lib(MH, ((-6, -16), (26, -14)), 4.8, LW, extra=()),
            brows=brows_lib(MH, ((-6, -34), (26, -32)), 10, LW * 1.2),
            mouth=self.mouths()))
        add_arm(self, "b", (-122, -236), (-164, -194), (-196, -150), 5, 6, MG["suit"], "#ffffff", LW, w=(30, 28), sleeve="full")
        add_arm(self, "f", (122, -236), (164, -194), (196, -150), 10, 11, MG["suit"], "#ffffff", LW, w=(30, 28), sleeve="full")

    def d_body(self, p):
        c = np.array([0, -200])
        p.shape(geo.circle(c[0], c[1], 148, 72), MG["suit"], LW, depth=26, hi=0.7)
        p.shape(np.array([(-40, -340), (40, -340), (0, -220)]), MG["shirt"], LW * 0.8, shade=0.2)
        p.shape(np.array([(-10, -330), (10, -330), (14, -250), (0, -228), (-14, -250)]), MG["tie"], LW * 0.7, shade=0.3)
        for sx in (-1, 1):
            p.shape(np.array([(sx * 40, -342), (sx * 70, -300), (sx * 30, -230), (sx * 6, -228)]), MG["suit_dk"], LW * 0.8, shade=0.3)
        for k in range(3):
            p.shape(geo.circle(0, -200 + k * 36, 7), "#fff2a8", LW * 0.5, shade=0.3)
        p.fill(geo.ellipse(-70, -290, 40, 22, 20, rot=-0.6), "#fff6d0", 0.75)

    def d_head(self, p):
        h = MH(p)
        h.shape(geo.circle(0, 0, 70, 50), MG["skin"], LW, depth=12)
        h.fill(geo.ellipse(-26, -38, 18, 10, 16, rot=-0.5), "#ffffff", 0.7)
        for sx in (-1, 1):
            h.shape(geo.ellipse(sx * 64, 6, 10, 14, 14), MG["skin"], LW * 0.8, depth=3)
        h.line([(30, -2), (40, 10), (30, 12)], LW * 0.5)
        hat = TPen(p, MHC[0] - 4, MHC[1] - 58, 1.0, -0.12)
        hat.shape(geo.ellipse(0, 0, 70, 12, 30), MG["hat"], LW, hi=0.3)
        hat.shape(geo.rect(-44, -96, 44, -4), MG["hat"], LW, hi=0.4)
        hat.shape(geo.rect(-44, -28, 44, -10), MG["band"], LW * 0.6, shade=0.3)
        hat.shape(geo.rect(14, -134, 34, -92), "#5a5a66", LW * 0.8, shade=0.4)        # the little chimney
        hat.shape(geo.rect(10, -142, 38, -132), "#3a3a44", LW * 0.6, shade=0.3)

    def mouths(self):
        lib = {}
        g = "#f2c33c"
        lib["grin"] = lambda pen: F.mouth(MH(pen), 12, 30, 30, "grin", 0.2, LW, teeth=g)
        lib["closed"] = lambda pen: F.mouth(MH(pen), 12, 30, 30, "grin", 0.0, LW, teeth=g)
        for k, o in (("t1", 0.4), ("t2", 0.8), ("t3", 1.2)):
            lib[k] = (lambda oo: (lambda pen: F.mouth(MH(pen), 12, 30, 30, "grin", oo, LW, teeth=g)))(o)
        lib["shout"] = lambda pen: F.mouth(MH(pen), 12, 32, 26, "shout", 1.0, LW, teeth=g)
        lib["frown"] = lambda pen: F.mouth(MH(pen), 12, 34, 20, "frown", 0.0, LW)
        lib["wobble"] = lambda pen: F.mouth(MH(pen), 12, 34, 20, "wobble", 0.0, LW)
        lib["o"] = lambda pen: F.mouth(MH(pen), 12, 34, 24, "o", 0.0, LW)
        return lib


# ============================================================================ BOLT (small)

BO = dict(can="#c7cdd4", label="#d8432f", label2="#f4eee0", rust="#a8582a", crab="#ff8a5c", crab_dk="#d65a34", eye="#ffffff")


class Bolt(Puppet):
    name = "bolt"
    limbs = {}
    posable = ("hips", "head", "claw")
    swap_keys = {"eyes": ("head", "eyes")}

    def define(self):
        P = self.part
        P("hips", None, (0, -30), 2, self.d_can)
        P("head", "hips", (38, -30), 3, self.d_crab, swaps=dict(eyes=self.eyes()), layers=dict(glow=self.d_glow))
        P("claw", "head", (52, -16), 4, self.d_claw)

    def d_can(self, p):
        p.shape(geo.rrect(-50, -60, 40, 0, 6), BO["can"], LW * 0.8, hi=0.4)
        p.shape(geo.rect(-50, -48, 40, -14), BO["label"], LW * 0.6, shade=0.3)
        p.shape(geo.rect(-40, -40, 10, -22), BO["label2"], LW * 0.4, shade=0.2)
        p.line([(-34, -31), (4, -31)], LW * 0.5, col=BO["label"])
        p.fill(geo.circle(-20, -6, 6), BO["rust"])
        p.fill(geo.circle(24, -52, 5), BO["rust"])
        p.shape(geo.ellipse(40, -30, 10, 30, 24), "#e2e6ea", LW * 0.8, shade=0.2)
        p.fill(geo.ellipse(42, -30, 6, 24, 20), "#3a2a2a")

    def d_crab(self, p):
        for k in range(3):
            p.line(geo.qbez((40, -16 + k * 6), (58, -6 + k * 8), (62, 0), 6), LW * 0.7, col=BO["crab_dk"])
        p.shape(geo.blob([(36, -44), (56, -48), (68, -34), (66, -16), (50, -10), (38, -16)], n=3), BO["crab"], LW * 0.8)
        for x in (52, 64):
            p.line([(x, -44), (x + 4, -66)], LW * 0.7, col=BO["crab_dk"])
        p.shape(geo.blob([(60, -30), (74, -32), (78, -24), (66, -20)], n=3), BO["crab"], LW * 0.6)

    def eyes(self):
        lib = {}
        for k, (dx, dy, r) in (("googly", (2, 2, 9)), ("left", (-3, 1, 9)), ("up", (0, -3, 9)), ("huge", (1, 1, 13))):
            lib[k] = (lambda ddx, ddy, rr: (lambda pen: [(pen.shape(geo.circle(x, -74, rr), BO["eye"], LW * 0.6, shade=0.2),
                                                          pen.fill(geo.circle(x + ddx, -74 + ddy, rr * 0.42), "#1b1424")) for x in (54, 70)]))(dx, dy, r)
        lib["angry"] = lambda pen: [(pen.shape(geo.circle(x, -74, 9), BO["eye"], LW * 0.6, shade=0.2), pen.fill(geo.circle(x + 1, -71, 4), "#1b1424"),
                                     pen.line([(x - 10, -86 + (x - 54) * 0.4), (x + 10, -80 - (x - 54) * 0.4)], LW * 0.9)) for x in (54, 70)]
        lib["happy"] = lambda pen: [pen.line(geo.qbez((x - 8, -72), (x, -84), (x + 8, -72), 8), LW * 0.8) for x in (54, 70)]
        return lib

    def d_claw(self, p):
        p.shape(geo.blob([(48, -20), (76, -30), (98, -22), (100, -6), (84, 2), (60, -2)], n=3), BO["crab"], LW * 0.8, hi=0.3)
        p.shape(np.array([(82, -8), (100, -18), (104, -8), (92, 0)]), BO["crab_dk"], LW * 0.6, shade=0.2)

    def d_glow(self, p):
        p.fill(geo.ellipse(56, -40, 70, 56, 30), "#2cfff0", 0.22)


class BoltGiant(Puppet):
    """Big Shell Time: house-sized armoured crab still wearing the soup can as a helmet."""
    name = "boltg"
    limbs = {}
    posable = ("hips", "head", "claw", "claw_b")
    swap_keys = {"eyes": ("head", "eyes")}

    def define(self):
        P = self.part
        P("claw_b", "hips", (-160, -260), 1, lambda p: self.d_claw(p, -1))
        P("hips", None, (0, -200), 2, self.d_body)
        P("head", "hips", (0, -360), 3, self.d_head, swaps=dict(eyes=self.eyes()))
        P("claw", "hips", (170, -260), 4, lambda p: self.d_claw(p, 1, big=True))

    def d_body(self, p):
        for sx in (-1, 1):
            for k in range(3):
                x0 = sx * (80 + k * 40)
                p.tube([(x0, -150), (x0 + sx * 60, -110), (x0 + sx * 80, 0)], 26, BO["crab_dk"], LW)
        p.shape(geo.blob([(-230, -200), (-180, -330), (0, -380), (180, -330), (230, -200), (160, -120), (0, -100), (-160, -120)], n=4),
                BO["crab"], LW * 1.3, depth=40, hi=0.4)
        for k in range(4):
            p.line(geo.qbez((-180 + k * 20, -170 - k * 40), (0, -200 - k * 45), (180 - k * 20, -170 - k * 40), 12), LW * 0.8, col=BO["crab_dk"])

    def d_head(self, p):
        p.shape(geo.rrect(-110, -470, 110, -330, 18), BO["can"], LW * 1.2, hi=0.4)
        p.shape(geo.rect(-110, -440, 110, -370), BO["label"], LW * 0.9, shade=0.3)
        p.shape(geo.rect(-70, -428, 50, -384), BO["label2"], LW * 0.6, shade=0.2)
        p.fill(geo.circle(-60, -350, 14), BO["rust"])
        for x in (-40, 40):
            p.line([(x, -380), (x * 1.3, -520)], LW * 1.6, col=BO["crab_dk"])

    def eyes(self):
        lib = {}
        for k, (dx, dy) in (("googly", (4, 4)), ("angry", (2, 6)), ("up", (0, -6))):
            lib[k] = (lambda ddx, ddy, kk: (lambda pen: [(pen.shape(geo.circle(x * 1.3, -540, 30), BO["eye"], LW, shade=0.2),
                                                          pen.fill(geo.circle(x * 1.3 + ddx * 2, -540 + ddy * 2, 13), "#1b1424"),
                                                          pen.line([(x * 1.3 - 30, -580 + (14 if x < 0 else -6)), (x * 1.3 + 30, -580 + (-6 if x < 0 else 14))], LW * 1.6)
                                                          if kk == "angry" else None) for x in (-40, 40)]))(dx, dy, k)
        return lib

    def d_claw(self, p, sx, big=False):
        s = 1.4 if big else 1.0
        g = TPen(p, sx * 170, -260, s)
        g.tube([(0, 0), (sx * 60, -40)], 40, BO["crab"], LW)
        g.shape(geo.blob([(sx * 40, -40), (sx * 120, -120), (sx * 190, -100), (sx * 200, -40), (sx * 150, 0), (sx * 80, -10)], n=3), BO["crab"], LW, hi=0.3)
        g.shape(np.array([(sx * 150, -60), (sx * 210, -110), (sx * 220, -70), (sx * 180, -40)]), BO["crab_dk"], LW, shade=0.2)


# ============================================================================ PIP / GUARD / RUSTMITE

PI = dict(skin="#c98a5e", hair="#2a1a14", dress="#ff8a2a", dress_dk="#d8641a", shoe="#d83a3a")
PHC = np.array([8.0, -222.0])


def PH(pen):
    return TPen(pen, PHC[0], PHC[1], 0.95)


class Pip(Puppet):
    name = "pip"
    limbs = {"arm_f": ("arm_f", "fore_f", (20, -84), -1), "arm_b": ("arm_b", "fore_b", (-22, -84), -1),
             "leg_f": ("leg_f", "shin_f", (10, -6), 1), "leg_b": ("leg_b", "shin_b", (-10, -6), 1)}
    posable = STD_POSABLE
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        P("hips", None, (0, -96), 7, lambda p: p.shape(geo.blob([(-30, -120), (30, -120), (46, -50), (-46, -50)], n=2, tension=0.2),
                                                         PI["dress"], LW, depth=10))
        P("chest", "hips", (0, -100), 8, lambda p: p.shape(geo.blob([(-26, -96), (-26, -150), (26, -150), (26, -96)], n=3), PI["dress"], LW))
        P("head", "chest", (4, -170), 9, self.d_head, swaps=dict(
            eyes=eyes_lib(PH, ((4, -2), (30, 0)), 5.6, LW), brows=brows_lib(PH, ((4, -24), (30, -22)), 8, LW * 0.9),
            mouth=mouths_lib(PH, 22, 26, 10, LW)))
        shoe = lambda g: g.shape(geo.blob([(-10, -12), (10, -12), (20, 0), (-12, 0)], n=3), PI["shoe"], LW)
        add_arm(self, "b", (-16, -146), (-20, -114), (-22, -84), 1, 2, PI["dress"], PI["skin"], LW, w=(14, 13), sleeve=0.3, size=0.8)
        add_leg(self, "b", (-10, -60), (-10, -34), (-10, -6), 3, 4, PI["skin"], LW, w=(14, 13), shoe=shoe)
        add_leg(self, "f", (10, -60), (10, -34), (10, -6), 5, 6, PI["skin"], LW, w=(14, 13), shoe=shoe)
        add_arm(self, "f", (14, -146), (18, -114), (20, -84), 10, 11, PI["dress"], PI["skin"], LW, w=(14, 13), sleeve=0.3, size=0.8)

    def d_head(self, p):
        h = PH(p)
        for sx in (-1, 1):
            h.shape(geo.circle(sx * 46 + 4, -10, 18), PI["hair"], LW, depth=4)
        h.shape(geo.circle(6, 0, 44, 36), PI["skin"], LW, depth=8)
        h.shape(geo.blob([(-40, -4), (-36, -36), (0, -50), (36, -40), (48, -14), (20, -26), (-10, -22)], n=3), PI["hair"], LW, depth=6)
        h.line([(42, 8), (46, 12), (42, 14)], LW * 0.4)


class Guard(Puppet):
    name = "guard"
    limbs = {"arm_f": ("arm_f", "fore_f", (90, -250), -1), "arm_b": ("arm_b", "fore_b", (-90, -250), -1),
             "leg_f": ("leg_f", "shin_f", (34, -8), 1), "leg_b": ("leg_b", "shin_b", (-34, -8), 1)}
    posable = STD_POSABLE
    swap_keys = STD_SWAPS

    def define(self):
        P = self.part
        col, skin = "#4a4f5c", "#d9a07a"
        P("hips", None, (0, -240), 7, lambda p: p.shape(geo.rect(-70, -270, 70, -220), col, LW))
        P("chest", "hips", (0, -250), 8, lambda p: (p.shape(geo.rrect(-110, -560, 110, -240, 30), col, LW, depth=24),
                                                    p.shape(geo.rect(-16, -556, 16, -440), "#e8e8e8", LW * 0.6, shade=0.2),
                                                    p.shape(np.array([(-8, -540), (8, -540), (10, -460), (0, -446), (-10, -460)]), "#202020", LW * 0.5, shade=0.2),
                                                    p.shape(geo.rect(40, -500, 80, -470), "#d6a640", LW * 0.5, shade=0.3)))
        hp = lambda pen: TPen(pen, 4, -620, 1.0)
        P("head", "chest", (0, -560), 9, lambda p: (hp(p).shape(geo.rrect(-40, -50, 44, 50, 18), skin, LW),
                                                    hp(p).shape(geo.rrect(-46, -60, 48, -36, 8), "#2a2a30", LW),
                                                    hp(p).shape(geo.rrect(-36, -14, 46, 8, 5), "#101014", LW * 0.6, shade=0, hi=0.4)),
          swaps=dict(eyes={"none": lambda pen: None}, brows={"none": lambda pen: None}, mouth=mouths_lib(hp, 10, 26, 14, LW)))
        add_arm(self, "b", (-96, -530), (-110, -400), (-90, -250), 1, 2, col, skin, LW, w=(46, 42), sleeve="full", size=1.5)
        add_leg(self, "b", (-34, -230), (-34, -120), (-34, -8), 3, 4, col, LW, w=(46, 42),
                shoe=lambda g: g.shape(geo.blob([(-26, -20), (20, -22), (44, -6), (44, 0), (-28, 0)], n=3), "#141418", LW))
        add_leg(self, "f", (34, -230), (34, -120), (34, -8), 5, 6, col, LW, w=(46, 42),
                shoe=lambda g: g.shape(geo.blob([(-26, -20), (20, -22), (44, -6), (44, 0), (-28, 0)], n=3), "#141418", LW))
        add_arm(self, "f", (96, -530), (110, -400), (90, -250), 10, 11, col, skin, LW, w=(46, 42), sleeve="full", size=1.5)


MITE = dict(body="#ff7a1a", dk="#c8501a", lt="#ffb05a")


def draw_mite(pen, x=0.0, y=0.0, s=1.0, eye="open", squash=1.0, lw=5.0, glow=True):
    g = TPen(pen, x, y, s)
    if glow:
        g.fill(geo.ellipse(0, -22 * squash, 40, 34 * squash, 18), MITE["body"], 0.22)
    for sx in (-1, 1):
        g.tube([(sx * 10, -8), (sx * 12, 0)], 8, MITE["dk"], lw * 0.7, shade=0)
    g.shape(geo.blob([(-24, -2), (-26, -24 * squash), (-8, -46 * squash), (10, -48 * squash), (26, -26 * squash), (24, -2), (0, 2)], n=4),
            MITE["body"], lw, shade=0.8, hi=0.6)
    if eye == "open":
        g.shape(geo.circle(2, -26 * squash, 11), "#fff6e0", lw * 0.6, shade=0.2)
        g.fill(geo.circle(5, -25 * squash, 5), "#1b1424")
        g.fill(geo.circle(3, -28 * squash, 1.8), "#ffffff")
    elif eye == "happy":
        g.line(geo.qbez((-8, -24 * squash), (2, -36 * squash), (12, -24 * squash), 8), lw * 0.8)
    elif eye == "angry":
        g.shape(geo.circle(2, -26 * squash, 10), "#fff6e0", lw * 0.6, shade=0.2)
        g.fill(geo.circle(4, -24 * squash, 4.5), "#1b1424")
        g.line([(-10, -40 * squash), (14, -32 * squash)], lw * 0.9)


class Rustmite(Puppet):
    name = "mite"
    limbs = {}
    posable = ("hips",)
    swap_keys = {"eyes": ("hips", "eyes")}

    def define(self):
        self.part("hips", None, (0, 0), 1, lambda p: None,
                  swaps=dict(eyes={k: (lambda kk: (lambda pen: draw_mite(pen, 0, 0, 1.0, kk)))(k) for k in ("open", "happy", "angry")}))
