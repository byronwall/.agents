# Report template

Write `report.md` in the run folder in this shape. Lead with what broke. Keep held results to the table: they show coverage, not findings.

```markdown
# Break-it: <change, with a few words on what it is> at <short sha>

**Verdict:** <one sentence: what broke at the tested boundary, or which tested behaviors held and where coverage stopped>. <n> candidates: <n> broke (<n> new, <n> pre-existing), <n> held, <n> inconclusive, <n> untested; by triage, <n> test, <n> accepted risk (<n> of them probed anyway), <n> skipped.

- **Target:** `<base>...<head>`, run against <dev server / test harness / unit probe>, <date>
- **Boundary:** [1-boundary.draft](diagrams/1-boundary.draft) — <one line: the entry points and where failures show>
- **Ledger:** [ledger.json](ledger.json)

![Where <thing> meets the outside](diagrams/1-boundary.draft)

## Results

<paste `cheese.py results ledger.json`>

## What broke

### C<n> · <title>

![C<n> <short name>](diagrams/2-c<n>-<name>.draft)

- **Holes that line up:** <condition (band)>, <condition (band)> … — <who hits it>
- **What happens:** <the harm, as the user sees it, at its destination>
- **New or pre-existing:** <base: same → pre-existing on base, name it as future work | base: differs → this change introduced it>
- **Evidence:** [<file>](<file>) — <the one line that shows it>
- **Fix:** <the smallest change that shuts one slice, and which slice>; <verified: probe now holds, control still fails | not attempted>

## Claims that don't hold

Each claim from the PR description, docs or comments that a probe contradicted, with the probe and its output. Listed whatever the harm, because the reviewer will take the claim at face value.

## Accepted risk

One line each for **note** candidates: the holes, who'd hit it, and why it's acceptable now ("requires simultaneous imports of the same file; observed on base"). A note candidate that a cheap probe broke stays here, with its result, unless the probe moved a band (then re-triage it).

## Test gaps

Behavior that held but that the suite would not catch if it regressed: the mutation that still passes the tests, and the known-caught mutant that showed the harness can fail.

## Coverage gaps

Include each gap from `cheese.py finish ledger.json` with its reason and any lower-level observation. Use `untested` for candidates skipped at triage.
```

## Notes on the shape

- The verdict counts must match the ledger. Generate the table; don't hand-type it.
- "Pre-existing" never blocks the change on its own, but it is still a finding: it goes to the one-level-up pass or future work.
- Links are relative to the report so the folder can move.
