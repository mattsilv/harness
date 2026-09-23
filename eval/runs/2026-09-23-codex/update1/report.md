Added **All, Active, and Completed** filters in [index.html](~/eval-runs/codex-2026-09-23/update1/index.html). Filtering changes only the visible list; saved tasks keep the same format, and reload starts on All.

Verified with `node --test tests/*.test.mjs` (2 passing checks covering filtering, storage, reload, add, toggle, and delete). I also inspected desktop and mobile screenshots and received an independent review with no functional findings.

Committed as `959d714` on `feat/task-filters`. No Git remote is configured, so I could not open a PR.