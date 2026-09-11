---
name: debug-ui-event-flow
description: Diagnose and repair browser interaction regressions where pointer, click, drag, focus, selection, URL state, or visual emphasis disagree. Use for click-versus-drag bugs, pointer-capture retargeting, delegated-event ordering, background clicks that swallow target clicks, selection outlines without downstream display changes, stale click suppression, or UI behavior that passes scripted checks but fails through real mouse input.
---

# Debug UI Event Flow

Recover the real browser event sequence before changing state or CSS. Prove the fix through the same physical interaction that failed.

## Establish the failure

1. Start a fresh service from the exact checkout and data root.
2. Record the commit, port, root, generation, and asset mode when available.
3. Reproduce with a real pointer or keyboard action. Do not use state injection, URL mutation, direct event dispatch, or forced DOM selection as decisive evidence.
4. Save the user's screenshot and exact URL as the acceptance baseline.
5. Separate these questions:
   - Did the target receive the gesture?
   - Did selection state change?
   - Did downstream state reconcile?
   - Did the rendered display change visibly?

Treat a selected outline without the expected connected-state display as a failure.

## Map event ownership

Trace one gesture across all owners:

```text
target pointerdown
  -> surface or camera pointerdown
  -> movement threshold
  -> optional pointer capture
  -> pointerup or cancel
  -> click capture
  -> target or background click
  -> selection action
  -> parent or URL update
  -> controlled-state reconciliation
  -> derived visual state
  -> rendered classes and computed styles
```

Inspect target handlers, surface handlers, camera controllers, delegated listeners, pointer capture, click suppression, and cleanup together. Do not debug only the final CSS.

## Instrument briefly

Add temporary structured logs only when ordinary browser tools cannot establish ordering.

- Use one stable prefix, a sequence number, and a timestamp.
- Log compact IDs, event targets, movement state, selections, modes, and result counts.
- Add `console.trace` only where selection clears or downstream mode becomes null.
- Record `target`, `currentTarget`, `composedPath()`, `pointerId`, capture state, and suppression state.
- Avoid full graphs, DTOs, or repeated high-volume pointermove payloads.
- Gate logs behind a debug switch by default. Follow an explicit request for unconditional logs.
- Remove all instrumentation immediately after it identifies the cause. Logs can slow or crash the browser.

For pointer-capture or delegated-click symptoms, read [references/pointer-capture-case.md](references/pointer-capture-case.md).

## Diagnose from ordering

Use missing events as evidence. For example, this sequence proves retargeting or swallowing:

```text
target:pointerdown
surface:pointerdown
surface:pointerup moved:false
surface:click
selection:clear-background
```

If `target:click` never occurs, do not repair selection reconciliation first. Find why the click stopped belonging to the target.

Check these common causes:

- Pointer capture starts on pointerdown and retargets a stationary click to the surface.
- A background handler treats a bubbled or retargeted target click as empty space.
- Capture-phase clearing runs before a delegated target click.
- Drag suppression remains set and swallows the next click.
- Pointer cancel or lost capture leaves stale gesture state.
- Controlled state preserves selection but resets its derived display mode.
- A test changes state directly and bypasses the failing event path.

## Preserve one gesture contract

For combined click and pan surfaces, prefer this contract:

- Keep a press as a potential click until movement crosses a small threshold.
- Start pointer capture only after the drag threshold when feasible.
- After capture begins, pan and suppress the synthetic release click.
- Let a stationary node or edge click retain its original target.
- Clear selection only for a confirmed empty-surface click.
- Let an empty-surface drag pan without clearing on release.
- Clean up on pointerup, pointercancel, and lostpointercapture.
- Preserve keyboard focus and activation independently from pointer logic.

Use a different contract only when platform evidence requires it. State the ownership rule in code.

## Prove state and display

After the fix, record both state and visible output:

- URL or controlled selection value.
- Local selection and derived display mode.
- Selected, active, secondary, and dimmed node and edge counts.
- Computed styles for one selected, connected, and disconnected sample.
- A fresh screenshot after a real target click.

Do not accept DOM counts alone. The screenshot must clearly show the requested visual change.

Verify this interaction matrix:

1. Stationary node click selects.
2. Same-node click toggles as designed.
3. Stationary edge click selects.
4. Node-start drag pans without selecting.
5. Edge-start drag pans without selecting.
6. Empty click clears.
7. Empty drag pans without clearing.
8. A click after several drags still works.
9. Keyboard activation and visible focus still work.
10. URL-restored state produces the same display as a live click.

## Finish cleanly

Run project-approved static checks. Use an independent browser pass when the change is user-visible or timing-sensitive.

Before reporting completion:

- Remove every temporary log, trace, debug helper, and payload.
- Confirm no stale service or old asset produced the evidence.
- Review the diff for accidental event or accessibility regressions.
- Report the root cause as an event sequence, not a guess.
- Include the proof screenshot path and any remaining risk.
