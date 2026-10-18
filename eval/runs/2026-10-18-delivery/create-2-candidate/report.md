Implemented the local to-do app. It trims task text, rejects blank tasks, lets you mark tasks complete or incomplete, delete them, and saves them in browser `localStorage`.

Checks passed: `node --test tests/todo.test.js` (5 tests) and `python3 scripts/delivery-check.py`. The app has no external runtime dependencies. The environment lacked Playwright and a browser, so I could not check desktop or mobile screenshots.

Run it with `python3 -m http.server 8000`, then open `http://localhost:8000`.

**Delivery:** committed as `45b8964` on `feat/local-todo-app`. No PR was opened because this checkout has no remote. It is not merged and was not deployed.

**Operator check:** Open the app and add a task, reload the page, then try completing and deleting it. [README.md](<run-dir>/README.md)
