# Probe prompt template

Every run after the Study. Send it **in the same chat** as the Study, so Pro can reuse its fixtures, revision pairs, ZIP, and results. Replace every `<…>`. Target prompt length, with the output contract pasted in: about 1,500–2,000 words. This is the shape of the Srcly run 3 prompt, which gave the best result in the chat.

````markdown
Continue the <product> evaluation in this chat. Run a **60–75 minute browser-based investigation** of <what changed: the fixes in #… / the new feature> and the workflows they are meant to unlock. This is not a rerun of the whole suite. Don't stop when the known happy paths pass; spend the extra time on adversarial controls, a second setting, and the first place each workflow breaks. Don't pad the run or claim time you didn't spend.

**The decision I want:** <question>. Options in view: <A>, <B>, a correctness fix you discover, or something else. End with a recommendation I can turn into one PR.

## 1. Build and baseline · about 8 minutes

- Fresh checkout of <owner>/<repo> at **<full SHA>** (<what it contains, e.g. "main after #459–#463">), or, for a private repo, fetched at that SHA through your GitHub connector as in the earlier run. Run it from source (database, server, and browser in one shell session):

  ```bash
  <verified run sheet>
  ```

  Record the SHA you tested, the runtime, the browser, and whether the checkout stayed clean. Put mutable fixtures in separate copies. Work entirely inside your own sandbox. Clone, install, build, and run the app there, and drive it with your own browser (your cloud browser, or headless Chromium through Playwright that you install). Do not use Chrome integration, a browser connector, connected apps other than GitHub for the source, or anything on my machine, even if one is offered or appears to work. If setup fails, solve it yourself inside the sandbox and record what you did; setup fixes are findings about the product's setup, not blockers.
- Baseline: the earlier runs in this chat (their ZIPs, dossier, and `results.json`), or the copies attached to this message. The immediate before-build is **<before SHA>**. Reuse the same fixture paths, anchors, and revision pairs. Keep case IDs; new controls get new IDs.
- Don't rerun the before-build in full. If you find a consequential failure whose history is ambiguous, replay that one case on it. Otherwise label it newly observed, not introduced.
- Attempt the browser workflows **before** reading the PR diffs or descriptions. Afterwards, use code, API responses, and Git to explain or falsify what you saw. If a browser, fixture, or build is unavailable, record which claims that blocks. No source-only substitutes for UI results.

## 2. Replay and try to break the fixes · about 20 minutes

Replay <case IDs>. Then try to make the build give a convincing wrong answer:

- **Wrong <source/history/revision>.** <Concrete replay steps and control, e.g. "compare the path set with Git, not just the total; open the exact historical witness and verify revision, side, path, line">.
- **Wrong <view/root/state>.** <Start from a different view than the happy path; same name in a second root; Back/Forward/refresh/shared link — record what survives for each piece of state separately; a controlled race if feasible, labeled as such>.
- **Wrong <evidence/completeness contract>.** <The claim the product makes and the control that would make it false; partial or unsupported cases must explain the limit, not fail blank or with an error>.

Spot-check <one or two passing case IDs> as preservation controls. Don't award a pass because the feature exists or CI is green.

## 3. The product opportunity · about 22 minutes

Start where a user starts: <the rendered value / the changed line / the error>, not the code you already know matters. Ask: **"<user question>"**. Try the natural UI first and log every fallback to source search. For each claim, separate what the UI proved from what you inferred from code.

Build a small falsification set in fixture copies:
1. **<pattern>** — <control and ground truth>.
2. **<pattern>** — …
3. **Honest stopping point** — <an opaque or unsupported upstream step>. Can the product name the last proven step and open its source without claiming the unknown?

For each case record: the nearest answer the UI showed, what it proved, the first widening or stop, the exact witness, and whether you could get back to your question. Then sketch the **smallest useful answer** the product could give using only evidence you observed. Mark any field that needs a new capability. If the evidence can't answer it, name one narrow handoff worth probing; don't assume a broader solver.

## 4. Second setting and decision · about 15 minutes

Repeat the user question in a second realistic setting: <a larger real checkout for a code tool; otherwise a second dataset, user state, or entry route>. Before opening the code, pick two realistic questions. Answer each with <product>, then with a plain independent reference (`rg`, Git, a query). Record time to first defensible answer if you can measure it, the detours, and the exact evidence. This is an expert walkthrough, not a benchmark. If this adds no evidence, spend the minutes on the highest-risk unresolved case instead. If a workflow is already good enough, say so.

<Optional: one design question the run should settle from observed behavior, e.g. "Should the filter live in the history entry, a session snapshot, or the URL? Decide from the return/share/refresh behavior you observe.">

<paste the block from output-contract.md here>

Keep correctness defects, usability friction, known analysis limits, and setup limits separate. Rank the work **fix now / shape next / defer**. A plausible wrong answer matters more than a noisy layout. A precise, clickable "I can't prove past here" can be acceptable.

Don't change <product> code, open issues or PRs, or publish a release. Out of scope: <features>. This run decides what to build; it doesn't build it.
````

## Notes for filling it

- Phases sum to 65 minutes; Pro used 63 in the Srcly run. Keep the sum between 60 and 75.
- Section 2's three "wrong" bullets come from [adversarial-patterns.md](adversarial-patterns.md). Pick the ones the fixes could have got wrong.
- Section 3 comes from the "shape next" item of the last run. Section 2 comes from its "fix now" items, now merged.
- A short Probe (one fix, one check) is allowed, but still give it minutes and a decision. Without them, Pro stops early (29 minutes in Srcly run 2).
