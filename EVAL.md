# Harness evaluation (maintainer-only)

A cheap smoke test that compares harness revisions on the same two tasks, tracked in
[issue #13](https://github.com/mattsilv/harness/issues/13). Nothing here ships to
projects: `harness-sync` copies only `template/`. Past runs are in [eval/runs/](eval/runs/).

## Create prompt

> Create a minimal local to-do app: add a nonblank task, mark it complete or incomplete, delete it, and preserve tasks across reloads. Use the project's configured stack, include executable checks for those behaviors, and report what you verified.

## Update prompt

> Add All, Active, and Completed filters to the existing to-do app. Preserve saved tasks and the existing add, toggle, delete, and reload behavior; add executable checks for filtering and report what you verified.

## Run

1. **Create:** in an empty disposable git repo, run
   `HARNESS_SYNC_SOURCE=<this checkout>/template harness-sync init` for the harness
   under test, answer its setup values, and give an agent the create prompt. Setup
   values: Stack "A single static HTML/JS page with localStorage; no build step and no
   server.", Merge policy `on-request`, Secrets none, Maintenance tracking issue none;
   model lines stay at the template defaults.
2. **Update:** copy `eval/fixture/` into a fresh disposable repo, init the harness the
   same way, and give an agent the update prompt. Always start from the committed
   baseline, never from a create run's output.

   Run each task twice per harness revision, each as a fresh headless session given only
   the prompt, and record the CLI version, model, and effort. Report both runs: a
   difference between revisions counts only when it exceeds the gap between a
   revision's own two runs.
3. **Check and count** the result (needs Node 22+ and a local Chrome or Chromium; no
   packages):

   ```bash
   node eval/check.mjs --task create|update <app-dir> [--url URL] \
     [--model M] [--effort E] [--tokens N] [--harness REV] [--out eval/results.jsonl] \
     [--shot shot.png]
   ```

   It serves `<app-dir>` statically (its `index.html`, or the only one below it, such as
   `src/index.html`), or tests `--url` if the app needs its own server,
   and exits 0 only when every check passes. It prints one JSON record: task, harness
   revision (from `.harness/version`), fixture revision, model, effort and tokens
   (`unverified`/`unavailable` unless given), results for each check, and counts. `--shot`
   saves a 1024×768 screenshot of the final state for reviewers.

- **Checks** are fixed and evaluator-owned; the agent's own tests are extra evidence,
  not the score. Create: loads, add, reject blank, toggle, delete, persist across
  reload. Update adds: saved baseline tasks survive, and the All/Active/Completed
  filters work. Elements are found by role and accessible name, so the app's markup
  is free.
- **Counts** are descriptive, not targets: non-blank lines in authored source files,
  whole-line comments, and lines in test files. Excluded: dependencies, build output,
  lockfiles, config, Markdown, and harness docs.

The baseline passes `create` and fails `update` on the three missing filters. To check
that the evaluator still catches a functional failure, drop the save call:

```bash
mkdir -p /tmp/broken && grep -v 'localStorage.setItem' eval/fixture/index.html > /tmp/broken/index.html
node eval/check.mjs --task create /tmp/broken   # FAIL persist_reload, exit 1
```

## Store

Append each run's record to `eval/results.jsonl`. Put its final report, check record,
classifier verdicts, diff (without lockfiles or dependencies), and screenshot in
`eval/runs/<date>-v<N>/`, plus the reviewers' findings. Replace local paths with `~` or
`<run-dir>`, and never commit transcripts.
