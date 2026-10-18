Changed the visible heading to **“My tasks”** in [index.html](<run-dir>/index.html:9). The task code, page title, and `localStorage` key remain unchanged, so saved tasks are preserved.

Verified: the diff contains only the heading change, `git diff --check` passes, and `scripts/delivery-check.py` passes with a clean feature branch. I did not run the app. The overlap check found no conflicting work. `harness-sync check` could not run because the environment denied permission.

**Review state:** committed on `change/my-tasks-heading` as `a9bf29b`. No PR opened or merge performed; the repo config says not to publish from this environment. Not deployed.

**Operator check:** Review the heading in [index.html](<run-dir>/index.html:9).
