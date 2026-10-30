---
name: retro
description: "Conduct a retrospective on recent coding sessions in the current project and suggest improvements to the agent's environment. `/retro ledger` checks only what other repos' retros learned against this repo. Use when Byron says `/retro`, `$retro`, asks for a retro or retrospective, or asks whether the retro log has relevant items for this repo."
disable-model-invocation: true
---

The user has asked for a **retrospective**. You suggest improvements to the coding agent's **environment** to improve future runs. You present findings and stop; Byron decides what to fix.

## Modes

- `/retro`: the full retro below.
- `/retro ledger`: step 2 only. Check other repos' findings against this repo, present the ones that apply, and stop.

## Scope (defaults)

Unless the user says otherwise:

- **Project**: the repo you are running in, worktrees included. Go broader only when asked.
- **Harness**: the one you are running in (Claude Code transcripts or Codex rollouts). Read both only when asked.
- **Window**: every session since the previous retro in this project (3 days if none in the last 30). A user-named session, time frame, or count wins.

State the scope in one line at the top of your reply.

## Tools

Everything deterministic is in the script. Never `cat` a transcript and never write your own parser. If the script lacks something you need, add it to the script.

```bash
R=~/.agents/skills/retro/scripts/list_sessions.py
python3 $R --last-retro        # previous findings; PR landing checked against origin's default branch
python3 $R --ledger            # other repos' findings; runs their checks here
python3 $R                     # sessions in the window (--days N, --source claude|codex|all)
python3 $R --scan > $TMPDIR/retro-scan.txt   # window report; saves this retro's metrics
python3 $R --scan --section users            # one section, full text (sessions|trend|fails|denials|slow|users)
python3 $R --digest FILE       # one session plus its subagents
python3 $R --record FILE       # upsert findings into ~/.agents/retro-ledger.jsonl
```

Subagent transcripts fold into their parent session: `S3.a2` is subagent 2 of session 3.

## Steps

1. **Previous retro.** Run `--last-retro`. A PR that says "NOT on origin/main" did not land, whatever its status says. A finding that came back is more severe the second time; a ledger row with `seen 2x` or more is a repeat.
2. **Ledger.** Run `--ledger`. Each item that says **applies** goes into this retro's list, marked "from <repo>". For each **judge** item, decide from its lesson and a quick look at the repo. Skip items that are clearly irrelevant, without comment.
3. **Scan.** Run `--scan` and read it in this order:
   - **Trend**: the change since the last retro. A fix that didn't move its number is a finding.
   - **Phrases you repeated** and **Likely corrections**: each repeat is a missing default, check, or skill rule.
   - **Failed calls**, **Permission denials**, **Slowest calls**: these point to the sessions worth a `--digest`.

   Open raw transcript lines only to confirm one finding. With more than ~10 sessions to dig into, hand batches to subagents that return findings with evidence.
4. **Look for candidates** in these categories:
   - **Navigation**: the agent took long to find a file or fact. Fix with a **navigation pointer**.
   - **Automated checks**: an agent mistake that a check could catch, or a repo with no **guardrail** (pre-commit hook running lint/typecheck/test). Read the repo's own check scripts and CI first; a check that exists but is unwired or broken is the finding. Suggest CI only where CI exists.
   - **Coding standards**: the reviewer missed a mistake. A **mechanical** violation gets a deterministic check (lint rule, hook, or existing CI job), not a rule. `CODING_STANDARDS.md` holds judgement calls only.
   - **Verification**: the agent declared success without evidence (unviewed screenshots, skipped checks, no real run), or the user found a defect the agent should have seen.
   - **User steering**: a phrase repeated across sessions, or a correction. Each one is a missing instruction, check, or skill default.
   - **Permission denials**: a repeated denial reason means a brief, a script file, or an allowlist entry is missing.
   - **Steering files**: a large `AGENTS.md`/`CLAUDE.md` (repo or global). Move rules to checks or standards, and delete lines that change no behavior.
   - **Tool economy**: expensive or token-heavy calls, including custom CLIs and MCPs.
   - **Information access**: a crucial fact the agent could not reach (dev server logs, deploy SHA, read-only service access).

   [references/where-fixes-live.md](references/where-fixes-live.md) says where each kind of fix belongs.
5. **Present** a numbered list in order of severity, so the user can answer "do 1, 3, 5". For each item give:
   - the evidence (session and a short quote, tool error, or metric),
   - the fix and where it lives (check, `CODING_STANDARDS.md`, `AGENTS.md`, repo skill, global skill, or a setting Byron must change),
   - its history: new, a repeat (with count), or from the ledger (with source repo).

   Then a short **What went well** list: patterns to keep, so a fix doesn't break them.
6. **Record** every presented item with `--record`, status `proposed`. Use one JSON object per item:

   ```json
   {"key": "no-precommit-guardrail", "scope": "repo", "title": "No pre-commit hook runs lint and typecheck",
    "fix": "Add .githooks/pre-commit running pnpm lint + type-check", "target": ".githooks/pre-commit",
    "lesson": "Every repo needs a local hook running its lint and typecheck",
    "check": "! git config core.hooksPath >/dev/null && [ ! -x .git/hooks/pre-commit ] && [ ! -d .husky ]",
    "status": "proposed"}
   ```

   - `key`: a stable slug. Reuse the ledger's key when the same problem shows up again, so repeats accumulate on one row.
   - `scope`: `repo` or `global`. Only `repo` items are offered to other repos.
   - `lesson`: one line that another repo can act on without this repo's context.
   - `check`: for mechanical items, a zsh command run at a repo root that exits 0 when the problem is present. Leave it out for judgement items.
7. **Stop.** Don't start fixing until Byron picks items. When he picks:
   - For each item, compare a few options with `consider-contrast` and pick the best or a hybrid.
   - Repo changes go out as stacked PRs, one item or a tight group per PR.
   - Edit global skills in place under `~/.agents/skills/`, with no PR.
   - Record the result: `picked` or `done` with `prs`, and `declined` for items he passed on.
