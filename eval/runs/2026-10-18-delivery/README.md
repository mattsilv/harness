# Delivery-helper smoke test — 2026-10-18

**Decision: do not adopt the helper in `template/`.** Both variants completed all
six tasks with clean commits on feature branches and unchanged default branches.
The old delivery failure did not recur. The candidate added instructions and wall
time without a demonstrated benefit. Keep it only as a maintainer experiment.
This valid no-go result completes [#63](https://github.com/mattsilv/harness/issues/63).

## Evidence and design

The [v8 pilot](../2026-09-23-v8.md) recorded four uncommitted runs, including default-
branch work. The current harness already has delivery rules. We compared pinned
baseline `7e7f3f44d16d0276641da461f15606ae6a9a0070` against that baseline plus the
exact [candidate helper](candidate.py) and the one-line trigger in
[manifest.json](manifest.json). No security or approval rule changed.

Ran `python3 eval/compare.py --baseline 7e7f3f44 --model gpt-6-luna --effort high
--seconds 180 --out <new-directory> --run-subscription` as one command. The
[manifest](manifest.json) records full input hashes, prompts, CLI version, and limits.
The requested model was `gpt-6-luna`, effort high, CLI `0.163.0`; the server model
version was not independently verified. Sampling was not seeded. Each task used a
fresh repository, identical permissions, and a 180-second model-call limit.
Baseline ran first in repetition 1, candidate first in repetition 2.

All 12 calls completed. No model run failed or timed out. One earlier setup attempt
stopped before any model call because it omitted generated `CLAUDE.md`. Preparation
was fixed to use the real pinned `harness init` command before this fresh experiment.
No model output was discarded or rerun.

## Outcome

| Measure (six runs per variant) | Baseline | Candidate |
|---|---:|---:|
| Functional checks, all tasks | 6/6 runs passed | 6/6 runs passed |
| Clean committed delivery on a feature branch | 6/6 | 6/6 |
| Default branch unchanged | 6/6 | 6/6 |
| Helper command observed | n/a | 6/6 |
| Total model wall seconds | 498.737 | 664.163 |
| Input tokens, including cached input | 1,644,430 | 1,761,921 |
| Cached input tokens (subset of input) | 1,419,136 | 1,600,256 |
| Output tokens | 28,323 | 28,901 |
| Initial instruction bytes per run | 14,447 | 14,551 |
| Monetary cost | unavailable | unavailable |

Instruction bytes count `AGENTS.md`, `CLAUDE.md`, and `PROJECT_CONFIG.md`. The helper
is loaded on demand; observed command invocation is evidence of its trigger, not
proof of correctness. Deterministic tests establish its pass and failure behavior.
Token counts are provider-reported event totals; do not add cached input again.
The runs used an existing subscription. No dollar estimate is inferred from tokens.
The candidate took 165.426 seconds more in this sample. Two repetitions per task
cannot establish a reliable latency or success-rate effect. Counts of source lines
include installed harness scripts and are descriptive, not app-size comparisons.

## Scoring correction

The original evaluator selected a toggle whose accessible name contained “Delete
me” as a delete button. This falsely failed deletion and persistence in three create
runs: baseline repetition 1 and both candidate repetitions. A regression fixture
reproduced the error before the fix. The corrected evaluator anchors delete action
names and counts `aria-pressed` buttons for blank-task checks. Another regression
proves a tag named `main` cannot substitute for a default branch.

All 12 frozen outputs were rescored with the same corrected evaluator and their
original externally pinned initial commits. [Original records](original-results.jsonl)
remain unchanged. [Corrected records](results.jsonl) retain all outcomes and usage;
the manifest records old and new evaluator hashes. Exactly six check results changed:
delete and persistence changed from fail to pass in those three runs. Every other
functional and delivery result remained unchanged. No model was rerun for rescoring.
The published candidate is the exact tested helper; its current maintainer copy also
has the later branch-ref hardening. That hardening does not change these valid repos.

## Validation and limits

- Known-good fixture passes; deliberate missing-save and blank-input failures are
  detected. Dirty work, changed default branches, missing baselines, and tag-only
  defaults fail deterministic delivery tests. The full suite passed 61 tests.
- Per-run sandbox preflight proved workspace writes, denied private reads, and denied
  tool network access. Agents could not access evaluator files. Independent probes
  found zero second-origin browser requests and no local Git fsmonitor execution.
- Independent review approved both scoring fixes and uniform rescoring. No template
  files changed. Scratch initialization confirmed no evaluator, fixture, or execution
  trace is distributed by the harness CLI.
- This tests small local static apps and local branch delivery. It does not test
  hosted PRs, production deployment, arbitrary malicious sandbox escapes, or other
  models. Ordinary child process groups are stopped; deliberately detached sessions
  remain outside the runner's cleanup guarantee.

Each run directory contains its final patch, evaluator record, screenshot, and model
report. Reports are agent claims; the evaluator records are the score. Local paths
were replaced with placeholders. Raw transcripts and credentials are not published.
Previous template changes were not evaluated individually; their effect is unknown.
No new root rule is justified by these results.

## Runs

| Run | Functional score | Seconds |
|---|---:|---:|
| [create-1-baseline](create-1-baseline/check.json) | 6/6 | 123.447 |
| [create-1-candidate](create-1-candidate/check.json) | 6/6 | 108.98 |
| [create-2-candidate](create-2-candidate/check.json) | 6/6 | 138.043 |
| [create-2-baseline](create-2-baseline/check.json) | 6/6 | 66.845 |
| [update-1-baseline](update-1-baseline/check.json) | 10/10 | 83.135 |
| [update-1-candidate](update-1-candidate/check.json) | 10/10 | 123.637 |
| [update-2-candidate](update-2-candidate/check.json) | 10/10 | 91.919 |
| [update-2-baseline](update-2-baseline/check.json) | 10/10 | 89.024 |
| [delivery-1-baseline](delivery-1-baseline/check.json) | 7/7 | 60.142 |
| [delivery-1-candidate](delivery-1-candidate/check.json) | 7/7 | 100.853 |
| [delivery-2-candidate](delivery-2-candidate/check.json) | 7/7 | 100.731 |
| [delivery-2-baseline](delivery-2-baseline/check.json) | 7/7 | 76.144 |
