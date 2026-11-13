#!/usr/bin/env python3
"""memory-free: one-call memory triage and cleanup for macOS.

  free.py               report only: pressure, growth, tiers
  free.py --kill-safe   also kill the SAFE tier, then print before/after
  free.py --aggressive  with --kill-safe, also kill flat dev servers and test runs
  free.py --no-sample   skip the growth sample (about 1 second, no growth numbers)
  free.py --keep-docker never quit Docker

Sizes are top's MEM (resident + compressed). ps RSS undercounts badly under
pressure, so never rank by it. The last line is always NEXT: done or NEXT: ask.
"""
import glob
import json
import os
import re
import signal
import subprocess
import sys
import time

MIN_MB = 150  # below this a process is not worth a row
KEEP_MB = 300  # an ASK item below this is kept unless it is growing
GROW_MB = 200  # MB a minute that counts as GROWING
ASK_MB = 1000  # ASK total that is worth a question
GUI_MB = 800
SAMPLE_S = 6
IDLE_S = 900  # a transcript this old is idle, whatever its tail says
TAIL = 262144

NEVER = re.compile(r"Claude\.app|claude\.app/Contents/MacOS/claude|WindowServer|^/System/|^/usr/libexec/|^/usr/sbin/")
CLAUDE_CLI = re.compile(r"(^|/)claude(\.app/Contents/MacOS/claude)?( |$)")
APP = re.compile(r"^/Applications/([^/]+)\.app/")
TS = re.compile(r"tsserver\.js|typescript-language-server|typescript-darwin-\w+/lib/tsc --lsp")
TS_LSP = re.compile(r"typescript-language-server")
TS_PROJ = re.compile(r" (/\S+)/node_modules/typescript/")
TEST = re.compile(r"vitest|jest|playwright|mocha")
DEV = re.compile(r"vite/bin|vinxi|next dev|webpack|astro dev")
NODE = re.compile(r"node|tsx|bun|deno")
SCRIPT = re.compile(r"(?:^| )\S*?([\w.-]+\.(?:mjs|cjs|js|ts|py))(?: |$)")
DOCKER_VM = "com.apple.Virtualization.VirtualMachine"


def run(*cmd, timeout=15):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except subprocess.TimeoutExpired:
        return ""


def mb(text):
    m = re.match(r"([\d.]+)([BKMG])?", text)
    n = float(m[1]) if m else 0
    return n * {"G": 1024, "K": 1 / 1024, "B": 1 / 1048576}.get(m and m[2], 1)


def snapshot():
    """One top call gives both the process sizes and the pressure numbers."""
    out = run("top", "-l", "1", "-s", "0", "-o", "mem", "-n", "80", "-stats", "pid,mem,cmprs")
    procs, rows = {}, False
    for line in out.splitlines():
        if rows:
            f = line.split()
            if len(f) == 3 and f[0].isdigit():
                procs[int(f[0])] = (int(mb(f[1])), int(mb(f[2])))
        elif line.startswith("PID"):
            rows = True
    pm = re.search(r"\((\S+) wired, (\S+) compressor\)", out)
    swap = re.search(r"used = ([\d.]+)M", run("sysctl", "-n", "vm.swapusage"))
    level = run("sysctl", "-n", "kern.memorystatus_vm_pressure_level").strip()
    return procs, {
        "swap": int(float(swap[1])) if swap else 0,
        "compressed": int(mb(pm[2])) if pm else 0,
        "wired": int(mb(pm[1])) if pm else 0,
        "level": int(level or 1),
    }


def verdict(p):
    if p["level"] >= 4 or (p["swap"] > 6000 and p["compressed"] > 5000):
        return "JAM"
    if p["level"] >= 2 or p["swap"] > 3000 or p["compressed"] > 4000:
        return "TIGHT"
    return "OK"


