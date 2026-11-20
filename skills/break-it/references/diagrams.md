# Diagrams for a break-it pass

Two kinds, both Draftably `.draft` files (read the `draftably` skill first). Number them so they sort: `1-boundary.draft`, `2-c1-duplicate-import.draft`, …

## 1. The boundary

One diagram per run. It answers "where does this change meet the outside, and where would a break show?"

- **Groups, left to right:** who calls it (actors, including the unexpected ones), what selects the path (config, flags, deploy templates), the change itself, and where it shows (outputs at their destinations).
- **Edges:** each actor to the entry it reaches; config to the code it selects (`kind=async` for deploy-time selection); the change to each output.
- **Seams:** label the edge where a fault can be injected with `seam: <what>` ("seam: retry repeats the import"). Keep it to the seams that produced candidates.
- **Colors:** one accent per group role, every accent in the legend. Changed code in `amber`, actors in `sky`, config in `violet`, outputs in `slate` works well.
- Start with `layout root flow gap=48 fit=slide`, run `draftably check --metrics --fit slide`, and if it reports crossings let `draftably vary <file> --fit slide` pick; a reading-right `compound-flow` usually wins for this shape.

Worked example: [boundary-example.draft](boundary-example.draft).

Two warnings come up often. `[stranded]` on the actors means they sit far from the deep node they all call: merge actors that reach the same entry into one box, add `frame=soft` on the groups (a group attribute, not a layout line), or let `vary --fit slide` re-lay it. `backward-side` on an edge into the change: add `to=left` on that edge.

If it needs more than about a dozen boxes, the inspection walked too far; cut the actors and outputs no candidate uses.

## 2. Swiss cheese, one per candidate that matters

Draw one for every `broke` candidate and for a `held` candidate whose defense is the point of the change. Generate the skeleton from the ledger:

```bash
python3 ~/.agents/skills/break-it/scripts/cheese.py draft <run>/ledger.json C1 > <run>/diagrams/2-c1-duplicate-import.draft
```

The skeleton reads left to right: who starts it, then one group per slice with the hole that was open (amber when often open, orange when rarely open), then the harm in red. A `held` candidate ends at the slice that stayed shut (mint), reached by a dashed edge.

Worked example: [cheese-example.draft](cheese-example.draft).

Then, by hand:

- **Write the subtitle** as the finding, about ten words: "A retry can store the same rows twice". The script's fallback subtitle is a placeholder; replace it, or set `subtitle` in the ledger and regenerate.
- **Name each slice** after the defense, not the code: "Retry", "Storage".
- Keep the condition text short (two to six words before the `\n`); the band goes on the second line.

## Copy rules

Byron reads the title and subtitle first, so they carry the finding.

- The title names the thing; the subtitle says what you found. Never describe the drawing ("this diagram shows", "left to right, the holes…").
- No words from the brief ("overview", "at a glance", "takeaway") and no filler (robust, comprehensive, seamless, crucial, potentially).
- Every reference carries its meaning: name the change next to its issue number.
- In Byron's planning workspace, `npm run lint -- <file.draft>` checks the worst of these; passing it is the floor.
