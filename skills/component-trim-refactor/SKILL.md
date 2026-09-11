---
name: component-trim-refactor
description: Keep UI components small and maintainable after feature additions. Use when new functionality is roughed in and now needs structural cleanup: split responsibilities, extract hooks/presentational components, and preserve behavior.
---

# Component Trim Refactor

## Goal

Ship features quickly, then deliberately refactor so components stay easy to maintain.

Use this skill when a component was expanded to land functionality and now mixes concerns (data parsing, state orchestration, rendering, modal UX, pointer math, timers, etc.).

## Trigger Signals

- A file grows past ~200 LOC.
- One component manages multiple feature islands.
- Repeated toolbar/action button markup appears in multiple places.
- Event math (zoom/pan/drag) lives inline with UI markup.
- Multiple timeout/reset effects exist without centralized cleanup.

## Core Policy

1. Rough-in is acceptable for momentum.
2. Before finishing, refactor to trim and isolate responsibilities.
3. Preserve behavior first; improve structure second.

## Refactor Workflow

1. Stabilize current behavior
- Run a quick verify (`pnpm type-check`).
- Keep existing UX working before moving code.

2. Identify natural boundaries
- Router/orchestrator logic
- Feature-specific view (e.g., code block vs mermaid block)
- Interaction logic (zoom/pan/keyboard)
- Reusable presentational controls (action trays, header actions)

3. Split by responsibility
- Keep parent component thin: detect mode and delegate.
- Move interaction math/state into a hook (`useX`).
- Move repeated control groups into small presentational components.
- Keep each extracted file focused on one concern.

4. Add cleanup ownership
- Centralize timeouts/subscriptions in the component or hook that creates them.
- Ensure `onCleanup` clears timers and detaches stateful side effects.

5. Verify and size-check
- Run `pnpm type-check`.
- Re-check file sizes and keep components near/under 200 LOC when practical.
- If one file remains larger, split one more layer (usually modal shell or action group).

## Structural Patterns

- **Thin router component**
  - Detect content type and render one of specialized children.
- **Behavior hook**
  - Store + handlers + computed outputs for interaction-heavy logic.
- **Presentational controls**
  - Stateless components for repeated button trays/toolbars.
- **Feature block component**
  - Owns lifecycle and feature state, delegates controls and viewport math.

## Guardrails

- Do not change behavior while splitting unless required to fix a known issue.
- Prefer additive extraction over in-place rewrites.
- Keep props explicit and typed; avoid prop-shape ambiguity.
- Preserve SSR/hydration-safe baseline markup for markdown-rendered content.

## Done Criteria

- Parent/orchestrator component is short and readable.
- Interaction-heavy logic is not embedded in large JSX trees.
- Repeated button groups are extracted.
- Timer and async cleanup is explicit.
- Type check passes.

## Example Prompts

- "Use component-trim-refactor on this oversized component after feature work."
- "I roughed this in; now split it into thin router + feature blocks + hooks."
- "Refactor this markdown renderer so each feature island is isolated and maintainable."
