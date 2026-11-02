"""Master timeline, computed from config/script.py and the generated voice lengths.

Every shot gets an absolute start/end; every dialogue line gets absolute t0/t1.
A shot is stretched when its dialogue (as actually performed by the voices in
build/vo/durations.json) would run past its end, so the picture always fits.
"""
import json
from pathlib import Path
from .script import SHOTS as _RAW

FPS = 24
W, H = 1920, 1080
ROOT = Path(__file__).resolve().parents[1]
DUR_FILE = ROOT / "build" / "vo" / "durations.json"

_durs = json.loads(DUR_FILE.read_text()) if DUR_FILE.exists() else {}


def _estimate(line):
    if line["who"] == "BOLT":
        return 1.6
    return 0.45 + 0.34 * len(line["text"].split())


SHOTS, LINES, BY_ID = [], [], {}
_t = 0.0
for _s in _RAW:
    _cur, _lines = None, []
    for _k, _l in enumerate(_s["lines"]):
        lid = f"{_s['id']}_{_k}"
        d = _durs.get(lid, _estimate(_l))
        if _l["at"] is not None:
            st = _l["at"]
        else:
            st = (_cur if _cur is not None else 0.3) + _l["gap"]
        _cur = st + d if _cur is None else max(_cur, st + d)
        _lines.append(dict(_l, id=lid, start=st, end=st + d, dur=d))
    dur = max(_s["dur"], (_cur + _s["tail"]) if _lines else 0.0)
    shot = dict(_s, start=_t, end=_t + dur, dur=dur, lines=_lines)
    SHOTS.append(shot)
    BY_ID[shot["id"]] = shot
    for ln in _lines:
        LINES.append(dict(ln, shot=shot["id"], t0=_t + ln["start"], t1=_t + ln["end"]))
    _t += dur
DURATION = round(_t, 4)


def shot(sid):
    return BY_ID[sid]


def shot_at(t):
    for s in SHOTS:
        if s["start"] <= t < s["end"]:
            return s
    return SHOTS[-1]


def cue(sid, name):
    """Absolute time of a named cue (or tuple of times)."""
    s = BY_ID[sid]
    v = s["cues"][name]
    if isinstance(v, (tuple, list)):
        return [s["start"] + x for x in v]
    return s["start"] + v


def line(sid, k):
    """Line k of shot sid (local start/end in the dict, absolute in t0/t1)."""
    s = BY_ID[sid]
    ln = s["lines"][k]
    return dict(ln, t0=s["start"] + ln["start"], t1=s["start"] + ln["end"])


def transitions():
    """(cut time, duration, kind) for every shot with a transition in."""
    out = []
    for s in SHOTS:
        if s["tin"]:
            out.append((s["start"], s["tin"][1], s["tin"][0]))
    return out


if __name__ == "__main__":
    for s in SHOTS:
        print(f"{s['start']:7.2f} {s['end']:7.2f} {s['dur']:5.2f}  {s['scene']:7s} {s['id']}")
    print("duration", DURATION)
