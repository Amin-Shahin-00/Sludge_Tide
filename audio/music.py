"""SLUDGE TIDE - original score, synthesized.

Two themes, as in the series notes:
  JUNK  - clanky percussion (pots, pipes, wrenches) + brass, C major, 132 bpm, hopeful
  RUST  - slow dripping cello with a ticking clock underneath, D minor, 66 bpm
In the final fight both themes play at the same time. The noodle-bowl walk is silence.
Cues are placed on the shot timeline (config/timeline.py), so re-timing the edit
re-times the score.

Output: build/audio/music.wav (48 kHz stereo float)
"""
import math, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import timeline as TL  # noqa: E402

SR = 48000
N = int((TL.DURATION + 2) * SR)
L = np.zeros(N, np.float32)
R = np.zeros(N, np.float32)
rng = np.random.default_rng(7)


def S(sid):
    return TL.shot(sid)["start"]


def E(sid):
    return TL.shot(sid)["end"]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, min(f, SR * 0.45), "low", fs=SR, output="sos"), x).astype(np.float32)


def bp(x, lo, hi, o=2):
    return signal.sosfilt(signal.butter(o, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x).astype(np.float32)


def env(n, a=0.01, d=0.1, s=0.7, r=0.1):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.full(n, s, np.float32)
    m = t < a
    e[m] = t[m] / max(a, 1e-4)
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / max(d, 1e-4)
    m = t > dur - r
    e[m] *= np.clip((dur - t[m]) / max(r, 1e-4), 0, 1)
    return e


def add(x, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    x = x[: N - i]
    L[i:i + len(x)] += x * g * math.cos((pan + 1) * math.pi / 4)
    R[i:i + len(x)] += x * g * math.sin((pan + 1) * math.pi / 4)


# ----------------------------------------------------------------------------- instruments

def saw(f, n, det=0.0, vib=0.0, vr=5.5):
    t = np.arange(n) / SR
    ph = np.cumsum(f * (1 + det) * (1 + vib * np.sin(2 * np.pi * vr * t))) / SR
    return (2 * (ph % 1.0) - 1).astype(np.float32)


def cello(f, dur, vel=1.0):
    n = int(dur * SR)
    x = sum(saw(f, n, d, 0.006 * min(1, dur), 5.0) for d in (-0.003, 0.0, 0.0035)) / 3
    x = lp(x, 1400) + 0.3 * bp(x, 200, 600)
    bow = bp(rng.standard_normal(n).astype(np.float32), f, f * 6) * 0.04
    return (x + bow) * env(n, 0.12, 0.2, 0.8, min(0.4, dur * 0.3)) * vel * 0.35


def brass(f, dur, vel=1.0, bright=2200):
    n = int(dur * SR)
    x = (saw(f, n, 0.0, 0.004) + saw(f, n, 0.004, 0.004)) * 0.5
    e = env(n, 0.03, 0.08, 0.75, 0.06)
    return lp(x * e, bright * (0.5 + 0.5 * vel)) * vel * 0.33


def strings(f, dur, vel=1.0, att=0.5, bright=1600):
    n = int(dur * SR)
    x = sum(saw(f, n, d, 0.004, 5.3 + d * 30) for d in (-0.006, 0.0, 0.005)) / 3
    return lp(x, bright) * env(n, att, 0.2, 0.85, min(0.8, dur * 0.4)) * vel * 0.25


def piano(f, dur, vel=1.0):
    n = int(max(dur, 1.6) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k, a in enumerate((1.0, 0.45, 0.25, 0.12, 0.06)):
        x += a * np.sin(2 * np.pi * f * (k + 1) * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.6 + 1.2 * k))
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * vel * 0.3


def glock(f, vel=1.0):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 3.5) * vel * 0.2).astype(np.float32)


def bass(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.tanh(1.6 * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)))
    return x * env(n, 0.01, 0.12, 0.65, 0.08) * vel * 0.4


