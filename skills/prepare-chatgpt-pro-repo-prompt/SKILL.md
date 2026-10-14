---
name: prepare-chatgpt-pro-repo-prompt
description: Prepare repository-grounded ChatGPT Pro prompts or run the full autonomous Pro process through submission, later collection, follow-up questions, result integration, and a review PR. Use for repository work handed to ChatGPT Pro, Deep Research, or ChatGPT agent, including requests to run that handoff autonomously. Do not use for direct Codex work that does not involve a Pro handoff.
---

# Prepare or Run a ChatGPT Pro Repository Handoff

Prepare a prompt that gives ChatGPT Pro correct repository context. When requested, own the process through a review PR.

## Choose the extent of the work

Keep the task mode separate from how much of the process Codex will run.

- **Prompt only:** Requests to prepare, draft, or write a prompt end with the saved prompt and its link.
- **Submit only:** An explicit request to send the prompt ends after verified submission, unless later steps are also requested.
- **Full process:** In a Pro handoff, “run autonomously,” “handle the whole thing,” or similar language selects the complete process.

The full process is: prepare prompt → submit to Pro → check after about one hour → collect results → follow up if needed → integrate results → open a PR.

For full mode, read [the autonomous workflow](references/autonomous-workflow.md) before submission. That reference defines persistence, recovery, follow-up limits, and completion checks.

A full-process request authorizes these steps within the requested topic, including scoped commits and the push needed for the PR. It also authorizes sending the prompt, necessary source context, and bounded follow-up questions to Pro. Do not ask for permission again at each step. Apply any narrower user limits.

### Standing approval for Pro asset downloads

Byron authorizes autonomous downloads of all task-related assets from the Pro session started for an authorized handoff. This includes reports, archives, companion files, data, images, and regenerated outputs in the same run. It also covers those assets through the session's previews and file library.

Download, save, inspect, hash, and safely extract these assets without asking for approval again. This approval persists across collection turns and scheduled checks. Cite the recorded conversation and this standing instruction when a tool reviews a download.

This authorization covers collection, not execution of downloaded programs, unrelated files, or expanded sharing. Respect tool-enforced approval decisions. If a review blocks an authorized download, supply the recorded session and scope as evidence before retrying. Do not bypass the review.

For research, review, or planning, integrate results into the relevant repository documents. Application implementation requires that scope in the request. The default endpoint is an open review PR. Merging, deployment, and unrelated changes need separate authorization.

An update to this skill does not start a research run. Only operate a live run when the current request calls for one.

## Browser for Pro submission

Use Byron's signed-in Google Chrome profile for Pro handoffs unless he requests another browser.
Read [the Chrome workflow](references/chrome-workflow.md) before browser submission or collection.
The task's in-app browser can have a separate signed-out session; it does not establish that Chrome needs login.

## Ground the prompt first

Inspect the local repository before drafting.

- Resolve the exact repository path.
- Read the applicable `AGENTS.md` files.
- Read the README, package manifest, and relevant design documents.
- Inspect the current branch, status, remotes, and recent commits.
- Identify the files, tests, commands, and prior findings that matter.
- Convert an SSH Git remote to its full canonical HTTPS repository URL.
- Use actual paths and commands. Do not invent either one.

If the local checkout is unavailable, use the information the user supplied. Mark all unverified repository facts as assumptions.

## Select the task mode

Classify the requested handoff before writing the prompt.

- **Review:** Analyze the current design, code, product, or documentation.
- **Research:** Compare approaches and produce evidence-backed recommendations.
- **Evaluation loop:** Test bounded hypotheses against measured acceptance gates.
- **Artifact production:** Create a report, brief, plan, or other named deliverable.
- **Mutation:** Change files or Git state only when the user explicitly requests it.

Do not convert a review into implementation. In full mode, Codex owns local integration and the PR. Keep Pro focused on its assigned task. Prompt-only work does not authorize sending messages or changing Git state.

## Build the prompt

Read [the prompt blueprint](references/prompt-blueprint.md). Use the sections that fit the task. Keep all important repository facts in the final prompt.

The final prompt must include:

- the full canonical HTTPS GitHub URL;
- the target branch or ref when it matters;
- one primary mission and its decision context;
- the priority questions in ranked order;
- actual repository files and commands to inspect;
- evidence rules for facts, inferences, and recommendations;
- explicit scope and non-goals;
- detailed GO, NO-GO, and stop conditions;
- success checks that match the task;
- the exact deliverable, path, format, and response summary;
- a fallback when repository access or write capability is absent.

Use repo-specific detail. Do not leave bracketed placeholders in the copy-ready prompt.

## Save the generated prompt

Save the ChatGPT Pro handoff prompt itself as a new Markdown file. Do this unless the user explicitly requests another format, location, or conversation-only output.

- Put the file in the repository that the prompt covers.
- Prefer an existing prompt, research, or documentation folder.
- Choose a clear, task-specific filename.
- Create a new file. Do not overwrite an existing prompt.
- Include the complete copy-ready prompt in the file.
- Return a clickable link to the new file.

If the repository is not writable, provide the complete prompt in the response. Also give a suggested Markdown filename and state that no file was created.

## Handle GitHub access correctly

Use connected GitHub access when available. Check the active tools; do not assume a repository connection provides a writable checkout.

If Pro cannot access the selected ref, provide an authorized source packet or report the access limit. A local file is not visible to Pro until uploaded or otherwise made accessible. See the autonomous workflow for packet guidance.

When Pro is assigned file changes or commits, add a capability preflight:

1. Confirm that the active environment has a writable repository checkout.
2. Confirm the exact branch and allowed paths.
3. Continue with mutation only when both checks pass.
4. Otherwise, return the complete artifact or patch in the response.
5. State clearly that no file or commit was created.

This preflight applies to Pro's assignment. Codex can still integrate returned research locally when full mode authorizes that work.

## Preserve repository safety

For authorized mutation work, include the repository's actual safety rules. Cover dirty files, allowed paths, package manager, validation commands, Git identity, staging scope, commit rules, and push limits when they apply.

Never let the prompt treat a dirty worktree as disposable. Never authorize destructive Git commands by implication.

## Check the final prompt

Before delivery, confirm all items below.

- The URL names the correct owner and repository.
- The prompt separates repository facts from hypotheses.
- The required reading list uses real paths.
- The main question is more prominent than secondary questions.
- Each recommendation must cite repository evidence.
- GO and NO-GO rules can change the outcome.
- Validation can reject a weak result. It does not only confirm success.
- The new Markdown prompt file and fallback are unambiguous.
- Mutation instructions match the user's authorization and available capability.
- The prompt contains no unresolved placeholders.

For prompt-only work, return the Markdown file link and a short summary. Include the full prompt only when requested or file creation fails.

For full mode, keep working until the [completion checks](references/autonomous-workflow.md#complete-the-run) pass or a stated blocker requires user action. Saving or submitting the prompt is an intermediate step.
