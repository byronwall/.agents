---
name: context-recorder-breakdown
description: Break down a Context Recorder session (a folder under ~/Movies/ContextRecorder/ with recording.mp4, marks, transcript, browser events and saved MHTML pages) into actionable output — an exhaustive categorized feedback list, fix-now changes plus a future-ideas doc, intent documents, or one Jira/Linear issue with annotated images. Scripted: `recorder.py` gives the tested host, environment, UTC window and folded browser problems, a coverage ledger of every sentence and mark, frames at any offset (joined sessions too), the on-screen text of each saved page, and the Observe revision, errors and slow spans for the session window. Use when Byron gives a ContextRecorder path ("Path = …/ContextRecorder/2026-…", "I recorded a session", "process my voiceover", "usability run", "walkthrough feedback") or a context-recorder-cloud link.
---

# Context Recorder breakdown

Byron records walkthroughs with Context Recorder (`/Users/byronwall/repos/context-recorder`; its README is the format spec). He narrates while he uses an app and presses a hotkey to mark moments. Turn the session into the artifact he asked for without losing a comment, and back each item with evidence: the image, the exact UI text, the code, and the telemetry.

## Run the scripts first

`R=~/.agents/skills/context-recorder-breakdown/scripts`, `SCRATCH=<your session scratchpad>`. SESSION is the folder or just its name (`2026-11-02_16-25-02`). Never write into the recorder folder.

```bash
python3 $R/recorder.py brief   SESSION                    # what was tested, env, UTC window, folded problems, marks with images
python3 $R/recorder.py ledger  SESSION > $SCRATCH/ledger.md   # every sentence in ~45 s blocks, ⚑ marks inline, problems per block
python3 $R/recorder.py pages   SESSION -o $SCRATCH/pages  # dialogs/alerts/menus open at each mark + DOM text files
python3 $R/recorder.py pages   SESSION --grep "no loaded rows"   # which marks show a string
python3 $R/recorder.py observe SESSION [--env NAME]       # deployed revision, warn/error logs, failed and slowest spans, with @offsets
python3 $R/recorder.py frame   SESSION 2:11 5:30 -o DIR [--burst 2]   # frames for unmarked moments or motion bugs
```

What each one settles:

- **brief** picks the tested host from Chrome clicks and navigation, so it ignores background tabs (a localhost app reconnecting every minute, Jira, Statsig). It maps the host to an Observe environment (`relationalai.up.railway.app` → `staging`, `localhost` → local, any other Railway host through the daily-planning instance inventory), lists the models visited, prints the segment table of a joined session, and lists errors, failed or slow requests and console errors/warnings on that host, folded with ×N. When a session has no Chrome events (joined sessions), it falls back to macOS context and labels it **UNRELIABLE**. That URL has twice named a different tab than the one on screen, so confirm it against the images.
- **ledger** is the coverage contract: write at least one item per block, or `none` and a reason. Byron often comments without marking, so unmarked blocks matter. Image paths are absolute; open them.
- **pages** reads the saved DOM (`pages/*.mhtml`) at each mark. Use it to quote the exact UI string ("This result has no loaded rows.", "Update failed"), to see what was open (dialog, menu, peek), and to grep the app source for that string. The DOM text includes text that CSS may hide.
- **observe** queries Rel app spans `41766875` and logs `43252774` for the session window ±1 min, with similar rows folded. Each first-seen time is shown as a session offset (`@10:41`), so it lines up with the ledger. Trace IDs are printed bare, which the plan viewer links. Spans carry no user, so match by time and route. If a query fails, it prints the command to adapt (OPAL help: `observability` skill).
- **frame** maps a session offset to the right source `recording.mp4`, even after cuts and joins. Use `--burst` (4 fps) for a before/after pair on motion bugs.

## Workflow

