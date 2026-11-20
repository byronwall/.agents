# Design note: break-it

The skill gives reviewers a repeatable way to select, test, and report the failures that matter.

The ask, in Byron's words: find the system boundary, its inputs and outputs, the internals' implicit assumptions and the places to inject a fault; then decide what is "actually a legitimate problem" versus "way deep in the internals, I'll accept that risk", using the Swiss-cheese model; then test, explain, verify and summarize.

Three decisions shaped the skill. Each was run through `consider-contrast`; the tables are below.

## 1. How to triage a candidate breakage

Decision: what rule turns a candidate into "test it", "note it as accepted risk" or "skip it".

Options:

- **A. Swiss-cheese layer count.** Count the independent conditions that must line up. Fewer holes, more worth testing.
- **B. Likelihood times impact.** Score each 1 to 5 and multiply, the classic risk matrix.
- **C. Hybrid: a hole ladder plus a harm ladder.** List the holes; give each a frequency band from a fixed ladder (always, routine, occasional, rare, contrived), judged given the holes before it; sum the bands into a "distance to harm"; compare that to a threshold that depends on the harm class (cosmetic, recoverable, stuck, wrong, exposure or loss). A contrived hole skips the candidate unless the harm is exposure or loss.

Dimensions, each from the request:

- **Niche separation:** does it push "way deep in the internals" cases out and keep realistic ones in? (Byron's main ask.)
- **Diagram fit:** can the score be drawn as lined-up holes, so the explanation and the triage are the same picture?
- **Same bucket from two agents:** would two runs on the same PR bucket a candidate the same way? The gate runs a fresh session per PR, so drift between sessions is the failure.
- **Who hits it:** does it force naming the person and the workflow, which is how Byron judges whether a break matters?
- **False precision:** 10 means the numbers can't pretend to more accuracy than the evidence has.

| Approach | Niche separation | Diagram fit | Same bucket from two agents | Who hits it | False precision | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A. Layer count | 5 | 9 | 7 | 3 | 8 | Treats one rare hole like one routine hole; a single-hole silent data loss and a single-hole typo score alike |
| B. Likelihood × impact | 6 | 3 | 4 | 5 | 3 | Agents pick 3 vs 4 freely, the product hides which condition made it likely, and nothing draws as cheese |
| C. Hole ladder + harm ladder | 9 | 9 | 8 | 8 | 7 | Needs a written ladder and a script to apply it; band choices are still judgment |

- **Choice:** C. The holes are the Swiss-cheese slices, so the triage table and the per-break diagram come from the same data. Bands are coarse words, not numbers, which keeps agents from inventing precision; the script applies the thresholds, so the bucket is repeatable once the bands are chosen.
- **Why:** niche separation and diagram fit decide it. A could not tell "rare" from "routine"; B could not be drawn.
- **Watch:** band inflation (calling everything "rare" to skip work). The skill asks for the person who hits each hole and a one-line reason for every "rare" or "contrived", and allows a cheap probe for a Note candidate when one command settles it.
- **Calibration:** the worked example scores a repeated import in `references/example-ledger.json`.

## 2. How to find the boundary

Decision: where the inspection starts and how far it walks.

Options:

- **A. Diff-driven.** Inputs and outputs are the changed functions' parameters and return values.
- **B. Architecture-driven.** Start from the system's real entry points (HTTP routes, sockets, CLI, scheduled jobs, deploy config) and map everything.
- **C. Diff-anchored, walk out to the real boundary.** Start at the changed code; walk callers out until you reach a real entry point (something a user, another process, a deploy or a clock drives) and walk outputs out until they land somewhere observable (UI text, a stored row, a log line, a span, a response). Stop at the first real boundary on each side.

Dimensions:

- **Stays in the change's blast radius:** probes spent on code the change can't affect are waste. Byron: don't "get lost in the minutiae".
- **Finds assumptions owned outside the diff:** a client retry policy can expose an importer that assumes one delivery per file.
- **Gives real observation points:** step 5 of the gate proves each surface at its destination; a boundary drawn at function level gives none.

| Approach | Stays in blast radius | Finds assumptions outside the diff | Gives real observation points | Main tradeoff |
| --- | ---: | ---: | ---: | --- |
| A. Diff-driven | 9 | 3 | 3 | Probes become unit tests of the changed function; deploy, config and second-actor cases never come up |
| B. Architecture-driven | 3 | 8 | 9 | Becomes an audit of the whole system on every PR |
| C. Diff-anchored walk-out | 8 | 8 | 8 | Needs a rule for when to stop walking |

- **Choice:** C, stopping at the first real boundary on each side, plus one hop for the config or deploy that selects the code path.
- **Why:** it is the only option that both stays on the change and reaches the deploy and second-actor assumptions that produced the real findings.
- **Watch:** walking too far. The inspection caps at what fits the boundary diagram, about a dozen boxes.

## 3. Report shape

Decision: how the run is summarized for Byron and for the gate's write-up.

Options include a narrative per probe, a single table, or a verdict followed by a table and short finding cards.

Dimensions: **find the break in ten seconds** (Byron reads diagrams and tables first), **evidence one click away** (the gate's step 5 rule), **accepted risk visible** (he wants to say "I'll accept that risk" knowingly, not by omission).

| Approach | Find the break in ten seconds | Evidence one click away | Accepted risk visible | Main tradeoff |
| --- | ---: | ---: | ---: | --- |
| A. Narrative per probe | 4 | 7 | 5 | Breaks hide among the probes that held |
| B. Table only | 8 | 8 | 6 | No room to explain why a break matters or how to fix it |
| C. Verdict, table, cards | 9 | 9 | 9 | Longer; cards only for broken and noted candidates keep it bounded |

- **Choice:** C, in `references/report-template.md`. The table comes from `scripts/cheese.py results` so it matches the ledger.

## Receipt tests

The receipt tests are documented in `evals/README.md`.
