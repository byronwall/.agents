# Dependency-Aware Execution

Use this mode only when the user asks to start implementation. The ticket graph
sets the frontier. Refine `open` tickets there before execution. Repository
state sets safe concurrency.

## Load the live graph

Read project instructions, git status, and every ticket in the requested epic or scope. Use the implementation plan only to audit ticket completeness or coordinate the graph. Never require an implementation worker to read it to understand assigned work. Use the tracker's live commands instead of inferring status from filenames.

For `tk`, inspect:

```sh
tk ready
tk frontier
tk blocked
tk dep cycle
tk dep tree --full <epic-id>
```

Refresh this view after each completed or changed ticket. The frontier includes
unblocked `open` and `ready` tickets. `open` means refinement remains; `ready`
means it can be executed. Never execute an `open` or dependency-blocked ticket.

For each `open` frontier ticket, follow the refinement pass in the main skill.
Inspect the current repository and proof environment. Split the ticket or add
coarse `open` prerequisites when the evidence requires it. Update dependencies
and the initiative state, then refresh the frontier. Repeat this pass before
each new wave. Set a ticket to `ready` only after its execution packet passes
the ready gate. Recheck a `ready` ticket before starting; demote it to `open`
and refine it again if material facts have changed.

Before `tk start`, confirm the ticket's ready gate against the current
repository and environment:

- no unresolved product decision or delete-or-preserve boundary;
- all required inputs and prerequisites exist;
- the acceptance proof can run;
- any observed baseline is still treated as evidence, not an invariant.

If this check fails, repair the ticket and graph or keep it blocked. Do not start
implementation and recover the missing decision in a private worker prompt.

## Build the next wave

For each `ready` ticket, record its outcome, owned context, likely files or shared state, proof, and downstream tickets it unlocks.

Choose the largest safe set that fits current worker capacity. Two ready tickets can run together only when they can make progress without unfinished output from each other and either:

- they own disjoint files and mutable state; or
- one is read-only.

Serialize work that can collide through shared migrations, schemas, generated files, lockfiles, fixtures, a single mutable database, one development server, or the same application files. A ready status does not prove edit independence.

When several safe sets have equal size, prefer tickets that unlock more downstream work. Then prefer higher tracker priority. Do not create fake parallelism to fill every slot.

## Work with orchestration

When `orchestrate-work` is active, the orchestrator owns scheduling, review, and the feedback loop. Use collaboration subagents, not persistent Codex tasks, for ticket workers. Apply `parallelize-work` principles when useful capacity remains.

Give one implementation ticket to each worker. The brief must include:

- the exact repository path and ticket ID;
- the full ticket body as the complete product and design handoff;
- owned files or responsibilities and known concurrent lanes;
- allowed and forbidden changes;
- required checks and acceptance proof;
- tracker status and reporting rules.

Put the outcome, owned seam, must/may/not boundary, and acceptance checklist
first. Include the full ticket once for the initial handoff. Do not add plan
excerpts that duplicate it.

Workers share one filesystem. Never assign overlapping writes without an explicit serialization boundary.

Do not supplement an incomplete ticket with private orchestrator context and continue. Repair the ticket first so its durable record matches the work being assigned. Repository inspection is still expected for implementation, but it must not be needed to recover omitted product intent.

For a repair pass, send only the failed checklist item, direct reproduction
evidence, allowed file scope, and required rerun. Do not resend the full ticket
unless the durable ticket changed materially.

Without active orchestration, follow current project rules. Do not silently turn the task into an orchestrator or create subagents without authorization.

## Advance the graph

Immediately before work begins, run `tk start <id>`. It requires `ready` status
and closed dependencies. After the worker reports:

1. inspect the diff and direct check output;
2. run or confirm each item in the ticket's acceptance checklist;
3. add a concise tracker note with evidence when supported;
4. close only after the outcome and required proof pass; move unavailable proof to a later ticket first;
5. keep failed or partial work in progress, or demote it to `open` when it needs a new planning pass;
6. reload frontier, ready, and blocked tickets;
7. dispatch the next safe wave.

Use a separate verification worker when risk or user-visible scope warrants it. Do not spend every slot on implementation if clean verification is the next useful lane.

If implementation evidence invalidates a dependency, scope, or ticket boundary, repair the graph and canonical initiative state. Do not work around a false graph in chat only.

Close the epic only when all required child outcomes and epic acceptance conditions pass. Stop at the requested scope, a human decision, an authorization boundary, or a blocker that no ready ticket can resolve.
