#!/bin/bash
# memory-free: one-call memory triage and cleanup for macOS.
#
#   free.sh               report only: pressure, growth, tiered candidates
#   free.sh --kill-safe   also kill the SAFE tier, then print before/after
#   free.sh --no-sample   skip the growth sample (instant, no growth column)
#   free.sh --keep-docker never quit Docker
#
# Sizes are top's MEM (resident + compressed). ps RSS undercounts badly
# under pressure, so never rank by it.
set -u
mode=report; wait=6; keep_docker=0
for a in "$@"; do
  case $a in
    --kill-safe) mode=kill ;;
    --no-sample) wait=0 ;;
    --keep-docker) keep_docker=1 ;;
  esac
done
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# pid -> MB (MEM, CMPRS), parsed from top; units K/M/G with optional +/-
snap() {
  top -l 1 -s 0 -o mem -n 80 -stats pid,mem,cmprs 2>/dev/null | awk '
    function mb(v){ u=substr(v,length(v)); sub(/[+-]$/,"",v); u=substr(v,length(v)); n=v+0
      return u=="G"?n*1024:u=="K"?n/1024:u=="B"?n/1048576:n }
    f && $1 ~ /^[0-9]+$/ {printf "%s %d %d\n",$1,mb($2),mb($3)} /^PID/{f=1}'
}

pressure() {
  local pm swap lvl cmp wired
  pm=$(top -l 1 -s 0 | grep PhysMem)
  cmp=$(echo "$pm" | sed -nE 's/.* ([0-9]+)M compressor.*/\1/p')
  wired=$(echo "$pm" | sed -nE 's/.*\(([0-9]+)M wired.*/\1/p')
  swap=$(sysctl -n vm.swapusage | awk '{v=$6; sub(/M/,"",v); printf "%d", v}')
  lvl=$(sysctl -n kern.memorystatus_vm_pressure_level)
  echo "${swap:-0} ${cmp:-0} ${wired:-0} ${lvl:-1}"
}

verdict() { # swap cmp lvl
  if [ "$3" -ge 4 ] || { [ "$1" -gt 6000 ] && [ "$2" -gt 5000 ]; }; then echo "JAM"
  elif [ "$3" -ge 2 ] || [ "$1" -gt 3000 ] || [ "$2" -gt 4000 ]; then echo "TIGHT"
  else echo "OK"; fi
}

secs() { # [[dd-]hh:]mm:ss -> seconds
  awk -v e="$1" 'BEGIN{d=0; if (index(e,"-")) {split(e,x,"-"); d=x[1]; e=x[2]}
    n=split(e,p,":"); s=(n==3?p[1]*3600+p[2]*60+p[3]:p[1]*60+p[2]); print d*86400+s}'
}

read -r swap0 cmp0 wired0 lvl0 <<<"$(pressure)"
echo "== Pressure: $(verdict "$swap0" "$cmp0" "$lvl0")  swap ${swap0}M, compressed ${cmp0}M, wired ${wired0}M, level $lvl0 (1 ok, 2 warn, 4 critical)"

snap > "$tmp/a"
if [ "$wait" -gt 0 ]; then command sleep "$wait"; snap > "$tmp/b"; else cp "$tmp/a" "$tmp/b"; fi
# pid mem cmprs growth_MB_per_min
awk -v w="$wait" 'NR==FNR{a[$1]=$2; next} {g=(w>0 && ($1 in a))?($2-a[$1])*60/w:0; printf "%s %d %d %d\n",$1,$2,$3,g}' "$tmp/a" "$tmp/b" |
  sort -k2 -nr > "$tmp/procs"

docker_up=0; containers=""
if pgrep -f com.apple.Virtualization.VirtualMachine >/dev/null; then
  docker_up=1; containers=$(docker ps --format '{{.Names}}' 2>/dev/null | paste -sd, -)
fi

