# Rationale

Why each rule in `template/` exists. Projects never receive this file. [REVIEW.md](REVIEW.md) uses it to tell load-bearing rules from leftovers.

"Unknown" means no failure was recorded when the rule was written. Those rules are
first in line for cutting unless a reviewer finds evidence they're needed. Add a
line in the same PR whenever you add or change a rule.

## AGENTS.md

Each rule's id, why, source, and latest review sit in an HTML comment under the rule in
[`template/AGENTS.md`](template/AGENTS.md). The `harness` CLI strips those comments
before projects receive the file, and CI checks every rule has a unique id, a why, and a source.

## PROJECT_CONFIG.md

| Rule | Why | Source |
|---|---|---|
| Merge policies: `auto` merges without asking | An agent under `auto` still asked the operator before each merge. | incident, 2026-09 |
| Merge policies: `auto` turns on auto-merge when the PR opens | A subagent waited in a CI poller to merge by hand, stopped, and left a green PR unmerged overnight. | incident, 2026-09 |
| Merge policies: `auto` only with required CI | `auto` merge without required checks would deploy unverified code. `harness check` enforces it. | design |
| Model tiers: planning model as a subagent of the primary session | Operator's tiering assigns planning and hard decisions to a separate model while the primary model codes and runs the session. | operator |
| Model tiers: at least one T3 subagent each for testing and research per implementation task, and a T3 PR review | Operator's choice: keeps testing and research off the T2 session's context and cost. | operator |
| Model tiers: runtime-specific defaults and a separate PR-review default | Model recommendations evolve by role and runtime; changing the review model must not change research and testing defaults. | operator, 2026-10 |
| Frontend review: off by default, independent T2 visual review when enabled | Projects opt into a stronger visual pass without changing the T3 code review or adding always-loaded UI rules; capture runner, command, and initial viewports stay project defaults. | operator, 2026-10 |
| Secrets: operator enters a value through the vendor's native interactive prompt | A value pasted into chat, a command argument, or an agent-run shell reaches the model's context, logs, or shell history; the vendor's no-value prompt keeps it in the operator's terminal. | operator |
| Secrets: Doppler structure, prefix in shared projects | Follows Doppler's one-project-per-app guidance; when apps share a project, generic names collide. | vendor docs, operator |
| Secrets: never print values; check by name or length | A printed value reaches the model's context and logs. | design |
| Secrets: Doppler local dev, CI tokens, expiry, sync targets, rotation, pitfalls | Doppler's documented practices and warnings: no `.env` files, least-privilege expiring CI tokens, one-way sync, the CLI's fallback cache, broad env injection. | vendor docs |
| CI runners: hosted by default; self-hosted records labels, slots, storage, and who adds capacity | Capacity was added by queue length on one host and made the suite slower; recording the measured slot count keeps the next change honest. | incident, 2026-10 |

Values, not rules. Each is the author's default and projects are expected to change
them. Vendors get one line each so a choice is recorded once; only the secrets lines
use "Set during setup", because `harness check` nags about every such line and
most projects don't need every vendor (operator). "Set during setup" values block work until answered because guessing them
(merge policy especially) would bring back the 2026-09 conflicts above.
The merge policy meanings sit on their own line because recording a value used to
replace the line that defined them: the phase 3 pilot's run repos read only
`on-request`, and one model left its work uncommitted in 4 of 4 runs, 2 of them on
the default branch (eval, 2026-09).

## docs/MAINTENANCE.md

A monthly audit, so docs, branches, and live contracts don't rot between
feature work. The interval is a default; monthly replaces an earlier weekly
default, which was more cadence than a small project needs (operator preference).

A weekly list holds only issue triage, run on a T3 subagent, which closes done or
superseded issues, puts others on hold, and assigns the rest to a sprint, and
reports the open-issue count (`harness check` shows it when the list is due).
Parallel agents open issues faster than a monthly review of 30-day-old ones
clears them; the goal is that none lingers unplanned (operator, 2026-09).

The docs check reviews pages changed since the last completed audit (via git log)
and pares them down, dedupes, or merges them so they don't drift; it also confirms
every page is linked from docs/README.md, fixing orphans and broken links, so a
stray page doesn't sit unfindable. (design)

