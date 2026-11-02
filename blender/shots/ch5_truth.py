"""CHAPTER 5: THE GIRL IN THE FACTORY."""
import math
import numpy as np
from bl import sets, fx, stage, geo, gp
from bl.gp import TPen
from bl.shot import walk_keys
from bl.cast.junk import Junk
from bl.cast.others import Granny, Sela, Magnus, Bolt, BoltGiant
from . import shot

TEAL, GOLD, ORANGE, PURPLE = "#2cfff0", "#ffd23c", "#ff7a1a", "#9a5ad0"
NIGHT = "#2a3470"


@shot("t1_bandage", preview=(2.0, 6.0, 9.6))
def t1_bandage(sh):
    sets.noodle_interior(sh, night=True)
    stage.glow_disc(sh.co, "lamp", 960, 300, 900, "#ffb060", 0.6, depth=1.0)
    j = sh.rig(Junk, "junk", x=1180, y=1000, s=1.0, face=-1)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    g = sh.rig(Granny, "granny", x=760, y=1000, s=1.05)
    L = [sh.line(k) for k in range(3)]
    sh.anim(g, [(0, dict(eyes="dot", brows="worried", mouth="flat", hand_f=(200, -300), hf="bandage", hand_b=(-110, -80))),
                (0.5, dict(hand_f=(240, -330))), (1.0, dict(hand_f=(200, -290))),
                (L[0][0], dict(eyes="half", brows="neutral", hand_f=(140, -180), hf="open", head=-6)),
                (L[1][0], dict(eyes="dot", brows="angry", hand_f=(220, -260), hf="point", head=4)),
                (L[2][0], dict(eyes="dot", brows="up", hand_f=(150, -180), hf="open")),
                (sh.end, dict(eyes="dot", brows="up"))])
    sh.lipsync(g, "GRANNY", base="flat")
    sh.blink(g, [3.2, 6.8])
    sh.anim(j, [(0, dict(eyes="closed", brows="worried", mouth="frown", hand_f=(80, -230), hand_b=(-60, -150), head=10)),
                (L[0][0] + 1.0, dict(eyes="dot", head=0)),
                (L[1][0] + 1.4, dict(eyes="dot", brows="up", mouth="o")),
                (L[2][0] - 0.2, dict(eyes="dot", brows="angry", mouth="frown", lean=10, hand_f=(140, -300), hf="fist", ease="snap")),
                (sh.end, dict(lean=12))])
    sh.lipsync(j, "JUNK", base="frown")
    sh.blink(j, [5.0])
    sh.cam.move([(sh.f(0), 960, 600, 1.1), (sh.f(L[2][0]), 1040, 560, 1.18), (sh.f(L[2][0] + 0.1), 1140, 520, 1.45), (sh.f(sh.end), 1150, 520, 1.47)])


