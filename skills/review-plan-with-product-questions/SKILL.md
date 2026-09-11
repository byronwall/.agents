---
name: review-plan-with-product-questions
description: Review technical, architectural, migration, implementation, or refactoring plans by first asking product-level questions that resolve technical choices, then identifying the weakest, least-clear, and most failure-prone parts. Use when a user wants plan feedback grounded in product priorities rather than architecture preferences, asks what an implementation is most likely to get wrong, or wants product questions that guide engineering decisions.
---

# Review Plans Through Product Priorities

Read the complete plan and enough surrounding project context to understand its intended product, users, workflows, compatibility promises, and constraints. Follow repository guidance when inspecting local plans.

## Review workflow

1. Separate explicit product requirements from technical assumptions disguised as requirements.
2. Identify decisions whose best technical answer depends on user value, usage patterns, scale, compatibility, or acceptable tradeoffs.
3. Ask the product questions first.
4. Then review the plan's weakest, least-clear, and most failure-prone parts.
5. End with the most plausible bad outcome if the plan is implemented literally.

Do not turn the product questions into architecture questions with softer wording. Ask about users, jobs, decisions, priorities, frequency, scale, persistence, compatibility, failure recovery, and acceptable tradeoffs. A useful answer should directly change an implementation choice.

When the user requests a number of questions, provide exactly that number. Otherwise, ask 8–10 non-overlapping questions, ordered by decision-making value. Briefly explain what each answer would determine when that is not obvious.

## Product-question themes

Select only themes relevant to the plan:

- the primary user and the job they are trying to finish;
- the most important workflow, screen, or output;
- what may be removed, deferred, or intentionally changed;
- the decision a user should make and how quickly;
- typical and worst-case scale plus acceptable latency;
- state that must survive refreshes, revisions, or sharing;
- compatibility audiences and the cost of breaking them;
- expected behavior during loading, failure, stale data, and empty results;
- accessibility, mobile, collaboration, or automation importance;
- product qualities that win when exact parity conflicts with improvement.

Avoid questions whose answers are already explicit in the plan. Prefer forced prioritization over vague prompts such as "What matters most?"

## Weakness review

Prioritize findings that could produce a technically correct but product-wrong implementation. Look especially for:

- undefined terms such as parity, stable, fast, minimal, compatible, or local scale;
- equal investment in features with unequal user value;
- missing primary journey or success measure;
- hidden identity, persistence, deep-link, and refresh semantics;
- eager or fragmented data boundaries chosen without usage and scale evidence;
- compatibility promises without named consumers or retirement criteria;
- test scope without risk ranking or measurable exit criteria;
- phase sequencing that delays validation of the highest-value or highest-risk workflow;
- error and empty states described as schemas rather than user recovery experiences;
- architectural completion criteria substituted for product outcomes.

For each material weakness:

1. Name the ambiguity or risk directly.
2. Explain the dumb implementation it invites.
3. State the product decision or evidence needed to resolve it.
4. Cite the relevant plan section or local file lines when available.

Group closely related issues and rank by product impact. Do not pad the review with generic engineering advice.

## Output order

Use this order unless the user explicitly requests another:

1. **Product questions**
2. **Weakest or least-clear parts**
3. **Most likely bad outcome**

Keep technical prescriptions conditional on product answers. The purpose is to expose the choices the product owner actually cares about, not to make architecture the product owner's problem.
