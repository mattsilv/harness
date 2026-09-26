# Rationale

Why each rule in `template/` exists, one line per rule. Projects never receive this
file. [REVIEW.md](REVIEW.md) uses it to tell load-bearing rules from leftovers.

"Unknown" means no failure was recorded when the rule was written. Those rules are
first in line for cutting unless a reviewer finds evidence they're needed. Add a
line in the same PR whenever you add or change a rule.

## AGENTS.md

| Rule | Why | Source |
|---|---|---|
| Priorities order | Unknown. A tiebreaker when rules pull in different directions. | author |
| Configuration: one config file, no duplicated policy | Five tools once gave agents contradictory merge and push rules, and which one won depended on load order. | incident, 2026-09 |
| Configuration: ask for "Set during setup" values first | Guessing merge policy would bring back the conflict above. `harness check` repeats the question until it's answered. | design |
| Autonomy: merge/deploy per merge policy | Same merge-rule conflict as above. The policy is now one value per project. | incident, 2026-09 |
| Autonomy: end each task report with PR and merge state, deploy state, and a link to check | The operator had to ask for status in most sessions of one project ("are we done here" in 5, "is ci done", "did that deploy?", "link me to what I'm checking") (#33). | incident, 2026-09 |
| Autonomy: ask-first list | Operator's safety boundary for irreversible, auth, spend, and external actions. Not a model-capability rule. | operator |
| Implementation: libraries over custom code; shared logic; define values once | Unknown. | author |
| Process: scale process to blast radius; review sized to risk | Carried over from the predecessor harness. Incident not recorded. | predecessor |
| Process: stop after two failing review/fix cycles | Carried over from the predecessor harness, to stop fix loops. Incident not recorded. | predecessor |
| Process: context lives in the issue; handoff is a short prompt naming it | Long self-contained primers were slow to write and read, and their context was lost once pasted. Keeping it in the issue makes the handoff trivial and the context durable. Fresh sessions still avoid stale context. | operator, 2026-09 |
| Security | Operator's safety boundary. | operator |
| Secrets | Operator's safety boundary. | operator |
| Testing | Unknown; general practice. The "never weaken expectations" clause targets agents that make tests pass by editing them. | author |
| UI: screenshots on desktop and mobile for layout, styling, or structure changes | Unknown for the screenshots themselves. Copy-only changes are exempt because a screenshot of changed words catches nothing a diff doesn't, and it slowed small PRs. | operator, 2026-09 |
| UI: use the frontend-design skill for any frontend change | Unknown. Agents defaulted to templated-looking UI without a nudge to reach for the design skill first. | operator, 2026-09 |
| Delivery: branch + PR, never push to default, never bypass checks | The default branch deploys. | author |
| Delivery: this file is the standing request to commit and open PRs | Coding tools' built-in prompts say to commit only when asked, and one model obeyed that over the branch/PR rule: DeepSeek left its work uncommitted in 6 of 6 eval runs, citing "commit only when asked" (#13). | eval, 2026-09 |
| Delivery: auto-merge only with required CI | `auto` merge without required checks would deploy unverified code. `harness check` enforces it. | design |
| Merge policies: `auto` merges without asking | An agent under `auto` still asked the operator before each merge. | incident, 2026-09 |
| Merge policies: `auto` turns on auto-merge when the PR opens | A subagent waited in a CI poller to merge by hand, stopped, and left a green PR unmerged overnight. | incident, 2026-09 |
| Delivery: one worktree per parallel writer, from a fresh default branch | A tool that shared one working directory across branches made parallel agents see each other's half-finished edits in builds and tests. | incident, 2026-09 |
| Delivery: every branch, even one in the main checkout, starts from the fetched remote default branch | A session cut a branch from a local default branch that lacked a PR merged 12 minutes earlier; its PR conflicted on open, got no CI run, and auto-merge waited silently. `scripts/branch-check.sh` and `scripts/pr-wait.sh` catch it before and while waiting. | incident, 2026-09 |
| Delivery: rebase only on a conflict | With branch protection's "require branches to be up to date" on, every merge invalidated every other open PR's check, so parallel agents queued behind each other for reruns. A conflict must be fixed because GitHub runs no CI on a conflicting PR and auto-merge never fires. Overlapping files alone no longer trigger a rebase: CI runs again on the default branch after each merge and gates the deploy, which catches the rare semantic clash. | incident, 2026-09 |
| Delivery: remove worktree and branch after merge | Unknown. | author |
| Delivery: sync worktrees to the default branch after each merge, skip dirty ones, notify the owning agent | Unknown. Parallel branches drifted from a merged default branch until their own PR update, hiding conflicts and stale dependencies from the agents working on them. | operator, 2026-09 |
| Delivery: scope CI to what changed | Full build and test runs on docs-only changes cost time for no signal. Required checks must still report, and a path-skipped required workflow blocks the merge, so the rule says to still pass them. Docs-only branches no longer update from the default branch first (see the update rule above). | operator |
| Documentation: wiki of small, cross-linked pages indexed by docs/README.md | Docs drift and duplicate as agents add pages; a linked index lets an agent find the existing page instead of writing a new one. | design |
| Maintenance: follow docs/MAINTENANCE.md | The audit lived only in MAINTENANCE.md, which agents rarely opened, so `harness check` now nags when it's overdue. | incident, 2026-09 |
| Delegation | Carried over from the predecessor harness. Incident not recorded. | predecessor |
| Delegation: search open issues before filing found work | Parallel sessions filed the same issue twice, two pairs in two days (#33). | incident, 2026-09 |
| Delegation: start a subagent on newly found work unless it needs an operator decision | Filing discovered work and stopping left it waiting on the operator to start another session mid-sprint. | operator, 2026-09 |
| Apply rules unprompted; quick questions exempt | The operator had to say "use our harness" before feature work. | operator, 2026-09 |
| Model selection: never claim an unverifiable model/effort change | Unknown. | author |
| Model tiers: planning model as a subagent of the primary session | Operator's tiering: the strongest model plans, a cheaper one codes and runs the session, and subagents research, test, and review. | operator |
| Model tiers: at least one T3 subagent each for testing and research per implementation task, and a T3 PR review | Operator's choice: keeps testing and research off the T2 session's context and cost. | operator |
| Runbook: read docs/RUNBOOK.md before bootstrapping, running, or calling a vendor CLI; record what took more than one attempt | Every worktree re-derived the local dev recipe (38 fresh installs, 53 env-file edits, 6 port collisions, the hosting CLI invoked 4 ways), and vendor errors learned by failure were recorded nowhere reusable (#33). | incident, 2026-09 |
| Migrations: check other sessions and worktrees before adding one; pause on conflict | Two parallel branches both created the same migration number, and a table rebuild on one failed after another branch changed a child table. Worktrees on one machine are the normal case (#33). | incident, 2026-09 |
| Languages: read `docs/languages/<language>.md` before editing | Keeps language rules out of every session's context. | design |

## PROJECT_CONFIG.md

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

## docs/languages/python.md

| Rule | Why | Source |
|---|---|---|
| Use the configured package manager, no ad-hoc global installs | One environment manager per project; which one is a config default (uv). | author |

## docs/languages/typescript.md

| Rule | Why | Source |
|---|---|---|
| Configured package manager, commit its lockfile | Reproducible installs; which manager is a config default (pnpm). | author |
| `strict`, no unexplained `any`/`@ts-ignore`, typecheck after shared-type changes | Carried over from an existing TypeScript monorepo rule ("type changes require full typecheck"). Incident not recorded. | author |
