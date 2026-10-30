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
print("ok")
