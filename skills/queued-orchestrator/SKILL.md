---
name: queued-orchestrator
description: Run multi-part work from one Claude Desktop session that acts as orchestrator. It splits the work into parallel worker sessions, each in its own worktree and branch, queues dependent layers until their parents land, forwards scope changes to running workers, and assembles every branch into one linear gh-stack PR stack. Use when Byron says `/queued-orchestrator`, asks Claude to "be the orchestrator", "use worker threads/sessions", "spawn workers", "run in parallel", "crank on them in parallel", "throw up PRs", "queue it after X", or "stack PRs as you go" for work with several separable pieces. Not for Codex (use `orchestrate-work`) or for a single small change.
---

# Queued Orchestrator

This session coordinates; worker **sessions** do the work. Byron asked for this
shape explicitly: no subagents or background tasks in the orchestrator thread
for agent work, parallel where safe, dependent work queued, PRs stacked.

## 0. Where the orchestrator runs

- Start the orchestrator in its own worktree from the first message, or stay in
  the main checkout. Don't call `EnterWorktree` mid-session: after it, the
  isolation check refuses git with `-C`, loops or chains that contain git, and
  pnpm or python commands with a `$VAR` path. If you're already inside one, run
  one plain git command per call and write helper scripts to files.

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

Run at most **3 workers at once that start a dev server, run e2e, or run the
full check suite**; queue the rest as the next wave. On Oct 21, seven at once
made the first page load take 4–5 minutes, a check chain take 430s, and a
Playwright run time out; on Oct 24 two parallel vitest runs swapped the Mac.
Workers that only read or edit docs don't count. Tell each heavy worker to
stop its dev server and drop its audit database before reporting.

Then update the plan with each step's `session`, wrap up, and end the turn.
Do not wait, poll, or predict results.

### When `start_session` is refused

Over Remote Control, `start_session` is refused ("you can start a session only
on a message typed in the desktop app"). Tell Byron in one line, then fall back
to `Agent` with `isolation: "worktree"` and `run_in_background: true`. Those
workers run under a strict isolation check that refused 103 commands in one
round. Add this to every fallback brief:

- Stay inside your own worktree. Never read or write the orchestrator's `tmp/`,
  scratchpad or worktree by absolute path. If you need a baseline, build it in
  your own `tmp/`, or use the repo's own baseline tool (in diagram-studio,
  `pnpm audit:compare --base <ref>`).
- One plain git command per call: no `git -C`, no git inside loops or `&&`
  chains, no `git worktree add`.
- Put any loop, multi-step pipeline or inline program (`node -e`, `python3 -`)
  in a script file under `tmp/` and run that file.
- You are a subagent: skip `update_plan` and `wrap_up` (the app refuses them),
  and hand back with the report described above.

## 4. While workers run

- **Scope change for a running worker:** send it with `SendMessage` to its
  `local_…` id, telling it to make the change as its own commit on the same branch.
  The first line must say what the message is about.
- **New dependent work** ("queue it after X"): add a pending step, then start it
  from X's branch (`source_branch`) once X reports and you've checked its
  diff. Never start it early on a guess.
- **Byron will be away:** a worker's report wakes you as an automated turn, and
  `start_session` is refused there. So when Byron says he'll step away, or the
  chain is long, start every queued worker now, in his turn. Each brief says
  "wait: edit nothing until the orchestrator messages you that `<parent branch>`
  landed", names the plan docs by branch and path (`git show <branch>:<path>`;
  they may not be on main yet), and allows only reading meanwhile. Release each
  worker with `SendMessage` and the exact branch to restack on.
- **How a waiting worker waits:** on your `SendMessage`, or on an exact head
  branch (`gh pr list --head <branch> --state merged`). Never on a marker
  through `gh pr list --search`: GitHub search is fuzzy and matched step 2's PR
  for step 5.
- **Memory-heavy runs** (a big repo's analysis or Program build, a survey): at
  most one at a time across all workers, each with a heap cap in its brief
  (`node --max-old-space-size=4096`). Two at once swapped the Mac on Oct 25 and
  a cleanup session killed one of them.
- **New independent work:** start another worker if its files don't overlap;
  otherwise queue it behind the owner.
- **Base branch owned by a running session** (Byron says "stack on top of
  @[other session]"): that branch keeps moving. `git fetch` it again right
  before you branch from it and before each PR, and when the other session
  reports a push, restack onto it before building further.
- **Reading worker progress:** use `get_session`, `list_events`, the worker's
  report, and its branch (`git log`, `git diff`). Never `Read` a session's
  `.jsonl` transcript; one costs about 60K characters.

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

## 7. Separate PRs to main (when Byron wants each fix as its own PR)

Sometimes each worker opens its own PR against main instead of a stack (for
example, a batch of fixes from one audit). File ownership still decides what
runs in parallel:

- Before launching, list the files each fix will change. Two fixes that both
  touch a hot engine file (a compile or layout pass, a router) are not
  independent: run the second on the first's branch, or queue it until the
  first merges.
- Tell each worker which other PRs are in flight and which shared files they
  touch, so it keeps its edits there small.
- Merge in dependency order, and have each later worker merge main and re-run
  its checks and audit before its PR merges. Don't merge a PR that GitHub shows
  as conflicting.

## 8. Landing PRs ("merge once CI is green")

Don't poll: no `sleep` loops on `gh pr checks` or `mergeable`, and no
foreground `gh pr checks --watch` (one ran 601s).

- Byron's words ("merge #50 once CI is green", "get them merged") are the
  approval. Quote them in the merge command's description so the auto-mode
  classifier sees it.
- Queue each PR with `gh pr merge <n> --auto --merge` and move on; GitHub
  merges it when checks pass. If the repo has auto-merge off, tell Byron once
  (Settings → General → Allow auto-merge) and use the fallback below.
- Stacked PRs: do not queue layers with `gh pr merge` or retarget them with
  `gh pr edit --base`. Wait for the top layer's checks, then run
  `gh stack merge <top-pr> --yes`. It merges that PR and every layer below it
  in one step.
- Fallback without auto-merge: one `gh pr checks <n> --watch` with
  `run_in_background: true`, then merge on its exit notice.

## Guardrails

- Two writers never share a file set. When in doubt, queue instead of parallelizing.
- Workers never push or open PRs; only the orchestrator does. The exception is
  separate PRs to main (section 7), where each worker opens its own.
- Keep this thread light: plan, route, review, assemble. Small checks (a grep,
  a diff) are fine here; implementation goes to workers.
- Keep the plan honest: exactly one step in progress, and running sessions
  shown on their steps.
