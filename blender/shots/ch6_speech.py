"""CHAPTER 6: THREE DAYS."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.gtext import draw_text
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.others import Granny, Sela
from . import shot

TEAL, GOLD, ORANGE, PURPLE = "#2cfff0", "#ffd23c", "#ff7a1a", "#7a3cb4"
CHALK = "#f2f4ee"


def chalkboard(sh, t_marks):
    """Sela's chalkboard, drawn stroke by stroke as she explains."""
    def board(pen):
        pen.shape(geo.rect(330, 120, 1590, 760), "#5a3a22", 10, shade=0.3)
        pen.fill(geo.rect(360, 150, 1560, 730), "#24382c")
    sets.card(sh.co, "board", 0.5, board)
    items = []
    # left: a little figure falling into the vat, rage -> rot
    items.append(lambda pen: (pen.line(geo.ellipse(620, 560, 160, 40, 30), 5, CHALK, closed=True),
                              pen.line([(460, 560), (480, 700), (760, 700), (780, 560)], 5, CHALK)))
    items.append(lambda pen: (pen.line(geo.circle(620, 300, 30, 20), 5, ORANGE, closed=True), pen.line([(620, 330), (620, 420)], 5, ORANGE),
                              pen.line([(570, 360), (670, 360)], 5, ORANGE), pen.line([(620, 420), (580, 480)], 5, ORANGE),
                              pen.line([(620, 420), (660, 480)], 5, ORANGE), draw_text(pen, "ANGER", 620, 240, 54, ORANGE, None, fname="hand")))
    items.append(lambda pen: (pen.line([(800, 400), (900, 400)], 6, CHALK), pen.line([(880, 380), (900, 400), (880, 420)], 6, CHALK),
                              draw_text(pen, "ROT", 1000, 420, 80, ORANGE, None, fname="hand")))
    items.append(lambda pen: (pen.line(geo.circle(1260, 300, 30, 20), 5, TEAL, closed=True), pen.line([(1260, 330), (1260, 420)], 5, TEAL),
                              pen.line([(1210, 360), (1310, 360)], 5, TEAL), draw_text(pen, "HOPE", 1260, 240, 54, TEAL, None, fname="hand"),
                              pen.line(geo.ellipse(1260, 560, 160, 40, 30), 5, CHALK, closed=True)))
    items.append(lambda pen: (pen.line([(1120, 640), (1000, 640)], 6, CHALK), draw_text(pen, "BUILD", 1000, 690, 70, TEAL, None, fname="hand")))
    items.append(lambda pen: (draw_text(pen, "SAME POWER. FLIPPED.", 960, 210, 64, GOLD, None, fname="hand"),
                              pen.line([(560, 222), (1360, 222)], 4, GOLD)))
    d = {}
    for f in range(sh.f(t_marks[0]), sh.f(sh.end) + 1, 2):
        t = sh.t(f)
        n = sum(1 for tm in t_marks if t >= tm)
        d[f] = (lambda nn: (lambda pen: [items[i](pen) for i in range(nn)]))(n)
    fx.fxcard(sh, "chalk", 0.45, d)


@shot("p1_theory", preview=(2.0, 6.0, 11.5))
def p1_theory(sh):
    sets.noodle_interior(sh)
    L = [sh.line(k) for k in range(4)]
    chalkboard(sh, [0.4, L[0][0] + 1.5, L[0][0] + 2.6, L[1][0] + 1.6, L[1][0] + 2.6, L[2][0]])
    s = sh.rig(Sela, "sela", x=1500, y=1060, s=1.0, face=-1)
    sh.anim(s, [(0, dict(eyes="dot", brows="neutral", mouth="flat", hand_f=(160, -420), hf="point", hand_b=(-30, -150), hb="clipboard")),
                (L[0][0] + 1.5, dict(hand_f=(260, -500))), (L[1][0], dict(hand_f=(180, -460), eyes="half")),
                (L[1][0] + 1.6, dict(hand_f=(200, -380), eyes="dot")),
                (L[2][0], dict(hand_f=(300, -560), brows="up", eyes="dot", ease="back")),
                (L[3][0], dict(hand_f=(60, -260), hf="open", brows="worried", eyes="dot", face=-1)),
                (sh.end, dict(brows="worried"))])
    sh.lipsync(s, "SELA", base="flat")
    s.show(sh.f(0) - 30, "head", "lenses")
    s.show(sh.f(L[1][0]), "head", "lenses", False)
    j = sh.rig(Junk, "junk", x=420, y=1060, s=0.95)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    sh.anim(j, [(0, dict(eyes="dot", brows="up", mouth="o", hand_f=(60, -200), hand_b=(-40, -200))),
                (L[3][0] - 0.6, dict(eyes="down", brows="worried", mouth="frown", head=20, hand_f=(120, -300), hand_b=(90, -310), hf="open", hb="open")),
                (sh.end, dict(eyes="sad", head=22))])
    sh.lipsync(j, "JUNK", base="frown")
    sh.cam.move([(sh.f(0), 960, 540, 1.0), (sh.f(L[3][0] - 0.5), 960, 520, 1.0), (sh.f(L[3][0]), 520, 560, 1.4), (sh.f(sh.end), 500, 560, 1.45)])


