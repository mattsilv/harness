I built the to-do app as a single static HTML/JS page that saves tasks in the browser's `localStorage`, which is the project's configured stack. All 32 tests pass (16 checks, each run at desktop and mobile sizes). The work is committed on branch `feat/todo-app`. It isn't merged: the repo has no remote to open a PR against, and the merge policy is to merge only when you ask.

**Run it:** open `src/index.html` directly, or run `pnpm start` and go to http://127.0.0.1:4173. Run the checks with `pnpm install`, then `pnpm test`.

**What the tests check** (they drive a real browser):
- **Add:** text is trimmed, the input clears, and Enter also adds. Empty, spaces-only and tab-only input is rejected with "Enter a task." and nothing is saved.
- **Complete / incomplete:** checking and unchecking a task is saved, and the right state shows after each reload.
- **Delete:** deleting the middle of three tasks removes only that one, and it stays gone after reload.
- **Reload:** the order and checked state of tasks are the same after a reload.
- **Opened from disk:** adding a task and reloading works when the page is opened as a file.
- **Robustness:**
  - Task text shows as plain text, so HTML typed in can't run.
  - Corrupted saved data doesn't crash the page.
  - If the browser can't save (storage full or blocked), an error appears and nothing changes.
  - After a delete, focus moves to the next task.
  - The page scrolls sideways at neither size.
- Every test fails if the page throws an error or tries to reach the internet.

**Proof the tests catch breakage:** with saving disabled, 8 tests failed; with the blank-task check removed, 6 failed. I looked at desktop and mobile screenshots and fixed some cramped row spacing and a gap above the list.

**Found by an independent review and fixed**, each with a test that failed before the fix:
- Opening the page from disk loaded no code in Chrome, so nothing worked; I confirmed this directly.
- If the browser couldn't save, the list on screen no longer matched what was stored, and no error was shown.
- After deleting a task, keyboard focus was lost.

**Not verified:**
- Tests ran only in Chromium, not Safari or Firefox.
- There is no CI because the repo has no remote.

I added `docs/README.md` as the docs index and `docs/todo-app.md` describing the app. Playwright is the only new dependency, and it's for testing only.