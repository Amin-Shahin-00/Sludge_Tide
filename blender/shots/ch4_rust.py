"""CHAPTER 4: BARON RUST."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.rust import BaronRust
from bl.cast.others import Granny
from . import shot

ORANGE, PURPLE, TEAL, GOLD = "#ff7a1a", "#7a3cb4", "#2cfff0", "#ffd23c"
FOGT = "#9fb0b8"


def lighthouse_bent(pen, x, base, sag=0.0, rust=0.0, fall=0.0):
    """Lighthouse that rusts (white/red -> orange/brown) and bends like a melting candle."""
    def warp(P):
        P = np.asarray(P, float).copy()
        h = np.clip((base - P[:, 1]) / 500.0, 0, 1.3)
        P[:, 0] += sag * 260 * h ** 2
        P[:, 1] += sag * 110 * h ** 2
        if fall:
            c, s = math.cos(fall), math.sin(fall)
            d = P - (x, base)
            P = np.stack([x + c * d[:, 0] - s * d[:, 1], base + s * d[:, 0] + c * d[:, 1]], 1)
        return P

    def col(c):
        return gp.hexs(gp.mix(gp.mix(c, "#d8641e", min(1, rust * 1.4)), "#6a2a10", max(0, rust - 0.6) * 1.5))
    pen.shape(warp(geo.spline([(x - 60, base), (x - 36, base - 420), (x + 36, base - 420), (x + 60, base)], n=8, tension=0.05)), col("#f4f1e6"), 5, depth=16)
    for k in range(3):
        y = base - 70 - k * 120
        pen.shape(warp(geo.spline([(x - 56 + k * 7, y), (x + 56 - k * 7, y), (x + 52 - k * 7, y - 50), (x - 52 + k * 7, y - 50)], closed=True, n=4, tension=0.05)),
                  col("#e8392f"), 4, shade=0.4)
    pen.shape(warp(geo.spline([(x - 44, base - 500), (x + 44, base - 500), (x + 44, base - 420), (x - 44, base - 420)], closed=True, n=4, tension=0.05)),
              col("#3a3a46"), 5)
    pen.fill(warp(geo.rect(x - 32, base - 490, x + 32, base - 430)), gp.hexs(gp.mix("#ffe9a0", "#ff8a1e", rust)))
    pen.shape(warp(geo.spline([(x - 54, base - 500), (x + 54, base - 500), (x, base - 560)], closed=True, n=4, tension=0.05)), col("#c8432f"), 5)
    if rust > 0.2:
        r = np.random.default_rng(3)
        for k in range(int(30 * rust)):
            yy = base - r.uniform(0, 500)
            pen.fill(warp(geo.circle(x + r.uniform(-40, 40), yy, r.uniform(6, 16), 10)), "#8a3a14", 0.8)


def fog_scene(sh, stilts=False, horizon=600, lighthouse=False):
    sets.harbor(sh, "fog", stilts=stilts, lighthouse=lighthouse, horizon=horizon)
    fx.fog(sh, "far", horizon - 120, horizon + 40, 10, alpha=0.5, seed=1)
    fx.fog(sh, "near", horizon + 120, horizon + 400, 1.5, alpha=0.35, drift=-160, seed=2)


def rust_walk_keys(t0, t1, x0, x1, y0, y1, s0, s1, step=1.15, base=None):
    keys = []
    n = max(1, int((t1 - t0) / (step / 2)))
    for i in range(n + 1):
        u = i / n
        t = t0 + (t1 - t0) * u
        k = dict(base or {})
        k.update(x=x0 + (x1 - x0) * u, y=y0 + (y1 - y0) * u, s=s0 + (s1 - s0) * u, bob=-10 if i % 2 else 0,
                 sway=0, chest=3 if i % 2 else -2, ease="io")
        k.pop("sway")
        keys.append((t, k))
    return keys


@shot("r1_fog", preview=(1.0, 4.5))
def r1_fog(sh):
    fog_scene(sh, horizon=640)
    d = {}
    for f in range(sh.f(0), sh.f(sh.end) + 1, 2):
        u = sh.t(f) / sh.end
        d[f] = (lambda uu: (lambda pen: lighthouse_bent(pen, 1500, 760, sag=0.5 * max(0, uu - 0.35) ** 1.5, rust=min(1, uu * 1.6))))(u)
    fx.fxcard(sh, "lighthouse", 6, d)
    sets.crowd_card(sh, "market", 0.6, -200, 2100, 1120, n=14, s=1.2, seed=11, shade=("#8a96a0", 0.35))
    fx.world_text(sh, "CREEEAK", 1300, 260, 64, t0=sh.cue("creak"), t1=sh.end, col="#ff9a5a", depth=-0.8, rot=0.15)
    sh.cam.move([(sh.f(0), 900, 760, 1.0), (sh.f(sh.end), 1240, 420, 1.15)])


@shot("r2_collapse", preview=(0.6, 1.8, 3.0))
def r2_collapse(sh):
    fog_scene(sh, horizon=640)
    crash = sh.cue("crash")
    d = {}
    for f in range(sh.f(0), sh.f(crash) + 1, 2):
        u = min(1.0, sh.t(f) / crash)
        d[f] = (lambda uu: (lambda pen: lighthouse_bent(pen, 1500, 760, sag=0.5 + 0.6 * uu, rust=1.0, fall=1.2 * uu ** 2)))(u)
    d[sh.f(crash) + 2] = None
    fx.fxcard(sh, "lighthouse", 6, d)
    fx.splash(sh, 1700, 760, crash, s=2.4, col="#dfe8ea", seed=9, depth=5.5)
    fx.crumble(sh, 1700, 700, crash, w=600, h=200, col="#a8501a", seed=4, dur=1.6, depth=5.5, wind=(160, -200))
    sets.crowd_card(sh, "market2", 0.6, -200, 2100, 1120, n=14, s=1.2, seed=11, shade=("#8a96a0", 0.35))
    fx.world_text(sh, "KER-SPLOOSH!", 1500, 380, 110, t0=crash, t1=sh.end, col="#ffffff", depth=-0.8, rot=-0.1)
    sh.cam.shake(sh.f(crash), sh.f(crash + 1.0), 24, 0.4)
    sh.cam.move([(sh.f(0), 1240, 460, 1.1), (sh.f(sh.end), 1200, 560, 1.0)])


@shot("r3_walk", preview=(1.0, 5.0))
def r3_walk(sh):
    fog_scene(sh, horizon=520)
    r = sh.rig(BaronRust, "rust", x=960, y=640, s=0.3, depth=0.0)
    r.tint(FOGT, 0.55, f=sh.f(0))
    r.tint(FOGT, 0.15, f=sh.f(sh.end))
    sh.anim(r, rust_walk_keys(0, sh.end, 960, 960, 640, 1040, 0.3, 0.75,
                              base=dict(eyes="glow", brows="neutral", mouth="closed", hand_f=(110, -230), hand_b=(-110, -230), hf="claw", hb="claw")))
    st0, per = sh.cue("step0"), sh.cue("period")
    k = 0
    while st0 + k * per / 2 < sh.end:
        t = st0 + k * per / 2
        u = t / sh.end
        x, y = 960 + (25 if k % 2 else -25) * (0.3 + 0.45 * u), 640 + 400 * u
        fx.bubbles(sh, x - 60, x + 60, y - 10, y + 10, t, min(sh.end, t + 1.0), n=8, col="#ffb05a", seed=40 + k, depth=-0.05, rise=60, size=0.8, glow=ORANGE)
        k += 1
    fx.mite_swarm(sh, "march", [(0, 960, 560, 0.25), (sh.end, 960, 760, 0.5)], n=40, w=1600, h=120, seed=3, depth=0.5)
    g = stage.glow_disc(sh.co, "rustglow", 960, 700, 500, ORANGE, 0.6, depth=0.6)
    sh.cam.move([(sh.f(0), 960, 560, 1.1), (sh.f(sh.end), 960, 600, 1.0)])


@shot("r4_bow", preview=(1.4, 4.5, 9.0, 13.5))
def r4_bow(sh):
    fog_scene(sh, horizon=420)
    sets.card(sh.co, "dock_r4", 0.4, lambda pen: (pen.fill(geo.rect(-1400, 1000, 3400, 1500), "#7a5a3a"),
                                                   [pen.line([(-1400 + k * 140, 1000), (-1400 + k * 140, 1500)], 3) for k in range(36)]))
    r = sh.rig(BaronRust, "rust", x=1000, y=1040, s=0.95)
    r.tint(FOGT, 0.1)
    L = [sh.line(k) for k in range(4)]
    base = dict(eyes="glow", brows="neutral", mouth="closed", hand_f=(150, -250), hand_b=(-150, -250), hf="claw", hb="claw")
    sh.anim(r, [(0, base),
                (L[0][0], dict(chest=0, hand_f=(260, -380), hf="open")),
                (L[0][1] - 0.3, dict(chest=38, head=20, hand_f=(120, -150), hand_b=(-240, -380), hf="flat", hb="open", ease="io")),
                (L[1][0] + 0.2, dict(chest=10, head=4, hand_f=(250, -330), hand_b=(-160, -260), hf="open", hb="claw")),
                (L[2][0], dict(chest=0, head=-6, brows="angry", hand_f=(200, -260), hf="claw")),
                (L[3][0], dict(chest=-4, head=-10, hand_f=(160, -420), hf="point", brows="neutral")),
                (L[3][1], dict(chest=14, head=8, hand_f=(120, -200), hand_b=(-120, -200), hf="flat", hb="flat")),
                (sh.end, dict(chest=12))])
    sh.lipsync(r, "RUST", base="closed")
    sh.blink(r, [3.0, 8.4], base="glow")
    stage.glow_disc(sh.co, "rustglow", 1000, 700, 700, ORANGE, 0.5, depth=0.8)
    sets.crowd_card(sh, "front", -0.6, -400, 2300, 1420, n=12, s=1.6, seed=21, rows=1, shade=("#1a1820", 0.8))
    sh.cam.move([(sh.f(0), 1000, 560, 1.0), (sh.f(L[2][0]), 1000, 480, 1.12), (sh.f(L[3][0]), 1010, 380, 1.3), (sh.f(sh.end), 1010, 380, 1.32)])


@shot("r5_swarm", preview=(1.0, 3.0))
def r5_swarm(sh):
    fog_scene(sh, horizon=480)
    sets.card(sh.co, "dock_r5", 0.4, lambda pen: (pen.fill(geo.rect(-1400, 960, 3400, 1500), "#7a5a3a"),
                                                   [sets.boat(pen, -300 + k * 520, 960, 1.2, seed=k) for k in range(6)]))
    fx.mite_swarm(sh, "eat", [(0, 400, 1060, 1.0), (sh.end, 1500, 1060, 1.0)], n=70, w=1600, h=200, seed=7, depth=0.1, eye="happy")
    for k in range(4):
        fx.crumble(sh, 200 + k * 520, 900, 0.4 + k * 0.7, w=260, h=120, col="#c8641e", seed=60 + k, dur=1.4, depth=0.2)
        fx.world_text(sh, "CHOMP", 220 + k * 520, 760, 60, t0=0.4 + k * 0.7, t1=1.0 + k * 0.7, col=ORANGE, depth=-0.6, rot=0.2 - k * 0.1)
    run = sets.crowd_card(sh, "runners", -0.2, -200, 1800, 1300, n=10, s=1.3, seed=31, cheer=True)
    run.location.x = 0
    run.keyframe_insert("location", frame=sh.f(0))
    run.location.x = -12.0
    run.keyframe_insert("location", frame=sh.f(sh.end))
    fx.world_text(sh, "AAAAH!", 600, 520, 90, t0=0.3, t1=sh.end, col="#ffffff", depth=-0.7, rot=-0.1)
    sh.cam.shake(sh.f(0), sh.f(sh.end), 8, 0.6)


@shot("r6_junk", preview=(1.0, 2.6))
def r6_junk(sh):
    fog_scene(sh, horizon=420)
    sets.crowd_card(sh, "flee", -0.3, -300, 2200, 1350, n=10, s=1.5, seed=41, cheer=True, rows=1, shade=("#5a6068", 0.4))
    j = sh.rig(Junk, "junk", x=960, y=1060, s=1.2)
    j.show(sh.f(0) - 30, "head", "streak")
    keys = walk_keys(j.p, 0, sh.end, 700, 1060, base=dict(s=1.2, lean=14, eyes="dot", brows="angry", mouth="shout", hb="fist", hf="fist"),
                     step=0.24, lift=40, bob=10, swing=70)
    sh.anim(j, keys)
    sh.lipsync(j, "JUNK", base="shout")
    fx.speedlines(sh, 0, sh.end, 960, 540, "#ffffff", n=40, seed=6, alpha=0.5, kind="parallel", angle=math.pi)
    sh.cam.move([(sh.f(0), 760, 560, 1.15), (sh.f(sh.end), 1080, 540, 1.2)])


@shot("r7_notice", preview=(0.8, 3.5))
def r7_notice(sh):
    fog_scene(sh, horizon=380)
    r = sh.rig(BaronRust, "rust", x=880, y=1700, s=1.7)
    l0, l1 = sh.line(0), sh.line(1)
    sh.anim(r, [(0, dict(eyes="glow", brows="neutral", mouth="closed", head=0, hand_f=(150, -250), hand_b=(-150, -250))),
                (l0[0] - 0.3, dict(head=-18, eyes="wide", brows="up", ease="snap")),
                (l1[0] + 1.2, dict(head=-10, eyes="narrow", brows="angry")),
                (sh.end, dict(head=-8))])
    sh.lipsync(r, "RUST", base="closed")
    stage.glow_disc(sh.co, "eyesglow", 1040, 520, 420, ORANGE, 0.5, depth=0.5)
    sh.cam.move([(sh.f(0), 980, 520, 1.0), (sh.f(sh.end), 1020, 470, 1.15)])


def rust_and_junk(sh, rust_x=1300, junk_x=560, y=1040, rs=0.85, js=0.9):
    sets.card(sh.co, f"dock_{sh.sid}", 0.4, lambda pen: (pen.fill(geo.rect(-1400, 1000, 3400, 1500), "#7a5a3a"),
                                                         [pen.line([(-1400 + k * 140, 1000), (-1400 + k * 140, 1500)], 3) for k in range(36)]))
    r = sh.rig(BaronRust, "rust", x=rust_x, y=y, s=rs, face=-1)
    j = sh.rig(Junk, "junk", x=junk_x, y=y, s=js)
    j.show(sh.f(0) - 30, "head", "streak")
    return r, j


@shot("r8_fist", preview=(1.4, 2.4, 3.6))
def r8_fist(sh):
    fog_scene(sh, horizon=420)
    r, j = rust_and_junk(sh, rust_x=1350, junk_x=640)
    swing, touch, dust = sh.cue("swing"), sh.cue("touch"), sh.cue("dust")
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(-140, -330), hand_b=(-60, -260), hf="fist", lean=-10, foot_f=(70, -8), foot_b=(-80, -8))),
                (swing, dict(hand_f=(420, -320), lean=20, x=760, foot_f=(150, -8), ease="snap")),
                (touch, dict(hand_f=(430, -320), x=770)),
                (dust + 0.3, dict(eyes="huge", brows="high", mouth="jaw")),
                (sh.end, dict(eyes="huge", mouth="jaw", lean=6, hand_f=(300, -300), hf="open"))])
    sh.lipsync(j, "JUNK", base="shout")
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(150, -250), hand_b=(-150, -250))),
                (touch - 0.4, dict(hand_f=(260, -380), hf="point")),
                (touch, dict(hand_f=(300, -400), hf="point", ease="snap")),
                (sh.end, dict(hand_f=(240, -380), hf="point"))])
    fist_tip = (770 + 0.9 * 430, 1040 - 0.9 * 320)
    fk = [(0.3, 640 - 0.9 * 150, 1040 - 0.9 * 330, 180, 0.7), (swing, fist_tip[0] - 80, fist_tip[1], 0, 0.85), (touch, fist_tip[0] - 70, fist_tip[1], 0, 0.85)]
    fist = fx.prop(sh, "fist", lambda pen: sets.hubcap_fist(pen, 0, 0, 1.0), fk, depth=-0.1, fx=[fx.glow_fx(TEAL, 20)])
    fx.vis(fist, 0.3, dust + 0.05, sh)
    fx.rot_web(sh, fist_tip[0] + 20, fist_tip[1] - 30, touch, dust, radius=220, seed=4, depth=-0.2)
    fx.crumble(sh, fist_tip[0] - 70, fist_tip[1], dust, w=420, h=220, col="#d8641e", seed=8, dur=1.6, depth=-0.15, wind=(-600, -160))
    fx.banner(sh, "HUBCAP HAYMAKER!", 0.2, swing + 0.4, col=TEAL, accent=GOLD)
    fx.impact_frame(sh, touch, frames=3, col=ORANGE)
    fx.world_text(sh, "...tap.", 1250, 360, 60, t0=touch, t1=dust + 0.8, col=ORANGE, depth=-0.7, fname="hand")
    sh.cam.move([(sh.f(0), 960, 560, 1.05), (sh.f(touch), 1060, 520, 1.2), (sh.f(sh.end), 1000, 540, 1.1)])


@shot("r9_lesson", preview=(0.6, 2.2, 3.9))
def r9_lesson(sh):
    fog_scene(sh, horizon=420)
    r, j = rust_and_junk(sh, rust_x=1400, junk_x=700)
    shield, rot, boots, plant = sh.cue("shield"), sh.cue("rot"), sh.cue("boots"), sh.cue("plant")
    sh.anim(j, [(0, dict(eyes="dot", brows="angry", mouth="shout", hand_f=(200, -350), hand_b=(160, -330), hf="open", hb="open")),
                (rot + 0.4, dict(eyes="huge", mouth="o")),
                (boots, dict(x=700, y=1000, lean=40, foot_f=(-60, -8), foot_b=(-100, -8), eyes="dot", brows="angry", mouth="shout", hand_f=(250, -200))),
                (boots + 0.6, dict(x=1100, y=900, lean=60, ease="in")),
                (plant - 0.2, dict(x=1180, y=1000, lean=80, eyes="huge")),
                (plant, dict(x=1220, y=1040, lean=96, eyes="spiral", mouth="jaw", foot_f=(-80, -60), foot_b=(-120, -40), ease="snap")),
                (sh.end, dict(x=1220, y=1040, lean=96))])
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(260, -380), hf="point", hand_b=(-150, -250))),
                (boots + 0.4, dict(x=1400)), (boots + 0.8, dict(x=1560, eyes="narrow", ease="snap")), (sh.end, dict(x=1560))])
    for k in range(4):
        x = 1000
        o = fx.prop(sh, f"manhole{k}", lambda pen: sets.scrap_piece(pen, 0, 0, 2.2, kind=6, seed=k),
                    [(shield + k * 0.08, x, 680 + k * 70, 90, 1.0)], depth=-0.1 - 0.01 * k)
        fx.vis(o, shield + k * 0.08, rot + 0.6, sh)
    fx.rot_web(sh, 1010, 780, rot, rot + 0.5, radius=200, seed=6, depth=-0.2)
    fx.crumble(sh, 1000, 780, rot + 0.5, w=200, h=300, col="#d8641e", seed=10, dur=1.0)
    fx.banner(sh, "MANHOLE WALL!", 0.0, rot + 0.3, col=TEAL, accent=GOLD, y=200, name="b1")
    fx.banner(sh, "ROCKET CLUNKERS!", boots - 0.2, plant - 0.4, col=TEAL, accent="#e8392f", y=200, name="b2")
    fx.crumble(sh, 1150, 960, plant - 0.5, w=200, h=80, col="#d8641e", seed=11, dur=0.9)
    fx.dust(sh, 1240, 1030, plant, n=16, spread=200, rise=80, seed=13)
    fx.world_text(sh, "THUD", 1300, 820, 90, t0=plant, t1=sh.end, col="#ffffff", depth=-0.7, rot=0.1)
    sh.cam.shake(sh.f(plant), sh.f(plant + 0.4), 16, 0.3)
    sh.cam.move([(sh.f(0), 1000, 560, 1.05), (sh.f(sh.end), 1150, 600, 1.15)])


@shot("r10_kneel", preview=(2.0, 6.0, 11.0, 16.0))
def r10_kneel(sh):
    fog_scene(sh, horizon=380)
    r, j = rust_and_junk(sh, rust_x=1260, junk_x=620, y=1060, rs=0.95, js=0.95)
    sh.anim(j, [(0, dict(lean=96, x=620, eyes="spiral", mouth="flat", foot_f=(-80, -60), foot_b=(-120, -40), hand_f=(60, -120), hand_b=(-20, -100))),
                (1.0, dict(eyes="closed", head=-10)),
                (3.0, dict(eyes="dot", brows="worried", mouth="frown", head=-30)),
                (sh.end, dict(eyes="dot", brows="angry", mouth="frown", head=-34))])
    L = [sh.line(k) for k in range(4)]
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(160, -250), hand_b=(-150, -250), hf="claw", hb="claw", y=1060)),
                (0.6, dict(y=1120, chest=34, head=22, hand_f=(140, -120), hf="open")),
                (L[1][0], dict(head=12, hand_f=(220, -200), hf="flat")),
                (L[2][0], dict(head=0, chest=20, hand_f=(160, -260), hf="claw", brows="angry")),
                (L[3][0], dict(chest=28, head=16, hand_f=(100, -140), hf="point", brows="neutral")),
                (sh.end, dict(chest=26))])
    sh.lipsync(r, "RUST", base="closed")
    sh.blink(r, [2.5, 9.0, 14.0], base="glow")
    stage.glow_disc(sh.co, "rustglow", 1240, 700, 600, ORANGE, 0.5, depth=0.8)
    sh.cam.move([(sh.f(0), 960, 640, 1.0), (sh.f(L[1][0]), 1000, 620, 1.08), (sh.f(L[2][0]), 1060, 580, 1.15), (sh.f(L[3][0]), 1120, 520, 1.3),
                 (sh.f(sh.end), 1130, 510, 1.33)])


@shot("r11_threat", preview=(1.0, 4.0, 7.5))
def r11_threat(sh):
    before = set(sh.co.objects)
    fog_scene(sh, horizon=460)
    r = sh.rig(BaronRust, "rust", x=960, y=1260, s=1.25)
    L = [sh.line(k) for k in range(2)]
    sh.anim(r, [(0, dict(eyes="glow", mouth="closed", hand_f=(160, -300), hand_b=(-160, -300))),
                (L[0][0], dict(hand_f=(240, -560), hf="point", ease="back")),
                (L[1][0], dict(hand_f=(300, -480), hf="open", hand_b=(-300, -480), hb="open")),
                (sh.end, dict(hand_f=(300, -480)))])
    sh.lipsync(r, "RUST", base="closed")
    sets.crowd_card(sh, "silent", -0.4, -300, 2200, 1330, n=11, s=1.4, seed=51, rows=1, shade=("#1a1820", 0.75))
    stage.glow_disc(sh.co, "rg", 960, 600, 700, ORANGE, 0.6, depth=0.8)
    a_objs = set(sh.co.objects) - before
    cut = L[1][1] + 0.2
    # insert: the six Stilts under Tumble Island
    before2 = set(sh.co.objects)
    sets.stilts_view(sh, mood="fog")
    stilts_objs = set(sh.co.objects) - before2
    for ob in a_objs:
        if ob.type != "EMPTY":
            fx.vis(ob, 0.0 - 1.0, cut, sh)
    for ob in stilts_objs:
        fx.vis(ob, cut, None, sh)
    for ob in list(sh.co.objects):
        if ob.name.startswith(f"{sh.sid}.fog") or ob.name.startswith(f"{sh.sid}.sea") or "W_" in ob.name:
            pass
    sh.cam.move([(sh.f(0), 960, 520, 1.0), (sh.f(cut - 0.05), 960, 420, 1.15), (sh.f(cut), 960, 600, 1.08), (sh.f(sh.end), 960, 560, 1.0)])
    fx.caption(sh, "THE STILTS", cut + 0.3, sh.end, y=1000, size=80, col="#ffffff")


@shot("r12_boat", preview=(1.5, 4.0, 6.0))
def r12_boat(sh):
    fog_scene(sh, horizon=470)
    sets.card(sh.co, "hotpot", 1.2, lambda pen: sets.noodle_boat(pen, 760, 900, 1.2, lit=True))
    stage.glow_disc(sh.co, "lanterns", 760, 700, 500, "#ffb060", 0.5, depth=1.4)
    r = sh.rig(BaronRust, "rust", x=1700, y=1060, s=0.85, face=-1)
    keys = rust_walk_keys(0, 1.8, 1700, 1250, 1060, 1060, 0.85, 0.85,
                          base=dict(face=-1, eyes="glow", mouth="closed", hand_f=(110, -230), hand_b=(-110, -230)))
    keys += [(2.0, dict(keys[-1][1], head=-6, eyes="glow", chest=0)),
             (2.6, dict(head=14, chest=6, eyes="glow_down")),
             (4.4, dict(head=16, eyes="closed", brows="worried")),
             (4.8, dict(head=4, eyes="glow", brows="neutral"))]
    keys += [(t, dict(k, eyes="glow", brows="neutral", head=0)) for t, k in rust_walk_keys(4.9, sh.end, 1250, 600, 1060, 1000, 0.85, 0.6,
                                                                                         base=dict(face=-1, hand_f=(110, -230), hand_b=(-110, -230)))]
    sh.anim(r, keys)
    r.tint(FOGT, 0.0, f=sh.f(4.9))
    r.tint(FOGT, 0.6, f=sh.f(sh.end))
    fx.fog(sh, "front", 700, 1100, -0.5, alpha=0.3, drift=-220, seed=9, puffs=6)
    sh.cam.move([(sh.f(0), 1100, 600, 1.0), (sh.f(sh.end), 900, 600, 1.05)])
