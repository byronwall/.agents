---
name: ticket-fan-out
description: Move a software initiative from messy source material through Software Design Sleuth artifacts and a repository-grounded implementation plan, create a small epic and ticket dependency graph, and optionally execute ready tickets in safe parallel waves. Use for the full intent-to-tickets workflow, plan fan-out, dependency-aware scheduling, or ticket-driven implementation. Do not use for one isolated issue.
---

# Ticket Fan-Out

Create a complete handoff from product intent to executable work. Keep the
sleuth artifacts as planning truth while tickets are created. After creation,
each ticket must stand alone for its executor. Repeat decision-changing context,
but do not copy background that does not affect execution or proof.

## Modes

Infer the mode from the request:

- `prepare` — run or resume sleuth, create the ticket graph, and stop. This is the default.
- `tickets` — create or repair the graph from an existing plan.
- `execute` — load an existing graph and implement ready tickets.
- `deliver` — prepare the graph, then execute it through the requested epic or scope.

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

## 3. Design the graph before creation

Use one epic only when several packets share one outcome. Skip the epic for a small initiative.

Create the fewest packets that leave clear ownership boundaries. Do not reduce ticket count by combining outcomes that need different proof or ownership. Each packet must:

- deliver one visible, operator-visible, or decision-changing outcome;
- fit one focused implementation pass;
- name the concrete repository context it owns;
- include settled decisions and a clear invention boundary;
- include the smallest proof that can fail if the work is wrong;
- state what remains below the cut line;
- retain provenance to the sleuth claim, selected shape, plan milestone, and repository baseline.

Before a packet can be ready, confirm that it has no unresolved product
decision, delete-or-preserve boundary, missing prerequisite, or proof that
cannot run in the current environment. Keep a packet blocked when any of these
remain. Do not use an `Open Decision` section in a ready ticket.

Before writing tickets, inventory every known goal, user need, requirement, decision, constraint, non-goal, current-system fact, dependency, risk, failure case, proof, rollout rule, and below-cut-line item in the current sleuth artifacts. Map every item to the tickets it affects. Copy cross-cutting items into every affected ticket.

Every source item must appear in at least one ticket. Any item that can change an executor's decisions must appear in that executor's ticket. The epic is not a substitute because an executor may receive only one child ticket.

Do not split work into horizontal frontend, backend, database, or test tickets unless that unit provides an independent proof. Do not create tickets for speculative polish or below-cut-line work.

Dependencies represent real prerequisites, not preferred chronology. Prefer one ready proof-first packet. Add parallel roots only when they are truly independent. Do not link every ticket to every other ticket.

## 4. Write execution packets

Use the tracker's native fields for title, type, priority, parent, dependencies,
tags, and external reference. Write a prioritized execution contract, not a
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

For `tk`, create the epic and packets first, then add prerequisite edges with `tk dep <ticket> <prerequisite>`. If the epic tracks completion, make it depend on its child packets. Do not make children depend on the epic merely because it is their parent.

## 5. Reconcile and verify

After IDs exist, record them in the canonical initiative state and add short links from the implementation plan when its format supports them. Do not duplicate ticket bodies in the plan.

Verify the observable graph with the tracker:

- every inventoried source item is present in each ticket it affects;
- no ticket depends on a linked plan or epic for essential context;
- every implementation detail is source-backed or clearly left to executor discretion;
- every ready ticket passes its ready gate and contains no open decision;
- exact acceptance values are fixtures or labeled observations, not volatile invariants;
- relevant partial-success, compatibility, data-exposure, and destructive boundaries are explicit;
- no dependency cycles;
- every ticket belongs to the intended initiative;
- blocked tickets have a real prerequisite;
- ready output exposes the intended first proof and any valid parallel roots;
- the epic completion graph includes all intended packets;
- sleuth artifact validation and repository formatting checks still pass.

Do not publish remote issues, push, or deploy unless the user also requests it. Follow active project and orchestration rules for workers and commits.

## Report

For `prepare` or `tickets`, return links to the implementation plan, epic when present, and first ready ticket. State the ticket count, ready roots, validation result, and any unresolved human decision.

For `execute` or `deliver`, report completed tickets, remaining ready and blocked tickets, verification evidence, and the next dependency wave.
