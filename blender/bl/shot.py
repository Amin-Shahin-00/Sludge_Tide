"""Shot = one Blender scene. Timing comes from config/timeline.py (shared with the audio).

Every shot scene has HANDLE frames of pre-roll before local time 0 so transitions
(dissolves / dips) can overlap neighbouring shots in the edit.
"""
import math
import sys
from pathlib import Path
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config import timeline as TL  # noqa: E402
from . import stage, gp, geo  # noqa: E402
from .puppet import BipedRig  # noqa: E402

FPS = 24
HANDLE = 24
_PUPPETS = {}
_ENV = None


def envelopes():
    global _ENV
    if _ENV is None:
        f = ROOT / "build" / "vo" / "envelopes.npz"
        d = np.load(f) if f.exists() else {}
        _ENV = {k: d[k] for k in (d.files if hasattr(d, "files") else [])}
    return _ENV


def puppet(cls):
    if cls not in _PUPPETS:
        _PUPPETS[cls] = cls()
    return _PUPPETS[cls]


def ease(name, u):
    u = min(1.0, max(0.0, u))
    if name == "lin":
        return u
    if name == "in":
        return u * u
    if name == "out":
        return 1 - (1 - u) ** 2
    if name == "hold":
        return 0.0 if u < 1 else 1.0
    if name == "back":
        v = u - 1
        return v * v * (2.9 * v + 1.9) + 1
    if name == "snap":                     # anime hit: fast out, settle
        return 1 - (1 - u) ** 4
    return 0.5 * (2 * u) ** 2.2 if u < 0.5 else 1 - 0.5 * (2 * (1 - u)) ** 2.2


