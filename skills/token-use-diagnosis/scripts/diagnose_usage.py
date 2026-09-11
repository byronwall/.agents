#!/usr/bin/env python3
"""Print a compact recent-token diagnosis from the local llmly CLI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


METRICS = (
    "total_input",
    "cached_input",
    "uncached_input",
    "new_input",
    "output",
    "reasoning",
    "calls",
    "failures",
    "result_chars",
    "duration_ms",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize recent llmly usage without printing raw prompts or tool results."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="llmly checkout containing app.py (default: current directory)",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=24.0,
        help="Recent window in hours; use 1 for the last hour (default: 24)",
    )
    parser.add_argument(
        "--source",
        choices=("all", "codex", "copilot", "claude"),
        default="codex",
        help="Usage source (default: codex)",
    )
    parser.add_argument(
        "--min-tokens",
        type=int,
        default=0,
        help="Minimum input tokens per session (default: 0)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="Number of raw tools and sessions to display (default: 15)",
    )
    return parser.parse_args()


def run_query(repo: Path, hours: float, source: str, min_tokens: int, group_by: str) -> dict[str, Any]:
    command = [
        "uv",
        "run",
        "app.py",
        "--usage-explorer",
        "--usage-output",
        "json",
        "--usage-source",
        source,
        "--usage-since-hours",
        str(hours),
        "--usage-min-tokens",
        str(min_tokens),
        "--usage-limit",
        "0",
        "--usage-group-by",
        group_by,
        "--usage-metric",
        "uncached_input",
        "--usage-attribution",
        "fractional",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("uv was not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "command failed").strip()
        raise RuntimeError(f"usage query failed: {detail}") from exc

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("usage query returned non-JSON output") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("usage query returned an unexpected payload")
    return payload


def number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def fmt_number(value: Any) -> str:
    amount = number(value)
    if amount.is_integer():
        return f"{int(amount):,}"
    return f"{amount:,.1f}"


def metric_text(metrics: dict[str, Any]) -> str:
    return (
        f"uncached={fmt_number(metrics.get('uncached_input'))} "
        f"cached={fmt_number(metrics.get('cached_input'))} "
        f"new={fmt_number(metrics.get('new_input'))} "
        f"total={fmt_number(metrics.get('total_input'))} "
        f"output={fmt_number(metrics.get('output'))} "
        f"reasoning={fmt_number(metrics.get('reasoning'))}"
    )


def compact_path(value: Any) -> str:
    if not value:
        return "-"
    path = os.path.normpath(str(value))
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        path = "~" + path[len(home) :]
    return path


def print_tools(payload: dict[str, Any], top: int) -> None:
    groups = payload.get("groups") or []
    omitted = max(0, len(groups) - top)
    print(f"Tool hotspots (showing top {min(top, len(groups))} of {len(groups)}; omitted {omitted})")
    if not groups:
        print("  none")
        return
    for index, group in enumerate(groups[:top], 1):
        metrics = group.get("metrics") or {}
        print(
            f"  {index}. {group.get('label') or group.get('key') or '-'} | "
            f"{metric_text(metrics)} | "
            f"requests={fmt_number(group.get('requests'))} "
            f"sessions={fmt_number(group.get('sessions'))} "
            f"calls={fmt_number(metrics.get('calls'))} "
            f"failures={fmt_number(metrics.get('failures'))} "
            f"result_chars={fmt_number(metrics.get('result_chars'))} "
            f"duration_ms={fmt_number(metrics.get('duration_ms'))}"
        )


def print_sessions(payload: dict[str, Any], top: int) -> None:
    groups = payload.get("groups") or []
    omitted = max(0, len(groups) - top)
    print(f"Session hotspots (showing top {min(top, len(groups))} of {len(groups)}; omitted {omitted})")
    if not groups:
        print("  none")
        return
    for index, group in enumerate(groups[:top], 1):
        rows = group.get("session_rows") or []
        row = rows[0] if rows else {}
        metrics = row.get("metrics") or group.get("metrics") or {}
        sid = row.get("sid") or group.get("key") or "-"
        workspace = compact_path(row.get("workspace"))
        print(
            f"  {index}. {sid} | {metric_text(metrics)} | "
            f"requests={fmt_number(row.get('requests') or group.get('requests'))} "
            f"workspace={workspace}"
        )


def print_signals(tool_payload: dict[str, Any], session_payload: dict[str, Any]) -> None:
    groups = tool_payload.get("groups") or []
    totals = tool_payload.get("totals") or {}
    sessions = session_payload.get("groups") or []
    uncached_total = number(totals.get("uncached_input"))
    if groups and uncached_total > 0:
        top = groups[0]
        share = number((top.get("metrics") or {}).get("uncached_input")) / uncached_total
        print(f"Signals: top tool is {top.get('label') or top.get('key') or '-'} ({share:.0%} of uncached input).")
    else:
        print("Signals: no uncached-input hotspot was found.")
    if sessions and number((sessions[0].get("metrics") or {}).get("new_input")) > 0:
        print("  The top session includes fresh input; inspect repeated context reads or large file scopes.")
    failures = number(totals.get("failures"))
    if failures:
        print(f"  Tool failures: {fmt_number(failures)}; check for retries or recovery loops.")
    result_chars = number(totals.get("result_chars"))
    if result_chars:
        print(f"  Tool result volume: {fmt_number(result_chars)} characters; compare it with calls and uncached input.")


def main() -> int:
    args = parse_args()
    if args.hours <= 0:
        print("--hours must be greater than zero", file=sys.stderr)
        return 2
    if args.min_tokens < 0:
        print("--min-tokens cannot be negative", file=sys.stderr)
        return 2
    if args.top <= 0:
        print("--top must be greater than zero", file=sys.stderr)
        return 2

    repo = args.repo.expanduser().resolve()
    if not (repo / "app.py").is_file():
        print(f"No app.py found in {repo}; pass --repo to the llmly checkout.", file=sys.stderr)
        return 2

    try:
        tool_payload = run_query(repo, args.hours, args.source, args.min_tokens, "tool")
        session_payload = run_query(repo, args.hours, args.source, args.min_tokens, "session")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    meta = tool_payload.get("meta") or {}
    print("Token-use diagnosis")
    print(
        f"Window: last {args.hours:g} hour(s) | source={args.source} | "
        f"sessions={fmt_number(meta.get('n_sessions'))} requests={fmt_number(meta.get('n_requests'))} | "
        f"attribution=fractional | display_top={args.top}"
    )
    print(f"Totals: {metric_text(tool_payload.get('totals') or {})}")
    print_tools(tool_payload, args.top)
    print_sessions(session_payload, args.top)
    print_signals(tool_payload, session_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
