---
name: break-it
description: >-
  Try to break a change on purpose, judge which breakages matter with a Swiss-cheese read, reproduce the ones
  worth it, and write up what held and what broke. Maps the boundary (inputs, outputs, implicit assumptions about
  order, concurrency, restarts, a second user or tab), lists fault-injection points and how each failure would be
  observed, triages candidates into test / accept the risk / skip, tests the top ones against a running system
  or a probe with kept evidence, checks base to tell new from pre-existing, and draws Draftably diagrams. Use for
  "break it", "try to break this", "break-it pass", step 3 of Byron's review gate, "my normal process of trying to
  break it", adversarial testing, edge-case or failure-mode hunting on a PR, branch or feature, or "what could go
  wrong with this", even when the user doesn't say "break-it".
---

# Break it

Break the change on purpose, but spend the effort where a real person would get hurt. The run has six parts: **inspect** the boundary, **triage** candidates with a Swiss-cheese read, **test** the ones worth it, **verify** each result, **explain** with diagrams, and **summarize**. The triage is what makes this different from poking at edge cases: every candidate names the conditions that must line up, how often each is true, and who would be there when they do, so "legitimate problem" and "deep in the internals, accept it" are decisions you can show, not moods.

Keep everything for the run in one folder, the **run folder**: the ledger, probe scripts, raw evidence, diagrams and the report. Budget about 45 minutes for a typical PR; the usual overruns are diagram fiddling and test-harness setup, so cap both (see steps 3 and 5). In Byron's planning workspace that is the owning task's assets (see [Inside Byron's review gate](#inside-byrons-review-gate)); elsewhere, the session scratchpad or a git-ignored `tmp/break-it/<target>/`. Never write into an untracked folder of the repository under test.

## 0. Pin the target

Write down, at the top of the report: the change (PR, branch or commit range), its head SHA, the base it is compared with, and how you can run it (a dev server, a test harness, a CLI, a unit-level probe), including the working directory and config files it reads. Fetch the base first; a stale base makes pre-existing failures look new. For a stacked PR, the base is the commit this layer sits on: the parent of the PR's first commit (`gh pr view <n> --json commits --jq '.commits[0].oid'`, then `<oid>^`). Not `git merge-base origin/main`, which sweeps in every layer below, and not the parent branch's current tip, which may have moved since a restack. Say which commit you used.

Test the pinned head. Commits pushed after it are not part of the target; look at them only in step 4, to say whether a break you already found is fixed there. If nothing can run the code at all, say so now: the run then ends at a triaged ledger and the report marks every candidate untested.

Set up a way to run the **base** too, without touching the checkout, because step 4 needs it for every break: `git archive <base-ref> | tar -x -C <run>/base-src`, then run the same probe with that copy first on the path (for Python, `PYTHONPATH=<run>/base-src/<pkg-root>:<run>`; note that `python <run>/probe.py` puts the run folder, not the current directory, on the path, so set `PYTHONPATH` explicitly for both head and base).

## 1. Inspect: find the boundary

Start at the changed code and walk outward until you hit something real on each side, then stop. Walking out matters because the best findings usually live just outside the diff, in the caller that assumes an order or the deploy config that picks the code path. Stopping matters because past the first real boundary you are auditing the whole system.

- **Inward (inputs):** follow callers out to a real entry point, something a person, another process, a deploy or a clock drives: a route, a socket message, a CLI flag, a scheduled job, a config value, an environment variable, a file the app reads. Then take one more hop to whatever selects this code path (feature flag, config, deploy template).
- **Outward (outputs):** follow what the change produces until it lands somewhere you can observe: UI text, a response body or status, a stored row or file, a log line, a trace span or metric, a message to another service.

Write the **boundary card** in the run folder (`boundary.md`), using [references/inspection.md](references/inspection.md) for the checklists:

1. **Actors and entry points:** who or what drives each input, including the ones the author didn't picture (a second tab, a second user, a retry, a scheduled job, an agent, an old client during a deploy).
2. **Inputs and how each can vary:** for each input, the variations from the input catalog that make sense here. Say which you'll consider and why the rest don't apply.
3. **Outputs and where each is observed:** the destination and the exact thing you'd look at (the UI string, the query, the log event name, the span).
4. **Implicit assumptions:** what the internals rely on without checking: ordering, single writer, idempotence, timing, a value being present, a process staying up, a cache being fresh, one process per host. Each assumption names the code that relies on it (`path:line`).
5. **Claims:** each behavior the PR description, docs or comments promise ("the tint and tooltip always agree", "refused requests are logged"). Security concerns receive source review and remediation guidance. Use runtime probes and mutation tests for functional correctness and reliability. Each functional claim is a candidate, and a claim a probe contradicts is reported whatever its harm, because the reviewer will believe it.
6. **Fault seams:** each place a fault can be injected (kill the process, drop the connection, delay a call, return an error, reorder two events, run two copies), how you'd inject it here, and which output would show it.

Then draw the boundary diagram ([references/diagrams.md](references/diagrams.md)). If you can't draw it in about a dozen boxes, you walked too far.

## 2. Triage: the Swiss-cheese read

Turn the card into candidate breakages. A candidate is a story: *who* does *what*, which *holes* line up, and what *harm* follows.

If one running server or harness can answer many candidates with a command each, run that cheap sweep now and record the results as you write the candidates. The triage still decides which candidates get the deeper work (the real-boundary check, the control, the base run, the diagram) and which are reported as accepted risk even though a probe touched them.

Write each candidate into the ledger (`ledger.json`, format in [references/ledger.md](references/ledger.md)), then let the script bucket them:

```bash
python3 ~/.agents/skills/break-it/scripts/cheese.py triage <run>/ledger.json
```

For each candidate:

- **List the holes:** the conditions that must all be true, one per defense layer (deployment shape, client behavior, timing, a check in the code, a user action). Merge two holes that always come together; that is one slice, and counting it twice makes a candidate look safer than it is.
- **Band each hole** on the ladder: `always`, `routine`, `occasional`, `rare`, `contrived`. Judge each *given the holes before it*. A one-line reason is required for every `rare` and `contrived`, naming the person and the setup; "rare" without a person is how niche cases sneak in and real ones sneak out.
- **Name the harm** on the ladder: `cosmetic`, `recoverable`, `stuck`, `wrong` (silently wrong result or saved state), `exposure`, `loss`. Silent beats loud: a wrong number nobody notices is worse than a crash. Judge `exposure` by what is exposed and to whom: a privileged API or user data is exposure; a dev-only tool's test fixtures readable from another local page is usually `cosmetic` or `recoverable`.
- **Name who hits it:** a real role and workflow ("an editor who imports a file twice", "a developer who fronts the server with nginx").

The script sums the bands into a **distance to harm** and buckets each candidate:

| Bucket | Meaning | What you do |
| --- | --- | --- |
| **test** | Close enough to harm for its class | Reproduce it in step 3 |
| **note** | Past the test line, or only through a contrived condition with exposure or loss | Record it as accepted risk with its holes; test it only if one cheap probe (a few minutes) settles it |
| **skip** | Far past the line, or contrived for a lesser harm | One line in the report so the reader knows it was considered |

You may override a bucket by setting `"bucket"` and `"bucket_reason"` in the ledger, for instance when the change exists to close exactly that hole. Say so in the report. Aim for roughly five to ten candidates in **test**; more means the bands are too generous or the boundary too wide.

Before testing, look at the list once more for what's missing. Most real breaks come from six families, and a run that has none from one of them probably skipped it:

- **Second actor:** tab, user, process, retry.
- **Lifecycle:** restart, deploy, reconnect, cancel mid-flow.
- **State shape:** empty, missing, duplicate, stale, very large, written by an old version.
- **Trust:** input from someone the code assumes is friendly.
- **Every variant:** each kind in a union, enum or spec type, run through every consumer of it, and each alternate path (traced or untraced, cached or fresh, fast path or slow path) run through every check. List the kinds and paths from the code itself, not from the tests; the kind the tests never build (an `xfail`, a `None`, a new enum member) and the path a check forgot to opt into are where consumers break.
- **Consistency:** two outputs built from the same fact by different code (a color and its tooltip, a count and its list, a status line and the log) must agree. Find each pair and feed one input that sits on the boundary between their two derivations.

## 3. Test: reproduce the top candidates

Work the **test** bucket in order, broken-likely first. For each:

1. **Write the hypothesis** in the ledger: "with X and Y, Z happens, visible as W."
2. **Pick the cheapest probe that reaches the real boundary.** A unit-level probe of the changed function is fine for exploring many inputs fast, but a candidate that breaks there must also be shown at its real entry point (a curl, a second browser tab, a killed process, a real job run), because the layers above may close the hole. When you can't reach the real boundary, say so and mark the result `inconclusive`, not `broke`.
3. **Run it and keep the evidence** in the run folder: the script, the command, its raw output, a screenshot, the query and its result. Name files by candidate (`c3-duplicate-import.txt`). Evidence that only exists in your context is gone when the session ends.
4. **Prove the probe can fail.** A probe that never fails proves nothing. For every `held`, record a **control**: run the same probe against a version with the defense removed (a mutant, the base, or for wholly new code the inner function called without the defense in front of it) and show it then reports the failure. This is the step most passes skip, and the reason "it held" is often worthless.
5. **Record the result:** `held`, `broke`, or `inconclusive`, using the receipt fields in [the ledger reference](references/ledger.md). Record the boundary actually reached. If only a source comparison or lower-level probe was possible, describe that observation in an inconclusive result for the user-facing claim.

Keep it bounded. If a candidate needs more than about twenty minutes of setup (a browser harness for client code, a second machine, a cloud deploy), write down what it needs and mark it `untested`, even in the test bucket; the report's "Coverage gaps" section lists it with that need, and the reader can decide it's worth the setup. Clean up anything you started (servers, temp databases, edited config) and say in the report that you did.

## 4. Verify: new, pre-existing, or fixed

For each `broke`:

- **Run the same probe on the base.** Same failure there means `base: same` (pre-existing: name it, don't block the change on it); a pass there means `base: differs` (this change introduced it). This is the line between "fix it in this PR" and "future work".
- **If a fix is proposed or made,** rerun the probe on the fix and show it now holds, with the control still able to fail.
- **Check that a test would catch it,** for every `broke` and for each `held` defense that is the point of the change. Mutate the defense (flip `all` to `any`, drop one condition, return early) in a copy, never in the checkout, and run the touched test files:
  ```bash
  python3 ~/.agents/skills/break-it/scripts/mutate.py --src <checkout-subdir> --run <run> --name duplicate-import \
      --file <path/in/src> --old "<exact text>" --new "<mutant>" -- <test command>
  ```
  For Python, verify the tested module's `__file__` resolves inside the copied mutant. A suite's pytest `pythonpath` setting can put the original checkout ahead of `PYTHONPATH`; disable that setting with `-o pythonpath=` when using the copy, or explicitly select the copy's source root. A passing run against the original is a setup failure, not a surviving mutant.

  `SURVIVED` means the tests still pass with the hole open: a **test gap**, worth naming even when the behavior held. Two traps: a mutant that breaks an import or the harness looks like a kill but isn't (the script reports `NOT A KILL` for pytest's collection errors; read the log for anything else), and a harness that can't see failures at all, so run one mutant you know the suite catches first, as the control.

Use `cheese.py check` while exploring. Keep probe scripts, captured output and control artifacts in the run folder through handoff and cleanup.

## 5. Explain: diagrams

**Required, never optional.** A brief that says to skip, shorten or "only if time allows" the diagrams does not override this; draw them anyway, or stop and say you could not (for example `draftably` won't run), and `cheese.py finish` fails until at least one `.draft` exists. You can't load skills in Codex, so read this file and run `draftably` from `/opt/homebrew/bin` directly.

Draw, following the `draftably` skill and [references/diagrams.md](references/diagrams.md):

1. **The boundary**: actors and entry points, the changed code, outputs and where they're observed, with the fault seams marked. One diagram. Start from [references/boundary-example.draft](references/boundary-example.draft) and merge actors that reach the same entry.
2. **A Swiss-cheese diagram for each of the (at most three) most serious breaks**, plus a `held` candidate whose defense is the point of the change. Other breaks stay as rows in the results table. Generate the skeleton, then write its subtitle by hand:
   ```bash
   python3 ~/.agents/skills/break-it/scripts/cheese.py draft <run>/ledger.json C3 > <run>/diagrams/2-c3-duplicate-import.draft
   ```

Run `draftably check <file> --metrics --fit slide` on each, and when it warns, apply `draftably vary <file> --fit slide`'s recommendation once rather than hand-tuning; give each diagram at most two rounds. The subtitle says what you found in about ten words, never what the picture shows.

## 6. Summarize

Before presenting the final report, run `python3 ~/.agents/skills/break-it/scripts/cheese.py finish <run>/ledger.json` against the retained files. Resolve each error or record the candidate as `inconclusive` or `untested` with the reason in `note`. Include the coverage gaps printed by the command. “Evidence complete” means the receipt fields and files are present. The agent is responsible for interpreting the observations and controls.

Write `report.md` in the run folder from [references/report-template.md](references/report-template.md): a verdict line, the results table (`cheese.py results`), a short card for each serious break, the PR claims that didn't hold, the accepted risks, test gaps, and what wasn't tried and why. Lead with what broke; a reader should know in ten seconds whether anything matters. Don't pad the held list; it's evidence of coverage, not a finding.

Report findings; don't fix the change unless asked. A break-it pass that silently patches what it found leaves the author and reviewer unaware of the hole.

## Things that waste a pass

- **Chasing internals no one reaches.** If the only way to a hole is to hand-edit state or call a private function in an order no caller uses, it's `contrived`. Write it down once and move on.
- **Testing only at the unit level.** The guard can hold in a unit probe and the route can still bypass it; or the unit can "break" while a layer above blocks it.
- **"Held" with no control.** See step 3.
- **Mistaking pre-existing for new.** Always run a `broke` on the base.
- **An attacker with no attack path.** Security candidates still need holes: who can reach the input, from where.
- **Reading ahead.** Commits pushed after the pinned head change the target and give away answers; read them only to check a break you already found.
- **Scope drift into review.** Style, naming and comments belong to the code review, not this pass.

## Inside Byron's review gate

This is step 3 of the review gate in `the owning workspace’s review-gate instructions`. When running it there:

- **Order:** run it after the Shakedown (step 2), so its correctness findings become candidates rather than rediscoveries, and before the one-level-up pass (step 4), which takes every `base: same` break and every test gap as a sibling to look for.
- **Feeds step 5:** the boundary card's outputs list is the start of step 5's surface list (every surface the diff reaches, proven at its destination). Hand it over rather than rebuilding it.
- **Run folder:** `tasks/TASK-NNNN/gate-<pr>/break-it/` in the planning workspace, under the task that owns the gate run. Here, and only here, the diagrams go in that task's `tasks/TASK-NNNN/diagrams/` folder instead of the run folder (numbered, embedded in the gate write-up), so the viewer shows them; follow the workspace's diagram rules (`npm run lint -- <file.draft>`).
- **Write-up:** the gate's README gets a "Break-it pass" section: the verdict line, the results table and links to the cards and the boundary diagram.
- **Models and harness:** inherit the model and harness that invoked the pass. A Codex run uses Codex subagents; a Claude run uses Claude subagents. Keep triage in the invoking session; delegate individual probes with written hypotheses to fresh subagents on that same model. Do not switch providers or launch another model CLI unless the user explicitly asks for it.
- **Nothing leaves:** no PR comments, issues or Slack. Findings go in the write-up; outbound drafts follow the workspace's outbound rules.
