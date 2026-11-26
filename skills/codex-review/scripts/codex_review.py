#!/usr/bin/env python3
"""Run one read-only Codex review of a commit, and feed its findings back into guidance.

    codex_review.py --repo <dir> --rev <sha|base..head> --focus <file> [--round N] [--follow-up <file>] [--out <file>]
    codex_review.py --repo <dir> --hazards            # this repo's most common finding classes (before you write code)
    codex_review.py --repo <dir> --close <slug>       # what to change so this loop's findings do not come back
    codex_review.py --repo <dir> --close all          # the same over every review in the last 90 days (repo harvest)

- Pins the review to a commit (a SHA, never HEAD: HEAD moves while you fix).
- Pins the model (MODEL below), so a changed app default in ~/.codex/config.toml cannot switch it.
- Starts Codex with stdin closed (without it `codex exec` waits forever).
- Asks for JSON findings (schema below), prints them as a severity table,
  and appends each finding to LEDGER (~/.agents/review-findings.jsonl).
- Stops at round 3. Round 3 must also return an architecture note.

Exit codes: 0 PASS (no in-scope P0/P1), 3 FAIL (in-scope P0/P1 findings), 4 STOP (round 3 still has an
in-scope P0: do not open the PR; ask Byron for review), 2 Codex could not run or bad arguments.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODEL = "gpt-6.2-sol"
EFFORT = "high"
MAX_ROUNDS = 3
BLOCKING = {"P0", "P1"}
LEDGER = Path.home() / ".agents" / "review-findings.jsonl"
HAZARD_DAYS = 90

CLASSES = {
    "divergent-paths": "two code paths, transports or copies that must agree give different answers",
    "missing-limit": "a size, rate, count or cost limit is missing or checked on only some routes",
    "input-normalization": "encoding, whitespace, BOM, case or format handled inconsistently",
    "absent-value": "null, undefined, empty, optional or default values handled wrong",
    "unsound-inference": "an analysis proves or assumes more than the code guarantees (overrides, aliasing, escapes)",
    "concurrency": "races, ordering, retries or idempotency",
    "stale-state": "caches, memoized values or derived state not invalidated",
    "error-handling": "failures swallowed, mis-reported or turned into the wrong status",
    "security-privacy": "auth, injection, data exposure, or docs that misstate what is stored",
    "wrong-logic": "the main logic computes the wrong result on ordinary inputs",
    "docs-mismatch": "docs, help text or examples disagree with behavior",
    "other": "none of the above",
}
PREVENT = {
    "check": "a lint rule, type, assertion or script could detect this mechanically",
    "test": "a test on a shared fixture or property would catch this class",
    "standard": "a written judgement rule for this repo would stop an agent writing it",
    "architecture": "a design change (one source of truth, one entry point) would make it impossible",
    "none": "a one-off; nothing general would prevent it",
}

SEVERITY = """Severity:
- P0: data loss, a security hole, or a crash in normal use.
- P1: a wrong result or a broken feature on inputs that real use will hit.
- P2: a wrong result on unusual but plausible inputs.
- P3: contrived inputs, polish, or style."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "findings", "architecture_note"],
    "properties": {
        "summary": {"type": "string", "description": "One sentence on the state of the change."},
        "architecture_note": {"type": "string", "description": "Empty unless asked for: a design change that would prevent this class of finding."},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["severity", "in_scope", "reproduced", "title", "file", "line", "input", "fix",
                             "class", "prevent", "prevent_detail", "covered_by_guidance"],
                "properties": {
                    "severity": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                    "in_scope": {"type": "boolean", "description": "true when this diff adds or changes the faulty code; false when it was already on the base branch."},
                    "reproduced": {"type": "boolean", "description": "true when you ran a probe or test that shows the failure."},
                    "title": {"type": "string", "description": "The defect in one short sentence."},
                    "file": {"type": "string", "description": "Path relative to the repository root."},
                    "line": {"type": "integer"},
                    "input": {"type": "string", "description": "The input or state that fails, and what goes wrong."},
                    "fix": {"type": "string"},
                    "class": {"type": "string", "enum": list(CLASSES)},
                    "prevent": {"type": "string", "enum": list(PREVENT)},
                    "prevent_detail": {"type": "string", "description": "The specific check, test, rule or design change, in one sentence, general enough to stop the next instance."},
                    "covered_by_guidance": {"type": "boolean", "description": "true when AGENTS.md, CODING_STANDARDS.md or a repo doc already has a rule this code breaks."},
                },
            },
        },
    },
}


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], stdin=subprocess.DEVNULL, capture_output=True, text=True).stdout.strip()


