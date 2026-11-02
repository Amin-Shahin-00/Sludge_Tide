"""CHAPTER 3: SCRAP HEART (the comedy chapter)."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.others import Granny, Bolt, BoltGiant
from . import shot

TEAL, GOLD, GREEN = "#2cfff0", "#ffd23c", "#5dff7a"


def at(x, y, s, face, tx, ty):
    return x + face * s * tx, y + s * ty


def stuck_stuff(pen, cx, cy, s=1.0, seed=1):
    r = np.random.default_rng(seed)
    for k in range(12):
        a = r.uniform(0, math.tau)
        rr = r.uniform(40, 150) * s
        x, y = cx + rr * math.cos(a) * 0.6, cy + rr * math.sin(a) * 1.4
        kind = r.integers(0, 3)
        g = TPen(pen, x, y, s, r.uniform(-1.5, 1.5))
        if kind == 0:                                           # fork
            g.line([(0, -40), (0, 30)], 6, col="#c8ccd4")
            for d in (-8, 0, 8):
                g.line([(d, -40), (d, -60)], 3, col="#c8ccd4")
        elif kind == 1:                                         # spoon
            g.line([(0, -10), (0, 40)], 6, col="#c8ccd4")
            g.shape(geo.ellipse(0, -26, 12, 18, 14), "#d8dce4", 3, hi=0.4)
        else:                                                   # little pot
            sets.scrap_piece(g, 0, 0, 0.7, kind=3, seed=k)


@shot("s1_ceiling", preview=(1.0, 3.0))
def s1_ceiling(sh):
    sets.noodle_interior(sh)
    r = sh.rig(Junk, "junk", x=980, y=500, s=1.0)
    r.show(sh.f(0) - 30, "head", "streak")
    base = dict(lean=180, head=10, eyes="closed", mouth="flat", hand_f=(60, -40), hand_b=(-60, -40), foot_f=(30, -420), foot_b=(-30, -420))
    keys = [(0, base), (1.2, dict(eyes="half")), (1.6, dict(eyes="dot", brows="worried")),
            (sh.line(0)[0], dict(eyes="dot", brows="worried", mouth="wobble")),
            (sh.end, dict(eyes="huge", brows="high", mouth="wobble"))]
    for t in np.arange(0, sh.end, 0.5):
        keys.append((t, dict(extra=dict(hips=180 + 3 * math.sin(t * 3)))))
    sh.anim(r, sorted(keys, key=lambda k: k[0]))
    sh.lipsync(r, "JUNK", base="wobble")
    sets.card(sh.co, "stuck_ceiling", -0.1, lambda pen: stuck_stuff(pen, 980, 330, 1.0, seed=3))
    fx.world_text(sh, "zzz", 760, 600, 50, t0=0.2, t1=1.2, col="#ffffff", depth=-0.5)
    sh.cam.move([(sh.f(0), 980, 380, 1.3), (sh.f(sh.end), 980, 400, 1.2)])


@shot("s2_bonk", preview=(0.8, 2.6, 5.5))
def s2_bonk(sh):
    sets.noodle_interior(sh)
    bonk, stick = sh.cue("bonk"), sh.cue("stick")
    j = sh.rig(Junk, "junk", x=1150, y=1000, s=1.0, face=-1)
    j.show(sh.f(0) - 30, "head", "streak")
    j.show(sh.f(stick), "head", "ladle")
    l0, l1 = sh.line(0), sh.line(1)
    sh.anim(j, [(0, dict(eyes="dot", brows="worried", mouth="wobble", hand_f=(60, -140), hand_b=(-60, -140))),
                (bonk, dict(eyes="x", brows="none", mouth="o", sq=0.82, head=10, ease="snap")),
                (bonk + 0.25, dict(sq=1.08)), (bonk + 0.4, dict(sq=1.0, eyes="spiral")),
                (l0[0] - 0.1, dict(eyes="happy", brows="up", mouth="grin", hand_f=(140, -460), hand_b=(-140, -440), hf="open", hb="open", head=-6, ease="back")),
                (l0[1], dict(eyes="huge", brows="high", hand_f=(150, -480), hand_b=(-150, -470))),
                (sh.end, dict(eyes="happy", hand_f=(80, -200), hand_b=(-80, -200)))])
    sh.lipsync(j, "JUNK", base="grin")
    sets.card(sh.co, "stuck_body", -0.05, lambda pen: stuck_stuff(pen, 1150, 760, 0.9, seed=5))
    g = sh.rig(Granny, "granny", x=760, y=1000, s=1.0)
    sh.anim(g, [(0, dict(eyes="dot", brows="angry", mouth="frown", hand_f=(140, -260), hf="ladle")),
                (bonk - 0.3, dict(hand_f=(60, -420), lean=-6)),
                (bonk, dict(hand_f=(260, -300), lean=10, ease="snap")),
                (stick, dict(hf="open", hand_f=(200, -240))),
                (l1[0], dict(eyes="half", brows="angry", mouth="flat", lean=0, hand_f=(150, -180), hf="fist")),
                (l1[1], dict(eyes="happy", brows="neutral", mouth="smile")),
                (sh.end, dict(eyes="happy", mouth="smile"))])
    sh.lipsync(g, "GRANNY", base="smile")
    g.show(sh.f(l1[1]), "head", "blush")
    fx.burst(sh, 1110, 560, bonk, col=GOLD, r1=220, seed=5)
    fx.world_text(sh, "BONK!", 1000, 400, 180, t0=bonk, t1=bonk + 1.1, col=GOLD, depth=-0.8, rot=-0.18)
    fx.impact_frame(sh, bonk + 0.04, frames=2, col=GOLD)
    sh.cam.shake(sh.f(bonk), sh.f(bonk + 0.4), 22, 0.3)
    sh.cam.move([(sh.f(0), 960, 620, 1.05), (sh.f(l0[0]), 1040, 560, 1.15), (sh.f(l1[0]), 940, 600, 1.05), (sh.f(sh.end), 940, 600, 1.08)])


@shot("s3_bikes", preview=(1.5, 3.0, 4.2))
def s3_bikes(sh):
    sets.harbor(sh, "day", stilts=False, horizon=480)
    sets.card(sh.co, "street", 0.6, lambda pen: (pen.fill(geo.rect(-1400, 900, 3400, 1500), "#c8b090"),
                                                 [sets.house(pen, -600 + k * 520, 900, 300, 380, sets.FOLK_COLS[k % 9], "#c8432f", tilt=0.03 * (k % 3 - 1), seed=k)
                                                  for k in range(7)]))
    pile = sh.cue("pile")
    j = sh.rig(Junk, "junk", x=960, y=1000, s=0.95)
    j.show(sh.f(0) - 30, "head", "streak")
    sh.anim(j, [(0, dict(eyes="happy", mouth="grin", hand_f=(120, -380), hand_b=(-120, -380))),
                (1.4, dict(eyes="huge", brows="high", mouth="shout", hand_f=(160, -300), hand_b=(-160, -300), hf="flat", hb="flat")),
                (pile - 0.1, dict(sq=1.0)), (pile, dict(sq=0.7, eyes="spiral", ease="snap")), (sh.end, dict(sq=0.75))])
    sh.lipsync(j, "JUNK", base="shout")
    for k, (x0, col) in enumerate(((-200, "#e8392f"), (2100, "#59c3e8"), (-400, "#9be070"), (2300, "#ffd23c"), (2500, "#ff9ec9"))):
        x1 = 960 + (k - 2) * 50
        keys = [(0.6 + k * 0.15, x0, 1000, 0, 1.0)]
        for t in np.arange(0.6 + k * 0.15, pile, 0.25):
            u = (t - 0.6 - k * 0.15) / (pile - 0.6 - k * 0.15)
            keys.append((t, x0 + (x1 - x0) * u, 1000 - 30 * abs(math.sin(t * 8)), 6 * math.sin(t * 9), 1.0))
        keys.append((pile, x1, 900 - k * 50, (k - 2) * 25, 1.0))
        keys.append((sh.end, x1, 900 - k * 50, (k - 2) * 25, 1.0))
        o = fx.prop(sh, f"bike{k}", (lambda c: (lambda pen: sets.bike(pen, 0, 0, 1.0, c)))(col), keys, depth=-0.1 - k * 0.01)
        fx.vis(o, 0.6 + k * 0.15, None, sh)
    fx.dust(sh, 960, 900, pile, n=20, spread=300, rise=140, seed=8)
    fx.world_text(sh, "CLANG!", 1220, 560, 120, t0=pile, t1=sh.end, col=GOLD, depth=-0.8, rot=0.12)
    sh.cam.move([(sh.f(0), 960, 620, 1.0), (sh.f(pile), 960, 640, 1.1), (sh.f(sh.end), 960, 640, 1.12)])
    sh.cam.shake(sh.f(pile), sh.f(pile + 0.4), 18, 0.3)


@shot("s4_bolt", preview=(0.8, 2.4, 4.4))
def s4_bolt(sh):
    sets.harbor(sh, "day", stilts=False, horizon=480)
    sets.card(sh.co, "beach", 0.8, lambda pen: pen.fill(geo.rect(-1400, 880, 3400, 1500), "#f0d8a0"))
    grow, grab = sh.cue("grow"), sh.cue("grab")
    b = sh.rig(Bolt, "bolt", x=900, y=980, s=2.2)
    sh.anim(b, [(0, dict(eyes="angry", extra=dict(claw=0))), (0.4, dict(extra=dict(claw=-30))), (0.6, dict(extra=dict(claw=0))),
                (0.8, dict(extra=dict(claw=-30))), (1.0, dict(extra=dict(claw=0), lean=-8)), (grow - 0.1, dict(lean=8))])
    b.hide(sh.f(grow), True)
    g = sh.rig(BoltGiant, "boltg", x=900, y=1060, s=1.0, depth=0.3)
    g.hide(sh.f(0) - 30, True)
    g.hide(sh.f(grow), False)
    sh.anim(g, [(grow, dict(eyes="angry", sq=0.7, extra=dict(claw=0))), (grow + 0.2, dict(sq=1.1, ease="snap")), (grow + 0.4, dict(sq=1.0)),
                (grab - 0.3, dict(eyes="up", extra=dict(claw=20))),
                (grab, dict(eyes="googly", extra=dict(claw=-40), lean=-6, ease="snap")),
                (sh.end, dict(eyes="googly", extra=dict(claw=-40), lean=-4))])
    lamp = fx.prop(sh, "shinybell", lambda pen: (pen.shape(geo.blob([(-40, 0), (-30, -60), (0, -80), (30, -60), (40, 0)], n=3), GOLD, 5, hi=0.6),
                                                  pen.fill(geo.circle(0, 6, 10), "#b88a10")),
                   [(0, 1500, 640, 0, 1.4), (grab, 1500, 640, 0, 1.4), (grab + 0.3, 1290, 420, 20, 1.4), (sh.end, 1290, 420, 20, 1.4)], depth=0.2)
    fx.flash(sh, grow, "#ffffff", frames=3)
    fx.dust(sh, 900, 960, grow, n=24, spread=420, rise=200, col="#f0e0c0", seed=9, size=2.0)
    fx.banner(sh, "BIG SHELL TIME!", grow + 0.1, grow + 1.6, col="#ff8a5c", accent=GOLD)
    fx.timer_hud(sh, grow, sh.end, start=30)
    for k, t in enumerate((0.45, 0.85)):
        fx.world_text(sh, "CLICK!", 760 + k * 220, 760, 50, t0=t, t1=t + 0.5, col="#ff8a5c", depth=-0.6, rot=0.1 * (k * 2 - 1))
    fx.sparks(sh, 1500, 620, grab - 0.4, col=GOLD, n=10, dur=0.4, spread=120)
    sh.cam.move([(sh.f(0), 900, 800, 1.5), (sh.f(grow), 900, 800, 1.5), (sh.f(grow + 0.1), 960, 540, 0.95), (sh.f(sh.end), 1000, 540, 1.0)])
    sh.cam.shake(sh.f(grow), sh.f(grow + 0.6), 24, 0.3)


@shot("s5_train", preview=(1.0, 2.0, 2.8, 5.8, 7.6))
def s5_train(sh):
    sets.harbor(sh, "day", stilts=True, horizon=470)
    sets.card(sh.co, "yard", 0.8, lambda pen: (pen.fill(geo.rect(-1400, 900, 3400, 1500), "#d8c098"),
                                                 [sets.crate(pen, 1500 + (k % 3) * 125, 900 - (k // 3) * 122, 120, seed=k) for k in range(6)]))
    c1, c2, c3, punch = sh.cue("clang1"), sh.cue("clang2"), sh.cue("clang3"), sh.cue("punch")
    launch, crash = sh.cue("launch"), sh.cue("crash")
    X, Y, S = 760, 1000, 1.0
    j = sh.rig(Junk, "junk", x=X, y=Y, s=S)
    j.show(sh.f(0) - 30, "head", "streak")
    l1 = sh.line(1)
    keys = [(0, dict(eyes="closed", brows="angry", mouth="flat", hand_f=(40, -300), hand_b=(-40, -300), hf="fist", hb="fist", lean=0)),
            (0.3, dict(mouth="shout", eyes="dot")),
            (c1, dict(hand_f=(-120, -330), lean=-10, foot_f=(70, -8), foot_b=(-80, -8))),
            (punch - 0.1, dict(hand_f=(-160, -330), lean=-14)),
            (punch, dict(hand_f=(360, -320), lean=18, foot_f=(150, -8), foot_b=(-60, -8), eyes="dot", brows="angry", ease="snap")),
            (punch + 0.8, dict(hand_f=(340, -320))),
            (l1[0] - 0.2, dict(hand_f=(60, -260), hand_b=(-60, -260), lean=0, foot_f=(20, -8), foot_b=(-20, -8), eyes="happy", mouth="grin")),
            (launch, dict(x=X, y=Y, eyes="huge", mouth="shout", hand_f=(150, -500), hand_b=(-150, -480), hf="open", hb="open")),
            (launch + 0.6, dict(x=X + 160, y=Y - 340, lean=30, ease="out")),
            (launch + 1.0, dict(x=X + 300, y=Y - 220, lean=-40, ease="io")),
            (launch + 1.4, dict(x=X + 500, y=Y - 420, lean=50)),
            (crash, dict(x=1640, y=Y - 120, lean=80, eyes="spiral", mouth="jaw", ease="in")),
            (sh.end, dict(x=1640, y=Y - 60, lean=95))]
    sh.anim(j, keys)
    sh.lipsync(j, "JUNK", base="shout")
    # the fist assembles in three clangs
    pieces = [(-700, -200), (2600, 100), (-600, 900)]
    for k, (t, (sx, sy)) in enumerate(zip((c1, c2, c3), pieces)):
        tgt = at(X, Y, S, 1, -130, -330)
        o = fx.prop(sh, f"flyin{k}", (lambda kk: (lambda pen: sets.scrap_piece(pen, 0, 0, 2.0, kind=(0, 2, 6)[kk], seed=kk)))(k),
                    [(t - 0.5, sx, sy, 0, 1.0), (t, tgt[0], tgt[1], 400, 1.0)], depth=-0.2, stepped=False)
        fx.vis(o, t - 0.5, t + 0.05, sh)
        fx.burst(sh, tgt[0], tgt[1], t, col=TEAL, r1=140, seed=20 + k, depth=-0.4)
        fx.world_text(sh, "CLANG", tgt[0] + 60 - k * 90, tgt[1] - 140 - k * 30, 60, t0=t, t1=t + 0.5, col="#ffffff", depth=-0.7, rot=0.2 - k * 0.2)
    fist_keys = [(c3, *at(X, Y, S, 1, -150, -330), 0, 0.8), (punch - 0.1, *at(X, Y, S, 1, -170, -330), 0, 0.85),
                 (punch, *at(X, Y, S, 1, 390, -320), 0, 1.0), (punch + 0.8, *at(X, Y, S, 1, 370, -320), 0, 1.0)]
    fist = fx.prop(sh, "fist", lambda pen: sets.hubcap_fist(pen, 0, 0, 1.0), fist_keys, depth=-0.15, fx=[fx.glow_fx(TEAL, 20)])
    fx.vis(fist, c3, punch + 1.0, sh)
    fx.crumble(sh, 1625, 780, punch + 0.05, w=380, h=260, col="#c8925a", seed=6, dur=1.2, wind=(500, -200))
    fx.impact_frame(sh, punch, frames=2, col=TEAL)
    fx.banner(sh, "HUBCAP HAYMAKER!", c1 - 0.2, punch + 0.9, col=TEAL, accent=GOLD)
    glow = stage.glow_disc(sh.co, "aura", X, Y - 250, 500, TEAL, 0.0, depth=0.2)
    for t, v in ((0, 0.0), (c1, 0.8), (punch + 1.0, 0.0), (launch, 0.6), (crash, 0.0)):
        stage.key_strength(glow, sh.f(t), v)
    # rocket clunkers: teal flame from the boots during the flight
    flames = {}
    for f in range(sh.f(launch), sh.f(crash), 1):
        flames[f] = None
    jet = fx.prop(sh, "jets", lambda pen: [pen.shape(geo.blob([(-20, 0), (20, 0), (8, 90), (0, 130), (-8, 90)], n=3), TEAL, 4, shade=0.2, hi=0.6)],
                  [(launch, X, Y + 20, 0, 1.0), (launch + 0.6, X + 160, Y - 320, 30, 1.0), (launch + 1.0, X + 300, Y - 200, -40, 1.0),
                   (launch + 1.4, X + 500, Y - 400, 50, 1.0), (crash, 1640, Y - 100, 80, 1.0)], depth=0.05, fx=[fx.glow_fx(TEAL, 30)])
    fx.vis(jet, launch, crash, sh)
    fx.banner(sh, "ROCKET CLUNKERS!", l1[0], launch + 1.2, col=TEAL, accent="#e8392f", y=200, name="banner2")
    fx.dust(sh, 1640, 860, crash, n=20, spread=280, rise=160, seed=12)
    fx.world_text(sh, "CRASH!", 1500, 480, 140, t0=crash, t1=sh.end, col=GOLD, depth=-0.8, rot=-0.2)
    sh.cam.move([(sh.f(0), 860, 640, 1.15), (sh.f(punch), 960, 600, 1.0), (sh.f(launch), 960, 600, 1.0), (sh.f(crash), 1300, 520, 1.0),
                 (sh.f(sh.end), 1400, 560, 1.15)])
    sh.cam.shake(sh.f(punch), sh.f(punch + 0.4), 22, 0.3)
    sh.cam.shake(sh.f(crash), sh.f(crash + 0.5), 22, 0.3)


@shot("s6_tincan", preview=(1.0, 3.5))
def s6_tincan(sh):
    sets.harbor(sh, "day", stilts=True, horizon=470)

    def sign(pen):
        g = TPen(pen, 960, 300, 1.0, -0.06)
        g.shape(geo.rect(-460, -70, 460, 70), "#f4f1e6", 6, shade=0.4)
        g.line([(-440, -70), (-500, -220)], 4)
        g.line([(440, -70), (520, -240)], 4)
    sets.card(sh.co, "tincan_sign", 1.0, sign)
    fx.world_text(sh, "TIN CAN KID", 960, 330, 110, col="#e8392f", depth=0.95, rot=-0.06, fname="lucky", ink="#1b1424")
    sets.crowd_card(sh, "cheer_l", 0.8, -300, 650, 1100, n=7, s=1.1, seed=7, cheer=True)
    sets.crowd_card(sh, "cheer_r", 0.8, 1270, 2220, 1100, n=7, s=1.1, seed=8, cheer=True)
    j = sh.rig(Junk, "junk", x=960, y=1020, s=1.0)
    j.show(sh.f(0) - 30, "head", "streak")
    l1 = sh.line(1)
    sh.anim(j, [(0, dict(eyes="happy", mouth="grin", hand_f=(80, -200), hand_b=(-80, -200))),
                (l1[0], dict(eyes="happy", hand_f=(150, -520), hf="thumb", hand_b=(-60, -230), lean=-6, ease="back")),
                (sh.end, dict(hand_f=(160, -540)))])
    sh.lipsync(j, "JUNK", base="grin")
    j.show(sh.f(l1[0]), "head", "blush")
    fx.speedlines(sh, l1[0], sh.end, 960, 520, GOLD, inner=420, n=40, seed=31, alpha=0.5)
    sh.cam.move([(sh.f(0), 960, 520, 1.0), (sh.f(sh.end), 960, 560, 1.12)])
