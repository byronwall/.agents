---
name: handoff-to-claude-desktop
description: Hand work to Claude Desktop in a named Code project, include local planning artifacts and an execution prompt, and verify that the session starts under the correct project. Use for explicit handoffs to Claude Desktop; not ordinary Claude API or terminal-only work.
---

# Handoff to Claude Desktop

Complete the requested handoff in Claude Desktop's Code surface. A prepared composer is not a submitted session. A matching folder name alone does not prove project membership.

## Choose the route

Check available dedicated tools first. Codex thread tools create Codex chats, not Claude Desktop sessions.

Supported launch methods, checked October 15, 2026:

- `claude://code/new?q=<encoded-prompt>&folder=<encoded-absolute-path>` prepares the Code composer. The app requires folder confirmation. This does not send the prompt or prove sidebar project membership. Encode values with a URL library; keep prompts below 14,000 characters. The Code route does not support file attachment through `file` today.
- `claude --desktop`, from the target directory, opens Desktop. It requires CLI 2.1.285 or later. It accepts no prompt. `--resume` takes a session ID. Do not assume this creates a submitted task.

Use these routes when preparation is sufficient. For a completed handoff in a named project, use the UI workflow below unless a current supported API proves the same result. Recheck official documentation when capabilities change.

Do not substitute a background CLI run or edit Claude's internal databases. Do not create a duplicate session merely to test a launch method.

Sources: [Desktop links](https://support.claude.com/en/articles/14729294-open-claude-desktop-with-a-link), [CLI reference](https://code.claude.com/docs/en/cli-reference).

## Prepare the handoff

Identify the exact project, saved checkout, authorized action, and relevant artifacts. Verify file paths before sending. Do not infer the saved checkout from a Codex worktree path.

The prompt must contain:

- A direct instruction such as “Execute the implementation plan; do not stop at another plan.” Use this only when execution is authorized.
- The destination project and checkout.
- Absolute paths to the plan, shape, intent, machine state, and useful visual references.
- Latest user decisions that supersede earlier proposals.
- Completion criteria and relevant verification commands.
- Any explicit boundaries on worktrees, deployment, cleanup, or unrelated work.

When artifacts are uncommitted in another checkout, say so. Instruct Claude to read them there and copy only the handoff artifacts into its working checkout when needed. Preserve newer destination content. Do not imply that untracked files arrive through Git. If the destination cannot access the files, provide their contents or report the specific blocker.

Keep large context in accessible files. Include enough decisions in the prompt to prevent stale documents from winning.

## Submit through the UI

Use `mcp__cua_repl` and its documented API for all UI actions. On first use, select Claude with `await cua.getApp("Claude")`. After context compaction, reload the tool documentation before continuing UI work.

1. Read the current accessibility state. Select Code if necessary.
2. Find the exact project in the sidebar. Prefer **New session in <project>** over the generic New control.
3. Verify the composer environment and absolute folder. If an environment error appears, inspect the selector and reselect the correct available local environment. Do not send while the destination remains uncertain.
4. Verify checkout mode before submission. A prompt saying “do not create a worktree” cannot prevent the app from creating one. Use the existing checkout unless the user authorized a worktree. If the app enforces a conflicting mode, report that conflict before submission.
5. Paste the complete prompt into the new session composer. Read fresh state to verify the text and destination.
6. Send once, then inspect fresh state. If the response is uncertain, inspect before retrying. Do not send again merely because a title has not appeared yet.

Use fresh element indices from each accessibility observation. Never reuse indices from this skill's source conversation. Use screenshots only when the accessibility state does not expose the needed control. Preserve current model and permission settings unless the user requested changes.

## Verify completion

Confirm all of these after submission:

- The new session has a real title or ID.
- Its sidebar row appears under the exact requested project.
- The submitted message includes the execution instruction and artifact paths.
- The session shows running/responding, or a concrete permission/error state.
- Environment details match the intended checkout mode.

An automatically created worktree must be reported honestly. Do not claim an existing-checkout handoff based only on prompt text. If checkout mode is wrong, use supported controls to correct it when possible. Do not delete worktrees or disturb unrelated sessions as cleanup.

Once these checks pass, stop. Report the actual title, project, and whether execution started. If only the composer is prepared, say that it still needs confirmation or sending.

## Observed lessons

The October 15, 2026 handoff created **Diagram themes and default styles** under **diagram-studio** through its project-specific New session button. Claude assigned a worktree automatically despite a prompt requesting the existing checkout. Future runs must check that setting before submission.

At that time the installed CLI was 2.1.281, below the documented `--desktop` requirement. Recheck with `claude --version`; do not assume this limitation persists.
