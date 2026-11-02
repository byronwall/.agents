---
name: context-recorder-breakdown
description: Break down a Context Recorder session (a folder under ~/Movies/ContextRecorder/ with recording.mp4, marks, transcript, browser events and saved MHTML pages) into actionable output — an exhaustive categorized feedback list, fix-now changes plus a future-ideas doc, intent documents, or one Jira/Linear issue with annotated images. One command (`recorder.py prep`) builds an evidence pack — a ledger of every sentence and mark with the on-screen dialog text, browser errors and the Observe spans and errors from that moment, plus the deployed revision, code anchors for what Byron pointed at, and the mark images — and `recorder.py check` proves every comment and mark was covered. Use when Byron gives a ContextRecorder path ("Path = …/ContextRecorder/2026-…", "I recorded a session", "process my voiceover", "usability run", "walkthrough feedback") or a context-recorder-cloud link.
---

# Context Recorder breakdown

Byron records walkthroughs with Context Recorder (`/Users/byronwall/repos/context-recorder`; its README is the format spec). He narrates while he uses an app and presses a hotkey to mark moments. Turn the session into the artifact he asked for, with every comment covered and each item backed by evidence: the image, the exact UI text, the telemetry and the code.

## The loop

```bash
R=~/.agents/skills/context-recorder-breakdown/scripts
python3 $R/recorder.py prep SESSION -o $PACK [--assets tasks/TASK-NNNN-assets/<name>-YYYY-MM-DD]   # ~10 s
# read $PACK/brief.md, then fill every block's "Items:" in $PACK/ledger.md
python3 $R/recorder.py check $PACK/ledger.md      # exit 0 = every block has an item, every mark is cited
```

SESSION is the folder or just its name (`2026-11-02_16-25-02`). `$PACK` goes in the session scratchpad. `--assets` copies the mark images as `mark-NNN.*` straight into the owning task's assets folder; without it they go to `$PACK/images/`. `prep` never writes into the recorder folder.

**What `prep` writes**

| File | Contents |
| --- | --- |
| `brief.md` | The tested host, picked from Chrome clicks (background tabs are ignored), mapped to its Observe environment (`staging`, a Railway env via the daily-planning instance inventory, or `local`). Also the UTC window, the models visited, a joined session's segment table, browser problems folded ×N, and every mark with its image path and the sentence it landed in. |
| `ledger.md` | The work surface. Transcript in ~45 s blocks with ⚑ marks inline. Under each mark: its image, the hovered selector, and **on screen** (the dialogs, menus and alerts open in the saved page, shown only when changed). Under each block: **browser** errors and slow requests, and **telemetry**: Observe ERROR logs, failed spans, and spans slower than 5 s (`--slow`), collapsed to the longest span per trace, with trace IDs. |
| `observe.md` | The deployed `vcs.revision`, then warnings and errors, failed spans and the slowest spans for the window, folded, with `@offset`s. Each section prints the OPAL it ran, so you can adapt it. |
| `code.md` | Every `aria-label` Byron pointed at, found in source: at the deployed revision, or in the worktree of a local dev server that is still running (found from its port), or `--repo`/`--rev`. Runtime-built labels resolve to their template (`Sort by ${…}`, `analysis-table.tsx:187`). |
| `pages/mNNN.txt` | The DOM text of each saved page. Grep these for exact UI strings, then grep the source for those strings. |

Spot tools: `recorder.py frame SESSION 2:11 [--burst 2] -o DIR` pulls frames from the right source recording, even in cut or joined sessions; use `--burst` for before/after pairs on motion bugs. `recorder.py pages SESSION --grep "no loaded rows"` lists the marks that show a string. `brief`, `ledger` and `observe` also run on their own.

## Filling the ledger

