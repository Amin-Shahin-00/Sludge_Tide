"""Sound effects and ambience beds, synthesized and placed on the shot cues.

Output: build/audio/sfx.wav (spot effects) and build/audio/beds.wav (ambience: sea,
harbor crowd, rain, fog wind, underwater) - stereo 48 kHz float.
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
rng = np.random.default_rng(99)


class Bus:
    def __init__(self):
        self.L = np.zeros(N, np.float32)
        self.R = np.zeros(N, np.float32)

    def add(self, x, t0, g=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= N or i < 0:
            return
        x = np.asarray(x, np.float32)[: N - i]
        self.L[i:i + len(x)] += x * g * math.cos((pan + 1) * math.pi / 4)
        self.R[i:i + len(x)] += x * g * math.sin((pan + 1) * math.pi / 4)


FX, BEDS = Bus(), Bus()


def S(sid):
    return TL.shot(sid)["start"]


def E(sid):
    return TL.shot(sid)["end"]


def cue(sid, name):
    return TL.cue(sid, name)


def line(sid, k):
    return TL.line(sid, k)


def noise(n):
    return rng.standard_normal(int(n)).astype(np.float32)


def bp(x, lo, hi, o=2):
    return signal.sosfilt(signal.butter(o, [lo, min(hi, 23000)], "band", fs=SR, output="sos"), x).astype(np.float32)


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x).astype(np.float32)


def hp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x).astype(np.float32)


def T(d):
    return np.arange(int(d * SR)) / SR


def fade(x, a=0.05, b=0.05):
    e = np.ones(len(x), np.float32)
    na, nb = int(a * SR), int(b * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nb:
        e[-nb:] = np.linspace(1, 0, nb)
    return x * e


# ----------------------------------------------------------------------------- sounds

def squeak():
    t = T(0.35)
    f = 1800 + 600 * np.sin(2 * np.pi * 7 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.35) * 0.18


def hum(d, f=110, buzz=True):
    t = T(d)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t) + 0.2 * np.sin(2 * np.pi * f * 3.02 * t)
    if buzz:   # beehive: amplitude flutter
        x *= 0.7 + 0.3 * np.sin(2 * np.pi * 23 * t) * np.sin(2 * np.pi * 0.7 * t)
    return fade(x.astype(np.float32) * 0.08, 0.5, 0.5)


def bubbles(d, rate=6.0):
    n = int(d * SR)
    x = np.zeros(n, np.float32)
    for k in range(int(d * rate)):
        i = rng.integers(0, max(1, n - 4000))
        L = rng.integers(1500, 4000)
        tt = np.arange(L) / SR
        f = rng.uniform(300, 900) * (1 + 3 * tt)
        x[i:i + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * rng.uniform(0.2, 0.6)
    return x * 0.5


def click():
    t = T(0.08)
    return (bp(noise(len(t)), 2000, 8000) * np.exp(-t * 120) + np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 80)) * 0.5


def whoosh(d=0.5, up=True, g=0.5):
    n = int(d * SR)
    x = noise(n)
    out = np.zeros(n, np.float32)
    seg = n // 10
    for k in range(10):
        fc = 300 + 3000 * (k / 9 if up else 1 - k / 9)
        out[k * seg:(k + 1) * seg] = bp(x, fc * 0.6, fc * 1.5)[k * seg:(k + 1) * seg]
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * g


def thud(f=80, g=1.0, d=0.5):
    t = T(d)
    return (np.sin(2 * np.pi * f * t * (1 - 0.3 * t)) * np.exp(-t * 12) + lp(noise(len(t)), 800) * np.exp(-t * 30) * 0.5) * g


def bonk():
    t = T(0.9)
    f = 520 * (1 + 0.6 * np.exp(-t * 6) * np.sin(2 * np.pi * 9 * t))
    ring = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    return (ring * 0.6 + thud(140, 0.8, 0.9)[:len(t)]) * 0.9


def clang(f0=600, g=1.0):
    t = T(1.2)
    x = sum(a * np.sin(2 * np.pi * f0 * m * t + k) * np.exp(-t * (3 + 2 * k)) for k, (m, a) in enumerate(((1, 1), (2.41, 0.7), (3.93, 0.5), (5.6, 0.3))))
    x += bp(noise(len(t)), 2500, 9000) * np.exp(-t * 50) * 0.5
    return x * 0.35 * g


def crumble(d=1.2, g=1.0):
    n = int(d * SR)
    x = np.zeros(n, np.float32)
    for k in range(int(d * 90)):
        i = rng.integers(0, max(1, n - 3000))
        L = rng.integers(300, 3000)
        x[i:i + L] += bp(noise(L), 300, 5000) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1.0)
    x += lp(noise(n), 300) * np.exp(-np.arange(n) / SR * 2) * 0.6
    return fade(x * 0.4 * g, 0.01, 0.3)


def sizzle(d=1.0, g=1.0):
    n = int(d * SR)
    am = np.abs(lp(noise(n), 30)) * 5
    return fade(bp(noise(n), 3000, 12000) * np.clip(am, 0, 2) * 0.25 * g, 0.05, 0.3)


def splash(g=1.0, big=1.0):
    d = 1.4 * big
    t = T(d)
    x = bp(noise(len(t)), 300, 6000) * np.exp(-t * 3 / big) * (1 - np.exp(-t * 60))
    x += lp(noise(len(t)), 250) * np.exp(-t * 4) * big
    x += bubbles(d, 20)[:len(t)] * 0.5
    return x * 0.6 * g


def boom(g=1.0, d=2.5):
    t = T(d)
    return (lp(noise(len(t)), 120) * 3 * np.exp(-t * 1.6) + np.sin(2 * np.pi * 42 * t) * np.exp(-t * 2.5) * 0.8) * g * 0.7


def rumble(d, g=1.0):
    n = int(d * SR)
    x = lp(noise(n), 90) * 3 * (0.6 + 0.4 * np.sin(np.arange(n) / SR * 2 * np.pi * 3))
    return fade(x * g * 0.5, 0.4, 0.6)


def creak(d=1.5, f=120):
    t = T(d)
    fm = f * (1 + 0.3 * np.sin(2 * np.pi * 0.7 * t)) + 30 * np.sin(2 * np.pi * 13 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(fm) / SR)) * 0.5
    return fade(bp(x, 200, 2500) * 0.25, 0.2, 0.4)


def jet(d, g=1.0):
    n = int(d * SR)
    x = bp(noise(n), 400, 4000) + 0.5 * hp(noise(n), 5000)
    return fade(x * 0.3 * g, 0.05, 0.2)


def suction(d, g=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = bp(noise(n), 200, 2000) * (0.6 + 0.4 * np.sin(2 * np.pi * 4 * t)) + np.sin(2 * np.pi * (80 + 20 * np.sin(2 * np.pi * 1.5 * t)) * t) * 0.3
    return fade(x * 0.35 * g, 0.2, 0.4)


def static(d, g=1.0):
    n = int(d * SR)
    return fade(bp(noise(n), 1000, 8000) * (0.5 + 0.5 * (rng.random(n) > 0.98)) * 0.12 * g, 0.05, 0.3)


def giggle(g=1.0):
    t = T(0.6)
    f0 = rng.uniform(600, 900)
    gate = (np.sin(2 * np.pi * 9 * t) > 0).astype(np.float32)
    x = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.2 * np.sin(2 * np.pi * 9 * t))) / SR) * gate * np.exp(-t * 3)
    return bp(x, 400, 4000) * 0.25 * g


def chomp():
    t = T(0.25)
    return (bp(noise(len(t)), 300, 3000) * np.exp(-t * 25) + np.sin(2 * np.pi * 160 * t) * np.exp(-t * 30) * 0.5) * 0.6


def gull():
    t = T(0.5)
    f = 1500 - 700 * t / 0.5
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / 0.5)
    return bp(x, 900, 3500) * 0.08


def bell():
    t = T(1.5)
    return sum(np.sin(2 * np.pi * 1200 * m * t) * np.exp(-t * (2 + k)) * a for k, (m, a) in enumerate(((1, 1), (2.7, 0.4), (5.2, 0.2)))) * 0.12


def slurp():
    t = T(1.2)
    f = 300 + 500 * t
    x = bp(noise(len(t)), 300, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.2
    return fade(x * 0.4, 0.05, 0.3)


def cough():
    out = []
    for k in range(2):
        t = T(0.18)
        out.append(bp(noise(len(t)), 300, 2500) * np.exp(-t * 18) * 0.6)
        out.append(np.zeros(int(0.12 * SR), np.float32))
    return np.concatenate(out)


def tear_paper():
    t = T(0.6)
    return bp(noise(len(t)), 1500, 8000) * (np.abs(lp(noise(len(t)), 80)) * 6) * 0.25


# ----------------------------------------------------------------------------- beds

def sea(d, level=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = lp(noise(n), 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t + 1)) + bp(noise(n), 1500, 6000) * 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t))
    return fade(x * 0.25 * level, 1.0, 1.0)


def crowd(d, level=1.0):
    n = int(d * SR)
    x = bp(noise(n), 250, 1600) * (0.6 + 0.8 * np.abs(lp(noise(n), 4)) * 4)
    return fade(x * 0.12 * level, 0.6, 0.6)


def cheer(d, level=1.0):
    n = int(d * SR)
    x = bp(noise(n), 400, 3000) * (0.7 + 0.6 * np.abs(lp(noise(n), 6)) * 4)
    return fade(x * 0.25 * level, 0.15, 0.8)


def screams(d, level=1.0):
    n = int(d * SR)
    out = np.zeros(n, np.float32)
    for k in range(10):
        i = rng.integers(0, max(1, n - SR))
        L = int(rng.uniform(0.4, 1.0) * SR)
        tt = np.arange(L) / SR
        f = rng.uniform(500, 900) * (1 - 0.3 * tt)
        out[i:i + L] += bp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 600, 3000) * np.sin(np.pi * tt / tt[-1]) * 0.1
    return fade(out * level, 0.1, 0.5)


def rain(d, level=1.0):
    n = int(d * SR)
    x = bp(noise(n), 500, 9000) * 0.2 + hp(noise(n), 4000) * 0.06
    drops = np.zeros(n, np.float32)
    for i in rng.integers(0, n - 400, int(d * 160)):
        L = rng.integers(80, 300)
        drops[i:i + L] += noise(L) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(0.1, 0.5)
    return fade((x + bp(drops, 800, 7000) * 0.6) * level, 0.8, 0.8)


def wind(d, level=1.0):
    n = int(d * SR)
    m = np.clip(0.5 + lp(noise(n), 1.2) * 8, 0, 2)
    return fade(bp(noise(n), 200, 1400) * m * 0.2 * level, 1.0, 1.0)


def underwater(d, level=1.0):
    n = int(d * SR)
    x = lp(noise(n), 300) * 0.5 + bubbles(d, 3) * 0.4
    return fade(x * 0.35 * level, 0.6, 0.6)


def bed(fn, sid0, sid1, g=1.0, **kw):
    a, b = S(sid0), E(sid1)
    BEDS.add(fn(b - a + 0.6, **kw), a - 0.3, g)


# ----------------------------------------------------------------------------- placement

def build():
    # cold open
    FX.add(whoosh(1.0, up=False, g=0.3), cue("o1_drip", "drip"), 0.7)
    FX.add(splash(1.0, 0.6), cue("o1_drip", "hit"), 0.8)
    FX.add(boom(0.8), cue("o1_drip", "hit"), 0.8)
    # 1. night shift
    bed(sea, "n1_isle", "n1_isle", 0.7)
    bed(wind, "n1_isle", "n1_isle", 0.5)
    bed(hum, "n2_hall", "n2_hall", 0.6, f=60, buzz=False)
    for k in range(9):
        FX.add(squeak(), S("n2_hall") + 0.4 + k * 0.62, 0.6, pan=-0.4 + 0.08 * k)
    FX.add(hum(TL.shot("n2_hall")["dur"] - cue("n2_hall", "door") + S("n2_hall") + 0.6, 220), cue("n2_hall", "door") - 0.4, 1.4, pan=0.5)
    bed(hum, "n3_vat", "n7_willhave", 1.2, f=150)
    bed(bubbles, "n3_vat", "n4_phone", 0.8)
    FX.add(click(), cue("n4_phone", "click"), 1.0, pan=0.2)
    FX.add(whoosh(0.4, up=True, g=0.3), cue("n5_magnus", "puff"), 0.5)
    for t in (cue("n8_struggle", "grab"), cue("n8_struggle", "grab") + 0.4, cue("n8_struggle", "grab") + 0.8):
        FX.add(thud(110, 0.8), t, 0.7, pan=rng.uniform(-0.3, 0.3))
    FX.add(clang(1400, 0.8), cue("n8_struggle", "snap"), 0.7)
    FX.add(thud(300, 0.6, 0.3), cue("n8_struggle", "snap"), 0.8)
    FX.add(whoosh(0.6, up=False, g=0.5), cue("n8_struggle", "slip"), 0.8)
    bed(hum, "n9_fall", "n9_fall", 1.4, f=110)
    FX.add(whoosh(2.4, up=False, g=0.4), cue("n9_fall", "letgo"), 0.7)
    FX.add(splash(1.4, 1.6), cue("n9_fall", "splash"), 1.0)
    FX.add(boom(1.0), cue("n9_fall", "splash"), 0.9)
    FX.add(sizzle(2.5, 1.2), cue("n10_orange", "rust"), 0.9)
    FX.add(crumble(2.5, 1.2), cue("n10_orange", "crumble"), 1.0)
    for k in range(10):
        FX.add(thud(90, 0.3, 0.2), cue("n10_orange", "run") + k * 0.22, 0.5, pan=0.5)
    FX.add(whoosh(0.8, up=True, g=0.4), S("n11_paper"), 0.8)
    FX.add(tear_paper(), cue("n11_paper", "land"), 0.8)
    bed(sea, "n11_paper", "n11_paper", 0.4)
    # 2. the bloom
    bed(sea, "b1_card", "b1_card", 0.9)
    bed(crowd, "b1_card", "b1_card", 0.4)
    for k in range(4):
        FX.add(gull(), S("b1_card") + 0.6 + k * 1.3, 0.6, pan=rng.uniform(-0.7, 0.7))
    bed(underwater, "b2_arm", "b4_cloud", 1.0)
    bed(bubbles, "b2_arm", "b4_cloud", 0.5)
    FX.add(whoosh(1.0, up=True, g=0.5), cue("b4_cloud", "fish"), 0.8)
    FX.add(clang(300, 0.6), cue("b4_cloud", "crack"), 0.6)
    FX.add(hum(TL.shot("b4_cloud")["dur"] - 2.0, 180), cue("b4_cloud", "crack"), 1.2)
    bed(sea, "b5_pip", "b5_pip", 0.8)
    FX.add(bubbles(2.0, 30), cue("b5_pip", "fizz"), 0.8)
    FX.add(splash(1.0, 1.0), cue("b5_pip", "splash"), 1.0)
    bed(underwater, "b6_dive", "b7_fall", 1.0)
    FX.add(whoosh(1.2, up=True, g=0.7), cue("b6_dive", "kick"), 1.0)
    bed(hum, "b7_fall", "b7_fall", 1.3, f=180)
    FX.add(boom(1.0), cue("b7_fall", "teal"), 0.8)
    bed(sea, "b8_bubble", "b9_glow", 0.8)
    bed(crowd, "b8_bubble", "b8_bubble", 0.6)
    FX.add(whoosh(2.4, up=True, g=0.4), cue("b8_bubble", "rise"), 0.7)
    FX.add(splash(1.0, 0.6), cue("b8_bubble", "pop"), 0.8)
    FX.add(bell(), cue("b8_bubble", "pop"), 1.0)
    BEDS.add(cheer(3.0), cue("b8_bubble", "pop") + 0.4, 0.8)
    FX.add(cough(), S("b9_glow") + 0.1, 0.7)
    # 3. scrap heart
    bed(crowd, "s1_ceiling", "s2_bonk", 0.15)
    FX.add(clang(900, 0.3), S("s1_ceiling") + 0.5, 0.5)
    FX.add(bonk(), cue("s2_bonk", "bonk"), 1.0)
    FX.add(clang(1600, 0.6), cue("s2_bonk", "stick"), 0.7)
    bed(sea, "s3_bikes", "s6_tincan", 0.5)
    bed(crowd, "s3_bikes", "s5_train", 0.4)
    for k in range(5):
        FX.add(bell(), S("s3_bikes") + 0.7 + k * 0.3, 0.7, pan=-0.5 + 0.25 * k)
    FX.add(crumble(0.8), cue("s3_bikes", "pile"), 0.6)
    for k in range(4):
        FX.add(clang(700 + 150 * k, 0.6), cue("s3_bikes", "pile") + k * 0.07, 0.8, pan=-0.3 + 0.2 * k)
    FX.add(whoosh(0.8, up=True, g=0.7), cue("s4_bolt", "grow") - 0.2, 0.8)
    FX.add(boom(1.0, 1.5), cue("s4_bolt", "grow"), 0.9)
    FX.add(bell(), cue("s4_bolt", "grab"), 0.9)
    for n in ("clang1", "clang2", "clang3"):
        FX.add(clang(500, 1.0), cue("s5_train", n), 1.0, pan=-0.2)
    FX.add(whoosh(0.4, up=True, g=0.7), cue("s5_train", "punch") - 0.3, 0.8)
    FX.add(boom(0.8, 1.2), cue("s5_train", "punch"), 0.9)
    FX.add(crumble(1.2), cue("s5_train", "punch") + 0.05, 0.9, pan=0.5)
    FX.add(jet(cue("s5_train", "crash") - cue("s5_train", "launch"), 1.0), cue("s5_train", "launch"), 0.8)
    FX.add(crumble(1.0), cue("s5_train", "crash"), 0.9)
    FX.add(boom(0.8, 1.2), cue("s5_train", "crash"), 0.8)
    BEDS.add(cheer(5.0), S("s6_tincan"), 0.9)
    # 4. baron rust
    bed(wind, "r1_fog", "r12_boat", 0.7)
    bed(sea, "r1_fog", "r12_boat", 0.5)
    bed(crowd, "r1_fog", "r1_fog", 0.6)
    FX.add(creak(3.0, 90), cue("r1_fog", "creak"), 0.9, pan=0.5)
    FX.add(sizzle(4.0, 0.8), cue("r1_fog", "creak") + 0.5, 0.6, pan=0.5)
    FX.add(creak(1.5, 70), S("r2_collapse"), 0.9, pan=0.5)
    FX.add(splash(1.4, 2.5), cue("r2_collapse", "crash"), 1.0, pan=0.5)
    FX.add(boom(1.2), cue("r2_collapse", "crash"), 0.9)
    BEDS.add(screams(3.0), cue("r2_collapse", "crash"), 0.9)
    t = cue("r3_walk", "step0")
    while t < E("r3_walk"):
        FX.add(sizzle(0.6, 0.8), t, 0.6)
        t += TL.shot("r3_walk")["cues"]["period"] / 2
    for k in range(14):
        FX.add(giggle(), S("r3_walk") + 1.0 + k * 0.45, 0.5, pan=rng.uniform(-0.8, 0.8))
    BEDS.add(screams(4.0, 1.2), S("r5_swarm"), 0.9)
    for k in range(10):
        FX.add(chomp(), S("r5_swarm") + 0.3 + k * 0.35, 0.8, pan=rng.uniform(-0.8, 0.8))
        FX.add(giggle(), S("r5_swarm") + 0.2 + k * 0.38, 0.5, pan=rng.uniform(-0.8, 0.8))
    for k in range(4):
        FX.add(crumble(1.2), S("r5_swarm") + 0.4 + k * 0.7, 0.6, pan=-0.6 + 0.4 * k)
    BEDS.add(screams(3.0), S("r6_junk"), 0.5)
    for k in range(16):
        FX.add(thud(100, 0.4, 0.2), S("r6_junk") + k * 0.24, 0.5)
    FX.add(clang(500, 0.8), S("r8_fist") + 0.4, 0.7)
    FX.add(whoosh(0.4, up=True, g=0.8), cue("r8_fist", "swing") - 0.3, 0.8)
    FX.add(click(), cue("r8_fist", "touch"), 1.2)
    FX.add(sizzle(0.6, 1.2), cue("r8_fist", "touch"), 0.9)
    FX.add(crumble(1.6), cue("r8_fist", "dust"), 0.9)
    FX.add(clang(400, 0.8), cue("r9_lesson", "shield"), 0.7)
    FX.add(sizzle(0.6), cue("r9_lesson", "rot"), 0.8)
    FX.add(crumble(0.9), cue("r9_lesson", "rot") + 0.5, 0.8)
    FX.add(jet(1.2), cue("r9_lesson", "boots"), 0.7)
    FX.add(thud(70, 1.2), cue("r9_lesson", "plant"), 1.0)
    FX.add(whoosh(0.6, up=False, g=0.3), S("r10_kneel") + 0.6, 0.6)
    FX.add(boom(0.6, 2.0), S("r11_threat") + TL.shot("r11_threat")["lines"][1]["end"] + 0.2, 0.8)
    for k in range(5):
        FX.add(thud(60, 0.3, 0.3), S("r12_boat") + k * 0.6, 0.4)
    # 5. the truth
    bed(rain, "t1_bandage", "t1_bandage", 0.25)
    bed(hum, "t2_sela", "t4_lights", 0.6, f=60, buzz=False)
    FX.add(whoosh(0.5, up=True, g=0.5), cue("t2_sela", "drone"), 0.8)
    FX.add(jet(TL.shot("t2_sela")["dur"] - 0.6, 0.15), cue("t2_sela", "drone") + 0.2, 0.4)
    FX.add(clang(900, 0.5), cue("t3_safe", "open"), 0.6)
    FX.add(creak(0.8, 160), cue("t3_safe", "open") + 0.1, 0.6)
    FX.add(click(), cue("t4_lights", "lights"), 1.0)
    FX.add(boom(0.6, 1.0), cue("t4_lights", "lights") + 0.05, 0.6)
    FX.add(boom(1.0, 1.5), cue("t5_escape", "grow"), 0.9)
    FX.add(crumble(1.6, 1.4), cue("t5_escape", "smash"), 1.0)
    FX.add(boom(1.2), cue("t5_escape", "smash"), 1.0)
    for k in range(6):
        FX.add(clang(600 + k * 90, 0.5), cue("t5_escape", "build") + k * 0.08, 0.6, pan=-0.5 + 0.2 * k)
    FX.add(splash(1.0, 1.2), cue("t5_escape", "land"), 1.0)
    bed(sea, "t5_escape", "t5_escape", 0.6)
    # 6. three days
    bed(crowd, "p1_theory", "p1_theory", 0.12)
    for k in range(10):
        FX.add(bp(noise(0.2 * SR), 2500, 7000) * 0.06, S("p1_theory") + 0.5 + k * 0.9, 0.6)    # chalk
    bed(sea, "p2_granny", "p3_faster", 0.5)
    bed(wind, "p2_granny", "p3_faster", 0.3)
    bonk_t = S("p3_faster") + TL.shot("p3_faster")["lines"][1]["end"] + 0.35
    FX.add(bonk() * 0.6, bonk_t, 0.7)
    bed(sea, "p4_stay", "p4_stay", 0.6)
    bed(crowd, "p4_stay", "p4_stay", 0.8)
    for k in range(8):
        FX.add(clang(rng.uniform(300, 1200), 0.4), S("p4_stay") + 0.5 + k * 0.8, 0.6, pan=rng.uniform(-0.6, 0.6))
    # 7. rot vs rebuild
    bed(sea, "f1_army", "f14_rage", 0.6)
    bed(wind, "f1_army", "f2_why", 0.5)
    FX.add(splash(1.4, 1.8), cue("f1_army", "rise"), 0.9)
    for k in range(20):
        FX.add(giggle(), S("f1_army") + 1.0 + k * 0.25, 0.5, pan=rng.uniform(-0.9, 0.9))
    FX.add(bubbles(3.0, 30), E("f2_why") - 2.6, 1.0)
    FX.add(boom(1.0), S("f3_round1"), 0.8)
    for k in range(8):
        FX.add(clang(rng.uniform(300, 900), 0.6), cue("f3_round1", "slam") + 0.2 + k * 0.3, 0.7, pan=rng.uniform(-0.6, 0.6))
    FX.add(boom(1.2), cue("f3_round1", "crab"), 1.0)
    BEDS.add(cheer(3.0, 1.2), cue("f3_round1", "crab") + 0.3, 0.8)
    FX.add(sizzle(6.0, 0.8), S("f4_blur") + 0.5, 0.6)
    bed(rain, "f5_rain", "f7_throne", 0.9)
    bed(sizzle, "f5_rain", "f7_throne", 0.5)
    BEDS.add(screams(4.0, 1.0), S("f5_rain") + 2.0, 0.8)
    FX.add(whoosh(cue("f6_titan", "slam") - cue("f6_titan", "pull"), True, 0.6), cue("f6_titan", "pull"), 1.0)
    for k in range(20):
        FX.add(clang(rng.uniform(250, 1400), 0.4), cue("f6_titan", "pull") + 0.3 + k * 0.2, 0.6, pan=rng.uniform(-0.9, 0.9))
    FX.add(boom(1.4, 3.0), cue("f6_titan", "slam"), 1.0)
    FX.add(bell(), cue("f6_titan", "heart"), 1.0)
    FX.add(bubbles(6.0, 10), S("f7_throne") + TL.shot("f7_throne")["lines"][2]["end"], 1.0)
    for n in ("hit1", "hit2"):
        FX.add(boom(1.2, 1.5), cue("f8_clash", n), 1.0)
        FX.add(clang(300, 1.0), cue("f8_clash", n), 0.8)
    FX.add(tear_paper() * 2, cue("f8_clash", "crack"), 1.0)
    FX.add(rumble(TL.shot("f9_rig")["dur"], 1.4), cue("f9_rig", "quake"), 1.0)
    FX.add(splash(1.4, 3.0), cue("f9_rig", "quake") + 0.5, 0.9)
    FX.add(suction(TL.shot("f10_hoses")["dur"] - 0.6, 1.2), cue("f10_hoses", "latch"), 1.0)
    FX.add(clang(200, 1.0), cue("f10_hoses", "latch"), 1.0)
    FX.add(crumble(2.5), cue("f10_hoses", "latch") + 1.5, 0.8)
    FX.add(click(), cue("f11_logs", "switch"), 1.2)
    FX.add(static(TL.shot("f11_logs")["dur"] - 2.0, 1.0), cue("f11_logs", "switch"), 0.6)
    FX.add(suction(cue("f12_hears", "touch") - S("f12_hears"), 0.6), S("f12_hears"), 0.6)
    FX.add(click(), cue("f12_hears", "touch"), 1.2)
    FX.add(sizzle(1.5, 1.2), cue("f12_hears", "touch"), 0.9)
    FX.add(sizzle(2.0, 1.2), cue("f13_collapse", "race"), 0.9)
    FX.add(creak(2.5, 50), cue("f13_collapse", "groan"), 1.0)
    FX.add(crumble(2.5, 1.5), cue("f13_collapse", "fall"), 1.0)
    FX.add(splash(1.4, 3.0), cue("f13_collapse", "splash"), 1.0)
    FX.add(boom(1.4, 3.0), cue("f13_collapse", "splash"), 1.0)
    bed(rain, "f14_rage", "f17_fade", 1.0)
    FX.add(whoosh(1.5, True, 0.7), S("f14_rage") + TL.shot("f14_rage")["lines"][1]["start"], 0.9)
    FX.add(sizzle(2.0, 1.0), S("f14_rage") + TL.shot("f14_rage")["lines"][1]["start"] + 0.3, 0.8)
    # f15: only the rain (handled by the mixer: everything else is muted)
    FX.add(thud(60, 0.4, 0.3), cue("f17_fade", "fall"), 0.6)
    FX.add(thud(80, 0.6, 0.4), cue("f17_fade", "catch"), 0.7)
    # 8. what rots, what stays
    bed(sea, "e1_rebuild", "e1_rebuild", 0.7)
    bed(crowd, "e1_rebuild", "e1_rebuild", 0.6)
    for k in range(12):
        FX.add(thud(rng.uniform(300, 500), 0.4, 0.15), S("e1_rebuild") + 0.3 + k * 0.5, 0.5, pan=rng.uniform(-0.7, 0.7))   # hammers
    FX.add(tear_paper(), cue("e2_paper", "land"), 0.8)
    bed(hum, "e3_cell", "e3_cell", 0.4, f=60, buzz=False)
    bed(sea, "e4_cliff", "e4_cliff", 0.6)
    bed(wind, "e4_cliff", "e4_cliff", 0.4)
    bed(sea, "e5_rattle", "e5_rattle", 0.6)
    bed(wind, "e5_rattle", "e5_rattle", 0.6)
    FX.add(slurp(), cue("e5_rattle", "slurp"), 1.0)
    bed(underwater, "e7_post", "e7_post", 0.8)
    for t in cue("e7_post", "crack"):
        FX.add(clang(220, 0.7), t, 0.8)
        FX.add(hum(2.0, 140), t, 1.0)

    out = ROOT / "build" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    for bus, name in ((FX, "sfx.wav"), (BEDS, "beds.wav")):
        st = np.stack([bus.L, bus.R], 1)[: int(TL.DURATION * SR)]
        sf.write(out / name, st.astype(np.float32), SR, subtype="FLOAT")
        print(name, f"peak {np.max(np.abs(st)):.2f}")


if __name__ == "__main__":
    build()
