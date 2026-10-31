"""PostToolUse hook for Claude Code and Codex: remind the agent to check a PR body.

Fires after `gh pr create`, `gh pr ready` and `gh stack submit`. It only adds
context for the agent and never blocks.
"""

import json
import re
import sys

# Where a command can start: line start, or after ; & | ( or a subshell.
START = r"(?:^|[;&|(]|\$\()\s*"
# Leading env assignments, and gh's global --repo style flags.
PREFIX = r"(?:\w+=\S*\s+)*"
GH_FLAGS = r"(?:-\S+(?:\s+[^-\s]\S*)?\s+)*"
PR_CMD = re.compile(START + PREFIX + r"gh\s+" + GH_FLAGS + r"(pr\s+create|pr\s+ready|stack\s+submit)\b", re.M)

COMMON = (
    "Check this against the `pr-description` skill (~/.agents/skills/pr-description/SKILL.md): "
    "a plain statement of what changed and what the user sees, the template for the PR type "
    "(feature, fix, dev, docs), and a non-empty Proof section with real evidence."
)
STACK = (
    " `gh stack submit` writes placeholder bodies, so replace each new layer's body now with "
    "`gh pr edit --body-file`. The bottom PR needs what splits, why it splits, and why this split "
    "was the best choice. Each other layer needs the short stack block."
)
SINGLE = " Read the saved body with `gh pr view`, and fix any gap with `gh pr edit --body-file`."


def main():
    data = json.load(sys.stdin)
    cmd = (data.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or "--help" in cmd:
        return
    found = [" ".join(m.split()) for m in PR_CMD.findall(cmd)]
    if not found:
        return
    context = "PR body check: " + COMMON + (STACK if "stack submit" in found else SINGLE)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))


if __name__ == "__main__":
    main()