def boat_edge(sh):
    def edge(pen):
        pen.shape(geo.rect(-1500, 900, 3400, 1500), "#6a4028", 8, depth=20)
        pen.fill(geo.rect(-1500, 900, 3400, 930), "#8a5a3a")
        for k in range(30):
            pen.line([(-1500 + k * 170, 930), (-1500 + k * 170, 1500)], 4, col="#4a2c1a")
        for x in (-300, 700, 1700):
            pen.shape(geo.ellipse(x, 860, 22, 28, 18), "#ff5a3a", 4, hi=0.4)
            pen.fill(geo.circle(x, 860, 60), "#ffb060", 0.3)
    sets.card(sh.co, "boatedge", 0.2, edge)


@shot("p2_granny", preview=(2.0, 6.0, 10.0, 14.0))
def p2_granny(sh):
    sets.stilts_view(sh, mood="night")
    fx.fog(sh, "mist", 600, 900, 6, col="#3a4a7a", alpha=0.3, seed=4)
    boat_edge(sh)
    L = [sh.line(k) for k in range(4)]
    g = sh.rig(Granny, "granny", x=760, y=930, s=0.95, depth=-0.05)
    sh.anim(g, [(0, dict(eyes="dot", brows="neutral", mouth="flat", head=-14, hand_f=(120, -120), hand_b=(-110, -80))),
                (L[0][0], dict(head=-6)),
                (L[1][0], dict(head=0, hand_f=(200, -300), hf="open")),
                (L[2][0] - 0.3, dict(head=10, hand_f=(140, -160), hf="fist", eyes="dot", brows="worried")),
                (L[3][0], dict(head=6, eyes="half", brows="neutral", hand_f=(220, -230), hf="point")),
                (sh.end, dict(eyes="dot", mouth="smile"))])
    sh.lipsync(g, "GRANNY", base="flat")
    sh.blink(g, [3.4, 9.0])
    j = sh.rig(Junk, "junk", x=1150, y=1120, s=0.95, face=-1, depth=-0.05)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    sh.anim(j, [(0, dict(eyes="down", brows="worried", mouth="frown", head=14, foot_f=(80, -40), foot_b=(30, -20), hand_f=(90, -230), hand_b=(50, -220))),
                (L[0][0] + 1.0, dict(eyes="dot", head=0)),
                (L[2][0], dict(eyes="up", brows="worried", head=-10)),
                (L[3][1], dict(eyes="dot", brows="up", mouth="o", head=-4)),
                (sh.end, dict(eyes="dot", brows="up"))])
    sh.blink(j, [5.0, 11.5])
    sh.cam.move([(sh.f(0), 960, 360, 1.0), (sh.f(L[1][0]), 960, 620, 1.0), (sh.f(L[2][0]), 900, 640, 1.2), (sh.f(sh.end), 920, 640, 1.38)])


