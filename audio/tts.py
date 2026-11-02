"""Character voices (local Kokoro-82M) + per-character processing.

Each line of config/script.py becomes build/vo/<line id>.wav (48 kHz mono).
Also writes build/vo/durations.json (line lengths, read by the timeline) and
build/vo/envelopes.npz (mouth-open curves at 100 Hz, read by the lip sync).

  python audio/tts.py              all lines
  python audio/tts.py r4_bow_0 ... only these lines
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config.script import SHOTS  # noqa: E402
import imageio_ffmpeg  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = ROOT / "build" / "vo"
SR = 48000
rng = np.random.default_rng(11)

# voice blend, speed, pitch shift (semitones, formants kept unless formant=True), extra processing
VOICES = {
    "NAR":    dict(blend={"bm_george": 0.7, "bm_fable": 0.3}, speed=0.92, pitch=-1.0),
    "JUNK":   dict(blend={"am_puck": 0.8, "am_echo": 0.2}, speed=1.10, pitch=2.6, formant=True, crack=True),
    "IGGY":   dict(blend={"bm_lewis": 0.6, "am_onyx": 0.4}, speed=0.90, pitch=-0.8),
    "RUST":   dict(blend={"am_onyx": 0.7, "bm_lewis": 0.3}, speed=0.82, pitch=-2.6, mask=True),
    "MAGNUS": dict(blend={"am_santa": 0.6, "am_fenrir": 0.4}, speed=1.0, pitch=-1.2),
    "GRANNY": dict(blend={"bf_emma": 0.7, "bf_isabella": 0.3}, speed=1.12, pitch=-3.4, grit=True),
    "SELA":   dict(blend={"af_heart": 0.75, "af_nicole": 0.25}, speed=1.06, pitch=0.6),
    "PIP":    dict(blend={"af_bella": 0.6, "af_sky": 0.4}, speed=1.05, pitch=4.5, formant=True),
    "MGR":    dict(blend={"am_eric": 0.6, "am_adam": 0.4}, speed=1.08, pitch=-0.5),
}
CROWD = ["am_adam", "af_bella", "am_echo", "af_sarah", "bm_george", "af_nova", "am_liam", "bf_alice"]


_K = None


def kokoro():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        _K = Kokoro(str(ROOT / "assets/tts/kokoro-v1.0.onnx"), str(ROOT / "assets/tts/voices-v1.0.bin"))
    return _K


def speakable(text):
    """Subtitle text -> text for the voice model: drop stage directions, un-shout ALL CAPS words."""
    text = re.sub(r"\*[^*]*\*|\([^)]*\)", "", text)
    return re.sub(r"\b([A-Z]{2,}[A-Z']*)\b", lambda m: m.group(1).capitalize(), text).strip()


def synth(text, blend, speed):
    k = kokoro()
    style = sum(k.get_voice_style(v) * w for v, w in blend.items())
    a, sr = k.create(text, voice=style, speed=speed, lang="en-us")
    return np.asarray(a, np.float32), sr


def ffx(x, sr, chain):
    tmp_in, tmp_out = OUT / "_in.wav", OUT / "_out.wav"
    sf.write(tmp_in, x, sr, subtype="FLOAT")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(tmp_in), "-af", chain,
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", str(tmp_out)], check=True)
    y, _ = sf.read(tmp_out, dtype="float32")
    return y


def bp(x, lo, hi, o=2):
    return signal.sosfilt(signal.butter(o, [lo, hi], "band", fs=SR, output="sos"), x).astype(np.float32)


def hp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x).astype(np.float32)


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x).astype(np.float32)


def room(x, rt=0.45, wet=0.12, seed=3, lo=200, hi=6000):
    r = np.random.default_rng(seed)
    n = int(SR * rt * 1.3)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-6.9 * t / rt)
    ir = signal.sosfilt(signal.butter(2, [lo, hi], "band", fs=SR, output="sos"), ir)
    ir[: int(0.008 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    y = signal.fftconvolve(x, ir)
    return np.pad(x, (0, len(y) - len(x))) + wet * y


def trim(x, thr=0.008, pre=0.03, post=0.12):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - int(pre * SR)): min(len(x), idx[-1] + int(post * SR))]


def env_follow(x, ms=12):
    k = int(SR * ms / 1000)
    return np.sqrt(np.convolve(x * x, np.ones(k) / k, mode="same")).astype(np.float32)


def mask_hiss(y):
    """Gas-mask hiss: filtered noise that follows the voice's consonants, plus an exhale at the end."""
    sib = env_follow(hp(y, 3500, 4), 20)
    body = env_follow(y, 30)
    n = len(y)
    hiss = bp(rng.standard_normal(n).astype(np.float32), 2500, 9000)
    g = np.clip(sib * 9 + body * 0.25, 0, 1.2)
    out = y + hiss * g * 0.55
    ex = int(0.55 * SR)
    tail = bp(rng.standard_normal(ex).astype(np.float32), 1800, 7000) * np.sin(np.linspace(0, np.pi, ex)) ** 2 * 0.09
    out = np.concatenate([out, tail])
    # a faint metallic resonance (the mask)
    d = int(0.0021 * SR)
    out[d:] += 0.25 * out[:-d]
    return out


def voice_crack(y):
    """Tiny random upward cracks on loud syllables (Junk shouting)."""
    e = env_follow(y, 40)
    loud = e > np.percentile(e, 92)
    if loud.mean() < 0.02:
        return y
    return y * (1 + 0.15 * loud * np.sin(np.arange(len(y)) * 2 * np.pi * 7 / SR))


