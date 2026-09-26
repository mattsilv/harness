#!/usr/bin/env bash
# Waits on the current branch's PR (or the PR number given) until it merges, and stops
# early with exit 1 when it can't merge on its own: conflicts, a failed check, or closed.
set -euo pipefail
pr=${1:-}
while :; do
  # A gh error (no PR for this branch, network) aborts here with gh's message.
  out=$(gh pr view ${pr:+"$pr"} --json state,baseRefName,mergeStateStatus,statusCheckRollup --jq '"\(.state) \(.baseRefName) \(.mergeStateStatus) \(
    [(.statusCheckRollup // [])[] | select((.conclusion // .state) | IN("FAILURE","ERROR","CANCELLED","TIMED_OUT","ACTION_REQUIRED","STARTUP_FAILURE"))] | length)"')
  read -r state base merge failed <<<"$out"
  case "$state/$merge" in
    MERGED/*) gh run list --branch "$base" --limit 1; exit 0 ;;
    CLOSED/*) echo "PR closed without merging"; exit 1 ;;
    */DIRTY) echo "PR conflicts with $base; CI will not run and auto-merge will wait forever."
             echo "Run scripts/branch-check.sh, rebase onto origin/$base, push."; exit 1 ;;
  esac
  if [ "$failed" != 0 ]; then echo "A check failed: gh pr checks $pr"; exit 1; fi
  sleep 30
done