def pad(f, dur, vel=1.0):
    """Choir-ish pad: saws through two vowel formants."""
    n = int(dur * SR)
    x = sum(saw(f * m, n, d, 0.005, 4.8) for m, d in ((1, 0), (1, 0.004), (2, -0.003))) / 3
    y = bp(x, 500, 900) + 0.6 * bp(x, 1000, 1400)
    return y * env(n, min(1.2, dur * 0.3), 0.3, 0.9, min(1.0, dur * 0.3)) * vel * 0.35


def metal(f0, vel=1.0, dec=6.0):
    """Clanky percussion: inharmonic modes - pots, pipes, wrenches."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k, (m, a) in enumerate(((1.0, 1.0), (2.32, 0.6), (3.87, 0.4), (5.41, 0.25), (6.9, 0.15))):
        x += a * np.sin(2 * np.pi * f0 * m * t + k) * np.exp(-t * dec * (1 + 0.4 * k))
    x += bp(rng.standard_normal(n).astype(np.float32), 2000, 9000) * np.exp(-t * 60) * 0.4
    return x * vel * 0.25


def kick(vel=1.0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) * vel * 0.8).astype(np.float32)


def taiko(vel=1.0):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    f = 60 + 60 * np.exp(-t * 14)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) + lp(rng.standard_normal(n).astype(np.float32), 600) * np.exp(-t * 20) * 0.5
    return (x * vel * 0.8).astype(np.float32)


def snare(vel=1.0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    x = bp(rng.standard_normal(n).astype(np.float32), 1500, 8000) * np.exp(-t * 20) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return x * vel * 0.32


def tick(vel=1.0, hi=True):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (2400 if hi else 1700) * t) * np.exp(-t * 90) + bp(rng.standard_normal(n).astype(np.float32), 2500, 7000)
            * np.exp(-t * 120)) * vel * 0.3


def drip(vel=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = 900 + 1400 * t / 0.3
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * vel * 0.18


def hit(t0, g=1.0, minor=True, root=38):
    add(taiko(1.0), t0, g)
    for m in (0, 3 if minor else 4, 7, 12):
        add(brass(hz(root + 12 + m), 1.2, 1.0, 1500), t0, g * 0.5)


def swell(t0, dur, g=0.4):
    n = int(dur * SR)
    x = bp(rng.standard_normal(n).astype(np.float32), 1500, 10000) * (np.arange(n) / n) ** 3
    add(x * 0.5, t0, g, -0.3)
    add(np.roll(x, 400) * 0.5, t0, g, 0.3)


def drone(t0, t1, m, g=0.2, kind="strings"):
    d = t1 - t0
    if d <= 0:
        return
    fn = strings if kind == "strings" else pad
    add(fn(hz(m), d, 1.0, att=min(2.0, d * 0.3)) if kind == "strings" else fn(hz(m), d), t0, g)


# ----------------------------------------------------------------------------- themes

C_MAJ = [0, 2, 4, 5, 7, 9, 11]
D_MIN = [0, 2, 3, 5, 7, 8, 10]


def deg(d, sc):
    d -= 1
    return 12 * (d // 7) + sc[d % 7]


JUNK_MEL = [(3, 1), (5, 1), (6, 1), (5, 1), (8, 1.5), (7, 0.5), (6, 1), (5, 1),
            (3, 1), (5, 1), (6, 1), (8, 1), (9, 3), (0, 1),
            (8, 1), (9, 1), (10, 1), (9, 1), (8, 1.5), (6, 0.5), (5, 2),
            (6, 1), (5, 1), (3, 1), (2, 1), (1, 3), (0, 1)]
JUNK_CH = [1, 4, 1, 5, 4, 5, 4, 1]
RUST_MEL = [(1, 2), (0, 1), (3, 1), (2, 2), (1, 2), (-3, 3), (0, 1), (-2, 1.5), (-3, 0.5), (-4, 1), (-3, 1), (1, 4)]


def junk_theme(t0, t1, tonic=60, bpm=132, layers=("brass", "metal", "bass", "kick", "glock"), vel=1.0, mel=True):
    beat = 60 / bpm
    t, i, bar = t0, 0, 0
    while t < t1 - 1e-3:
        # comp + percussion per bar (4 beats)
        ch = JUNK_CH[bar % len(JUNK_CH)]
        root = tonic - 24 + deg(ch, C_MAJ)
        for b in range(4):
            tb = t + b * beat
            if tb >= t1:
                break
            if "bass" in layers:
                add(bass(hz(root + (7 if b % 2 else 0)), beat * 0.9, 0.9 * vel), tb, 0.8)
            if "kick" in layers and b in (0, 2):
                add(kick(0.8 * vel), tb, 0.7)
            if "metal" in layers:
                add(metal(rng.choice([520, 610, 780, 940, 1250]), 0.7 * vel), tb + beat * 0.5, 0.6, pan=rng.uniform(-0.5, 0.5))
                if b % 2:
                    add(metal(330, 0.9 * vel, 4), tb, 0.6, pan=0.3)
            if "snare" in layers and b in (1, 3):
                add(snare(0.7 * vel), tb, 0.6)
            if "brass" in layers and b in (1, 3):
                for m in (deg(ch, C_MAJ), deg(ch + 2, C_MAJ), deg(ch + 4, C_MAJ)):
                    add(brass(hz(tonic - 12 + m), beat * 0.45, 0.5 * vel, 1600), tb, 0.35, pan=-0.3)
        bar += 1
        t += 4 * beat
    if mel:
        t = t0 + 4 * beat
        k = 0
        while t < t1 - 1e-3:
            d, b = JUNK_MEL[k % len(JUNK_MEL)]
            if d:
                f = hz(tonic + deg(d, C_MAJ))
                add(brass(f, b * beat * 0.92, 0.9 * vel, 2600), t, 0.55, pan=0.1)
                if "glock" in layers and b >= 1.5:
                    add(glock(f * 2, vel), t, 0.5, pan=0.4)
            t += b * beat
            k += 1


def rust_theme(t0, t1, tonic=50, bpm=66, vel=1.0, clock=True, drips=True, mel=True, low=True):
    beat = 60 / bpm
    if clock:
        t, k = t0, 0
        while t < t1:
            add(tick(0.6 * vel, k % 2 == 0), t, 0.5, pan=0.5 if k % 2 else -0.5)
            t += beat / 2
            k += 1
    if low:
        add(strings(hz(tonic - 12), t1 - t0, 0.8 * vel, att=1.5, bright=500), t0, 0.5)
    if mel:
        t, k = t0 + 2 * beat, 0
        while t < t1 - beat:
            d, b = RUST_MEL[k % len(RUST_MEL)]
            if d:
                dd = d if d > 0 else d + 8
                m = tonic + deg(dd, D_MIN) - (12 if d < 0 else 0)
                add(cello(hz(m), b * beat * 1.02, vel), t, 0.7, pan=-0.1)
            t += b * beat
            k += 1
    if drips:
        t = t0 + 1.0
        while t < t1:
            add(drip(0.8 * vel), t, 0.4, pan=rng.uniform(-0.6, 0.6))
            t += rng.uniform(1.2, 2.6)


def tender(t0, t1, tonic=60, vel=0.8, strings_on=True):
    """Piano + soft strings (Granny, the noodle bowl aftermath)."""
    prog = [1, 6, 4, 5]
    beat = 0.75
    t, k = t0, 0
    while t < t1 - 0.2:
        ch = prog[k % 4]
        notes = [deg(ch, C_MAJ), deg(ch + 2, C_MAJ), deg(ch + 4, C_MAJ)]
        for j, m in enumerate(notes + [notes[1] + 12]):
            add(piano(hz(tonic + m), 1.8, 0.6 * vel), t + j * beat, 0.5, pan=-0.2 + 0.15 * j)
        if strings_on:
            add(strings(hz(tonic - 12 + notes[0]), 4 * beat, 0.6 * vel, att=1.0, bright=1100), t, 0.5)
        t += 4 * beat
        k += 1


def suspense(t0, t1, root=50, g=0.35):
    add(strings(hz(root - 12), t1 - t0, 0.8, att=1.0, bright=500), t0, g)
    add(strings(hz(root - 11), t1 - t0, 0.5, att=2.0, bright=700), t0, g * 0.6, pan=0.4)
    t = t0
    while t < t1:
        add(strings(hz(root + 12), 0.18, 0.4, att=0.01, bright=2500), t, g * 0.5, pan=-0.3)
        t += 0.5


def sting(t0, kind="comedy", g=0.6):
    if kind == "comedy":
        for k, m in enumerate((72, 76, 79, 84)):
            add(glock(hz(m)), t0 + k * 0.07, g)
    elif kind == "slide":
        n = int(0.7 * SR)
        f = np.linspace(700, 200, n)
        add((np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.01, 0.1, 0.7, 0.2) * 0.3).astype(np.float32), t0, g)
    elif kind == "boing":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = 220 * (1 + 0.5 * np.sin(2 * np.pi * 12 * t) * np.exp(-t * 4))
        add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.4).astype(np.float32), t0, g)


# ----------------------------------------------------------------------------- the cue sheet

def build():
    # COLD OPEN: low drone, the drip, the title hit (teal major / orange minor at once)
    drone(0.0, 2.3, 38, 0.25, "pad")
    hit(TL.cue("o1_drip", "hit"), 0.9)
    for m in (60, 64, 67, 72):
        add(brass(hz(m), 3.5, 0.8, 1800), TL.cue("o1_drip", "hit") + 0.1, 0.25, pan=-0.4)
    for m in (62, 65, 69):
        add(cello(hz(m - 12), 3.5, 0.8), TL.cue("o1_drip", "hit") + 0.1, 0.4, pan=0.4)
    swell(S("n1_isle") - 1.2, 1.2, 0.2)

    # 1. THE NIGHT SHIFT - Rust's theme, before he is Rust: thin, clock, drips
    rust_theme(S("n1_isle"), S("n3_vat"), vel=0.6, mel=False)
    rust_theme(S("n3_vat"), S("n4_phone"), vel=0.7, mel=True, clock=True)
    suspense(S("n4_phone"), S("n8_struggle"), 50, 0.3)
    hit(S("n5_magnus") + 0.05, 0.6)
    junk_theme(S("n8_struggle"), E("n8_struggle"), tonic=50, bpm=150, layers=("metal", "kick", "snare", "bass"), mel=False, vel=0.8)
    # the fall: slow-motion choir, the "Hey, you"s, a massive orange hit at the splash
    drone(S("n9_fall"), TL.cue("n9_fall", "splash"), 38, 0.35, "pad")
    drone(S("n9_fall") + 3.0, TL.cue("n9_fall", "splash"), 45, 0.25, "pad")
    hit(TL.cue("n9_fall", "splash"), 1.0)
    rust_theme(S("n10_orange"), E("n10_orange"), vel=1.0, mel=True, clock=True)
    add(piano(hz(62), 2.0, 0.6), S("n11_paper") + 4.4, 0.5)
    add(piano(hz(57), 2.5, 0.5), S("n11_paper") + 5.8, 0.5)

    # 2. THE BLOOM - Junk's theme arrives
    swell(S("b1_card") - 1.0, 1.0, 0.25)
    junk_theme(S("b1_card"), S("b4_cloud"), bpm=132, vel=0.8)
    suspense(S("b4_cloud"), S("b6_dive"), 50, 0.3)
    junk_theme(S("b6_dive"), E("b6_dive"), tonic=62, bpm=160, layers=("metal", "kick", "snare"), mel=False, vel=0.9)
    drone(S("b7_fall"), TL.cue("b7_fall", "teal"), 38, 0.35, "pad")
    drone(S("b7_fall") + 3.0, TL.cue("b7_fall", "teal"), 45, 0.25, "pad")
    tl = TL.cue("b7_fall", "teal")
    add(taiko(1.0), tl, 0.9)
    for m in (60, 64, 67, 72, 76):
        add(brass(hz(m), 2.6, 1.0, 2600), tl, 0.35)
        add(pad(hz(m), 2.6, 0.8), tl, 0.25)
    junk_theme(S("b8_bubble"), E("b8_bubble"), bpm=132, vel=1.0)
    sting(S("b9_glow") + TL.shot("b9_glow")["lines"][1]["start"], "comedy")

    # 3. SCRAP HEART - bouncy comedy
    junk_theme(S("s1_ceiling"), E("s6_tincan"), bpm=140, vel=0.75, layers=("metal", "bass", "kick", "glock", "brass"))
    sting(TL.cue("s2_bonk", "bonk"), "boing", 0.8)
    sting(TL.cue("s3_bikes", "pile"), "slide", 0.6)
    hit(TL.cue("s4_bolt", "grow"), 0.5, minor=False, root=36)
    hit(TL.cue("s5_train", "punch"), 0.6, minor=False, root=36)
    sting(TL.cue("s5_train", "crash"), "slide", 0.6)

    # 4. BARON RUST
    rust_theme(S("r1_fog"), S("r5_swarm"), vel=0.9)
    hit(TL.cue("r2_collapse", "crash"), 0.8)
    junk_theme(S("r5_swarm"), S("r7_notice"), tonic=50, bpm=150, layers=("metal", "kick", "snare", "bass"), mel=False, vel=0.9)
    rust_theme(S("r7_notice"), S("r8_fist"), vel=0.8, mel=False)
    junk_theme(S("r8_fist"), TL.cue("r8_fist", "touch"), bpm=150, vel=0.9, layers=("brass", "metal", "kick", "snare"))
    hit(TL.cue("r8_fist", "touch"), 0.9)
    junk_theme(S("r9_lesson"), E("r9_lesson"), tonic=50, bpm=150, layers=("metal", "kick", "snare"), mel=False, vel=0.8)
    rust_theme(S("r10_kneel"), E("r11_threat"), vel=0.9)
    hit(S("r11_threat") + TL.shot("r11_threat")["lines"][1]["end"], 0.9)
    rust_theme(S("r12_boat"), E("r12_boat"), vel=0.5, mel=True, clock=False)

    # 5. THE TRUTH
    tender(S("t1_bandage"), E("t1_bandage"), vel=0.6)
    t = S("t2_sela")
    while t < E("t2_sela"):                                        # sneaky pizzicato
        for k, m in enumerate((62, 65, 69, 65)):
            add(strings(hz(m - 12), 0.12, 0.6, att=0.005, bright=2400), t + k * 0.25, 0.45, pan=-0.3 + 0.2 * k)
        t += 1.0
    suspense(S("t3_safe"), E("t4_lights"), 50, 0.35)
    hit(TL.cue("t4_lights", "lights"), 0.7)
    junk_theme(S("t5_escape"), E("t5_escape"), bpm=150, vel=1.0)

    # 6. THREE DAYS
    tender(S("p1_theory"), E("p1_theory"), vel=0.5, strings_on=False)
    tender(S("p2_granny"), E("p2_granny"), vel=0.8)
    junk_theme(S("p3_faster") + 2.0, E("p4_stay"), bpm=126, vel=0.7, layers=("brass", "bass", "metal", "glock"))

    # 7. ROT VS. REBUILD - both themes at once
    rust_theme(S("f1_army"), E("f2_why"), vel=1.0)
    hit(S("f3_round1"), 0.9)
    junk_theme(S("f3_round1"), E("f3_round1"), bpm=150, vel=1.0, layers=("brass", "metal", "kick", "snare", "bass"))
    beat_t, gap = S("f4_blur") + 0.8, 0.5
    while beat_t < E("f4_blur"):
        add(taiko(0.9), beat_t, 0.7)
        add(metal(780, 0.8), beat_t + gap / 2, 0.6)
        beat_t += gap
        gap = max(0.083, gap * 0.86)
    rust_theme(S("f5_rain"), E("f5_rain"), vel=1.0, clock=True)
    swell(S("f6_titan"), TL.cue("f6_titan", "slam") - 0.0, 0.5)
    hit(TL.cue("f6_titan", "slam"), 1.0, minor=False, root=36)
    junk_theme(TL.cue("f6_titan", "slam"), E("f8_clash"), bpm=132, vel=1.0, layers=("brass", "metal", "kick", "snare", "bass", "glock"))
    rust_theme(S("f7_throne"), E("f8_clash"), vel=1.0, clock=True, drips=False)
    for t in (TL.cue("f8_clash", "hit1"), TL.cue("f8_clash", "hit2"), TL.cue("f8_clash", "crack")):
        hit(t, 0.8)
    suspense(S("f9_rig"), E("f10_hoses"), 38, 0.45)
    hit(TL.cue("f10_hoses", "latch"), 0.8)
    junk_theme(S("f11_logs") + 2.0, E("f11_logs"), bpm=120, vel=0.8, layers=("brass", "bass", "glock"))
    rust_theme(S("f12_hears"), E("f13_collapse"), vel=1.0, clock=True)
    hit(TL.cue("f12_hears", "touch"), 0.9)
    hit(TL.cue("f13_collapse", "splash"), 1.0)
    rust_theme(S("f14_rage"), E("f14_rage"), vel=1.0, clock=True)
    junk_theme(S("f14_rage"), E("f14_rage"), tonic=50, bpm=150, layers=("kick", "snare", "metal"), mel=False, vel=0.9)
    # f15: silence except the rain (no music)
    add(piano(hz(72), 3.0, 0.5), S("f16_granny") + 1.0, 0.5)
    tender(S("f17_fade") + 2.6, E("f17_fade"), vel=0.6)

    # 8. WHAT ROTS, WHAT STAYS
    junk_theme(S("e1_rebuild"), E("e2_paper"), bpm=120, vel=0.7, layers=("brass", "bass", "metal", "glock"))
    rust_theme(S("e3_cell"), E("e3_cell"), vel=0.5, mel=True, clock=False)
    tender(S("e4_cliff"), E("e4_cliff"), vel=0.7)
    rust_theme(S("e5_rattle"), E("e5_rattle"), vel=0.7, mel=True, clock=True)
    hit(S("e6_title") + 0.4, 0.9, minor=False, root=36)
    junk_theme(S("e6_title") + 0.4, E("e6_title") - 0.5, bpm=132, vel=0.9)
    rust_theme(S("e6_title") + 0.4, E("e6_title") - 0.5, vel=0.6, clock=False, drips=False)
    drone(S("e7_post"), E("e7_post"), 33, 0.4, "pad")
    for t in TL.cue("e7_post", "crack"):
        add(taiko(0.6), t, 0.5)
        add(glock(hz(rng.choice([79, 84, 86]))), t, 0.4)

    # reverb, then silence the noodle-bowl walk completely
    def verb(x, rt=2.0, wet=0.2, seed=3):
        r = np.random.default_rng(seed)
        n = int(SR * rt)
        tt = np.arange(n) / SR
        ir = r.standard_normal(n) * np.exp(-6.9 * tt / rt)
        ir = signal.sosfilt(signal.butter(2, [150, 6000], "band", fs=SR, output="sos"), ir)
        ir[: int(0.02 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        return x + wet * signal.fftconvolve(x, ir)[: len(x)].astype(np.float32)
    st = np.stack([verb(L, seed=1), verb(R, seed=2)], 1)
    a, b = int(S("f15_bowl") * SR), int(E("f15_bowl") * SR)
    fd = int(0.6 * SR)
    st[a:a + fd] *= np.linspace(1, 0, fd)[:, None]
    st[a + fd:b] = 0
    st = st[: int(TL.DURATION * SR)]
    st /= max(1e-6, np.max(np.abs(st))) / 0.8
    out = ROOT / "build" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    sf.write(out / "music.wav", st.astype(np.float32), SR, subtype="FLOAT")
    print("music ->", out / "music.wav", f"{len(st) / SR:.1f}s")


if __name__ == "__main__":
    build()
