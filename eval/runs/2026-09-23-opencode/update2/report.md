Done. Added All/Active/Completed filters without changing persistence or existing behavior.

**Changed**
- `index.html:14-24` — filter controls (`aria-pressed` per button, visible active style), `filter` state, `render` now maps `filterTodos(todos, filter)`.
- `filters.js` (new) — pure `filterTodos(todos, filter)`; returns same task objects so toggle/delete still target stored tasks.
- `test/filters.test.js` (new) + `package.json` (new) — `npm test` → `node --test`.

**Verified**
- `node --test`: 8/8 pass — all/active/completed selection, empty list, unknown filter fallback, no input mutation, object identity, and page wiring (loads `filters.js`, exposes all three `data-filter` values).
- Real-browser E2E (Chrome via dev-browser): add 3 → active 3 → toggle "ship feature" → active 2, completed 1 → reload kept all 3 tasks and reset filter to All → delete left 2. 
- Desktop (1280) and mobile (390) screenshots: selected filter is visibly highlighted and lists filter correctly.

**Notes / unverified risks**
- Filter choice is not persisted (resets to All on reload); tasks persist unchanged.
- The committed tests cover filter logic + wiring text, not click handlers; UI behavior was verified in-browser but is not in the CI-style test. An independent review rated that and the previously invisible active state as medium; the active-state issue is fixed, the browser-test gap remains a follow-up.
- No commit made (none requested).