@shot("p3_faster", preview=(1.0, 4.0, 5.6))
def p3_faster(sh):
    sets.stilts_view(sh, mood="night")
    boat_edge(sh)
    L = [sh.line(k) for k in range(2)]
    bonk = L[1][1] + 0.35
    j = sh.rig(Junk, "junk", x=1100, y=1140, s=1.05, face=-1)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    sh.anim(j, [(0, dict(eyes="up", brows="up", mouth="o", head=-4, foot_f=(80, -40), foot_b=(30, -20), hand_f=(90, -230), hand_b=(50, -220))),
                (L[1][0] - 0.2, dict(foot_f=(20, -8), foot_b=(-30, -8), y=920, eyes="dot", brows="angry", mouth="grin", hand_f=(160, -520), hf="fist", ease="back")),
                (bonk, dict(eyes="x", mouth="o", sq=0.85, ease="snap")),
                (bonk + 0.3, dict(sq=1.0, eyes="happy", mouth="grin")),
                (sh.end, dict(eyes="happy"))])
    sh.lipsync(j, "JUNK", base="grin")
    j.tint(TEAL, 0.0, f=sh.f(L[1][0] - 0.3))
    j.tint(TEAL, 0.2, f=sh.f(L[1][0]))
    g = sh.rig(Granny, "granny", x=720, y=930, s=0.95)
    sh.anim(g, [(0, dict(eyes="dot", mouth="smile", hand_f=(140, -200), hf="ladle")),
                (bonk - 0.3, dict(hand_f=(150, -480), lean=-4)),
                (bonk, dict(hand_f=(320, -440), lean=8, ease="snap")),
                (sh.end, dict(eyes="happy", mouth="smile", hand_f=(220, -300)))])
    g.show(sh.f(bonk + 0.2), "head", "blush")
    fx.world_text(sh, "bonk.", 980, 330, 110, t0=bonk, t1=sh.end, col="#ffb0c0", depth=-0.8, rot=-0.15)
    fx.burst(sh, 1050, 430, bonk, col="#ffb0c0", r1=150, seed=6)
    fx.speedlines(sh, L[1][0], bonk - 0.05, 1100, 400, TEAL, inner=330, n=50, seed=8, alpha=0.6)
    sh.cam.move([(sh.f(0), 960, 600, 1.15), (sh.f(L[1][0]), 1040, 480, 1.25), (sh.f(bonk), 960, 560, 1.1), (sh.f(sh.end), 960, 560, 1.12)])


@shot("p4_stay", preview=(1.5, 4.0, 6.8))
def p4_stay(sh):
    sets.stilts_view(sh, mood="day")
    fx.gulls(sh, 0, sh.end, n=4, y=150)
    mtn = sets.card(sh.co, "scrap_mtn_grow", 1.0, lambda pen: sets.scrap_mountain_draw(pen, 960, 980, w=1100, h=480))
    k0 = mtn.scale[0]
    mtn.scale = (k0, k0, k0 * 0.25)
    mtn.keyframe_insert("scale", frame=sh.f(0))
    mtn.scale = (k0, k0, k0)
    mtn.keyframe_insert("scale", frame=sh.f(sh.end))
    for side, (x0, x1, seed) in enumerate(((-500, 520, 1), (2400, 1400, 2))):
        for k in range(3):
            c = sets.crowd_card(sh, f"carry{side}{k}", -0.2 - 0.1 * k, -200, 400, 1120, n=3, s=1.1, seed=seed * 10 + k, cheer=True, rows=1)
            st = 0.6 * k
            c.location.x = (x0 - 100) * gp.PX
            c.keyframe_insert("location", frame=sh.f(st))
            c.location.x = (x1 - 100 + (k * 80 if side == 0 else -k * 80)) * gp.PX
            c.keyframe_insert("location", frame=sh.f(st + 5.0))
            for kind in (5, 3, 6):
                pass
    for k, (kind, x0, x1, t0) in enumerate(((5, -300, 600, 0.3), (3, 2300, 1300, 0.8), (7, -400, 760, 1.4), (6, 2400, 1200, 2.0), (9, -300, 880, 2.6))):
        o = fx.prop(sh, f"carried{k}", (lambda kk: (lambda pen: sets.scrap_piece(pen, 0, 0, 1.8, kind=kk, seed=kk)))(kind),
                    [(t0, x0, 860 - (k % 2) * 40, 0, 1.0), (t0 + 5.0, x1, 860 - (k % 2) * 40, 0, 1.0)], depth=-0.25)
    piano = fx.prop(sh, "piano", lambda pen: (pen.shape(geo.rect(-150, -120, 150, 60), "#1e1a22", 6, hi=0.4),
                                               pen.shape(geo.rect(-140, -20, 140, 10), "#f4f1e6", 4, shade=0),
                                               [pen.line([(-140 + k * 20, -20), (-140 + k * 20, 10)], 2) for k in range(15)]),
                    [(1.0, 2400, 900, 0, 1.0), (sh.end, 1500, 900, -3, 1.0)], depth=-0.3)
    fx.caption(sh, "DAY THREE", 0.4, 3.0, y=990, size=84, col="#ffffff")
    sh.cam.move([(sh.f(0), 960, 600, 1.05), (sh.f(sh.end), 960, 540, 0.95)])
