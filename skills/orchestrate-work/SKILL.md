---
name: orchestrate-work
description: Coordinate substantial work from one persistent orchestrator with narrowly scoped GPT-6 Luna collaboration subagents. Use when Byron says `$orchestrate-work`, asks Codex to be an orchestrator, requests parallel implementation or investigation, asks to split coding from verification, or wants a coordinated feedback loop. Create a dedicated Codex task only for a new orchestrator, an explicit request for a separate task, or a wholly new scope that needs independent ownership and history.
---

# Orchestrate Work

Turn the invoking chat into the orchestrator. Keep coordination, synthesis, and
the feedback loop here. Use narrowly scoped collaboration subagents for
investigation, implementation, and verification.

## Delegate by default

- Treat invocation of this skill as an orchestrator declaration.
- Choose the family emoji and set the task name to
  `⭐ <emoji> 00 · <short description>` when title tools are available.
- Treat the starred task name as the authoritative orchestrator status at the
  start of every turn.
- For nearly every user message in an orchestrator, spawn a new collaboration
  subagent with empty context. Reuse an existing subagent only when its prior
  context is materially useful for the next step.
- Delegate substantive investigation, implementation, verification, and
  follow-up work, even when direct work would be faster.
- Byron accepts the extra time. He expects smaller models to do the work and
  the orchestrator to check their results.
- Keep direct work to coordination, synthesis, worker review, small
  administrative actions, and urgent safety handling.
- If no useful worker scope exists or subagents are unavailable, work directly.
  State the applicable exception when no delegation occurs.
- This rule applies only to orchestrator tasks. Other tasks can work directly
  unless another instruction requires delegation.

## Establish the orchestrator

1. Resolve the owning project and exact saved-checkout path.
2. Read its `AGENTS.md` and inspect git status before work starts.
3. Preserve dirty state and unrelated changes.
4. Choose one distinctive, meaningful emoji for the orchestration family.
5. Rename this chat to `⭐ <emoji> 00 · <short description>` when title tools
   are available.

Subagents do not appear as sidebar tasks. Do not assign them sidebar numbers or
create dedicated tasks only to preserve the title family.

## Default to Luna subagents

- Use collaboration tools such as `spawn_agent`, `wait_agent`, `send_message`,
  `followup_task`, and `interrupt_agent`.
- Unless Byron specifies otherwise, spawn workers with `model:
  "gpt-6-luna"` and `reasoning_effort: "high"`.
- Default to `fork_turns: "none"`. Use a small bounded turn count only when
  inherited context has clear value. Give each subagent a self-contained brief.
- Default to a new subagent with empty context. Do not reuse a subagent only
  because it is available. Reuse it only when its prior context is materially
  useful, such as a focused repair of its own implementation.
- Keep each new subagent useful and bounded. Parallelize independent work.
- Serialize overlapping edits or give concurrent subagents disjoint ownership.
- Remember that subagents share the current filesystem and working directory.
- If subagents are unavailable, do the work in the orchestrator or serialize it.
  Do not create a dedicated task as a fallback.
- Let a subagent finish without repeated messages or forced progress.
- Use long waits. Intervene only for a request, blocker, failure, or excessive
  run time.

Treat invocation of this skill as authorization to create and coordinate the
needed subagents. It also authorizes progress commits under the rules below. It
does not authorize pushes, deployments, destructive actions, external messages,
or scope beyond the user's request.

## Create a dedicated task only for new scope

Use Codex task or thread tools only when one of these conditions applies:

- Byron explicitly asks for a separate task or thread.
- Byron asks this task to create another persistent orchestrator.
- The work is a wholly new scope that needs independent ownership and history.

Do not create a dedicated task only because a worker needs separate context,
parallel execution, implementation ownership, or clean-room verification. Use a
subagent for those cases.

If this orchestrator remains responsible for the result, the scope is a worker
scope. Use a subagent even when the work is substantial or cross-project.

