I added All, Active, and Completed filters to the to-do app, and all 10 new browser tests pass on desktop and mobile Chromium. The work is committed on the `feat/todo-filters` branch. I haven't merged it: your merge policy is merge-on-request, and the repo has no git remote, so I couldn't open a PR.

**What changed**
- `index.html`: filter buttons above the list, with the selected one shown dark and marked for screen readers. The filter only changes what's shown. It doesn't change how tasks are saved, isn't saved itself, and goes back to All on reload.
- `tests/todo.spec.js`: Playwright tests that run the real `index.html` with all network calls blocked. Run them with `pnpm test`.
- I also added `package.json`, a lockfile, a GitHub Actions workflow that runs the tests, and short docs pages (`docs/README.md`, `docs/todo-app.md`, `docs/testing.md`).

**What the tests check (each runs on desktop and mobile)**
- **Existing behavior:** adding works and blank input is ignored; toggling and deleting work; after a reload the remaining task is still there and still checked, and the saved data is correct.
- **Tasks saved before this change:** they load unchanged, All is selected by default, and filtering doesn't rewrite them.
- **Filtering:** Active shows only unfinished tasks, Completed shows only finished ones, All shows everything, and the right button is marked as selected.
- **Actions while filtered:**
  - Completing a task while on Active hides it.
  - Adding a task while on Completed saves it but keeps it hidden.
  - Un-checking a task while on Completed hides it.
  - Deleting while on Active works.
  - The saved tasks come out correct at the end.

**Also checked**
- **Screenshots:** the first desktop and mobile screenshots showed no visible selected filter and cramped spacing. I added a little styling (dark selected button, larger touch targets) and checked the screenshots again.
- **Review:** a separate review agent found no significant issues. It noted one older issue: if two tasks have the same text, their checkboxes and Delete buttons get identical screen-reader labels.
- **Not verified:** the GitHub Actions workflow has never run, because there's no remote. I only ran the tests locally.