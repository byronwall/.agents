---
name: propose-fixes
description: Develop, compare, and recommend among multiple plausible fixes for a problem. Use only when the user explicitly invokes $propose-fixes or asks to use the propose-fixes skill for a bug, architecture issue, UX problem, performance concern, process failure, tooling limitation, or other general-purpose problem where several viable approaches may exist. Inspect supplied context and relevant files, but ask before running diagnostics. Present 3-5 meaningfully distinct options, score them on problem-specific dimensions, recommend one option or a deliberate hybrid, and wait for the user's decision before taking action.
---

# Propose Fixes

Analyze a problem as a decision among genuinely different solution strategies. Produce a recommendation the user can challenge before any implementation begins.

## Guardrails

- Remain analysis-only during this workflow.
- Read the supplied context and inspect relevant files, configuration, documentation, and existing tests when available.
- Ask for permission before running any diagnostic, test, build, benchmark, reproduction, or other command intended to gather new evidence. Explain briefly what it would clarify. Continue with existing evidence if the user declines.
- Do not edit files, implement a fix, create or dispatch a worker task, or make external changes.
- Clearly separate observed facts from assumptions. Ask a clarifying question only when unresolved ambiguity would materially change the options or recommendation.

## Develop the Options

1. State the problem, desired outcome, and important constraints in a compact framing.
2. Identify 3-5 viable options. Prefer different mechanisms, intervention layers, ownership boundaries, or tradeoff profiles—not cosmetic variations of the same idea.
3. Make each option concrete enough to evaluate. For each, describe:
   - the core mechanism;
   - the main changes it would require;
   - its strongest advantage;
   - its most important drawback or failure mode.
4. Exclude clearly infeasible options rather than padding the list. If fewer than three credible options remain, say so and explain why.
5. Consider a hybrid only when specific elements reinforce one another. Avoid combining options merely to accumulate advantages; account for added complexity and interaction risk.

## Choose Evaluation Dimensions

Select the dimensions that matter for the current problem. Usually use 4-7 dimensions, such as correctness, user impact, implementation effort, delivery speed, operational risk, maintainability, reversibility, performance, migration burden, or fit with the existing architecture.

- Define each dimension briefly so the direction of a high score is unambiguous.
- Score every option from 0 to 10, where 0 is unacceptable for that dimension and 10 is excellent.
- Weight dimensions implicitly by emphasizing the user's stated priorities. If priorities conflict or weighting could reverse the decision, make the weighting explicit.
- Support scores with short task-specific reasons. Do not manufacture precision from weak evidence.
- When uncertainty is materially high, give a crude range such as `5-7` and name the missing fact that drives it. Otherwise, use a single score and omit confidence commentary.
- Treat the scores as decision aids, not a substitute for judgment. Note hard constraints separately because averaging must not rescue a disqualifying flaw.

## Compare and Recommend

Present a compact comparison table followed by a short synthesis:

1. Explain the important tradeoffs and where options differ most.
2. Identify any option dominated by another and why.
3. Recommend the best option or a clearly specified hybrid.
4. Explain why it best fits the problem and priorities, what it gives up, and the main risk to watch.
5. If the choice depends on an unresolved fact, say what would change the recommendation.

End with an explicit decision point. Ask the user whether they agree, want to modify the recommendation, prefer another option, or want a worker task created to implement an approved direction. Stop and wait. Do not treat silence or the initial invocation as approval.
