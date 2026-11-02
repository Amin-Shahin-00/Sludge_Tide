"""CHAPTER 8: WHAT ROTS, WHAT STAYS + title + post-credits."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.gtext import draw_text
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.rust import BaronRust, Iggy
from bl.cast.others import Sela, Bolt, BoltGiant, p_bowl
from . import shot

TEAL, GOLD, ORANGE = "#2cfff0", "#ffd23c", "#ff7a1a"


@shot("e1_rebuild", preview=(1.0, 4.0, 6.5))
def e1_rebuild(sh):
    sets.harbor(sh, "day", stilts=True, horizon=470)
    fx.gulls(sh, 0, sh.end, n=4)
    sets.card(sh.co, "yard_e1", 0.8, lambda pen: pen.fill(geo.rect(-1400, 900, 3400, 1500), "#d8c098"))
    j = sh.rig(Junk, "junk", x=620, y=1000, s=0.9)
    j.show(sh.f(0) - 30, "head", "streak")
    sh.anim(j, [(0, dict(eyes="closed", brows="angry", mouth="grin", hand_f=(140, -560), hand_b=(-120, -560), hf="open", hb="open")),
                (3.0, dict(eyes="happy", lean=-4)), (sh.end, dict(eyes="happy", lean=-6))])
    hk = [(0, 640, 1000, 0, 1.0), (2.5, 640, 520, -6, 1.0), (sh.end, 640, 480, 4, 1.0)]
    house = fx.prop(sh, "liftedhouse", lambda pen: sets.house(pen, 0, 0, 220, 200, "#59c3e8", "#c8432f", seed=7), hk, depth=0.1,
                    fx=[fx.glow_fx(TEAL, 20)])
    g = stage.glow_disc(sh.co, "lift", 640, 500, 400, TEAL, 0.7, depth=0.3)
    bg = sh.rig(BoltGiant, "boltg", x=1400, y=1040, s=0.6, depth=0.2)
    keys = []
    for k, t in enumerate(np.arange(0, sh.end, 0.5)):
        keys.append((t, dict(x=1300 + 40 * t, eyes="googly", bob=-8 if k % 2 else 0, extra=dict(claw=-20, claw_b=20))))
    sh.anim(bg, keys)
    fx.prop(sh, "beam", lambda pen: (pen.shape(geo.rect(-260, -18, 260, 18), "#c8925a", 6, depth=6),
                                      [pen.line([(-200 + k * 80, -18), (-200 + k * 80, 18)], 3) for k in range(6)]),
            [(t, 1310 + 40 * t, 760, 0, 1.0) for t in np.arange(0, sh.end, 0.5)], depth=0.15)
    fx.timer_hud(sh, 0, sh.end, start=17)
    sets.crowd_card(sh, "builders", 0.6, -300, 2200, 1110, n=12, s=1.0, seed=91, cheer=True, rows=1)
    sh.cam.move([(sh.f(0), 900, 600, 1.0), (sh.f(sh.end), 1000, 560, 1.05)])


@shot("e2_paper", preview=(0.4, 2.5))
def e2_paper(sh):
    stage.gradient_bg(sh.co, "bg", [(0.0, "#ffe2b0"), (1.0, "#fff4dc")], depth=40)
    land = sh.cue("land")
    sets.card(sh.co, "bugle2", 0.3, lambda pen: sets.newspaper(pen, "", "", photo="big", x=960, y=560, s=0.62))
    for txt, y, size in (("THE BARNACLE BAY BUGLE", 190, 54), ("JANITOR INNOCENT.", 300, 70), ("CEO GUILTY.", 372, 70)):
        fx.world_text(sh, txt, 960, y, size, col="#1b1424", fname="anton", depth=0.25, ink=None, ow=0.0)
    def portrait(pen):
        from bl import face as F
        P = Iggy()
        s, ox, oy = 0.55, 1110 - 44 * 0.55, 600 + 520 * 0.55
        g = TPen(pen, ox, oy, s)
        P.d_chest(g)
        P.d_head(g)
        h = TPen(pen, ox + 44 * s, oy - 520 * s, 1.1 * s)
        for ex, ey in ((8, -14), (32, -12)):
            F.eye(h, ex, ey, 5.6, "dot", (0.3, 0), 6)
        F.mouth(h, 30, 30, 11, "smile", 0, 5.4)
    sets.card(sh.co, "iggy_photo", 0.29, portrait)
    sh.cam.move([(sh.f(0), 960, 540, 0.6), (sh.f(land), 960, 540, 1.0), (sh.f(sh.end), 1040, 520, 1.18)])
    fx.flash(sh, land, "#ffffff", frames=2, alpha=0.6)


@shot("e3_cell", preview=(1.0, 5.0, 10.0))
def e3_cell(sh):
    def cell(pen):
        pen.fill(geo.rect(-1400, -600, 3400, 1500), "#4a4e5a")
        for k in range(20):
            pen.line([(-1400 + k * 260, -600), (-1400 + k * 260, 1500)], 4, col="#3e4250")
        pen.fill(geo.rect(-1400, 880, 3400, 1500), "#353842")
        pen.shape(geo.rect(560, 760, 1360, 820), "#7a5a3a", 6, depth=10)
        pen.shape(geo.rect(600, 820, 640, 900), "#5a3a2a", 5)
        pen.shape(geo.rect(1280, 820, 1320, 900), "#5a3a2a", 5)
        pen.shape(geo.rect(1500, 160, 1700, 360), "#2a2e3a", 6)
        for k in range(4):
            pen.line([(1520 + k * 50, 160), (1520 + k * 50, 360)], 8, col="#6a6e7a")
    sets.card(sh.co, "cell_bg", 0.6, cell)
    sets.card(sh.co, "cell_bars", -0.6, lambda pen: [pen.line([(-200 + k * 190, -300), (-200 + k * 190, 1400)], 26, col="#2a2e38") for k in range(13)])
    fx.prop(sh, "emptybowl", lambda pen: (pen.shape(geo.blob([(-60, -14), (60, -14), (48, 28), (0, 42), (-48, 28)], n=4), "#f3ead6", 5, hi=0.3),
             pen.line(geo.qbez((-52, 6), (0, 22), (52, 6), 10), 4, "#d84a3a"),
             pen.fill(geo.ellipse(0, -14, 58, 10, 20), "#d8c8b0")),
            [(0, 820, 740, 0, 1.2)], depth=0.5)
    L = [sh.line(k) for k in range(3)]

    def note(pen):
        pen.shape(geo.rect(-150, -100, 150, 100), "#f4f1e6", 4, shade=0.3)
    fx.prop(sh, "note", note, [(0, 1080, 760, -8, 1.0), (L[0][0], 1080, 760, -8, 1.0)], depth=0.48)
    for k, (txt, y) in enumerate((("Thank you for the meal.", 460), ("This isn't over, Tin Can Kid.", 540), ("Not until I decide what I am.", 620))):
        fx.caption(sh, txt, L[k][0], sh.end + 1, x=1020, y=y, size=58, col="#2a2a40", fname="hand", name=f"note{k}", ink=None)
    sh.cam.move([(sh.f(0), 960, 560, 1.0), (sh.f(L[0][0]), 1060, 700, 1.6), (sh.f(L[0][0] + 0.6), 1060, 560, 1.0), (sh.f(sh.end), 1040, 560, 1.05)])
    fx.fade_card(sh, L[0][0] - 0.1, sh.end, "#f4f1e6", 0.9, 0.9, name="paperbg", depth=0.4)


@shot("e4_cliff", preview=(1.0, 4.0, 8.0))
def e4_cliff(sh):
    sets.cliff(sh)
    L = [sh.line(k) for k in range(4)]
    j = sh.rig(Junk, "junk", x=800, y=820, s=0.75)
    j.show(sh.f(0) - 30, "head", "streak")
    j.tint("#ff9a5a", 0.15)
    sh.anim(j, [(0, dict(eyes="dot", mouth="smile", hand_f=(60, -200), hand_b=(-60, -200))),
                (L[1][0], dict(eyes="happy", mouth="grin", head=-4)),
                (L[3][0], dict(eyes="dot", mouth="grin", hand_f=(120, -470), hf="thumb", ease="back")),
                (sh.end, dict(eyes="happy"))])
    sh.lipsync(j, "JUNK", base="grin")
    s = sh.rig(Sela, "sela", x=1020, y=820, s=0.72, face=-1)
    s.tint("#ff9a5a", 0.15)
    sh.anim(s, [(0, dict(eyes="dot", mouth="smirk", hand_f=(60, -200), hf="clipboard", hand_b=(-40, -150))),
                (L[1][1], dict(eyes="half", brows="up", mouth="smile")), (sh.end, dict(eyes="happy", mouth="smile"))])
    sh.lipsync(s, "SELA", base="smirk")
    b = sh.rig(Bolt, "bolt", x=900, y=830, s=1.2)
    sh.anim(b, [(0, dict(eyes="googly")), (L[3][1], dict(eyes="happy"))])
    sh.cam.move([(sh.f(0), 760, 560, 1.15), (sh.f(L[3][0]), 860, 600, 1.2), (sh.f(sh.end), 760, 520, 0.95)])


@shot("e5_rattle", preview=(1.0, 4.0, 6.5))
def e5_rattle(sh):
    sets.rattlecrown(sh)
    slurp = sh.cue("slurp")
    r = sh.rig(BaronRust, "rust", x=960, y=300, s=0.48, depth=14.0)
    r.tint("#1a0c18", 0.55)
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(140, -420), hf="claw", hand_b=(-140, -280))),
                (slurp - 0.6, dict(hand_f=(180, -600), head=10)), (slurp, dict(hand_f=(170, -640), head=14)),
                (slurp + 1.2, dict(hand_f=(140, -420), head=4)), (sh.end, dict(hand_f=(140, -420)))])
    fx.world_text(sh, "slurrrp", 1180, 260, 60, t0=slurp, t1=slurp + 1.6, col="#ffb05a", depth=-0.7, fname="hand")
    sh.cam.move([(sh.f(0), 960, 540, 0.9), (sh.f(sh.end), 1040, 420, 1.5)])


@shot("e6_title", preview=(2.0, 6.0))
def e6_title(sh):
    stage.gradient_bg(sh.co, "black", [(0.0, "#05040a"), (1.0, "#0c0a14")], depth=40)
    g1 = stage.glow_disc(sh.co, "gt", 700, 500, 800, TEAL, 0.6, depth=2.0)
    g2 = stage.glow_disc(sh.co, "go", 1220, 500, 800, ORANGE, 0.6, depth=2.0)
    fx.world_text(sh, "SLUDGE", 700, 560, 230, t0=0.4, col=TEAL, fname="lucky", depth=-0.3)
    fx.world_text(sh, "TIDE", 1290, 560, 230, t0=0.55, col=ORANGE, fname="lucky", depth=-0.3)
    fx.world_text(sh, "WHAT ROTS, WHAT STAYS", 960, 700, 64, t0=1.4, col="#f4f1e6", fname="bangers", depth=-0.3)
    fx.world_text(sh, "drawn and animated in Blender Grease Pencil", 960, 900, 40, t0=2.6, col="#9a96a8", fname="hand", depth=-0.3, ink=None)
    sh.cam.move([(sh.f(0), 960, 560, 1.0), (sh.f(sh.end), 960, 560, 1.06)])
    fx.fade_card(sh, sh.end - 1.0, sh.end, "#000000", 0.0, 1.0)


@shot("e7_post", preview=(2.0, 5.0, 8.0))
def e7_post(sh):
    sets.deepsea(sh)
    cracks = sh.cue("crack")
    cols = ["#3a8aff", "#ff3a3a", "#ffd23c", "#3a8aff"]
    xs = [560, 860, 1160, 1420]
    for k, (t, x, c) in enumerate(zip(cracks, xs, cols)):
        def barrel(pen, c=c, cracked=False):
            sets.barrels(pen, 0, 0, n=1, cracked=cracked, seed=10 + k, glow=c)
        b0 = fx.prop(sh, f"barrel{k}", (lambda cc: (lambda pen: sets.barrels(pen, 55, 0, n=1, cracked=False, seed=10)))(c), [(0, x, 900, 0, 1.2)], depth=0.5)
        b1 = fx.prop(sh, f"barrelc{k}", (lambda cc: (lambda pen: sets.barrels(pen, 55, 0, n=1, cracked=True, seed=10, glow=cc)))(c), [(0, x, 900, 0, 1.2)], depth=0.49,
                     fx=[fx.glow_fx(c, 30)])
        fx.vis(b0, None, t, sh)
        fx.vis(b1, t, None, sh)
        g = stage.glow_disc(sh.co, f"bg{k}", x, 800, 380, c, 0.0, depth=1.0)
        stage.key_strength(g, sh.f(t), 0.0)
        stage.key_strength(g, sh.f(t + 0.3), 1.2)
        stage.key_strength(g, sh.f(sh.end), 0.9)
        fx.world_text(sh, "crk", x + 60, 700, 50, t0=t, t1=t + 0.8, col=c, depth=-0.5, fname="hand")
    fx.bubbles(sh, 400, 1600, 820, 920, 2.8, sh.end, n=30, col="#9ab8ff", depth=0.4, rise=400, size=1.4)
    sh.cam.move([(sh.f(0), 960, 600, 1.2), (sh.f(sh.end), 960, 640, 1.0)])
    fx.fade_card(sh, sh.end - 1.2, sh.end, "#000000", 0.0, 1.0)
