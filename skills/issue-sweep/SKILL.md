---
name: issue-sweep
description: Load every open issue in a repository, group them by the code they touch, resolve the groups in batches of worker sessions, and merge each PR as it passes CI, until all issues are closed and all PRs are merged. Defaults to GitHub issues; follows another tracker (Linear, Jira, a GitHub Project, a doc or list) when Byron names one. Use when Byron says `/issue-sweep`, "check all the issues", "resolve all the issues", "group them and resolve them", "clear the issue backlog", or "merge as you go" for a whole issue list. Not for one issue (just fix it) or for planning-only work (use `ticket-fan-out`).
---

# Issue Sweep

Goal: **end with every in-scope issue closed and every PR from this sweep merged.**
This session is the orchestrator. It reads the issues, groups them, runs
workers, checks their work, opens PRs and merges them. Workers write the code.

Use the `queued-orchestrator` skill for the worker mechanics (worker briefs,
file ownership, the 3-session limit, refused starts, stack assembly, landing
PRs). This skill adds the issue-specific steps around it. Use `gh-stack` for
stack commands.

## 1. Find the issue source

- **Default:** GitHub issues for the current repository.
  ```bash
  gh issue list --state open --limit 200 --json number,title,labels,body,comments,updatedAt
  ```
  Then run `gh issue view <n> --comments` on any issue whose body is short or
  points to something else.
- **Another tracker:** when Byron names a source (a Linear team or project, a
  Jira board, a GitHub Project, a milestone, a label, a Visual Notes list, a
  doc, a pasted list), follow it to the real items:
  - Look for a connected tool first with `ToolSearch` (for example "linear
    issues", "jira"). Use a CLI only if no tool exists (`gh project item-list`,
    `jira`, `linear`).
  - Follow links inside items (a GitHub issue that points to a Linear ticket,
    a doc that lists issue numbers) until you have the items that hold the
    actual requests.
  - Note how that tracker comments on and closes an item. You use the same
    tracker for both at the end.
  - If no tool or CLI can read the source, tell Byron and ask for an export.
- **Scope:** all open items unless Byron gives a filter. Leave out items that
  are only discussion, a question to Byron, or blocked on something outside
  the repo. List them in the first report with the reason.

## 2. Read and ground

- Read every in-scope issue in full, comments included. Read the open PRs
  too (`gh pr list --state open`), so you know which issues already have work
  in flight and which branches touch the same files.
- For each issue, read just enough code to name the files, functions and
  likely root cause. Workers get facts, not "go investigate".
- Ask product questions with `AskUserQuestion` only where an issue leaves a
  real choice open. Ask them all in one round before you start workers.

## 3. Group

Group by **the files the fix touches**, not by label or theme.

- Issues that change the same files go in one group, run by one worker. Inside
  a group, each issue gets its own branch, stacked in a sensible order (for
  example, the DSL group in draftably was escapes → `count=N` → `note`, three
  branches, one stack).
- An issue that needs another group's result is **queued** behind that group,
  and its worker starts from the parent's branch (`source_branch`) after you
  check the parent. In draftably, export (#246, #247) waited for the viewer
  frame (#238) because exports had to match the viewer.
- A large or risky issue (performance, a rewrite) is its own group and runs
  last, so it does not block the quick wins.
- Order the queue: independent and quick groups first, then dependents, then
  the large ones.

Write the groups to a plan file in the scratchpad (group, issues, owned files,
depends on, status). Update it as groups move. Then report the grouping to
Byron in a short list, and start work in the same turn. Don't wait for
approval unless a product question is open.

## 4. Run the batches

Follow `queued-orchestrator` sections 3–5. The points that mattered here:

- **At most 3 live workers.** Start a new one each time one finishes.
- Each brief names its issue numbers and says: one commit per verified step,
  one branch per issue, `Closes #N` in each commit body, no push, no PR,
  screenshots for any visible change (before and after) in an ignored folder,
  and a report that says what is **not** done.
- A performance issue's brief asks for a timing table (main vs branch) and a
  quality check (audit, snapshot, or test suite) so a speedup can't hide a
  regression.
- A worker's report wakes you as an automated turn, where `start_session` may
  be refused. When Byron is at the keyboard, start the next workers in his
  turn. If a start is refused, leave the card and say in one line that it
  waits for him.

## 5. Check each report

The report is a claim. Before a PR:

- Read `git log` and `git diff main...<branch>`. Confirm the diff fixes what
  the issue asks, not a nearby thing.
- Confirm the stated checks passed (the worker's output, or run the fast check
  yourself).
- Look at the screenshots. If a "before" image looks wrong, render a new one
  from main. In draftably, a worker's "before" image was out of date and made
  an unchanged layout look different.
- Send fixes back to the same worker with `SendMessage`. Don't start a new one.

## 6. Open PRs and merge as you go

- One PR per issue. Single branch: `gh pr create`. Several branches in a group:
  `gh stack init ...` then `gh stack submit --auto`. Fix titles and bodies with
  `gh pr edit`, with `Closes #N`, screenshots through `--attach`, and a
  "Not done" section when the worker left a part out.
- **Read the CI result before every merge.** A watch that exits 0 is not a
  pass. In draftably, a stack merged while its `proofs` job had failed.
  Run `gh pr checks <n>` and confirm every check passed, then merge.
  - Single PR: `gh pr merge <n> --auto --merge`, and GitHub merges it on pass.
  - Stack: watch the top PR's checks in the background (one
    `gh pr checks <top> --watch` with `run_in_background: true`), read the
    result, then `gh stack merge <top> --yes`.
  - A failed check: rerun it once if it looks flaky, and confirm on main's CI
    after the merge. Otherwise send it back to the worker.
- Rebase the remaining stacks on main after each merge, and re-run the fast
  check at the top.
- Quote Byron's words ("Merge as you go") in each merge command's description
  so auto mode sees the approval.

## 7. Close out

- Confirm each issue closed when its PR merged. Close any that didn't, with a
  comment that links the PR. For a performance issue, post the timing table on
  the issue first.
- A part a worker left out: open a new issue for it and link it from the
  closed one. Don't leave it only in a PR body.
- For another tracker, comment and close there, with the PR link.
- **Don't merge PRs that existed before the sweep** without asking Byron.
  A "Version Packages" or release PR publishes a package. Research and plan
  PRs are not meant to merge. List them at the end and ask.
- Final report: each issue → PR → merged, any new follow-up issues, the
  skipped items with reasons, and the pre-existing PRs that wait on Byron.