1. **brief**, then read Byron's request again. It sets the output shape, the categories, and any companion sources ("combine with Ilian's PR review", "check Observe", "file for Jeremy").
2. **ledger**: read every block. Draft one row per distinct comment: the offset range, what Byron said in his own words (cleaned up), what he expected, the ⚑ marks, and the images. Visible problems he didn't mention are "(seen, not narrated)". Comments without a mark get a `frame`.
3. **Open the images.** `image` already prefers Byron's own markup (`annotations/`); region `screenshots/` beat full `frames/`. Don't trust a mark's title; it's just the nearest sentence.
4. **pages** for exact strings and open UI. **observe** for anything about slowness, failures, wrong data or missing state. Both go in as evidence on the matching item.
5. **Map items to code** in `/Users/byronwall/repos/modeler` at the deployed revision (`git show <rev>`, not `main`). Read its `AGENTS.md` and skills first. Search for the exact strings from `pages`, the `aria-label` and selectors from `ledger`, and request routes (`/api/models/<model>/task/<uuid>/body`). Give `file:line` and mark each cause as verified or suspected.
6. **Answer open questions from sources.** Whatever the code and telemetry can't answer becomes a **telemetry gap** item: which span or attribute would have answered it.
7. **Fold in other feedback** if Byron asked for it (teammates' PR reviews, Slack, Jira). Dedupe against his items and credit each source.
8. **Write the output**, ending with a coverage line: "all N sentences in K blocks and M marks reviewed".

For sessions over ~10 minutes, run subagents in parallel: (a) code mapping, given the item list, revision and `pages` dir; (b) Observe deep dives, given the `observe` output, the UTC window and each item's `@offset`; (c) teammates' feedback. Keep the ledger and item list yourself.

## Joins for Modeler and the Rel app

| Host in brief | Where it ran | Telemetry |
| --- | --- | --- |
| `relationalai.up.railway.app` | Railway project `modeler`, env `staging` | `observe` (env `staging`) |
| other `*.up.railway.app` | the Railway env for that host, resolved from daily-planning `tasks/TASK-0059-assets/instance-inventory.md` | `observe` (or `--env` if the host isn't listed) |
| `localhost:<port>` | Byron's local server or worktree | `modeler/server/logs/redwood2_*.jsonl`, newest first (modeler `server-log-troubleshooting` skill) |
| AWS / ECS | `relapp-server`, plus browser spans `relapp-browser` (`rum.sessionId`), by `customer.id` | `observe` with a custom filter |

- **Revision:** use the `vcs.revision` that `observe` reports. Note it in the output, because items are against that build.
- **URL hash:** `#model=<MODEL>&layout=map|full&view=logical&modelVizSelection=<uuid>` tells you the model, the layout and the selected concept or question. Reopen the URL in the app to reproduce when an item is unclear.
- **Display vs model name:** the UI shows the ontology's display name (`OSI_FLIGHTS_INSTALL_MODE_LOGIC`), while URLs and Observe use the model (`FLIGHTS_REASONERS`). Name both once.

## Output shapes

- **Exhaustive feedback list** (usability run): numbered items grouped as broken, polish, unfinished, stop doing, start doing, found in telemetry, telemetry gaps, and what worked (keep these working). Each item: a bold one-line problem, one or two sentences of detail and cause, the offsets, image links, the source credit, and any existing PR or issue that already covers it.
- **Fix now + future ideas** (feedback on work in progress): implement the actionable items in the target repo, and collect the forward-looking ones in one future-ideas doc. Cite marks as `R<MMDD>-NNN @m:ss`.
- **Intent documents:** pass the ledger and items to `software-design-sleuth-full` as a raw source.
- **One issue** (`jira` skill, or modeler `create-linear-issues` for Linear): a standalone body with no local paths or task IDs, and only the most useful images, each annotated with `scripts/annotate.py`. Run `grid` to read pixel coordinates, then `render` a JSON spec with a caption bar and numbered boxes. Embed each image inline under its item, with the timestamp above it. For motion bugs, use a before/after frame pair, not a video attachment. For Jira image upload, see the memory note "Jira image embedding". File only when Byron says so.

**Where it goes:** the owning task's `tasks/TASK-NNNN-assets/` in daily-planning; create the task first if needed. Copy images in as `mark-NNN.<ext>` in a dated subfolder, and link the session folder, `session.md` and `viewer.html` by absolute path. Cloud copy: `exports/cloud.json` → `url`. Never write into the recorder folder or a repo checkout.

## Pitfalls

- Folder names are local time (US Eastern); `wallTime` and Observe are UTC. The scripts convert.
- Transcripts are Parakeet ASR and mangle names: "Alien" is Ilian, "Sourcely" is Srcly. Check names against daily-planning `reference/people/` before writing them.
- The browser log records failed or slow requests only, with no request or trace IDs. Join to Observe by time and route.
- A joined session's media and per-mark notes live in its source folders. Don't move or rename them.
- Don't drop low-signal comments to tidy the list. Byron wants exhaustive.
