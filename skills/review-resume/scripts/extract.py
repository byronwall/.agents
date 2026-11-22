"""Render page 1 of a resume PDF for the markup artifact.

Usage: <venv>/bin/python -I extract.py resume.pdf OUTDIR

Writes OUTDIR/page.png (2x, phone numbers and emails blanked) and
OUTDIR/lines.json (page size, line boxes, redaction box, wraps).
Prints every line with its index (notes point at these indices) and
every wrapped item with the word count of its last line.
Needs PyMuPDF (pip install pymupdf).
"""
import json, pathlib, re, sys
import pymupdf

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
BULLETS = tuple("•●▪◦‣–-*")
DANGLE = 3  # a last line with this many words or fewer dangles

pdf, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(pdf)
if len(doc) > 1:
    print(f"warning: {len(doc)} pages; the markup covers page 1 only")
p = doc[0]

# Find contact strings before redaction, so their lines can be left out.
text = p.get_text()
secrets = set(EMAIL.findall(text)) | set(m.group(0) for m in PHONE.finditer(text))
rects = [r for s in secrets for r in p.search_for(s)]

lines = []
for bi, b in enumerate(p.get_text("dict")["blocks"]):
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"]).strip()
        if t and not any(s in t for s in secrets):
            lines.append({"t": t, "b": [round(v, 1) for v in l["bbox"]], "blk": bi})
lines.sort(key=lambda l: (round(l["b"][1]), l["b"][0]))

redact = None
if rects:
    for r in rects:
        p.add_redact_annot(r, fill=(1, 1, 1))
    p.apply_redactions()
    u = rects[0]
    for r in rects[1:]:
        u |= r
    redact = [round(v, 1) for v in u]

scale = 2
pix = p.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
pix.save(out / "page.png")

# Wraps: a line continues the one above when it sits in the same block, just
# below it, does not start a new bullet, and is either indented under a bullet
# or follows a paragraph line that ran to the right edge.
right = max(l["b"][2] for l in lines)
head_of = {}
for i, l in enumerate(lines):
    above = [j for j in range(i) if lines[j]["b"][1] < l["b"][1] - 2 and lines[j]["b"][0] < l["b"][2]]
    if not above:
        continue
    j = above[-1]
    prev, head = lines[j], lines[head_of.get(j, j)]
    if l["blk"] != prev["blk"] or l["t"].startswith(BULLETS) or l["b"][1] - prev["b"][3] > 4:
        continue
    indented = head["t"].startswith(BULLETS) and l["b"][0] > head["b"][0] + 2
    para = not head["t"].startswith(BULLETS) and prev["b"][2] > right - 70 and abs(l["b"][0] - prev["b"][0]) < 2
    if indented or para:
        head_of[i] = head_of.get(j, j)

last = {}
for i, h in head_of.items():
    last[h] = max(last.get(h, i), i)
wraps = [{"head": h, "tail": t, "words": len(lines[t]["t"].split())} for h, t in sorted(last.items())]

json.dump({
    "page": {"w": p.rect.width, "h": p.rect.height, "pw": pix.width, "ph": pix.height},
    "lines": [{"t": l["t"], "b": l["b"]} for l in lines],
    "redact": redact,
    "wraps": wraps,
}, open(out / "lines.json", "w"))

for i, l in enumerate(lines):
    print(f"[{i:2}] y={l['b'][1]:5.1f} x={l['b'][0]:5.1f} | {l['t'][:100]}")
print(f"\nredacted {len(rects)} contact strings")
print(f"{len(wraps)} wrapped items:")
for w in wraps:
    flag = "  DANGLING" if w["words"] <= DANGLE else ""
    print(f"  lines {w['head']}-{w['tail']}: {w['words']} words on the last line{flag}")