When a dedicated task is justified:

- Use `create_thread`, `wait_threads`, `read_thread`,
  `send_message_to_thread`, and `set_thread_title` as needed.
- Use the owning project's saved checkout and a local environment.
- Never create a git worktree unless Byron explicitly requests one.
- For a new persistent orchestrator, use GPT-5.6 Sol at High reasoning. Never
  use GPT-6 Luna for that orchestrator.
- For other dedicated tasks, use GPT-6 Luna at High reasoning unless project
  instructions or Byron set a different default.
- For a worker in this orchestrator family, title it `<emoji> 01 · <short
  description>`, then increase the number by creation order.
- For a new orchestrator, give it its own emoji and `⭐ <emoji> 00 · <short
  description>` title.
- Keep responsibility for tracking the task unless Byron explicitly asks for a
  handoff.

## Git commits

- On a branch other than `main`, workers may create small, coherent commits.
- Use useful checkpoint commits instead of one large diff.
- On `main`, commit only when Byron explicitly requests it.
- Before each commit, verify both Git identities are `Byron Wall
  <byron@byroni.us>`.
- Never use an agent, bot, Codex, or OpenAI identity.
- If an identity differs or is missing, set both identities for that commit.
  Do not change unrelated repository configuration.

## Brief each worker

Give each subagent a self-contained prompt with:

- its role and concrete outcome;
- the exact project path and saved-checkout requirement;
- applicable `AGENTS.md`, skill, and package-manager rules;
- relevant evidence, artifacts, URLs, reproduction steps, and acceptance
  criteria;
- file or responsibility boundaries and known concurrent work;
- allowed and forbidden changes, required checks, and terminal actions;
- the required report shape.

Require each worker to inspect git status, preserve unrelated changes, report
blockers precisely, and avoid coaching other workers. Route cross-worker
findings through the orchestrator.

Luna High is fast. State the decisive evidence, success boundary, required
checks, and stopping condition. Add detail for ambiguous or high-risk work.

## Separate roles and context

Use the smallest combination that fits the work:

- **Investigation:** Read-only diagnosis, architecture study, or competing
  explanations.
- **Implementation:** A bounded change with explicit ownership and verification
  commands.
- **Verification:** An independent review of the combined result, preferably
  read-only.
- **Browser verification:** A clean-room, black-box subagent. Give it the
  user-visible goal, starting URL, run instructions, fixtures, credentials when
  authorized, environmental constraints, and acceptance criteria.

Do not give a browser verifier a source walkthrough or likely bug locations.
Ask it to avoid source inspection unless blocked. If it reads source, it must
separate observations made before and after that inspection.

Treat difficulty with controls, labels, navigation, accessibility, or flow
completion as product evidence. Do not coach the verifier around these issues.

Use a separate verification subagent when an independent pass is practical.

## Run the feedback loop

1. Dispatch the first useful subagent wave and record each role and boundary.
2. Wait for all workers with long, bounded waits. Do not narrate unchanged
   snapshots.
3. Inspect final reports and concrete evidence. Do not accept unsupported
   success claims.
4. Reconcile findings in the orchestrator.
5. Send precise revision evidence to the responsible implementation subagent.
   Reuse it with `followup_task` only when its implementation context is useful.
6. Send revised behavior to a separate verification subagent.
7. Continue implementation, verification, and focused repair until acceptance
   is met or user input is required.
8. Run or confirm project-level terminal checks and any explicitly requested
   commit, push, deployment, or production verification.
9. Report the combined outcome, verification, and unresolved risks.

## Review from evidence

Use GPT-6 Luna at High reasoning for all subagent work. Review each
result against direct evidence and required checks. Change the model only when
Byron explicitly requests it.

When a subagent has trouble, give it the earlier attempts, errors, diagnostics,
verification results, and exact unresolved question. Do not repeat discovery
work.
