---
name: token-burn
description: Find work that is worth spare usage on the strongest frontier model (today Claude Fable) before the weekly limit resets. Survey Byron's active repos and planning tasks, keep only ideas where the frontier model changes the result and an existing machine check proves it, verify the top picks against origin/main, and write a ranked list with IDs, baselines, pre-flight questions, and a run prompt to a planning task. Use when Byron says `/token-burn`, "I have spare usage", "burn tokens", "what should Fable work on", "use up the weekly limit", "big project for the best model", or asks for ambitious unattended work across his repos. Not for running a picked idea (that is `queued-orchestrator`) or for one small task.
---

# Token Burn

Two things are scarce here: frontier tokens that expire at the weekly reset,
and Byron's attention. The best idea turns many tokens into a result that a
cheaper model could not reach, and it needs Byron only at the start and at the end.

This skill finds and prepares that work. It does not run it.

## The bar

An idea goes on the list only if it passes all six checks.

1. **Frontier delta.** Name the failure a weaker model would make. Good reasons:
   - an exact port or rewrite with no tolerance for drift
   - a long chain of dependent steps across many files
   - diagnosis of a fault that has resisted earlier attempts
   - design judgment against a quality bar or a rubric
   - a search where each round reads the result of the last one

   "It is big" is not a reason. Bulk renames, format changes, simple content
   fills, and one-pattern refactors go to a cheaper model.
2. **An existing gate.** One command, already in the repo or cheap to add first,
   decides pass or fail: byte parity, a test suite, a benchmark budget, an eval
   score, a validator, or a screenshot proof. Write the command, today's value,
   and the target value. With no gate, a long run drifts.
3. **Unattended.** Every design decision can be answered before launch. Each
   remaining question becomes a pre-flight question (see "Report").
4. **Fits the window.** The run can reach its gate before the reset with the
   usage that is left. If it cannot, cut it to the largest milestone that can.
5. **Lasting value.** The result ships, unblocks other work, or removes a real
   risk. A report that nobody reads does not count. Work that a cheaper model
   will do well next week is low value now.
6. **Safe.** It never sends, posts, publishes, deploys, or spends money. Flag
   web access and paid APIs.

## Burn shapes

Pick the shape that turns the most tokens into quality. Each one needs the gate.

- **Deep run:** one orchestrator and two to four workers on one hard change.
  This is the default.
- **Score loop:** measure, change, measure again until the score moves past the
  target or stops moving. Use it for quality scores, perf, and evals.
- **Best of N:** two or three workers try different approaches in parallel, and
  the gate picks the winner. Use it when the right design is unclear and a gate
  can rank the results.
- **Wide fan-out:** many workers on many same-shape units (books, files, plans),
  with a validator on each unit and a frontier review of a sample. Use it only
  when each unit needs judgment. Otherwise a cheaper model does it.

## Process

### 1. Budget and window

- Name the strongest model now. Today it is Fable (`fable` in the Agent tool,
  `claude-fable-5-2` in the API). Use a newer frontier model if one exists.
- Read the limits with `mcp__ccd_session_mgmt__get_usage`. It returns several
  windows. Three of them matter:
  - **Weekly for that model** (for example "Weekly · Fable"): this is the
    budget, and its reset is the deadline. The last run stopped at this limit.
  - **Weekly · all models:** the survey and any cheaper workers use this one.
  - **5-hour limit:** it can stop a run partway. Checkpoint commits cover it,
    so it limits pace, not scope.

  If the tool is missing or says `unavailable`, ask Byron in one line.
- Turn the budget into a count of runs. Use the usage figures in the task's
  `## Outcomes` to estimate the cost of one run. With no figures, plan two deep
  runs per full weekly budget, and say that this is a guess.

### 2. Sources

Read these before you survey code. They tell you what Byron cares about now.

- **An open token-burn task.** Run `grep -l token-burn ~/Projects/planning/tasks/*.md`.
  If one is open, refresh it: mark shipped ideas, drop stale ones, and read its
  `## Outcomes`. Do not start a second list.
- **Planning tasks.** Read the `active` tasks and any overdue check-ins in
  `~/Projects/planning/tasks/`. A task that waits on agent work is a strong lead.
- **Active repos.** Rank the repos by recent commits:

  ```bash
  for d in ~/Projects/*/; do
    [ -d "$d/.git" ] || continue
    n=$(git -C "$d" log --since='30 days ago' --oneline 2>/dev/null | wc -l | tr -d ' ')
    [ "$n" -gt 0 ] && echo "$n ${d:t}"
  done | sort -rn | head -20
  ```

