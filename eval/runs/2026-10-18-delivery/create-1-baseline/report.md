Built the static to-do app in [index.html](<run-dir>/index.html). It saves tasks in `localStorage` and supports adding nonblank tasks, toggling completion, and deleting tasks.

**Verified:** `node --test tests/todo.test.mjs` passed all 5 checks. `node --check app.js` and `git diff --check` passed. I did not verify the UI in a browser; Playwright and Chromium were unavailable.

Commit: `b7a9f81` on `feature/local-todo-app`. PR: none; this evaluation environment has no remote. Merge state: not merged. Deployed: no. Operator check: open `index.html` and try adding, toggling, deleting, then reloading a task.
