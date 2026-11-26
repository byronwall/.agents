# Climb prompt

Paste the four lines from the skill into the top block. Everything below them is the same for every repo; don't edit it per repo. A later round in the same chat sends only the "Next round" message at the bottom.

````markdown
# Performance climb

```text
Source:  <public repo URL> @ <full SHA>
Goal:    <one sentence in user terms>
Known:   <optional: slow spots, numbers, existing perf docs or scripts>
Fence:   <optional: what must not change, and areas out of scope>
```

You have about 70 minutes to make this measurably faster (or smaller, or lighter, per the goal) without changing what it outputs. You decide what to measure, how to prove nothing broke, where to look, and what to try. I care most about your judgment: the right metric, the right inputs, and the ideas with the biggest real gain. Don't pad the run or claim time you didn't spend. Record start and end times for each phase.

Work entirely inside your own sandbox. Clone, install, build, and run everything there. If the repo is private, a plain clone fails: use your GitHub connector to fetch the tree and blobs at the SHA, rebuild the checkout, and verify the commit hash. Run every server the measurement needs in the same shell session. Do not use Chrome integration, browser connectors, other connected apps, or anything on my machine. If setup fails, solve it yourself and record what you did.

## 1. Set up and choose the metric · about 15 minutes

- Build the repo at the SHA. Read enough of it to understand the hot path for the goal.
- Choose the **metric**: the one number that best matches the goal. Choose its **inputs**: realistic and large enough to matter; you may clone a public repo or generate data, pinned to a SHA or seed. Say whether it is cold (new process, empty caches) or warm, and why.
- Choose a **hold-out input** of the same kind that you will measure only now and at the end.
- Build the **no-change check**: capture the current outputs for a set of inputs and compare later outputs byte for byte (strip only fields that legitimately vary, such as timings, and list them), plus the repo's own tests, typecheck, and lint.
- Write all of this as a small harness inside the repo: one command that prints `{"metric": …, "value": …, "runs": […], "unit": …}`, and one command that prints PASS or FAIL for the no-change check. Commit it as the first patch.
- Run the metric at least 5 times. Report the median, the spread, and the noise band you will use as the keep threshold. Record the machine (CPU count, memory) and runtime versions.

## 2. Find where the cost goes · about 10 minutes

Profile the metric's path (CPU profile, phase timings, allocations, or whatever fits the metric). Rank the top costs with `path:line`. Write ranked hypotheses: each with its evidence and expected gain.

## 3. Climb · about 40 minutes

For each trial:

1. Make one change.
2. Run the no-change check and the repo's gates. If either fails, reject the change and log why.
3. Measure the current best and the change interleaved, in one session. Use enough pairs to tell the gain from noise; reject a trial that stays inconclusive.
4. Keep it only if the no-change check passes and the gain beats the noise band. Commit it locally with the idea and the numbers in the message. It becomes the new best.
5. Log the trial, kept or not.

Prefer removing repeated work, wasted allocation, or a worse algorithm over micro-tuning. Return to the profile after each kept change; the ranking moves. Don't stop after the first win.

Don't game the metric. After the baseline, don't change the harness, the inputs, limits, timeouts, budgets, or test expectations. No caching across processes unless the product really ships that cache. No skipped work that the output needs.

## 4. Confirm · reserve the time from the measured baseline cost, plus packaging

Interleave the harness-only baseline and the final stack on both the main input and the hold-out. Call the stack a win only if the gain beats noise on both; otherwise report it as unconfirmed.

## Deliverables

**The main deliverable is the context dossier, `perf-context.md`.** Write it for an engineer who has not seen this run and will land the patches. Long and dense is the goal; be exhaustive and never shorten it. Sections:
1. Run narrative, with times, including dead ends.
2. Why you chose this metric, these inputs, and this no-change check, and what you rejected.
3. Where the cost goes: profile results, ranked, with `path:line`.
4. How the hot path actually works.
5. Each kept change: what, why it works, numbers.
6. Each rejected idea and why it failed. These are as valuable as the wins.
7. Setup and environment notes.
8. What still dominates the profile, and the next ideas, ranked with expected gains.

If an earlier dossier exists in this chat, update it and add **Changes since the last run**. Append to the dossier after each phase, so nothing is lost if the run is cut short.

Put `perf-context.md` and all the files below in one ZIP, and link the ZIP in your final message:
- `patches/`: `git format-patch` files in order, the harness first, applying cleanly to the source SHA.
- `ledger.json`: one row per trial: `id`, `idea`, `files`, `kept`, `reason`, `best_median`, `change_median`, `noise_band`, `no_change_check` (PASS/FAIL), `gates` (PASS/FAIL).
- `REPLAY.md`: exact commands to rebuild, apply the patches, and re-run the metric, the hold-out, and the no-change check.
- `evidence/`: profile summaries as text, raw run numbers, check output.

Your sandbox files are deleted minutes after you finish, so the chat is the only lasting record. In chat: every kept patch inline as a fenced `diff` block, in order, the harness first; the metric you chose and why in two lines; baseline and final medians on the main input and the hold-out; each kept change in one line; the three most useful rejected ideas; the next three ideas; the ZIP link.

Don't push, open PRs, or change anything outside your sandbox. I will re-measure on my machine and land the patches.
````

## Next round (same chat)

````markdown
Continue the performance climb in this chat. The new baseline is <full SHA>, which contains your harness and patches <ids> (re-measured on my machine: <before> → <after>). Use the same harness, inputs, and hold-out. Start from your ledger's next ideas and the current profile. Same phases, rules, and deliverables; update the dossier.
````
