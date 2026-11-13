---
name: memory-free
description: Quickly free memory on Byron's Mac when it is in a jam, such as heavy swap, a red or yellow Memory Pressure graph, beachballs, or "free up memory ASAP". A single script call measures real footprint (resident plus compressed), matches each process to its Claude session, kills what is idle, and prints before/after numbers, a ready kill line and a NEXT verdict. Use when Byron says `/memory-free`, "free up memory", "my Mac is swapping", "memory pressure is red", or pastes an Activity Monitor memory screenshot.
argument-hint: "[report] [aggressive] [keep-docker] [-- notes]"
user-invocable: true
---

# memory-free

Byron runs many Claude, Codex and editor sessions on an 18 GB Mac. By the time he calls this, the machine is already swapping. Every tool call is slow. The script makes every decision, so one call does nearly all the work.

## Step 1: run the script

```bash
~/.claude/skills/memory-free/scripts/free.py --kill-safe
```

It takes about 8 seconds. Do not call `list_sessions`: the script reads session state from disk.

Flags:
- `report` in the arguments: leave out `--kill-safe`.
- `keep-docker`: add `--keep-docker`.
- `aggressive`: add `--aggressive`. This also kills dev servers and test runs that are not growing.
- `--no-sample`: skips the growth sample. A run takes about 2 seconds. Use it to re-measure.

## Step 2: follow the last line

- `NEXT: done`: write the report.
- `NEXT: ask (...)`: ask one wrap-up question ("Kill the rest?") with "Kill them" / "Leave them" buttons. List each ASK row with its size, growth and owner, GROWING rows first.

Never quit GUI apps yourself. Name the ones in the `APPS` line so Byron can quit them.

## Step 3: if Byron says yes

Run the printed `Kill all ASK:` line exactly. If he names only some rows, run `kill` with the pids in those rows. Then re-measure with `free.py --no-sample`.

If an ASK row is a Docker row, its `kill` pids are not in that line. Run `osascript -e 'quit app "Docker Desktop"'` instead.

## Step 4: tell the owning session

The `After that, tell:` line names each running session that lost a process. Send each one a message (`SendMessage` to its `local_…` id). Include:

- what was killed and that its failure is expected;
- the size and growth evidence;
- how to rerun safely: cap workers (`--pool=forks --poolOptions.forks.maxForks=2` or `maxWorkers: 2`), run one suite at a time, find the heavy file with `--logHeapUsage`, and leave no orphaned processes.

A session that is mid-turn queues the message. Auto mode blocks `stop_session` on sessions you didn't start, so if Byron wants the message delivered now, he presses Stop in that session.

## What the script decides

| Tier | What's in it |
|---|---|
| SAFE (killed) | TypeScript servers whose session is idle, or that run over an hour, or whose project folder is gone; dev servers whose session is idle; orphaned node processes and test runs that serve no port; Docker's VM when no containers run |
| ASK | Other TypeScript servers, dev servers and test runs; node processes with a live parent; orphans that serve a port; Docker with containers |
| keep | Claude.app, `claude` CLIs, WindowServer, system processes, GUI helpers, and any ASK item under 300 MB that is not growing |

- A test run is one row. The row holds the root runner and all of its descendants, so one kill stops all of them.
- GROWING means 200 MB a minute or more over the 6-second sample. One sample is noisy, so a row can read flat a minute later.
- A session is idle when its transcript's last conversation entry ends a turn, or when the transcript has not changed for 15 minutes. If the state is unknown, the session counts as running.
- `free.py` tags Codex work by its folder and process names. It cannot tell if a Codex run is active, so Codex rows stay in ASK.

If you change a rule, change it in `free.py`, then update this table.

## Rules that keep this from failing

- **Rank by `top`'s MEM, never by `ps` RSS or the "free percentage".** Under pressure, RSS leaves out compressed pages: a process `ps` shows at 51 MB can really be 250 MB. `memory_pressure` reports about 34% free while the machine swaps 11 GB. If Byron's Activity Monitor screenshot disagrees with your numbers, trust the screenshot.
- **Keep your own footprint small.** Don't start subagents, open the browser, or run builds or tests while memory is in a jam.
- **Never touch** Claude.app, `claude` CLI processes, WindowServer or system daemons, and never use `sudo`. If Byron wants the cache dropped, give him `sudo purge` to run himself. It helps little.
- **Docker that comes back means something needs it.** If Docker restarted after an earlier quit, say so and do not kill it again without asking.
- **Swap drains slowly.** Compressed and wired memory drop first, and swap shrinks over minutes as pages are read back in. Say so if the swap number hasn't moved yet.

## Report

Copy the script's before/after table, then write three short lists:
- what was killed and why;
- what was left running and why;
- the apps Byron could quit, with their sizes.