def repo_name(repo: str) -> str:
    """owner/name from the origin remote, the same for every clone and worktree; else the folder name."""
    url = git(repo, "remote", "get-url", "origin")
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else Path(repo).resolve().name


def ledger(repo: str) -> list[dict]:
    if not LEDGER.exists():
        return []
    name, since = repo_name(repo), (datetime.now(timezone.utc) - timedelta(days=HAZARD_DAYS)).isoformat()
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    return [r for r in rows if r["repo"] == name and r["ts"] >= since]


def hazards(repo: str, top: int = 5) -> str:
    """This repo's most common in-scope finding classes, with what would prevent them."""
    rows = [r for r in ledger(repo) if r["in_scope"] and r["class"] != "other"]
    if not rows:
        return ""
    by = defaultdict(list)
    for r in rows:
        by[r["class"]].append(r)
    out = [f"Past Codex findings in {repo_name(repo)} (last {HAZARD_DAYS} days, {len({r['slug'] for r in rows})} reviews), most common first:"]
    for cls, rs in sorted(by.items(), key=lambda x: (-len({r["slug"] for r in x[1]}), -len(x[1])))[:top]:
        loops = len({r["slug"] for r in rs})
        out.append(f"- {cls} ({len(rs)} findings in {loops} reviews): {CLASSES[cls]}.")
        for d, _ in Counter(r["prevent_detail"] for r in rs if r["prevent"] != "none").most_common(2):
            out.append(f"    prevent: {d}")
    return "\n".join(out)


def close(repo: str, slug: str) -> str:
    """The guidance changes this loop's findings call for."""
    rows = ledger(repo)
    mine = [r for r in rows if (slug == "all" or r["slug"] == slug) and r["in_scope"]]
    if not mine:
        return f"No in-scope findings recorded for {slug} in {repo_name(repo)}."
    loops = defaultdict(set)
    for r in rows:
        if r["in_scope"]:
            loops[r["class"]].add(r["slug"])
    seen = set()
    act = defaultdict(list)
    for r in mine:
        key = (r["prevent"], r["prevent_detail"])
        if key in seen or r["prevent"] == "none":
            continue
        seen.add(key)
        repeat = len(loops[r["class"]]) >= 2
        note = f"[{r['severity']} {r['class']}{', repeat' if repeat else ''}{', guidance existed' if r['covered_by_guidance'] else ''}] {r['prevent_detail']}"
        if r["severity"] == "P3":
            act["skip"].append(note + " (P3)")
        elif r["prevent"] == "standard" and not repeat and not r["covered_by_guidance"]:
            act["skip"].append(note + " (first time in this repo: no standard yet)")
        elif r["prevent"] == "standard" and r["covered_by_guidance"]:
            act["check"].append(note + " (the written rule did not stop it: make it a check or test)")
        else:
            act[r["prevent"]].append(note)
    head = {
        "check": "Add in this PR: checks (lint rule, type, assertion, script)",
        "test": "Add in this PR: tests that cover the class, not only the instance",
        "standard": "Add to CODING_STANDARDS.md (create it if missing): judgement rules for repeat classes",
        "architecture": "Propose as a follow-up session: design changes",
        "skip": "No action yet (recorded; a second occurrence promotes it)",
    }
    out = [f"# Close the loop: {slug} ({len(mine)} in-scope findings)"]
    for k in head:
        if act[k]:
            out += ["", f"## {head[k]}", *[f"- {n}" for n in act[k]]]
    return "\n".join(out)


