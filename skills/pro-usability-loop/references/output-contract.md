# Output contract

Insert the block below into the **Deliverables** section of either template. Replace `<slug>` with the run's slug (for example `srcly-compare`). Keep the block whole: it is the one source for the dossier, the files, and the case schema.

````markdown
## Deliverables

**The main deliverable is the context dossier, `<slug>-context.md`.** Write it for an engineer or coding agent who has not seen this run and will build the next PR from it. Long and dense is the goal. Be exhaustive and include every detail that would save the next agent time; never shorten it to save space. If an earlier dossier exists in this chat or is attached, update it instead of starting over, and add a section **Changes since the last run** (confirmed, corrected, new).

Sections:
1. **Run narrative.** What you did, in order, with times: setup, each task, each control, each detour. Include failed attempts and dead ends, and what each taught.
2. **How the system actually works.** Architecture, the path from UI to backend and back, where state lives, key functions and contracts between layers, with `path:line`. Mark confirmed versus inferred.
3. **What went well.** Each working workflow, why it works, and its witness. These must survive later changes.
4. **What went badly.** Each failure, wrong answer, and friction point, with its root cause as far as you traced it, the code location, and your confidence.
5. **Setup and environment.** Exactly what a clean build and run took: missing, slow, or flaky steps, and the fix for each.
6. **Gotchas and surprises.** Behavior that differs from the docs, misleading names, places where two views or code paths disagree.
7. **Fixtures and controls.** Each one you built, what it tests, its ground truth, and how to recreate it.
8. **Open questions.** What you could not settle, what evidence would settle it, and what you would test with another hour.
9. **Ideas.** Product and engineering ideas, each tied to the observation that suggested it, ranked.

**Write as you go.** Append to the dossier at the end of each phase, so nothing is lost if the run is cut short. Post a dense progress update in chat after each phase too (numbers, witnesses, corrections). Before your final answer, check that the ZIP contains the dossier and every file below, and link the ZIP in chat.

**Your sandbox files are deleted minutes after you finish, so the chat is the only lasting record.** Make the final message stand on its own: include the full text of `<slug>-report.md` inline, not only a link. If you can save files to my ChatGPT Library, save the ZIP there too and say so.

Other files, all in one ZIP and each linked in your final message:
- `<slug>-report.md`: the verdict, the capability map (Study), the old → new case table (Probe), ranked findings with case IDs and witnesses, the next PR, and what you would leave out. Refer to the dossier for the narrative; do not repeat it.
- `<slug>-results.json`: one row per case in the schema below. This is the reusable suite: the next run replays cases from it.
- `REPLAY.md`: exact commands to rebuild the app, recreate every fixture (with hashes), and rerun every oracle, from a fresh directory.
- `evidence/` and `evidence-index.md`: each witness file with a one-line caption. Prefer text witnesses (exact lines, API bodies, command output) to screenshots. Keep all files the report and REPLAY link to at their relative paths.

In chat: a one-paragraph verdict; the three most important findings, each with its exact witness; **one next PR** with its title, narrow scope with file paths, and the smallest acceptance test that could falsify it; whether I should do more fixes, more testing, or product work; and the ZIP link.

Rank work as **fix now / shape next / defer**. Correctness defects outrank usability friction, which outranks polish. Group findings that share a root cause.

Results schema:

```json
{
  "schema_version": 1,
  "tested_build": "<full SHA>",
  "before_build": "<full SHA or null>",
  "checkout_clean": true,
  "minutes": { "total": 0, "browser": 0 },
  "verdict": "",
  "next_pr": { "title": "", "scope": "", "acceptance_test": "" },
  "cases": [
    {
      "id": "A04",
      "objective": "what a user tries to do",
      "fixture": { "root": "", "revision": "", "variant": null },
      "starting_state": "where the replay starts",
      "action": "what to do in the UI",
      "pass_condition": "the checkable fact that means success",
      "baseline_status": "success | friction | partial | blocked | not run",
      "current_status": "success | friction | partial | blocked | not run",
      "class": "correctness | usability | analysis-limit | setup | null",
      "history": "introduced | persistent | fixed | preserved | newly observed | not run",
      "observed_result": "what the UI showed",
      "learned_from_source": "what code, API or Git added",
      "witness": "rev:path:line, an evidence file, or a screenshot",
      "first_friction": "",
      "rank": "fix now | shape next | defer | none",
      "confidence": "high | medium | low"
    }
  ]
}
```

- Keep case IDs stable across runs. A new control gets a new ID; never reuse an ID.
- `success`: the bounded objective was met. `friction`: met with a significant detour. `partial`: an important part stayed unresolved. `blocked`: could not be done. `not run`: not attempted on that build.
- `class` is `null` when the case found no defect or limit. A `setup` case is never a product defect. Missing functionality is not a UI bug.
- `preserved` means a verified earlier pass still passes.
- Unmeasured values are `null`, never estimated.
````
