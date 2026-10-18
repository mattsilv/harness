Added All, Active, and Completed filters. Filter changes only affect the display; saved tasks and add, toggle, delete, and reload behavior remain intact.

Verified with `scripts/check-todo.mjs`: all filters, add, toggle, delete, and reload persistence passed. `git diff --check` passed, and the branch is clean. `harness-sync check` could not run because the environment denied it. The overlap check found no local worktree conflict; it could not fetch or check open PRs because this repository has no remote.

Branch: `add-todo-filters`. Commit: `c56aef6`.

PR: none opened; merge state: not merged; deployed: no. Operator check: review [index.html](<run-dir>/index.html) and run [check-todo.mjs](<run-dir>/scripts/check-todo.mjs).