@shot("t2_sela", preview=(0.8, 2.5, 5.5, 7.6))
def t2_sela(sh):
    sets.hallway(sh)
    d0 = sh.cue("drone")
    L = [sh.line(k) for k in range(3)]
    j = sh.rig(Junk, "junk", x=520, y=1000, s=0.95)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    j.tint(NIGHT, 0.2)
    keys = walk_keys(j.p, 0, d0, 360, 640, base=dict(s=0.95, lean=16, eyes="dot", brows="angry", mouth="flat", hand_f=(120, -330), hand_b=(-40, -330),
                                                     hf="flat", hb="flat"), step=0.3, lift=40, bob=4)
    keys += [(d0 + 0.1, dict(keys[-1][1], lean=-14, eyes="shock", brows="high", mouth="jaw", hand_f=(80, -460), hand_b=(-120, -470), hf="open", hb="open", ease="snap")),
             (L[1][0] - 0.2, dict(lean=0, eyes="dot", brows="angry", mouth="shout", hand_f=(260, -360), hf="point")),
             (L[1][1], dict(eyes="huge", brows="high", mouth="o")),
             (L[2][1], dict(eyes="dot", brows="worried", mouth="wobble", hand_f=(60, -230), hf="open")),
             (sh.end, dict(eyes="dot"))]
    sh.anim(j, keys)
    sh.lipsync(j, "JUNK", base="shout")
    b = sh.rig(Bolt, "bolt", x=430, y=1010, s=1.4)
    sh.anim(b, [(0, dict(x=280, eyes="googly")), (d0, dict(x=470)), (d0 + 0.1, dict(eyes="huge", sq=1.3, ease="snap")), (sh.end, dict(x=470, eyes="googly"))])
    s = sh.rig(Sela, "sela", x=1500, y=1000, s=1.0, face=-1)
    s.tint(NIGHT, 0.15)
    sh.anim(s, [(0, dict(x=1700, eyes="half", brows="angry", mouth="smirk", hand_f=(60, -400), hf="open", hand_b=(-30, -150))),
                (L[0][0], dict(x=1240, eyes="half", brows="angry")),
                (L[2][0], dict(eyes="closed", brows="up", mouth="smirk", lean=-4, hand_f=(20, -300), hand_b=(-20, -290))),
                (sh.end, dict(eyes="half", brows="angry", mouth="smirk"))])
    sh.lipsync(s, "SELA", base="smirk")
    dk = [(d0, 1300, 360, 0, 0.2), (d0 + 0.3, 780, 560, 0, 1.0)]
    for t in np.arange(d0 + 0.5, sh.end, 0.4):
        dk.append((t, 790 + 10 * math.sin(t * 7), 560 + 8 * math.sin(t * 5), 4 * math.sin(t * 6), 1.0))
    dr = fx.prop(sh, "drone", lambda pen: sets.drone(pen), dk, depth=-0.2, fx=[fx.glow_fx("#ff3a3a", 14)])
    fx.vis(dr, d0, None, sh)
    fx.world_text(sh, "BEEP!", 900, 440, 54, t0=d0 + 0.3, t1=d0 + 1.0, col="#ff6a6a", depth=-0.7)
    fx.speedlines(sh, d0 + 0.1, d0 + 0.8, 760, 560, "#ffffff", inner=300, n=40, seed=5, alpha=0.6)
    sh.cam.move([(sh.f(0), 600, 600, 1.1), (sh.f(d0), 700, 600, 1.1), (sh.f(L[0][0]), 960, 600, 1.0), (sh.f(L[1][0]), 900, 600, 1.05),
                 (sh.f(L[2][0]), 1160, 560, 1.15), (sh.f(sh.end), 1160, 560, 1.17)])


def photo(pen):
    g = TPen(pen, 0, 0, 1.0)
    g.shape(geo.rect(-130, -100, 130, 100), "#f4f1e6", 5, shade=0.3)
    g.fill(geo.rect(-112, -84, 112, 70), "#1c3a1c")
    g.fill(geo.ellipse(0, 70, 110, 30, 20), "#5dff7a")
    g.fill(geo.circle(30, 0, 44), "#e2b33c")
    g.fill(geo.circle(30, -54, 22), "#f2b8a0")
    g.fill(geo.rect(14, -96, 46, -72), "#202028")


