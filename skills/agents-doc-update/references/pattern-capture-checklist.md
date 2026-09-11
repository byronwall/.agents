# Pattern Capture Checklist

Use this checklist when updating AGENTS/docs after implementation work.

## Source collection

- Conversation notes: pain points, constraints, explicit preferences
- Code diff themes: repeated structures, helper extraction, anti-pattern removals
- Runtime incidents: regressions, root causes, verification outcomes

## Candidate rule selection

Promote to docs when at least one is true:

- The issue recurred multiple times in one session.
- The issue was subtle and expensive to debug.
- The issue involves cross-file/cross-surface consistency.
- The rule can be expressed as an actionable do/don’t.

## Rule template

- Context: "When <situation>"
- Directive: "Do <specific action>"
- Guardrail: "Avoid <failure mode>"
- Verification: "Check <observable signal>"

## Anti-patterns to avoid in docs

- Generic best-practice fluff with no project anchor.
- Long historical narratives.
- Duplicate rules in multiple locations without cross-reference.
- Non-testable language ("should probably", "might want to").

## Final consistency checks

- No conflict with existing AGENTS guidance.
- Terminology matches current codebase.
- File paths and commands are real.
- Checklist items align with current review expectations.
