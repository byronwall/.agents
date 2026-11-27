#!/usr/bin/env python3
"""Check a byron-artifact page before publishing.

Usage: python3 check.py site/page.html

Fails (exit 1) on:
  - a button.pic whose image isn't an SVG diagram and has no data-kind of "mockup" or "built"
  - a data-kind other than mockup, built, diagram or chart
  - a local image or file the page references that doesn't exist
Warns on an em dash in visible text (prose must have none; a quoted title or an empty table cell may), and when a mockup or built thumbnail has no kind tag in the HTML (fine if the page's script adds it).
Prints the supporting files to pass to the Artifact tool's `files` (with `root` set to the page's folder).
"""

import html.parser
import pathlib
import re
import sys

KINDS = {"mockup", "built", "diagram", "chart"}


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pics = []  # [attrs, img_src, has_tag]
        self.in_pic = 0
        self.refs = set()
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "button" and "pic" in cls:
            self.pics.append([a, None, False])
            self.in_pic += 1
        elif self.in_pic and tag == "img" and self.pics[-1][1] is None:
            self.pics[-1][1] = a.get("src")
        elif self.in_pic and tag == "span" and "kind" in cls:
            self.pics[-1][2] = True
        for key in ("src", "href"):
            v = a.get(key)
            if v and not re.match(r"^(https?:|#|mailto:|data:|//)", v):
                self.refs.add(v.split("#")[0].split("?")[0])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "button" and self.in_pic:
            self.in_pic -= 1

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def main(path):
    page = pathlib.Path(path)
    p = Page()
    p.feed(page.read_text())
    errors, warnings = [], []
    for attrs, src, has_tag in p.pics:
        kind = attrs.get("data-kind")
        name = src or attrs.get("data-title") or "?"
        if kind is None:
            if not (src or "").endswith(".svg"):
                errors.append(f"no data-kind (mockup or built): {name}")
        elif kind not in KINDS:
            errors.append(f"unknown data-kind {kind!r}: {name}")
        elif kind in ("mockup", "built") and not has_tag:
            warnings.append(f"{kind} thumbnail has no kind tag in the HTML: {name}")
    files = sorted(r for r in p.refs if r and r != page.name)
    for r in files:
        if not (page.parent / r).exists():
            errors.append(f"missing file: {r}")
    for line in "".join(p.text).splitlines():
        if "—" in line:
            warnings.append(f"em dash in text: {line.strip()[:90]}")
    kinds = {}
    for attrs, src, _ in p.pics:
        k = attrs.get("data-kind") or "diagram"
        kinds[k] = kinds.get(k, 0) + 1
    print("images:", ", ".join(f"{v} {k}" for k, v in sorted(kinds.items())) or "none")
    print("files for the Artifact tool:", files)
    untagged = [w for w in warnings if "kind tag" in w]
    if untagged:
        print(f"WARN {len(untagged)} thumbnails have no static kind tag; confirm the page script adds them (first: {untagged[0]})")
    for w in warnings:
        if "kind tag" not in w:
            print("WARN", w)
    for e in errors:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
