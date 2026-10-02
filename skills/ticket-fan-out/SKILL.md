---
name: ticket-fan-out
description: Move a software initiative from messy source material through Software Design Sleuth artifacts and a repository-grounded implementation plan, create a small epic and ticket dependency graph, and optionally execute ready tickets in safe parallel waves. Use for the full intent-to-tickets workflow, plan fan-out, dependency-aware scheduling, or ticket-driven implementation. Do not use for one isolated issue.
---

# Ticket Fan-Out

Plan each ticket twice. First create a coarse `open` graph for the full outcome.
Then refine each ticket when it reaches the frontier, just before execution.
Keep the sleuth artifacts as planning truth. A `ready` ticket must stand alone
for its executor; an `open` ticket records the known outcome and route to it.

## Modes

Infer the mode from the request:

- `prepare` — run or resume sleuth, create the coarse `open` graph, and stop. This is the default.
- `tickets` — create or repair the graph from an existing plan.
- `execute` — refine frontier tickets, then implement `ready` tickets.
- `deliver` — prepare the graph, then refine and execute it through the requested scope.

Do not start implementation unless the user asks to execute, implement, start, run, or deliver the work. For `execute` or `deliver`, read [references/execution.md](references/execution.md).

## 1. Resume or run Software Design Sleuth

Use the available `software-design-sleuth` skill. Read and follow its instructions. Do not restate its method here.

- If no initiative artifacts exist, run the safe phases from intent through plan.
- If artifacts exist, resume from their recorded state. Do not restart stable phases.
- Absorb new evidence and regenerate stale downstream artifacts before ticket creation.
- Stop when the sleuth skill requires a consequential human decision. Do not encode an unresolved product choice as ticket work.

The ticket gate is open only when the current implementation plan is repository-grounded and plan-ready. It must identify the first proof, outcome milestones, real dependencies, verification, risks, and the cut line.

## 2. Resolve the ticket destination

Inspect project instructions and existing tracker files before creating anything.

1. Use the repository's established issue system when it is clear.
2. Otherwise, use `tk` when it is installed. It stores Git-backed Markdown tickets in `.tickets/`.
3. If neither exists, stop after the plan and name the missing tracker. Do not install or invent one.

Creating local repository tickets is within scope when the user asks to fan out the work. Creating remote GitHub, Jira, Linear, or other shared issues requires an explicit request for that destination.

Inspect the tracker help before mutation. Preserve dirty work and unrelated tickets.

## 3. Create the coarse graph

Use one epic only when several packets share one outcome. Skip the epic for a small initiative.

Create the fewest tickets that leave clear outcome and ownership boundaries.
Do not reduce ticket count by combining outcomes that need different proof or
ownership. Each coarse ticket must:

- deliver one visible, operator-visible, or decision-changing outcome;
- describe the user-facing or operator-facing change and main steps;
- name likely components or architecture only at a general level;
- record known dependencies, decisions, and a provisional ready gate;
- name the intended proof and what remains below the cut line;
- retain provenance to the sleuth claim, selected shape, plan milestone, and repository baseline.

Write high-level to medium-level scope for the full change. Do not add line
numbers, code samples, exact file edits, or detailed implementation steps to
`open` tickets. Record only high-confidence work. Leave uncertain structure
for the frontier pass. An `open` status means the ticket still needs refinement,
even when its dependencies are closed. Do not mark it `ready` during broad
fan-out merely because the initial plan looks complete.

Use a short coarse body with `Outcome`, `Likely Steps`, `Ready Gate`, and
`Provenance`. The ready gate names what to confirm at the frontier: current
repository shape, required decisions, prerequisites, and runnable proof. Add
known failure or data boundaries when they affect the outcome. Do not fill the
execution-packet template during this first pass.

Before writing tickets, map each decision-changing goal, constraint, system
fact, failure case, proof, and cut-line item from the sleuth artifacts to the
tickets it affects. Each affected ticket must carry its relevant context; the
epic cannot carry required context for a child.

Do not split work into horizontal frontend, backend, database, or test tickets unless that unit provides an independent proof. Do not create tickets for speculative polish or below-cut-line work.

Dependencies represent real prerequisites, not preferred chronology. Prefer one
proof-first root. Add parallel roots only when they are truly independent.

For `tk`, create the epic and `open` tickets first, then add prerequisite edges
with `tk dep <ticket> <prerequisite>`. If the epic tracks completion, make it
depend on its children. Children do not depend on the epic merely because it is
their parent.

## 4. Refine the frontier into execution packets

The frontier contains tickets with status `open` or `ready` whose dependencies
are closed. With `tk`, use `tk frontier` to see it, `tk ready` to see executable
tickets, and `tk blocked` to see unfinished tickets with unresolved dependencies.
Refresh the frontier after each graph change or completion.

Before executing an `open` frontier ticket, inspect the current repository,
plan, dependencies, and proof environment. Re-plan that ticket against what
exists now. Split it when separate outcomes or proof demand separate work.
Create newly found prerequisite tickets as coarse `open` tickets, add real
dependency edges, and refine the new frontier first. Repeat until the graph
has an executable root. Keep blocked tickets `open`; a dependency alone does
not mean the ticket has passed refinement. Do not implement an `open` ticket.

