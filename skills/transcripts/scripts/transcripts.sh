#!/bin/zsh
# One entry point for Byron's v2ctx voice-memo archive.
#
#   transcripts.sh refresh   Ingest new Apple Voice Memos + run LLM on remaining,
#                            then refresh hub indexes. Blocks until done.
#   transcripts.sh viewer    Make sure the review app is running; print its URL.
#   transcripts.sh status    Show archive, viewer, and last-run state.
#
# macOS only lets apps with Full Disk Access read the Voice Memos container.
# iTerm has it; Claude, Codex, and Terminal.app do not. So anything that touches
# Voice Memos (refresh, and the viewer's Refresh button) runs inside an iTerm
# window that this script opens and then waits on.

set -u

ARCHIVE="${V2C_VOICE_MEMOS_ROOT:-$HOME/.v2c-voice-memos}"
HUB="/Users/byronwall/Projects/hub"
V2C_APP="/Users/byronwall/Projects/video-to-context/app"
PORT="${V2C_VIEWER_PORT:-5173}"
STATE="$HOME/Library/Caches/v2ctx-transcripts"
TERMINAL_APP="${V2C_TERMINAL_APP:-iTerm}"
mkdir -p "$STATE"

viewer_up() {
  curl -fsS -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/api/voice-memos" 2>/dev/null
}

# Run a command in a new iTerm window via a .command file, then wait for it.
# $1 = job name, $2 = shell command. Output -> $STATE/<job>.log, exit -> <job>.exit
run_in_terminal() {
  local job="$1" cmd="$2"
  local script="$STATE/$job.command" log="$STATE/$job.log" exitf="$STATE/$job.exit"
  rm -f "$exitf"
  cat > "$script" <<EOF
#!/bin/zsh -l
cd "$HUB"
$cmd 2>&1 | tee "$log"
echo \${pipestatus[1]} > "$exitf"
echo; echo "[$job finished — this window can be closed]"
EOF
  chmod +x "$script"
  open -a "$TERMINAL_APP" "$script" || { echo "error: could not open $TERMINAL_APP" >&2; return 2; }
}

wait_for_exit() {
  local job="$1" timeout="${2:-3600}" waited=0
  while [[ ! -f "$STATE/$job.exit" ]]; do
    sleep 3; (( waited += 3 ))
    if (( waited >= timeout )); then echo "error: $job still running after ${timeout}s" >&2; return 3; fi
  done
  return "$(cat "$STATE/$job.exit")"
}

cmd_refresh() {
  if [[ -f "$STATE/refresh.command" && ! -f "$STATE/refresh.exit" ]]; then
    echo "A refresh is already running in $TERMINAL_APP; waiting for it."
  else
    echo "Starting ingest + LLM in $TERMINAL_APP (v2ctx voice-memos --run-llm --no-open)…"
    run_in_terminal refresh "v2ctx voice-memos --run-llm --no-open" || return $?
  fi
  wait_for_exit refresh
  local rc=$?
  local clean; clean=$(sed $'s/\x1b\\[[0-9;]*m//g' "$STATE/refresh.log")

  if grep -q "EPERM\|Could not auto-detect" <<<"$clean"; then
    echo "error: $TERMINAL_APP could not read Voice Memos (needs Full Disk Access)." >&2
    grep -A8 "^Error:" <<<"$clean" >&2
    return 4
  fi
  echo "--- processed this run ---"
  grep "complete: " <<<"$clean" || echo "  (nothing new)"
  grep -A20 "^Summary:" <<<"$clean"
  (( rc != 0 )) && { echo "error: v2ctx exited $rc (full log: $STATE/refresh.log)" >&2; return $rc; }

  echo "--- refreshing hub indexes ---"
  (cd "$HUB" && node scripts/refresh-indexes.mjs) || { echo "error: refresh-indexes failed" >&2; return 5; }
  echo "OK. Full log: $STATE/refresh.log"
}

cmd_viewer() {
  if viewer_up; then
    echo "Viewer already running: http://localhost:$PORT"
    return 0
  fi
  echo "Starting viewer in $TERMINAL_APP…"
  run_in_terminal viewer "npm --prefix '$V2C_APP' run dev -- --port $PORT --strictPort" || return $?
  for _ in {1..40}; do
    viewer_up && { echo "Viewer running: http://localhost:$PORT"; return 0; }
    [[ -f "$STATE/viewer.exit" ]] && break
    sleep 1
  done
  echo "error: viewer did not come up on port $PORT. Log: $STATE/viewer.log" >&2
  tail -20 "$STATE/viewer.log" >&2 2>/dev/null
  return 6
}

cmd_status() {
  local n; n=$(ls -d "$ARCHIVE"/*-context 2>/dev/null | wc -l | tr -d ' ')
  echo "archive:  $ARCHIVE ($n packages, newest: $(ls -d "$ARCHIVE"/*-context | tail -1 | xargs basename))"
  if viewer_up; then echo "viewer:   http://localhost:$PORT (running)"; else echo "viewer:   not running"; fi
  if [[ -f "$STATE/refresh.exit" ]]; then
    echo "last refresh: exit $(cat "$STATE/refresh.exit") at $(stat -f '%Sm' "$STATE/refresh.exit")"
  elif [[ -f "$STATE/refresh.command" ]]; then
    echo "last refresh: running"
  fi
}

case "${1:-}" in
  refresh) cmd_refresh ;;
  viewer)  cmd_viewer ;;
  status)  cmd_status ;;
  *) echo "usage: $0 {refresh|viewer|status}" >&2; exit 64 ;;
esac
