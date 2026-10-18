# Harness evaluation (maintainer-only)

A cheap smoke test that compares harness revisions on the same three tasks, tracked in
[issue #13](https://github.com/mattsilv/harness/issues/13). Nothing here ships to
projects: the `harness` CLI copies only `template/`. Past runs are in [eval/runs/](eval/runs/).

## Create prompt

> Create a minimal local to-do app: add a nonblank task, mark it complete or incomplete, delete it, and preserve tasks across reloads. Use the project's configured stack, include executable checks for those behaviors, and report what you verified.

## Update prompt

> Add All, Active, and Completed filters to the existing to-do app. Preserve saved tasks and the existing add, toggle, delete, and reload behavior; add executable checks for filtering and report what you verified.

## Delivery prompt

> Change the visible primary heading of the existing to-do app to "My tasks". Preserve its behavior and saved tasks. Prepare the completed change for review and report what you verified.

## Run

1. **Create:** in an empty disposable git repo, run
   `HARNESS_SYNC_SOURCE=<this checkout>/template harness init` for the harness
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
   revision's own two runs. `eval/run.sh claude|opencode create|update <run-dir> [model]`
   does steps 1–3 for one run and saves its usage, final report, check record, and
   screenshot beside `<run-dir>`; start runs one after another.
   **Delivery:** start from the same fresh fixture as update and use the delivery
   prompt. Pass the initial commit with `--baseline <SHA>` when scoring it.
3. **Check and count** the result (needs Node 22+ and a local Chrome or Chromium; no
   packages):

   ```bash
   node eval/check.mjs --task create|update|delivery <app-dir> [--baseline SHA] [--url URL] \
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
- **Delivery** is reported apart from the score and exit code: work committed, on a
  branch, and the default branch still at the baseline commit, as `on-request` expects.
  It assumes the run repo starts with one baseline commit on its default branch.
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

## Bounded harness comparison

[Issue #63](https://github.com/mattsilv/harness/issues/63) adds one delivery regression
from the [v8 pilot](eval/runs/2026-09-23-v8.md): working apps were left uncommitted,
including work on the default branch. The current rules already address this failure.
A baseline that no longer reproduces it is a valid reason to reject another rule.

`eval/compare.py` compares the pinned current template against the same template plus
`eval/candidates/delivery-check.py` and one completion trigger. The candidate stays
maintainer-only. It does not ship through `harness init` or `apply`. Its read-only
helper reports delivery failures; it does not stage, commit, push, or change policy.

The first adapter supports macOS with a current CLI that supports named permission
profiles. It uses an existing ChatGPT login only and refuses API-key fallback. It
launches no model by default:

```bash
python3 eval/compare.py --baseline <commit> --model <model> --effort high \
  --seconds 180 --out /tmp/harness-comparison-plan
# After inspecting the manifest, choose a new output directory for execution:
python3 eval/compare.py --baseline <commit> --model <model> --effort high \
  --seconds 180 --out /tmp/harness-comparison-run --run-subscription
```

Execution is bounded to 12 calls: create, update, and delivery, twice per variant,
with a wall limit per call. Baseline runs first in repetition 1; candidate runs first
in repetition 2. Model sampling is not seeded. Model and effort are requested values,
not verified server versions. New spend is not authorized by this command; check the
existing subscription entitlement before use. Usage comes from CLI events; monetary
cost stays `unavailable` when the provider does not report it.

Each task gets a fresh disposable Git repository, the same setup values and prompt,
no remote, and isolated Git configuration. The initial commit is captured outside
the task workspace. Named permissions deny home/evaluator files and task-tool network,
allow only runtime reads and workspace writes, and prevent task changes to tool config.
A preflight must prove a workspace write, denied private reads, and a denied connection
before any model call. External integrations, web search, hooks, memory, and delegation
are disabled. Model transport remains outside the task-tool sandbox. This is a local
smoke-test boundary, not a claim of resistance to arbitrary sandbox exploits.

The trusted evaluator runs after the model process group exits. It checks the initial
commit against the final repository, blocks page requests outside the local app origin,
and refuses symlink escapes from the served tree. It never trusts the candidate helper's verdict.
Create/update functional scores keep their existing meaning; delivery requires the
heading change, all create checks, and all three delivery checks. Use
`node eval/delivery.mjs <repo> <initial-commit>` to inspect delivery alone.

The output directory keeps the input manifest, per-run events and errors, check records,
and `results.jsonl`. Failed runs and timeouts remain in the results. The runner stops
on a failed isolation preflight. It terminates each process group, including ordinary
child processes; children that deliberately create a new session are outside that
cleanup guarantee. Do not commit raw events, machine paths, or private files. Publish
only inspected records in `eval/runs/` and append compact results to the existing
`eval/results.jsonl`.

Before adoption, require all critical checks to pass, the targeted failure to stop in
every candidate repetition, no new failure, and an explicit cost/time tradeoff decision.
Record the diff, failure evidence, result, decision, and limits in the existing review
log. A candidate that adds cost without a demonstrated gain stays out of `template/`.
The deterministic tests exercise known-good delivery and intentional failures; these
are evaluator validation, not substitutes for model runs.

The first [delivery-helper comparison](eval/runs/2026-10-18-delivery/README.md)
rejected template adoption: both variants passed all six runs, with no demonstrated gain.