@shot("t3_safe", preview=(1.0, 4.0, 7.0, 10.0))
def t3_safe(sh):
    sets.office(sh)
    op = sh.cue("open")
    L = [sh.line(k) for k in range(3)]
    door = fx.prop(sh, "safedoor", lambda pen: (pen.shape(geo.rrect(-160, -200, 160, 200, 16), "#6a7080", 5, hi=0.3),
                                                 pen.shape(geo.circle(0, 0, 60), "#8a909c", 5, hi=0.4)),
                   [(0, 1400, 560, 0, 1.0), (op, 1400, 560, 0, 1.0), (op + 0.6, 1260, 560, 0, 0.25)], depth=-0.05, stepped=True)
    s = sh.rig(Sela, "sela", x=980, y=1060, s=1.0)
    j = sh.rig(Junk, "junk", x=640, y=1060, s=0.95)
    for k in ("streak", "bandage"):
        j.show(sh.f(0) - 30, "head", k)
    keys = [(0, dict(eyes="dot", brows="neutral", mouth="flat", hand_f=(200, -380), hf="open", hand_b=(-40, -150))),
            (op + 0.6, dict(hand_f=(60, -260), hf="logs", eyes="dot", brows="worried")),
            (L[1][0], dict(eyes="huge", brows="worried", mouth="frown"))]
    for k, t in enumerate(np.arange(L[1][0], L[2][1], 1 / 6)):
        keys.append((t, dict(hand_f=(60 + (6 if k % 2 else -6), -260 + (4 if k % 2 else -4)), ease="hold")))
    keys.append((sh.end, dict(eyes="sad", brows="worried", mouth="frown", hand_f=(60, -260))))
    sh.anim(s, keys)
    sh.lipsync(s, "SELA", base="frown")
    s.show(sh.f(L[1][0]), "head", "sweat")
    sh.anim(j, [(0, dict(eyes="dot", brows="up", mouth="o", hand_f=(80, -200), hand_b=(-60, -200))),
                (L[2][0] + 1.0, dict(eyes="shock", brows="high", mouth="jaw", ease="snap")),
                (sh.end, dict(eyes="shock", mouth="jaw"))])
    # inserts: the photo, then the blueprint
    ins1 = fx.prop(sh, "photo", photo, [(L[0][0] + 0.8, 1300, 380, -6, 0.2), (L[0][0] + 1.1, 1320, 380, -4, 1.4)], depth=-0.5)
    fx.vis(ins1, L[0][0] + 0.8, L[1][0], sh)
    bp = fx.prop(sh, "blueprint", lambda pen: (pen.fill(geo.rect(-760, -440, 760, 440), "#1c4a8a"), sets.leviathan(pen, 0, -40, 0.62, blue=True)),
                 [(L[2][0] - 0.2, 960, 540, 0, 0.3), (L[2][0] + 0.1, 960, 520, 0, 1.0), (sh.end, 960, 520, 0, 1.04)], depth=-1.2)
    fx.vis(bp, L[2][0] - 0.2, sh.end + 1, sh)
    t = fx.world_text(sh, "LEVIATHAN RIG", 960, 230, 110, t0=L[2][0] + 0.3, col="#e8f4ff", depth=-1.3, ink="#0c2a5a", fname="anton")
    fx.world_text(sh, "CAPTURE.  DRAIN.  BOTTLE.  SELL.", 960, 930, 56, t0=L[2][0] + 1.0, col="#ffd23c", depth=-1.3, ink="#0c2a5a", fname="anton")
    sh.cam.move([(sh.f(0), 1100, 600, 1.0), (sh.f(L[0][0]), 1000, 580, 1.08), (sh.f(L[2][0]), 960, 560, 1.0), (sh.f(sh.end), 960, 540, 1.06)])


@shot("t4_lights", preview=(0.1, 1.5, 3.5))
def t4_lights(sh):
    sets.office(sh)
    lt = sh.cue("lights")
    dark = fx.fade_card(sh, -1.0, lt, "#05040a", 0.75, 0.75, name="dark", clear_after=True)
    m = sh.rig(Magnus, "magnus", x=960, y=1100, s=1.25)
    sh.anim(m, [(0, dict(eyes="dot", mouth="grin", brows="neutral", hand_f=(200, -150), hand_b=(-200, -150))),
                (sh.line(0)[0], dict(hand_f=(260, -330), hf="open", hand_b=(-260, -330), hb="open", ease="back")),
                (sh.line(1)[0], dict(eyes="happy", head=6)),
                (sh.end, dict(eyes="half", brows="angry"))])
    sh.lipsync(m, "MAGNUS", base="grin")
    fx.smoke(sh, 960 + 11, 1100 - 590 * 1.25, sh.line(1)[0], sh.end, col=PURPLE, every=0.35, depth=-0.2, rise=200, size=0.9)
    fx.flash(sh, lt, "#ffffff", frames=2, alpha=0.8)
    fx.world_text(sh, "CLICK", 1500, 300, 70, t0=lt, t1=lt + 0.7, col="#ffffff", depth=-0.7)
    sh.cam.move([(sh.f(0), 960, 520, 1.0), (sh.f(sh.end), 960, 470, 1.15)])


