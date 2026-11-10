#!/usr/bin/env bash
# Lists files this branch (or the paths given as arguments) touches that another open PR or
# another local worktree is also changing, so sessions coordinate before they conflict.
# Run before the first edit (with the paths you plan to touch) and again before opening a PR.
# Read-only; exits 0 on overlap (a prompt to message the other session, not an error) and 2 when
# the fetch or gh failed, so a sandboxed run never reads as a clean result.
set -euo pipefail
cd "$(dirname "$0")/.."
main=$(git symbolic-ref -q --short refs/remotes/origin/HEAD || true); main=${main#origin/}
main=${main:-main}
unverified=""
git fetch -q origin "$main" || unverified="git fetch failed"
up=origin/$main
me=$(git branch --show-current)

if [ "$#" -gt 0 ]; then
  mine=$(printf '%s\n' "$@" | sort -u)
else
  mine=$({ git diff --name-only "$up"...HEAD; git diff --name-only HEAD; } | sort -u)
fi
if [ -z "$mine" ]; then echo "no files to check (pass paths, or make changes first)"; exit 0; fi

found=0
report() { # label; candidate files on stdin; returns 0 on overlap (runs in a pipe, so no state)
  local label=$1 hits
  hits=$(comm -12 <(echo "$mine") <(sort -u))
  if [ -n "$hits" ]; then
    echo "$label"; while IFS= read -r f; do echo "  $f"; done <<<"$hits"
    return 0
  fi
  return 1
}

if prs=$(gh pr list --state open --limit 50 --json number,headRefName,files \
    --jq '.[] | "\(.number)\t\(.headRefName)\t\([.files[].path]|join(","))"' 2>/dev/null); then
  while IFS=$'\t' read -r num br files; do
    if [ -z "$num" ] || [ "$br" = "$me" ]; then continue; fi
    tr ',' '\n' <<<"$files" | report "open PR #$num ($br):" && found=1
  done <<<"$prs"
else
  unverified="${unverified:+$unverified; }gh failed, open PRs not checked"
fi

wt=""
while IFS= read -r line; do
  case $line in
    "worktree "*) wt=${line#worktree } ;;
    "branch "*)
      br=${line#branch refs/heads/}
      if [ "$br" = "$me" ]; then continue; fi
      # Mid-merge of main, a worktree's status lists main's files too; count only its own commits then.
      { git diff --name-only "$up"..."$br" 2>/dev/null || true
        git -C "$wt" rev-parse -q --verify MERGE_HEAD >/dev/null || git -C "$wt" status --porcelain | cut -c4-; } \
        | report "worktree $wt ($br):" && found=1 ;;
  esac
done < <(git worktree list --porcelain)

if [ "$found" = 1 ]; then
  echo "overlap: message the owning sessions before editing these: agree who goes first; the other merges $main once that PR lands"
elif [ -z "$unverified" ]; then
  echo "ok: no other open PR or worktree touches these files"
fi
if [ -n "$unverified" ]; then
  echo "UNVERIFIED: $unverified. Rerun with network and git write access."; exit 2
fi