1. Read Byron's request again. It sets the output shape, the categories, and any companion sources ("combine with Ilian's PR review", "file for Jeremy").
2. Work block by block. **Open every image.** Your eyes beat the title, and `image` already prefers Byron's own markup. For each distinct comment, write one bullet under `Items:`: what Byron said and expected (his words, cleaned up), the cited marks as `⚑NNN`, and the evidence that explains it, taken from the on-screen, browser and telemetry lines in that block. A block with nothing actionable gets `- none: <reason>`. Visible problems Byron didn't mention go in as "(seen, not narrated)". Unmarked comments need a `frame`.
3. When telemetry contradicts Byron's guess, say so: "Observe shows there isn't one: …". Questions that the ledger, `observe.md` and the code can't answer become **telemetry gap** items, naming the span or attribute that would have answered them.
4. Map each item to code. Start with `code.md`, then grep the exact strings from "on screen" and `pages/` at the revision in the `code.md` header (`git -C ~/repos/modeler grep -nF '<string>' <rev> -- client server`). Give `file:line`, and mark each cause as verified or suspected. Read Modeler's `AGENTS.md` and skills before proposing fixes.
5. Fold in other feedback if Byron asked for it (teammates' PR reviews, Slack, Jira). Dedupe it against his items and credit each source.
6. Run `check` until it exits 0, then write the output from the filled ledger. End with the coverage line `check` printed.

For sessions over ~15 minutes, split the ledger's blocks among subagents. Give each the pack path and its block range, and have it fill only those `Items:` sections. You merge, dedupe and run `check`.

## Output shapes

- **Exhaustive feedback list** (usability run): numbered items grouped as broken, polish, unfinished, stop doing, start doing, found in telemetry, telemetry gaps, and what worked (keep these working). Each item: a bold one-line problem, one or two sentences of detail and cause, the offsets, image links, the source credit, and any existing PR or issue that already covers it.
- **Fix now + future ideas** (feedback on work in progress): implement the actionable items in the target repo, and collect the forward-looking ones in one future-ideas doc. Cite marks as `R<MMDD>-NNN @m:ss`.
- **Intent documents:** pass the filled ledger to `software-design-sleuth-full` as a raw source.
- **One issue** (`jira` skill, or modeler `create-linear-issues` for Linear): a standalone body with no local paths or task IDs, and only the most useful images, each annotated:

  ```bash
  uv run --with pillow python $R/annotate.py grid mark-004.png -o grid.png   # read box pixels off the grid
  uv run --with pillow python $R/annotate.py render spec.json               # caption bar + numbered red boxes
  ```

  Embed each image inline under its item, with the timestamp above it. For motion bugs, use a `frame --burst` before/after pair, not a video attachment. For Jira image upload, see the memory note "Jira image embedding". File only when Byron says so.

**Where it goes:** the owning task's `tasks/TASK-NNNN-assets/` in daily-planning; create the task first if needed. Put images in a dated subfolder (`--assets`), keep the filled ledger next to them as the evidence record, and link the session folder, `session.md` and `viewer.html` by absolute path. The cloud copy's link is `url` in `exports/cloud.json`.

## Pitfalls

- When a session has no Chrome events (older or joined sessions), the brief labels the host **UNRELIABLE**. It comes from macOS context, which has twice named a different tab than the one on screen, so trust the images.
- Spans carry no user, so other people on the same environment show up in telemetry. Match on time, route and what's on screen. Telemetry `@offset`s assume one continuous recording; for joined sessions, use the segment table in `brief.md`.
- The UI shows the ontology display name (`OSI_FLIGHTS_INSTALL_MODE_LOGIC`), while URLs and Observe use the model (`FLIGHTS_REASONERS`). Name both once.
- Transcripts are Parakeet ASR and mangle names: "Alien" is Ilian, "Sourcely" is Srcly. Check names against daily-planning `reference/people/`.
- `prep` without a session.json means the session wasn't processed: `python3 ~/repos/context-recorder/scripts/process_session.py <session>`.
- Don't drop low-signal comments to tidy the list. Byron wants exhaustive, and `check` enforces it.
