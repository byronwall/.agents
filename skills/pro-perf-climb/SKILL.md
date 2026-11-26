---
name: pro-perf-climb
description: Point ChatGPT Pro at any repo with a one-line performance goal ("make srcly's cold trace way faster") and let it hill-climb for 60–75 minutes in its own sandbox. Pro decides what to measure, builds its own benchmark and no-change check, profiles, picks the approaches, keeps only measured wins that leave output unchanged, and returns a patch series (harness first), a ledger of every trial including failures, and a long context dossier. Claude then re-measures on the Mac and opens the PRs. Works for speed, memory, bundle size, or any number. Use when Byron says `/pro-perf-climb`, "make X faster with Pro", "have Pro hill-climb <metric>", or "Pro perf run". For usability runs use `pro-usability-loop`; for design questions use `prepare-chatgpt-pro-repo-prompt`.
---

# Pro perf climb

Pro is better than Claude at the judgment in a performance push: which number matters, which input is representative, where the time really goes, which idea to try first, and when a direction is dead. So Claude does not design the benchmark. Claude gives Pro the repo and the goal, and Pro owns the method. Claude's job is the guardrails before the run and the re-measure after it.

This skill reuses [`pro-usability-loop`](../pro-usability-loop/SKILL.md) for the **sandbox-only** rule, how far to go (draft / send / run), and step 4 (send, wait, collect).

## What Claude fills in

Four lines. Nothing repo-specific beyond these.

```text
Source:  repo URL @ full SHA (pushed; a private repo comes through Pro's GitHub connector)
Goal:    one sentence in user terms: "make the first trace on a large repo much faster"
Known:   optional: slow spots or numbers Byron already has, prior perf docs, existing timing scripts (paths only)
Fence:   optional: what must not change beyond output (public API, limits, file formats) and areas out of scope
```

Get `Known` from the repo in two minutes (`rg -il "perf|bench|timing|profile"`, docs/research), not from a study. Don't rehearse the setup or write a harness; Pro does both. Then paste the lines into [references/prompt-climb.md](references/prompt-climb.md) and send.

## What Pro decides (and the prompt says so)

1. **What to measure.** It picks the metric that best matches the goal, the inputs (it may clone a public corpus repo and pin its SHA), and cold versus warm, and explains why.
2. **How to prove nothing broke.** It captures baseline outputs for a set of inputs it chooses and builds a byte-level or exact-count check, plus the repo's own tests.
3. **The noise band.** It measures its own run-to-run spread and sets the keep threshold from it.
4. **Where to look and what to try.** It profiles, ranks the costs, and chooses the order of ideas, changing course when the profile says so.

Its harness is the first patch in the series, so the repo keeps the benchmark after the run.

## Rules the prompt keeps fixed

These protect the result and are the same for every repo:

- One change per trial. Gates and the no-change check before any timing. A and B measured interleaved in one session.
- Keep a change only if output is unchanged and the gain beats the noise band.
- A hold-out input, measured only at the start and end, must also improve, or the stack is reported as unconfirmed.
- No gaming: no changes to limits, timeouts, budgets, test expectations, or the harness after the baseline; no caches across processes unless the product ships them; no skipped work the output needs.
- Every trial goes in the ledger, kept or not, with its reason.

## After the run

1. Collect per `pro-usability-loop` step 4 into `tasks/<TASK>/pro-climb-<date>/`, the moment Pro finishes: file links expire within minutes (the files outlive them; a re-link message recovers them). The patches are also inline in the final chat message.
2. At the tested SHA, apply the harness patch and measure that baseline on the Mac. Then apply each kept patch on top of the last patch that held up on the Mac: rebuild, run the no-change check and the gates, and compare with that parent. Drop a patch that fails or does not reproduce (note why in the ledger) before testing the next. Confirm the final stack on both inputs. The Mac numbers are the truth; Pro's only rank the ideas.
3. Open a `gh stack`: the harness first, then one layer per patch that held up, with Mac before and after numbers in each body.
4. Copy the dossier to the product's `<product>-context.md` and log the round in the planning task.
5. Next round in the **same chat**: the new baseline SHA and "continue from your ledger's next ideas". Stop when a round keeps less than the noise band.
