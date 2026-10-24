---
name: transcripts
description: Single entry point for Byron's voice-memo transcript archive (v2ctx, `~/.v2c-voice-memos`). Ingests new Apple Voice Memos with local speech-to-text, runs the LLM summaries, starts the voice-to-context review viewer, refreshes the hub indexes, and searches, reviews, or synthesizes what he said. Use when Byron says `/transcripts` or `$transcripts`, "refresh transcripts", "load new transcripts", "process my voice memos", "run speech to text", "run the transcript LLM processing", "open/start the voice memo viewer", "review the transcripts about...", "what did I say about...", asks whether a topic or project appears in his transcripts, or wants themes, decisions, requirements, opportunities, or changes of thinking recovered from voice memos.
---

# Transcripts

“The transcripts” means the full archive at `~/.v2c-voice-memos` unless Byron
names another source. Do the work yourself and never hand Byron commands to
run.

Every operational step goes through one script:

```sh
~/.agents/skills/transcripts/scripts/transcripts.sh {refresh|viewer|status}
```

## Why it runs through iTerm

macOS lets an app read the Voice Memos container
(`~/Library/Group Containers/group.com.apple.VoiceMemos.shared`) only if that
app has Full Disk Access. On Byron's Mac, **iTerm has it. Claude, Codex, and
Terminal.app don't**, and running outside the agent sandbox doesn't help. If
you run `v2ctx voice-memos` directly, it fails with `EPERM` / "Could not
auto-detect an Apple Voice Memos folder". The script avoids this: it writes a
`.command` file, opens it in iTerm, and blocks until iTerm writes the exit code.
The viewer's dev server starts in iTerm for the same reason, so its
**Refresh recordings** button works too.

`open -a iTerm` is blocked by the agent sandbox. Run `refresh` and `viewer`
with the sandbox disabled (Claude Code: `dangerouslyDisableSandbox: true`).
A refresh can take many minutes, so run it in the background and wait for the
completion notice. Don't poll it.

## What Byron asks for → what to do

Run one or more of these routines, depending on the request. With a bare
`/transcripts` and no topic, run **Refresh** and then **Viewer**.

### Refresh (ingest + speech-to-text + LLM)

Any wording like "refresh", "process my memos", "load new ones", "run the LLM"
authorizes both stages Byron normally starts from the app: **Refresh recordings**
and then **Run LLM on remaining**.

1. `transcripts.sh refresh`. It runs `v2ctx voice-memos --run-llm --no-open`
   from `/Users/byronwall/Projects/hub` in iTerm. The run is idempotent: it
   skips completed work and uses the saved defaults in
   `~/.v2c-voice-memos/llm-settings.json`. When v2ctx succeeds, the script then
   runs `node scripts/refresh-indexes.mjs`.
2. The script prints the packages processed in this run plus the v2ctx summary
   (advanced / complete / waiting / failed). Report a table of new memos with
   date, length, and title. Read each title from
   `<package>/analysis/transcript-summary.json` (`.title`) and the length from
   the last cue in `transcript/transcript.srt`. Report the LLM cost (sum the
   `LLM total … cost=` lines in the log) and any failed packages with the
   reason.
3. Exit codes: `4` = iTerm lost Full Disk Access (tell Byron which folder
   failed; don't try other terminals). `3` = timed out. Any other nonzero value
   = a v2ctx or index failure. Never call the refresh a success when the exit
   code is nonzero. The full log is at
   `~/Library/Caches/v2ctx-transcripts/refresh.log`.

Use `--force`, `--force-analysis`, or `--reset-analysis` only when Byron asks
to rebuild or repair existing output, for example a package that keeps failing
with "No transcript found". Don't change the saved LLM settings unless he asks.
Known permanent failure: `20260628-142357-34FE2496-context` has an empty
`transcript/` folder. Mention it only if it's still failing and he asks.

### Viewer

1. `transcripts.sh viewer`. If something already answers on port 5173, the
   script reuses it. Otherwise it starts the app from
   `/Users/byronwall/Projects/video-to-context/app` (Vite + Solid) in iTerm.
2. Show it to Byron: in the Claude desktop app, open it with the built-in
   browser (`preview_start` with `url: http://localhost:5173`). Elsewhere, give
   him the URL. To open a specific memo, use
   `http://localhost:5173/?transcript=<package-name>&view=review`. After a
   refresh, open the newest memo.
3. Don't start the viewer with `preview_start` + a launch.json, `npm run dev`
   from the agent shell, or anything else that leaves Claude as the parent
   process. That server can't read Voice Memos, so its Refresh button fails.
   If a server like that is already holding port 5173, stop it, then run
   `viewer`.

### Status

`transcripts.sh status` prints the package count, the newest package, whether
the viewer is up, and the last refresh's exit code. Use it to answer "is the
viewer running?" or "when did I last refresh?".

### Search and review

1. Work from `/Users/byronwall/Projects/hub`. Run
   `node scripts/refresh-indexes.mjs` to discover newly added or partially
   analyzed transcript packages. This step is local and free.
2. `node scripts/search-transcripts.mjs "<topic or project>"`. If the wording is
   broad or ambiguous, also run one or two searches on synonyms, project names,
   or adjacent concepts. Don't ask Byron to write search syntax.
3. Read the full `transcript/transcript.txt` for the strongest matches. Use
   `analysis/transcript-summary.json` and `indexes/transcripts.md` for routing
   and cross-reference only, never as a substitute for the transcript itself.
4. Answer directly. Cite the dated transcript files with clickable absolute
   paths. When the viewer is running, you may also link
   `http://localhost:5173/?transcript=<package>&view=review`.

When Byron asks to refresh and then search, finish **Refresh** first and search
the regenerated index.

## Synthesis rules

- Include every clearly relevant memo, not just the highest-scoring result.
- Separate recurring ideas from one-off speculation.
- Keep meaningful differences, contradictions, and changes over time.
- Mark what Byron committed to, what he only considered, and what is still an
  open question.
- When the request names a project, check its project cross-reference and
  nearby related memos even if the exact repository name never appears.
- Say when a match is weak, inferred, or based only on raw transcript text.
- Don't run paid, provider-backed analysis for a search-only or review-only
  request. Run it only for a refresh, ingestion, or LLM-processing request.
- Don't copy or modify transcript source files.

## Response shape

Lead with the answer, not the search process. For a refresh: a table of new
memos, then cost, failures, and the viewer link. For a simple lookup: a short
list of relevant memos and why each matters. For a review: a compact synthesis
followed by the source memos. Mention archive or index gaps only when they
affect confidence.
