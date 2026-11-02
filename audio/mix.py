"""Final mix: voices over music + effects + beds, with ducking, the f15 'only the rain'
silence, a limiter and two-pass EBU R128 loudness to -16 LUFS. Also writes subtitles.

Output: build/audio/mix.wav, output/sludge_tide.srt
"""
import json, math, re, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import timeline as TL  # noqa: E402
import imageio_ffmpeg  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
A = ROOT / "build" / "audio"
VO = ROOT / "build" / "vo"
OUT = ROOT / "output"
G = dict(vo=1.0, music=0.34, sfx=0.55, beds=0.45)
DUCK_MUSIC, DUCK_BEDS = -9.0, -4.0


def load(name, n):
    x, sr = sf.read(A / name, dtype="float32")
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    return np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]


def smooth_mask(iv, n, ramp=0.2):
    m = np.zeros(n, np.float32)
    for a, b in iv:
        m[max(0, int(a * SR)):min(n, int(b * SR))] = 1
    k = int(ramp * SR)
    return np.clip(np.convolve(m, np.ones(k, np.float32) / k, "same"), 0, 1)


def limiter(x, ceil=0.89):
    pk = ndimage.maximum_filter1d(np.max(np.abs(x), 1), 481)
    g = np.minimum(1, ceil / np.maximum(pk, 1e-9))
    g = ndimage.minimum_filter1d(g, 481)
    g = np.convolve(g, np.ones(960) / 960, "same")
    return x * g[:, None]


def main():
    n = int(TL.DURATION * SR)
    vo = np.zeros((n, 2), np.float32)
    iv = []
    for ln in TL.LINES:
        x, _ = sf.read(VO / f"{ln['id']}.wav", dtype="float32")
        i = int(ln["t0"] * SR)
        pan = {"RUST": 0.08, "IGGY": 0.08, "MAGNUS": 0.1, "SELA": -0.08, "GRANNY": -0.1, "JUNK": -0.05}.get(ln["who"], 0.0)
        x = x[: n - i]
        vo[i:i + len(x), 0] += x * math.cos((pan + 1) * math.pi / 4) * 1.41
        vo[i:i + len(x), 1] += x * math.sin((pan + 1) * math.pi / 4) * 1.41
        iv.append((ln["t0"] - 0.1, ln["t1"] + 0.25))
    duck = smooth_mask(iv, n)
    music = load("music.wav", n) * G["music"] * (10 ** (DUCK_MUSIC * duck / 20))[:, None]
    beds = load("beds.wav", n) * G["beds"] * (10 ** (DUCK_BEDS * duck / 20))[:, None]
    sfx = load("sfx.wav", n) * G["sfx"]
    # the noodle bowl: all sound drops out except the rain (and Junk's voice)
    s15 = TL.shot("f15_bowl")
    quiet = smooth_mask([(s15["start"] + 0.3, s15["end"] - 0.2)], n, ramp=0.6)
    sfx *= (1 - quiet)[:, None]
    mix = vo * G["vo"] + music + beds + sfx
    mix = limiter(mix)
    pre = A / "premix.wav"
    sf.write(pre, mix.astype(np.float32), SR, subtype="FLOAT")
    r = subprocess.run([FF, "-hide_banner", "-i", str(pre), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr, re.S)[-1])
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(pre), "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", str(A / "mix.wav")], check=True)
    print("mix ->", A / "mix.wav", f"(measured {m['input_i']} LUFS before normalising)")
    OUT.mkdir(exist_ok=True)

    def ts(t):
        h, rem = divmod(t, 3600)
        mi, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(mi):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    rows = [ln for ln in TL.LINES if ln["sub"]]
    srt = [f"{k}\n{ts(ln['t0'])} --> {ts(ln['t1'] + 0.25)}\n{ln['text']}\n" for k, ln in enumerate(rows, 1)]
    (OUT / "sludge_tide.srt").write_text("\n".join(srt), encoding="utf-8")
    print("srt ->", OUT / "sludge_tide.srt")


if __name__ == "__main__":
    main()