If a new product decision is required, use the sleuth update flow and stop at
its decision gate. If repository evidence changes the plan or graph, update the
canonical initiative state and affected tickets. Preserve the original outcome
when splitting; close a replaced ticket only after its outcome is delivered by
the replacement tickets.

Before changing status to `ready`, confirm no unresolved product decision,
delete-or-preserve boundary, missing prerequisite, or unavailable proof. For
browser or database proof, check the server and data target. Name disposable
test data or a safe read-only path. Otherwise, defer that proof to another
ticket. Only then write the execution packet and run `tk status <id> ready`.

Use the tracker's native fields for title, type, priority, parent, dependencies,
tags, and external reference. The following detail applies when refining a
frontier ticket to `ready`. Write a prioritized execution contract, not a
miniature copy of the plan. Aim for 300–650 words when that range can retain all
decision-changing facts. For a body over 700 words, split independent proofs or
state why one executor needs the extra context.

Use this compact body by default:

```markdown
## Outcome and Why

## Ready Gate

## Owned Context and Scope

## Decisions and Discretion

Must:

Executor may choose:

Do not:

## Behavior and Failure Proof

## Acceptance Checklist

## Cut Line and Provenance
```

Keep each section short and weighted toward facts that change implementation or
proof. The ready gate must state that required decisions, dependencies, and
proof resources are settled. If not, block the ticket and name the decision.

Add a conditional section only when its content changes executor decisions:

- `Data and Trust Boundary` for private data, browser/server exposure, logs,
  secrets, recovery payloads, or external providers.
- `Migration and Recovery` for schema changes, destructive work, preserved
  data, rollout, or rollback.
- `Coordination Boundary` for shared schemas, generated files, one mutable
  database, concurrent work, or exact file ownership.
- `Destructive Disposition` for cleanup. Classify each important code group as
  delete, preserve, or inspect before change.
- `Open Decision` only for a blocked ticket. Never expose it as ready.

In `Behavior and Failure Proof`, include only relevant cases. Distinguish a
failed operation from a successful operation followed by a failed refresh,
render, notification, or readback. State whether retry is safe. Include one
representative compatibility shape when compatibility can change control flow.

In `Acceptance Checklist`, label exact evidence as one of:

- `Invariant` — must hold for every valid input.
- `Fixture` — exact controlled data owned by the test.
- `Observed baseline` — reproduction evidence that can change.

Do not use live production counts as invariants. Include the smallest automated
proof, the required user-visible or operator-visible proof, and the project
verification command. A long proof list usually means the packet needs a split
or a shorter release-gate summary.

Transfer all decision-changing knowledge from the plan and its upstream sleuth
artifacts. Repeat cross-cutting context only where omission could change the
executor's choices. Include rationale when it prevents an attractive wrong
implementation.

Do not use phrases such as "see the plan," "follow the epic," or "refer to the source document" as a replacement for content. Links in `Provenance` are for traceability and later review only. The executor must understand the intent and complete the work without opening them.

Do not invent requirements, architecture, file names, APIs, estimates,
implementation steps, edge cases, or acceptance criteria during transfer.
Include implementation detail only when the plan, repository evidence, project
instructions, or user already established it. Put genuine freedom under
`Executor may choose`. Put unresolved decisions in `Open Decision`, keep the
ticket blocked, and do not resolve them by assumption.

Use acceptance criteria for observable completion conditions already supported
by the source material. Preserve uncertainty labels, alternatives, and cut-line
decisions. If the plan lacks detail required for a safe ticket, return to the
sleuth update flow instead of filling the gap. Do not compensate with a longer
ticket.

## 5. Reconcile and verify

After IDs exist, record them in the canonical initiative state and add short links from the implementation plan when its format supports them. Do not duplicate ticket bodies in the plan.

Verify the observable graph with the tracker:

- every inventoried source item is present in each ticket it affects at the
  detail appropriate for its status;
- no ticket depends on a linked plan or epic for essential context;
- coarse `open` tickets contain no premature code or line-level detail;
- every `ready` ticket has current repository evidence and stands alone;
- every implementation detail is source-backed or clearly left to executor discretion;
- every ready ticket passes its ready gate and contains no open decision;
- exact acceptance values are fixtures or labeled observations, not volatile invariants;
- relevant partial-success, compatibility, data-exposure, and destructive boundaries are explicit;
- no dependency cycles;
- every ticket belongs to the intended initiative;
- blocked tickets have a real prerequisite;
- frontier output exposes the intended first proof and any valid parallel roots;
- the epic completion graph includes all intended packets;
- sleuth artifact validation and repository formatting checks still pass.

Do not publish remote issues, push, or deploy unless the user also requests it. Follow active project and orchestration rules for workers and commits.

## Report

For `prepare` or `tickets`, return links to the implementation plan, epic when
present, and first frontier ticket. State the ticket count, frontier roots,
validation result, and any unresolved human decision.

For `execute` or `deliver`, report completed tickets, remaining `open`, `ready`,
and blocked tickets, verification evidence, and the next frontier wave.
