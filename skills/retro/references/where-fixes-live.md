# Where fixes live

## Implementation vs review

All work goes through two stages. The implementation agent carries the most **context pressure**: it explores, writes code, and debugs. The review agent gets a diff, so it needs no exploration and rarely writes code.

So the review agent enforces coding standards, not the implementation agent.

## Files

- `CLAUDE.md` / `AGENTS.md`: pushed into every agent's context in this repo. Use them sparingly, mostly for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: read at review time, not implementation. Holds judgement calls only. Past ~1,000 lines, split into docs and point to them.
- Docs: reference files that other files point to. Look for an existing doc before writing a new one.
- Repo skills (`.claude/skills/`): for procedures and user-invoked commands. The description is always in context; the body loads on demand.
- Global skills (`~/.agents/skills/<name>/`): for lessons that hold across repos. Read and edit them through the `~/.agents` path. `~/.claude/skills` is a symlink, and the Edit tool treats the two paths as different files.
- Checks: lint rules, pre-commit hooks, scripts. Use one for any **mechanical** violation (a fixed pattern, banned API, import shape, file location). Add CI only when the repo already has CI.
- Settings (repo or account): auto-merge, delete-on-merge, required checks, permission allowlists. The agent can't change some of these; name them as a step for Byron.
