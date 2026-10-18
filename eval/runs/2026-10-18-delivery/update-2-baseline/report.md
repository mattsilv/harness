Added **All**, **Active**, and **Completed** filters. Filters preserve the existing saved task format and add, toggle, delete, and reload behavior. The executable check is [scripts/check-filters.mjs](<run-dir>/scripts/check-filters.mjs).

Verified with `./scripts/check-filters.mjs` and `git diff --check`. The check covers all filters, pressed states, task actions, saved data, and reload. `harness-sync check` could not run because the command was blocked by the environment.

Committed as `96927ed` on `feature/todo-filters`; the branch is clean. PR: none; merge state: not merged. Deployment: no.

Check the filters and saved tasks in a browser after reloading the page.