When a list has never completed, its clock starts at the harness install (first commit of `.harness/`), which `harness check` reads from git: 8 sessions on a 2-day-old repo were told the audit was due, and none ran it, since a new repo has nothing to audit (#33). (incident, 2026-09)

The stale-area check (one folder or feature set untouched 4+ months per audit) catches features that are dead or hard to work on before an agent has to touch them under pressure; one area keeps each audit small, in the spirit of kaizen. (operator)

## docs/RUNBOOK.md

A skeleton the project fills in: the exact commands for bootstrapping a worktree, running locally, migrations, remote vendor commands, finishing a PR, launching subagents and review, and known vendor errors. It is on demand, like `docs/languages/`, because the content is project- and vendor-specific (#33). The guidance for many worktrees on one machine (per-worktree values derived from one identifier and passed as flags, runtime secret injection instead of a local env file, two idempotent scripts, collision-proof migration ids) comes from the same sessions: the 53 env-file edits were port changes, and two branches picked the same migration number. (incident, 2026-09)

Test runners take the per-worktree ports and never reuse a server they didn't start: an end-to-end config reused whatever answered on its fixed default port, and another project's dev server held that port, so a default run in any worktree would have silently tested the wrong app. (incident, 2026-09)

## docs/FRONTEND.md and scripts/ui-capture.mjs

The operator reported unclear, verbose, poorly spaced interfaces and requested committed screenshots and independent review (2026-10). One representative per distinct template limits capture cost; a generated sitemap makes references findable. Batch capture and freshness checks prevent ad hoc navigation and stale images. The opt-in workflow extends existing screenshot review to copy that affects fit. The CLI uses the configured browser driver, with project-owned setup hooks for authentication and readiness. Screenshot storage is a project choice because live-data full-page captures can churn tens of megabytes per run (2026-10).

## docs/CI.md

The on-demand checklist behind delivery-14. A project ran 8 self-hosted runner slots on one host; its test suite created databases with write-ahead logging and full durability, so concurrent jobs serialized on the shared disk's filesystem journal and a 20 s suite took 337 s. Adding slots made it worse. The fix was ephemeral (tmpfs) workspaces for test data and slots sized from a measured 1/2/4/8 concurrency run. Dependency caches stay on durable disk because they are read-mostly and a loss only costs a rebuild. The path-filter bullet restates the delivery-4 trap (a path-skipped required workflow never reports) where CI is configured. Self-hosted runners must not run untrusted code, since they keep state between jobs and sit on the project's own network (design). (incident, 2026-10)

## docs/languages/python.md

| Rule | Why | Source |
|---|---|---|
| Use the configured package manager, no ad-hoc global installs | One environment manager per project; which one is a config default (uv). | author |

## scripts/context-watch.py

Reads the last assistant `usage` line of each running subagent transcript (modified in the last two minutes) and of the orchestrating session; context is input plus cache-read plus cache-creation tokens. It only reports, because the orchestrator, not a script, decides when to stop an agent or tell the operator. The transcript format is undocumented, so it exits non-zero rather than guess (after still reporting the other agents). It is runtime-specific to Claude Code, an accepted exception to the no-tool-names rule since projects on other runtimes can ignore it. Running means the transcript changed in the last two minutes, so a long silent tool call can read as not running; a transcript that ends on a finished assistant turn is not running however recent, because reporting a finished agent as `handoff` had the orchestrator relaunch work that was already done. It exits 3 when nothing is running so a wrapper can tell a quiet watch from no watch. The transcripts root honours `CLAUDE_CONFIG_DIR`, as the runtime does (review, #54). Subagents had run past 250k tokens of context unnoticed. (operator, 2026-10)

## scripts/snitch.sh and docs/SUBAGENT-CONTEXT-WATCH.md

A bash loop that runs `context-watch.py` for every session with active subagents and exits on the first new alert, so a background task notification wakes the orchestrator at zero model tokens. It replaced the rule to poll `context-watch.py` every 5 minutes, which cost tokens per poll and was forgotten; it scans every project because the polled script saw one session while other sessions' subagents on the same machine crossed 250k unnoticed. It is a separate file so `context-watch.py` keeps its single-shot contract and tests; at-most-once delivery across snitches comes from a per-key marker created with `noclobber` (atomic on every bash), since a duplicate `handoff` would have two orchestrators relaunch the same subagent and a grep-then-append on the shared log could interleave; the log is append-only because a rewrite would race another snitch's append; `compact-clear` is recorded only after a successful watch, because clearing on a watcher error or an unwatched scan re-fired `compact-now` for an orchestrator that never compacted; the idle timer counts only sessions this snitch may report, so a snitch does not live on another session's activity (review, #54); a per-session heartbeat makes a session's own snitch its sole reporter, because with N snitches sharing one file a session's alert would otherwise land at a random orchestrator and need forwarding (review, #53); `--once` records nothing so a manual check cannot consume an alert; the idle exit follows the Processes rule. The doc is on demand: AGENTS.md carries only the three actions, and the doc holds the output format, env, and dedupe shapes. (#52; incident, 2026-10)

## scripts/overlap-check.sh

Lists the files this branch, or the given paths, share with other open PRs and local worktrees, so parallel sessions agree on an order before they conflict. It always exits 0, because an overlap needs a conversation, not a failure. It came from a project where 12 PRs in 7 days conflicted after parallel edits to the same files. (incident, 2026-10)

## docs/languages/typescript.md

| Rule | Why | Source |
|---|---|---|
| Configured package manager, commit its lockfile | Reproducible installs; which manager is a config default (pnpm). | author |
| `strict`, no unexplained `any`/`@ts-ignore`, typecheck after shared-type changes | Carried over from an existing TypeScript monorepo rule ("type changes require full typecheck"). Incident not recorded. | author |
