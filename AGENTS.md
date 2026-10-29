# Global instructions

This file is the one source for Claude and Codex. `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` are symlinks to `~/.agents/AGENTS.md`. Edit only this file. Sections marked "Codex only" do not apply to Claude.

## Shell

- Edit source with your file-edit tool. A scripted replace (`python3`, `sed`, `perl`) must assert its match count, so a stale match fails instead of exiting 0 with nothing changed.
- The shell is zsh. Quote globs in arguments (`grep --include='*.ts'`), pass file lists as arrays (`files=(a b); cmd "${files[@]}"`), and don't start an `echo` argument with `=`.
- zsh reads `$var:r`, `$var:h` and similar as modifiers. Write `${var}:` when a colon follows a variable.
- macOS has no GNU `timeout`. Use the tool call's own timeout, or `gtimeout` if it is installed.
- `git cherry-pick` has no `-q` flag; with it, nothing is picked.
- Wait on a background job through its exit notice or a file it writes, not `pgrep -f <pattern>`. The waiting shell's own command line contains the pattern, so `until ! pgrep -f ...` never ends.
- Unset `GIT_DIR` and other `GIT_*` variables before a git hook runs tests. Otherwise a test's `git init` or commit acts on the real repository.

## Project scale and implementation

- Byron is a personal developer who mainly builds personal projects.
- Assume most projects have no users and can be discarded unless evidence says otherwise.
- Choose the simplest implementation that solves the current problem.
- Do not add enterprise patterns or production safeguards because they sound useful.
- Assume one server, one client, and one deployed version unless the project shows otherwise.
- Do not add mixed client/server fallbacks, backward compatibility, or version coexistence support by default.
- If omitting that support seems unsafe, ask Byron before adding it.
- Write few tests. Keep only tests that protect important behavior or likely failure points.
- Do not write tests that only repeat the current implementation or internal structure.
- Use concise variable names that keep their meaning clear.
- Prefer direct control flow and short call stacks.
- Avoid DTOs, normalization layers, and extra parsing unless they solve a concrete boundary problem.
- Prefer context or direct data pass-through when it stays clear.

## Codex task creation (Codex only)

- Create project tasks in the saved project checkout using the local environment.
- Never create a Git worktree unless Byron explicitly requests one.
- “Create a task/thread in the project” means the existing project directory, not a worktree.
- Create a separate Codex task only for a new orchestrator, an explicit request
  for a dedicated task, or a wholly new scope that needs independent ownership
  and history. Do not create a task for an ordinary worker on the current task.
- When Byron declares an orchestrator or invokes the `$orchestrate-work` skill,
  use a shared sidebar title system for it and each dedicated worker task:
  - Choose one emoji that meaningfully represents the orchestrator's work and is visually distinct from other active orchestrators.
  - Use that emoji as the family icon for the orchestrator and all of its workers.
  - Prefix the orchestrator title with `⭐ <family-icon> 00 · `.
  - Prefix worker titles with `<family-icon> 01 · `, `<family-icon> 02 · `, and so on, numbered by spawn order within that orchestrator. Workers do not get the star.
  - Keep the text after the prefix short and descriptive.
  - Apply the title as soon as the task's real ID is available.
  - Number parallel workers by spawn order, not completion order.

## Orchestration and workers (Codex only)

- An orchestrator task name starts with `⭐ <family-icon> 00 ·`. Treat this
  starred task name as the authoritative status at the start of every turn.
- For nearly every user message in an orchestrator, spawn a new collaboration
  subagent with empty context. Reuse an existing subagent only when its prior
  context is materially useful for the next step.
- Delegate substantive work by default, even when direct work would be faster.
- Keep direct orchestrator work to coordination, synthesis, worker review,
  small administrative actions, and urgent safety handling.
- If no useful worker scope exists or subagents are unavailable, work directly.
  State the applicable exception when no delegation occurs.
- Prefer delegation even when it takes longer. Byron accepts the extra time and
  expects the orchestrator to review work from smaller models.
- A task that is not an orchestrator can work directly unless another rule
  requires delegation.
- Use the orchestrator to separate implementation, verification, and follow-up work so each worker receives only the context needed for its role. Route findings and revisions through the orchestrator.
- Use collaboration subagents for bounded workers on the current task. This includes investigation, implementation, and verification.
- Unless Byron specifies otherwise, spawn each subagent with GPT-6 Luna at High reasoning. Give it only the context its role needs.
- When Byron asks a thread to spawn a new persistent orchestrator, create it
  with GPT-5.6 Sol at High reasoning. Never use GPT-6 Luna for that
  orchestrator.