def seconds(etime):
    days, _, rest = etime.rpartition("-")
    parts = [int(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return int(days or 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def process_table():
    table = {}
    for line in run("ps", "-axo", "pid=,ppid=,etime=,command=").splitlines():
        f = line.split(None, 3)
        if len(f) == 4:
            table[int(f[0])] = {"ppid": int(f[1]), "age": seconds(f[2]), "etime": f[2], "cmd": f[3]}
    return table


def cwds(pids):
    out = run("lsof", "-b", "-w", "-a", "-d", "cwd", "-Fpn", "-p", ",".join(map(str, sorted(pids))))
    found, pid = {}, None
    for line in out.splitlines():
        if line[:1] == "p":
            pid = int(line[1:])
        elif line[:1] == "n" and pid:
            found[pid] = line[1:]
    return found


def listeners():
    out = run("lsof", "-b", "-w", "-nP", "-iTCP", "-sTCP:LISTEN", "-Fp")
    return {int(x[1:]) for x in out.splitlines() if x[:1] == "p"}


def load_sessions():
    root = os.path.expanduser("~/Library/Application Support/Claude/claude-code-sessions")
    by_cwd = {}
    for path in glob.glob(root + "/*/*/local_*.json"):
        try:
            with open(path) as f:
                s = json.load(f)
        except (OSError, ValueError):
            continue
        if s.get("cwd") and not s.get("isArchived"):
            by_cwd.setdefault(s["cwd"], []).append(s)
    return by_cwd


def is_idle(s):
    """True when the transcript shows a finished turn. Unknown counts as busy."""
    hits = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{s.get('cliSessionId')}.jsonl"))
    if not hits:
        return time.time() - s.get("lastActivityAt", 0) / 1000 > IDLE_S
    if time.time() - os.path.getmtime(hits[0]) > IDLE_S:
        return True
    with open(hits[0], "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - TAIL))
        lines = f.read().decode("utf8", "ignore").splitlines()[1:]
    for line in reversed(lines):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        kind = e.get("type")
        if kind == "system" and e.get("subtype") in ("stop_hook_summary", "turn_duration"):
            return True
        if kind == "assistant":
            return (e.get("message") or {}).get("stop_reason") == "end_turn"
        if kind == "user":
            return False
    return False


def session_for(cwd, by_cwd):
    """The sessions at cwd or the nearest parent folder (a dev server runs in app/)."""
    while cwd and cwd != "/":
        if cwd in by_cwd:
            return by_cwd[cwd]
        cwd = os.path.dirname(cwd)
    return []


def chain(pid, table):
    while pid in table and pid != 1:
        yield pid
        pid = table[pid]["ppid"]


def descendants(root, table):
    kids = {}
    for pid, p in table.items():
        kids.setdefault(p["ppid"], []).append(pid)
    out, todo = [], [root]
    while todo:
        pid = todo.pop()
        out.append(pid)
        todo += kids.get(pid, [])
    return out


def label(p):
    m = SCRIPT.search(p["cmd"])
    if m:
        return m[1]
    if TS.search(p["cmd"]):
        return "tsserver"
    return " ".join(os.path.basename(x) for x in p["cmd"].split()[:2])[:40]


def owner(pid, table, cwd_of, by_cwd):
    """Returns (text, state, session id). State is idle, running, codex or none."""
    links = list(chain(pid, table))
    cmds = [table[x]["cmd"] for x in links]
    cwd = cwd_of.get(pid, "")
    claude = next((x for x in links if CLAUDE_CLI.search(table[x]["cmd"])), None)
    sessions = session_for(cwd_of.get(claude, "") if claude else cwd, by_cwd)
    if sessions:
        sessions.sort(key=lambda s: s.get("lastActivityAt", 0), reverse=True)
        idle = all(is_idle(s) for s in sessions)
        s = sessions[0]
        state = "idle" if idle else "running"
        title = (s.get("title") or "untitled")[:44]
        return f'{state} session "{title}"', state, s["sessionId"]
    if "/.codex/" in cwd or any("/.codex/" in c or "codex" in os.path.basename(c.split()[0]).lower() for c in cmds):
        return "Codex: " + (cwd.replace(os.path.expanduser("~"), "~") or "unknown folder"), "codex", None
    parents = " < ".join(os.path.basename(table[x]["cmd"].split()[0]) for x in links[1:3])
    return f"no session; parent {parents or 'launchd'}", "none", None


def classify(table, sizes, by_cwd, keep_docker):
    big = [p for p, (mem, _) in sizes.items() if mem >= MIN_MB and p in table]
    claudes = {x for p in big for x in chain(p, table) if CLAUDE_CLI.search(table[x]["cmd"])}
    roots = {}  # test process -> root of its run
    for p in big:
        if NEVER.search(table[p]["cmd"]):
            continue
        hits = [x for x in chain(p, table) if TEST.search(table[x]["cmd"])]
        if hits:
            roots[p] = hits[-1]
    cwd_of = cwds(set(big) | claudes | set(roots.values()))
    ports = listeners()

    docker_up = any(DOCKER_VM in p["cmd"] for p in table.values())
    containers = ""
    if docker_up:
        containers = ",".join(run("docker", "ps", "--format", "{{.Names}}", timeout=5).split())

    items, apps, seen = [], {}, set()
    for pid, p in table.items():
        m = APP.match(p["cmd"])
        if m and m[1] != "Claude" and pid in sizes:
            apps[m[1]] = apps.get(m[1], 0) + sizes[pid][0]

    def add(tier, kind, pids, name, why, root):
        text, state, sid = owner(root, table, cwd_of, by_cwd)
        items.append({"tier": tier, "kind": kind, "pids": pids, "name": name, "why": why,
                      "owner": text, "state": state, "session": sid, "cmd": None,
                      "mem": sum(sizes.get(x, (0, 0))[0] for x in pids)})

    for pid in big:
        if pid in seen:
            continue
        p = table[pid]
        cmd = p["cmd"]
        state = owner(pid, table, cwd_of, by_cwd)[1]
        if DOCKER_VM in cmd:
            tier = "keep" if keep_docker else "ask" if containers else "safe"
            add(tier, "docker", [pid], "Docker VM", f"containers: {containers or 'none'}", pid)
            items[-1]["cmd"] = "osascript -e 'quit app \"Docker Desktop\"'"
        elif NEVER.search(cmd) or CLAUDE_CLI.search(cmd) or APP.match(cmd):
            continue
        elif TS.search(cmd):
            pids = [pid]
            if TS_LSP.search(table.get(p["ppid"], {}).get("cmd", "")):
                pids.append(p["ppid"])
            proj = TS_PROJ.search(cmd)
            gone = proj and not os.path.isdir(proj[1])
            why = "project gone" if gone else f"up {p['etime']}"
            tier = "safe" if gone or p["age"] > 3600 or state == "idle" else "ask"
            add(tier, "ts-server", pids, "tsserver", why, pid)
        elif pid in roots:
            root = roots[pid]
            pids = descendants(root, table)
            seen.update(pids)
            orphan = table[root]["ppid"] == 1 and not ports & set(pids)
            add("safe" if orphan else "ask", "test-run", pids, label(table[root]),
                ("orphaned; " if orphan else "") + f"{len(pids)} procs, up {table[root]['etime']}", root)
        elif DEV.search(cmd):
            add("safe" if state == "idle" else "ask", "dev-server", [pid], label(p), f"up {p['etime']}", pid)
        elif NODE.search(cmd):
            parent = table.get(p["ppid"], {}).get("cmd", "")
            if p["ppid"] == 1:
                serving = pid in ports
                add("ask" if serving else "safe", "orphan", [pid], label(p),
                    "serving a port" if serving else "no port", pid)
            elif not APP.match(parent) and "Claude.app" not in parent:
                add("ask", "node", [pid], label(p), f"up {p['etime']}", pid)
    return items, apps


def growth(pids, a, b, wait):
    if not wait or not any(x in a for x in pids):
        return 0
    return int(sum(b.get(x, (0, 0))[0] - a.get(x, (0, 0))[0] for x in pids) * 60 / wait)


def row(i):
    g = i["grow"]
    trend = f"GROWING +{g}M/min" if g >= GROW_MB else "flat"
    sid = f" {i['session']}" if i["session"] and i["state"] == "running" else ""
    print(f"  {i['mem']:>5}M  {trend:<20} {i['kind']:<10} {i['name']}  ({i['why']})")
    print(f"          {i['owner']}{sid}  pids {' '.join(map(str, i['pids'][:6]))}"
          + (" ..." if len(i["pids"]) > 6 else ""))


def section(title, rows):
    print(f"\n== {title}: {sum(i['mem'] for i in rows)}M in {len(rows)} items")
    for i in sorted(rows, key=lambda i: (i["grow"] < GROW_MB, -i["mem"])):
        row(i)


def kill(items):
    for i in items:
        if i["cmd"]:
            run("sh", "-c", i["cmd"])
            continue
        for pid in i["pids"]:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass


def main():
    args = set(sys.argv[1:])
    do_kill = "--kill-safe" in args
    wait = 0 if "--no-sample" in args else SAMPLE_S

    a, before = snapshot()
    print(f"== {verdict(before)}  swap {before['swap']}M, compressed {before['compressed']}M, "
          f"wired {before['wired']}M, level {before['level']} (1 ok, 2 warn, 4 critical)")
    if wait:
        time.sleep(wait)
        b, _ = snapshot()
    else:
        b = a
    table = process_table()
    table.pop(os.getpid(), None)
    items, apps = classify(table, b, load_sessions(), "--keep-docker" in args)
    for i in items:
        i["grow"] = growth(i["pids"], a, b, wait)
        if i["tier"] == "ask" and i["mem"] < KEEP_MB and i["grow"] < GROW_MB:
            i["tier"] = "keep"
        if "--aggressive" in args and i["tier"] == "ask" and i["kind"] in ("dev-server", "test-run") \
                and i["grow"] < GROW_MB:
            i["tier"] = "safe"

    safe = [i for i in items if i["tier"] == "safe"]
    ask = [i for i in items if i["tier"] == "ask"]
    section("KILLED" if do_kill else "SAFE to kill", safe)
    section("ASK", ask)
    gui = sorted(((m, n) for n, m in apps.items() if m >= GUI_MB), reverse=True)
    if gui:
        print("\n== APPS Byron can quit: " + ", ".join(f"{n} {m}M" for m, n in gui))
    pids = [str(x) for i in ask if not i["cmd"] for x in i["pids"]]
    if pids:
        print(f"\n== Kill all ASK: kill {' '.join(pids)}")
    notify = [i for i in ask if i["state"] == "running"]
    if notify:
        print("   After that, tell: " + ", ".join(f"{i['session']} ({i['name']})" for i in notify))

    if do_kill and safe:
        kill(safe)
        time.sleep(3)
        for _ in range(20):
            if not any(i["cmd"] for i in safe) or DOCKER_VM not in run("ps", "-axo", "command="):
                break
            time.sleep(1)
        alive = [x for i in safe for x in i["pids"] if run("ps", "-o", "pid=", "-p", str(x)).strip()]
        _, after = snapshot()
        print(f"\n== Result: {sum(i['mem'] for i in safe)}M released"
              + (f"; still alive: {alive}" if alive else ""))
        print(f"   {'':<11}{'before':>8}{'after':>8}")
        for k in ("swap", "compressed", "wired"):
            print(f"   {k:<11}{before[k]:>7}M{after[k]:>7}M")
        print(f"   {'level':<11}{before['level']:>8}{after['level']:>8}")
        print(f"   {'verdict':<11}{verdict(before):>8}{verdict(after):>8}")
        print("   Swap drains over minutes as pages fault back in.")

    total = sum(i["mem"] for i in ask)
    growing = any(i["grow"] >= GROW_MB for i in ask)
    print("\nNEXT: " + (f"ask ({total}M in ASK" + (", GROWING)" if growing else ")")
                        if total >= ASK_MB or growing else "done"))


if __name__ == "__main__":
    main()
