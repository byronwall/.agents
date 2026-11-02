#!/usr/bin/env python3
"""Read a Context Recorder session for an agent. Standard library only (plus the `observe` and `ffmpeg` CLIs).

  recorder.py brief   SESSION             what was tested, UTC window, problems on the tested host, marks
  recorder.py ledger  SESSION             every transcript sentence in time blocks, marks and problems inline
  recorder.py frame   SESSION 1:23 ... -o DIR [--burst 2]   frames at session offsets (joined sessions handled)
  recorder.py observe SESSION [--env E]   deployed revision, warnings/errors, failed and slowest spans
  recorder.py pages   SESSION [-o DIR] [--grep TEXT]   open dialogs/alerts per mark from the saved MHTML; DOM text files

SESSION is a folder under ~/Movies/ContextRecorder/ or just its name (2026-11-02_16-25-02).
"""
import argparse, collections, csv, datetime as dt, email, io, json, re, subprocess, sys
from email import policy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path.home() / "Movies" / "ContextRecorder"
SPANS, LOGS = "41766875", "43252774"
INVENTORY = Path.home() / "repos/daily-planning/tasks/TASK-0059-assets/instance-inventory.md"


def load(arg):
    p = Path(arg).expanduser()
    if not p.exists():
        p = ROOT / arg
    if not (p / "session.json").exists():
        sys.exit(f"{p}: no session.json. Process it first: python3 ~/repos/context-recorder/scripts/process_session.py {p}")
    return p.resolve(), json.load(open(p / "session.json"))


