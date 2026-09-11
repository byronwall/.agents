---
name: agents-doc-update
description: Update AGENTS.md and related documentation after implementation work. Use when the user asks to capture patterns, lessons, conventions, or reusable workflows from an extended discussion, bugfix session, refactor, or feature delivery.
---

# Agents + Docs Update

Codify what changed into maintainable project guidance with minimal prompt overhead.

## Outcomes

- Keep `AGENTS.md` aligned with current implementation patterns.
- Update supporting docs (`README.md`, `docs/*.md`, runbooks) when behavior or workflow changed.
- Preserve practical rules that prevent repeated regressions.

## Workflow

1. Establish scope.
2. Extract themes from conversation + changed files.
3. Convert themes into concise, enforceable guidance.
4. Patch docs with targeted edits.
5. Verify internal consistency and summarize updates.

## 1) Establish scope

Confirm which docs to touch:

- Always consider `AGENTS.md` first when the request mentions standards, patterns, conventions, or team workflow.
- Include product/feature docs when behavior changed.
- Include setup or troubleshooting docs when toolchain/process changed.

If scope is unclear, default to:

- `AGENTS.md`
- the most relevant `docs/*.md` file(s)
- `README.md` only if onboarding/usage changed.

## 2) Extract themes from real work

Use concrete evidence, not generic advice:

- User pain points from the thread.
- Bugs found/fixed and root causes.
- Repeated implementation patterns.
- Verification expectations (type-checks, manual checks, smoke tests).

Prefer high-signal patterns such as:

- data flow invariants
- rendering/SSR safety rules
- shared component boundaries
- migration or fixture update pitfalls
- consistency checks between parallel UI surfaces.

## 3) Write enforceable guidance

Rules should be specific enough to execute.

Good rule qualities:

- States **when** it applies.
- States **what to do** (imperative).
- States **what to avoid** when relevant.
- Uses short examples for fragile patterns.

Keep prose lean:

- Avoid narrative timelines.
- Avoid repeating existing guidance.
- Prefer bullets and checklists over paragraphs.

## 4) Patch strategy

For `AGENTS.md` updates:

- Add new sections near related existing topics (do not scatter).
- Keep naming and style consistent with existing headings.
- Add narrowly scoped checklists for repeat-prone workflows.

For supporting docs:

- Update only sections affected by behavior/process changes.
- Add short “Gotchas” notes for tricky edge cases.
- Link to `AGENTS.md` guidance when team conventions are referenced.

## 5) Verification pass

Before finalizing:

- Confirm no contradictions between new and existing guidance.
- Confirm examples match current code patterns.
- Confirm referenced files/commands exist.
- Run repo-standard verification command(s) when code was touched.

## Quality bar

Treat each documentation change as operational guardrails:

- Would this rule have prevented the issue we just debugged?
- Can a teammate apply it without reading the full thread?
- Is the wording testable during review?

If any answer is "no", tighten wording.

## Output format (for the final response)

1. Brief change summary.
2. List of files updated.
3. Key rules/themes captured.
4. Any follow-up docs worth updating next.

## Reusable prompt snippets

- "Use $agents-doc-update and codify the key rules from this debugging session into AGENTS.md and relevant docs."
- "Use $agents-doc-update to sync our new implementation patterns into project guidance with minimal churn."
- "Use $agents-doc-update and add only high-signal conventions that would have prevented this regression."
