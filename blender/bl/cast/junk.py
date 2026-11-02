"""JUNK (Juno Tamaki), 16 - silhouette: a skinny spring.

Model sheet (char-local px, ground y=0, facing right, ~500 tall to the hair tips):
hips y=-205, shoulders y=-345, head centre (8,-435) drawn at 1.18x, arms ~230 long,
thin hose legs. Seafoam spiky hair (teal streak after the Bloom), cracked brass goggles
on the forehead, patched sunflower overalls with ONE broken strap, navy tee, red rain
boot (front foot), huge metal diving boot (back foot), a single bolt earring.
"""
import math
import numpy as np
from .. import geo
from ..gp import TPen
from ..puppet import Puppet
from .. import face as F

C = dict(skin="#f4c79d", hair="#8fe3cf", hair_dk="#4fb8a6", streak="#2cfff0", over="#ffc928", over_dk="#e0a516",
         tee="#2d3e78", boot_r="#e8392f", boot_m="#8a929c", brass="#d6a640", lens="#a7dcef", patch1="#ff7a3c",
         patch2="#3cc8c8", nut="#b8bcc4")
LW = 6.0
HC = np.array([8.0, -435.0])
HS = 1.18


def H(pen):
    return TPen(pen, HC[0], HC[1], HS)


class Junk(Puppet):
    name = "junk"
    limbs = {"arm_f": ("arm_f", "fore_f", (30, -122), -1), "arm_b": ("arm_b", "fore_b", (-34, -122), -1),
             "leg_f": ("leg_f", "shin_f", (20, -8), 1), "leg_b": ("leg_b", "shin_b", (-20, -8), 1)}
    posable = ("hips", "chest", "head", "arm_f", "fore_f", "arm_b", "fore_b", "leg_f", "shin_f", "leg_b", "shin_b")
    swap_keys = {"eyes": ("head", "eyes"), "brows": ("head", "brows"), "mouth": ("head", "mouth"),
                 "hf": ("fore_f", "hand"), "hb": ("fore_b", "hand")}

    def define(self):
        P = self.part
        P("hips", None, (0, -205), 7, self.d_hips)
        P("chest", "hips", (0, -215), 8, self.d_chest)
        P("head", "chest", (8, -352), 9, self.d_head, swaps=dict(eyes=self.eyes(), brows=self.brows(), mouth=self.mouths()),
          layers=dict(streak=self.d_streak, helmet=self.d_helmet, cracked=self.d_cracked, ladle=self.d_ladle,
                      sweat=lambda p: F.sweat(H(p), 70, -36, 1.2), tears=lambda p: F.tears(H(p), 26, -2, 0.8),
                      blush=lambda p: F.blush(H(p), 30, 20), bandage=self.d_bandage))
        P("arm_b", "chest", (-22, -345), 1, lambda p: self.d_upper(p, (-22, -345), (-28, -234)))
        P("fore_b", "arm_b", (-28, -234), 2, lambda p: self.d_fore(p, (-28, -234), (-34, -122)),
          swaps=dict(hand=self.hands((-34, -122), (-6, 112))))
        P("leg_b", "hips", (-12, -200), 3, lambda p: self.d_thigh(p, (-12, -200), (-16, -104)))
        P("shin_b", "leg_b", (-16, -104), 4, lambda p: self.d_shin(p, (-16, -104), (-20, -8), metal=True))
        P("leg_f", "hips", (12, -200), 5, lambda p: self.d_thigh(p, (12, -200), (16, -104)))
        P("shin_f", "leg_f", (16, -104), 6, lambda p: self.d_shin(p, (16, -104), (20, -8), metal=False))
        P("arm_f", "chest", (18, -345), 10, lambda p: self.d_upper(p, (18, -345), (24, -234)))
        P("fore_f", "arm_f", (24, -234), 11, lambda p: self.d_fore(p, (24, -234), (30, -122)),
          swaps=dict(hand=self.hands((30, -122), (6, 112))))

    # ------------------------------------------------------------ body
    def d_hips(self, p):
        p.shape(geo.blob([(-37, -236), (37, -236), (39, -196), (22, -180), (-22, -180), (-39, -196)], n=3), C["over"], LW)

    def d_chest(self, p):
        o = np.array([0, -205])
        p.shape(geo.blob(np.array([(-32, 10), (-30, -50), (-38, -120), (-36, -150), (36, -150), (34, -110), (28, -50), (34, 10)]) + o, n=4),
                C["tee"], LW, depth=12)
        p.shape(geo.blob(np.array([(-36, 14), (-32, -60), (-28, -100), (28, -100), (30, -60), (36, 14)]) + o, n=4), C["over"], LW, depth=12)
        p.shape(geo.rect(-18, -78, 12, -54) + o, C["patch1"], LW * 0.5, shade=0.3)
        p.line(np.array([(-14, -74), (8, -74)]) + o, LW * 0.3, col="#ffffff")
        p.shape(geo.rect(8, -36, 28, -16) + o, C["patch2"], LW * 0.5, shade=0.3)
        p.line(np.array([(-26, -96), (-25, -148)]) + o, LW * 1.4, col=C["over_dk"])
        p.line(geo.qbez((24, -98), (38, -84), (30, -66), 8) + o, LW * 1.4, col=C["over_dk"])     # the broken strap
        p.fill(geo.circle(-25, -98 - 205, 4.5), "#c8ccd4")
        p.fill(geo.circle(24, -98 - 205, 4.5), "#c8ccd4")

    def d_upper(self, p, a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        p.tube([a, (a + b) / 2, b], 20, C["skin"], LW)
        p.tube([a, a + (b - a) * 0.3], 24, C["tee"], LW)

    def d_fore(self, p, a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        p.tube([a, (a + b) / 2, b], 19, C["skin"], LW)

    def hands(self, wrist, d):
        ang = math.atan2(d[1], d[0])
        lib = {}
        for k in F.HANDS:
            lib[k] = (lambda kk: (lambda pen: F.hand(pen, wrist[0], wrist[1], ang, 1.05, kk, C["skin"], LW)))(k)
        lib["hidden"] = lambda pen: None
        from .others import p_bowl, p_logs
        lib["bowl"] = lambda pen: p_bowl(pen, wrist, ang, skin=C["skin"], size=1.05)
        lib["logs"] = lambda pen: p_logs(pen, wrist, ang, skin=C["skin"])
        return lib

    def d_thigh(self, p, a, b):
        p.tube([a, b], 23, C["over"], LW)

    def d_shin(self, p, a, b, metal):
        a, b = np.asarray(a, float), np.asarray(b, float)
        p.tube([a, b + (0, -46)], 22, C["over"], LW)
        g = TPen(p, b[0], b[1] + 8, 1.0)
        if metal:
            g.shape(geo.blob([(-26, -62), (22, -62), (26, -30), (54, -24), (60, 0), (-30, 0), (-32, -30)], n=3, tension=0.3), C["boot_m"], LW, hi=0.3)
            g.shape(geo.rect(-34, -10, 62, 6), "#4a4f58", LW * 0.8, shade=0.4)
            g.shape(geo.ellipse(40, -16, 18, 12, 20), C["brass"], LW * 0.6, depth=3)
            for k in range(4):
                g.dot(-20 + k * 13, -50, 3, "#d8dde4")
        else:
            g.shape(geo.blob([(-16, -70), (14, -70), (16, -18), (40, -12), (44, 0), (-20, 0), (-20, -30)], n=3, tension=0.3), C["boot_r"], LW, hi=0.35)
            g.line([(-17, -60), (15, -60)], LW * 0.5)

    # ------------------------------------------------------------ head
    def d_head(self, p):
        h = H(p)
        h.shape(geo.blob([(-56, -10), (-50, -44), (-20, -62), (20, -62), (50, -44), (60, -8), (58, 22), (40, 50), (14, 62),
                          (-16, 56), (-44, 34)], n=4), C["skin"], LW, depth=10)
        h.shape(geo.ellipse(-46, 8, 11, 15, 20), C["skin"], LW * 0.8, depth=4)
        h.line(geo.qbez((-48, 0), (-42, 8), (-48, 16), 6), LW * 0.4)
        h.line([(-48, 22), (-48, 30)], LW * 0.35)
        h.shape(geo.ellipse(-48, 36, 6, 6, 6), C["nut"], LW * 0.4, shade=0.3)
        h.line([(56, 12), (60, 18), (55, 20)], LW * 0.45)
        for fx, fy in ((22, 14), (28, 18), (16, 19)):
            h.dot(fx, fy, 1.6, "#c98f62")
        spikes = [(-62, 8), (-86, -22), (-60, -30), (-84, -62), (-46, -60), (-52, -100), (-18, -70), (-6, -118), (14, -74),
                  (40, -112), (40, -70), (74, -88), (58, -48), (84, -42), (60, -20), (64, -6), (40, -30), (-10, -40), (-40, -20)]
        h.shape(geo.spline(spikes, closed=True, n=3, tension=0.25), C["hair"], LW, depth=12)
        for q in ([(-20, -60), (-30, -88)], [(10, -64), (20, -96)], [(-50, -40), (-66, -54)]):
            h.taper(q, LW * 0.7, C["hair_dk"])
        y = -46
        h.line(geo.qbez((-64, y + 6), (-20, y - 12), (66, y + 2), 14), LW * 2.6, col="#3a2a30")
        for (x, r) in ((6, 19), (46, 16)):
            h.shape(geo.circle(x, y, r), C["brass"], LW * 0.9, depth=4)
            h.shape(geo.circle(x, y, r * 0.72), C["lens"], LW * 0.6, shade=0.4, hi=0.5)

    def d_streak(self, p):
        h = H(p)
        h.fill(geo.ellipse(30, -92, 34, 30, 20), C["streak"], 0.25)
        h.shape([(14, -74), (40, -112), (40, -70), (28, -62)], C["streak"], LW * 0.8, shade=0.2, hi=0.6)

    def d_cracked(self, p):
        h = H(p)
        h.line([(40, -56), (46, -48), (42, -42), (50, -36)], LW * 0.4, col="#ffffff")
        h.line([(46, -48), (54, -50)], LW * 0.35, col="#ffffff")

    def d_bandage(self, p):
        h = H(p)
        h.shape(geo.blob([(-58, -30), (60, -24), (62, -10), (-58, -14)], n=2, tension=0.2), "#ffffff", LW * 0.7, shade=0.3)
        h.shape(geo.rect(36, 8, 54, 22), "#f2d8b0", LW * 0.4, shade=0.2)
        h.line([(40, 15), (50, 15)], LW * 0.3)

    def d_helmet(self, p):
        h = H(p)
        h.fill(geo.circle(10, 4, 112, 60), "#bfe8ff", 0.2)
        h.line(geo.circle(10, 4, 112, 60), LW * 0.9, col="#e8f8ff", closed=True)
        h.line(geo.qbez((-60, -60), (-30, -92), (14, -100), 10), LW * 1.3, col="#ffffff", alpha=0.8)
        h.shape(geo.ellipse(10, 106, 70, 16, 30), C["brass"], LW * 0.8, depth=4)

    def d_ladle(self, p):
        h = H(p)
        h.line([(40, -62), (130, -150)], LW * 2.2, col="#8a5a32")
        h.shape(geo.ellipse(30, -54, 26, 15, 22, rot=-0.3), "#b9c0c8", LW * 0.8, hi=0.4)

    def eyes(self):
        lib = {}
        for k, look in (("dot", (0.3, 0)), ("up", (0.2, -0.8)), ("down", (0.2, 0.8)), ("back", (-0.8, 0)), ("ahead", (0.9, 0))):
            lib[k] = (lambda lk: (lambda pen: [F.eye(H(pen), ex, ey, 6.8, "dot", lk, LW) for ex, ey in ((10, -4), (42, -2))]))(look)
        for k in ("half", "closed", "happy", "sad", "huge", "shock", "spiral", "x"):
            lib[k] = (lambda kk: (lambda pen: [F.eye(H(pen), ex, ey, 6.8, kk, (0.3, 0), LW) for ex, ey in ((10, -4), (42, -2))]))(k)
        return lib

    def brows(self):
        lib = {}
        for k, ang in (("neutral", 0.0), ("angry", 0.5), ("worried", -0.4), ("up", -0.15)):
            dy = -8 if k == "up" else 0
            lib[k] = (lambda a, d: (lambda pen: (F.brow(H(pen), 10, -26 + d, 11, a, LW, side=-1),
                                                 F.brow(H(pen), 42, -24 + d, 10, a, LW, side=1))))(ang, dy)
        lib["high"] = lambda pen: (F.brow(H(pen), 8, -54, 12, -0.4, LW, side=-1), F.brow(H(pen), 44, -52, 11, -0.4, LW, side=1))
        lib["none"] = lambda pen: None
        return lib

    def mouths(self):
        lib = {}
        for k in ("smile", "smirk", "frown", "flat", "wobble", "o"):
            lib[k] = (lambda kk: (lambda pen: F.mouth(H(pen), 34, 36, 14, kk, 0.0, LW)))(k)
        lib["grin"] = lambda pen: F.mouth(H(pen), 34, 36, 15, "grin", 0.3, LW, teeth="#ffffff")
        lib["shout"] = lambda pen: F.mouth(H(pen), 34, 38, 15, "shout", 0.8, LW)
        lib["jaw"] = lambda pen: F.mouth(H(pen), 34, 38, 15, "jaw", 1.0, LW)
        F.talk_set(lib, lambda pen, o: F.mouth(H(pen), 34, 36, 14, "talk", o, LW))
        return lib
