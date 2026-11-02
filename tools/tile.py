"""Tile review images into one sheet: python tools/tile.py out.jpg img1 img2 ... [--cols 3]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

args = sys.argv[1:]
cols = 3
if "--cols" in args:
    i = args.index("--cols")
    cols = int(args[i + 1])
    del args[i:i + 2]
out, files = args[0], [Path(a) for a in args[1:]]
W, H = 640, 360
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W, rows * (H + 20)), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for k, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = (k % cols) * W, (k // cols) * (H + 20)
    sheet.paste(im, (x, y + 20))
    d.text((x + 4, y + 4), f.stem, fill=(230, 230, 230))
sheet.save(out, quality=90)
print(out)
