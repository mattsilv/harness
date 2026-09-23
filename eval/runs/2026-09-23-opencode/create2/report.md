Done. Built per the configured stack (static page + `localStorage`, no build, no server, no deps) on branch `feat/todo-app`.

**Files**
- `index.html` — markup/styles; mounts on `window.localStorage`
- `todo.js` — storage-agnostic store: validation, toggle, delete, persistence (key `todos.v1`)
- `app.js` — DOM wiring, renders with `textContent` (no HTML injection)
- `tests/` — executable checks (`todo.test.js`, `app.test.js`, `page.test.js`, `fake-dom.js`)
- `package.json` — `npm test` → `node --test`
- `docs/README.md` (new index) + `docs/todo-app.md`

**Verified**
- `npm test`: **13/13 pass** on Node v26.3.0 — nonblank add + trim, blank/whitespace/non-string rejected with no task, toggle complete↔incomplete, delete only the target, persistence across a fresh store (reload), corrupt/malformed storage degrades to empty, plus DOM-level add/toggle/delete and a check that the real `index.html` exposes the expected ids/scripts.
- Rendered `index.html` in headless Chrome at desktop 520px and mobile 390px: layout is clean, no overflow, Add/Delete reachable, completed item struck through.

**Notes / unverified**
- Changes are left uncommitted on `feat/todo-app` (you didn't ask me to commit); no merge or push, consistent with the `on-request` merge policy. No remote exists, so no PR.
- Real-browser `localStorage` persistence wasn't driven end-to-end (only confirmed the page boots against `window.localStorage`); persistence is covered by the store/DOM tests.