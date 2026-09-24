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
| Autonomy: ask-first list | Operator's safety boundary for irreversible, auth, spend, and external actions. Not a model-capability rule. | operator |
| Implementation: libraries over custom code; shared logic; define values once | Unknown. | author |
| Process: scale process to blast radius; review sized to risk | Carried over from the predecessor harness. Incident not recorded. | predecessor |
| Process: stop after two failing review/fix cycles | Carried over from the predecessor harness, to stop fix loops. Incident not recorded. | predecessor |
| Process: handoff primer at the end of each phase | Operator's choice: long sessions accumulate stale context, so each phase starts fresh from a self-contained primer. | operator |
| Security | Operator's safety boundary. | operator |
| Secrets | Operator's safety boundary. | operator |
| Testing | Unknown; general practice. The "never weaken expectations" clause targets agents that make tests pass by editing them. | author |
| UI: screenshots on desktop and mobile | Unknown. | author |
| Delivery: branch + PR, never push to default, never bypass checks | The default branch deploys. | author |
| Delivery: this file is the standing request to commit and open PRs | Coding tools' built-in prompts say to commit only when asked, and one model obeyed that over the branch/PR rule: DeepSeek left its work uncommitted in 6 of 6 eval runs, citing "commit only when asked" (#13). | eval, 2026-09 |
| Delivery: auto-merge only with required CI | `auto` merge without required checks would deploy unverified code. `harness check` enforces it. | design |
| Merge policies: `auto` merges without asking | An agent under `auto` still asked the operator before each merge. | incident, 2026-09 |
| Delivery: one worktree per parallel writer, from a fresh default branch | A tool that shared one working directory across branches made parallel agents see each other's half-finished edits in builds and tests. | incident, 2026-09 |
| Delivery: update before merge; remove worktree and branch after | Unknown. | author |
| Delivery: scope CI to what changed | Full build and test runs on docs-only changes cost time for no signal. Required checks must still report, and a path-skipped required workflow blocks the merge, so the rule says to still pass them. | operator |
| Documentation: wiki of small, cross-linked pages indexed by docs/README.md | Docs drift and duplicate as agents add pages; a linked index lets an agent find the existing page instead of writing a new one. | design |
| Maintenance: follow docs/MAINTENANCE.md | The audit lived only in MAINTENANCE.md, which agents rarely opened, so `harness check` now nags when it's overdue. | incident, 2026-09 |
| Delegation | Carried over from the predecessor harness. Incident not recorded. | predecessor |
| Model selection: never claim an unverifiable model/effort change | Unknown. | author |
| Model tiers: planning model as a subagent of the primary session | Operator's tiering: the strongest model plans, a cheaper one codes and runs the session, and subagents research, test, and review. | operator |
| Model tiers: at least one T3 subagent each for testing and research per implementation task | Operator's choice: keeps testing and research off the T2 session's context and cost. | operator |
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

A monthly audit, so docs, branches, issues, and live contracts don't rot between
feature work. The interval is a default; monthly replaces an earlier weekly
default, which was more cadence than a small project needs (operator preference).

The docs check reviews pages changed since the last completed audit (via git log)
and pares them down, dedupes, or merges them so they don't drift; it also confirms
every page is linked from docs/README.md, fixing orphans and broken links, so a
stray page doesn't sit unfindable. (design)

The stale-area check (one folder or feature set untouched 4+ months per audit) catches features that are dead or hard to work on before an agent has to touch them under pressure; one area keeps each audit small, in the spirit of kaizen. (operator)

## docs/languages/python.md

| Rule | Why | Source |
|---|---|---|
| Use the configured package manager, no ad-hoc global installs | One environment manager per project; which one is a config default (uv). | author |

## docs/languages/typescript.md

| Rule | Why | Source |
|---|---|---|
| Configured package manager, commit its lockfile | Reproducible installs; which manager is a config default (pnpm). | author |
| `strict`, no unexplained `any`/`@ts-ignore`, typecheck after shared-type changes | Carried over from an existing TypeScript monorepo rule ("type changes require full typecheck"). Incident not recorded. | author |
