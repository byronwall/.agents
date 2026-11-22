#!/usr/bin/env bash
# GitHub Pages settings for a project landing page.
#   pages.sh status   owner/repo   show visibility, Pages source, domain, website
#   pages.sh enable   owner/repo   set the Pages source to GitHub Actions (public repos only)
#   pages.sh homepage owner/repo   set the repo website to the Pages URL; list other homepage fields
set -euo pipefail

cmd=${1:?usage: pages.sh status|enable|homepage owner/repo}
repo=${2:?usage: pages.sh $cmd owner/repo}

visibility=$(gh repo view "$repo" --json visibility --jq .visibility)
website=$(gh repo view "$repo" --json homepageUrl --jq .homepageUrl)
pages=$(gh api "repos/$repo/pages" 2>/dev/null) || pages=""

pages_url() {
  local url
  url=$(gh api "repos/$repo/pages" --jq .html_url 2>/dev/null) || url=""
  if [[ -z $url ]]; then
    url="https://${repo%%/*}.github.io/${repo#*/}/"
  fi
  echo "${url%/}/"
}

case $cmd in
  status)
    echo "repo:       $repo ($visibility)"
    echo "website:    ${website:-<none>}"
    if [[ -z $pages ]]; then
      echo "pages:      off"
    else
      echo "$pages" | jq -r '"pages:      \(.html_url)\nsource:     \(.build_type) \(.source.branch // "")\(.source.path // "")\ndomain:     \(.cname // "<none>")"'
    fi
    if gh api "repos/$repo/branches/gh-pages" --silent 2>/dev/null; then
      echo "gh-pages:   branch exists (list what it serves before you replace it)"
    fi
    ;;

  enable)
    if [[ $visibility != PUBLIC ]]; then
      echo "refused: $repo is $visibility. Landing pages deploy only from public repos." >&2
      exit 2
    fi
    if [[ -z $pages ]]; then
      gh api -X POST "repos/$repo/pages" -f build_type=workflow --jq '"created: \(.html_url) (\(.build_type))"'
    elif [[ $(echo "$pages" | jq -r .build_type) != workflow ]]; then
      gh api -X PUT "repos/$repo/pages" -f build_type=workflow
      echo "switched: $repo Pages source is now GitHub Actions"
    else
      echo "unchanged: $repo already deploys Pages from GitHub Actions"
    fi
    echo "github-pages environment branch rules:"
    gh api "repos/$repo/environments/github-pages/deployment-branch-policies" \
      --jq '.branch_policies[] | "  \(.name)"' 2>/dev/null || echo "  (environment appears on the first deploy)"
    ;;

  homepage)
    url=$(pages_url)
    code=$(curl -s -o /dev/null -w '%{http_code}' "$url")
    if [[ $code != 200 ]]; then
      echo "not live: $url returned $code. Wait for the Pages run, then retry." >&2
      exit 3
    fi
    if [[ $(echo "$pages" | jq -r '.cname // empty') != "" ]]; then
      url="https://$(echo "$pages" | jq -r .cname)/"
    fi
    if [[ ${website%/} == "${url%/}" ]]; then
      echo "unchanged: website is already $url"
    else
      gh repo edit "$repo" --homepage "$url"
      echo "website: ${website:-<none>} -> $url"
    fi
    # Package metadata that may also name a homepage. Print it; edit it in a commit.
    for f in package.json pyproject.toml Cargo.toml; do
      body=$(gh api "repos/$repo/contents/$f" -H "Accept: application/vnd.github.raw" 2>/dev/null) || body=""
      [[ -z $body ]] && continue
      echo "$f:"
      echo "$body" | grep -nEi '"?homepage"?\s*[:=]|^\s*(Homepage|Documentation)\s*=' | sed 's/^/  /' || echo "  no homepage field"
    done
    ;;

  *)
    echo "unknown command: $cmd" >&2
    exit 1
    ;;
esac
