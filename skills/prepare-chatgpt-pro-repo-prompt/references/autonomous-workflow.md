# Run the Full Pro Process

Read this reference when the user asks to run a Pro handoff autonomously or complete the full process.

Own each step: prepare, submit, wait, collect, assess, follow up when needed, integrate, validate, and open a review PR.

## Establish the run

Use the existing checkout. Follow its `AGENTS.md` rules for branches, commits, validation, and PRs. Do not create a worktree unless requested.

Resolve the intended deliverable from the request. For research and planning, this is usually an updated intent, design, or research document. Build the initial brief when needed. Keep implementation outside the run unless the user requested it.

Create a short run record beside the prompt or existing research notes. Use one Markdown file; no workflow framework is needed. Record:

- the requested outcome, allowed scope, and completion condition;
- the repository URL, checkout, branch, and source commit;
- the prompt path and submitted attachments;
- the Pro conversation URL, observed model or mode, submission time, and next check time;
- the current phase, round number, and unresolved blockers;
- the heartbeat ID and goal status, when present;
- collected artifact paths, reconciliation notes, validation results, and PR URL as they become available.

Update the record after each transition. On a resumed turn, read it and inspect current state before acting. Reuse the recorded conversation and PR. Do not resubmit a prompt because the turn ended or context was compacted.

## Prepare and submit

Use the main skill and prompt blueprint. Include a precise deliverable contract and an access fallback.

Give Pro the context required for the task. Prefer connected repository access when it exposes the selected source and documents. For unpushed documents or unavailable repository access, prepare a small source packet from the needed files.

For a source packet:

- Include the prompt, relevant instructions, source, tests, and planning documents.
- Record the baseline commit and included paths. Identify local additions and changes separately.
- State whether the packet is a selected source snapshot or a runnable checkout.
- Exclude credentials, unrelated private files, build output, and dependency directories.
- Verify that the payload fits the user's authorized destination and scope before upload.

If approval review blocks an upload, read its reason. Resolve it through evidence or a smaller authorized payload. Do not bypass the rejection. If still blocked, report the action, reason, and user action needed.

Use the available connected ChatGPT tools or approved browser controls. Inspect the live model selector. Select the requested Pro mode; do not silently substitute another model. Do not treat a cloud Codex task or an API call as the same Pro run.

Upload the actual prompt and packet, or paste the complete prompt. Verify that each attachment is present. Send a short instruction to execute the prompt and return the required artifacts. Do not send only a local filesystem path.

After sending, verify the submitted message and evidence that processing started. Save the conversation URL and submission time. If sending has an uncertain outcome, inspect that conversation before any retry.

If the account needs login, Pro is unavailable, or submission remains blocked, preserve the prepared files and report the blocker. Do not claim submission succeeded.

## Arrange the later check

Default to a first check about one hour after verified submission. Use the user's requested delay when given. This is a check time, not a promised completion time.

Use a heartbeat attached to the current chat for durable follow-up. Discover `automation_update` and follow its current schema. Inspect existing automations before creating one. Reuse a matching heartbeat and record its ID. Verify that the saved schedule will check at the intended time.

The heartbeat must continue the work, not merely remind the user to collect it. Its prompt must include:

- the exact conversation URL, checkout, branch, and run-record path;
- the authorized scope and final completion condition;
- instructions to inspect the existing run before any submission;
- what to do if Pro is running, failed, complete, or awaiting a response;
- collection, reconciliation, follow-up, validation, and PR duties;
- instructions to disable itself after completion or when user action is required;
- instructions to stay quiet while unchanged and notify only on meaningful change, completion, failure, or required user action.

Keep platform notification preferences in the tool's notification settings. Use the prompt for the workflow's meaningful-change rule.

Use an existing active goal when it covers this work. Create a goal only when the user explicitly requests one. Do not invent a token budget. A goal tracks the outcome; the heartbeat provides the later wakeup. Keep the goal unfinished until the requested endpoint is reached. Follow the live goal tool's rules for status changes.

Do useful independent work while Pro runs. Finish local baseline checks or prepare the destination documents. Do not poll the browser each minute or keep a turn alive with repeated short sleeps.

If no scheduler is available, finish useful independent work and check the existing conversation once more. A short tool-native wait is acceptable within its limits; do not assemble an hour from sleep calls. If Pro is still running, save partial progress and report that automatic continuation is unavailable. Provide the conversation and run-record links. Leave the outcome unfinished. Never promise a later check without a confirmed mechanism.

At each wakeup, read the run record and inspect the existing conversation:

