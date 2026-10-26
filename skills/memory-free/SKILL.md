---
name: memory-free
description: Quickly free memory on Byron's Mac when it is in a jam, such as heavy swap, a red or yellow Memory Pressure graph, beachballs, or "free up memory ASAP". A single script call measures real footprint (resident plus compressed), sorts processes into SAFE, ASK and keep tiers, kills the SAFE tier and reports before/after numbers. Then it matches the remaining hogs to Claude sessions, asks one question about active work, and tells the owning session what happened. Use when Byron says `/memory-free`, "free up memory", "my Mac is swapping", "memory pressure is red", or pastes an Activity Monitor memory screenshot.
argument-hint: "[report] [aggressive] [keep-docker] [-- notes]"
user-invocable: true
---

# memory-free

Byron runs many Claude, Codex and editor sessions on an 18 GB Mac. By the time he calls this, the machine is already swapping. Every tool call is slow, so act in as few calls as possible: kill what is clearly idle right away, and ask one question about everything else.

## Call 1: free and measure (send both in the same message)

```bash
~/.claude/skills/memory-free/scripts/free.sh --kill-safe
```

Send `mcp__ccd_session_mgmt__list_sessions` (limit 40) in the same message. In about 10 seconds the script:

- prints a verdict (JAM, TIGHT or OK) from swap, compressed memory and the kernel's pressure level;
- samples the process list twice, 6 seconds apart, and flags anything **GROWING** by 200 MB a minute or more;
- sorts processes over 150 MB into three tiers and gives each one its exact `act:` command;
- kills the SAFE tier and prints a before/after table.

Flags:
- `report` in the arguments: leave out `--kill-safe`.
- `keep-docker`: add `--keep-docker`.
- `--no-sample`: skips the growth sample. Use it only when a second run follows soon after.

The tiers, which the script works out itself:

| Tier | What's in it |
|---|---|
| SAFE (killed) | TypeScript servers running over an hour or whose project folder is gone, along with their LSP parent; orphaned (PPID 1) node processes or test workers that aren't serving a port; Docker's VM when no containers are running |
| ASK | Test runners and dev servers (with their cwd), TypeScript servers under an hour old (with the owning session's cwd), Docker with containers, orphans serving a port, GUI apps over 800 MB |
| keep | Claude.app, `claude` CLIs, WindowServer and system processes, GUI helper processes, anything under 300 MB that isn't growing |

## Step 2: promote using session state (no question needed)

Match each ASK item's cwd (a worktree path) against the `cwd` values from `list_sessions`:

- **Its session has `isRunning: false`**: a TypeScript server or dev server for a session that is idle, archived or merged is idle. Run its `act:` line now and say so in the report.
- **Its session has `isRunning: true`, or no session matches**: leave it in ASK.
- `aggressive` in the arguments: also kill dev servers and test runners in ASK that aren't GROWING.

## Step 3: one question, if anything is left

If ASK still holds items worth at least 1 GB in total, or anything GROWING, ask one wrap-up question ("Kill the rest?") with "Kill them" / "Leave them" buttons. List each item in the message with its size, growth and owning session. A GROWING test runner goes first. Don't wait to ask when something is past 2 GB and still climbing. Never quit GUI apps yourself; name them with their sizes so Byron can quit them.

When Byron says yes, run the `act:` lines exactly as printed. For a test runner, `act:` kills the root runner and all of its workers. Then re-measure with `free.sh --no-sample`.

## Step 4: tell the owning session

When you killed a running session's test run or dev server, or it caused the jam, send that session a message (`SendMessage` to its `local_…` id). Include:

- what was killed and that its failure is expected;
- the size and growth evidence;
- how to rerun safely: cap workers (`--pool=forks --poolOptions.forks.maxForks=2` or `maxWorkers: 2`), run one suite at a time, find the heavy file with `--logHeapUsage`, and leave no orphaned processes.

A session that is mid-turn queues the message. Auto mode blocks `stop_session` on sessions you didn't start, so if Byron wants the message delivered now, he presses Stop in that session.

## Rules that keep this from failing

- **Rank by `top`'s MEM, never by `ps` RSS or the "free percentage".** Under pressure, RSS leaves out compressed pages: a process `ps` shows at 51 MB can really be 250 MB. `memory_pressure` reports about 34% free while the machine swaps 11 GB. If Byron's Activity Monitor screenshot disagrees with your numbers, trust the screenshot.
- **Keep your own footprint small.** Don't start subagents, open the browser, or run builds or tests while memory is in a jam.
- **Never touch** Claude.app, `claude` CLI processes, WindowServer or system daemons, and never use `sudo`. If Byron wants the cache dropped, give him `sudo purge` to run himself. It helps little.
- **Docker that comes back means something needs it.** If Docker restarted after an earlier quit, keep it in ASK and say it restarted.
- **Swap drains slowly.** Compressed and wired memory drop first, and swap shrinks over minutes as pages are read back in. Say so if the swap number hasn't moved yet.

## Report

Write a short before/after table (swap, compressed, wired, verdict), then three lists:
- what you killed and why (SAFE tier, plus items promoted by session state);
- what you left running and why;
- the next-biggest consumers Byron could quit himself, with their sizes.
