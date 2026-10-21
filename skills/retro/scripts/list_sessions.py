#!/usr/bin/env python3
"""List agent sessions for one project since the previous retro, newest first.

The default source is the harness running this script: Claude Code
transcripts under Claude (CLAUDECODE is set), Codex rollouts under Codex
(any CODEX_* variable is set).
Worktrees count as part of the project: <root>/.claude/worktrees/* for
Claude, and ~/.codex/worktrees/*/<name> for Codex.

The window starts at the previous retro session (looking back 30 days);
with none found it falls back to 3 days. --days N sets a plain window.

Usage:
  list_sessions.py [--project PATH] [--days N] [--source auto|claude|codex|all]
                   [--all-projects] [--limit N] [--json]
  list_sessions.py --scan            # window-wide: failures by command, slow calls, user messages
  list_sessions.py --digest FILE     # one session: tools, failures, slow and large calls, user messages
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
# A retro run: pasted retro prompt, /retro command, or $retro skill link.
RETRO_RE = re.compile(r"name: retro\b|<command-name>/?retro<|skills/retro\b|^\s*[/$]retro\b", re.I | re.M)
NOISE_RE = re.compile(
    r"<(system-reminder|command-message|command-name|command-args|local-command-stdout|cross-session-message|side-sessions-event|ci-monitor-event|task-notification)[^>]*>.*?</\1[^>]*>",
    re.S,
)
PASTE_RE = re.compile(r"<pasted_content[^>]*>(.*?)</pasted_content[^>]*>", re.S)


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


def events(path, source):
    """Yield (kind, ts, data) for user messages, tool calls, and tool results.

    kind is "meta" (data = record), "user" (data = text), "call" (id, name,
    input), or "result" (id, text, error).
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
                if rec.get("isSidechain") or rec.get("type") not in ("user", "assistant"):
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


def collect(path):
    source = "codex" if "/.codex/" in str(path) else "claude"
    calls, tools, errors, results, users = {}, {}, [], [], []
    for kind, ts, d in events(path, source):
        if kind == "call":
            calls[d[0]] = (d[1], " ".join(d[2].split()), ts)
            tools[d[1]] = tools.get(d[1], 0) + 1
        elif kind == "result":
            name, inp, t0 = calls.get(d[0], ("?", "", ts))
            row = {"ts": ts, "name": name, "inp": inp, "key": command_key(name, inp),
                   "secs": wall_time(d[1]) or _secs(t0, ts), "chars": len(d[1]), "out": " ".join(d[1].split())[:200]}
            results.append(row)
            if d[2]:
                errors.append(row)
        elif kind == "user":
            clean = clean_text(d)
            if clean:
                users.append((ts, clean))
    return {"tools": tools, "errors": errors, "results": results, "users": users}


WAITS_ON_USER = {"AskUserQuestion", "ExitPlanMode", "request_user_input", "sleep", "wait"}


def slowest(results, n):
    return sorted((x for x in results if (x[1] if isinstance(x, tuple) else x)["name"] not in WAITS_ON_USER),
                  key=lambda x: -(x[1] if isinstance(x, tuple) else x)["secs"])[:n]


def _call_line(r, session=""):
    return f"{r['secs']:6.0f}s {r['chars']:7}ch {session}{r['name']}: {r['inp'][:110]}"


def digest(path):
    """Everything a retro needs from one transcript, in a screen or two."""
    c = collect(path)
    print("## Tools: " + ", ".join(f"{n} {k}" for k, n in sorted(c["tools"].items(), key=lambda x: -x[1])))
    print(f"\n## Failed calls ({len(c['errors'])})")
    for r in c["errors"][:20]:
        print(f"{r['ts'][:16]} {r['name']}: {r['inp'][:100]}\n      -> {r['out']}")
    print("\n## Slowest calls")
    for r in slowest(c["results"], 6):
        print(_call_line(r))
    print("\n## Largest results")
    for r in sorted(c["results"], key=lambda r: -r["chars"])[:6]:
        print(_call_line(r))
    print(f"\n## User messages ({len(c['users'])})")
    for ts, text in c["users"]:
        print(f"--- {ts[:16]}\n{text}")


def scan(rows):
    """Deterministic pass over the whole window: failures, slow calls, user messages."""
    fails, results, users = {}, [], []
    for i, row in enumerate(rows, 1):
        c = collect(Path(row["path"]))
        tag = f"S{i} "
        for r in c["errors"]:
            fails.setdefault(r["key"], []).append((tag, r))
        results += [(tag, r) for r in c["results"]]
        users += [(ts, tag, text) for ts, text in c["users"]]
    print("## Sessions")
    for i, row in enumerate(rows, 1):
        print(f"S{i} {row['end'][:16]} {row['user_msgs']}msg {row['errors']}err  {row['first'][:90]}\n   {row['path']}")
    print(f"\n## Failed calls by command ({sum(len(v) for v in fails.values())})")
    for key, items in sorted(fails.items(), key=lambda x: -len(x[1]))[:15]:
        tag, r = items[-1]
        where = " ".join(sorted({t.strip() for t, _ in items}))
        print(f"{len(items):4}x {key}  [{where}]\n      e.g. {r['inp'][:100]}\n      -> {r['out'][:160]}")
    print("\n## Slowest calls")
    for tag, r in slowest(results, 12):
        print(_call_line(r, tag))
    print(f"\n## User messages ({len(users)}, oldest first)")
    for ts, tag, text in sorted(users):
        print(f"--- {tag}{ts[:16]}\n{text}")


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
                has_retro = has_retro or bool(RETRO_RE.search(d))
            clean = " ".join(clean_text(d).split())
            if clean and first is None:
                first = clean
    if n_user == 0:
        return None
    return {
        "source": source, "path": str(path), "cwd": cwd or "", "start": start or "", "end": end or "",
        "user_msgs": n_user, "errors": n_err, "kb": path.stat().st_size // 1024,
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
    a = ap.parse_args()
    if a.digest:
        return digest(Path(a.digest))
    since_retro = a.days is None

    if a.source == "auto":
        a.source = detect_harness()
    root = project_root(a.project)
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
    if since_retro:
        retros = [r for r in rows if r["retro"]]
        prior = next((r for r in retros if r["end"] < rows[0]["end"]), None) if rows else None
        if prior:
            rows = [r for r in rows if r["end"] >= prior["start"]]
            print(f"# window starts at previous retro: {prior['start'][:16]} {prior['path']}", file=sys.stderr)
        else:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            rows = [r for r in rows if r["end"] >= cutoff]
            print("# no earlier retro in 30 days; using last 3 days", file=sys.stderr)

    rows = rows[: a.limit]
    print(f"# project root: {root}  source: {a.source}  sessions: {len(rows)}", file=sys.stderr)
    if a.scan:
        return scan(rows)
    if a.json:
        json.dump(rows, sys.stdout, indent=1)
        return
    for r in rows:
        tag = " RETRO" if r["retro"] else ""
        where = r["cwd"].replace(root, ".") if r["cwd"].startswith(root) else r["cwd"]
        print(f"{r['end'][:16]} {r['source']:6} {r['user_msgs']:3}msg {r['errors']:3}err {r['kb']:6}KB{tag}  {where}\n"
              f"    {r['first']}\n    {r['path']}")


if __name__ == "__main__":
    main()
