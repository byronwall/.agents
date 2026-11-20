# The ledger and the Swiss-cheese rule

The ledger (`ledger.json` in the run folder) is the one record of every candidate: its holes, its harm, its bucket, and once tested, its result and evidence. `scripts/cheese.py` reads it to bucket candidates, build the results table and draw each candidate's diagram, so the report, the diagrams and the triage never disagree.

An illustrative example in the work-in-progress format is in [example-ledger.json](example-ledger.json).

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | `C1`, `C2` … stable for the run |
| `title` | yes | The story in one line: who does what, and what goes wrong |
| `who` | yes in practice | The real person and workflow that would hit it |
| `trigger` | no | What starts it, for the diagram's first box (defaults to `who`) |
| `holes` | yes | Ordered list of `{layer, condition, freq, why?}`; `why` is expected for `rare` and `contrived`. A layer outside the change (a proxy, a browser rule) is named as such: `"layer": "Browser CORS (outside this change)"` |
| `harm` | yes | One of the harm ladder below |
| `observe` | yes in practice | Where and how the failure would be seen |
| `hypothesis` | when tested | "With X and Y, Z happens, visible as W" |
| `status` | no | `untested` (default), `held`, `broke`, `inconclusive`, `skipped` |
| `blocked_at` | for held | 1-based index of the hole that stayed shut, for the diagram |
| `base` | for broke | `same` (pre-existing), `differs` (new in this change), `n/a` (the code is new, so there is nothing on base to run) |
| `evidence` | for held, broke | Paths in the run folder (or `path:line` in the repo) |
| `control` | for held | How you showed the probe can fail |
| `bucket`, `bucket_reason` | no | Manual override; say why |
| `subtitle` | for diagrams | What you found, about ten words |
| `note` | no | Anything else the reader needs |

## Final receipts

Run `cheese.py finish ledger.json` before reporting. The fields above also serve historical ledgers and work in progress (`cheese.py check`). At finish, every candidate needs an explicit status. Use `untested` for a deliberate skip and `inconclusive` for an attempt that could not settle the claim. Put the reason in `note`, for example “Settings Apply would write shared configuration.” Both appear under coverage gaps.

For `held` and `broke`, add these fields directly to the candidate. Give reproduction instructions for the tested commit, including working directory, setup, command or manual actions, and how to repeat the control if used. Keep each evidence path relative to the ledger and retain every named file. A probe, log or capture is sufficient for a nonvisual check.

```json
{
  "revision": "abc1234",
  "reproduce": "From the checkout root run python /path/to/run/probe.py. Repeat with --drop-draft to simulate remount losing the draft.",
  "expected": "The edited field still reads West after the poll.",
  "observed": "The Settings field read West after the poll.",
  "evidence": ["probe.py", "head.log"],
  "control": {
    "outcome": "failure-observed",
    "observed": "With --drop-draft the same field reverted to East after the poll.",
    "evidence": ["control.log"]
  }
}
```

Only `held` needs the control object. Record `failure-observed` only when the same probe reached its observation point and detected the target failure. An import error or failed setup leaves the result inconclusive. For a break, describe the bad behavior at the real entry point and keep the existing `base` comparison. A probe can print the bad value and exit zero. The validator checks receipt structure and file availability. The agent interprets their contents.

## Frequency ladder (per hole)

Judge each hole *given the holes before it*. The question is "when the earlier holes are open, how often is this one open too, for the person who'd hit it?"

| Band | Score | Means | Example |
| --- | ---: | --- | --- |
| `always` | 0 | True in every run of the feature; not a defense | each import reads the file |
| `routine` | 1 | Most users hit it in a normal week | a file with a header row |
| `occasional` | 2 | Some users, or every deploy, restart or second tab | an import retried after a restart |
| `rare` | 3 | An unusual but legitimate setup or timing | two imports finishing in one clock tick |
| `contrived` | 5 | Hand-edited state, an attacker the threat model excludes, or several rare things at once | a checkpoint edited by hand |

## Harm ladder

| Harm | Means | Test within distance |
| --- | --- | ---: |
| `cosmetic` | Wrong text, log noise; nobody acts on it wrongly | 1 |
| `recoverable` | Visible failure; a retry or reload fixes it | 2 |
| `stuck` | Visible failure the user can't get past without help | 3 |
| `wrong` | Silently wrong result, grade, number or saved state | 5 |
| `exposure` | Sensitive data or a privileged surface reachable by someone who shouldn't reach it (judge by what is exposed: dev-tool fixtures are not user data) | 6 |
| `loss` | User data destroyed, or a write silently dropped | 6 |

## The rule

- **Distance to harm** is the sum of the hole scores. Lower means closer to happening.
- **Slices** is the number of holes that aren't `always`: the real defenses.
- A candidate with any `contrived` hole is **skip**, unless its harm is `exposure` or `loss`, then **note**.
- Otherwise it is **test** when its distance is within the harm's line, **note** within three more, and **skip** beyond that.

The thresholds are deliberately coarse. They exist so two agents put the same candidate in the same bucket once they agree on the bands; the judgment lives in the bands and their reasons. If the rule gives an answer you think is wrong, override it with `bucket` and say why, and consider whether a band is off first.
