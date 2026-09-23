Built with the configured stack (static page, no build/server; pnpm for tooling).

**Files**
- `index.html` — markup/styles, loads `app.js` as a module.
- `app.js` — `createTodoStore` (persistence/validation) + `initTodoApp` (DOM wiring), self-inits in the browser.
- `test/todo.test.js` — `node --test` + jsdom driving the real page.
- `package.json`, `pnpm-lock.yaml`, `.gitignore`, `docs/README.md`, `docs/todo-app.md`.

**Verified** (`pnpm test`, Node v26.3.0, jsdom 30.1.1): 7 passed, 0 failed
- Add: nonblank task is trimmed, rendered, and written to `localStorage`; input clears.
- Blank rejection: `""`, `"   "`, `"\t\n "` add nothing, persist nothing, show an error.
- Complete/incomplete: checkbox click flips state in DOM and storage, both directions.
- Delete: only the targeted task is removed (DOM + storage).
- Persistence across reload: fresh DOM + same storage reproduces tasks and completion state.
- Resilience: corrupted JSON and malformed entries are ignored; app keeps working.

**Not verified / risks**
- "Reload" is simulated by re-mounting a fresh DOM seeded with the prior `localStorage` snapshot; a real browser reload was not exercised.
- No browser rendering/screenshot check (none available here), so visual/mobile layout is unverified.
- No linter/typechecker is configured in the repo; only `node --check` syntax validation was run.

Per the `on-request` merge policy I did not commit or merge. There's also no git remote, so a PR isn't possible from here — say the word and I'll branch and commit, or set up a remote and open a PR.