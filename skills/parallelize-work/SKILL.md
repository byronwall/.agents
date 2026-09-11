---
name: parallelize-work
description: Find safe parallel seams in an active orchestrator task and put idle collaboration agents to useful work. Use when Byron invokes `$parallelize-work`, asks whether more work can run in parallel, or says the orchestrator has too few active agents.
---

# Parallelize Work

Increase useful concurrency now. Do not only suggest a future split.

## Fill the idle slots

1. Inspect the current goal, active agents, pending work, and available slots.
2. Identify the critical path and work that does not need its next result.
3. Spawn the best bounded workers that can start now, up to the useful capacity.
4. Keep the orchestrator free to coordinate, review evidence, and unblock work.
5. State the new lanes and their boundaries in one concise update.

Follow the active project's orchestrator rules for model, reasoning, context,
briefs, filesystem safety, and verification. Invocation authorizes collaboration
subagents for the current scope. It does not authorize new persistent tasks,
external changes, destructive actions, or broader product scope.

## Find seams quickly

Look for these seams in order:

- Independent questions whose answers can change different decisions.
- Read-only inspection across separate subsystems, repositories, logs, or data.
- Implementation slices with disjoint file or responsibility ownership.
- One implementation lane plus independent test, review, or black-box verification.
- Pattern search, reproduction, fixture preparation, or risk analysis that can run
  before the main result exists.
- Documentation or cleanup only when it is already required by the request.

Split by outcome, not by arbitrary file count. Give each worker one concrete
deliverable, decisive evidence, boundaries, checks, and a stopping condition.

## Use thin slices

A good slice:

- can start with current evidence;
- has little or no dependency on another worker's unfinished result;
- owns distinct files or stays read-only;
- returns a decision, patch, test result, or reproduction;
- is large enough to justify its context cost.

Prefer a short investigation that unlocks implementation over a broad survey.
Prefer one clean verifier over several workers repeating the same review.

## Do not create fake parallelism

Do not spawn a worker when it would:

- wait for another worker's output before it can begin;
- edit the same files or shared state without a clear ownership boundary;
- duplicate an active investigation without a contrasting hypothesis;
- produce optional polish outside the request;
- cost more coordination than the task itself.

If no safe seam exists, say why in one sentence and continue the critical path.
Reassess after each material result because new seams can appear.
