#!/usr/bin/env bash
# Tells a session whether its branch must be rebased before it opens or waits on a PR
# (AGENTS.md Delivery: rebase only on a conflict). Exit 1 on a conflict, 0 otherwise.
set -euo pipefail
cd "$(dirname "$0")/.."
main=$(git symbolic-ref -q --short refs/remotes/origin/HEAD || true); main=${main#origin/}
main=${main:-$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)}
git fetch -q origin "$main"
up=origin/$main
base=$(git merge-base HEAD "$up")
echo "branch $(git branch --show-current): $(git rev-list --count "HEAD..$up") commit(s) behind $up"

status=0
# merge-tree exits 0 when clean, 1 on conflicts (tree oid, then conflicted paths), >1 on error.
rc=0; conflicts=$(git merge-tree --write-tree --name-only --no-messages "$up" HEAD) || rc=$?
if [ "$rc" -gt 1 ]; then exit "$rc"; fi
if [ "$rc" = 0 ]; then
  echo "ok: no conflicts; no rebase needed (CI reruns on $main after the merge)"
  overlap=$(comm -12 <(git diff --name-only "$base" "$up" | sort) \
                     <(git diff --name-only "$base" HEAD | sort))
  if [ -n "$overlap" ]; then
    echo "info: $main also changed these files since this branch started:"
    while IFS= read -r f; do echo "  $f"; done <<<"$overlap"
  fi
else
  echo "CONFLICT with $up (no CI runs on a conflicting PR and auto-merge never fires); rebase onto $up:"
  echo "$conflicts" | tail -n +2 | sed 's/^/  /'
  status=1
fi

if pr=$(gh pr view --json number,mergeable,mergeStateStatus \
    --jq '"PR #\(.number): mergeable=\(.mergeable) mergeStateStatus=\(.mergeStateStatus)"' 2>/dev/null); then
  echo "$pr"
fi
exit $status
