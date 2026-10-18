Added All, Active, and Completed filters to the to-do app. They preserve saved tasks and the existing add, toggle, delete, and reload behavior. Added an executable check at [scripts/test-filters.mjs](<run-dir>/scripts/test-filters.mjs).

Verified the filter and task flows with `node scripts/test-filters.mjs`; `node --check` and `scripts/delivery-check.py` also passed. I did not capture browser screenshots.

Committed as `5e84110` on `codex/todo-filters`. No PR was opened; the branch is unmerged and not deployed. The configured environment has no remote or publishing access.

Operator check: review [index.html](<run-dir>/index.html) and run `node scripts/test-filters.mjs`.
