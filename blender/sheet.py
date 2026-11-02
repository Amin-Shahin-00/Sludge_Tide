"""Model-sheet test renders of the puppets, inside Blender.

  blender -b --factory-startup --python blender/sheet.py -- junk [rust granny ...]
  -> build/sheets/<name>.png
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "vendor")]
import bpy  # noqa: E402
from bl import stage, gp  # noqa: E402
from bl.puppet import BipedRig, Rig  # noqa: E402

OUT = HERE.parent / "build" / "sheets"


def render(sc, name):
    OUT.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.context.window.scene = sc if bpy.context.window else None
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print("SHEET", sc.render.filepath)


def sheet_junk():
    from bl.cast.junk import Junk
    sc = stage.new_scene("sheet_junk", 1, 1)
    co = stage.collection(sc, "cast")
    stage.Camera(sc)
    stage.gradient_bg(co, "bg", [(0.0, "#f0e2c0"), (1.0, "#fdf6e3")])
    P = Junk()
    poses = [
        dict(x=220, hand_f=(40, -130), hand_b=(-40, -130)),
        dict(x=620, eyes="huge", mouth="jaw", brows="high", hand_f=(140, -420), hand_b=(-150, -400), hand_f_k="open"),
        dict(x=1000, face=-1, lean=10, eyes="dot", brows="angry", mouth="shout", hand_f=(230, -330), hand_b=(-60, -150),
             foot_f=(70, -8), foot_b=(-60, -8), hand_f_k="fist"),
        dict(x=1400, eyes="happy", mouth="grin", hand_f=(90, -470), hand_b=(-100, -460)),
        dict(x=1740, face=-1, eyes="closed", mouth="t3", lean=-6, hand_f=(60, -140), hand_b=(-60, -140)),
    ]
    for i, ps in enumerate(poses):
        r = BipedRig(P, co, f"junk{i}", x=ps.pop("x"), y=1000, s=1.0, face=ps.pop("face", 1))
        hk = ps.pop("hand_f_k", "open")
        sw = {k: ps.pop(k) for k in ("eyes", "brows", "mouth") if k in ps}
        r.pose(1, **ps, **sw, hand_f=hk) if False else None
        r.pose(1, **ps, **sw)
        r.swap(1, "fore_f", "hand", hk)
        r.swap(1, "fore_b", "hand", "open")
        if i in (1, 2, 4):
            r.show(1, "head", "streak")
        if i == 3:
            r.show(1, "head", "helmet")
        if i == 4:
            r.show(1, "head", "tears")
            r.show(1, "head", "cracked")
    stage.text3d(co, "title", "JUNK - MODEL SHEET", 960, 110, 70)
    render(sc, "junk")


def sheet_cast():
    from bl.cast.junk import Junk
    from bl.cast.rust import Iggy, BaronRust
    from bl.cast.others import Granny, Sela, Magnus, Bolt, BoltGiant, Pip, Guard, Rustmite
    sc = stage.new_scene("sheet_cast", 1, 1)
    co = stage.collection(sc, "cast")
    cam = stage.Camera(sc)
    cam.set(None, 1500, 620, 0.62)
    stage.gradient_bg(co, "bg", [(0.0, "#f0e2c0"), (1.0, "#fdf6e3")], depth=60)
    y = 1000
    BipedRig(BoltGiant(), co, "bg_", x=-80, y=y, s=0.9).pose(1)
    BipedRig(Guard(), co, "guard", x=330, y=y).pose(1, hand_f=(90, -250), hand_b=(-90, -250))
    BipedRig(Iggy(), co, "iggy", x=700, y=y).pose(1, lean=8, hand_f=(60, -230), hand_b=(-30, -220), hf="mop")
    r = BipedRig(BaronRust(), co, "rust", x=1150, y=y)
    r.pose(1, hand_f=(260, -330), hand_b=(-170, -230), hf="point", mouth="t2")
    BipedRig(Junk(), co, "junk", x=1620, y=y).pose(1, hand_f=(120, -300), hand_b=(-50, -130), hf="thumb", mouth="grin", eyes="happy")
    BipedRig(Sela(), co, "sela", x=1900, y=y).pose(1, hand_f=(70, -230), hand_b=(-40, -130), hf="clipboard", mouth="smirk")
    BipedRig(Granny(), co, "granny", x=2200, y=y).pose(1, hand_f=(200, -250), hf="ladle", mouth="smile")
    BipedRig(Magnus(), co, "magnus", x=2620, y=y).pose(1, hand_f=(220, -260), hand_b=(-190, -140), hf="thumb", mouth="grin")
    BipedRig(Pip(), co, "pip", x=2960, y=y).pose(1, hand_f=(30, -90), hand_b=(-30, -90))
    BipedRig(Bolt(), co, "bolt", x=3120, y=y, s=1.4).pose(1, eyes="googly")
    for i in range(3):
        BipedRig(Rustmite(), co, f"mite{i}", x=3250 + i * 70, y=y, s=1.2).pose(1, eyes=("open", "happy", "angry")[i])
    stage.text3d(co, "title", "SLUDGE TIDE - CAST", 1500, 60, 120)
    render(sc, "cast")


SHEETS = {"junk": sheet_junk, "cast": sheet_cast}

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(SHEETS)
    for a in args:
        SHEETS[a]()