: > "$tmp/safe"; : > "$tmp/ask"; : > "$tmp/keep"
while read -r pid mem cmprs grow; do
  [ "$mem" -lt 150 ] && continue
  line=$(ps -o ppid=,etime=,command= -p "$pid" 2>/dev/null) || continue
  read -r ppid etime cmd <<<"$line"
  age=$(secs "$etime"); short=$(echo "$cmd" | cut -c1-100)
  tier=keep; kind=app; why=""; act=""
  case "$cmd" in
    *Virtualization.VirtualMachine*)
      kind=docker-vm
      if [ "$keep_docker" = 1 ]; then tier=keep; why="--keep-docker"
      elif [ -z "$containers" ]; then tier=safe; why="no containers running"
      else tier=ask; why="containers: $containers"; fi
      act="osascript -e 'quit app \"Docker Desktop\"'" ;;
    *Claude.app*|*claude.app/Contents/MacOS/claude*|*WindowServer*|/System/*|/usr/libexec/*|/usr/sbin/*)
      kind=never; why="live session or system" ;;
    /Applications/*)
      kind=gui; [ "$mem" -ge 800 ] && { tier=ask; why="GUI app (incl. helpers): suggest quitting, never quit yourself"; } ;;
    *tsserver.js*|*typescript-language-server*)
      kind=tsserver
      proj=$(echo "$cmd" | sed -nE 's#.* (/[^ ]+)/node_modules/typescript/.*#\1#p')
      # LSP parent's parent is the owning claude CLI (one per session); its cwd names the session
      lsp=$ppid; owner=$(ps -o ppid= -p "$lsp" 2>/dev/null | tr -d ' ')
      ocwd=$(lsof -a -p "${owner:-0}" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
      if [ -n "$proj" ] && [ ! -d "$proj" ]; then tier=safe; why="project dir deleted"
      elif [ "$age" -gt 3600 ]; then tier=safe; why="idle LSP, up $etime"
      else tier=ask; why="LSP up $etime; kill if session idle: ${ocwd:-unknown}"; fi
      act="kill $pid $lsp" ;;
    *vitest*|*jest*|*playwright*|*mocha*)
      kind=test-runner; root=$pid
      while :; do p=$(ps -o ppid= -p "$root" | tr -d ' '); pc=$(ps -o command= -p "$p" 2>/dev/null)
        case "$pc" in *vitest*|*jest*|*playwright*|*mocha*) root=$p ;; *) break ;; esac; done
      rcwd=$(lsof -a -p "$root" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
      if [ "$ppid" = 1 ]; then tier=safe; why="orphaned test worker"; act="kill $pid"
      else tier=ask; why="run up $(ps -o etime= -p "$root" | tr -d ' '), cwd $rcwd"; act="pkill -P $root; kill $root"; fi ;;
    *vite/bin*|*vinxi*|*next\ dev*|*webpack*|*astro\ dev*)
      kind=dev-server; tier=ask; why="up $etime, cwd $(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')"; act="kill $pid" ;;
    *node*|*tsx*|*bun*|*deno*)
      kind=node
      if [ "$ppid" = 1 ]; then
        if lsof -nP -iTCP -sTCP:LISTEN -a -p "$pid" >/dev/null 2>&1; then tier=ask; why="orphan but serving a port"
        else tier=safe; why="orphaned, no port"; fi
      elif ps -o command= -p "$ppid" | grep -q "^/Applications/"; then tier=keep; why="app helper"
      else tier=ask; why="child of $(ps -o comm= -p "$ppid" | sed 's#.*/##')"; fi
      act="kill $pid" ;;
  esac
  [ "$grow" -ge 200 ] && why="GROWING +${grow}M/min; $why"
  printf "%6s %6sM %6sM %+6s  %-11s %s\n      %s\n      act: %s\n" "$pid" "$mem" "$cmprs" "$grow" "$kind" "$why" "$short" "${act:--}" >> "$tmp/$tier"
  [ "$tier" = ask ] && [ "$mem" -lt 300 ] && [ "$grow" -lt 200 ] && tier=keep
  [ "$tier" = safe ] && echo "$mem|$act" >> "$tmp/safe.acts"
done < "$tmp/procs"

hdr() { printf "\n== %s\n   PID    MEM  CMPRS  M/min  KIND        WHY\n" "$1"; }
hdr "SAFE (idle; respawns or unowned)"; cat "$tmp/safe"
hdr "ASK (active work or someone's app)"; cat "$tmp/ask"
echo; echo "== Biggest kept (never touch / small):"; grep -E '^ +[0-9]' "$tmp/keep" | head -5

[ "$mode" = kill ] || { echo; echo "Report only. Rerun with --kill-safe to free the SAFE tier."; exit 0; }
[ -s "$tmp/safe.acts" ] || { echo; echo "Nothing in SAFE tier."; exit 0; }

echo; echo "== Killing SAFE tier"
freed=0
while IFS='|' read -r mem act; do
  echo "  $act"; eval "$act" 2>/dev/null; freed=$((freed + mem))
done < "$tmp/safe.acts"
for i in $(seq 1 20); do pgrep -f com.apple.Virtualization.VirtualMachine >/dev/null || break
  grep -q Docker "$tmp/safe.acts" || break; command sleep 1; done
command sleep 3
read -r swap1 cmp1 wired1 lvl1 <<<"$(pressure)"
echo
echo "== Result: about ${freed}M of footprint released"
printf "   %-11s %8s %8s\n" "" before after
printf "   %-11s %7sM %7sM\n" swap "$swap0" "$swap1" compressed "$cmp0" "$cmp1" wired "$wired0" "$wired1"
printf "   %-11s %8s %8s\n" level "$lvl0" "$lvl1" verdict "$(verdict "$swap0" "$cmp0" "$lvl0")" "$(verdict "$swap1" "$cmp1" "$lvl1")"
echo "   Swap drains over minutes as pages fault back in; compressed and wired move first."