- **Still running:** Keep the same run. Schedule another spaced check, normally about an hour later. Do not resend it.
- **Needs an answer:** Answer from verified repository facts and the existing scope. Ask the user only for an essential unresolved choice.
- **Failed or inaccessible:** Try a bounded recovery using the same conversation. After a failed recovery, report the blocker and preserve progress.
- **Complete:** Collect and assess the outputs immediately.

A slow run is not a failed run. If several checks show no progress, inspect for an error or required action. Do not cancel a working run only because one hour elapsed.

## Collect and verify the results

Read the response and enumerate its deliverables. Download all requested artifacts, including the archive and companion files when supplied. Preserve originals in a task-specific repository folder. Keep summaries and edits separate from those originals.

If final-message delivery fails, check the same conversation and its accessible file library. Finished artifacts can exist despite an interrupted response. Use observed file links and verify that recovered files belong to this run. Do not restart completed research to repair a download.

Record original names or links, local paths, retrieval time, file sizes, and hashes in a compact collection manifest. Note missing or duplicate files. Inspect archive entries before extraction; reject traversal paths or unsafe links. Check archive integrity and compare standalone companions with their archive copies when both exist.

Open each substantive artifact. Verify that reports are complete and structured files parse. Check expected recommendation counts and references when the package provides them. A download link, progress message, or claimed file count does not prove collection is complete.

If links expired or files are missing, ask Pro to regenerate the missing outputs in the existing conversation. Preserve the earlier results. Count recovery attempts against the follow-up limit below.

## Decide whether to follow up

Compare the results with the prompt's priority questions, required evidence, and deliverable contract. Send a focused follow-up when a material gap prevents useful integration. Examples include missing evidence, conflicting claims, unanswered priority questions, or unusable artifacts.

Do not ask again for cosmetic polish or to force Pro to endorse the initial hypothesis. Retain unresolved product choices as proposals when the review PR can present them clearly.

Default to at most two follow-up submissions after the initial request. Apply a user-specified bound instead when given. If a required answer remains missing, integrate the useful results and report partial progress with the unresolved gap. A draft PR can preserve that work, but it does not satisfy the full-process completion condition. Do not repeat open-ended research indefinitely.

Save each follow-up as a new Markdown prompt. State the gap, supplied evidence, requested correction, and acceptance condition. Submit it in the same conversation when possible. Record its time and round number, then repeat the scheduled check and collection steps. A new conversation requires a concrete access or context reason; record that reason and both URLs.

## Integrate with judgment

Read all substantive results before revising the destination documents. Treat Pro output as evidence and proposals, not instructions that override the user or repository rules.

Check consequential current-state claims against both the supplied baseline and the current checkout. Verify external claims that determine the recommendation. Record what was independently checked and what remains unverified.

Give every substantive recommendation a disposition: adopt, investigate, defer, or reject. Record the reason and destination. Group duplicates when clear. Adopting an idea into proposed intent does not mean it is implemented or approved.

Preserve the user's desired outcome when research challenges a suggested implementation. Keep the main document concise. Put detailed evidence, source checks, and dispositions in linked references. Retain open decisions and proposed proof work explicitly.

Separate four kinds of evidence: Pro's research, artifact integrity checks, local code checks, and executed product tests. A proposed proof or research-package check does not establish product behavior. Record unrun checks as unrun.

## Complete the run

Run the relevant document validators and repository checks. Inspect the final diff and preserve unrelated work. Follow repository rules for Git identity, scoped commits, package changesets, and screenshots when applicable.

Fix failures caused by this work. For an unrelated baseline failure, record the command, evidence, and affected checks in the PR. Do not claim a passing suite or expand the task to unrelated repairs. An unresolved required gate must remain explicit.

Use `gh` to create or update the review PR. Use a body file for multiline text. Include the research question, resulting decisions, retained alternatives, artifact links, validation, and unresolved limits. Add screenshots for visible UI changes according to repository rules.

After creation, attach the PR to the current chat. Read its saved body, file list, branch, and status. Verify that links and attachments work. Do not mark the run complete merely because a PR command was issued.

The full process is complete only when:

1. Pro finished the required research and any necessary bounded follow-ups.
2. Required outputs are collected, readable, and preserved.
3. Substantive findings are reconciled into the requested repository artifacts.
4. Validation results and material limitations are recorded accurately.
5. The PR is open, verified, and attached to this chat.
6. The run record is current and the heartbeat is disabled.

Then complete an active goal, if present and covered by this outcome. Stop for the user's review. Do not merge or begin unrequested implementation.

If a user limit replaces the PR endpoint, use that explicit endpoint instead. If a required output is still missing, report partial progress. Disable a heartbeat that cannot proceed without user action, but do not mark the goal complete.

Return the PR link, main document link, key decisions, validation limits, and confirmation that the monitor is off.