- Default to a new subagent with empty context. Do not reuse a subagent only
  because it is available. Reuse it only when its prior context is materially
  useful, such as a focused repair of its own implementation.
- Do not create a dedicated worker task for work that remains part of the current task. Create one only under the task-creation exceptions above.
- If the current task remains responsible for the result, treat the work as a worker scope and use a subagent.
- If subagents are unavailable, do the worker scope locally or serialize it. Do not use a dedicated task as a fallback.
- When a dedicated worker task is justified, use GPT-6 Luna at High
  reasoning unless Byron specifies otherwise.
- Give Luna High workers a precise brief. Include the outcome, boundaries,
  evidence, acceptance criteria, checks, and report format.
- Review Luna High results against direct evidence. Use a separate verification
  worker when the risk or user-visible scope warrants it.
- Give each worker a clear and complete brief. Then let the worker finish without repeated messages or forced progress.
- Use long wait intervals. Do not poll, prod, interrupt, or redirect a worker only because it remains active.
- Intervene only when the worker requests attention, reports a blocker, fails, or runs well beyond the expected time.
- Keep all subagent work on GPT-6 Luna at High reasoning. Change the
  model only when Byron explicitly requests it.
- For browser verification, use a separate subagent whenever practical. Treat it as a clean-room, black-box verification pass rather than a continuation of the coding worker.
- Give the browser-verification worker the user-visible goal, acceptance criteria, starting URL or run instructions, relevant credentials or fixture guidance when authorized, and any known environmental constraints. Do not give it a source-code walkthrough, implementation explanation, or detailed hints about where bugs are likely to be.
- The browser-verification worker should avoid reading source code unless it cannot proceed otherwise. If it must inspect code, it should state why and distinguish observations made before and after that inspection.
- Treat difficulty discovering controls, navigating the interface, understanding labels, completing the flow, or operating it with accessibility-oriented interaction as product evidence. Do not coach the verifier around these problems merely to finish the test; report them as possible UX or accessibility defects with reproduction details.
- The orchestrator owns the feedback loop: dispatch implementation and browser-verification workers, pass verification evidence back to the coding worker, request focused fixes, and send the revised behavior back for clean verification. Keep those worker contexts separate while continuing the loop until the requested terminal condition is reached or user input is required.

## Skill copies

- Create new global skills in `~/.agents/skills/<skill-name>/`.
- Do not create global skills in `~/.codex/skills/` unless Byron explicitly requests that location.
- Use local `consider-contrast`, `impeccable`, and `write-byron-voice` skills from `~/.agents/skills/<name>/`.
- Do not use their Claude cloud copies under `~/.agents/skills/synced/`, even when the copies appear in the skill catalog.
- In Codex, keep these synced copies disabled by path in `~/.codex/config.toml`.
- Preserve Claude's synced files. If the sync bucket changes, update the disabled paths.

## Package management

- Always use pnpm for installing packages, managing dependencies, and running package scripts.
- Do not use npm or Yarn unless Byron explicitly requests an exception.

## Project technology

- Use TypeScript, TSX, and SolidJS for all new work in a project that has a
  `package.json` file.
- Treat a project with a `package.json` file as a real project, regardless of
  its size or expected lifetime.
- Simple `index.html` files and other single-file demos can use a smaller stack.
- Do not convert an existing project to this stack unless Byron requests the
  conversion.

## Git commits

- On a branch other than `main`, create small, coherent commits as work progresses.
- Use useful checkpoint commits instead of accumulating a large diff.
- On `main`, do not create routine progress commits. Commit on `main` only when Byron explicitly requests it.
- Before each commit, verify both Git identities are `Byron Wall <byron@byroni.us>`.
- Never use an agent, bot, Codex, or OpenAI identity for the author or committer.
- If either identity differs or is missing, set both identities for that commit. Do not change unrelated repository configuration.

## Multi-part work

- When a request has several separable pieces (a plan, "fix everything in this transcript", "10x these examples"), stack one PR per piece, with screenshots in each PR that changes UI. Open the first PR as soon as it builds, with `gh stack submit --auto`.
- Keep going through every piece without stopping to ask. Stop only for a product decision you can't make from the request, the code, or a sensible default.

