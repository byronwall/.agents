# Pointer capture case study

Use this reference when a graph, canvas, SVG, map, or editor supports both selection and panning.

## Symptom

A node shows a selected outline, but connected emphasis does not activate. Disconnected nodes stay fully visible. Earlier scripted checks appear to pass.

## Decisive trace

```text
target:pointerdown
surface:pointerdown
surface:pointerup moved:false
surface:click-capture ignored:false
surface:click ignored:false
selection:clear-empty
emphasis-mode:null
outbound selection:null
```

The trace contains no target click after pointerup.

## Cause

The SVG surface captured the pointer on pointerdown. Browser pointer capture retargeted the stationary release and click to the capturing SVG. The background click handler then treated the node gesture as empty space and cleared selection-derived emphasis before the delegated target click could run.

The selected outline could still appear through a separate or earlier state path. That made the bug look like an emphasis or opacity defect.

## Repair

Keep pointerdown as a potential click. Start SVG capture only after movement crosses the drag threshold. A stationary click then keeps its node or edge target. A real drag gains capture and suppresses its release click.

Keep background clearing on a confirmed empty-surface click. Do not infer empty space from a click retargeted by capture.

## Proof

Verify the event order after repair:

```text
target:pointerdown
surface:pointerdown
surface:pointerup moved:false
surface:click-capture ignored:true
target:click
selection:select-target
emphasis-mode:both
reconcile active and dimmed counts
```

Then remove the trace code and repeat the interaction matrix on a clean console.

## Lessons

- A visual selection marker does not prove downstream selected-state behavior.
- Computed opacity samples do not prove that a live click activated the emphasis model.
- Forced clicks and state injection can bypass pointer-capture defects.
- Missing events are often more useful than extra logs.
- Fresh screenshots are required when the defect is visual.
- High-volume logging can destabilize the browser. Instrument briefly and remove it promptly.
