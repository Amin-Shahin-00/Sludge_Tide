"""Rebuild the FILM edit from the rendered frames and render the final movie.

  blender -b Sludge_Tide.blend --python blender/finish.py [-- --norender]
"""
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "blender"), str(ROOT / "blender" / "vendor"), str(ROOT)]
import edit  # noqa: E402

sc = edit.build_film()
bpy.ops.wm.save_mainfile()
print("EDIT SAVED")
if "--norender" not in sys.argv:
    (ROOT / "output").mkdir(exist_ok=True)
    bpy.ops.render.render(animation=True, scene=sc.name)
    print("FILM RENDERED", sc.render.filepath)
