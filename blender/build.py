"""Build the SLUDGE TIDE Blender project.

  blender -b --factory-startup --python blender/build.py -- [options]

  --shots a,b,c        only these shots (default: all)
  --stills             render preview stills of the built shots -> build/stills/<shot>_<t>.png
  --at 1.5,3.0         override preview times (seconds into the shot)
  --save PATH          save the .blend (default: Sludge_Tide.blend at the project root when building all)
  --nosave             don't save

One scene per shot (named by shot id) + the FILM scene that edits the rendered
shots together with the sound in the Video Sequencer (see blender/edit.py).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / "vendor"), str(ROOT)]

import bpy  # noqa: E402
from config import timeline as TL  # noqa: E402
from bl import shot as SH  # noqa: E402
import shots  # noqa: E402


def handles(sid):
    """Pre/post roll so dissolves can overlap neighbours."""
    ids = [s["id"] for s in TL.SHOTS]
    i = ids.index(sid)
    s = TL.SHOTS[i]
    pre = s["tin"][1] / 2 if s["tin"] and s["tin"][0] == "dissolve" else 0.0
    post = 0.0
    if i + 1 < len(ids):
        n = TL.SHOTS[i + 1]
        if n["tin"] and n["tin"][0] == "dissolve":
            post = n["tin"][1] / 2
    return pre, post


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opt = {}
    k = 0
    while k < len(argv):
        a = argv[k]
        if a in ("--shots", "--save", "--at"):
            opt[a] = argv[k + 1]
            k += 2
        else:
            opt[a] = True
            k += 1
    shots.load_all()
    ids = [s["id"] for s in TL.SHOTS]
    want = opt["--shots"].split(",") if "--shots" in opt else ids
    bpy.ops.wm.read_factory_settings(use_empty=True)
    t0 = time.time()
    built = []
    for sid in want:
        if sid not in shots.REG:
            print("NO BUILDER", sid)
            continue
        pre, post = handles(sid)
        sh = SH.Shot(sid, pre, post)
        shots.REG[sid](sh)
        sh.finish()
        built.append(sh)
        print(f"BUILT {sid:14s} {sh.n:5d} frames  ({time.time() - t0:6.1f}s)", flush=True)
    for sc in list(bpy.data.scenes):
        if sc.name == "Scene" and len(bpy.data.scenes) > 1:
            bpy.data.scenes.remove(sc)
    if "--stills" in opt:
        out = ROOT / "build" / "stills"
        out.mkdir(parents=True, exist_ok=True)
        for sh in built:
            times = [float(x) for x in opt["--at"].split(",")] if "--at" in opt else shots.PREVIEW.get(sh.sid, (0.5,))
            for t in times:
                for scx in bpy.data.scenes:
                    scx.frame_current = sh.f(t)
                sh.sc.frame_set(sh.f(t))
                sh.sc.render.filepath = str(out / f"{sh.sid}_{t:05.2f}.png")
                bpy.ops.render.render(write_still=True, scene=sh.sc.name)
                print("STILL", sh.sc.render.filepath, flush=True)
    if "--nosave" not in opt:
        path = opt.get("--save") or (str(ROOT / "Sludge_Tide.blend") if "--shots" not in opt else str(ROOT / "build" / "partial.blend"))
        if "--edit" in opt or "--shots" not in opt:
            import edit
            edit.build_film()
        bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
        print("SAVED", path)


if __name__ == "__main__":
    main()
