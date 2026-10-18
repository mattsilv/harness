Added All, Active, and Completed filters to [index.html](<run-dir>/index.html). Filters change the visible tasks without changing saved tasks.

Added executable checks in [todo.test.js](<run-dir>/tests/todo.test.js). `node --test tests/todo.test.js` passed: both checks cover filtering and the existing add, toggle, delete, and reload behavior. The delivery check passed.

Commit: `03e01e2` on `add-todo-filters`. PR: not opened; this environment has no remote. Merge state: unmerged. Deployed: no. Screenshot check: unavailable because the repo has no screenshot manifest or browser runner.

Operator check: Open the app with a mix of active and completed tasks, then try each filter.
