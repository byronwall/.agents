---
name: queued-orchestrator
description: Run multi-part work from one Claude Desktop session that acts as orchestrator. It splits the work into parallel worker sessions, each in its own worktree and branch, queues dependent layers until their parents land, forwards scope changes to running workers, and assembles every branch into one linear gh-stack PR stack. Use when Byron says `/queued-orchestrator`, asks Claude to "be the orchestrator", "use worker threads/sessions", "run in parallel", "queue it after X", or "stack PRs as you go" for work with several separable pieces. Not for Codex (use `orchestrate-work`) or for a single small change.
---

# Queued Orchestrator

This session coordinates; worker **sessions** do the work. Byron asked for this
shape explicitly: no subagents or background tasks in the orchestrator thread
for agent work, parallel where safe, dependent work queued, PRs stacked.

## 1. Ground and decide (orchestrator, here)

- Ingest the inputs yourself (recordings, transcripts, the code areas). Read
  just enough code to name concrete files, functions, and root causes.
  Workers get facts, not "go investigate".
- Ask product questions with `AskUserQuestion` before splitting work. Use
  `consider-contrast` when a real choice exists, then give a choice.
- When a worker's report or Byron's follow-up exposes a gap ("does X happen
  automatically?"), verify it in the code before answering, then route it.

## 2. Split by file ownership

Draw the piece list as a dependency graph, not a feature list.

- One worker per independent piece. Give each an **owned file set** and a
  "do not touch" list naming the other workers' files. Shared hot files (a
  route that wires everything) get "minimal edits only" in every brief.
- Big refactors that unblock redesigns are their own bottom layer, with
  no behavior change and tests that pin current behavior.
- A piece that needs another's result is **queued**, not started. Track it as a
  pending plan step with the parent named.
- Decide the final stack order up front: foundations at the bottom (server or
  data, then refactors), the queued layers right above their parents, then
  independent UI layers.

## 3. Launch workers

Load `mcp__ccd_session__start_session` first. Then, in one message:
`mark_chapter` ("Wave N …"), a bold title line plus one sentence for each, and
the `start_session` calls in parallel with:

- `initiation: "user_asked"`, `context: "fresh"`, `use_worktree: true`
- short `name` and `branch_name` (for example `canvas-rail`), which you reuse as the plan
  step's `session`
- `background`: product context, Byron's decisions so far, root causes found,
  and how this piece fits the whole
- `prompt` (the brief) with:
  - the task as concrete changes, naming files and identifiers in backticks
  - owned files and a "do not touch" list
  - which repo skills apply (taste, motion, Solid, audit harness)
  - verification: the repo's lint/type-check/test plus a browser pass where it
    applies, with screenshots kept in an ignored folder
  - git: **commit on your worktree branch as you go (each verified step) so a
    crash loses little; do NOT push or open a PR; the orchestrator assembles
    the stack**
  - the report: branch name, what changed, verification results, and anything
    left over

Then update the plan with each step's `session`, wrap up, and end the turn.
Do not wait, poll, or predict results.

## 4. While workers run

- **Scope change for a running worker:** send it with `SendMessage` to its
  `local_…` id, telling it to make the change as its own commit on the same branch.
  The first line must say what the message is about.
- **New dependent work** ("queue it after X"): add a pending step, then start it
  from X's branch (`source_branch`) once X reports and you've checked its
  diff. Never start it early on a guess.
- **New independent work:** start another worker if its files don't overlap;
  otherwise queue it behind the owner.

**When Byron says "keep going":** check `list_sessions {"linked": true}`,
then each branch's `git log main..<branch>` and worktree `git status`. A
worker that is idle with no report was usually killed (look for `exit code 143`
in `list_events`). Resume it with `SendMessage`, telling it what is already in
its worktree and what is left. Don't start a new session for it.

## 5. When a worker reports

The note is a claim, not proof. Check `git log`/`git diff main...<branch>` and
the stated test results before marking the step done. Then:

- start any queued layer that was waiting on it
- send fixes back to the same worker (`SendMessage`) instead of starting a new one
- once every layer is in, assemble the stack

## 6. Assemble the stack (orchestrator, here)

Follow the `gh-stack` skill. Branches already exist, so adopt them in order:

```bash
git config rerere.enabled true
gh stack init <bottom-branch> <next-branch> ... <top-branch>
gh stack rebase            # resolve conflicts layer by layer, then --continue
```

- `gh stack rebase` refuses to run if any worker worktree has untracked or dirty files
  (stray screenshot specs are common). Move them to the scratchpad instead of
  deleting them, then run the rebase from any stack worktree.
- When a lower layer only reformatted a file (Prettier), check that by
  formatting both sides and diffing, then keep the upper layer's version
  and re-format it.
- Resolve conflicts in the layer that owns the change. Re-run the checks at
  the top of the stack after the rebase.
- Push and open PRs only when Byron has asked for PRs ("stack PRs" counts):
  `gh stack submit --auto`, then fix titles and bodies with `gh pr edit`
  (include screenshots with `--attach`; never commit them).
- Report each layer's PR link and what the checks did not cover.

## Guardrails

- Two writers never share a file set. When in doubt, queue instead of parallelizing.
- Workers never push or open PRs; only the orchestrator does.
- Keep this thread light: plan, route, review, assemble. Small checks (a grep,
  a diff) are fine here; implementation goes to workers.
- Keep the plan honest: exactly one step in progress, and running sessions
  shown on their steps.
