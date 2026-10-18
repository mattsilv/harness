Built a local to-do app in [index.html](<run-dir>/index.html) and [app.js](<run-dir>/app.js). It rejects blank tasks, lets you add, complete, uncomplete, and delete tasks, and saves them in `localStorage`.

Verified: `node --test app.test.js` passed all four checks; `node --check app.js` and `git diff HEAD^ HEAD --check` passed. The working tree is clean.

Commit: `e5327a7` on `feature/local-todo-app`. PR: none; the repository has no remote. Merge state: unmerged. Deployed: no. Operator check: open `index.html` in a browser and try adding, toggling, deleting, and reloading a task.