Weight the list toward where Byron spends his time. Two strong ideas in his most
active repo are worth more than one weak idea in each of ten repos. If Byron
named a count or a scope, use his.

### 3. Survey

Fan out read-only survey agents, about five repos each, on a cheaper model
(`sonnet`). They collect facts. You judge. Give each agent this brief:

- Run `git fetch` first, and read `origin/main`, not the local branch. Report
  how far the local checkout is behind.
- Open plans (`docs/intent/*`, `docs/plans/*`, `TODO.md`, PRDs): the milestone
  each one reached, and which milestones already shipped (merged PRs, code on
  main).
- Open PRs and issues, with counts and ages.
- Hard spots: the largest files, untyped or untested core code, slow suites,
  known quality scores, and perf baselines.
- Gates: the exact commands for tests, parity, bench, evals, and proofs. Also
  read the CI workflow and list what CI runs that the local check does not.
- Blockers: decisions that wait on Byron, missing credentials, paid APIs.
- Give paths, counts, and command output. Do not give adjectives.

### 4. Draft and cut

Write candidates from the survey, then apply the bar. Cut hard. A short list
that all passes is better than a long list that Byron must filter. Merge ideas
that touch the same files, or mark them `not with <ID>`.

### 5. Verify the top picks yourself

Survey facts are leads, not truth. For each top pick:

- Read the files that the idea names on `origin/main`, and confirm the numbers.
- Check that the work did not already ship: `git log origin/main` on those paths,
  and `gh pr list --state merged --search <keyword>`.
- Run the gate command if it finishes in about two minutes, and record the
  baseline value. Otherwise copy the latest value from CI or the docs, and name
  where it came from.
- Write down each design question that a worker would hit. Do not guess the
  answer for Byron.

Mark each fact in the idea as `verified` or `from survey`.

### 6. Write the task

Write to the open token-burn task, or create the next
`~/Projects/planning/tasks/TASK-NNNN.md` in the format of the other tasks
(front matter, `## Work breakdown`, `## Next actions`, `## Updates`).

Each idea uses this form:

```markdown
- `DRAFT-1` **Port the engines to TypeScript.** <facts with paths and numbers>
  - Frontier delta: <the failure a weaker model would make>
  - Shape: deep run | score loop | best of N | wide fan-out
  - Gate: `pnpm test:engines` parity 320/320 against `reference/v7`; `pnpm bench` within budget (baseline: verified 2026-11-14)
  - Size: <runs or hours>; fits the window: yes | cut to <milestone>
  - Pre-flight: <questions for Byron, or "none">
  - Flags: <needs Byron | web | paid API | not with <ID>>
```

Then add:

- **Top picks:** three to six ideas that fit the budget, in order. Rank by
  frontier delta, then value, then gate strength. Give one line on why each one
  beats the next idea.
- **Notes for a run:** shared files, stale checkouts, and the flags.
- **Run prompt:** the block in "Run handoff", with the task ID filled in.

### 7. Report

Give Byron a table of the top picks (ID, repo, frontier delta, gate, size,
pre-flight count) and a link to the task. Ask which ideas to run.

When he picks, ask all pre-flight questions for those ideas in one batch, with
your recommended answer first. Write the answers into the ideas. Only then hand
off. One batch now saves several interruptions during the run.

## Run handoff

Hand each picked idea to `queued-orchestrator` with this prompt:

```prompt
Read tasks/TASK-NNNN.md in ~/Projects/planning and find the idea <ID>. Its pre-flight answers are final.
Open its repo in a new worktree from origin/main. Read AGENTS.md and the files the idea names.
Use the queued-orchestrator skill. Run every worker on the strongest model. Use the idea's burn shape.
The gate in the idea decides done. Never edit the gate, its reference outputs, its thresholds, or its tests to make it pass.
If the gate cannot be met, stop and report the gap with numbers.
Commit after each working piece, so a usage limit loses nothing. After a limit, resume the same workers; do not start new ones.
Before each push, run every command the CI workflow runs, not only the local check.
If the run finishes a docs/intent plan, retire the plan in a final PR.
Ask Byron only about a decision the pre-flight did not cover. Record each scope change and result as dated bullets under ## Updates.
```

If a session cannot start other sessions (for example over Remote Control), run
the workers as subagents with `model: fable` instead.

## After a run

Add one line per finished idea under `## Outcomes` in the task: the ID, whether
the gate passed, the PRs, the percent of the model's weekly limit it used (read
`get_usage` before and after), and Byron's verdict.
The next token-burn run reads these lines to size ideas and to see which shapes
paid off.