@shot("t5_escape", preview=(0.9, 2.6, 3.4, 5.0))
def t5_escape(sh):
    grow, smash, build, land = sh.cue("grow"), sh.cue("smash"), sh.cue("build"), sh.cue("land")
    sets.gloam_isle_night(sh)
    wall = sets.card(sh.co, "wall_t5", 0.2, lambda pen: (pen.fill(geo.rect(-600, -400, 2500, 1500), "#4a2f3a"),
                                                         [pen.line([(-600, y), (2500, y)], 4, col="#3a222c") for y in range(-400, 1500, 80)]))
    fx.vis(wall, -1, smash, sh)
    fx.crumble(sh, 960, 540, smash, w=1600, h=1000, col="#6a3a48", seed=5, dur=1.4, depth=-0.3, wind=(0, 300))
    fx.flash(sh, smash, "#ffffff", frames=2)
    fx.world_text(sh, "KRAKOOM!", 960, 380, 160, t0=smash, t1=smash + 1.0, col=GOLD, depth=-0.9, rot=-0.1)
    fx.banner(sh, "BIG SHELL TIME!", grow, smash + 0.4, col="#ff8a5c", accent=GOLD, y=200)
    fx.timer_hud(sh, grow, sh.end, start=30)
    bg = sh.rig(BoltGiant, "boltg", x=960, y=1300, s=1.0, depth=-0.1)
    sh.anim(bg, [(grow, dict(eyes="angry", extra=dict(claw=-30))), (smash, dict(eyes="angry", extra=dict(claw=30), lean=10, y=1250, ease="snap")),
                 (build, dict(y=1700, lean=-20, eyes="googly", ease="in")), (sh.end, dict(y=1900))])
    for cls, tag, x, kw in ((Junk, "junk", 820, dict(hf="open", hb="open")), (Sela, "sela", 1100, dict(hf="logs", hb="open"))):
        r = sh.rig(cls, tag, x=x, y=700, s=0.75)
        if tag == "junk":
            for k in ("streak", "bandage"):
                r.show(sh.f(0) - 30, "head", k)
        r.hide(sh.f(0) - 30, True)
        r.hide(sh.f(smash), False)
        sh.anim(r, [(smash, dict(y=-200, eyes="shock", brows="high", mouth="shout", lean=-20, hand_f=(80, -500), hand_b=(-80, -500), **kw)),
                    (build, dict(y=600, lean=10, ease="lin")),
                    (land, dict(y=900, lean=0, eyes="dot" if tag == "sela" else "happy", mouth="grin" if tag == "junk" else "o", ease="in")),
                    (sh.end, dict(x=x + 600, y=900, ease="in"))])
        if tag == "junk":
            sh.lipsync(r, "JUNK", base="grin")
    rk = [(build, 960, 1300, 0, 0.3), (land - 0.2, 960, 920, 0, 1.0), (land, 960, 930, 0, 1.0), (sh.end, 1560, 930, 0, 1.0)]
    rf = fx.prop(sh, "raft_t5", lambda pen: sets.raft(pen, 0, 0, 0.9, seed=70), rk, depth=-0.05, fx=[fx.glow_fx(TEAL, 20)])
    fx.vis(rf, build, None, sh)
    fx.sparks(sh, 960, 1000, build, col=TEAL, n=26, dur=0.6, spread=500)
    fx.splash(sh, 960, 950, land, s=1.6, seed=13)
    sh.cam.move([(sh.f(0), 960, 540, 1.2), (sh.f(smash), 960, 540, 1.0), (sh.f(build), 960, 640, 0.95), (sh.f(sh.end), 1200, 640, 1.0)])
    sh.cam.shake(sh.f(smash), sh.f(smash + 0.5), 26, 0.3)
