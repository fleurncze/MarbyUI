"""Regenerate the card shadows and faded-card overlays in assets.py.

Run this after changing any card size in dmarby.py:
    pip install pillow
    python tools/make_assets.py
It walks every screen (tools/tour.py) to find each card size in use, then
rewrites SHADOWS and FADES in assets.py. Everything else is kept as is.
"""
import base64
import io
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.environ["DMARBY_COLLECT"] = "1"

import tour  # noqa: E402
import dmarby  # noqa: E402

STYLE = {"card": (150, 11), "overlay": (170, 12)}   # shadow alpha, blur radius
PAD = 30


def png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def shadow(w, h, r, kind):
    alpha, blur = STYLE[kind]
    im = Image.new("RGBA", (w + PAD * 2, h + PAD * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([PAD, PAD, PAD + w, PAD + h], radius=r,
                                         fill=(2, 8, 40, alpha))
    return png(im.filter(ImageFilter.GaussianBlur(blur)))


def fade(w, h, r):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(214, 222, 240, 170))
    return png(im)


def dump(name, d):
    out = [f"{name} = {{"]
    for k, v in sorted(d.items()):
        out.append(f'    "{k}": (')
        out += [f'        "{v[i:i + 96]}"' for i in range(0, len(v), 96)]
        out.append("    ),")
    out.append("}")
    return "\n".join(out)


def main():
    tour.run()
    keys = sorted(tour.d._COLLECTED)
    shadows, fades = {}, {}
    for key in keys:
        kind, size, r = key.split(":")
        w, h = map(int, size.split("x"))
        shadows[key] = shadow(w, h, int(r), kind)
        fades[f"{w}x{h}:{r}"] = fade(w, h, int(r))
    path = os.path.join(ROOT, "assets.py")
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"\nSHADOWS = \{.*", "\n", text, flags=re.S).rstrip() + "\n\n"
    text += dump("SHADOWS", shadows) + "\n\n" + dump("FADES", fades) + "\n"
    open(path, "w", encoding="utf-8").write(text)
    print(f"{len(shadows)} shadows, {len(fades)} fades written")


if __name__ == "__main__":
    main()
