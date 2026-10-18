Implemented the static to-do app in [index.html](<run-dir>/index.html) and [app.js](<run-dir>/app.js). It rejects blank tasks, trims task text, supports completion toggles and deletion, and saves changes in `localStorage`.

Run the executable checks with `node checks.mjs`. They passed, along with JavaScript syntax checks and `scripts/delivery-check.py`.

Committed as `109ae3d` on `feature/local-todo`. The worktree is clean. No PR was opened and the change is not merged; this environment has no configured remote. `harness-sync check` was blocked by the environment. The checks cover task behavior and stored state; I did not verify the UI in a browser.

Operator check: open `index.html` in a browser and confirm the task controls work.
