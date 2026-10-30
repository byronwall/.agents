#!/usr/bin/env python3
"""List agent sessions for one project since the previous retro, newest first.

The default source is the harness running this script: Claude Code
transcripts under Claude (CLAUDECODE is set), Codex rollouts under Codex
(any CODEX_* variable is set).
Worktrees count as part of the project: <root>/.claude/worktrees/* for
Claude, and ~/.codex/worktrees/*/<name> for Codex. Claude subagent
transcripts (<session>/subagents/*.jsonl) fold into their parent session.

The window starts at the previous retro session (looking back 30 days);
with none found it falls back to 3 days. --days N sets a plain window.

Findings live in one global ledger, ~/.agents/retro-ledger.jsonl, so a
retro in one repo can check what other repos learned.

Usage:
  list_sessions.py [--project PATH] [--days N] [--source auto|claude|codex|all]
                   [--all-projects] [--limit N] [--json]
  list_sessions.py --scan [--section S]  # window-wide report; saves metrics on the default window
  list_sessions.py --digest FILE         # one session: tools, failures, denials, slow and large calls
  list_sessions.py --last-retro          # previous retro's findings and whether their PRs reached main
  list_sessions.py --ledger              # other repos' findings, with their checks run against this repo
  list_sessions.py --ledger --all-projects   # the whole ledger, grouped by key
  list_sessions.py --record FILE         # upsert findings (JSON list or JSONL) into the ledger
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude" / "projects"
CODEX_DIR = HOME / ".codex" / "sessions"
LEDGER = Path(os.environ.get("RETRO_LEDGER") or HOME / ".agents" / "retro-ledger.jsonl")
# A retro run, matched on cleaned text so harness tags (worktree paths
# like ".../worktrees/retro-7e2df5") can't fake one.
RETRO_RE = re.compile(r"name: retro\b|\[skill body: retro\]|^\s*[/$]retro\b", re.I | re.M)
RETRO_CMD_RE = re.compile(r"<command-name>/?retro</command-name>")
NOISE_RE = re.compile(
    r"<(system-reminder|command-message|command-name|command-args|local-command-stdout|cross-session-message|side-sessions-event|ci-monitor-event|task-notification)[^>]*>.*?</\1[^>]*>",
    re.S,
)
PASTE_RE = re.compile(r"<pasted_content[^>]*>(.*?)</pasted_content[^>]*>", re.S)
# User messages that likely correct the agent. Kept narrow: broad words
# ("instead", "stop") mostly hit plain instructions.
STEER_RE = re.compile(
    r"^no[,.!]|\b(again|still not|still broken|i said|i told you|i already|why did|why are you|you forgot|"
    r"not what i|how are we still|should have)\b",
    re.I | re.M,
)
STOP = set("a an the and or but to of in on for with as at by is are be it its this that these those i you we "
           "me my our your can do does if then so just let s lets please go get all from up out it ok okay".split())
DENY_RE = re.compile(r"^\s*(Permission (for|to) .{0,80}denied|The user doesn't want to proceed)")


def clean_text(t):
    """Drop harness-injected blocks; shrink pastes to a stub so logs stay visible."""
    if t.lstrip().startswith("Base directory for this skill:"):
        return "[skill body: " + t.split("\n", 1)[0].rsplit("/", 1)[-1] + "]"
    t = PASTE_RE.sub(lambda m: f"[pasted: {' '.join(m.group(1).split())[:200]}…]", t)
    t = NOISE_RE.sub(" ", t).strip()
    if t.startswith("Another Claude session sent a message"):
        return "[message from another session]"
    if t.startswith("Background (from the session that started this one)"):
        task = t.split("Task:", 1)[-1]
        return f"[brief from parent session, {len(t)} chars: {' '.join(task.split())[:200]}…]"
    if len(t) > 1500 and len(re.findall(r"^#{1,3} ", t, re.M)) >= 2:
        return f"[injected command or doc, {len(t)} chars: {' '.join(t.split())[:160]}…]"
    return t if len(t) <= 1500 else t[:1500] + f"…[+{len(t) - 1500} chars]"


def is_retro(raw):
    return bool(RETRO_CMD_RE.search(raw) or RETRO_RE.search(clean_text(raw)))


def is_steer(text):
    return not text.startswith("[") and bool(STEER_RE.search(text))


def project_root(path):
    """Main checkout root, even when called from inside a worktree."""
    try:
        common = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        return str(Path(common).parent)
    except Exception:
        return str(Path(path).resolve())


def detect_harness():
    if os.environ.get("CLAUDECODE"):
        return "claude"
    if any(k.startswith("CODEX_") for k in os.environ):
        return "codex"
    return "claude"


def claude_encode(path):
    return re.sub(r"[^A-Za-z0-9]", "-", path)


ERR_RE = re.compile(r'exit_code"?\s*[:=]\s*[1-9]|Exit code:?\s*[1-9]|^\s*(Error|error:|Traceback)', re.M)


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(_text(c.get("text") or c.get("content") or "") for c in content if isinstance(c, dict))
    return ""


def events(path, source, sidechain=False):
    """Yield (kind, ts, data) for user messages, tool calls, and tool results.

    kind is "meta" (data = record), "user" (data = text), "call" (id, name,
    input), or "result" (id, text, error). sidechain=True reads a subagent file.
    """
    with open(path, errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            p = rec.get("payload", {})
            ts = rec.get("timestamp") or p.get("timestamp") or ""
            yield "meta", ts, rec
            if source == "claude":
                if (rec.get("isSidechain") and not sidechain) or rec.get("type") not in ("user", "assistant"):
                    continue
                content = rec.get("message", {}).get("content")
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                for c in content or []:
                    t = c.get("type") if isinstance(c, dict) else None
                    if t == "text" and rec["type"] == "user":
                        yield "user", ts, c.get("text", "")
                    elif t == "tool_use":
                        yield "call", ts, (c.get("id"), c.get("name"), json.dumps(c.get("input")))
                    elif t == "tool_result":
                        yield "result", ts, (c.get("tool_use_id"), _text(c.get("content")), bool(c.get("is_error")))
            elif rec.get("type") == "response_item":
                t = p.get("type")
                if p.get("role") == "user":
                    for c in p.get("content", []):
                        text = c.get("text", "") if isinstance(c, dict) else ""
                        if not text.lstrip().startswith(("<", "# AGENTS.md")):
                            yield "user", ts, text
                elif t in ("function_call", "custom_tool_call"):
                    yield "call", ts, (p.get("call_id"), p.get("name"), str(p.get("arguments") or p.get("input")))
                elif t in ("function_call_output", "custom_tool_call_output"):
                    out = _text(p.get("output"))
                    yield "result", ts, (p.get("call_id"), out, bool(ERR_RE.search(out[:2000])))


def _secs(a, b):
    try:
        f = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        return (f(b) - f(a)).total_seconds()
    except ValueError:
        return 0.0


def wall_time(out):
    m = re.search(r"Wall time:? ([\d.]+) seconds", out[:300])
    return float(m.group(1)) if m else None


def command_key(name, inp):
    """Group calls by what ran: `pnpm test`, `gh pr`, or the tool name."""
    m = re.search(r'\b(?:command|cmd)\\?"?\s*:\s*\\?"(.*)', inp)
    if not m:
        return name
    for seg in re.split(r"&&|;|\|\||\\n", m.group(1)):
        words = [w for w in seg.strip().split() if "=" not in w][:2]
        if words and words[0] not in ("cd", "export", "set", "source"):
            return " ".join(words).strip("\\\"'")
    return name


def deny_reason(out):
    m = re.search(r"Reason: (\[[^\]]+\])", out)
    if m:
        return m.group(1)
    if "doesn't want to proceed" in out:
        return "[rejected by user]"
    if "safety check" in out:
        return "[built-in safety check]"
    if "auto mode classifier" in out:
        return "[auto mode, no category]"
    return "[other]"


def subagent_files(path):
    d = Path(path).with_suffix("") / "subagents"
    return sorted(d.glob("*.jsonl")) if d.is_dir() else []


def subagent_label(p):
    try:
        return json.loads(p.with_suffix(".meta.json").read_text()).get("description") or p.stem
    except (OSError, ValueError):
        return p.stem


def _collect(path, source, who, c):
    calls = {}
    for kind, ts, d in events(path, source, sidechain=bool(who)):
        if kind == "call":
            calls[d[0]] = (d[1], " ".join(d[2].split()), ts)
            c["tools"][d[1]] = c["tools"].get(d[1], 0) + 1
        elif kind == "result":
            name, inp, t0 = calls.get(d[0], ("?", "", ts))
            row = {"ts": ts, "who": who, "name": name, "inp": inp, "key": command_key(name, inp),
                   "secs": wall_time(d[1]) or _secs(t0, ts), "chars": len(d[1]), "out": " ".join(d[1].split())[:200]}
            c["results"].append(row)
            if DENY_RE.search(d[1]):
                row["reason"] = deny_reason(d[1])
                c["denials"].append(row)
            elif d[2]:
                c["errors"].append(row)
        elif kind == "user" and not who:  # a subagent's user turns are its brief, not Byron
            clean = clean_text(d)
            if clean:
                c["users"].append((ts, clean))


def collect(path):
    """One session plus its subagents. Subagent rows carry who="a1", "a2", …"""
    source = "codex" if "/.codex/" in str(path) else "claude"
    c = {"tools": {}, "errors": [], "denials": [], "results": [], "users": [], "subs": []}
    _collect(path, source, "", c)
    for i, sp in enumerate(subagent_files(path), 1):
        c["subs"].append(f"a{i} {subagent_label(sp)}")
        _collect(sp, source, f"a{i}", c)
    return c


WAITS_ON_USER = {"AskUserQuestion", "ExitPlanMode", "request_user_input", "sleep", "wait"}


def slowest(results, n):
    return sorted((x for x in results if (x[1] if isinstance(x, tuple) else x)["name"] not in WAITS_ON_USER),
                  key=lambda x: -(x[1] if isinstance(x, tuple) else x)["secs"])[:n]


def _call_line(r, session=""):
    who = f"{session.strip()}.{r['who']} " if r["who"] and session else (f"{r['who']} " if r["who"] else session)
    return f"{r['secs']:6.0f}s {r['chars']:7}ch {who}{r['name']}: {r['inp'][:110]}"


def _denials(items, tag_of):
    by = {}
    for item in items:
        by.setdefault(item[1]["reason"], []).append(item)
    for reason, rows in sorted(by.items(), key=lambda x: -len(x[1])):
        print(f"{len(rows):4}x {reason}  [{' '.join(sorted({tag_of(i) for i in rows}))}]")
        for _, r in rows[-2:]:
            print(f"      e.g. {r['name']}: {r['inp'][:110]}")


def digest(path):
    """Everything a retro needs from one transcript, in a screen or two."""
    c = collect(path)
    print("## Tools: " + ", ".join(f"{n} {k}" for k, n in sorted(c["tools"].items(), key=lambda x: -x[1])))
    if c["subs"]:
        print("\n## Subagents\n" + "\n".join(c["subs"]))
    print(f"\n## Failed calls ({len(c['errors'])})")
    for r in c["errors"][:20]:
        print(f"{r['ts'][:16]} {r['who'] + ' ' if r['who'] else ''}{r['name']}: {r['inp'][:100]}\n      -> {r['out']}")
    print(f"\n## Permission denials ({len(c['denials'])})")
    _denials([("", r) for r in c["denials"]], lambda i: i[1]["who"] or "main")
    print("\n## Slowest calls")
    for r in slowest(c["results"], 6):
        print(_call_line(r))
    print("\n## Largest results")
    for r in sorted(c["results"], key=lambda r: -r["chars"])[:6]:
        print(_call_line(r))
    print(f"\n## User messages ({len(c['users'])})")
    for ts, text in c["users"]:
        print(f"--- {ts[:16]}{' STEER' if is_steer(text) else ''}\n{text}")


# ---------- ledger ----------

STATUSES = ("proposed", "picked", "declined", "done", "dropped")


def ledger_rows():
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def write_ledger(rows):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def upsert(new_rows):
    """Merge rows by id. Lists (prs, seen) union; other fields overwrite."""
    rows = ledger_rows()
    index = {r.get("id"): i for i, r in enumerate(rows)}
    for n in new_rows:
        i = index.get(n["id"])
        if i is None:
            index[n["id"]] = len(rows)
            rows.append(n)
            continue
        old = rows[i]
        for k in ("prs", "seen"):
            if k in n or k in old:
                n[k] = sorted(set(old.get(k, [])) | set(n.get(k, [])))
        rows[i] = {**old, **n}
    write_ledger(rows)


def record(file, root):
    """Validate findings from FILE and upsert them. id = <project>:<key>, so a repeat updates the row."""
    text = Path(file).read_text().strip()
    items = json.loads(text) if text.startswith("[") else [json.loads(l) for l in text.splitlines() if l.strip()]
    today = datetime.now().date().isoformat()
    rows, bad = [], []
    for f in items:
        f.setdefault("kind", "finding")
        f.setdefault("project", root)
        f.setdefault("date", today)
        missing = [k for k in ("key", "scope", "title", "fix", "status") if not f.get(k)]
        if missing or f["status"] not in STATUSES or f["scope"] not in ("repo", "global"):
            bad.append(f"{f.get('key', '?')}: missing {missing}" if missing else f"{f.get('key')}: bad status or scope")
            continue
        f["id"] = f"{f['project']}:{f['key']}"
        f["seen"] = [f["date"]]
        f["prs"] = [int(p) for p in f.get("prs", [])]
        rows.append(f)
    if bad:
        sys.exit("ledger: nothing written. Fix these rows:\n  " + "\n  ".join(bad))
    upsert(rows)
    print(f"ledger: upserted {len(rows)} rows into {LEDGER}")


def run_check(cmd, root):
    """Exit 0 means the problem exists in this repo."""
    try:
        p = subprocess.run(["zsh", "-c", cmd], cwd=root, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "check timed out"
    return {0: "APPLIES", 1: "clear"}.get(p.returncode, f"check error {p.returncode}: {(p.stderr or p.stdout).strip()[:100]}")


def ledger_apply(root, all_projects):
    finds = [r for r in ledger_rows() if r.get("kind") == "finding" and r.get("status") != "dropped"]
    if not finds:
        print(f"ledger: no findings yet in {LEDGER}")
        return
    if all_projects:
        by = {}
        for r in finds:
            by.setdefault(r["key"], []).append(r)
        for key, rs in sorted(by.items(), key=lambda x: -len(x[1])):
            print(f"## {key}  ({len(rs)} repos)  {rs[-1]['title']}")
            for r in rs:
                prs = " ".join(f"#{n}" for n in r.get("prs", []))
                print(f"   {r['date']} {Path(r['project']).name:18} {r['status']:9} {prs}")
        return
    mine = {r["key"] for r in finds if r["project"] == root}
    other = {}
    for r in sorted(finds, key=lambda r: r["date"]):
        if r["project"] != root and r["scope"] == "repo" and r["key"] not in mine:
            other.setdefault(r["key"], []).append(r)
    groups = {"APPLIES": [], "judge": [], "clear": [], "error": []}
    for key, rs in other.items():
        r = rs[-1]
        where = ", ".join(sorted({Path(x["project"]).name for x in rs}))
        result = run_check(r["check"], root) if r.get("check") else "judge"
        g = result if result in groups else "error"
        groups[g].append(f"{key}  [{where}]  {r['title']}\n      lesson: {r.get('lesson') or r['fix']}"
                         + (f"\n      {result}" if g == "error" else ""))
    print(f"# ledger: {len(other)} findings from other repos not yet recorded for {Path(root).name}")
    for g, label in (("APPLIES", "Check says it applies here"), ("judge", "No check: judge from the lesson"),
                     ("error", "Check failed to run"), ("clear", "Check says this repo is clear")):
        if groups[g]:
            print(f"\n## {label} ({len(groups[g])})")
            print("\n".join(groups[g] if g != "clear" else [x.split("\n")[0] for x in groups[g]]))


def default_branch(root):
    try:
        return subprocess.check_output(["git", "-C", root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return "origin/main"


def pr_landing(root, prs, base):
    out = []
    for n in prs:
        try:
            j = json.loads(subprocess.check_output(["gh", "pr", "view", str(n), "--json", "state,mergeCommit,baseRefName"],
                                                   cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=30))
        except Exception:
            out.append(f"#{n} unknown")
            continue
        if j["state"] != "MERGED":
            out.append(f"#{n} {j['state'].lower()}")
            continue
        sha = (j.get("mergeCommit") or {}).get("oid")
        ok = sha and subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", sha, base],
                                    capture_output=True).returncode == 0
        out.append(f"#{n} on {base}" if ok else f"#{n} merged into {j['baseRefName']} but NOT on {base}")
    return out


def last_retro(root, prior):
    finds = [r for r in ledger_rows() if r.get("kind") == "finding" and r["project"] == root]
    if finds:
        subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], capture_output=True, timeout=120)
        base = default_branch(root)
        print(f"# ledger findings for {Path(root).name} (landing checked against {base})")
        for r in sorted(finds, key=lambda r: r["seen"][-1], reverse=True):
            seen = f" seen {len(r['seen'])}x" if len(r["seen"]) > 1 else ""
            land = "; ".join(pr_landing(root, r.get("prs", []), base)) or "no PRs"
            print(f"{r['seen'][-1]} {r['status']:9} {r['key']}{seen}: {r['title']}\n      {r['scope']} -> {r.get('target', '')}  {land}")
        return
    if not prior:
        print("# no previous retro in the last 30 days and no ledger rows for this project")
        return
    # Before the ledger: the findings are the longest assistant text in that session.
    print(f"# no ledger rows yet; reading the previous retro transcript: {prior['path']}")
    texts, users = [], []
    for kind, ts, d in events(prior["path"], prior["source"]):
        if kind == "meta" and d.get("type") == "assistant" and not d.get("isSidechain"):
            texts += [(ts, c["text"]) for c in d["message"].get("content", []) if isinstance(c, dict) and c.get("type") == "text"]
        elif kind == "user":
            users.append((ts, clean_text(d)))
    if not texts:
        return
    ts, best = max(texts, key=lambda x: len(x[1]))
    print(f"\n## Findings ({ts[:16]})\n{best}\n\n## User replies after it")
    for uts, u in users:
        if uts > ts and u:
            print(f"--- {uts[:16]}\n{u[:400]}")


# ---------- scan ----------

def repeated_phrases(cs, n=15):
    """3-word phrases Byron typed in 2+ sessions: each one is a default the agent should already know."""
    where, example = {}, {}
    for i, c in enumerate(cs, 1):
        for _, text in c["users"]:
            if text.startswith("["):
                continue
            words = re.findall(r"[a-z0-9#/-]+", text.lower())
            for g in zip(words, words[1:], words[2:]):
                if sum(w not in STOP for w in g) >= 2:
                    where.setdefault(g, set()).add(i)
                    example.setdefault(g, text)
    picked, shown = [], set()
    for g, ss in sorted(where.items(), key=lambda x: -len(x[1])):
        if len(ss) < 2 or len(picked) >= n:
            break
        seen = (frozenset(ss), example[g])
        if seen in shown:
            continue  # another phrase from the same message in the same sessions
        shown.add(seen)
        picked.append((g, ss))
    return [(" ".join(g), sorted(ss), " ".join(example[g].split())[:140]) for g, ss in picked]


def metrics(cs):
    n = max(len(cs), 1)
    res = [r for c in cs for r in c["results"] if r["name"] not in WAITS_ON_USER]
    return {
        "sessions": len(cs),
        "fails/session": round(sum(len(c["errors"]) for c in cs) / n, 1),
        "denials/session": round(sum(len(c["denials"]) for c in cs) / n, 1),
        "corrections/session": round(sum(is_steer(t) for c in cs for _, t in c["users"]) / n, 1),
        "repeated phrases": len(repeated_phrases(cs, 50)),
        "slow-call min/session": round(sum(r["secs"] for r in res if r["secs"] > 60) / 60 / n, 1),
    }


def scan(rows, root, section, save):
    """Deterministic pass over the whole window: failures, denials, slow calls, user messages."""
    cs = [collect(Path(row["path"])) for row in rows]
    want = lambda s: section in (None, s)
    if want("sessions"):
        print("## Sessions")
        for i, (row, c) in enumerate(zip(rows, cs), 1):
            subs = f" +{len(c['subs'])}sub" if c["subs"] else ""
            print(f"S{i} {row['end'][:16]} {row['user_msgs']}msg {len(c['errors'])}err {len(c['denials'])}deny{subs}  {row['first'][:90]}\n   {row['path']}")
    if want("trend"):
        m = metrics(cs)
        prev = [r for r in ledger_rows() if r.get("kind") == "metrics" and r["project"] == root
                and r["date"] < datetime.now().date().isoformat()]
        last = prev[-1]["values"] if prev else {}
        print(f"\n## Trend (vs previous retro {prev[-1]['date'] if prev else ': none recorded'})")
        for k, v in m.items():
            was = last.get(k)
            print(f"   {k:24} {v:>6}" + (f"   was {was}" if was is not None else ""))
        if save:
            today = datetime.now().date().isoformat()
            upsert([{"kind": "metrics", "id": f"{root}:metrics:{today}", "project": root, "date": today, "values": m}])
    if want("fails"):
        fails = {}
        for i, c in enumerate(cs, 1):
            for r in c["errors"]:
                fails.setdefault(r["key"], []).append((f"S{i}", r))
        print(f"\n## Failed calls by command ({sum(len(v) for v in fails.values())})")
        for key, items in sorted(fails.items(), key=lambda x: -len(x[1]))[:15]:
            tag, r = items[-1]
            where = " ".join(sorted({t + ("." + x["who"] if x["who"] else "") for t, x in items}))
            print(f"{len(items):4}x {key}  [{where}]\n      e.g. {r['inp'][:100]}\n      -> {r['out'][:160]}")
    if want("denials"):
        ds = [(f"S{i}", r) for i, c in enumerate(cs, 1) for r in c["denials"]]
        print(f"\n## Permission denials by reason ({len(ds)})")
        _denials(ds, lambda i: i[0])
    if want("slow"):
        print("\n## Slowest calls")
        for tag, r in slowest([(f"S{i} ", r) for i, c in enumerate(cs, 1) for r in c["results"]], 12):
            print(_call_line(r, tag))
    if want("users"):
        users = sorted((ts, f"S{i} ", t) for i, c in enumerate(cs, 1) for ts, t in c["users"])
        cap = 1500 if section == "users" else 300
        if section != "users":  # image stubs carry no text
            users = [u for u in users if not u[2].startswith("[Image")]
        print("\n## Phrases you repeated across sessions (each is a missing default)")
        for phrase, ss, ex in repeated_phrases(cs):
            print(f"{len(ss):4} sessions  \"{phrase}\"  [{' '.join(f'S{s}' for s in ss[:8])}]\n      e.g. {ex}")
        steer = [u for u in users if is_steer(u[2])]
        print(f"\n## Likely corrections ({len(steer)})")
        for ts, tag, text in steer:
            print(f"--- {tag}{ts[:16]}\n{text[:cap]}")
        print(f"\n## User messages ({len(users)}, oldest first; --section users for full text)")
        for ts, tag, text in users:
            print(f"--- {tag}{ts[:16]}\n{text[:cap]}" + ("…" if len(text) > cap else ""))


def summarize(path, source):
    first, start, end, cwd, n_user, has_retro, n_err = None, None, None, None, 0, False, 0
    for kind, ts, d in events(path, source):
        if kind == "meta":
            if ts:
                start, end = start or ts, ts
            cwd = cwd or d.get("cwd") or d.get("payload", {}).get("cwd")
            if d.get("type") == "session_meta" and d.get("payload", {}).get("parent_thread_id"):
                return None  # Codex sub-thread (subagent, approval reviewer)
        elif kind == "result":
            n_err += d[2]
        elif kind == "user":
            n_user += 1
            if n_user <= 2:
                has_retro = has_retro or is_retro(d)
            clean = " ".join(clean_text(d).split())
            if clean and first is None:
                first = clean
    if n_user == 0:
        return None
    return {
        "source": source, "path": str(path), "cwd": cwd or "", "start": start or "", "end": end or "",
        "user_msgs": n_user, "errors": n_err, "kb": path.stat().st_size // 1024, "subs": len(subagent_files(path)),
        "first": (first or "(pasted prompt only)")[:140], "retro": has_retro,
    }


def claude_files(root, all_projects):
    prefix = claude_encode(root)
    for d in CLAUDE_DIR.iterdir():
        if d.is_dir() and (all_projects or d.name == prefix or d.name.startswith(prefix + "-")):
            yield from d.glob("*.jsonl")


def codex_files(since):
    day = since.date()
    while day <= datetime.now(timezone.utc).date():
        yield from (CODEX_DIR / f"{day:%Y/%m/%d}").glob("*.jsonl")
        day += timedelta(days=1)


def in_project(cwd, root):
    name = Path(root).name
    return cwd == root or cwd.startswith(root + "/") or (
        "/.codex/worktrees/" in cwd and Path(cwd).name == name
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--days", type=float, help="plain window; default is since the previous retro")
    ap.add_argument("--digest", metavar="FILE", help="print one transcript's retro digest and exit")
    ap.add_argument("--source", choices=["auto", "claude", "codex", "all"], default="auto")
    ap.add_argument("--all-projects", action="store_true")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--scan", action="store_true", help="aggregate report over the listed sessions")
    ap.add_argument("--section", choices=["sessions", "trend", "fails", "denials", "slow", "users"],
                    help="with --scan: print one section; 'users' prints full message text")
    ap.add_argument("--last-retro", action="store_true", help="previous retro's findings and their landing status")
    ap.add_argument("--ledger", action="store_true", help="other repos' findings checked against this repo")
    ap.add_argument("--record", metavar="FILE", help="upsert findings into the ledger")
    a = ap.parse_args()
    if a.digest:
        return digest(Path(a.digest))
    root = project_root(a.project)
    if a.record:
        return record(a.record, root)
    if a.ledger:
        return ledger_apply(root, a.all_projects)
    since_retro = a.days is None

    if a.source == "auto":
        a.source = detect_harness()
    lookback = 30 if since_retro else a.days
    since = datetime.now(timezone.utc) - timedelta(days=lookback)
    files = []
    if a.source in ("claude", "all"):
        files += [(p, "claude") for p in claude_files(root, a.all_projects)]
    if a.source in ("codex", "all") and CODEX_DIR.exists():
        files += [(p, "codex") for p in codex_files(since)]

    rows = []
    for p, src in files:
        if datetime.fromtimestamp(p.stat().st_mtime, timezone.utc) < since:
            continue
        s = summarize(p, src)
        if not s:
            continue
        if src == "codex" and not a.all_projects and not in_project(s["cwd"], root):
            continue
        rows.append(s)
    rows.sort(key=lambda r: r["end"], reverse=True)

    # Skip the retro session that is running right now (newest, still open).
    prior = None
    if since_retro:
        retros = [r for r in rows if r["retro"]]
        prior = next((r for r in retros if r["end"] < rows[0]["end"]), None) if rows else None
        if a.last_retro:
            return last_retro(root, prior)
        if prior:
            rows = [r for r in rows if r["end"] >= prior["start"]]
            print(f"# window starts at previous retro: {prior['start'][:16]} {prior['path']}", file=sys.stderr)
        else:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            rows = [r for r in rows if r["end"] >= cutoff]
            print("# no earlier retro in 30 days; using last 3 days", file=sys.stderr)
    elif a.last_retro:
        sys.exit("--last-retro uses the since-retro window; drop --days")

    rows = rows[: a.limit]
    print(f"# project root: {root}  source: {a.source}  sessions: {len(rows)}", file=sys.stderr)
    if a.scan:
        return scan(rows, root, a.section, save=since_retro and not a.all_projects)
    if a.json:
        json.dump(rows, sys.stdout, indent=1)
        return
    for r in rows:
        tag = " RETRO" if r["retro"] else ""
        subs = f" +{r['subs']}sub" if r["subs"] else ""
        where = r["cwd"].replace(root, ".") if r["cwd"].startswith(root) else r["cwd"]
        print(f"{r['end'][:16]} {r['source']:6} {r['user_msgs']:3}msg {r['errors']:3}err {r['kb']:6}KB{subs}{tag}  {where}\n"
              f"    {r['first']}\n    {r['path']}")


if __name__ == "__main__":
    main()
