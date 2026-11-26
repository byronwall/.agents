# Retro: the Srcly UX Evaluation chat

Chat: https://chatgpt.com/c/6b030b45-ebc8-83ea-b9e1-bea5a2006e6d (2026-11-22 to 2026-11-23). Results: `~/Projects/planning/tasks/TASK-0065/pro-retest-2026-11-23/`.

## The three runs

| Run | Prompt shape | Pro worked | What came back |
|---|---|---|---|
| 1. Study | ~3,500 words. 20 named scenarios, a 12-part method, 0–4 scores on 7 dimensions, 8 deliverable files, a "10× more useful" section | 75 min | 20 scenario records, 18 issues (1 P0, 4 P1), 3-horizon roadmap, eval suite, 55 screenshots, 16 MB ZIP |
| 2. Retest | ~450 words. Pinned SHA, a 5-case smoke pass, two deep workflows with exact steps, a compact table, "single next change" | 29 min | 11-row old → new table, one blocked case (HTTP 500), one next change with an acceptance test |
| 3. Probe | ~1,300 words. A decision question, four timed phases (8 + 20 + 22 + 15 min), adversarial controls, falsification fixtures, a transfer test, fix now / shape next / defer | 77 min (63 min of browser work, self-reported to the millisecond) | Verdict, 3 findings, 21 cases, one PR spec, a replay sheet, a 2 MB ZIP. W17–W20 in TASK-0065 came straight from it |

## Where Pro did its best work

- **It found a lie.** Run 1 found an alias-mutation labeled "Closed" and proved it by running the fixture's code (a runtime oracle). Run 3 found a declaration-only callee labeled "Closed" and replayed it on the before-build to show it was old, not a regression. Both came from prompts that defined "seriously misleading analysis" as P0 and asked Pro to try to make the product lie.
- **It kept categories apart.** "Implemented but broken" versus "partially implemented" versus "not implemented" versus "environment failure"; "newly observed" versus "introduced"; "what the UI proved" versus "what I learned reading code". The prompts asked for each split by name.
- **It built its own controls.** Same output with a different cause; same file name in a second root; a reverted JSON edit to separate Touched from Net; a dirty worktree with a value that conflicts with the committed text; a delayed response to force a race. Run 3 asked for these by pattern, and Pro built more than were named.
- **It verified against oracles.** Git path sets, exact revision and line, API response bodies, runtime execution. Every important row has an exact witness.
- **It ended in one buildable decision.** Run 3's next PR had file and line scope, five acceptance criteria, and "the smallest test that could falsify it". It became a worker prompt with no rewrite.
- **It was honest about limits.** No speedup claims, timings labeled as walkthroughs, before-build replays only where history was ambiguous, unrun controls listed as unrun.
- **It shipped a replay.** `REPLAY.md` recreates the build, the fixtures with hashes, and the Git oracles from a fresh directory.

## Which prompt moves caused that

| Move | Run | Effect |
|---|---|---|
| A decision question with options ("narrow field-producer, Compare state, a correctness fix you discover, or something else?") | 3 | The run ended in one PR instead of a roadmap |
| Minutes per phase, "don't stop when happy paths pass", "don't pad or claim time you didn't spend" | 3 | 63 min of real browser work, measured; run 2 had no minutes and stopped at 29 |
| "Try to make the combined build give a convincing wrong answer" with three named kinds | 3 | Found the A04 false-Closed defect |
| Falsification fixtures described by pattern, not by expected result | 3 | Pro built the controls and the ground truth itself |
| "Attempt the workflows before reading PR descriptions or expected outcomes" | 2, 3 | Results describe what a user meets, not what the PR claims |
| "No source-only substitutes for UI results"; "separate what the UI showed from what you learned reading code" | 1, 2, 3 | Clean UI-versus-source evidence in every row |
| Pinned SHA, run API/engine/client from source, "record the SHA you actually tested", "not the published package" | 2, 3 | No confusion about what was tested |
| Same chat for retests; "reuse the original fixtures, revision pairs, saved results" | 2, 3 | Exact old → new comparison per case ID |
| "Distinguish implemented / difficult / broken / partial / not implemented / unsupported" | 1 | Missing features were not reported as UI bugs |
| P0 defined as "seriously misleading analysis" | 1 | Correctness defects ranked above layout noise |
| "A missing metric is not a zero metric"; "a precise 'I can't prove past here' can be acceptable" | 3 | Pro judged honest stopping points as good, not as failures |

## What cost time or added little

- **The Chrome detour.** Run 3: Pro first tried the connected Chrome, hit an "originating-browser-context" error, and fell back to its own cloud browser, where it did the whole run. Early helper requests also returned 403. Pro solved both itself. Fix: forbid Chrome and connectors outright, tell Pro to solve setup inside its sandbox, and give it a cold-start-verified run sheet.
- **Run 1's breadth.** Twenty scenarios × seven 0–4 scores × eight files made a 16 MB package. The scores and most of the 20 scenario records were not used after the run; the issue ledger, the P0, and the eval suite were.
- **Run 2's missing time budget.** It was precise but small, and Pro stopped at 29 minutes with one deep check blocked.
- **The large-repo transfer.** It hit a 30-second engine timeout in both builds. Worth running, but name an alternate question in case the first one is blocked.
- **Context left in the chat.** Pro's reports were dense, but much of what it learned (how the engine really works, every detour, why each fix was needed) stayed in its head and the chat. Run 3's REPLAY and next-PR files show how much it can write when asked. Fix: ask for a long, cumulative context dossier as the main deliverable.
- **The handoff back.** Claude had to turn Pro's case IDs into planning work items by hand. The skill now does that in step 6.

## Rules this retro gives the skill

1. Lead with the decision. 2. Give minutes per phase that sum to 60–75. 3. Ask for a convincing wrong answer by named kind. 4. Describe controls by pattern; let Pro build them. 5. UI first, then source, and keep the two apart. 6. Pin the SHA and rehearse the cold start. 7. Retest in the same chat by case ID. 8. End in one PR with a falsifying test. 9. Cut scoring grids and generic checklists. 10. Keep Pro in its sandbox: no Chrome, no connectors. 11. Make the long context dossier the main deliverable, and never ask Pro to be brief.
