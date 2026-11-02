"""Render every shot scene of Sludge_Tide.blend to build/frames/<shot>/####.png (resumable).

  blender -b Sludge_Tide.blend --python blender/render_shots.py -- [--part k/n] [--shots a,b]
"""
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "blender"), str(ROOT)]
from config import timeline as TL  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ids = [s["id"] for s in TL.SHOTS]
if "--shots" in argv:
    ids = argv[argv.index("--shots") + 1].split(",")
if "--part" in argv:
    k, n = map(int, argv[argv.index("--part") + 1].split("/"))
    ids = ids[k::n]
for sid in ids:
    sc = bpy.data.scenes.get(sid)
    if sc is None:
        print("MISSING SCENE", sid)
        continue
    out = ROOT / "build" / "frames" / sid
    out.mkdir(parents=True, exist_ok=True)
    have = len(list(out.glob("*.png")))
    need = sc.frame_end - sc.frame_start + 1
    if have >= need:
        print("SKIP", sid)
        continue
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.compression = 15
    sc.render.filepath = str(out) + "\\"
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True, scene=sid)
    print("RENDERED", sid, need, flush=True)
