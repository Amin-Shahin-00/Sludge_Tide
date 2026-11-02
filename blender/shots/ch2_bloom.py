"""CHAPTER 2: THE BLOOM."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.others import Bolt, Pip
from . import shot

GREEN, ORANGE, TEAL, GOLD = "#5dff7a", "#ff8a1e", "#2cfff0", "#ffd23c"


def swim(base, t, amp=10, k=0):
    """Floating / kicking pose offsets for underwater."""
    s = math.sin(t * 4 + k)
    return dict(base, bob=amp * math.sin(t * 2.2 + k), foot_f=(30 + 30 * s, -20 - 20 * max(0, s)), foot_b=(-40 - 30 * s, -10 - 20 * max(0, -s)))


def swim_keys(base, t0, t1, step=0.25, **kw):
    out = []
    t = t0
    while t <= t1 + 1e-6:
        out.append((t, swim(base, t, **kw)))
        t += step
    return out


@shot("b1_card", preview=(1.0, 4.0))
def b1_card(sh):
    sets.harbor(sh, "day", stilts=True)
    fx.gulls(sh, 0, sh.end, n=5)
    fx.caption(sh, "SIX MONTHS LATER", 1.2, 4.8, y=980, size=84, col="#ffffff")
    sh.cam.move([(sh.f(0), 960, 380, 1.12), (sh.f(sh.end), 960, 540, 1.0)])


def robot_arm(pen):
    g = TPen(pen, 0, 0, 1.4)
    g.tube([(-90, 20), (-10, -10), (70, 30)], 30, "#c87a3a", 5)
    g.shape(geo.circle(-10, -10, 20), "#8a5a2a", 5)
    g.shape(geo.circle(-90, 20, 18), "#8a5a2a", 5)
    g.shape(geo.blob([(70, 10), (110, -6), (120, 30), (90, 56)], n=3), "#8a909c", 5, hi=0.4)
    g.line([(110, 0), (140, -20)], 6)
    g.line([(118, 34), (146, 44)], 6)
    for k in range(3):
        g.fill(geo.circle(-60 + k * 30, 10 - k * 6, 5), "#5a3a1a")


@shot("b2_arm", preview=(1.0, 4.0, 7.0))
def b2_arm(sh):
    sets.underwater(sh)
    fx.bubbles(sh, 0, 1920, 400, 1100, 0, sh.end, n=30, depth=3.0, rise=500)
    r = sh.rig(Junk, "junk", x=900, y=900, s=1.15)
    for k in ("helmet",):
        r.show(sh.f(0) - 30, "head", k)
    base = dict(lean=-8, head=-6, eyes="huge", brows="high", mouth="shout", hand_f=(70, -300), hand_b=(-20, -300), hf="grab", hb="grab")
    L = [sh.line(k) for k in range(3)]
    keys = swim_keys(base, 0, sh.end, amp=8)
    for t, k in keys:
        if t > L[1][0]:
            k.update(eyes="happy", brows="up", mouth="grin", lean=6, head=8)
        if t > L[2][0]:
            k.update(eyes="dot", brows="neutral", mouth="grin", head=-4)
    sh.anim(r, keys)
    sh.lipsync(r, "JUNK", base="grin")
    r.show(sh.f(L[0][0]), "head", "tears")
    r.show(sh.f(L[1][0]), "head", "tears", False)
    arm_keys = [(t, 900 + 30, 900 - 1.15 * 300 + 8 * math.sin(t * 2.2), 8 * math.sin(t * 1.5), 1.0) for t in np.arange(0, sh.end + 0.01, 0.25)]
    fx.prop(sh, "robotarm", robot_arm, arm_keys, depth=-0.05)
    fx.burst(sh, 960, 380, L[0][0], col="#ffffff", r1=200, seed=2, depth=-0.6)
    sh.cam.move([(sh.f(0), 960, 520, 1.15), (sh.f(L[0][0]), 960, 520, 1.15), (sh.f(L[0][0] + 0.15), 960, 470, 1.35), (sh.f(sh.end), 960, 520, 1.2)])
    fx.speedlines(sh, L[0][0], L[0][1], 950, 420, "#ffffff", inner=420, n=50, seed=4, alpha=0.6)


@shot("b3_bolt", preview=(0.8, 3.5))
def b3_bolt(sh):
    sets.underwater(sh)
    sets.card(sh.co, "netbag", 0.5, lambda pen: sets.net_bag(pen, 780, 760, 1.4))
    b = sh.rig(Bolt, "bolt", x=730, y=820, s=2.4, depth=0.3)
    l0, l1 = sh.line(0), sh.line(1)
    keys = []
    for k, t in enumerate(np.arange(0, l0[1] + 0.3, 1 / 6)):
        keys.append((t, dict(eyes="angry", lean=6 * (1 if k % 2 else -1), extra=dict(claw=-30 if k % 2 else 10), ease="hold")))
    keys.append((l1[0], dict(eyes="googly", lean=0, extra=dict(claw=0))))
    keys.append((sh.end, dict(eyes="left", lean=-4, extra=dict(claw=-6))))
    sh.anim(b, keys)
    j = sh.rig(Junk, "junk", x=1500, y=1500, s=2.0, face=-1)
    j.show(sh.f(0) - 30, "head", "helmet")
    sh.anim(j, swim_keys(dict(lean=-6, head=-6, eyes="dot", brows="worried", mouth="smile", hand_f=(80, -280), hand_b=(-40, -230), hb="open"),
                         0, sh.end, amp=6))
    sh.lipsync(j, "JUNK", base="smile")
    for k, t in enumerate((0.45, 0.7, 0.95, 1.25)):
        fx.world_text(sh, "CLICK" if k % 2 else "click", 540 + k * 70, 520 - k * 30, 44 + k * 8, t0=t, t1=t + 0.5, col="#ff8a5c", depth=-0.6, rot=0.2 - k * 0.1)
    sh.cam.move([(sh.f(0), 880, 600, 1.1), (sh.f(sh.end), 960, 580, 1.15)])


@shot("b4_cloud", preview=(1.0, 3.5, 5.6))
def b4_cloud(sh):
    sets.underwater(sh)
    sets.card(sh.co, "barrels_b4", 2.0, lambda pen: sets.barrels(pen, 1200, 980, n=8, cracked=True, seed=3))
    fx.fish_school(sh, sh.cue("fish"), sh.cue("fish") + 1.6, 300, 500, 2400, 380, n=11, depth=3.0)
    fx.fish_school(sh, sh.cue("fish") + 0.3, sh.cue("fish") + 1.8, 600, 700, 2500, 640, n=7, col="#59c3e8", seed=22, depth=4.0)
    fx.sludge_cloud(sh, 1240, 900, sh.cue("crack"), sh.end, r0=40, r1=520, depth=1.8, rise=-260)
    g = stage.glow_disc(sh.co, "cloudglow", 1240, 820, 900, GREEN, 0.0, depth=2.5)
    stage.key_strength(g, sh.f(sh.cue("crack")), 0.0)
    stage.key_strength(g, sh.f(sh.end), 1.0)
    r = sh.rig(Junk, "junk", x=420, y=860, s=0.9, depth=0.5)
    r.show(sh.f(0) - 30, "head", "helmet")
    hu = sh.line(0)[0]
    keys = swim_keys(dict(lean=-4, head=0, eyes="happy", brows="up", mouth="grin", hand_f=(80, -230), hand_b=(-40, -230), face=-1), 0, hu - 0.3, amp=8)
    keys += [(hu - 0.2, dict(keys[-1][1], face=1, eyes="dot", mouth="o", ease="hold")),
             (hu, dict(keys[-1][1], face=1, eyes="huge", brows="high", mouth="o", head=-6, ease="snap")),
             (sh.end, dict(keys[-1][1], face=1, eyes="huge", brows="high", mouth="o", head=-8))]
    sh.anim(r, keys)
    sh.lipsync(r, "JUNK", base="o")
    r.tint(GREEN, 0.0, f=sh.f(sh.cue("crack")))
    r.tint(GREEN, 0.2, f=sh.f(sh.end))
    sh.cam.move([(sh.f(0), 760, 600, 1.0), (sh.f(sh.cue("crack")), 860, 600, 1.0), (sh.f(sh.end), 1000, 640, 0.95)])


@shot("b5_pip", preview=(1.0, 2.8, 3.6))
def b5_pip(sh):
    sets.harbor(sh, "day", stilts=False, lighthouse=True, boats=False, horizon=520)
    tip, spl, fz = sh.cue("tip"), sh.cue("splash"), sh.cue("fizz")
    bx = lambda t: 700 + 60 * t
    boat_keys = [(t, bx(t), 880 + 6 * math.sin(t * 3), 4 * math.sin(t * 2.5), 1.3) for t in np.arange(0, tip, 0.25)]
    boat_keys += [(tip + 0.3, bx(tip) + 20, 900, -35, 1.3), (spl, bx(tip) + 40, 940, -80, 1.3), (sh.end, bx(tip) + 50, 960, -95, 1.3)]
    fx.prop(sh, "fruitboat", lambda pen: sets.fruit_boat(pen), boat_keys, depth=0.05)
    p = sh.rig(Pip, "pip", x=700, y=860, s=1.1, depth=0.1)
    keys = []
    for t in np.arange(0, tip, 0.25):
        s = math.sin(t * 6)
        keys.append((t, dict(x=bx(t) - 10, y=860 + 6 * math.sin(t * 3), eyes="dot", mouth="smile", hand_f=(60 + 20 * s, -110), hand_b=(70 + 20 * s, -120),
                             hf="grab", hb="grab")))
    keys += [(fz + 0.2, dict(eyes="huge", brows="high", mouth="o")),
             (tip, dict(x=bx(tip), lean=-20, eyes="shock", mouth="shout", hand_f=(20, -220), hand_b=(-60, -200), hf="open", hb="open", ease="snap")),
             (spl, dict(x=bx(tip) + 90, y=1100, lean=-120, ease="in")),
             (sh.end, dict(x=bx(tip) + 100, y=1400, lean=-150))]
    sh.anim(p, keys)
    sh.lipsync(p, "PIP", base="shout")
    fx.bubbles(sh, 600, 1200, 900, 980, fz, sh.end, n=40, col="#9dff9a", depth=-0.1, rise=100, size=1.2, glow=GREEN)
    gl = stage.glow_disc(sh.co, "fizzglow", 920, 960, 600, GREEN, 0.0, depth=0.3)
    stage.key_strength(gl, sh.f(fz), 0.0)
    stage.key_strength(gl, sh.f(tip), 0.9)
    fx.splash(sh, bx(tip) + 80, 960, spl, s=1.1, col="#e8fbff", seed=5)
    fx.world_text(sh, "FIZZZ", 1180, 840, 54, t0=fz + 0.3, t1=tip + 0.4, col=GREEN, depth=-0.6, rot=-0.1)
    sh.cam.move([(sh.f(0), 900, 640, 1.15), (sh.f(tip), 1000, 660, 1.25), (sh.f(sh.end), 1040, 700, 1.15)])
    sh.cam.shake(sh.f(spl), sh.f(spl + 0.5), 12, 0.4)


@shot("b6_dive", preview=(0.4, 1.6))
def b6_dive(sh):
    sets.underwater(sh)
    k = sh.cue("kick")
    r = sh.rig(Junk, "junk", x=960, y=1000, s=1.0)
    r.show(sh.f(0) - 30, "head", "helmet")
    sh.anim(r, [(0, dict(eyes="dot", brows="angry", mouth="shout", lean=8, foot_f=(30, 40), foot_b=(-30, 40), hand_f=(60, -200), hand_b=(-60, -200))),
                (k, dict(y=980, foot_f=(20, 0), foot_b=(-20, 0), bob=30)),
                (k + 0.25, dict(y=600, lean=-4, foot_f=(10, 40), foot_b=(-10, 60), hand_f=(30, -620), hand_b=(-10, -640), hf="fist", hb="fist", bob=0, ease="snap")),
                (sh.end, dict(y=-200, lean=-2, ease="in"))])
    sh.lipsync(r, "JUNK", base="shout")
    fx.dust(sh, 960, 1000, k, n=16, col="#d8c8a0", seed=7, spread=260, rise=60)
    fx.speedlines(sh, k + 0.1, sh.end, 960, 540, "#e8fbff", n=50, seed=9, alpha=0.7, kind="parallel", angle=math.pi / 2)
    fx.sludge_cloud(sh, 960, 80, 0, sh.end, r0=300, r1=500, depth=1.0, rise=40, alpha=0.6)
    sh.cam.move([(sh.f(0), 960, 620, 1.0), (sh.f(k), 960, 620, 1.0), (sh.f(sh.end), 960, 260, 1.05)])


@shot("b7_fall", preview=(2.0, 5.0, 7.5, 9.2))
def b7_fall(sh):
    """Mirror of n9_fall: same camera, same slow-motion timing. Iggy's ends in orange; Junk's in teal."""
    teal = sh.cue("teal")
    bg_g = stage.gradient_bg(sh.co, "pit", [(0.0, "#a8ff60"), (0.25, "#2a6a2a"), (0.6, "#101418"), (1.0, "#08060c")], depth=30)
    stage.glow_disc(sh.co, "below", 960, 1300, 1500, GREEN, 1.2, depth=4)
    fx.bubbles(sh, 0, 1920, 900, 1200, 0, sh.end, n=40, col="#c8ffd0", depth=2, rise=500, size=2.4, glow=GREEN)
    fx.sludge_cloud(sh, 960, 640, 0, teal, r0=700, r1=760, depth=3.0, rise=0, alpha=0.35)
    pip = sh.rig(Pip, "pip", x=1200, y=520, s=0.9, depth=0.1)
    sh.anim(pip, [(0, dict(x=1240, y=420, lean=-60, eyes="shock", mouth="shout", hand_f=(80, -200), hand_b=(40, -220), hf="open", hb="open")),
                  (sh.cue("grab"), dict(x=1180, y=500, lean=-40, eyes="closed", mouth="frown")),
                  (teal, dict(x=1160, y=520, lean=-20, eyes="closed", mouth="frown")),
                  (sh.end, dict(x=1150, y=520, lean=-10, eyes="dot", mouth="o"))])
    j = sh.rig(Junk, "junk", x=820, y=900, s=0.9)
    j.show(sh.f(0) - 30, "head", "helmet")
    hang = dict(lean=-55, chest=-10, head=-45, eyes="huge", brows="high", mouth="o", hand_f=(250, -470), hand_b=(150, -520), hf="open", hb="open",
                foot_f=(220, -330), foot_b=(260, -250))
    sh.anim(j, [(0, dict(hang, x=820, y=860)),
                (sh.cue("grab"), dict(hand_f=(390, -430), hf="grab", ease="snap")),
                (2.5, dict(x=826, y=880, eyes="dot", brows="worried", mouth="frown", ease="lin")),
                (3.2, dict(eyes="closed", brows="angry", mouth="frown", head=-36)),
                (5.6, dict(brows="angry", x=832, y=900, ease="lin")),
                (sh.line(1)[1], dict(eyes="dot", brows="angry", mouth="smile")),
                (teal, dict(eyes="dot", brows="angry", mouth="grin", lean=-20, head=-10, ease="snap")),
                (sh.end, dict(eyes="dot", brows="angry", mouth="grin", x=840, y=880))])
    sh.lipsync(j, "JUNK", base="frown")
    # mirror of the "HEY, YOU." beat: the broken things he never threw away
    for k, (lt, x, y, kind) in enumerate(((3.2, 560, 380, 7), (4.0, 1380, 500, 8), (4.7, 700, 760, 5))):
        o = fx.prop(sh, f"memory{k}", (lambda kk: (lambda pen: sets.scrap_piece(pen, 0, 0, 2.0, kind=kk, seed=kk)))(kind),
                    [(lt, x, y, 0, 0.01), (lt + 0.25, x, y, -8, 1.0), (teal - 0.3, x + 20, y - 30, 8, 1.1), (teal, 960, 600, 0, 0.01)], depth=-1.0)
    j.tint(TEAL, 0.0, f=sh.f(teal - 0.5))
    j.tint(TEAL, 0.35, f=sh.f(teal))
    j.show(sh.f(teal), "head", "streak")
    fx.flash(sh, teal, "#d8fff8", frames=4)
    tg = stage.gradient_bg(sh.co, "pit_teal", [(0.0, "#fff2a0"), (0.3, "#20d8c8"), (0.7, "#0c5a6a"), (1.0, "#06222a")], depth=29)
    fx.vis(tg, teal, None, sh)
    g2 = stage.glow_disc(sh.co, "gold", 900, 600, 1200, GOLD, 0.0, depth=2)
    stage.key_strength(g2, sh.f(teal), 0.0)
    stage.key_strength(g2, sh.f(teal + 0.4), 1.2)
    fx.speedlines(sh, teal, sh.end, 880, 560, TEAL, inner=330, n=60, seed=12, alpha=0.8)
    sh.cam.move([(sh.f(0), 960, 420, 1.15), (sh.f(teal), 940, 470, 1.25), (sh.f(sh.end), 940, 480, 1.3)])


@shot("b8_bubble", preview=(1.5, 3.2, 5.0))
def b8_bubble(sh):
    sets.harbor(sh, "day", stilts=True, horizon=560)
    sets.crowd_card(sh, "docks_b8l", 1.5, -200, 560, 1070, n=7, s=0.9, seed=3, cheer=False)
    sets.crowd_card(sh, "docks_b8r", 1.5, 1380, 2140, 1070, n=7, s=0.9, seed=4, cheer=False)
    rise, pop = sh.cue("rise"), sh.cue("pop")
    bub = fx.prop(sh, "lightbubble", lambda pen: (pen.fill(geo.circle(0, 0, 260, 60), TEAL, 0.35), pen.line(geo.circle(0, 0, 260, 60), 8, "#ffffff", 0.9, closed=True),
                                                   pen.line(geo.qbez((-170, -120), (-120, -200), (-20, -230), 10), 10, "#ffffff", 0.9)),
                  [(rise, 960, 1100, 0, 0.6), (pop - 0.1, 960, 700, 0, 1.0), (pop, 960, 690, 0, 1.15)], depth=0.2, fx=[fx.glow_fx(TEAL, 40)])
    fx.vis(bub, rise, pop + 0.05, sh)
    gl = stage.glow_disc(sh.co, "bubglow", 960, 700, 800, TEAL, 0.0, depth=1.0)
    stage.key_strength(gl, sh.f(rise), 0.3)
    stage.key_strength(gl, sh.f(pop), 1.4)
    stage.key_strength(gl, sh.f(sh.end), 0.5)
    fx.flash(sh, pop, "#e8fffa", frames=3)
    fx.burst(sh, 960, 700, pop, col=GOLD, r1=420, seed=3, depth=-0.2)
    fx.sparks(sh, 960, 700, pop, col=TEAL, n=30, dur=0.8, spread=600)
    rf = sets.card(sh.co, "raft_b8", 0.3, lambda pen: sets.raft(pen, 960, 930, 1.0))
    fx.vis(rf, pop, None, sh)
    j = sh.rig(Junk, "junk", x=960, y=910, s=0.9, depth=0.25)
    j.show(sh.f(0) - 30, "head", "streak")
    j.hide(sh.f(0) - 30, True)
    j.hide(sh.f(pop), False)
    sh.anim(j, [(pop, dict(eyes="closed", mouth="grin", brows="up", hand_f=(60, -620), hand_b=(-20, -630), hf="grab", hb="grab", foot_f=(60, -8), foot_b=(-60, -8))),
                (sh.end, dict(eyes="dot", mouth="grin", bob=6))])
    p = sh.rig(Pip, "pip", x=990, y=910 - 0.9 * 600, s=0.85, depth=0.2)
    p.hide(sh.f(0) - 30, True)
    p.hide(sh.f(pop), False)
    sh.anim(p, [(pop, dict(lean=-80, eyes="closed", mouth="o", hand_f=(60, -80), hand_b=(-40, -80)))])
    fx.prop(sh, "boltcan", lambda pen: sets.scrap_piece(pen, 0, 0, 1.2, kind=3, seed=1),
            [(pop, 1300, 1010, 10), (sh.end, 1320, 1016, -6)], depth=0.1, fx=[fx.glow_fx(TEAL, 30)])
    fx.world_text(sh, "POP!", 1240, 520, 120, t0=pop, t1=pop + 1.0, col=GOLD, depth=-0.8, rot=-0.15)
    sh.cam.move([(sh.f(0), 960, 620, 0.95), (sh.f(pop), 960, 640, 1.05), (sh.f(sh.end), 960, 600, 1.2)])


@shot("b9_glow", preview=(1.2, 3.4))
def b9_glow(sh):
    sets.harbor(sh, "day", stilts=False, island=False, boats=False, horizon=700)
    p = sh.rig(Pip, "pip", x=520, y=1460, s=2.6, face=1)
    l0, l1 = sh.line(0), sh.line(1)
    sh.anim(p, [(0, dict(eyes="closed", mouth="o", lean=10, head=12, hand_f=(40, -130), hand_b=(30, -120), hf="fist")),
                (0.3, dict(head=-4, lean=-4)), (0.55, dict(head=12, lean=10)), (0.8, dict(eyes="dot", head=0, lean=0, hand_f=(80, -220), hf="point")),
                (sh.end, dict(eyes="dot", head=-2))])
    sh.lipsync(p, "PIP", base="flat")
    j = sh.rig(Junk, "junk", x=1300, y=1500, s=1.9, face=-1)
    j.show(sh.f(0) - 30, "head", "streak")
    sh.anim(j, [(0, dict(eyes="dot", mouth="grin", brows="up", hand_f=(40, -150), hand_b=(-40, -150))),
                (l1[0] - 0.4, dict(eyes="up", mouth="flat", head=-8)),
                (l1[0], dict(eyes="huge", brows="high", mouth="jaw", head=-14, ease="snap")),
                (sh.end, dict(eyes="huge", brows="high", mouth="jaw", head=-16))])
    sh.lipsync(j, "JUNK", base="jaw", shapes=("jaw", "jaw", "jaw"))
    fx.world_text(sh, "COUGH", 700, 420, 56, t0=0.1, t1=0.9, col="#ffffff", depth=-0.6, rot=0.15)
    fx.speedlines(sh, l1[0], sh.end, 1300, 420, "#ffffff", inner=380, n=60, seed=13, alpha=0.6)
    sh.cam.move([(sh.f(0), 900, 540, 1.0), (sh.f(l1[0]), 940, 540, 1.0), (sh.f(l1[0] + 0.1), 1240, 470, 1.3), (sh.f(sh.end), 1250, 470, 1.32)])
