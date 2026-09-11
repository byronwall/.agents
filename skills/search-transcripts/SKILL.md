---
name: search-transcripts
description: Refresh, search, review, and synthesize Byron's living v2c transcript archive without asking him to run commands or identify files. Use when Byron says "refresh transcripts", "load new transcripts", "process my voice memos", "run speech to text", "run the transcript LLM processing", "review the transcripts about...", "find the relevant ideas in...", "what did I say about...", asks whether a topic or project appears in his transcripts, or wants themes, decisions, requirements, opportunities, or changes of thinking recovered from voice memos.
---

# Search Transcripts

Treat “the transcripts” as the complete current archive at
`~/.v2c-voice-memos` unless Byron names another source. Perform ingestion and
retrieval yourself; never give Byron commands to run.

## Refresh workflow

Treat “refresh transcripts” and equivalent requests as authorization to perform
both stages Byron normally starts from the app, in this order:

1. Load new Apple Voice Memos and run local speech-to-text.
2. Run provider-backed LLM processing for recordings that still need the
   augmentations enabled in the app's saved LLM settings.

From `/Users/byronwall/Projects/hub`, run:

```sh
v2ctx voice-memos --run-llm --no-open
```

This is the idempotent CLI equivalent of pressing **Refresh recordings** and
then **Run LLM on remaining**. It reads the saved defaults from
`~/.v2c-voice-memos/llm-settings.json`, skips completed work, and does not open
the report UI.

After it completes:

1. Run `node scripts/refresh-indexes.mjs`.
2. Check the v2ctx summary for advanced, complete, waiting, and failed counts.
3. Report what was processed and surface any recording-specific failures or
   permission problems. Do not claim the refresh succeeded if either v2ctx or
   index generation failed.

Do not use `--force`, `--force-analysis`, or `--reset-analysis` unless Byron
explicitly asks to rebuild or repair existing output. Do not change the saved
LLM settings unless he asks.

## Search and review workflow

1. Work from `/Users/byronwall/Projects/hub`.
2. Run `node scripts/refresh-indexes.mjs` to discover newly added or partially
   analyzed transcript packages.
3. Run `node scripts/search-transcripts.mjs "<topic or project>"`.
4. If the wording is broad or ambiguous, run one or two useful synonym,
   project-name, or adjacent-concept searches. Do not ask Byron to formulate
   search syntax.
5. Read the full `transcript/transcript.txt` for the strongest matches. Use
   `analysis/transcript-summary.json` and `indexes/transcripts.md` for routing
   and cross-reference, not as substitutes for the source.
6. Answer the request directly. Cite the dated transcript files with clickable
   absolute paths.

If Byron asks to refresh and then search or review, complete the refresh
workflow first and use the newly regenerated index for retrieval.

## Synthesis rules

- Include every clearly relevant memo, not merely the highest-scoring result.
- Separate recurring ideas from one-off speculation.
- Preserve meaningful differences, contradictions, and evolution over time.
- Distinguish what Byron committed to, what he considered, and what remains an
  open question.
- When the request names a project, inspect its project cross-reference and
  nearby related memos even if the exact repository name is absent.
- State when a match is weak, inferred, or based only on raw transcript text.
- Do not run paid/provider-backed analysis for a search-only or review-only
  request. Run it only when Byron explicitly requests a refresh, ingestion, or
  LLM-processing workflow as described above.
- Do not copy or modify transcript source files.

## Response shape

Lead with the recovered answer, not the search process. For a simple lookup,
return a short list of relevant memos and why they matter. For a review, provide
a compact synthesis followed by the source memos. Mention archive/index gaps
only when they affect confidence.