def process(x, sr, v, fx):
    ratio = 2 ** (v.get("pitch", 0.0) / 12)
    form = "shifted" if v.get("formant") else "preserved"
    chain = [f"rubberband=pitch={ratio:.4f}:formant={form}:transients=crisp"] if abs(ratio - 1) > 1e-3 else []
    chain += ["highpass=f=70", "equalizer=f=3000:t=q:w=1.2:g=2", "acompressor=threshold=-20dB:ratio=3:attack=6:release=120:makeup=3"]
    if v.get("grit"):
        chain += ["vibrato=f=5.5:d=0.18", "equalizer=f=900:t=q:w=1.4:g=2.5"]
    y = ffx(x, sr, ",".join(chain))
    if v.get("grit"):
        y = np.tanh(y * 2.4) / np.tanh(2.4)
    if v.get("crack"):
        y = voice_crack(y)
    if v.get("mask"):
        y = mask_hiss(y)
        y = np.tanh(y * 1.4) / np.tanh(1.4)
    if fx == "whisper":
        y = hp(y, 180) * 0.62
        y = room(y, 0.35, 0.10)
    elif fx == "soft":
        y = room(y * 0.75, 0.4, 0.10)
    elif fx == "echo":
        y = hp(y, 250)
        y = room(y, 2.4, 0.9, seed=9) * 0.6
    elif fx == "inner":
        dl = int(0.023 * SR)
        y = y + 0.4 * np.pad(y, (dl, 0))[: len(y)]
        y = room(y, 1.6, 0.55, seed=5)
    elif fx == "loudspeaker":
        y = bp(y, 350, 4200, 3)
        y = np.tanh(y * 4.0) / 2.0
        dl = int(0.11 * SR)
        y = y + 0.45 * np.pad(y, (dl, 0))[: len(y)]
        y = room(y, 1.4, 0.4, seed=4)
    elif fx == "radio":
        y = bp(y, 380, 3200, 3)
        y = np.tanh(y * 3.0) / 1.8
        y = y + bp(rng.standard_normal(len(y)).astype(np.float32), 800, 6000) * 0.02
    else:
        y = room(y, 0.4, 0.08)
    y = trim(np.asarray(y, np.float32), thr=0.006)
    return (y / (np.max(np.abs(y)) + 1e-9) * 0.9).astype(np.float32)


def crowd(text):
    """Several voices shouting together, slightly out of sync."""
    parts = []
    for i, v in enumerate(CROWD):
        a, sr = synth(text, {v: 1.0}, 1.0 + 0.04 * (i % 3))
        y = ffx(a, sr, f"rubberband=pitch={2 ** (rng.uniform(-1.5, 1.5) / 12):.4f}:formant=preserved")
        parts.append((int(rng.uniform(0, 0.12) * SR), y * rng.uniform(0.6, 1.0)))
    n = max(o + len(y) for o, y in parts)
    out = np.zeros(n, np.float32)
    for o, y in parts:
        out[o:o + len(y)] += y
    out = room(out, 0.9, 0.3)
    return trim(out / (np.max(np.abs(out)) + 1e-9) * 0.9)


def bolt_clicks(text):
    """Bolt speaks in clicks: one burst of clicks per word, the CAPS words louder and faster."""
    words = re.findall(r"\*([^*]*)\*", text)
    words = re.split(r"[\s\-.]+", words[0]) if words else ["click", "click"]
    out = []
    for w in words:
        if not w:
            continue
        loud = w.isupper()
        n_cl = 3 if loud else 2
        for k in range(n_cl):
            n = int(0.05 * SR)
            t = np.arange(n) / SR
            f = rng.uniform(2200, 3600) * (1.25 if loud else 1.0)
            c = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + bp(rng.standard_normal(n).astype(np.float32), 2000, 9000) * np.exp(-t * 300)
            out.append(c * (1.0 if loud else 0.6))
            out.append(np.zeros(int((0.035 if loud else 0.06) * SR), np.float32))
        out.append(np.zeros(int(0.16 * SR), np.float32))
    y = np.concatenate(out).astype(np.float32)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8


def envelope(y, rate=100):
    hop = SR // rate
    n = len(y) // hop
    e = np.sqrt(np.mean(y[: n * hop].reshape(n, hop) ** 2, 1))
    ref = np.percentile(e[e > 1e-4], 90) if np.any(e > 1e-4) else 1.0
    return np.clip(e / (ref + 1e-9), 0, 1.4).astype(np.float32)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    dfile, efile = OUT / "durations.json", OUT / "envelopes.npz"
    durs = json.loads(dfile.read_text()) if dfile.exists() else {}
    envs = dict(np.load(efile)) if efile.exists() else {}
    for s in SHOTS:
        for k, ln in enumerate(s["lines"]):
            lid = f"{s['id']}_{k}"
            if only and lid not in only:
                continue
            who, fx = ln["who"], ln["fx"]
            if who == "BOLT":
                y = bolt_clicks(ln["text"])
            elif who == "CROWD":
                y = crowd(speakable(ln["say"] or ln["text"]))
            else:
                v = VOICES[who]
                a, sr = synth(speakable(ln["say"] or ln["text"]), v["blend"], v["speed"])
                a = a / (np.max(np.abs(a)) + 1e-9)
                y = process(a, sr, v, fx)
            sf.write(OUT / f"{lid}.wav", y, SR, subtype="PCM_24")
            durs[lid] = round(len(y) / SR, 3)
            envs[lid] = envelope(y)
            print(f"{lid:16s} {who:7s} {durs[lid]:5.2f}s  {ln['text']}", flush=True)
    dfile.write_text(json.dumps(durs, indent=1))
    np.savez(efile, **envs)


if __name__ == "__main__":
    main()
