The to-do app now has All, Active, and Completed filters, and saved tasks and the existing behavior still work. It's committed on the `todo-filters` branch (`d279fcb`). The repo has no git remote, so I couldn't open a PR. Your merge policy is "on request", so it isn't merged into `main` yet.

**What changed**
- **`index.html`:** three filter buttons that mark the selected one with `aria-pressed`. The filter only changes what's shown: it isn't saved, and it goes back to All on reload. Saved tasks keep the same `localStorage` key and format, and add, toggle and delete work as before.
- **Styling:** my first screenshots showed nothing marked which filter was selected, and the buttons were small on mobile. The selected filter is now dark, and the buttons are touch-sized.
- **Tests:** `tests/todo.spec.js` runs against the real page in Chromium at a desktop and a mobile screen size, and fails on any network request. Run it with `pnpm install` and then `pnpm test`.
- **Docs:** added `docs/testing.md` and a `docs/README.md` index linking every page.

**What I verified** (all 10 tests pass, 5 at each screen size)
- **Existing behavior:** adding tasks (blank ones are ignored), toggling, deleting, and tasks and their done state surviving a reload.
- **Saved tasks:** tasks already in `localStorage` load unchanged, and switching filters leaves the stored data exactly as it was.
- **Filters:** each filter shows the right tasks in order. The list also updates correctly when you add, toggle or delete while a filter is on (for example, a task you complete leaves the Active view, and a new task doesn't appear under Completed).
- **Screenshots:** I checked them at both sizes after the styling fix.
- **Independent review:** a separate reviewer found no bugs, regressions or weak tests, and confirmed task text is still shown as plain text, not HTML.

**Worth knowing**
- **New dependency:** there was no test setup before, so I added `package.json`, `@playwright/test` (development only, installed with pnpm) and a lockfile.
- **No CI:** the tests only run locally for now. I didn't set up a CI workflow because there's no remote to run it on.