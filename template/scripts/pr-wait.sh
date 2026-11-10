#!/usr/bin/env bash
# Waits on the current branch's PR (or the PR number given) until it merges and the merge
# commit's runs on the base branch (the deploy) finish. Exits 1 when the PR can't merge on
# its own (conflicts, a failed check, closed) or a post-merge run did not succeed.
set -euo pipefail
pr=${1:-}
while :; do
  # A gh error (no PR for this branch, network) aborts here with gh's message.
  out=$(gh pr view ${pr:+"$pr"} --json state,baseRefName,mergeStateStatus,statusCheckRollup --jq '"\(.state) \(.baseRefName) \(.mergeStateStatus) \(
    [(.statusCheckRollup // [])[] | select((.conclusion // .state) | IN("FAILURE","ERROR","CANCELLED","TIMED_OUT","ACTION_REQUIRED","STARTUP_FAILURE"))] | length)"')
  read -r state base merge failed <<<"$out"
  case "$state/$merge" in
    MERGED/*)
      sha=$(gh pr view ${pr:+"$pr"} --json mergeCommit --jq .mergeCommit.oid)
      n=0
      while :; do  # runs take a moment to appear; give up after 2 minutes if none do
        runs=$(gh run list --commit "$sha" --json status,conclusion,name,url \
          --jq '.[] | "\(.status)\t\(.conclusion)\t\(.name)\t\(.url)"')
        if [ -z "$runs" ]; then
          n=$((n + 1)); [ "$n" -lt 4 ] || { echo "merged $sha; no run on $base for it"; exit 0; }
        elif ! grep -qv '^completed' <<<"$runs"; then
          echo "merged $sha; runs on $base:"; echo "$runs"
          # A cancelled run is usually superseded by a later merge: check the newest run on the base branch.
          ! cut -f2 <<<"$runs" | grep -qvE '^(success|skipped|neutral)$'; exit
        fi
        sleep 30
      done ;;
    CLOSED/*) echo "PR closed without merging"; exit 1 ;;
    */DIRTY) echo "PR conflicts with $base; CI will not run and auto-merge will wait forever."
             echo "Run scripts/branch-check.sh, rebase onto origin/$base, push."; exit 1 ;;
    */BEHIND) echo "PR refused as not up to date with $base: the ruleset's up-to-date requirement drifted on."
              echo "Turn that requirement off (harness INSTALL.md step 6) instead of updating the branch."; exit 1 ;;
  esac
  if [ "$failed" != 0 ]; then echo "A check failed: gh pr checks $pr"; exit 1; fi
  sleep 30
done
