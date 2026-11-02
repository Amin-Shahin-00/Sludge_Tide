"""CHAPTER 7: ROT VS. REBUILD."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.rust import BaronRust
from bl.cast.others import Granny, Sela, Magnus, BoltGiant
from . import shot

TEAL, GOLD, ORANGE, PURPLE, GREEN = "#2cfff0", "#ffd23c", "#ff7a1a", "#7a3cb4", "#5dff7a"
SUNSET = "#ff9a5a"


def battlefield(sh, mood="sunset", mountain=True, roofs=True):
    sets.stilts_view(sh, mood=mood, scrap_mountain=mountain)
    if roofs:
        sets.card(sh.co, "roofs", 12, lambda pen: sets.rooftops(pen, 160))
        sets.crowd_card(sh, f"roofcrowd_{mood}", 11.5, -400, 2300, 160, n=16, s=0.7, seed=61, cheer=True, rows=1)


def junk_rig(sh, x, y, s=1.0, face=1, tag="junk", extra=("streak",), depth=0.0):
    j = sh.rig(Junk, tag, x=x, y=y, s=s, face=face, depth=depth)
    for k in extra:
        j.show(sh.f(0) - 30, "head", k)
    return j


def big_stilt(pen, x=960, top=-200, base=1300, w=200, rust=0.0):
    pen.shape(geo.rect(x - w / 2, top, x + w / 2, base), "#6e6a72", 7, depth=w * 0.25)
    for yy in np.arange(top + 60, base, 140):
        pen.line([(x - w / 2, yy), (x + w / 2, yy)], 6)
        for sx in (-1, 1):
            pen.fill(geo.circle(x + sx * w * 0.32, yy - 20, 8, 10), "#4a464e")
    pen.fill(geo.rect(x - w / 2 + 10, top + 10, x - w / 2 + 30, base - 10), "#9a96a0", 0.6)


@shot("f1_army", preview=(1.0, 4.0, 6.0))
def f1_army(sh):
    battlefield(sh)
    rise = sh.cue("rise")
    r = sh.rig(BaronRust, "rust", x=1400, y=1400, s=0.55, face=-1, depth=2.0)
    r.tint(SUNSET, 0.2)
    sh.anim(r, [(0, dict(y=1500, eyes="glow", mouth="closed", hand_f=(150, -250), hand_b=(-150, -250))),
                (rise, dict(y=1500)), (rise + 2.5, dict(y=930, ease="out")), (sh.end, dict(y=930))])
    for k, (x0, w) in enumerate(((1600, 1400), (1100, 1000), (2000, 900))):
        fx.mite_swarm(sh, f"army{k}", [(rise + 0.5 * k, x0, 1150), (sh.end, x0 - 300, 980)], n=60, w=w, h=200, s=0.55, seed=70 + k, depth=1.5 + k * 0.3)
    fx.bubbles(sh, 1200, 1600, 900, 960, rise, sh.end, n=30, col="#ffb05a", rise=120, size=1.4, glow=ORANGE, depth=1.8)
    j = junk_rig(sh, 520, 960, 0.45, extra=("streak", "bandage"))
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="flat", hand_f=(60, -150), hand_b=(-60, -150), hf="fist", hb="fist"))])
    fx.caption(sh, "SUNSET", 0.3, 2.6, y=990, size=76)
    sh.cam.move([(sh.f(0), 960, 540, 0.95), (sh.f(sh.end), 1100, 600, 1.08)])


@shot("f2_why", preview=(1.5, 5.5, 9.5))
def f2_why(sh):
    battlefield(sh, roofs=False)
    L = [sh.line(k) for k in range(4)]
    r = sh.rig(BaronRust, "rust", x=1360, y=1060, s=0.95, face=-1)
    r.tint(SUNSET, 0.15)
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(160, -250), hand_b=(-160, -250), head=6)),
                (L[1][0], dict(head=-8, hand_f=(240, -380), hf="open")),
                (L[3][1] - 0.3, dict(eyes="wide", brows="up", head=-2, hand_f=(160, -260), hf="claw", ease="snap")),
                (L[3][1] + 0.9, dict(eyes="narrow", brows="angry", head=4)),
                (sh.end, dict(eyes="narrow", brows="angry"))])
    sh.lipsync(r, "RUST", base="closed")
    j = junk_rig(sh, 560, 1060, 1.0, extra=("streak", "bandage"))
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="flat", hand_f=(60, -150), hand_b=(-60, -150), hf="fist", hb="fist")),
                (L[2][0], dict(hand_f=(120, -280), hf="open")),
                (L[3][0], dict(eyes="dot", brows="worried", hand_f=(260, -320), hf="open", lean=6)),
                (sh.end, dict(eyes="dot", brows="angry"))])
    sh.lipsync(j, "JUNK", base="flat")
    boil = L[3][1] + 0.9
    fx.bubbles(sh, 900, 1900, 1040, 1100, boil, sh.end, n=50, col="#ffb05a", rise=200, size=1.6, glow=ORANGE, depth=-0.1)
    g = stage.glow_disc(sh.co, "boil", 1360, 1060, 900, ORANGE, 0.0, depth=0.5)
    stage.key_strength(g, sh.f(boil), 0.0)
    stage.key_strength(g, sh.f(sh.end), 1.2)
    sh.cam.move([(sh.f(0), 960, 600, 1.0), (sh.f(L[3][0]), 760, 560, 1.25), (sh.f(L[3][1]), 1240, 500, 1.3), (sh.f(sh.end), 1260, 500, 1.35)])
    sh.cam.shake(sh.f(boil), sh.f(sh.end), 8, 0.6)


@shot("f3_round1", preview=(1.0, 3.4, 5.0))
def f3_round1(sh):
    battlefield(sh)
    slam, crab = sh.cue("slam"), sh.cue("crab")
    fx.caption(sh, "ROUND ONE", 0.1, 1.6, y=200, size=120, col=GOLD)
    j = junk_rig(sh, 520, 1000, 0.8, extra=("streak", "bandage"))
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(60, -500), hand_b=(-60, -500), hf="open", hb="open")),
                (slam, dict(hand_f=(120, -20), hand_b=(40, -20), lean=40, ease="snap")),
                (sh.end, dict(lean=34))])
    fx.mite_swarm(sh, "charge", [(0, 1700, 1080), (crab, 1100, 1080), (sh.end, 1000, 1080)], n=70, w=1200, h=200, s=0.6, seed=75, depth=0.4)
    arms = {}
    for f in range(sh.f(slam), sh.f(sh.end), 2):
        u = min(1, (sh.t(f) - slam) / 0.8)
        tt = sh.t(f)

        def draw(pen, u=u, tt=tt):
            for k in range(6):
                bx = 700 + k * 170
                a = math.sin(tt * 5 + k) * 0.6
                L_ = 300 * u
                tip = (bx + L_ * math.sin(a), 1000 - L_ * math.cos(a))
                pen.tube([(bx, 1040), ((bx + tip[0]) / 2, (1040 + tip[1]) / 2 - 20), tip], 34, "#8a7a9a", 5)
                pen.shape(geo.blob([(tip[0] - 40, tip[1] - 10), (tip[0] + 40, tip[1] - 10), (tip[0] + 30, tip[1] - 60), (tip[0] - 30, tip[1] - 60)], n=2),
                          "#c8ccd4", 5, hi=0.4)
        arms[f] = draw
    fx.fxcard(sh, "metalarms", 0.2, arms, fx=[fx.glow_fx(TEAL, 15)])
    for k in range(3):
        wm = fx.prop(sh, f"washer{k}", lambda pen: (pen.shape(geo.rrect(-70, -80, 70, 80, 10), "#f4f1e6", 6, hi=0.3),
                                                    pen.shape(geo.circle(0, 10, 44), "#59c3e8", 5, hi=0.6)),
                     [(slam + 0.3, 820 + k * 260, 960, 0, 1.0)], depth=0.15)
        fx.vis(wm, slam + 0.3, None, sh)
    bg = sh.rig(BoltGiant, "boltg", x=1300, y=-400, s=0.8, depth=0.3)
    sh.anim(bg, [(crab - 0.6, dict(y=-500, eyes="angry")), (crab, dict(y=1080, eyes="angry", sq=0.7, ease="in")), (crab + 0.3, dict(sq=1.05)),
                 (crab + 0.5, dict(sq=1.0)), (sh.end, dict(y=1080, eyes="googly"))])
    fx.dust(sh, 1300, 1060, crab, n=24, spread=500, rise=200, col="#e8b080", seed=17, size=2.0)
    fx.world_text(sh, "SPLAT!", 1500, 520, 140, t0=crab, t1=sh.end, col=GOLD, depth=-0.8, rot=0.1)
    fx.impact_frame(sh, crab, frames=2, col=ORANGE)
    sh.cam.move([(sh.f(0), 960, 600, 1.0), (sh.f(sh.end), 1060, 620, 1.05)])
    sh.cam.shake(sh.f(slam), sh.f(slam + 0.4), 14, 0.3)
    sh.cam.shake(sh.f(crab), sh.f(crab + 0.5), 26, 0.3)


@shot("f4_blur", preview=(1.0, 3.5, 6.0))
def f4_blur(sh):
    stage.gradient_bg(sh.co, "sky", sets.MOODS["sunset"]["sky"], depth=60)
    sets.card(sh.co, "bigstilt", 1.0, lambda pen: big_stilt(pen, 960, -400, 1400, 220))
    fx.caption(sh, "ROUND TWO", 0.1, 1.5, y=200, size=120, col=GOLD)
    beats, t, gap = [], 0.8, 0.5
    while t < sh.end - 0.2:
        beats.append(t)
        gap = max(0.083, gap * 0.86)
        t += gap
    fx.rot_climb(sh, 960, -300, 1300, 0.6, sh.end, w=220, depth=0.95, beats=beats)
    d = {}
    for k, b in enumerate(beats):
        f0 = sh.f(b)
        col = ORANGE if k % 2 == 0 else TEAL
        d[f0] = (lambda c, kk: (lambda pen: pen.fill(geo.rect(-200, -200, 2120, 1280), c, min(0.55, 0.12 + kk * 0.02))))(col, k)
        d[f0 + 1] = None
    fx.fxcard(sh, "heartbeat", 0.0, d, screen=True)
    r = sh.rig(BaronRust, "rust", x=1560, y=1200, s=0.9, face=-1)
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(320, -360), hf="point", hand_b=(-150, -250))), (sh.end, dict(eyes="narrow", brows="angry"))])
    j = junk_rig(sh, 360, 1200, 0.9, extra=("streak", "bandage"))
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(330, -380), hand_b=(300, -330), hf="open", hb="open", lean=10))])
    sh.cam.move([(sh.f(0), 960, 600, 1.0), (sh.f(sh.end), 960, 560, 1.18)])
    sh.cam.shake(sh.f(sh.end - 2.5), sh.f(sh.end), 10, 0.25)


@shot("f5_rain", preview=(0.8, 3.0, 5.0))
def f5_rain(sh):
    sets.stilts_view(sh, mood="purple", scrap_mountain=True)
    fx.caption(sh, "ROUND THREE", 0.1, 1.5, y=200, size=120, col=GOLD)
    r = sh.rig(BaronRust, "rust", x=1300, y=1080, s=0.95, face=-1)
    r.tint(PURPLE, 0.2)
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(160, -250), hand_b=(-160, -250))),
                (0.6, dict(hand_f=(330, -620), hand_b=(-330, -620), hf="open", hb="open", head=-10, ease="io")),
                (sh.end, dict(hand_f=(340, -640), hand_b=(-340, -640)))])
    sh.lipsync(r, "RUST", base="closed")
    fx.rain(sh, 1.0, sh.end, col="#ff8a3a", angle=0.15, n=200, seed=9, alpha=0.9, sizzle=True)
    for k, (x, y) in enumerate(((300, 360), (800, 300), (1500, 380))):
        fx.rot_web(sh, x, y, 1.8 + k * 0.6, 3.0 + k * 0.6, radius=160, seed=30 + k, depth=8)
        fx.crumble(sh, x, y, 3.0 + k * 0.6, w=300, h=160, seed=40 + k, depth=8, dur=1.4)
    fx.world_text(sh, "SSSSS", 960, 160, 70, t0=1.4, t1=sh.end, col="#ff8a3a", depth=-0.7)
    fx.world_text(sh, "AAAH!", 420, 260, 70, t0=2.6, t1=sh.end, col="#ffffff", depth=-0.7, rot=-0.2)
    sh.cam.move([(sh.f(0), 1200, 520, 1.15), (sh.f(sh.end), 960, 520, 0.95)])


@shot("f6_titan", preview=(1.5, 4.0, 5.6, 8.0))
def f6_titan(sh):
    sets.stilts_view(sh, mood="purple", scrap_mountain=False)
    pull, slam, heart = sh.cue("pull"), sh.cue("slam"), sh.cue("heart")
    fx.rain(sh, 0, sh.end, col="#ff8a3a", angle=0.15, n=180, seed=10, alpha=0.8, sizzle=True)
    j = junk_rig(sh, 960, 1060, 0.8, extra=("streak", "bandage"))
    sh.anim(j, [(0, dict(eyes="closed", brows="angry", mouth="flat", hand_f=(80, -200), hand_b=(-80, -200))),
                (pull, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(240, -560), hand_b=(-240, -560), hf="open", hb="open", ease="back")),
                (slam - 0.3, dict(hand_f=(120, -640), hand_b=(-120, -640))),
                (slam, dict(y=900, ease="snap")), (sh.end, dict(y=900))])
    sh.lipsync(j, "JUNK", base="shout")
    j.tint(TEAL, 0.0, f=sh.f(pull))
    j.tint(TEAL, 0.4, f=sh.f(slam))
    j.hide(sh.f(slam + 0.1), True)
    fx.tornado(sh, 960, 1000, pull, slam + 0.1, n=80, r0=1100, r1=160, h=1000)
    g = stage.glow_disc(sh.co, "aura", 960, 700, 1000, TEAL, 0.0, depth=2.0)
    for t, v in ((pull, 0.0), (slam, 1.4), (sh.end, 0.8)):
        stage.key_strength(g, sh.f(t), v)
    T = fx.prop(sh, "titan", lambda pen: sets.titan(pen, 0, 0, 1.0), [(slam, 960, 1380, 0, 0.5), (slam + 0.25, 960, 1380, 0, 1.08),
                                                                      (slam + 0.4, 960, 1380, 0, 1.0), (sh.end, 960, 1380, 0, 1.02)],
                depth=-0.2, fx=[fx.glow_fx(TEAL, 30)])
    fx.vis(T, slam, None, sh)
    fx.flash(sh, slam, "#e8fffa", frames=3)
    fx.impact_frame(sh, slam + 0.12, frames=2, col=TEAL)
    fx.banner(sh, "JUNKYARD TITAN!!", sh.line(0)[0], sh.end, col=TEAL, accent=GOLD, size=170)
    fx.sparks(sh, 960, 920, heart, col=TEAL, n=40, dur=0.8, spread=700)
    sh.cam.move([(sh.f(0), 960, 760, 1.2), (sh.f(slam), 960, 640, 1.0), (sh.f(sh.end), 960, 420, 0.8)])
    sh.cam.shake(sh.f(pull), sh.f(slam + 0.6), 14, 0.3)


@shot("f7_throne", preview=(1.0, 5.0, 9.5))
def f7_throne(sh):
    sets.stilts_view(sh, mood="purple", scrap_mountain=False)
    fx.rain(sh, 0, sh.end, col="#ff8a3a", angle=0.15, n=120, seed=11, alpha=0.6, sizzle=True)
    T = fx.prop(sh, "titan", lambda pen: sets.titan(pen, 0, 0, 1.0), [(0, 420, 1500, 0, 0.85), (sh.end, 400, 1500, -2, 0.85)], depth=1.0,
                fx=[fx.glow_fx(TEAL, 30)])
    L = [sh.line(k) for k in range(3)]
    base_y, top_y = 1200, 560
    r = sh.rig(BaronRust, "rust", x=1360, y=base_y, s=0.7, face=-1)
    rise0 = L[1][1]
    keys = [(0, dict(eyes="closed", mouth="closed", hand_f=(160, -250), hand_b=(-160, -250), chest=-6))]
    for k, t in enumerate(np.arange(L[0][0], L[0][1], 1 / 6)):
        keys.append((t, dict(chest=-14 if k % 2 else -6, eyes="closed", ease="hold")))
    keys += [(L[1][0], dict(chest=0, eyes="glow", hand_f=(250, -330), hf="open")),
             (rise0, dict(y=base_y, hand_f=(150, -260), hf="flat", hand_b=(-150, -260), hb="flat")),
             (sh.end, dict(y=top_y, eyes="narrow", brows="angry", ease="io"))]
    sh.anim(r, keys)
    sh.lipsync(r, "RUST", base="closed")
    fx.goo_column(sh, 1360, 1300, rise0, sh.end, top_y + 20, w=200)
    fx.world_text(sh, "HA. HA HA HA.", 1300, 260, 80, t0=L[0][0], t1=L[0][1] + 0.4, col=ORANGE, depth=-0.7, fname="hand")
    fx.banner(sh, "SLUDGE THRONE", rise0 + 0.3, sh.end, col=ORANGE, accent=PURPLE, y=200, name="b2")
    sh.cam.move([(sh.f(0), 1320, 520, 1.25), (sh.f(rise0), 1200, 560, 1.0), (sh.f(sh.end), 960, 420, 0.85)])


@shot("f8_clash", preview=(1.0, 1.5, 2.7, 4.5))
def f8_clash(sh):
    h1, h2, cr = sh.cue("hit1"), sh.cue("hit2"), sh.cue("crack")

    def halves(pen):
        pen.fill(np.array([(-400, -300), (1060, -300), (860, 1400), (-400, 1400)]), "#0c5a6a")
        pen.fill(np.array([(1060, -300), (2400, -300), (2400, 1400), (860, 1400)]), "#6a2a10")
        for k in range(18):
            pen.taper([(960 - 80 * k, -300 + k * 90), (-400, -300 + k * 120)], 10, "#2cfff0", 0.4, 1.0, 0.1)
            pen.taper([(960 + 80 * k, 1400 - k * 90), (2400, 1400 - k * 120)], 10, "#ff9a3a", 0.4, 1.0, 0.1)
    sets.card(sh.co, "split", 3.0, halves)
    tf = fx.prop(sh, "titanfist", lambda pen: sets.hubcap_fist(pen, 0, 0, 2.2), [(0, -300, 560, 0, 1.0), (h1, 700, 560, 0, 1.0), (h1 + 0.4, 600, 560, 0, 1.0),
                                                                                  (h2, 760, 520, 0, 1.0), (sh.end, 640, 540, 0, 1.0)], depth=0.2, fx=[fx.glow_fx(TEAL, 30)])

    def rotfist(pen):
        pen.shape(geo.blob([(240, -120), (-60, -150), (-200, -90), (-220, 60), (-80, 140), (240, 120)], n=4), ORANGE, 9, hi=0.5)
        for k in range(6):
            pen.line(geo.circle(-100 + k * 50, -40 + (k % 2) * 60, 16, 12), 5, "#ffd0a0", closed=True)
    rf = fx.prop(sh, "rotfist", rotfist, [(0, 2300, 560, 0, 1.6), (h1, 1240, 560, 0, 1.6), (h1 + 0.4, 1340, 560, 0, 1.6), (h2, 1180, 600, 0, 1.6),
                                          (sh.end, 1300, 560, 0, 1.6)], depth=0.2, fx=[fx.glow_fx(ORANGE, 30)])
    for t in (h1, h2):
        fx.impact_frame(sh, t, frames=3, col=GOLD)
        fx.burst(sh, 960, 560, t + 0.12, col="#ffffff", r1=380, seed=int(t * 10))
    fx.speedlines(sh, 0, sh.end, 960, 540, "#ffffff", inner=420, n=50, seed=14, alpha=0.5)
    d = {sh.f(cr): lambda pen: [pen.line([(960, -100), (930, 200), (990, 420), (940, 640), (1000, 860), (950, 1200)], 22, "#ffffff"),
                                pen.line([(960, -100), (930, 200), (990, 420), (940, 640), (1000, 860), (950, 1200)], 8, "#1b1424"),
                                pen.line([(990, 420), (1160, 380)], 10, "#ffffff"), pen.line([(940, 640), (760, 700)], 10, "#ffffff")]}
    fx.fxcard(sh, "crack", 0.0, d, screen=True)
    fx.flash(sh, cr, "#ffffff", frames=2)
    sh.cam.shake(sh.f(h1), sh.f(sh.end), 18, 0.3)


@shot("f9_rig", preview=(1.0, 3.5, 6.5))
def f9_rig(sh):
    sets.harbor(sh, "purple", stilts=True, lighthouse=False, boats=False, horizon=640)
    q = sh.cue("quake")
    L0 = sh.line(0)
    rig = fx.prop(sh, "leviathan", lambda pen: sets.leviathan(pen, 0, 0, 1.0), [(q, 1250, 1700, 0, 0.8), (L0[0], 1250, 980, 0, 0.8), (sh.end, 1200, 940, -2, 0.82)],
                  depth=3.0)
    fx.splash(sh, 1250, 760, q + 0.5, s=3.0, col="#c8b0d8", seed=21, depth=2.8, dur=1.6)
    fx.smoke(sh, 1250, 430, L0[0] - 0.5, sh.end, col="#9a5ad0", every=0.25, depth=2.5, rise=300, size=2.0)
    m = sh.rig(Magnus, "magnus", x=1250, y=680, s=0.3, depth=2.9)
    sh.anim(m, [(0, dict(y=1240, mouth="grin", hand_f=(200, -150), hand_b=(-200, -150))), (L0[0], dict(y=640)),
                (L0[0] + 0.3, dict(hand_f=(240, -330), hand_b=(-240, -330), hf="open", hb="open")), (sh.end, dict(y=610))])
    sh.lipsync(m, "MAGNUS", base="grin")
    T = fx.prop(sh, "titan", lambda pen: sets.titan(pen, 0, 0, 1.0), [(0, 420, 1300, 0, 0.5)], depth=0.5, fx=[fx.glow_fx(TEAL, 30)])
    fx.world_text(sh, "RUMBLE RUMBLE", 960, 1000, 90, t0=q, t1=L0[0], col="#ffffff", depth=-0.7)
    sh.cam.shake(sh.f(q), sh.f(L0[0]), 22, 0.35)
    sh.cam.move([(sh.f(0), 960, 620, 1.0), (sh.f(L0[0]), 1150, 520, 1.0), (sh.f(sh.end), 1230, 480, 1.4)])


@shot("f10_hoses", preview=(0.8, 2.5, 4.5))
def f10_hoses(sh):
    sets.harbor(sh, "purple", stilts=True, lighthouse=False, boats=False, horizon=640)
    latch = sh.cue("latch")
    fx.prop(sh, "leviathan", lambda pen: sets.leviathan(pen, 0, 0, 1.0), [(0, 1500, 860, 0, 0.5)], depth=3.0)
    T = fx.prop(sh, "titan", lambda pen: sets.titan(pen, 0, 0, 1.0), [(0, 420, 1300, 0, 0.55), (latch + 1.5, 420, 1300, 0, 0.55),
                                                                      (sh.end, 380, 1500, -12, 0.5)], depth=0.5, fx=[fx.glow_fx(TEAL, 30)])
    fx.crumble(sh, 420, 800, latch + 1.5, w=600, h=600, col="#8a8078", seed=50, dur=2.5, depth=0.4, wind=(-200, 400))
    hose1 = [(1240, 640), (900, 400), (600, 560), (440, 640)]
    hose2 = [(1300, 700), (1200, 900), (1080, 880)]
    fx.hose(sh, "a", hose1, depth=0.6, t_on=latch)
    fx.hose(sh, "b", hose2, depth=0.6, t_on=latch)
    fx.hose_flow(sh, hose1[::-1], latch + 0.2, sh.end, col=TEAL, seed=1, depth=0.55)
    fx.hose_flow(sh, hose2[::-1], latch + 0.2, sh.end, col=ORANGE, seed=2, depth=0.55)
    r = sh.rig(BaronRust, "rust", x=1080, y=1120, s=0.5, face=-1, depth=0.4)
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(160, -250), hand_b=(-160, -250))),
                (latch + 0.2, dict(eyes="wide", hand_f=(120, -500), hf="claw", ease="snap")),
                (sh.end, dict(y=1220, chest=30, head=20, eyes="narrow", s=0.42))])
    fx.flash(sh, latch, "#ffffff", frames=2)
    fx.world_text(sh, "SHLUUURP", 900, 260, 100, t0=latch + 0.2, t1=sh.end, col="#c8ccd4", depth=-0.7, rot=-0.1)
    sh.cam.move([(sh.f(0), 960, 600, 0.95), (sh.f(sh.end), 860, 640, 1.05)])
    sh.cam.shake(sh.f(latch), sh.f(sh.end), 10, 0.4)


@shot("f11_logs", preview=(0.8, 3.0, 6.0, 9.5))
def f11_logs(sh):
    L = [sh.line(k) for k in range(4)]
    sw = sh.cue("switch")
    sets.harbor(sh, "purple", stilts=True, lighthouse=False, boats=False, horizon=640)
    before = set(sh.co.objects)
    sets.card(sh.co, "roof_near", 0.3, lambda pen: pen.shape(np.array([(-300, 1500), (-300, 900), (900, 760), (2400, 900), (2400, 1500)]), "#c8432f", 8, depth=20))
    s = sh.rig(Sela, "sela", x=1100, y=880, s=1.0)
    sh.anim(s, [(0, dict(eyes="dot", brows="angry", mouth="flat", hand_f=(180, -200), hf="open", hand_b=(-60, -160))),
                (sw, dict(hand_f=(210, -150), hf="fist", ease="snap")),
                (L[1][0], dict(hand_f=(60, -300), hf="open", eyes="dot", brows="angry")), (sh.end, dict(eyes="dot"))])
    sh.lipsync(s, "SELA", base="flat")
    tr = fx.prop(sh, "transmitter_off", lambda pen: sets.transmitter(pen, 0, 0, 1.2, on=False), [(0, 1330, 880, 0, 1.0)], depth=0.05)
    fx.vis(tr, None, sw, sh)
    tr2 = fx.prop(sh, "transmitter_on", lambda pen: sets.transmitter(pen, 0, 0, 1.2, on=True), [(0, 1330, 880, 0, 1.0)], depth=0.05, fx=[fx.glow_fx("#e8392f", 20)])
    fx.vis(tr2, sw, None, sh)
    fx.radio_waves(sh, 1414, 470, sw + 0.1, sh.end, col=GOLD, rmax=1800)
    # Junk below, logs held high (inset at the start)
    j = junk_rig(sh, 420, 1500, 1.5, extra=("streak", "bandage", "cracked"))
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(160, -720), hf="logs", hand_b=(-60, -300))),
                (L[0][1] + 0.3, dict(hand_f=(180, -740)))])
    sh.lipsync(j, "JUNK", base="shout")
    fx.caption(sh, "ON EVERY RADIO IN THE ARCHIPELAGO", L[1][0] + 0.5, sh.end - 0.2, y=1000, size=58, col=GOLD)
    sh.cam.move([(sh.f(0), 520, 520, 1.3), (sh.f(L[0][1]), 520, 520, 1.3), (sh.f(sw - 0.3), 1150, 560, 1.15), (sh.f(L[1][0] + 1.0), 1150, 560, 1.15),
                 (sh.f(sh.end), 1100, 460, 0.7)])


@shot("f12_hears", preview=(1.0, 3.0, 5.0))
def f12_hears(sh):
    stage.gradient_bg(sh.co, "sky", sets.MOODS["purple"]["sky"], depth=60)
    touch = sh.cue("touch")
    hose = [(2200, -200), (1600, 200), (1300, 520), (1160, 640)]
    fx.hose(sh, "r", hose, depth=0.3)
    fx.hose_flow(sh, hose[::-1], 0, touch, col=ORANGE, seed=3, depth=0.25)
    r = sh.rig(BaronRust, "rust", x=900, y=1700, s=1.6)
    sh.anim(r, [(0, dict(eyes="tired", brows="worried", mouth="closed", head=14, chest=10, hand_f=(160, -300), hand_b=(-160, -300))),
                (1.4, dict(eyes="glow", brows="up", head=0)),
                (2.6, dict(head=-24, eyes="wide", brows="neutral")),
                (3.6, dict(eyes="narrow", brows="angry", head=-20, hand_f=(250, -620), hf="point")),
                (touch, dict(hand_f=(280, -650), ease="snap")),
                (sh.end, dict(hand_f=(280, -650)))])
    fx.rot_web(sh, 1180, 640, touch, sh.end, radius=200, seed=7, depth=0.2)
    fx.world_text(sh, "...tap.", 1300, 420, 70, t0=touch, t1=sh.end, col=ORANGE, depth=-0.7, fname="hand")
    fx.radio_waves(sh, 960, 200, 0, 2.4, col=GOLD, rmax=900, seed=4)
    sh.cam.move([(sh.f(0), 960, 520, 1.0), (sh.f(2.6), 960, 480, 1.1), (sh.f(touch), 1060, 560, 1.15), (sh.f(sh.end), 1080, 580, 1.2)])


@shot("f13_collapse", preview=(1.0, 3.0, 4.5, 6.4))
def f13_collapse(sh):
    sets.harbor(sh, "purple", stilts=True, lighthouse=False, boats=False, horizon=640)
    race, groan, fall, spl = sh.cue("race"), sh.cue("groan"), sh.cue("fall"), sh.cue("splash")
    rig = fx.prop(sh, "leviathan", lambda pen: sets.leviathan(pen, 0, 0, 1.0),
                  [(0, 1150, 860, 0, 0.55), (groan, 1150, 860, 0, 0.55), (fall, 1180, 900, 8, 0.55), (spl, 1300, 1400, 28, 0.55), (sh.end, 1320, 1600, 30, 0.55)],
                  depth=3.0)
    rig.grease_pencil_modifiers.new("rusting", "GP_TINT")
    t = rig.grease_pencil_modifiers["rusting"]
    t.color = gp.to_linear(gp.rgb("#c8501a"))
    t.factor = 0.0
    rig.keyframe_insert('grease_pencil_modifiers["rusting"].factor', frame=sh.f(race))
    t.factor = 0.75
    rig.keyframe_insert('grease_pencil_modifiers["rusting"].factor', frame=sh.f(groan + 0.6))
    for k in range(6):
        fx.rot_web(sh, 900 + k * 90, 640 + (k % 2) * 60, race + 0.2 * k, groan + 0.6, radius=150, seed=60 + k, depth=2.9)
    fx.crumble(sh, 1150, 700, fall, w=1200, h=600, col="#a8501a", seed=61, dur=2.6, depth=2.8)
    fx.splash(sh, 1300, 760, spl, s=3.4, col="#d8c0e0", seed=62, depth=2.7, dur=1.6)
    fx.sludge_cloud(sh, 1300, 700, spl, sh.end, r0=200, r1=700, col=ORANGE, core="#ffd23c", depth=2.6, rise=-200, alpha=0.7)
    m = sh.rig(Magnus, "magnus", x=1150, y=640, s=0.2, depth=2.95)
    sh.anim(m, [(0, dict(mouth="shout", eyes="shock", brows="high", hand_f=(200, -350), hand_b=(-200, -350))),
                (fall, dict(y=700)), (spl, dict(y=1300, lean=40, ease="in"))])
    sh.lipsync(m, "MAGNUS", base="shout", shapes=("shout", "shout", "shout"))
    fx.world_text(sh, "GROOOAN", 1100, 300, 90, t0=groan, t1=fall + 0.5, col="#ffb05a", depth=-0.7)
    cg = fx.prop(sh, "coastguard", lambda pen: sets.coastguard(pen), [(spl + 0.6, -300, 900, 0, 0.8), (sh.end, 400, 900, 0, 0.8)], depth=0.5)
    sh.cam.move([(sh.f(0), 1150, 520, 1.0), (sh.f(spl), 1200, 600, 0.95), (sh.f(sh.end), 1000, 640, 0.95)])
    sh.cam.shake(sh.f(groan), sh.f(sh.end), 16, 0.35)


@shot("f14_rage", preview=(1.5, 5.0, 7.5))
def f14_rage(sh):
    sets.stilts_view(sh, mood="purple", scrap_mountain=False)
    fx.rain(sh, 0, sh.end, col="#c8d0e8", angle=0.12, n=200, seed=12, alpha=0.6)
    L = [sh.line(k) for k in range(2)]
    r = sh.rig(BaronRust, "rust", x=1100, y=1180, s=1.0, face=-1)
    r.show(sh.f(0) - 30, "head", "tears")
    sh.anim(r, [(0, dict(eyes="glow", brows="worried", mouth="closed", hand_f=(160, -300), hand_b=(-160, -300), head=10)),
                (L[0][0] + 0.4, dict(hand_f=(300, -500), hand_b=(-200, -520), hf="claw", hb="claw", brows="angry", head=-6)),
                (L[1][0], dict(hand_f=(420, -400), hand_b=(380, -360), hf="open", hb="open", chest=14, eyes="wide", ease="snap")),
                (sh.end, dict(chest=18))])
    sh.lipsync(r, "RUST", base="closed")
    wave = {}
    for f in range(sh.f(L[1][0]), sh.f(sh.end) + 1, 2):
        u = (sh.t(f) - L[1][0]) / max(0.1, sh.end - L[1][0])

        def draw(pen, u=u):
            x = 1000 - 1200 * u
            pen.shape(geo.blob([(x + 300, 1200), (x + 200, 700 - 200 * u), (x - 100, 500 - 200 * u), (x - 260, 640), (x - 300, 1200)], n=4),
                      ORANGE, 8, shade=0.6, hi=0.5)
            for k in range(5):
                from bl.cast.others import draw_mite
                draw_mite(pen, x - 120 + k * 60, 900 - k * 70, 1.4, "angry")
        wave[f] = draw
    fx.fxcard(sh, "corrode_wave", -0.2, wave, fx=[fx.glow_fx(ORANGE, 30)])
    fx.banner(sh, "CORRODE WAVE", L[1][0], sh.end, col=ORANGE, accent=PURPLE, y=200)
    sh.cam.move([(sh.f(0), 1120, 480, 1.4), (sh.f(L[1][0]), 1100, 520, 1.2), (sh.f(sh.end), 900, 560, 1.0)])
    sh.cam.shake(sh.f(L[1][0]), sh.f(sh.end), 16, 0.3)


@shot("f15_bowl", preview=(2.0, 6.0, 10.0, 13.5))
def f15_bowl(sh):
    """The quietest, slowest moment of the season: all sound out but the rain."""
    sets.stilts_view(sh, mood="night", scrap_mountain=False)
    fx.rain(sh, 0, sh.end, col="#a8b8d8", angle=0.08, n=140, seed=13, alpha=0.45, length=80)
    sets.card(sh.co, "wreck", 0.8, lambda pen: [sets.scrap_piece(pen, 200 + k * 140, 1040 + (k % 3) * 14, 1.2, kind=k % 10, seed=200 + k) for k in range(12)])
    L = [sh.line(k) for k in range(2)]
    r = sh.rig(BaronRust, "rust", x=1500, y=1060, s=0.9, face=-1)
    r.show(sh.f(0) - 30, "head", "tears")
    r.tint("#2a3470", 0.2)
    sh.anim(r, [(0, dict(eyes="glow", brows="angry", mouth="closed", hand_f=(260, -420), hf="claw", hand_b=(-160, -300), chest=10)),
                (L[0][0], dict(eyes="wide", brows="worried", chest=0, hand_f=(160, -300), hf="open")),
                (sh.end, dict(eyes="sad", brows="worried", head=10))])
    j = junk_rig(sh, 300, 1060, 0.9, extra=("streak", "bandage"), depth=-0.06)
    j.tint("#2a3470", 0.15)
    pick = 2.0
    keys = [(0, dict(eyes="dot", brows="worried", mouth="frown", hand_f=(60, -150), hand_b=(-60, -150))),
            (pick - 0.6, dict(lean=30, hand_f=(120, -30), hf="open")),
            (pick, dict(lean=30, hand_f=(120, -30), hf="bowl")),
            (pick + 0.8, dict(lean=0, hand_f=(120, -300), hand_b=(90, -290), hb="open"))]
    walk = walk_keys(j.p, pick + 1.0, L[0][0] - 0.2, 300, 1150, base=dict(s=0.9, eyes="dot", brows="worried", mouth="frown", hand_f=(120, -300),
                                                                         hand_b=(90, -290), hf="bowl", hb="open"), step=1.0, lift=16, bob=4)
    keys += walk
    keys += [(L[0][0], dict(walk[-1][1], hand_f=(220, -360), hand_b=(190, -350), eyes="dot", brows="worried", mouth="smile", ease="io")),
             (sh.end, dict(walk[-1][1], hand_f=(230, -370), hand_b=(200, -360), eyes="dot", brows="worried", mouth="smile"))]
    sh.anim(j, keys)
    sh.lipsync(j, "JUNK", base="smile")
    j.show(sh.f(7.0), "head", "cracked")
    for k in range(6):
        fx.rot_web(sh, 600 + k * 140, 1060, 3.0 + k * 0.9, 3.6 + k * 0.9, radius=90, seed=80 + k, depth=0.1)
    sh.cam.move([(sh.f(0), 760, 620, 1.0), (sh.f(L[0][0]), 1180, 600, 1.15), (sh.f(sh.end), 1240, 560, 1.3)])


@shot("f16_granny", preview=(1.0, 3.0))
def f16_granny(sh):
    sets.harbor(sh, "night", stilts=True, lighthouse=False, boats=False, island=True, horizon=560)
    fx.rain(sh, 0, sh.end, col="#a8b8d8", angle=0.08, n=120, seed=14, alpha=0.4, length=80)
    sets.card(sh.co, "hotpot_far", 1.0, lambda pen: sets.noodle_boat(pen, 960, 900, 1.3, lit=True))
    stage.glow_disc(sh.co, "lanterns", 960, 700, 600, "#ffb060", 0.6, depth=1.2)
    g = sh.rig(Granny, "granny", x=980, y=830, s=0.7, depth=0.9)
    sh.anim(g, [(0, dict(eyes="dot", brows="worried", mouth="flat", hand_f=(140, -200), hf="ladle")),
                (1.0, dict(hand_f=(140, -460), ease="io")),
                (2.0, dict(head=12, eyes="closed")), (2.6, dict(head=0, eyes="dot")), (3.2, dict(head=12, eyes="closed", mouth="smile")),
                (sh.end, dict(head=4, eyes="dot", mouth="smile"))])
    sh.cam.move([(sh.f(0), 960, 640, 1.2), (sh.f(sh.end), 970, 600, 1.35)])


@shot("f17_fade", preview=(1.0, 3.5, 6.0, 8.6))
def f17_fade(sh):
    sets.stilts_view(sh, mood="night", scrap_mountain=False)
    fx.rain(sh, 0, sh.end, col="#a8b8d8", angle=0.08, n=110, seed=15, alpha=0.4, length=80)
    fl, jan, fall, catch = sh.cue("flicker"), sh.cue("janitor"), sh.cue("fall"), sh.cue("catch")
    r = sh.rig(BaronRust, "rust", x=1200, y=1060, s=0.95, face=-1)
    r.show(sh.f(0) - 30, "head", "tears")
    hm = r.obs["head"].grease_pencil_modifiers["show_human"]
    cm = r.obs["head"].grease_pencil_modifiers["show_crown"]
    for f, h in ((sh.f(fl), 0.0), (sh.f(fl + 0.3), 0.6), (sh.f(fl + 0.5), 0.0), (sh.f(fl + 0.9), 0.7), (sh.f(fl + 1.1), 0.1), (sh.f(jan), 1.0)):
        hm.factor = h
        r.obs["head"].keyframe_insert('grease_pencil_modifiers["show_human"].factor', frame=f)
        cm.factor = 1.0 - h
        r.obs["head"].keyframe_insert('grease_pencil_modifiers["show_crown"].factor', frame=f)
    sh.anim(r, [(0, dict(eyes="sad", brows="worried", mouth="closed", hand_f=(200, -380), hf="open", hand_b=(-160, -300))),
                (jan - 0.1, dict(eyes="sad", mouth="closed")),
                (jan, dict(eyes="none", brows="none", mouth="none", hand_f=(230, -420), hf="open")),
                (fall - 0.3, dict(chest=10)),
                (fall, dict(chest=40, x=1150, y=1100, ease="in")),
                (catch, dict(chest=70, x=1000, y=1200, ease="in")),
                (sh.end, dict(chest=70, x=990, y=1200))])
    aura = stage.glow_disc(sh.co, "aura", 1200, 700, 800, ORANGE, 0.8, depth=0.6)
    for t, v in ((fl, 0.8), (fl + 0.2, 0.1), (fl + 0.4, 0.8), (fl + 0.7, 0.0), (fl + 1.0, 0.6), (jan, 0.0)):
        stage.key_strength(aura, sh.f(t), v)
    j = junk_rig(sh, 780, 1060, 0.9, extra=("streak", "bandage", "cracked"), depth=-0.06)
    sh.anim(j, [(0, dict(eyes="dot", brows="worried", mouth="smile", hand_f=(230, -370), hand_b=(200, -360), hf="bowl", hb="open")),
                (fall - 0.4, dict(eyes="huge", brows="high", mouth="o")),
                (catch, dict(x=880, lean=10, hand_f=(200, -200), hand_b=(160, -240), hf="open", hb="open", eyes="dot", brows="up", mouth="smile", ease="snap")),
                (sh.end, dict(x=880, eyes="happy"))])
    sh.cam.move([(sh.f(0), 1100, 520, 1.25), (sh.f(jan), 1180, 440, 1.6), (sh.f(fall), 1100, 520, 1.25), (sh.f(sh.end), 1000, 600, 1.1)])
