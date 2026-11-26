---
name: codex-review
description: "Have Codex review a commit from Claude, and fix and re-review until it passes (no in-scope P0/P1), for at most 3 rounds. Use when Byron says to have Codex review, check or tighten work (\"have Codex review this\", \"the gnarly parts\", \"open the PR once the review is clean\"), and by default before opening a PR that changes core logic: analysis, algorithms, merging or projecting data, concurrency, caching, or two code paths that must agree."
---

# Codex review loop

Codex (`gpt-6.2-sol`, high effort, read-only) finds what Claude's own tests miss: it probes inputs beyond the fixtures. Run it on each layer of core-logic work. Open the PR when a round passes, or after round 3 unless an in-scope P0 is left; then stop for Byron's review.

The script owns the model. It passes `-m gpt-6.2-sol`, so a model picked in the Codex app does not change reviews. To change the review model, edit `MODEL` in the script.

## Run one review

1. Commit the work. Pin the review to the commit's SHA, never `HEAD`: `HEAD` moves while you fix.
2. Write a focus file in the repo's `tmp/` (for example `tmp/codex-focus-<slug>.md`). The slug becomes the Codex thread title. Include:
   - the goal, in product terms, and the invariant that must hold;
   - what the commit changes, in a few lines;
   - the places you are least sure of, as questions;
   - the check you ran and its scope ("243 fixture anchors"), so Codex can test beyond it.
   Do not argue that the code is right. Codex anchors on your conclusion.
3. Run it in the background (it takes 5 to 15 minutes):

   ```bash
   python3 ~/.agents/skills/codex-review/scripts/codex_review.py --repo "$PWD" --rev <sha> --round 1 --focus tmp/codex-focus-<slug>.md --out tmp/codex-review-<slug>.log > tmp/codex-verdict-<slug>-r1.md
   ```

   Exit 0 is PASS (no in-scope P0 or P1), 3 is FAIL, 2 is "Codex could not run" (the reason is on stderr). The verdict file starts with one summary line, then a table: severity, `diff` or `base` (pre-existing), whether Codex reproduced it, file:line and the finding. Details follow the table.
4. Several independent layers (engine and client) get separate reviews, in parallel.

Severity: P0 is data loss, a security hole or a crash in normal use. P1 is a wrong result on inputs real use will hit. P2 is unusual but plausible inputs. P3 is contrived inputs or polish.

## Act on the findings

- Fix every in-scope P0 and P1. Reproduce or reason through each one first.
- P2 and P3: fix the ones that are cheap. List the rest in the PR body with a one-line reason. They do not need another round.
- `base` findings were already on the main branch. Do not fix them in this PR. Tell Byron about a serious one.
- When several findings share one cause, fix the cause. Codex found five drifting copies of the same stop rules before the real fix (one source of truth) closed them all.
- Only when a round fails: commit, then re-run with `--round <N+1> --follow-up <previous verdict file>` on the new SHA.
- Stop after round 3. The script refuses round 4. Round 3 also returns an architecture note: a design change that would prevent the kind of findings the rounds kept finding. Put it in the PR body, and tell Byron about it if it is worth a follow-up.
- **Round 3 with an in-scope P0 (exit 4): stop.** A P0 after 3 rounds means the fixes keep missing or the design is wrong. Do not open the PR or the next layer, and do not try another fix. Push the branch, then send Byron the verdict, the architecture note, and one line per P0 on what each round tried. Wait for his call.
- **Round 3 with only P1s (exit 3):** open the PR. List each open P1 in the PR body, and add it as an open work step in the planning task, so it is not lost after merge.
- In the PR body, say which rounds ran and what they changed. List open and declined findings with their severity and a reason.

## Feed findings back into guidance

The goal is fewer findings next time, not only a clean PR. The script appends every finding to `~/.agents/review-findings.jsonl`, keyed by the origin repo (`owner/name`). Each finding has a `class` (such as `divergent-paths` or `missing-limit`) and a `prevent`: `check`, `test`, `standard`, `architecture` or `none`.

- **Before you write core-logic code**, run `codex_review.py --repo "$PWD" --hazards`. It prints this repo's most common finding classes and what prevents them. Put the result in a worker's brief and in the focus file. The script also gives it to Codex.
- **When the loop ends** (PASS or round 3), run `codex_review.py --repo "$PWD" --close <slug>` and act on each group:
  - `check` and `test`: add them in this PR. A check that would have caught the finding beats any prose rule. The script also lists here a `standard` whose written rule already existed and did not stop the finding.
  - `standard`: add one line to the repo's `CODING_STANDARDS.md`, and create the file if it is missing. The script lists a standard only when its class has come up in two or more reviews in this repo, so one-off rules stay out.
  - `architecture`: propose a follow-up session with the design change.
  - "No action yet": nothing to do. A second occurrence promotes it.
- Say in the PR body what the close step added.

## When Codex cannot run

- `model_not_found` or "Model metadata … not found": the CLI is too old for the pinned model. Run `brew upgrade --cask codex`. Do not change `MODEL` to get around it.
- Never call `codex exec` without stdin closed (`< /dev/null`, or the script). It prints "Reading additional input from stdin..." and waits forever.
