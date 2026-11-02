"""The FILM scene: the Video Sequencer edit of every shot + sound + subtitles.

Picture: image-sequence strips of each shot's render (build/frames/<shot>/), placed on
the film timeline, with dissolves / dips to black / white flashes from the timeline.
Sound: the final mix (build/audio/mix.wav) plus muted stems (voice lines, music, sfx)
for re-balancing inside Blender. Subtitles: text strips.
"""
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FRAMES = ROOT / "build" / "frames"
sys.path[:0] = [str(HERE), str(ROOT)]
from config import timeline as TL  # noqa: E402
from bl.shot import HANDLE, FPS  # noqa: E402


def _abs_frame(t):
    return int(round(t * FPS)) + 1


def build_film(name="FILM"):
    sc = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.frame_end = int(round(TL.DURATION * FPS))
    sc.view_settings.view_transform = "Standard"
    if sc.sequence_editor is None:
        sc.sequence_editor_create()
    se = sc.sequence_editor
    for s in list(se.sequences_all):
        se.sequences.remove(s)
    trans = {s["id"]: s["tin"] for s in TL.SHOTS}
    for i, s in enumerate(TL.SHOTS):
        sid = s["id"]
        d = FRAMES / sid
        files = sorted(d.glob("*.png")) if d.exists() else []
        ch = 1 + (i % 2)
        start = _abs_frame(s["start"])
        if files:
            st = se.sequences.new_image(sid, str(files[0]), ch, start)
            for fpath in files[1:]:
                st.elements.append(fpath.name)
            # the render covers [scene.frame_start .. frame_end]; shift so local frame HANDLE+1 lands on start
            first_local = int(files[0].stem)
            st.frame_start = start - (HANDLE + 1 - first_local)
        else:
            src = bpy.data.scenes.get(sid)
            if src is None:
                continue
            st = se.sequences.new_scene(sid, src, ch, start)
            st.frame_start = start - (HANDLE + 1 - src.frame_start)
        st.blend_type = "ALPHA_OVER"
    # transitions
    for s in TL.SHOTS:
        tin = s["tin"]
        if not tin:
            continue
        kind, dur = tin
        a = _abs_frame(s["start"])
        n = max(2, int(round(dur * FPS)))
        if kind in ("black", "white"):
            col = (0, 0, 0) if kind == "black" else (1, 1, 1)
            c = se.sequences.new_effect(f"dip_{s['id']}", "COLOR", 5, a - n // 2, frame_end=a + n // 2)
            c.color = col
            c.blend_type = "ALPHA_OVER"
            for f, v in ((a - n // 2, 0.0), (a, 1.0), (a + n // 2, 0.0)):
                c.blend_alpha = v
                c.keyframe_insert("blend_alpha", frame=f)
    # dissolves: whichever strip is on top fades (incoming fades in, or outgoing fades out)
    for k, s in enumerate(TL.SHOTS):
        tin = s["tin"]
        if not (tin and tin[0] == "dissolve") or k == 0:
            continue
        nxt = se.sequences.get(s["id"])
        prv = se.sequences.get(TL.SHOTS[k - 1]["id"])
        if nxt is None or prv is None:
            continue
        a = _abs_frame(s["start"])
        n = int(round(tin[1] * FPS))
        if nxt.channel > prv.channel:
            for f, v in ((a - n // 2, 0.0), (a + n // 2, 1.0)):
                nxt.blend_alpha = v
                nxt.keyframe_insert("blend_alpha", frame=f)
        else:
            for f, v in ((a - n // 2, 1.0), (a + n // 2, 0.0)):
                prv.blend_alpha = v
                prv.keyframe_insert("blend_alpha", frame=f)    # sound
    mix = ROOT / "build" / "audio" / "mix.wav"
    if mix.exists():
        se.sequences.new_sound("MIX", str(mix), 10, 1)
    for k, stem in enumerate(("music.wav", "sfx.wav", "beds.wav")):
        p = ROOT / "build" / "audio" / stem
        if p.exists():
            s = se.sequences.new_sound(stem, str(p), 11 + k, 1)
            s.mute = True
    for ln in TL.LINES:
        p = ROOT / "build" / "vo" / f"{ln['id']}.wav"
        if p.exists():
            s = se.sequences.new_sound(ln["id"], str(p), 14, _abs_frame(ln["t0"]))
            s.mute = True
    # subtitles
    for ln in TL.LINES:
        if not ln["sub"]:
            continue
        a, b = _abs_frame(ln["t0"]), _abs_frame(ln["t1"] + 0.25)
        t = se.sequences.new_effect(f"sub_{ln['id']}", "TEXT", 8, a, frame_end=max(b, a + 12))
        t.text = ln["text"]
        t.font_size = 46
        t.use_outline = True
        t.outline_color = (0.06, 0.04, 0.08, 1)
        t.outline_width = 0.12
        t.location = (0.5, 0.07)
        t.align_x = "CENTER"
        t.align_y = "BOTTOM"
        t.blend_type = "ALPHA_OVER"
        t.color = (1, 1, 1, 1) if ln["who"] != "BOLT" else (1.0, 0.82, 0.5, 1)
    # output
    r = sc.render
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 256
    r.ffmpeg.audio_mixrate = 48000
    r.filepath = str(ROOT / "output" / "sludge_tide.mp4")
    sc.render.use_sequencer = True
    sc.render.use_compositing = False
    return sc


if __name__ == "__main__":
    build_film()
