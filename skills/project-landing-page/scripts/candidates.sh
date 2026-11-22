#!/usr/bin/env bash
# List public repos with recent commits and no landing page.
#   candidates.sh [owner] [days]
# A repo has a landing page when GitHub Pages is on or its website field is set.
set -euo pipefail

owner=${1:-$(gh api user --jq .login)}
days=${2:-45}
since=$(date -u -v-"${days}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-$days days" +%Y-%m-%dT%H:%M:%SZ)

printf '%-8s %-28s %s\n' commits repo description
gh repo list "$owner" --visibility public --no-archived --source --limit 300 \
  --json name,pushedAt,homepageUrl,description \
  --jq ".[] | select(.pushedAt > \"$since\") | select((.homepageUrl // \"\") == \"\") | select(.name | startswith(\".\") | not) | [.name, (.description // \"\")] | @tsv" |
while IFS=$'\t' read -r name desc; do
  if gh api "repos/$owner/$name/pages" --silent 2>/dev/null; then
    continue
  fi
  n=$(gh api "repos/$owner/$name/commits?since=$since&per_page=100" --jq length 2>/dev/null || echo 0)
  printf '%-8s %-28s %s\n' "$n" "$name" "${desc:0:70}"
done | sort -rn
