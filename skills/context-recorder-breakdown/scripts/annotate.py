"""Annotate walkthrough images for an issue: a caption bar on top and numbered red boxes on the problem.

  uv run --with pillow python annotate.py grid IMAGE -o OUT.png     coordinate grid (every 100 px) to read box positions from
  uv run --with pillow python annotate.py render SPEC.json          render every image in the spec

SPEC.json is a list; paths are relative to the spec file:
  [{"out": "annotated/13-no-rows.png", "src": "mark-004.png",
    "caption": ["13 · Running quick view says 'This result has no loaded rows'."],
    "boxes": [[90, 246, 295, 273, "13"]]}]
Box coordinates are source-image pixels; read them off the `grid` image, not off a downscaled preview.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
RED = (225, 29, 72)


def font(size):
    return ImageFont.truetype(FONT, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def grid(src, out):
    img = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(img)
    f = font(max(12, img.width // 120))
    for x in range(0, img.width, 100):
        d.line((x, 0, x, img.height), fill=(0, 200, 255), width=1)
        d.text((x + 2, 2), str(x), font=f, fill=(0, 120, 255))
    for y in range(0, img.height, 100):
        d.line((0, y, img.width, y), fill=(0, 200, 255), width=1)
        d.text((2, y + 2), str(y), font=f, fill=(0, 120, 255))
    img.save(out)
    print(out, img.size)


def render(spec_path):
    base = Path(spec_path).resolve().parent
    for spec in json.loads(Path(spec_path).read_text()):
        img = Image.open(base / spec["src"]).convert("RGB")
        w, h = img.size
        stroke = max(3, w // 400)
        lab = font(max(14, min(24, w // 45)))
        d = ImageDraw.Draw(img)
        for x0, y0, x1, y1, label in spec.get("boxes", []):
            d.rectangle((x0, y0, x1, y1), outline=RED, width=stroke)
            tw = d.textlength(label, font=lab)
            th = lab.size + 6
            ty = y0 - th if y0 - th >= 0 else y0
            d.rectangle((x0, ty, x0 + tw + 12, ty + th), fill=RED)
            d.text((x0 + 6, ty + 2), label, font=lab, fill="white")
        cap = font(max(15, min(26, w // 42)))
        pad = cap.size // 2 + 4
        lines = [l for c in spec.get("caption", []) for l in wrap(d, c, cap, w - 2 * pad)]
        bar_h = pad * 2 + len(lines) * round(cap.size * 1.3) if lines else 0
        canvas = Image.new("RGB", (w, h + bar_h), (31, 41, 55))
        canvas.paste(img, (0, bar_h))
        cd = ImageDraw.Draw(canvas)
        for i, line in enumerate(lines):
            cd.text((pad, pad + i * round(cap.size * 1.3)), line, font=cap, fill="white")
        out = base / spec["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, **({"quality": 88} if out.suffix == ".jpg" else {}))
        print(out, canvas.size)


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "grid" and sys.argv[3] == "-o":
        grid(sys.argv[2], sys.argv[4])
    elif len(sys.argv) == 3 and sys.argv[1] == "render":
        render(sys.argv[2])
    else:
        sys.exit(__doc__)
