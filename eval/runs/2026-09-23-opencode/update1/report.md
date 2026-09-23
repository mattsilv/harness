Added All/Active/Completed filters on branch `feat/todo-filters`.

**Changes**
- `filters.js` — one shared `filterTodos(todos, filter)` + `FILTERS`, used by the page (`TodoFilters` global) and tests.
- `index.html:19` — filter button group (`aria-pressed` state), `filter` state, render uses `filterTodos`; `todos` still persist unchanged under `todos` as `[{id,text,done}]`. Add/toggle/delete/reload untouched.
- `tests/filters.test.js`, `tests/e2e.test.js`, `package.json` (`pnpm test`), `docs/todo-app.md`, `docs/README.md`, `.gitignore`, `pnpm-lock.yaml`.

**Verified** (`pnpm test` → 18 pass, 0 fail)
- Unit: each filter, empty list, unknown filter→all, no mutation/reorder, object identity, saved shape.
- E2E (real page in headless Chrome): add shows under All; Active hides done; Completed shows only done; toggling out of Active removes live; delete persists; reload keeps tasks and resets to All.
- Reviewed `tests/screenshots/desktop-all|active|completed.png` and `mobile-all.png`: filters above the fold, clear pressed state, no layout issues.

Not committed — per your merge policy (`on-request`) and the repo having no remote/`gh` auth, I left the work uncommitted on the branch. Want me to commit and/or merge to `main`?