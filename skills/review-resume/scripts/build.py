"""Build the resume markup page.

Usage: python3 -I build.py OUTDIR review.json out.html

OUTDIR holds page.png and lines.json from extract.py. review.json holds
{"meta": {...}, "notes": [...]}; see references/markup-artifact.md.
Checks the notes, then writes one self-contained HTML file.
"""
import base64, json, pathlib, sys

ACTIONS = {"cut", "clarify", "revise", "move", "keep"}
TIERS = {"first", "next", "opt"}

work, review_path, out = map(pathlib.Path, sys.argv[1:4])
data = json.loads((work / "lines.json").read_text())
review = json.loads(review_path.read_text())
meta, notes = review["meta"], review["notes"]
n_lines = len(data["lines"])

errors = []
for i, n in enumerate(notes, 1):
    a, b = n.get("at", [None, None])
    if not (isinstance(a, int) and isinstance(b, int) and 0 <= a <= b < n_lines):
        errors.append(f"note {i}: 'at' must be [first, last] line indices in 0..{n_lines - 1}")
    if n.get("s") not in ACTIONS:
        errors.append(f"note {i}: 's' must be one of {sorted(ACTIONS)}")
    if n.get("s") != "keep" and n.get("pr") not in TIERS:
        errors.append(f"note {i}: 'pr' must be one of {sorted(TIERS)}")
    if not n.get("t"):
        errors.append(f"note {i}: 't' (title) is missing")
    for p in n.get("p", []):
        if not n.get("long") and len(p.split()) > 14:
            errors.append(f"note {i}: proposal has {len(p.split())} words (limit 14): {p}")
if not meta.get("name"):
    errors.append("meta.name is missing")
if errors:
    sys.exit("\n".join(errors))

tpl = (pathlib.Path(__file__).resolve().parent.parent / "assets" / "markup-template.html").read_text()
for k in ("__TITLE__", "__IMG__", "__DATA__"):
    assert tpl.count(k) == 1, k
img = "data:image/png;base64," + base64.b64encode((work / "page.png").read_bytes()).decode()
payload = json.dumps({**data, "meta": meta, "notes": notes}).replace("</", "<\\/")
html = (tpl.replace("__TITLE__", f"{meta['name']} Resume Markup")
           .replace("__IMG__", img)
           .replace("__DATA__", payload))
out.write_text(html)

count = lambda key, v: sum(1 for n in notes if n.get(key) == v and n.get("s") != "keep")
print(f"wrote {out} ({len(html) // 1024} KB): {len(notes)} notes; "
      f"do first {count('pr', 'first')}, do next {count('pr', 'next')}, optional {count('pr', 'opt')}, "
      f"keep {sum(1 for n in notes if n.get('s') == 'keep')}; "
      f"{sum(1 for n in notes if n.get('q'))} questions")