def record(repo: str, slug: str, rev: str, rnd: int, findings: list[dict]) -> None:
    sha = git(repo, "rev-parse", "--short", rev.split("..")[-1]) or rev
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LEDGER.open("a") as f:
        for x in findings:
            f.write(json.dumps({"ts": ts, "repo": repo_name(repo), "slug": slug, "sha": sha, "round": rnd, **x}) + "\n")


def run_codex(repo: str, prompt: str, out: str | None) -> tuple[dict | None, str]:
    """Codex's parsed JSON answer (None if it gave none) and its full log."""
    with tempfile.TemporaryDirectory() as tmp:
        schema = Path(tmp, "schema.json")
        schema.write_text(json.dumps(SCHEMA))
        last = Path(tmp, "last.json")
        run = subprocess.run(
            ["codex", "exec", "-m", MODEL, "-c", f"model_reasoning_effort={EFFORT}", "--sandbox", "read-only",
             "-C", repo, "--output-schema", str(schema), "-o", str(last), prompt],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
        )
        log = run.stdout + run.stderr
        if out:
            Path(out).write_text(log)
        try:
            return json.loads(last.read_text()), log
        except (OSError, ValueError):
            return None, log


def why_failed(log: str) -> str:
    if "model_not_found" in log or "not supported when using Codex" in log or "Model metadata" in log:
        version = subprocess.run(["codex", "--version"], stdin=subprocess.DEVNULL, capture_output=True, text=True).stdout.strip()
        return f"{version} cannot run {MODEL}. Run `brew upgrade --cask codex`, then retry."
    return "Codex gave no JSON answer:\n" + log[-3000:]


