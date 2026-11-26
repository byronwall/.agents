#!/usr/bin/env python3
"""Run: python3 -I test_list_sessions.py. Guards the two failure points that cost real retros."""
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ["RETRO_LEDGER"] = str(Path(tempfile.mkdtemp()) / "ledger.jsonl")
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import list_sessions as ls  # noqa: E402

# A worktree named retro-* must not mark a session as a retro: that moved the window start.
reminder = "<system-reminder>\nWorktree path: /x/.claude/worktrees/retro-7e2df5\nWorktree name: retro-7e2df5\n</system-reminder>\nBuild a landing page"
assert not ls.is_retro(reminder)
assert ls.is_retro("Base directory for this skill: /Users/b/.claude/skills/retro\n\n# body")
assert ls.is_retro("<command-name>/retro</command-name>")
assert ls.is_retro("/retro last 20 threads")

# A finding seen again updates its row: repeat dates and PRs accumulate.
f = Path(tempfile.mkdtemp()) / "f.json"
row = {"key": "k", "scope": "repo", "title": "t", "fix": "x", "status": "proposed", "project": "/p"}
f.write_text(json.dumps([{**row, "date": "2026-10-01", "prs": [1]}]))
ls.record(f, "/p")
f.write_text(json.dumps([{**row, "date": "2026-10-20", "prs": [2], "status": "done"}]))
ls.record(f, "/p")
(r,) = ls.ledger_rows()
assert r["seen"] == ["2026-10-01", "2026-10-20"] and r["prs"] == [1, 2] and r["status"] == "done", r

# A message typed while the agent works is a queued command wrapped in reminders; a task notice in the same shape is not Byron.
t = Path(tempfile.mkdtemp()) / "s.jsonl"
queued = lambda text: {"type": "attachment", "timestamp": "2026-11-23T04:03:53Z", "attachment": {"type": "queued_command", "prompt": [{"type": "text", "text": text}]}}
t.write_text("\n".join(json.dumps(x) for x in [
    queued("<system-reminder>\nLinked sessions now\n</system-reminder>\n\nFor the gnarly parts, have Codex review"),
    queued("<task-notification>\n<status>completed</status>\n</task-notification>"),
]))
said = [data for kind, _, data in ls.events(t, "claude") if kind == "user"]
assert said == ["For the gnarly parts, have Codex review"], said
print("ok")
