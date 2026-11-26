# Study prompt template

The first Pro run on a target, in a new chat. Replace every `<…>`. Delete a section only when it truly does not apply. Target prompt length, with the output contract pasted in: about 1,500–2,000 words. The Srcly Study was 3,500 words; the extra length bought breadth that later runs did not use. The output should be the opposite: as long as the dossier needs.

````markdown
# Hands-on evaluation of <product> — <feature or workflows>

**The decision I want:** <one question Byron will act on>. Options in view: <A>, <B>, <a correctness fix you discover>, or something else. End with a recommendation I can turn into one PR.

<product> is <one sentence: what it is and who uses it>. The question users bring to <target> is: **"<real user question>"**. I want to know how well it answers that question with evidence a developer can trust, and where it breaks.

Run a **60–75 minute browser-based investigation**. Actually use the product. Don't stop when the known happy paths pass; spend the extra time on adversarial controls and the first place each workflow breaks. Don't pad the run or claim time you didn't spend. Record start and end times for each phase.

## 1. Build and baseline · about 10 minutes

Get the source: <either "Clone https://github.com/<owner>/<repo> and check out **<full SHA>** detached." or, for a private repo, "The repo is private: https://github.com/<owner>/<repo> at **<full SHA>**. A plain clone will fail; use your GitHub connector to fetch the tree and blobs at that SHA, rebuild the checkout, and verify the commit hash. Record how you did it."> Run it from source with these commands (verified from a cold start on <date>):

```bash
<verified run sheet: clone, bootstrap, start API, start client, health check>
```

The app is ready when <curl or screen that proves it>. Run the database, the app server, and the browser in one shell session; separate sessions can't reach each other's localhost. Work entirely inside your own sandbox. Clone, install, build, and run the app there, and drive it with your own browser (your cloud browser, or headless Chromium through Playwright that you install). Do not use Chrome integration, a browser connector, connected apps other than GitHub for the source, or anything on my machine, even if one is offered or appears to work. If setup fails, solve it yourself inside the sandbox and record what you did; setup fixes are findings about the product's setup, not blockers. Record the SHA you tested, the runtime versions, the browser, and whether the checkout stayed clean. Put mutable fixtures in separate copies.

If the build, a fixture, or the browser is unavailable, say exactly what is missing and which claims it blocks. Don't substitute a code review for a browser run.

Fixtures with known ground truth: <paths or how to make them>. Independent oracles: <git, rg, a runtime script, the API at …>.

## 2. Map what exists · about 10 minutes

Map the visible entry points from the running UI only; don't read the README or docs yet, so you meet the product as a new user does. After the tasks in section 3, use docs and source to classify each capability in <list 4–8 capabilities>: implemented and working / implemented but hard to use / implemented but broken / partial / not implemented. Missing functionality is not a UI bug.

## 3. Real tasks · about 25 minutes

Run these tasks as a competent developer who has never seen <product>. For each: state the objective and what success proves, attempt it in the UI **before** reading code or docs about it, record where you hunted, guessed, or got blocked, then check the result against an oracle.

1. **<T1 id> — <title>.** Start at <entry>. Goal: <verifiable outcome>.
2. **<T2 id> — <title>.** …
3. **<T3 id> — <title>.** …
4. **<T4 id> — <title>.** …
5. **<T5 id> — <title>.** …

<5–8 tasks. Each starts from where a user really starts, and ends in a checkable fact.>

For every claim, keep apart what the UI showed and what you learned from reading code, the API, or Git.

## 4. Try to make it give a convincing wrong answer · about 20 minutes

A plausible wrong answer matters more than a noisy layout. Build small controls in fixture copies and check each against its oracle:

- **<pattern 1>:** <control and ground truth, without the expected UI result>
- **<pattern 2>:** …
- **<pattern 3>:** …

Also test one honest-limit case: <opaque or unsupported input>. A precise "I can't establish past here" with a clickable last step is a good result; a blank panel, a crash, or a confident claim is not. A missing value is not a zero.

## 5. Synthesis · about 5 minutes of the run, plus packaging

Rank the work as **fix now / shape next / defer**. Correctness defects outrank usability friction, which outranks polish. Consolidate findings that share a root cause.

## Severity

P0: seriously misleading results or a core workflow that fails. P1: a common task blocked. P2: recurring friction or an important gap. P3: polish.

<paste the block from output-contract.md here>

## Limits

Don't change <product>'s code, commit, open issues or PRs, or publish anything. Out of scope: <features>. No invented screenshots, timings, or results; unmeasured values are null. Don't describe this as research with real users. Codex or Claude will check your results against the code and do all repository work.

Proceed on your own. When information is incomplete, make a reasonable call and record it.
````

## Notes for filling it

- Tasks: pick them from the target card's user questions. A good task starts from what the user sees (a rendered value, a changed line, an error) and ends in a fact an oracle can check.
- Keep Byron's hunches out of sections 3 and 4. Add them, if at all, as "areas I'm unsure about" after the deliverables, so Pro attempts first.
- For a **project** target with no chosen workflow, pick the two or three workflows the README leads with and say so in the decision line.
