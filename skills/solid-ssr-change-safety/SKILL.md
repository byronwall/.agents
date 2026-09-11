---
name: solid-ssr-change-safety
description: Prevent SolidJS SSR hydration mismatches during frontend edits. Use when changing components that render on both server and client, especially markdown renderers, conditional JSX, list rendering, and DOM-structure-heavy UI.
---

# Solid SSR Change Safety

## Goal

Keep the server-rendered DOM tree identical to the initial client hydration tree.

## Core Rule

Match node existence and hierarchy between SSR and first client render.
Only mutate attributes/text/content after mount.

## Change Guardrails

- Keep the same JSX element structure for SSR and initial client render.
- Do not pass already-created JSX elements through ordinary props and then conditionally insert them inside SSR-rendered layout shells. In Solid hydration this can surface as `template2 is not a function`. Prefer data props, component references, render callbacks invoked in one stable branch, or explicit call-site slots with stable wrapper nodes.
- Avoid render-time branches based on `window`, `document`, viewport size, time, random values, or client-only APIs.
- Treat select/menu/popover portal behavior as hydration-sensitive.
  - Prefer in-tree rendering (`skipPortal`/non-portalled mode) on SSR route surfaces by default.
  - Only enable portal rendering when required by clipping/stacking constraints, then hard-refresh verify parity.
- Avoid returning different element types for the same markdown node (`code` must stay `code`, `pre` must stay `pre`).
- Defer enhancements to `onMount` and use client-side DOM mutation for progressive enhancement.
- Prefer setting `id`, `class`, `data-*`, `innerHTML`, and event hooks post-mount over changing JSX tree shape.
- Preserve stable wrapper nodes when adding buttons/overlays; hide/show after hydration with attributes/CSS.

## Async Data Guardrails (High Signal)

- Prefer separate `Suspense` islands for independent async resources.
  - Example: if one section uses `createAsync(fetchA)` and another uses `createAsync(fetchB)`, do not mix both sections under one shared `Show`/list subtree unless they are intentionally coupled.
- Keep each async section’s fallback/empty states local to that section.
  - Avoid one section’s unresolved state changing the DOM shape of another section.
- Avoid mixing multiple async accessors inside one list-render gate.
  - Gate one list with one resolved accessor where possible.
- Keep list ordering deterministic across server and client.
  - Prefer stable lexical comparisons (`a < b ? -1 : 1`) over locale-sensitive comparators when hydration stability matters.

## Safe Workflow

1. Identify where SSR output is generated.
2. Keep a minimal baseline renderer that is hydration-safe.
3. Add enhancement logic only in `onMount`.
4. Ensure fallback markup is identical server/client pre-hydration.
5. Hard refresh and verify no hydration mismatch.
6. For async-heavy pages, validate each async section in isolation before recombining.

## Red Flags

- Hydration errors like `template2 is not a function` or missing hydration keys.
- `template2 is not a function` after adding a panel/header/icon prop, especially `icon={<Icon />}` or other JSX-valued props that are conditionally rendered by a shared shell.
- Brief flash of content before crash.
- Failures that disappear when select/content portal is disabled (`skipPortal`) indicate portal hydration ownership mismatch.
- Component works only when custom renderer is disabled.
- Hash/query navigation state conflicts that change rendered tree at load.
- Page works when one async section is removed, but fails when two async sections render in the same boundary.

## Recent Incident Notes (Vacation Planner)

- `template2` failures were triggered by pre-hydration tree-shape changes from derived "effective" selectors that changed major `Show` branches before hydration completed.
  - Rule: avoid introducing fallback memos that can switch whole route subtrees during initial hydration.
  - Prefer stable signal defaults (or route-level serialized state) that do not alter branch ownership between SSR and first client pass.
- `SimpleSelect` portal rendering increased hydration fragility in this app.
  - Rule: default overlay/select wrappers to non-portalled in SSR surfaces unless a portal is required.
  - If portal is required, validate hard-refresh SSR parity explicitly.
- Ark/Zag `Splitter` surfaced `ReferenceError: document is not defined` in server/HMR cleanup paths.
  - Rule: when SSR errors mention `@zag-js/splitter` cleanup (`removeGlobalCursor` / `clearGlobalCursor`), treat Splitter as the first suspect and swap to static CSS split as containment.
- Color palette debugger hit `template2 is not a function` when a reusable `Panel` accepted `icon?: JSX.Element` and inserted `props.icon` inside a conditional header.
  - Rule: reusable SSR shells should own their header tree directly or accept serializable/icon-name data, not conditionally reinsert pre-created JSX nodes.

## Example Prompts

- "Use the Solid SSR safety skill and refactor this markdown renderer so hydration is stable while keeping features."
- "Before I merge this frontend change, run an SSR safety pass and list any DOM-tree mismatch risks."
- "Apply hydration-safe progressive enhancement rules to this Solid component and avoid render-time client-only branches."

## Verification

Run `pnpm type-check`.
Use hard-refresh/manual navigation checks for hydration behavior.
