"""COLD OPEN + CHAPTER 1: THE NIGHT SHIFT."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys, rest_hands
from bl.cast.rust import Iggy
from bl.cast.others import Magnus, Guard, Granny, p_paper
from . import shot

GREEN, ORANGE, TEAL = "#5dff7a", "#ff8a1e", "#2cfff0"
NIGHT = "#2a3470"


# ---------------------------------------------------------------------------- cold open
@shot("o1_drip", preview=(1.0, 2.5, 4.0))
def o1_drip(sh):
    stage.gradient_bg(sh.co, "black", [(0.0, "#05040a"), (1.0, "#0a0812")], depth=40)
    hit = sh.cue("hit")
    d = {}
    for f in range(sh.f(0.6), sh.f(hit) + 1):
        u = min(1.0, max(0.0, (sh.t(f) - 0.6) / (hit - 0.6)))
        y = -60 + 560 * u ** 2.2

        def draw(pen, y=y, u=u):
            L = 30 + 80 * u
            pen.shape(geo.blob([(960, y - L), (972, y - 10), (976, y + 8), (960, y + 22), (944, y + 8), (948, y - 10)], n=3),
                      GREEN, 4, shade=0.0, hi=0.6)
            pen.fill(geo.ellipse(960, y + 12, 9, 7, 12), ORANGE)
        d[f] = draw
    d[sh.f(hit) + 1] = None
    fx.fxcard(sh, "drip", -0.5, d, fx=[fx.glow_fx(GREEN, 40)])
    fx.splash(sh, 960, 520, hit, s=0.9, col=GREEN, seed=2)
    fx.flash(sh, hit, "#c8ffd8", frames=2)
    g1 = stage.glow_disc(sh.co, "glow_t", 700, 560, 700, TEAL, 0.0, depth=1.0)
    g2 = stage.glow_disc(sh.co, "glow_o", 1220, 560, 700, ORANGE, 0.0, depth=1.0)
    for g in (g1, g2):
        stage.key_strength(g, sh.f(hit), 0.0)
        stage.key_strength(g, sh.f(hit + 0.4), 0.9)
        stage.key_strength(g, sh.f(6.8), 0.7)
        stage.key_strength(g, sh.f(7.6), 0.0)
    a = fx.world_text(sh, "SLUDGE", 700, 640, 250, t0=sh.cue("title"), col=TEAL, fname="lucky", depth=-0.3)
    b = fx.world_text(sh, "TIDE", 1290, 640, 250, t0=sh.cue("title") + 0.15, col=ORANGE, fname="lucky", depth=-0.3)
    # drips sliding down the letters
    dd = {}
    for f in range(sh.f(3.0), sh.f(7.6), 2):
        u = (sh.t(f) - 3.0) / 4.6

        def draw(pen, u=u):
            for k, (x, c) in enumerate(((560, TEAL), (840, TEAL), (1180, ORANGE), (1400, ORANGE))):
                L = 40 + 120 * min(1, u * (1.2 + k * 0.2))
                pen.tube([(x, 650), (x + 2, 650 + L)], 14, c, 3, shade=0.2)
                pen.shape(geo.circle(x + 2, 660 + L, 12), c, 3, shade=0.2)
        dd[f] = draw
    fx.fxcard(sh, "letterdrips", -0.4, dd, fx=[fx.glow_fx(TEAL, 18)])
    sh.cam.move([(sh.f(0), 960, 540, 1.0), (sh.f(hit), 960, 540, 1.0), (sh.f(hit + 0.1), 960, 540, 1.08), (sh.f(7.6), 960, 545, 1.14)])
    sh.cam.shake(sh.f(hit), sh.f(hit + 0.6), 18, 0.4)
    fx.fade_card(sh, sh.cue("out"), 8.0, "#000000", 0.0, 1.0)


# ---------------------------------------------------------------------------- 1. the night shift
@shot("n1_isle", preview=(2.0,))
def n1_isle(sh):
    sets.gloam_isle_night(sh)
    fx.caption(sh, "GLOAMWORKS ISLE  -  3:00 A.M.", 0.6, 4.6, y=990, size=76, col="#e8e0ff")
    sh.cam.move([(sh.f(0), 880, 540, 1.0), (sh.f(sh.end), 1040, 520, 1.08)])


@shot("n2_hall", preview=(2.0, 8.0, 10.5))
def n2_hall(sh):
    sets.hallway(sh)
    P = None
    r = sh.rig(Iggy, "iggy", x=200, y=1000, s=0.95)
    P = r.p
    r.tint(NIGHT, 0.22)
    door = sh.cue("door")
    l2s, l2e = sh.line(2)
    base = dict(lean=10, head=6, eyes="tired", brows="worried", mouth="flat", hf="mop", hb="open", s=0.95)
    keys = walk_keys(P, 0.0, l2s + 0.2, 200, 900, base=dict(base, hand_f=(80, -250)), step=0.55, lift=14, bob=4, swing=10)
    keys += [(l2s + 0.6, dict(base, x=900, lean=16, head=14, chest=6, eyes="closed", foot_f=(18, -10), foot_b=(-18, -10), hand_f=(70, -240))),
             (door - 0.2, dict(base, x=900, lean=14, head=10, eyes="tired")),
             (door + 0.5, dict(base, x=900, lean=4, head=-4, eyes="ahead", brows="up", mouth="o", ease="snap")),
             (sh.end, dict(base, x=930, lean=2, head=-6, eyes="ahead", brows="up", mouth="o"))]
    sh.anim(r, keys)
    sh.lipsync(r, "IGGY", base="flat")
    sh.blink(r, [1.5, 4.2])
    # the green-orange light spilling from the door
    g = stage.glow_disc(sh.co, "doorglow", 1510, 520, 520, GREEN, 0.0, depth=0.5)
    stage.key_strength(g, sh.f(door - 0.6), 0.0)
    stage.key_strength(g, sh.f(door + 0.6), 1.2)
    d = {}
    for f in range(sh.f(door - 0.6), sh.f(sh.end) + 1, 2):
        u = min(1, (sh.t(f) - door + 0.6) / 1.2)

        def draw(pen, u=u):
            pen.fill(np.array([(1404, 760), (1620, 760), (1400 + 260 * u, 1080), (1100 - 300 * u, 1080)]), GREEN, 0.35 * u)
            pen.fill(geo.rect(1404, 270, 1420, 760), ORANGE, 0.9 * u)
            pen.fill(geo.rect(1420, 270, 1440, 760), GREEN, 0.8 * u)
        d[f] = draw
    fx.fxcard(sh, "doorlight", 0.3, d, fx=[fx.glow_fx(GREEN, 30)])
    r.tint("#5dff7a", 0.0, f=sh.f(door - 0.4))
    r.tint("#5dff7a", 0.28, f=sh.f(door + 0.8))
    sh.cam.move([(sh.f(0), 700, 560, 1.0), (sh.f(l2s), 980, 560, 1.0), (sh.f(door), 1000, 560, 1.0), (sh.f(sh.end), 1240, 520, 1.25)])
    fx.world_text(sh, "SQUEAK", 330, 980, 40, t0=0.6, t1=1.4, col="#ffe9a0", depth=-0.6, rot=-0.2)
    fx.world_text(sh, "SQUEAK", 640, 990, 40, t0=1.8, t1=2.6, col="#ffe9a0", depth=-0.6, rot=0.15)


def vat_card(sh, name, col_top, col_bot, depth=6.0):
    def draw(pen):
        sets.vat(pen, 760, 700, 980, col_top, col_bot)
    return sets.card(sh.co, name, depth, draw)


@shot("n3_vat", preview=(1.0, 5.0))
def n3_vat(sh):
    sets.vat_room(sh)
    v = vat_card(sh, "vat_green", GREEN, ORANGE)
    v.shader_effects.new("glow", "FX_GLOW")
    v.shader_effects["glow"].mode = "COLOR"
    v.shader_effects["glow"].select_color = gp.to_linear(gp.rgb(GREEN))
    v.shader_effects["glow"].glow_color = gp.to_linear(gp.rgb(GREEN))
    v.shader_effects["glow"].size = (60, 60)
    stage.glow_disc(sh.co, "vatglow", 760, 640, 900, GREEN, 0.9, depth=5.0)
    fx.bubbles(sh, 380, 1140, 620, 700, 0, sh.end, n=30, col="#c8ffd0", depth=5.5, rise=120, size=1.6, glow=GREEN)

    def boat(pen):
        g = TPen(pen, 1620, 760, 1.0)
        g.shape(geo.blob([(-300, -80), (320, -80), (280, 60), (-260, 70)], n=3, tension=0.25), "#3a3a44", 5, depth=20)
        for k in range(4):
            for j in range(2):
                g.shape(geo.rrect(-240 + k * 110, -200 - j * 110, -160 + k * 110, -86 - j * 110, 10), "#7a7a3a", 4, depth=8)
                g.fill(geo.circle(-200 + k * 110, -143 - j * 110, 14), "#ffd23c")
        g.fill(geo.rect(-280, -50, 260, 10), "#4a4a56")
    sets.card(sh.co, "darkboat", 8, boat)
    t = fx.world_text(sh, "GRAVEYARD SHELF", 1620, 790, 46, col="#c8c0b0", fname="anton", depth=7.9, ow=0.0, ink=None)
    pc = {sh.f(0): lambda pen: [pen.fill(geo.rect(1400 + k * 80, 750 + (k % 3) * 6, 1440 + k * 80, 790 - (k % 2) * 8), "#22222a", 0.8) for k in range(6)]}
    fx.fxcard(sh, "paintover", 7.8, pc)
    r = sh.rig(Iggy, "iggy", x=150, y=930, s=0.5, depth=2.0)
    r.tint(GREEN, 0.16)
    sh.anim(r, [(0, dict(x=120, lean=4, head=-6, eyes="huge", brows="up", mouth="o", hf="mop", hand_f=(60, -250), hand_b=(-40, -230))),
                (2.0, dict(x=140)), (sh.end, dict(x=150, head=4, eyes="dot", brows="worried", mouth="frown"))])
    sh.lipsync(r, "IGGY", base="frown")
    sh.cam.move([(sh.f(0), 760, 520, 1.0), (sh.f(sh.end), 1200, 560, 1.06)])


@shot("n4_phone", preview=(1.0, 3.0))
def n4_phone(sh):
    stage.gradient_bg(sh.co, "dark", [(0.0, "#0c2a18"), (1.0, "#14101e")], depth=40)
    stage.glow_disc(sh.co, "g", 1500, 900, 1200, GREEN, 0.8, depth=10)
    fx.bubbles(sh, 0, 1920, 700, 1100, 0, sh.end, n=18, col="#b8ffc8", depth=8, rise=300, size=2.0, glow=GREEN)
    r = sh.rig(Iggy, "iggy", x=760, y=1480, s=1.9)
    r.tint(GREEN, 0.2)
    m = sh.line(0)[0]
    sh.anim(r, [(0, dict(lean=6, head=4, eyes="dot", brows="worried", mouth="frown", hand_f=(40, -230), hand_b=(-40, -220), hf="open")),
                (0.6, dict(hand_f=(120, -470), hf="phone", ease="snap")),
                (sh.cue("click") + 0.4, dict(hand_f=(122, -474))),
                (m + 0.05, dict(eyes="dot")),
                (m + 0.3, dict(eyes="shock", brows="high", mouth="o", head=-8, ease="snap")),
                (sh.end, dict(eyes="shock", head=-10))])
    r.show(sh.f(m + 0.6), "head", "sweat")
    fx.flash(sh, sh.cue("click"), "#ffffff", frames=2, alpha=0.6)
    fx.world_text(sh, "CLICK", 1250, 360, 70, t0=sh.cue("click"), t1=sh.cue("click") + 0.6, col="#ffffff", depth=-1.0)
    fx.speedlines(sh, m + 0.3, sh.end, 900, 400, "#ffffff", inner=420, n=50, seed=3, alpha=0.5)
    sh.cam.move([(sh.f(0), 900, 520, 1.0), (sh.f(m + 0.3), 900, 520, 1.0), (sh.f(m + 0.4), 860, 500, 1.18), (sh.f(sh.end), 850, 495, 1.22)])


def magnus_smoke(sh, r, t0, t1, every=0.45):
    # chimney top in home px (approx: hat chimney above head)
    x, y = r.base["x"], r.base["y"]
    s = r.base["s"]
    face = r.base["face"]
    fx.smoke(sh, x + face * 9 * s, y - 590 * s, t0, t1, col="#9a5ad0", every=every, depth=-0.2, rise=180 * s, size=0.7 * s)


@shot("n5_magnus", preview=(1.0, 4.0))
def n5_magnus(sh):
    stage.gradient_bg(sh.co, "dark", [(0.0, "#2a1a10"), (0.5, "#1a1424"), (1.0, "#0c0a14")], depth=40)
    stage.glow_disc(sh.co, "under", 960, 1100, 1000, ORANGE, 0.9, depth=6)
    for i, x in enumerate((420, 1500)):
        g = sh.rig(Guard, f"guard{i}", x=x, y=1150, s=1.05, face=1 if i == 0 else -1, depth=3)
        g.tint("#140c1c", 0.7)
        sh.anim(g, [(0, dict(hand_f=(110, -240), hand_b=(-100, -240)))])
    r = sh.rig(Magnus, "magnus", x=960, y=1180, s=1.5)
    r.tint(ORANGE, 0.18)
    l0, l1 = sh.line(0), sh.line(1)
    sh.anim(r, [(0, dict(lean=0, eyes="dot", brows="neutral", mouth="grin", hand_f=(200, -150), hand_b=(-200, -150))),
                (l0[0], dict(lean=6, head=8, eyes="half", brows="angry", hand_f=(150, -260), hf="point")),
                (l1[0], dict(lean=-2, head=-4, eyes="dot", brows="up", hand_f=(230, -300), hf="open", ease="back")),
                (sh.end, dict(lean=-3))])
    sh.lipsync(r, "MAGNUS", base="grin", shapes=("t1", "t2", "t3"))
    magnus_smoke(sh, r, sh.cue("puff"), sh.end)
    sh.cam.move([(sh.f(0), 960, 760, 1.0), (sh.f(sh.end), 960, 640, 1.12)])


def walkway(sh, depth=0.0):
    def draw(pen):
        pen.fill(geo.rect(-1400, 900, 3400, 960), "#4a4e5e")
        pen.line([(-1400, 900), (3400, 900)], 5)
        pen.line([(-1400, 960), (3400, 960)], 5)
        pen.line([(-1400, 760), (3400, 760)], 8, col="#6a6e80")
        for k in range(30):
            x = -1400 + k * 160
            pen.line([(x, 760), (x, 900)], 6, col="#5a5e70")
        pen.line([(-1400, 760), (3400, 760)], 3)
    return sets.card(sh.co, "walkway", depth, draw)


@shot("n6_frame", preview=(2.0, 7.0))
def n6_frame(sh):
    stage.gradient_bg(sh.co, "dark", [(0.0, "#3a2a10"), (0.4, "#1a1820"), (1.0, "#0c0a14")], depth=40)
    stage.glow_disc(sh.co, "vatglow", 960, 1300, 1400, GREEN, 0.9, depth=8)
    fx.bubbles(sh, 0, 1920, 1000, 1150, 0, sh.end, n=16, col="#b8ffc8", depth=6, rise=200, size=2.0, glow=GREEN)
    walkway(sh, 0.4)
    m = sh.rig(Magnus, "magnus", x=520, y=930, s=0.95)
    i = sh.rig(Iggy, "iggy", x=1300, y=930, s=0.95, face=-1)
    for r in (m, i):
        r.tint(GREEN, 0.25)
    L = [sh.line(k) for k in range(3)]
    sh.anim(m, [(0, dict(mouth="grin", eyes="dot", brows="neutral", hand_f=(190, -170), hand_b=(-190, -150))),
                (L[0][0], dict(hand_f=(230, -300), hf="open", lean=4)),
                (L[1][0], dict(hand_f=(260, -250), hf="point", lean=10, head=6, ease="snap")),
                (L[1][1], dict(lean=6)),
                (sh.end, dict(hand_f=(200, -220), hf="open"))])
    sh.lipsync(m, "MAGNUS", base="grin")
    sh.anim(i, [(0, dict(lean=12, head=8, eyes="dot", brows="worried", mouth="frown", hf="mop", hand_f=(60, -250), hand_b=(-40, -230))),
                (L[1][0] + 1.0, dict(lean=4, head=-2, eyes="huge", brows="high", mouth="o", ease="snap")),
                (L[2][0], dict(lean=-6, head=-8, eyes="dot", brows="worried", hand_b=(80, -380), hb="open")),
                (sh.end, dict(lean=-8, head=-10))])
    sh.lipsync(i, "IGGY", base="frown")
    i.show(sh.f(L[1][0] + 1.0), "head", "sweat")
    sh.cam.move([(sh.f(0), 960, 620, 1.0), (sh.f(L[2][0]), 1040, 600, 1.06), (sh.f(sh.end), 1180, 560, 1.2)])


@shot("n7_willhave", preview=(1.0, 3.2))
def n7_willhave(sh):
    stage.gradient_bg(sh.co, "dark", [(0.0, "#2a1a10"), (1.0, "#0c0a14")], depth=40)
    stage.glow_disc(sh.co, "under", 960, 1200, 1100, ORANGE, 0.8, depth=6)
    r = sh.rig(Magnus, "magnus", x=900, y=1560, s=2.5)
    r.tint(ORANGE, 0.15)
    l1 = sh.line(1)
    sh.anim(r, [(0, dict(eyes="happy", brows="neutral", mouth="grin", hand_f=(200, -150), hand_b=(-200, -150), head=-4)),
                (l1[0] - 0.2, dict(eyes="half", brows="angry", head=4, ease="snap")),
                (sh.end, dict(head=5))])
    sh.lipsync(r, "MAGNUS", base="grin")
    magnus_smoke(sh, r, l1[0], sh.end, every=0.3)
    sh.cam.move([(sh.f(0), 960, 500, 1.0), (sh.f(sh.end), 980, 480, 1.18)])


@shot("n8_struggle", preview=(0.5, 1.6, 3.0))
def n8_struggle(sh):
    stage.gradient_bg(sh.co, "dark", [(0.0, "#123018"), (1.0, "#0c0a14")], depth=40)
    stage.glow_disc(sh.co, "vatglow", 960, 1300, 1400, GREEN, 1.0, depth=8)
    walkway(sh, 0.4)
    i = sh.rig(Iggy, "iggy", x=960, y=930, s=0.95)
    g1 = sh.rig(Guard, "g1", x=620, y=930, s=0.85, depth=0.1)
    g2 = sh.rig(Guard, "g2", x=1320, y=930, s=0.85, face=-1, depth=0.1)
    for r in (i, g1, g2):
        r.tint(GREEN, 0.3)
    grab, snap, slip = sh.cue("grab"), sh.cue("snap"), sh.cue("slip")
    sh.anim(i, [(0, dict(eyes="shock", brows="high", mouth="o", hf="mop", hand_f=(60, -260), hand_b=(-40, -240), lean=0)),
                (grab, dict(lean=-6, hand_b=(-120, -420), hb="open", mouth="shout")),
                (grab + 0.4, dict(lean=8, x=950)), (grab + 0.8, dict(lean=-8, x=975)), (snap - 0.1, dict(lean=6, x=955)),
                (snap, dict(hf="fist", hand_f=(120, -300), ease="snap")),
                (slip, dict(lean=-4, x=960)),
                (slip + 0.4, dict(lean=-28, x=990, foot_f=(80, -60), eyes="huge", ease="in")),
                (sh.end, dict(lean=-40, x=1010, foot_f=(120, -120), foot_b=(-10, -10)))])
    for g, side in ((g1, 1), (g2, 1)):
        sh.anim(g, [(0, dict(hand_f=(110, -250), hand_b=(-100, -250), mouth="flat")),
                    (grab, dict(hand_f=(260, -380), hf="grab", lean=14, ease="snap")),
                    (snap, dict(lean=4, hand_f=(220, -340))), (sh.end, dict(lean=-10, hand_f=(260, -450), hf="open"))])
    fx.speedlines(sh, grab, slip, 960, 520, "#ffffff", inner=360, n=40, seed=8, alpha=0.4)
    fx.burst(sh, 1080, 660, snap, col="#ffd23c", seed=4)
    fx.world_text(sh, "SNAP!", 1180, 560, 90, t0=snap, t1=snap + 0.8, col="#ffd23c", depth=-0.8, rot=0.15)
    pieces = {}
    for f in range(sh.f(snap), sh.f(snap + 1.6), 2):
        u = (sh.t(f) - snap) / 1.6

        def draw(pen, u=u):
            for k, (vx, vy, sp) in enumerate(((300, -500, 8), (-200, -420, -6))):
                x, y = 1080 + vx * u, 640 + vy * u + 1400 * u * u
                g = TPen(pen, x, y, 1.0, sp * u)
                g.line([(-60, 0), (60, 0)], 12, col="#8a6a44")
                g.line([(-60, 0), (60, 0)], 3)
        pieces[f] = draw
    pieces[sh.f(snap + 1.6)] = None
    fx.fxcard(sh, "mopbits", -0.5, pieces)
    sh.cam.shake(sh.f(grab), sh.f(sh.end), 14, 0.35)
    sh.cam.move([(sh.f(0), 960, 600, 1.05), (sh.f(sh.end), 980, 620, 1.15)])


def fall_frame(sh, who="iggy"):
    """The mirrored signature shot: the same camera, the same slow-motion timing for both falls."""
    pass


@shot("n9_fall", preview=(2.0, 5.0, 7.5, 9.5))
def n9_fall(sh):
    stage.gradient_bg(sh.co, "pit", [(0.0, "#a8ff60"), (0.25, "#2a6a2a"), (0.6, "#101418"), (1.0, "#08060c")], depth=30)
    stage.glow_disc(sh.co, "below", 960, 1300, 1500, GREEN, 1.2, depth=4)
    fx.bubbles(sh, 0, 1920, 900, 1200, 0, sh.end, n=40, col="#c8ffd0", depth=2, rise=500, size=2.4, glow=GREEN)

    def rail(pen):
        pen.fill(geo.rect(-600, 330, 2600, 400), "#4a4e5e")
        pen.line([(-600, 330), (2600, 330)], 6)
        pen.line([(-600, 400), (2600, 400)], 6)
        pen.line([(-600, 200), (2600, 200)], 8, col="#6a6e80")
        for k in range(20):
            pen.line([(-600 + k * 180, 200), (-600 + k * 180, 330)], 8, col="#5a5e70")
    sets.card(sh.co, "rail_top", 0.8, rail)
    sets.card(sh.co, "goo_surface", 2.0, lambda pen: (pen.fill(geo.ellipse(960, 1180, 1500, 160, 60), ORANGE),
                                                       pen.fill(geo.ellipse(960, 1170, 1460, 140, 60), GREEN)), )
    m = sh.rig(Magnus, "magnus", x=1240, y=340, s=0.6, face=-1, depth=0.6)
    m.tint(GREEN, 0.35)
    sh.anim(m, [(0, dict(mouth="grin", eyes="dot", brows="neutral", hand_f=(190, -170), hand_b=(-190, -150), head=10))])
    i = sh.rig(Iggy, "iggy", x=820, y=900, s=0.9)
    i.tint(GREEN, 0.3)
    letgo, splash = sh.cue("letgo"), sh.cue("splash")
    hang = dict(lean=-55, chest=-10, head=-45, eyes="huge", brows="high", mouth="o", hand_f=(250, -470), hand_b=(150, -520), hf="open", hb="open",
                foot_f=(220, -330), foot_b=(260, -250))
    sh.anim(i, [(0, dict(hang, x=820, y=860)),
                (2.5, dict(hang, x=826, y=880, eyes="dot", brows="worried", mouth="frown", ease="lin")),
                (3.2, dict(eyes="dot", brows="angry", mouth="frown", head=-36)),
                (5.6, dict(brows="angry", mouth="shout", x=832, y=900, ease="lin")),
                (letgo, dict(x=836, y=910, eyes="closed", brows="angry", mouth="frown", hand_f=(260, -380), hand_b=(200, -420))),
                (splash, dict(x=900, y=1900, lean=-140, ease="in")),
                (sh.end, dict(x=900, y=1900))])
    i.tint(ORANGE, 0.0, f=sh.f(3.0))
    i.tint(ORANGE, 0.55, f=sh.f(letgo))
    for k, (lt, x, y, rot) in enumerate(((3.2, 560, 380, -0.12), (4.0, 1380, 500, 0.15), (4.7, 700, 760, 0.08))):
        fx.world_text(sh, "HEY, YOU." if k != 1 else "HEY, YOU!", x, y, 70 + k * 18, t0=lt, t1=letgo + 0.3, col="#c8c0b0", fname="anton",
                      depth=-1.0, rot=rot, ink="#3a1010")
    rage = {}
    for f in range(sh.f(3.0), sh.f(letgo + 0.5), 2):
        u = (sh.t(f) - 3.0) / (letgo - 2.5)

        def draw(pen, u=u):
            for k in range(int(6 + 18 * u)):
                a = k * 2.39
                rr = 260 + 40 * math.sin(k * 3.1 + u * 9)
                pen.taper([(900 + rr * math.cos(a), 520 + rr * math.sin(a)), (900 + (rr + 80 + 60 * u) * math.cos(a), 520 + (rr + 80 + 60 * u) * math.sin(a))],
                          10, ORANGE, min(1, u * 1.2), 1.0, 0.1)
        rage[f] = draw
    rage[sh.f(letgo + 0.5)] = None
    fx.fxcard(sh, "rage", -0.3, rage, fx=[fx.glow_fx(ORANGE, 30)])
    fx.flash(sh, splash, "#ff9a3a", frames=3)
    fx.splash(sh, 960, 1000, splash, s=1.6, col=ORANGE, seed=9)
    sh.cam.move([(sh.f(0), 960, 420, 1.15), (sh.f(letgo), 940, 470, 1.25), (sh.f(splash), 960, 900, 1.0), (sh.f(sh.end), 960, 940, 0.98)])


@shot("n10_orange", preview=(0.5, 2.5, 5.0))
def n10_orange(sh):
    sets.vat_room(sh)
    o, cr, ru, run = sh.cue("orange"), sh.cue("crumble"), sh.cue("rust"), sh.cue("run")
    vg = vat_card(sh, "vat_green", GREEN, ORANGE)
    vo = vat_card(sh, "vat_orange", ORANGE, "#c84a10", depth=5.9)
    for ob, on in ((vg, (1, 0)), (vo, (0, 1))):
        md = ob.grease_pencil_modifiers.new("fade", "GP_OPACITY")
        md.factor = on[0]
        ob.keyframe_insert('grease_pencil_modifiers["fade"].factor', frame=sh.f(o))
        md.factor = on[1]
        ob.keyframe_insert('grease_pencil_modifiers["fade"].factor', frame=sh.f(o + 0.6))
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=sh.f(0))
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=sh.f(cr + 1.4))
    g = stage.glow_disc(sh.co, "vatglow", 760, 640, 1000, GREEN, 0.8, depth=5.0)
    g2 = stage.glow_disc(sh.co, "vatglow2", 760, 640, 1100, ORANGE, 0.0, depth=5.0)
    stage.key_strength(g, sh.f(o), 0.8)
    stage.key_strength(g, sh.f(o + 0.5), 0.0)
    stage.key_strength(g2, sh.f(o), 0.0)
    stage.key_strength(g2, sh.f(o + 0.5), 1.4)
    fx.flash(sh, o, "#ff9a3a", frames=2, alpha=0.7)
    for k, (x, y) in enumerate(((420, 860), (760, 900), (1100, 860), (600, 780), (950, 780))):
        fx.rot_web(sh, x, y, ru + k * 0.15, cr, radius=180, seed=20 + k, depth=5.7)
    fx.crumble(sh, 760, 860, cr, w=1000, h=380, seed=3, dur=2.4, depth=5.5)
    fx.smoke(sh, 760, 700, cr, sh.end, col="#c86a2a", every=0.25, depth=5.0, rise=400, size=2.2)
    for k, x in enumerate((1500, 1640, 1760)):
        cls = Magnus if k == 0 else Guard
        r = sh.rig(cls, f"runner{k}", x=x, y=980, s=0.45 if k else 0.5, face=1, depth=1.0)
        r.tint("#100810", 0.75)
        keys = walk_keys(r.p, run, sh.end, x, x + 700, base=dict(s=0.45 if k else 0.5, lean=14, eyes="shock", mouth="shout"), step=0.22, lift=30, bob=10, swing=60)
        sh.anim(r, [(0, dict(keys[0][1]))] + keys)
    sh.cam.shake(sh.f(cr), sh.f(sh.end), 16, 0.4)
    sh.cam.move([(sh.f(0), 860, 600, 1.05), (sh.f(sh.end), 960, 560, 0.95)])


@shot("n11_paper", preview=(1.6, 5.5))
def n11_paper(sh):
    stage.gradient_bg(sh.co, "morning", [(0.0, "#ffe2b0"), (1.0, "#fff4dc")], depth=40)
    land = sh.cue("land")
    g = sh.rig(Granny, "granny", x=940, y=980, s=1.7, depth=0.6)
    sh.anim(g, [(0, dict(hand_f=(140, -190), hand_b=(-140, -190), hf="grab", hb="grab", eyes="dot", brows="neutral", mouth="flat", head=0)),
                (3.6, dict(head=0)),
                (sh.line(0)[0] - 0.4, dict(eyes="half", brows="up", head=-6)),
                (sh.line(1)[0], dict(eyes="dot", brows="worried", mouth="flat", head=4)),
                (sh.end, dict(head=6))])
    sh.lipsync(g, "GRANNY", base="flat")

    def paper(pen):
        sets.newspaper(pen, "", "", photo="tiny", x=960, y=540, s=0.62)
    pc = sets.card(sh.co, "bugle1", -0.2, paper)
    pc.rotation_mode = "XYZ"
    lift = 3.4
    for f, rot, sc, z in ((sh.f(0), 6.0, 0.05, 0.0), (sh.f(land), 0.0, 1.0, 0.0), (sh.f(lift), 0.0, 1.0, 0.0), (sh.f(lift + 0.6), 0.0, 1.0, -7.2)):
        pc.rotation_euler = (0, rot * math.tau / 6, 0)
        k = (stage.CAM_DIST - 0.2) / stage.CAM_DIST * sc
        pc.scale = (k, k, k)
        pc.location = (0, -0.2, z)
        pc.keyframe_insert("rotation_euler", frame=f)
        pc.keyframe_insert("scale", frame=f)
        pc.keyframe_insert("location", frame=f)
    from mathutils import Matrix
    k0 = (stage.CAM_DIST - 0.2) / stage.CAM_DIST
    rest = Matrix.LocRotScale((0, -0.2, 0), None, (k0, k0, k0))
    for txt, y, size, fn in (("THE BARNACLE BAY BUGLE", 182, 54, "anton"), ("JANITOR CAUSES TOXIC SPILL,", 330, 64, "anton"),
                             ("FLEES IN SHAME", 400, 64, "anton")):
        t = fx.world_text(sh, txt, 960, y, size, col="#1b1424", fname=fn, depth=-0.25, ink=None, ow=0.0)
        t.parent = pc
        t.matrix_parent_inverse = rest.inverted()
    fx.flash(sh, 0.0, "#ffffff", frames=4)
    sh.cam.move([(sh.f(0), 960, 540, 1.0), (sh.f(lift), 960, 540, 1.0), (sh.f(sh.end), 960, 540, 1.08)])
