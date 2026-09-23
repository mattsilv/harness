# Codex to-do smoke test — 2026-09-23

Two independent builds of each fixed prompt in [EVAL.md](../../../EVAL.md) ran for issue #13. Create runs began in empty disposable repositories; update runs each began with a fresh copy of `eval/fixture/index.html`. Each repository had harness v8 from `origin/main` at `0e112f88ca4f8118c57b26df9809105810ded1ce`, with the evaluation stack set to one static HTML/JS page and localStorage. The primary model was `gpt-6-sol` at medium effort through Codex CLI 0.156.1.

The fixed evaluator came from PR #17 (`3bd196ab6aac2167c49e8b251d25920866ef58bf`). It ran outside the repository and reported `fixture: unknown` because it determines that field from its own directory; the fixture used for both update runs was from `0e112f88ca4f8118c57b26df9809105810ded1ce`. All behavior checks passed. Source and test line counts are descriptive.

| Run | Checks | Source lines | Test lines | Input tokens | Cached input | Output tokens | Total tokens | Duration | Build subagent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [create1](create1/screenshot.png) | 6/6 | 271 | 58 | 646,573 | 584,448 | 10,023 | 656,596 | 264.633 s | `gpt-6-sol`, medium |
| [create2](create2/screenshot.png) | 6/6 | 244 | 59 | 1,226,021 | 1,130,240 | 18,553 | 1,244,574 | 377.297 s | `gpt-5.6-terra`, high |
| [update1](update1/screenshot.png) | 10/10 | 159 | 81 | 700,881 | 641,536 | 9,174 | 710,055 | 241.476 s | `gpt-5.6-terra`, high |
| [update2](update2/screenshot.png) | 10/10 | 167 | 93 | 884,553 | 811,904 | 8,400 | 892,953 | 196.796 s | `gpt-5.6-terra`, high |

Each run took one primary turn and spawned one review subagent. Token totals add the separately reported primary and subagent usage; cached input is included in input, not added again. Duration is the interval between the primary session's start and task-completion events. The CLI reported no monetary cost, so cost is unavailable. The primary model and effort were verified in the session records. User-level instructions were excluded with an isolated Codex home; repository `AGENTS.md` loaded, and no MCP servers were configured. The CLI injected a plugin recommendation message, but the task prompt itself matched EVAL.md exactly.

Each screenshot is a 960×700 local Chrome capture of the completed app with two sample tasks, “Plan weekly review” and “Archive notes”; the latter is complete. The screenshots illustrate appearance and are separate from the evaluator score. Each build session committed its work on a branch in its disposable repository, as the harness's delivery rule asks. The instruction not to commit applied to the operator agent running them, and nothing was committed to or published from this harness repository during the runs.

Each run folder also has `report.md` (the agent's final report), `jev.json` (the classifier's verdicts on it), and `check-rescored.json` with `check-screenshot.png` from rescoring at `633e7a3` with `--shot`. That screenshot is the same fixed view as the Claude and OpenCode runs; see [the pilot summary](../2026-09-23-v8.md).

| Run | Screenshot | Exact check | Usage | Baseline diff |
|---|---|---|---|---|
| create1 | [PNG](create1/screenshot.png) | [JSON](create1/check.json) | [JSON](create1/usage.json) | [patch](create1/diff.patch) |
| create2 | [PNG](create2/screenshot.png) | [JSON](create2/check.json) | [JSON](create2/usage.json) | [patch](create2/diff.patch) |
| update1 | [PNG](update1/screenshot.png) | [JSON](update1/check.json) | [JSON](update1/usage.json) | [patch](update1/diff.patch) |
| update2 | [PNG](update2/screenshot.png) | [JSON](update2/check.json) | [JSON](update2/usage.json) | [patch](update2/diff.patch) |
