---
name: prepare-chatgpt-pro-repo-prompt
description: Create copy-ready, repository-grounded prompts for ChatGPT Pro to review, research, evaluate, or plan work in a software repository. Use when a user wants to hand a GitHub repository to ChatGPT Pro, Deep Research, or ChatGPT agent. Do not use when the user wants Codex to do the repository work directly.
---

# Prepare a ChatGPT Pro Repository Prompt

Produce a prompt that lets ChatGPT Pro begin with correct repository context. Make the prompt detailed enough to run without a second briefing.

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

Do not convert a review into implementation. Do not add commit, push, branch, or pull-request instructions without user authorization.

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

ChatGPT can read connected GitHub repositories. The GitHub app is read-only. Do not promise that ChatGPT Pro can write or commit through that connection.

When the user requests file changes or commits, add a capability preflight:

1. Confirm that the active environment has a writable repository checkout.
2. Confirm the exact branch and allowed paths.
3. Continue with mutation only when both checks pass.
4. Otherwise, return the complete artifact or patch in the response.
5. State clearly that no file or commit was created.

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

Return the new Markdown file link and a short summary. Include the full prompt in the response only when the user requests it or file creation fails.
