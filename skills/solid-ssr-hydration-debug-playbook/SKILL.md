---
name: solid-ssr-hydration-debug-playbook
description: Troubleshoot and resolve SolidJS hydration mismatches using a comment-out and re-enable playbook. Use when seeing hydration errors, template crashes, or server/client DOM mismatch behavior.
---

# Solid SSR Hydration Debug Playbook

## Goal

Find the exact mismatch source fast, then restore features with targeted hydration-safe fixes.

## Isolation Method

Use coarse-to-fine comment/backout isolation.

1. Disable a large suspect subtree.
2. Confirm hydration stabilizes.
3. Re-enable one chunk at a time.
4. Stop when mismatch returns.
5. Rewrite only that chunk with hydration-safe patterns.

## Practical Sequence (General)

1. Disable custom render overrides first (high signal).
2. Restore plain baseline render path.
3. Re-enable headings only.
4. Re-enable `code` behavior only.
5. Re-enable `pre` wrappers/controls.
6. Re-enable mermaid/client-only visuals last.

## Practical Sequence (Async Route Pages)

1. Reduce route to static content (no `createAsync`, no list rendering).
2. Re-enable one async section only.
3. Re-enable second async section only.
4. If each works alone but fails together, split into separate `Suspense` islands.
5. Re-enable list iteration in steps:
   - scalar render (`count` only)
   - list loop with native elements
   - styled/components wrappers
6. Keep each suspect step as a single small delta so regressions are attributable.

## Fix Patterns

- Keep SSR and initial client DOM identical.
- Move dynamic branching to `onMount` only when truly client-only behavior is needed.
- Prefer one async resource per `Suspense` boundary for unrelated sections.
- Replace shared mixed-resource list gates with section-local gates.
- Keep list ordering deterministic across SSR/client.
- If `grouped().length` works but `For each={grouped()}` fails, suspect row subtree hydration ownership and isolate row markup/component boundaries.

## Debug Signals

- `template2 is not a function` with content flash: likely tree mismatch.
- `Hydration Mismatch. Unable to find DOM nodes for hydration key ...` with `data-source-loc`: use the source location to isolate that exact JSX subtree first.
- Routes with Ark/overlay selects that stabilize when `skipPortal` is enabled: treat portal ownership as the first suspect.
- Works when one section is removed, fails when both are present: boundary interaction problem.
- Works until one feature re-enabled: culprit localized.
- `ReferenceError: document is not defined` with `@zag-js/splitter` frames (`removeGlobalCursor` / `clearGlobalCursor`): Splitter machine cleanup is running in server context.

## Recent Incident Pattern (Vacation Planner)

Use this order for similar failures:

1. Check for framework machine stack traces first.
   - If stack includes `@zag-js/splitter`, remove/gate Splitter immediately and verify with static CSS columns.
2. Revert pre-hydration "effective state" memos that can change `Show` gates.
   - Example: derived IDs that pick first record (`selected || firstItem`) caused route subtree ownership flips during hydration.
3. Disable portalling in select/popover wrappers on SSR routes.
   - Keep overlays in-tree first; only re-enable portals after hydration is stable.
4. Re-run verification in this order:
   - hard refresh `/`
   - direct deep-link URL load
   - in-app navigation between tabs/views
   - `pnpm type-check`

## Example Prompts

- "Use the hydration debug playbook: comment out risky chunks, isolate the mismatch, then re-enable features incrementally."
- "I get a Solid hydration error on refresh. Apply the backout-and-restore workflow and fix only the culprit area."
- "Run a coarse-to-fine SSR mismatch triage on this component and propose targeted post-mount fixes."

## Completion Criteria

- Hard refresh loads without hydration error.
- Server render and client hydration both succeed.
- Required features restored incrementally.
- No broad rewrites outside culprit area.

## Verification

Run `pnpm type-check`.
Validate with hard refresh, direct URL load, and in-app navigation.