def mmss(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def parse_offset(s):
    if ":" in s:
        m, sec = s.rsplit(":", 1)
        return int(m) * 60 + float(sec)
    return float(s)


def source_start(folder):
    # ponytail: the folder name is the local start time, to the second; good enough for Observe windows.
    return dt.datetime.strptime(folder.name, "%Y-%m-%d_%H-%M-%S").astimezone(dt.timezone.utc)


def locate(path, s, offset):
    """Map a session offset to (source folder, seconds into its recording.mp4)."""
    segs = s.get("segments") or [{"source": ".", "start": 0, "end": s["duration"], "editedStart": 0}]
    seg = segs[0]
    for g in segs:
        if g["editedStart"] <= offset:
            seg = g
    return (path / seg["source"]).resolve(), offset - seg["editedStart"] + seg["start"]


def utc(path, s, offset):
    src, t = locate(path, s, offset)
    return source_start(src) + dt.timedelta(seconds=t)


def host(url):
    u = urlsplit(url or "")
    return f"{u.scheme}://{u.netloc}" if u.netloc else ""


def env_for(h):
    n = urlsplit(h).hostname or ""
    if n == "relationalai.up.railway.app":
        return "staging"
    if n in ("localhost", "127.0.0.1"):
        return "local"
    # Rows look like: | `MAREF2` | modeler-maref2.up.railway.app | ...
    if n and INVENTORY.exists():
        m = re.search(r"^\|\s*`([^`]+)`\s*\|\s*" + re.escape(n) + r"\s*\|", INVENTORY.read_text(), re.M | re.I)
        if m:
            return m.group(1)
    return None


def tested_host(s):
    """The host Byron clicked and navigated on most. Returns (host, all hosts with event counts, how it was found)."""
    every = collections.Counter(host(e["event"].get("url")) for e in s["browser"])
    acted = collections.Counter(host(e["event"].get("url")) for e in s["browser"] if e["event"]["kind"] in ("click", "nav"))
    every.pop("", None); acted.pop("", None)
    if acted:
        return acted.most_common(1)[0][0], every, "Chrome extension"
    m = collections.Counter(host((mk.get("browser") or {}).get("url")) for mk in s["marks"])
    m.pop("", None)
    if m:
        return m.most_common(1)[0][0], m, "marks"
    # Joined sessions carry no browser events; macOS context may name a different tab than the one on screen.
    c = collections.Counter(host((mk.get("context") or {}).get("browserURL")) for mk in s["marks"])
    c.pop("", None)
    return (c.most_common(1)[0][0] if c else ""), c, "macOS context only, UNRELIABLE: confirm against the images"


def problems(s, h):
    """Errors, failed or slow requests and console errors/warnings on the tested host, folded."""
    out = collections.OrderedDict()
    for e in s["browser"]:
        ev = e["event"]
        if host(ev.get("url")) != h:
            continue
        k = ev["kind"]
        if k == "request" and ((ev.get("status") or 0) >= 400 or ev.get("status") == 0 or ev.get("slow")):
            label = f"request {ev.get('method', '')} {ev.get('status')} {ev.get('ms')}ms {urlsplit(ev.get('requestUrl', '')).path}"
            body = (ev.get("error") or "")[:160]
        elif k == "error":
            label, body = "error", ev.get("message") or ev.get("error") or ""
        elif k == "console" and ev.get("level") in ("error", "warn"):
            label, body = f"console.{ev['level']}", ev.get("message") or ""
        else:
            continue
        body = " ".join(body.split())[:160]
        key = re.sub(r"\d+", "#", label + body)
        p = out.setdefault(key, {"label": label, "body": body, "first": e["offsetSeconds"], "last": 0, "n": 0})
        p["n"] += 1
        p["last"] = e["offsetSeconds"]
    return list(out.values())


def fmt_problem(p):
    span = mmss(p["first"]) + (f"–{mmss(p['last'])}" if p["last"] - p["first"] >= 1 else "")
    return f"{span} ×{p['n']} {p['label']} {p['body']}".rstrip()


def models(s, h):
    seen = collections.OrderedDict()
    for e in s["browser"]:
        u = e["event"].get("url") or ""
        if host(u) == h:
            m = re.search(r"[#&?]model=([^&]+)", u)
            if m:
                seen.setdefault(m.group(1), e["offsetSeconds"])
    return seen


def image(path, m):
    rel = m.get("image") or m.get("frame") or ""
    return str((path / rel).resolve()) if rel else ""


def title(m):
    """The sentence the mark landed in (the narration window has a ⚑ where it landed)."""
    n = " ".join((m.get("narration") or "").split())
    if "⚑" not in n:
        return n[:90]
    before, after = n.split("⚑", 1)
    head = re.split(r"(?<=[.?!])\s", before)[-1]
    tail = re.split(r"(?<=[.?!])\s", after)[0]
    return " ".join((head + tail).split())[:120]


def cmd_brief(a):
    path, s = load(a.session)
    h, hosts, how = tested_host(s)
    t0, t1 = utc(path, s, 0), utc(path, s, s["duration"])
    segs = s.get("segments") or []
    print(f"Session {path.name} · {mmss(s['duration'])} · {len(s['marks'])} marks · {len(s['transcript'])} sentences"
          + (f" · joined from {len(segs)} recordings" if len(segs) > 1 or (segs and segs[0]['source'] != '.') else ""))
    print(f"UTC {t0:%Y-%m-%dT%H:%M:%SZ} – {t1:%H:%M:%SZ}  (folder names are local time)")
    print(f"Tested host ({how}): {h or 'unknown'} → environment: {env_for(h) or 'look up the host in daily-planning tasks/TASK-0059-assets/instance-inventory.md'}")
    others = [f"{k} ({v})" for k, v in hosts.most_common() if k != h]
    if others:
        print("Other tabs, ignored: " + ", ".join(others[:5]))
    ms = models(s, h)
    if ms:
        print("Models: " + ", ".join(f"{k} from {mmss(v)}" for k, v in ms.items()))
    if len(segs) > 1 or (segs and segs[0]["source"] != "."):
        print("Segments (session offset → source recording):")
        for g in segs:
            print(f"  {mmss(g['editedStart'])}+ → {(path / g['source']).resolve()}/recording.mp4 at {mmss(g['start'])}")
    ps = problems(s, h)
    print(f"Problems on the tested host ({len(ps)} kinds):")
    for p in ps[:25]:
        print("  " + fmt_problem(p))
    if s.get("errors"):
        print("Processing errors: " + "; ".join(map(str, s["errors"]))[:300])
    print("Marks:")
    for m in s["marks"]:
        print(f"  {m['index']:03d} {mmss(m['offsetSeconds'])} {m['kind']:<10} {image(path, m)}  “{title(m)}”")
    if s.get("hiddenMarks"):
        print(f"  ({len(s['hiddenMarks'])} marks fall inside cuts and are hidden)")


def cmd_ledger(a):
    path, s = load(a.session)
    h, _, _ = tested_host(s)
    sents = s["transcript"]
    marks = sorted(s["marks"], key=lambda m: m["offsetSeconds"])
    blocks, cur = [], []
    for x in sents:
        if cur and (x["start"] - cur[-1]["end"] > a.gap or x["end"] - cur[0]["start"] > a.span):
            blocks.append(cur)
            cur = []
        cur.append(x)
    if cur:
        blocks.append(cur)
    probs = [(e["offsetSeconds"], e) for e in s["browser"]]
    print(f"# Ledger · {path.name}\n")
    print(f"{len(sents)} sentences, {len(marks)} marks, {len(blocks)} blocks. Times are session offsets; UTC in brackets.")
    print("Write at least one item per block, or `none` with a reason. Images are absolute paths: open them.\n")
    mi = 0
    for i, b in enumerate(blocks):
        start = b[0]["start"]
        end = blocks[i + 1][0]["start"] if i + 1 < len(blocks) else s["duration"] + 1
        text = []
        for x in b:
            while mi < len(marks) and marks[mi]["offsetSeconds"] < x["end"] and marks[mi]["offsetSeconds"] < end:
                text.append(f"⚑{marks[mi]['index']:03d}")
                mi += 1
            text.append(x["text"].strip())
        while mi < len(marks) and marks[mi]["offsetSeconds"] < end:
            text.append(f"⚑{marks[mi]['index']:03d}")
            mi += 1
        print(f"## B{i + 1:02d} · {mmss(start)}–{mmss(b[-1]['end'])} [{utc(path, s, start):%H:%M:%SZ}]\n")
        print("> " + " ".join(text) + "\n")
        for m in s["marks"]:
            if start <= m["offsetSeconds"] < end or (i == 0 and m["offsetSeconds"] < start):
                hov = ((m.get("browser") or {}).get("hovered") or {}).get("selector", "")
                print(f"- ⚑{m['index']:03d} {mmss(m['offsetSeconds'])} {m['kind']}: {image(path, m)}" + (f" · `{hov}`" if hov else ""))
        sub = {"browser": [e for t, e in probs if start <= t < end]}
        for p in problems(sub, h):
            print("- problem: " + fmt_problem(p))
        print("\nItems:\n")


def cmd_frame(a):
    path, s = load(a.session)
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    for o in a.offsets:
        src, t = locate(path, s, parse_offset(o))
        name = o.replace(":", "-")
        if a.burst:
            dst = out / f"frame-{name}-%02d.jpg"
            args = ["-ss", f"{max(t - 0.5, 0):.3f}", "-i", str(src / "recording.mp4"), "-t", str(a.burst), "-vf", "fps=4"]
        else:
            dst = out / f"frame-{name}.jpg"
            args = ["-ss", f"{t:.3f}", "-i", str(src / "recording.mp4"), "-frames:v", "1"]
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-q:v", "3", str(dst)], check=True)
        print(dst if not a.burst else sorted(out.glob(f"frame-{name}-*.jpg")))


def observe(dataset, start, end, q):
    r = subprocess.run(["observe", "query", "-i", dataset, "-s", start, "-e", end, "--csv", "-q", q],
                       capture_output=True, text=True)
    if r.returncode:
        return None, (r.stderr or r.stdout).strip()
    return list(csv.DictReader(io.StringIO(r.stdout))), ""


def cmd_observe(a):
    path, s = load(a.session)
    h, _, _ = tested_host(s)
    env = a.env or env_for(h)
    if env == "local":
        print("Local run: read /Users/byronwall/repos/modeler/server/logs/redwood2_*.jsonl (newest first) for this window,")
        print("or pass --env with the environment your local server exports to Observe.")
    if not env or env == "local":
        sys.exit(f"No Observe environment for {h or 'this session'}; pass --env NAME.")
    start = (utc(path, s, 0) - dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end = (utc(path, s, s["duration"]) + dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    f = f'filter environment = "{env}"'
    queries = [
        ("Deployed revision", LOGS, f'{f} | make_col rev:string(resource_attributes."vcs.revision") | statsby n:count(), group_by(rev)'),
        ("Warnings and errors (logs)", LOGS, f'{f} and severity_text != "INFO" | make_col msg:substring(string(body), 0, 160) '
                                            '| statsby n:count(), first:min(timestamp), trace:any(trace_id), group_by(severity_text, msg) | topk 25, max(n)'),
        ("Failed spans", SPANS, f'{f} and error = true | make_col msg:substring(string(error_message), 0, 200) '
                                '| statsby n:count(), first:min(start_time), trace:any(trace_id), group_by(span_name, msg) | topk 25, max(n)'),
        ("Slowest spans", SPANS, f'{f} | make_col ms:duration/1000000 | statsby n:count(), max_ms:max(ms), trace:any(trace_id), '
                                 'group_by(span_name) | topk 20, max(max_ms)'),
    ]
    t0 = utc(path, s, 0)

    def offset_of(t):
        # ponytail: assumes one continuous recording; for joined sessions read the brief's segment table.
        sec = (t - t0).total_seconds()
        return ("-" if sec < 0 else "") + mmss(abs(sec))

    print(f"Observe · environment {env} · {start} – {end}")
    print("Spans have no user: other people on this environment appear too. Match by time and route.\n")
    for name, ds, q in queries:
        print(f"## {name}\n$ observe query -i {ds} -s {start} -e {end} --csv -q '{q}'")
        rows, err = observe(ds, start, end, q)
        if rows is None:
            print(f"  failed: {err[:300]}\n")
            continue
        folded = collections.OrderedDict()
        for r in rows:
            r.pop("_c_rank", None)
            # Fold names that differ only in quoted names, ids and numbers ("pending (depth=36)", "'primitive_x'").
            label = [v for k, v in r.items() if k in ("severity_text", "span_name", "msg", "rev")]
            key = tuple(re.sub(r"'[^']*'|\([^)]*\)|[0-9a-f-]{8,}|\d+", "…", " ".join(str(v).split()))[:60] for v in label)
            f_ = folded.get(key)
            if not f_:
                folded[key] = dict(r, kinds=1)
                continue
            f_["kinds"] += 1
            f_["n"] = str(int(f_.get("n") or 0) + int(r.get("n") or 0))
            if "max_ms" in r and float(r["max_ms"]) > float(f_["max_ms"]):
                f_["max_ms"], f_["trace"] = r["max_ms"], r["trace"]
            if r.get("first", "") < f_.get("first", ""):
                f_["first"] = r["first"]
        for r in folded.values():
            kinds = r.pop("kinds")
            parts = [" ".join(str(v).split())[:200] for k, v in r.items() if k in ("severity_text", "span_name", "msg", "rev")]
            if kinds > 1:
                parts[-1] += f"  [+{kinds - 1} similar]"
            parts.append(f"n={r.get('n')}")
            if "max_ms" in r:
                parts.append(f"max {float(r['max_ms']) / 1000:.1f}s")
            if (r.get("first") or "").isdigit():
                t = dt.datetime.fromtimestamp(int(r["first"]) / 1e9, dt.timezone.utc)
                parts.append(f"first {t:%H:%M:%SZ} (@{offset_of(t)})")
            if r.get("trace"):
                parts.append(r["trace"])
            print("  " + " · ".join(parts))
        print()


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP = {"script", "style", "noscript", "template", "svg", "head"}
OVERLAY_ROLES = {"dialog", "alertdialog", "alert", "status", "tooltip", "menu", "listbox"}


class PageText(HTMLParser):
    """DOM text in document order, plus the text of dialogs, alerts, menus and other open overlays."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.lines, self.overlays = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        role = a.get("role") or ""
        ov = role in OVERLAY_ROLES or a.get("aria-live") in ("assertive", "polite") or a.get("aria-modal") == "true"
        label = a.get("aria-label") or ""
        if ov:
            self.overlays.append({"what": role or "live region", "label": label, "text": []})
        self.stack.append((tag, ov))

    def handle_endtag(self, tag):
        while self.stack:
            t, ov = self.stack.pop()
            if ov and self.overlays and not any(o for _, o in self.stack):
                pass
            if t == tag:
                break

    def handle_data(self, data):
        if any(t in SKIP for t, _ in self.stack):
            return
        text = " ".join(data.split())
        if not text:
            return
        if not self.lines or self.lines[-1] != text:
            self.lines.append(text)
        depth = sum(1 for _, o in self.stack if o)
        if depth and self.overlays:
            # ponytail: text goes to the innermost open overlay by count; fine for Ark/Radix-style portals.
            open_ovs = [o for o in self.overlays][-depth:]
            open_ovs[-1]["text"].append(text)


def read_page(path):
    msg = email.message_from_binary_file(open(path, "rb"), policy=policy.default)
    part = next((p for p in msg.walk() if p.get_content_type() == "text/html"), None)
    # Chrome writes quoted-printable UTF-8 without a charset; get_content() would guess latin-1.
    html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace") if part else ""
    p = PageText()
    p.feed(html)
    return msg["Snapshot-Content-Location"] or "", msg["Subject"] or "", p


def cmd_pages(a):
    path, s = load(a.session)
    out = Path(a.out).expanduser() if a.out else None
    seen = set()
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for m in s["marks"]:
        rel = (m.get("browser") or {}).get("pageFile")
        src = (path / (m.get("sourceSession") or ".") / rel) if rel else None
        if not src or not src.exists():
            continue
        url, page_title, p = read_page(src)
        ovs = [o for o in p.overlays if o["text"]]
        if a.grep:
            hits = [l for l in p.lines if a.grep.lower() in l.lower()]
            if hits:
                print(f"⚑{m['index']:03d} {mmss(m['offsetSeconds'])}: " + " | ".join(hits[:3])[:300])
            continue
        print(f"⚑{m['index']:03d} {mmss(m['offsetSeconds'])} {page_title} · {url}")
        for o in ovs:
            line = f"{o['what']}{' “' + o['label'] + '”' if o['label'] else ''}: " + " · ".join(o["text"])[:240]
            print("   " + (f"(unchanged) {line[:70]}…" if line in seen else line))
            seen.add(line)
        if out:
            f = out / f"m{m['index']:03d}.txt"
            body = [f"# ⚑{m['index']:03d} {mmss(m['offsetSeconds'])} {page_title}", url, f"saved page: {src}", ""]
            for o in ovs:
                body.append(f"## {o['what']} {o['label']}".rstrip())
                body += o["text"] + [""]
            body += ["## DOM text (document order; includes text CSS may hide)"] + p.lines
            f.write_text("\n".join(body))
    if out:
        print(f"wrote {out}/mNNN.txt; grep them for exact UI strings, then `rg -F '<string>'` the app source")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brief"); b.add_argument("session"); b.set_defaults(fn=cmd_brief)
    l = sub.add_parser("ledger"); l.add_argument("session")
    l.add_argument("--gap", type=float, default=4, help="start a new block after this many silent seconds")
    l.add_argument("--span", type=float, default=45, help="longest block in seconds")
    l.set_defaults(fn=cmd_ledger)
    f = sub.add_parser("frame"); f.add_argument("session"); f.add_argument("offsets", nargs="+")
    f.add_argument("-o", "--out", required=True); f.add_argument("--burst", type=float, help="seconds of frames at 4 fps")
    f.set_defaults(fn=cmd_frame)
    o = sub.add_parser("observe"); o.add_argument("session"); o.add_argument("--env"); o.set_defaults(fn=cmd_observe)
    p = sub.add_parser("pages"); p.add_argument("session"); p.add_argument("-o", "--out"); p.add_argument("--grep")
    p.set_defaults(fn=cmd_pages)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
