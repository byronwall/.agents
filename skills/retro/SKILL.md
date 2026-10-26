---
name: retro
description: "Conduct a retrospective on recent coding sessions in the current project and suggest improvements to the agent's environment. Use when Byron says `/retro`, `$retro`, or asks for a retro or retrospective."
disable-model-invocation: true
---

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

## Scope (defaults)

Unless the user says otherwise:

- **Project**: the repo you are running in. Worktrees under it count as the same project. Run broader (other projects, all projects) only when the user explicitly asks.
- **Harness**: the one you are running in. Under Claude Code, read Claude Code transcripts; under Codex, read Codex rollouts. Read both only when asked.
- **Window**: every session since the previous retro in this project (3 days if none in the last 30). A user-named session, time frame, or count ("last 20 threads") wins.

The bundled script does the deterministic pass. It auto-detects the harness and scopes to the project:

```bash
R=~/.agents/skills/retro/scripts/list_sessions.py
python3 $R                 # list sessions in the window (--days N, --source claude|codex|all, --all-projects)
python3 $R --scan > $TMPDIR/retro-scan.txt   # failures by command, slowest calls, every user message
python3 $R --digest FILE   # one session: tool counts, failures, slow and large calls, user messages
```

It prints one row per session (last activity, message count, size, worktree, first user message, transcript path) and marks earlier retro sessions `RETRO`. State the scope you used in one line at the top of your reply.

## Steps

1. Call the Skill tool with `writing-for-agents` for the writing style guide, if it is installed. If not, write findings for agents: short, imperative, one point once, navigation pointers over prose.
2. Read the primary sources for the sessions in scope. Transcripts are multi-MB JSONL; never `cat` them, and don't write your own parser. Read the `--scan` report first: the user's messages are the highest-signal part (what they asked, repeated, or corrected), and failures and slow calls point to the sessions worth a `--digest`. Open raw transcript lines only to confirm a specific finding. With more than ~10 sessions to dig into, hand batches to subagents that return findings with evidence. If a previous retro exists, read its findings first and check whether each one landed (`git log --since=<retro date> --oneline -- AGENTS.md CLAUDE.md CODING_STANDARDS.md .github`). A finding that came back is more severe the second time.
3. Look for candidates for improvement in these categories.
- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? Linting, typing, tests, filesystem linters? Read the repo's own check command first (its `package.json`/build-tool `lint`/`check` scripts, its CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook running its lint/typecheck/test command) is itself a finding: an un-linted repo is a standing missed opportunity, not a neutral default. Suggest CI (GitHub Actions or any hosted CI job) only when the repo already has CI or the user asks about it; otherwise the guardrail is a local check such as a pre-commit hook. _Use when_ the agent made a mistake an automated check could have caught, or the repo has no guardrail at all.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop: a custom rule in the repo's own linter, a new pre-commit hook, or (only where the repo already has CI) a new CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style," anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Verification**: did the agent prove its work the way the change demands? UI work needs screenshots that someone actually looked at. Behavior changes need a test or a real run. A PR that claims "done" with unchecked visuals or skipped checks is a finding. _Use when_ the user found a defect the agent should have seen, or the agent declared success without evidence.
- **User steering**: what did the user have to say more than once, correct, or redo by hand? Each repeat is a missing instruction, check, or skill default. _Use when_ the same correction shows up in two or more sessions.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? Is there any custom tooling (CLI's, MCP's) that is particularly token-inefficient? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.
4. Present these candidates to the user as a numbered list, in order of severity, so the user can answer "do 1, 3, 5". For each one give:
   - the evidence (session and a short quote or tool error),
   - the proposed fix and where it lives (check, `CODING_STANDARDS.md`, `AGENTS.md`, a repo skill, or a global skill in `~/.agents/skills`),
   - whether a previous retro already raised it.

   Then add a short **What went well** list: patterns worth keeping, so a fix doesn't break them.
5. Stop and let the user pick. Do not start fixing unless asked. When asked to fix:
   - For each item, compare a few options with `consider-contrast` and pick the best or a hybrid.
   - Repo changes go out as stacked PRs, one item or tight group per PR.
   - Global skills (`~/.agents/skills/*`) are edited in place, with no PR.

## Reference
### Implementation vs Review
Remember that all work goes through two stages: implementation and review. The implementation agent has the most **context pressure**. They are responsible for exploration, writing code, and debugging failures.

The review agent has the least context pressure - it receives a diff, so no exploration needed. It often does not need to write code or debug.

This means that the review agent should be responsible for imposing coding standards, not the implementation agent.
### Files
You have access to several files in the repo:
- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. They should be used incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: this file is read during review, not implementation. Add **navigation pointers** to docs folders if the standards file gets more than 1,000 lines long.
- Docs: use docs as references files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into the agent's context window), or for user-invoked commands. Follow the advice in the `writing-for-agents` skill.
