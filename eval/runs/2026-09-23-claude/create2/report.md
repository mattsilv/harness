The to-do app is built and all 16 checks pass. It's on the `feat/todo-app` branch in two commits. I haven't merged it: the merge policy is on-request, and the repo has no GitHub remote, so there's nowhere to open a PR yet.

**What's there:** it's the configured stack, a single static page (`index.html` + `app.js`) that saves to the browser's localStorage, with no build step or server. You can open `index.html` directly in a browser.
- **Add:** the text is trimmed, and blank or whitespace-only input is refused with "Enter a task."
- **Complete/incomplete:** a checkbox per task; done tasks are struck through.
- **Delete:** a Delete button per task.
- **Reloads:** tasks and their done state survive a reload. If the saved data is corrupt, the app starts with an empty list instead of breaking.

**Checks:** `pnpm test` runs Playwright browser tests in `tests/todo.spec.js`, 8 tests each at desktop and phone size. The tests load the app from disk and block all other network requests. I also added a CI workflow (`.github/workflows/test.yml`) that runs the same command.

**What I verified:**
- **Tests pass:** 16/16 locally. They cover adding, refusing blank input, toggling both ways, deleting only the chosen task, and persistence after reload (including after toggles and deletes). Also covered: two tasks with identical text, task text that looks like HTML (shown as plain text, not run), and corrupt saved data.
- **Tests catch real breakage:** with saving switched off, the 2 persistence tests failed; with trimming removed, the add and blank-input tests failed. Both changes were reverted afterwards.
- **Opening the file directly works:** in Chromium, 3 tasks and a checked state survived a reload.
- **Layout:** I checked desktop (1280×720) and phone (Pixel 7) screenshots. Everything is visible without scrolling, long tasks wrap, and buttons are large enough to tap.
- **Independent review:** found no correctness or security bugs. I acted on its two small points: I removed a redundant input label and added the identical-text test.

**Not verified:**
- Firefox and Safari; the tests only run in Chromium.
- The CI workflow itself, since there's no remote to run it on.

**Known limitation:** two tasks with identical text also share the same screen-reader label, so a screen-reader user can't tell them or their Delete buttons apart. The app handles them correctly otherwise.

I also added `docs/todo-app.md` and a `docs/README.md` index. Maintenance is skipped because there's no maintenance tracking issue. To go further, add a GitHub remote so I can push and open a PR, then tell me when to merge.