## Stacked PRs

- "Stack PRs", "stacked PRs", or "a stack" means a real GitHub stack made with `gh stack`. A chain of PRs where each one targets the branch below it is not a stack.
- Use the `gh-stack` skill for the commands and their non-interactive forms.
- Build the stack with `gh stack init` and `gh stack add`. If the branches already exist, adopt them in order with `gh stack init <bottom> ... <top>`.
- Open and update the PRs with `gh stack submit --auto`. Do not use `gh pr create --base <other-branch>` for a layer. Fix titles and bodies, and attach screenshots, with `gh pr edit` after the submit.
- Keep the stack current with `gh stack rebase`, `gh stack push`, and `gh stack sync`.
- Merge with `gh stack merge <pr> --yes`. Do not use `gh pr merge` on a layer, and do not retarget a layer by hand with `gh pr edit --base`.
- Before you report, run `gh stack view --json` and confirm that every layer has a PR in the stack.
- If `gh stack` fails with exit code 9 (stacked PRs not enabled on the repository), stop and tell Byron. Do not fall back to a branch-to-branch chain without his approval.
- Repository docs mention stacks only for a real exception to these rules.

## GitHub pull requests and screenshots

- Use `gh` for GitHub PR creation, edits, and screenshot uploads. Do not use browser automation for these actions.
- Use `--body-file` for multiline PR descriptions.
- GitHub CLI 2.102.0 supports `--attach` on `gh pr create`, `gh pr edit`, and `gh pr comment`.
- Include screenshots in the PR description for every visible fix or UI change.
- Save screenshots under the project's `tmp/` folder. Upload them with `--attach`; do not commit screenshot evidence.
- `--attach` is the only upload path. Do not push screenshots to a separate assets branch, and do not ask Byron to drag files into the PR.
- Repeat `--attach` for up to 50 files per command. A file that the body does not reference is added to the end of the body.
- Match each Markdown image path exactly to its `--attach` path, relative to the shell working directory.
- Use `![alt](tmp/screenshot.png)` with `--attach 'tmp/screenshot.png#alt'`. Do not use `./` or only the basename.
- The body file location does not change the attachment path. Run these commands from the project root.
- Create a PR with a screenshot:
  ```sh
  gh pr create --base main --head codex/branch --title "Change title" --body-file tmp/pr.md --attach 'tmp/screenshot.png#Changed app view'
  ```
- Add a screenshot to an existing PR without replacing its description:
  ```sh
  gh pr edit 123 --attach 'tmp/screenshot.png#Changed app view'
  ```
- Repeat `--attach` for multiple images. Quote paths with `#` alt text.
- With matching paths, `gh` replaces the local Markdown image destination with the uploaded GitHub URL.
- After every upload or body edit, read the saved body with `gh pr view 123 --json body --jq .body`.
- Confirm every screenshot uses a GitHub attachment URL. Remove broken local references and duplicate images before reporting completion.
- Repair broken screenshots with `gh pr edit --body-file --attach`, using the same exact path in both arguments.
  Example body: `![Changed app view](tmp/screenshot.png)`.
  ```sh
  gh pr edit 123 --body-file tmp/pr.md --attach 'tmp/screenshot.png#Changed app view'
  gh pr view 123 --json body --jq .body
  ```
- For later body-only edits, preserve the uploaded GitHub URLs. Do not restore local image destinations without attaching those files again.
- An attachment failure can return a nonzero exit after creating the PR. Check the printed URL before retrying creation.
- Sandboxed network failures can produce false authentication errors. Retry with approved network access before changing credentials.
- Do not bypass an approval rejection. State the blocked action and its reason.

## Prose style

These rules apply to all prose you write: docs, commit messages, PR descriptions, reports, and replies.

Follow ASD-STE100 Simplified Technical English for technical text:

- Use approved words only. Each word has one meaning.
- Use one word for one idea. Do not use two words for the same thing.
- Write short sentences. Use 20 words or less for instructions.
- Use active voice. Write "Turn the switch", not "The switch must be turned".
- Write short paragraphs. Keep one topic in each paragraph.

Use an exception only when all these conditions are true:

- You write public-facing copy in Byron's voice.
- You use the `$write-byron-voice` skill.
- Clear voice evidence supports the specific deviation.

The skill does not permit a deviation by itself. Follow the global guidance when evidence does not support the deviation.
