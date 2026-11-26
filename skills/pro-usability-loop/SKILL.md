---
name: pro-usability-loop
description: Point ChatGPT Pro at a repository, project, or one feature for a 60–75 minute hands-on usability and evaluation run. Pro builds and runs the app in its own sandbox (no Chrome, no connectors), drives it in a browser, tries to make it give a wrong answer, checks claims against source and Git, and returns a long, dense context dossier, a verdict, a reusable case ledger, a replayable evidence ZIP, and one next PR with a falsifying acceptance test. Also runs the retest loop in the same chat after fixes land. Use when Byron says `/pro-usability-loop`, "run Pro on the UX of X", "Pro usability study", "Pro eval loop", "have Pro test feature Y", "retest with Pro", or "another Pro pass". For design, methods, strategy, or code-review handoffs with no hands-on run, use `prepare-chatgpt-pro-repo-prompt`.
---

# Pro usability loop

Pro is excellent at one job: run the product for an hour, find where it breaks or lies, prove it, and write down everything it learned. This skill sets up that run so all of Pro's time goes to the evaluation, and so each run feeds the next.

Two rules shape everything:

- **Pro lives in its own sandbox.** It clones, builds, runs, and drives the app with its own browser. Never Chrome integration, a browser connector, or anything on Byron's machine; the GitHub connector is allowed only to fetch a private repo's source. Pro solves its own setup problems.
- **Pro is a context machine.** After an hour of hands-on work it can write more dense, accurate context than any other agent. The decision is the headline; the **context dossier** is the main product.

The evidence for these rules is in [references/srcly-retro.md](references/srcly-retro.md) (Srcly, three runs) and the Family Finances retro (`~/Projects/planning/tasks/TASK-0076/pro-study-2026-11-23/retro.md`, the first run of this skill).

## The loop

- **Study:** the first run on a target, in a new chat. Wide on purpose. Builds the reusable case suite.
- **Probe:** every later run, in the **same chat** as the Study, so Pro can reuse its fixtures and files. Narrow, adversarial, ends in one decision. Open the saved chat URL directly. If you can't tell whether Pro still has the earlier files, attach the last dossier and `results.json`.

## How far to go

- "Draft" or "prepare": done when the prompt is saved.
- "Send": done when the sent message, the processing state, and the conversation URL are verified.
- "Run it" or "handle it": done when the results are saved and turned into work items (step 5).

A Pro message is scarce: one run is one message. Merging, deployment, and product code changes need a separate ask.

## 1. Target card

Four lines, plus one for a Probe. Fill the rest of the prompt from the repo (`AGENTS.md`, README, `scripts/`, tests, the planning task), not from Byron.

```text
Source:    repo URL @ full SHA (public, or private through Pro's GitHub connector)
Run:       the commands that start the app from a fresh clone, and the entry URL
Question:  the question a user brings to this target ("which value produced this field?")
Decision:  what Byron will decide from the run ("fix Compare state or build field-producer UI?")
Baseline:  (Probe) before-SHA and the case IDs to replay
```

For a **feature**, name its routes and two or three real user questions. For a **project**, pick the two or three workflows that matter most; with none chosen, a Study gives breadth and no decision.

Save everything for one run in one folder: `tasks/<TASK>/pro-<study|probe>-<date>/` in the planning repo, or the repo's research folder when there is no task.

## 2. Make the source reachable and the start cold

- **Public repo:** push the SHA. In a scratch folder, clone over HTTPS, check out the SHA, and run the Run line exactly. Fix the commands until a cold start reaches the entry URL with no hand edits.
- **Private repo:** push the SHA. Pro's plain `git clone` fails (no credentials), but its GitHub connector works: in the Family Finances run Pro fetched the tree, the commit, and all 293 blobs, rebuilt the checkout, and verified the commit hash. Tell Pro to do exactly that. It gets one commit, not history; name every SHA a case needs. Don't upload a bundle of a private repo (blocked as a data-leak risk).
- **Local-only repo:** push it to a private GitHub repo first.
- Reuse a run sheet you verified on an earlier run when the setup, dependencies, and entry route have not changed.
- A setup defect you find is a finding for the prompt (with its workaround), not a detour.
- Never send real credentials. Give Pro seed data or a local stand-in.

## 3. Write the prompt

Start from [references/prompt-study.md](references/prompt-study.md) or [references/prompt-probe.md](references/prompt-probe.md), and paste [references/output-contract.md](references/output-contract.md) into its Deliverables section. The templates already carry the moves that worked:

1. The decision question first, with the options in view.
2. Timed phases that sum to 60–75 minutes, plus "don't stop at the happy paths" and "don't pad". Without minutes, Pro stopped at 29.
3. The sandbox-only paragraph.
4. UI first, then source: attempt in the browser before reading code or docs, and keep apart what the UI showed and what the code added.
5. "Try to make it give a convincing wrong answer", with two or three patterns from [references/adversarial-patterns.md](references/adversarial-patterns.md).
6. The output contract: the long dossier, written as Pro goes, plus the case JSON, REPLAY, and one next PR.

Keep the *prompt* plain: cut anything that does not change what Pro does. Never ask for short *output*.

Check before sending: decision first; minutes sum to 60–75; the source line works cold; Probe case IDs named; no hunches or expected results before the "attempt first" line; no placeholders or secrets.

## 4. Send, wait, collect

Use `prepare-chatgpt-pro-repo-prompt`'s [Chrome workflow](../prepare-chatgpt-pro-repo-prompt/references/chrome-workflow.md) only for the mechanics: open ChatGPT (or the saved chat for a Probe), check **Pro** in the model selector, attach files, send, verify, and download. Make sure no connector or tool is turned on in the composer. This is Claude's delivery channel; Pro's run stays in its sandbox.

**Collect the moment it finishes.** A file link works only for a short time after the message that created it. In the Family Finances run every link returned `404 File not available` about 6 minutes after Pro's final message, although the files were still in Pro's sandbox. So check every 5 minutes from about minute 55 (session `CronCreate` `*/5`, deleted once collected), and on the first finished check download the ZIP before reading anything. A run that is still working is not a failed run.

If the links already return 404, the files are usually still there. Send one short message in the same chat: "Your download links expired. Re-link the ZIP and every deliverable in a new message; don't redo any work." The new message's links work; download them at once. That recovered the full ZIP 26 minutes after the run ended.

Extract the ZIP into the run folder (check for absolute or `..` paths first). Keep everything at its relative path, so every link in the report and every REPLAY input still resolves. Commit the extracted files; keep the ZIP itself out of git. Also save the chat text (expand the collapsed sections, then `innerText` of `main`) as `chat-transcript.md`: it is the only record that never expires.

If even re-linked files are gone, ask Pro to re-emit the dossier inline. Never follow up for polish or length.

## 5. Turn the run into work

1. Copy the dossier to `tasks/<TASK>/<product>-context.md`, one cumulative file per product. Every worker prompt from this run starts with "Read `<that path>` first."
2. Check the next-PR finding on current `main` (the named file and lines, or a quick replay). `main` may have moved since the tested SHA.
3. Add work items grouped by root cause, with Pro's case IDs: `- W18: Declaration-only callee shows Closed (Pro probe 3, A04) [open] {pr, S}`. Copy Pro's acceptance test into the next-PR item. Mark it "Pro's pick"; Byron decides.
4. Log the run under `## Updates`: SHA, minutes, old → new counts, verdict, link.
5. Save a draft of the next Probe beside the run, while the context is fresh. Send it after the fixes land.