def render(ans: dict, rnd: int) -> tuple[str, bool]:
    """Markdown verdict, and whether it passes."""
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    fs = sorted(ans["findings"], key=lambda f: (not f["in_scope"], order[f["severity"]]))
    ok = not any(f["in_scope"] and f["severity"] in BLOCKING for f in fs)
    counts = " ".join(f"{s}:{sum(f['severity'] == s and f['in_scope'] for f in fs)}" for s in order)
    lines = [f"# Codex review round {rnd}: {'PASS' if ok else 'FAIL'} ({counts} in scope; {sum(not f['in_scope'] for f in fs)} pre-existing)", "", ans["summary"], ""]
    if fs:
        lines += ["| # | Sev | Scope | Repro | Class | Where | Finding |", "|---|---|---|---|---|---|---|"]
        for i, f in enumerate(fs, 1):
            title = f["title"].replace("|", "\\|")
            lines.append(f"| {i} | {f['severity']} | {'diff' if f['in_scope'] else 'base'} | {'yes' if f['reproduced'] else 'no'} | {f['class']} | `{f['file']}:{f['line']}` | {title} |")
        lines.append("")
        for i, f in enumerate(fs, 1):
            lines += [f"{i}. **{f['title']}** `{f['file']}:{f['line']}`", f"   - Fails: {f['input']}", f"   - Fix: {f['fix']}",
                      f"   - Prevent ({f['prevent']}{', guidance existed' if f['covered_by_guidance'] else ''}): {f['prevent_detail']}"]
    if ans["architecture_note"].strip():
        lines += ["", "## Architecture note", "", ans["architecture_note"].strip()]
    return "\n".join(lines), ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", help="a commit SHA or base..head; never HEAD")
    ap.add_argument("--focus", help="file: the goal, what changed, and what to check")
    ap.add_argument("--round", type=int, default=1, help=f"review round, 1 to {MAX_ROUNDS}")
    ap.add_argument("--follow-up", help="file: the earlier verdict this commit answers")
    ap.add_argument("--out", help="file for Codex's full log")
    ap.add_argument("--hazards", action="store_true", help="print this repo's most common finding classes and exit")
    ap.add_argument("--close", metavar="SLUG", help="print the guidance changes this loop's findings call for and exit")
    args = ap.parse_args()

    if args.hazards:
        print(hazards(args.repo) or f"No findings recorded yet for {repo_name(args.repo)}.")
        return 0
    if args.close:
        print(close(args.repo, args.close))
        return 0
    if not args.rev or not args.focus:
        print("--rev and --focus are required for a review.", file=sys.stderr)
        return 2
    if re.search(r"(^|\.\.)HEAD", args.rev):
        print("Pin --rev to a SHA (git rev-parse --short HEAD): HEAD moves while you fix.", file=sys.stderr)
        return 2
    if not 1 <= args.round <= MAX_ROUNDS:
        print(f"Codex reviews stop at round {MAX_ROUNDS}. Open the PR and list the open findings under Limits.", file=sys.stderr)
        return 2

    slug = re.sub(r"^codex-focus-", "", Path(args.focus).stem)
    show = f"git show {args.rev}" if ".." not in args.rev else f"git diff {args.rev} and git log {args.rev}"
    follow = (f"\n\nThis is round {args.round}. Your earlier findings, which this change answers:\n{Path(args.follow_up).read_text()}\n"
              "Check each is fixed and that the fix broke nothing new. Do not repeat a finding that is fixed.") if args.follow_up else ""
    arch = ("\n\nThis is the last round. In architecture_note, recommend one design change that would prevent the kind of "
            "findings these rounds kept turning up, or say none is needed.") if args.round == MAX_ROUNDS else ""
    past = hazards(args.repo)
    past = f"\n\n{past}\nCheck these classes, but do not limit the review to them." if past else ""
    classes = "\n".join(f"- {k}: {v}" for k, v in CLASSES.items())
    prevent = "\n".join(f"- {k}: {v}" for k, v in PREVENT.items())
    prompt = (
        f"Codex review · {slug} · r{args.round}\n\n"
        f"Review {args.rev} in this repository ({show}). Read-only: do not edit files. You may run read-only probes and tests.\n\n"
        f"{Path(args.focus).read_text()}{follow}{past}\n\n"
        "Scope: this is a personal project with few users. Weigh each input by how likely real use is to hit it. "
        "Report every P0 and P1, plus at most three P2/P3 items worth knowing. "
        "Mark a finding in_scope=false when the faulty code was already on the base branch.\n\n"
        f"{SEVERITY}\n\n"
        "Give each finding a file and line, the input or state that fails, and a fix. Reproduce it before you report it when you can. "
        "Read AGENTS.md, CLAUDE.md and CODING_STANDARDS.md if the repo has them.\n\n"
        "For each finding, also say how the next agent would avoid writing it:\n"
        f"class:\n{classes}\nprevent (prefer check, test or architecture over standard):\n{prevent}\n"
        "prevent_detail is the specific rule, check or design change, general enough to stop the next instance. "
        "covered_by_guidance is true when a written rule already forbids it.\n\n"
        f"Return an empty findings list when nothing material is left.{arch}"
    )
    ans, log = run_codex(args.repo, prompt, args.out)
    if ans is None:
        print(why_failed(log), file=sys.stderr)
        return 2
    record(args.repo, slug, args.rev, args.round, ans["findings"])
    text, ok = render(ans, args.round)
    p0 = [f for f in ans["findings"] if f["in_scope"] and f["severity"] == "P0"]
    if args.round == MAX_ROUNDS and p0:
        print("# STOP: human review needed\n\n"
              f"Round {MAX_ROUNDS} still has {len(p0)} in-scope P0. After 3 rounds that means the fixes keep missing "
              "or the design is wrong. Do not open the PR and do not fix it again. Send Byron this verdict, "
              "the architecture note and the branch, and wait.\n")
        print(text)
        return 4
    print(text)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
