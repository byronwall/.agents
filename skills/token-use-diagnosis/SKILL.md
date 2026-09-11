---
name: token-use-diagnosis
description: Diagnose recent local Codex or agent-thread token use by querying llmly's usage explorer, grouping results by raw tool and session, and explaining token hotspots, tool overhead, and practical process changes. Use when asked why a recent task used many tokens, to review the last hour or day of agent work, or to compare sessions without exposing full prompts or tool results.
---

# Token Use Diagnosis

## Overview

Use the local `llmly` usage explorer to find recent token hotspots. Produce a compact report that separates model input, output, reasoning, tool activity, and session totals.

## Workflow

1. Locate the `llmly` checkout. Prefer the current repository when it contains `app.py` and `llmly/analyzer/`. For this installation, use `/Users/byronwall/Projects/data-viz-copilot-usage`.
2. Run the bundled helper from the skill directory:

   ```bash
   python3 /Users/byronwall/.codex/skills/token-use-diagnosis/scripts/diagnose_usage.py \
     --repo /Users/byronwall/Projects/data-viz-copilot-usage \
     --hours 1 \
     --top 15
   ```

3. Use `--hours 24` for the default day view. Pass another positive number to inspect a different recent window.
4. Use `--top 15` by default. Pass another positive number to change the display bound.
5. Keep `--source codex` for Codex threads. Use `--source all` only when the user asks for combined local sources. The CLI also accepts `copilot` and `claude`.
6. Read both sections of the helper output:
   - Tool hotspots explain which exact logged tool names correlate with input tokens, calls, result size, duration, or failures.
   - Session hotspots identify the sessions that consumed the most tokens. Use the session ID for follow-up inspection.
7. Explain causes with evidence from the aggregates. Recommend process changes such as smaller context windows, fewer repeated searches, narrower file reads, shorter tool results, or earlier task decomposition.

## CLI Contract

The helper runs two read-only commands from the checkout. The exact repository flags are:

```text
uv run app.py --usage-explorer --usage-output json
  --usage-source {all,codex,copilot,claude}
  --usage-since-hours HOURS
  --usage-min-tokens N
  --usage-limit 0
  --usage-group-by {tool,session}
  --usage-metric {total_input,cached_input,uncached_input,new_input,output,
                  reasoning,calls,failures,result_chars,duration_ms}
  --usage-attribution {fractional,full}
```

Use `uncached_input` as the primary hotspot metric and `fractional` attribution. Fractional attribution keeps request token totals additive when one request has several tools. Use `full` only when the user wants every tool's full causal share.

The explorer defaults to the last 24 hours when no window is supplied. `--usage-limit 0` means all matching sessions. The helper sets both the raw-tool and session queries to those safe defaults. The app also accepts `tool_family`, but this skill does not request that grouping.

The helper's `--top N` flag limits display only. It still queries every matching session and every raw tool with `--usage-limit 0`, then computes totals and sorts all results. It prints the top N tools and sessions, plus the count omitted from each section. The default is 15. `--top` is a helper flag, not an `llmly` CLI flag.

## Interpretation Rules

- Compare `uncached_input` with `total_input`. High cached input means context was reused; high uncached or new input means the model received more fresh context.
- Compare `output` and `reasoning` with input. A large output points to response scope. A large reasoning count points to model effort, not tool output.
- Compare `result_chars`, `calls`, and `duration_ms` by raw tool name. Large values suggest tool overhead, but they are not token counts.
- Treat `failures` as a process signal. Repeated failures can cause retries and extra context.
- Treat `no tool` as a valid group. It represents model requests without a classified non-user tool cause.
- Keep similarly named tools separate. Raw-tool grouping does not merge aliases or related operations.
- Do not infer causation from a single tool group. Check the matching session totals and request counts.
- Do not print `first_user`, raw prompt text, raw tool arguments, or raw tool results. The helper bounds labels and omits raw payloads.
- State when no matching sessions exist, when a source path is missing, or when metrics are estimates from the source adapter.

## Limits

The report depends on local Codex history discovery and the selected source adapter. It cannot explain events that were not logged, deleted, outside the time window, or stored in an unsupported profile. Tool result characters and duration are operational indicators, not token counts. Raw-tool attribution is a causal heuristic, not proof that a tool caused all request tokens. Source adapters may use different names for similar operations, so raw-tool results can be fragmented.

## Resource

Run `scripts/diagnose_usage.py` for the compact two-query report. Read or modify it only when the checkout's CLI contract changes.