def _lerp(a, b, u):
    if isinstance(a, (tuple, list, np.ndarray)) and isinstance(b, (tuple, list, np.ndarray)):
        return tuple(float(x) + (float(y) - float(x)) * u for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * u
    return a if u < 1 else b


class Shot:
    def __init__(self, sid, pre=0.0, post=0.0):
        s = TL.shot(sid)
        self.sid = sid
        self.data = s
        a, b = int(round(s["start"] * FPS)), int(round(s["end"] * FPS))
        self.n = b - a
        self.abs0 = a
        self.dur = self.n / FPS
        f0 = 1 + HANDLE - int(round(pre * FPS))
        f1 = HANDLE + self.n + int(round(post * FPS))
        self.sc = stage.new_scene(sid, f0, f1)
        self.co = stage.collection(self.sc, sid)
        self.cam = stage.Camera(self.sc)
        self.cam.set(self.f(0), 960, 540, 1.0)
        self.comp = stage.comp_glare(self.sc)
        self.rigs = []
        self.lines = s["lines"]
        self.cues = s["cues"]

    # ------------------------------------------------------------ time
    def f(self, t):
        return 1 + HANDLE + int(round(t * FPS))

    def t(self, f):
        return (f - 1 - HANDLE) / FPS

    def line(self, k):
        ln = self.lines[k]
        return ln["start"], ln["end"]

    def cue(self, name):
        return self.cues[name]

    @property
    def end(self):
        return self.dur

    # ------------------------------------------------------------ cast
    def rig(self, cls, tag, depth=0.0, x=960, y=900, s=1.0, face=1, boil=True):
        r = BipedRig(puppet(cls), self.co, f"{self.sid}.{tag}", depth=depth, x=x, y=y, s=s, face=face)
        self.rigs.append(r)
        if boil:
            for ob in r.obs.values():
                md = ob.grease_pencil_modifiers.new("boil", "GP_NOISE")
                md.factor = 0.18 / max(s, 0.3)
                md.factor_strength = 0.0
                md.factor_thickness = 0.06
                md.factor_uvs = 0.0
                md.noise_scale = 0.3
                md.step = 2
                md.seed = hash(ob.name) % 1000
        return r

    def anim(self, r, keys, step=2, t0=None, t1=None):
        """Stepped in-betweens on twos between key poses. keys: [(t, {pose}), ...]; a key may set
        'ease' for the segment that ends at it. Swaps (eyes, mouth, hands...) change at their key."""
        keys = sorted(keys, key=lambda k: k[0])
        full = []
        cur = {}
        for t, kv in keys:
            cur = dict(cur)
            cur.update(kv)
            full.append((t, cur))
        t0 = keys[0][0] if t0 is None else t0
        t1 = keys[-1][0] if t1 is None else t1
        fa, fb = self.f(t0), self.f(t1)
        frames = list(range(fa, fb + 1, step))
        if frames[-1] != fb:
            frames.append(fb)
        for fr in frames:
            t = self.t(fr)
            if t <= full[0][0]:
                pose = dict(full[0][1])
            elif t >= full[-1][0]:
                pose = dict(full[-1][1])
            else:
                for i in range(1, len(full)):
                    if t <= full[i][0]:
                        ta, A = full[i - 1]
                        tb, B = full[i]
                        u = ease(B.get("ease", "io"), (t - ta) / max(tb - ta, 1e-6))
                        pose = {}
                        for k in set(A) | set(B):
                            if k == "ease":
                                continue
                            if k in A and k in B:
                                pose[k] = _lerp(A[k], B[k], u)
                            else:
                                pose[k] = B.get(k, A.get(k))
                        break
            pose.pop("ease", None)
            r.pose(fr, **pose)

    def lipsync(self, r, who, base="closed", shapes=("t1", "t2", "t3"), only=None):
        """Mouth flaps on twos from the voice line's loudness."""
        env = envelopes()
        for k, ln in enumerate(self.lines):
            if ln["who"] != who or (only is not None and k not in only):
                continue
            e = env.get(ln["id"])
            fa, fb = self.f(ln["start"]), self.f(ln["end"])
            for fr in range(fa, fb, 2):
                i = int((self.t(fr) - ln["start"]) * 100)
                v = float(np.mean(e[max(0, i - 3): i + 4])) if e is not None and i < len(e) else 0.5
                m = base if v < 0.14 else shapes[0] if v < 0.42 else shapes[1] if v < 0.8 else shapes[2]
                r.swap(fr, *r.p.swap_keys["mouth"], m)
            r.swap(fb, *r.p.swap_keys["mouth"], base)

    def blink(self, r, times, base="dot"):
        part, lay = r.p.swap_keys["eyes"]
        for t in times:
            f = self.f(t)
            r.swap(f, part, lay, "half")
            r.swap(f + 1, part, lay, "closed")
            r.swap(f + 3, part, lay, "half")
            r.swap(f + 4, part, lay, base)

    def finish(self):
        for r in self.rigs:
            r.finish()


# ============================================================================ walk cycles

def walk_keys(P, t0, t1, x0, x1, base=None, step=0.5, lift=22, bob=6, swing=34, y=None):
    """Key poses for a walk (contact / passing on each step) from x0 to x1 (home px).
    Feet are planted relative to the travelling root, hands swing opposite the legs."""
    base = dict(base or {})
    face = 1 if x1 >= x0 else -1
    base.setdefault("face", face)
    limbs = P.limbs
    wf = np.asarray(limbs["leg_f"][2], float) if "leg_f" in limbs else None
    wb = np.asarray(limbs["leg_b"][2], float) if "leg_b" in limbs else None
    hf = np.asarray(limbs["arm_f"][2], float) if "arm_f" in limbs else None
    hb = np.asarray(limbs["arm_b"][2], float) if "arm_b" in limbs else None
    n = max(1, int(round((t1 - t0) / step)))
    stride = abs(x1 - x0) / n / max(base.get("s", 1.0), 1e-3)
    keys = []
    for i in range(n * 2 + 1):
        t = t0 + (t1 - t0) * i / (n * 2)
        u = i / (n * 2)
        x = x0 + (x1 - x0) * u
        k = dict(base)
        k["x"] = x
        k["ease"] = "lin"
        phase = i % 4
        if y is not None:
            k["y"] = y
        if i == 0 or i == n * 2:
            s = 0.0
            k["bob"] = 0.0
        else:
            s = (1 if (i // 2) % 2 == 0 else -1)
        if phase in (0, 2) or i in (0, n * 2):            # contact
            a = stride / 2 * (s if s else 0)
            if wf is not None:
                k["foot_f"] = (wf[0] + a, wf[1])
                k["foot_b"] = (wb[0] - a, wb[1])
            k["bob"] = bob * 0.6 if s else 0.0
        else:                                              # passing: one foot up
            up = 1 if (i // 2) % 2 == 0 else -1
            if wf is not None:
                k["foot_f"] = (wf[0], wf[1] - (lift if up > 0 else 0))
                k["foot_b"] = (wb[0], wb[1] - (lift if up < 0 else 0))
            k["bob"] = -bob
        if hf is not None and "hand_f" not in base:
            k["hand_f"] = (hf[0] - swing * s, hf[1] + 4 - abs(s) * 6)
        if hb is not None and "hand_b" not in base:
            k["hand_b"] = (hb[0] + swing * s, hb[1] + 4 - abs(s) * 6)
        keys.append((t, k))
    return keys


def rest_hands(P, dx=0.0, dy=0.0):
    hf = np.asarray(P.limbs["arm_f"][2], float) + (dx, dy)
    hb = np.asarray(P.limbs["arm_b"][2], float) + (-dx, dy)
    return dict(hand_f=tuple(hf), hand_b=tuple(hb))
