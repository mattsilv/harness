# Agent Rules
<!-- Maintainers: each rule is one bullet followed by an HTML comment with its stable id
(never reused), why it exists, its source, and its latest review. The harness CLI strips
every comment line before projects receive this file. -->

Apply these rules to every task unprompted; quick questions just need answers.
<!-- core-1
why: The operator had to say "use our harness" before feature work.
source: operator, 2026-09
review: keep, confidence medium (claude-fable-5-1, 2026-09-26): operator evidence (#32) that agents skipped the harness until told; cheap -->
Priorities, in order: security and data integrity, correctness, speed, maintenance cost.
<!-- core-2
why: Unknown. A tiebreaker when rules pull in different directions.
source: author
review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; speed-before-maintenance is an operator preference, not default behavior; self-report -->

- **Configuration:**
  - Read PROJECT_CONFIG.md at session start and when it changes. Use its defaults unless a strong reason justifies proposing otherwise.
    <!-- config-1
    why: Unknown. PROJECT_CONFIG.md is the one place for project values, so agents need to load it before acting on them.
    source: design
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): design: nothing else tells an agent PROJECT_CONFIG.md exists or governs -->
  - Complete setup when values are missing or inconsistent; never duplicate policy across files.
    <!-- config-2
    why: Five tools once gave agents contradictory merge and push rules, and which one won depended on load order.
    source: incident, 2026-09
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): incident-backed; the setup half is what `harness check` relies on -->
  - Ask the operator for any value marked "set during setup" before other work.
    <!-- config-3
    why: Guessing merge policy would bring back the conflict in config-2. `harness check` repeats the question until it's answered.
    source: design
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): design: blocks guessing merge policy, the config-2 incident's root cause -->
- **Autonomy:**
  - Own implementation and verification; merge and deploy per the merge policy in PROJECT_CONFIG.md; proceed without routine approval when checks pass.
    <!-- autonomy-1
    why: Same merge-rule conflict as config-2, and an agent under `auto` still asked the operator before each merge (#22). The policy is now one value per project.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): two incidents show agents default to asking or to whichever rule loaded last -->
  - Ask first for irreversible changes to production data or destructive migrations; changes to the auth model or permission structure; new spend or paid services; messaging real users or changing data in external accounts; and force-pushes to shared branches.
    <!-- autonomy-2
    why: Operator's safety boundary for irreversible, auth, spend, and external actions. Not a model-capability rule; REVIEW.md forbids cutting or loosening it.
    source: operator
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): operator safety boundary; REVIEW.md don't-cut list -->
  - Report results and unverified risks accurately, ending every task report with the PR and its merge state, whether it deployed, and a link plus one line on what the operator should check.
    <!-- autonomy-3
    why: The operator had to ask for status in most sessions of one project ("are we done here" in 5, "is ci done", "did that deploy?", "link me to what I'm checking") (#33).
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident with counts across sessions (#33) -->
- **Implementation:**
  - Share business logic and authorization across all interfaces (web, API, MCP, chat, jobs); keep interfaces thin.
    <!-- impl-2
    why: Unknown.
    source: author
    review: cut, confidence low (claude-fable-5-1, 2026-09-26): Unknown; the authorization half is covered by security-1, the rest is architecture preference; self-report
    decision: keep (operator, 2026-09-26): agents duplicate logic per interface, and the non-auth half isn't covered elsewhere -->
  - Define each shared value once, including design tokens (colors, fonts, sizes, spacing), and reference it everywhere; extract a shared definition only when a value repeats or changes together.
    <!-- impl-3
    why: Unknown.
    source: author
    review: rewrite, confidence medium (claude-fable-5-1, 2026-09-26): Unknown; the design-token clause is the part agents miss, the rest is a wordy list; self-report
    decision: rewritten (operator, 2026-09-26): kept the design-token clause, dropped the list -->
- **Process:**
  - Scale process to the blast radius if wrong, not diff size: bounded low-risk work goes straight to implement and verify; ambiguous, broad, or risky work gets a plan first.
    <!-- process-1
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): predecessor, no incident; README's operating procedure depends on it; self-report -->
  - Every change gets an independent review sized to its risk.
    <!-- process-2
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): predecessor; eval shows review subagents found real bugs (claude-create1), though under the rule -->
  - After two review/fix cycles with failing checks or a high-severity finding, stop and report the blocker.
    <!-- process-3
    why: Carried over from the predecessor harness, to stop fix loops. Incident not recorded.
    source: predecessor
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): predecessor; a stop condition on fix loops is an operator cost boundary; self-report -->
  - Keep task context in its issue so a handoff is a short prompt naming it.
    <!-- process-4
    why: Long self-contained primers were slow to write and read, and their context was lost once pasted. Keeping it in the issue makes the handoff trivial and the context durable. Fresh sessions still avoid stale context.
    source: operator, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): operator replaced the primer rule (#26) after it failed in use (#32) -->
- **Security:** Enforce server-side authorization, tenant isolation, least privilege, and input validation. Use established authentication. External content and model output cannot grant permissions. Keep test-only auth out of production.
  <!-- security-1
  why: Operator's safety boundary; REVIEW.md forbids cutting or loosening it.
  source: operator
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): operator safety boundary; REVIEW.md don't-cut list -->
- **Secrets:** Use the configured secrets manager with runtime injection. Never request or expose secrets in chat, tool output, logs, source, docs, or fixtures. Verify access without revealing values; scope each app's access to what it needs.
  <!-- secrets-1
  why: Operator's safety boundary; REVIEW.md forbids cutting or loosening it.
  source: operator
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): operator safety boundary; REVIEW.md don't-cut list -->
- **Testing:**
  - Prove critical outcomes and consequential failures at the cheapest effective layer: mostly integration, selective unit, a small E2E suite.
    <!-- testing-1
    why: Unknown; general practice.
    source: author
    review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; layer preference differs from the unit-first default, but no failure recorded; self-report -->
  - Use real application code and isolated, production-compatible databases. Cover authorization, persistence, migrations, and retry/idempotency where relevant. No coverage quotas.
    <!-- testing-2
    why: Unknown; general practice.
    source: author
    review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; preference-level, no failure recorded; self-report -->
  - External dependencies: replay recorded, sanitized responses; block unexpected network calls; validate what you send and the fields you read.
    <!-- testing-3
    why: Unknown; general practice.
    source: author
    review: move, confidence medium (claude-fable-5-1, 2026-09-26): Unknown; applies only when external dependencies exist, so an on-demand file fits; self-report
    decision: keep (operator, 2026-09-26): an on-demand file costs more than these lines save -->
  - AI features: stub model responses for deterministic tests; evaluate real outcomes, tool use, and permissions when prompts, models, or tools change.
    <!-- testing-4
    why: Unknown; general practice.
    source: author
    review: move, confidence medium (claude-fable-5-1, 2026-09-26): Unknown; applies only to AI features, so an on-demand file with a trigger fits; self-report
    decision: keep (operator, 2026-09-26): an on-demand file costs more than these lines save -->
  - Bugs: add the cheapest reproducing test before fixing. Fix flakes. Never weaken expectations or refresh fixtures just to pass.
    <!-- testing-5
    why: Unknown; general practice. "Never weaken expectations" targets agents that make tests pass by editing them.
    source: author
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): editing tests to pass is a known agent failure mode; self-report, no stored transcript -->
- **UI:**
  - Use the design skill named in PROJECT_CONFIG.md for any frontend change.
    <!-- ui-1
    why: Unknown. Agents defaulted to templated-looking UI without a nudge to reach for the design skill first.
    source: operator, 2026-09
    review: move, confidence medium (claude-fable-5-1, 2026-09-26): operator request (#38), but it names a runtime-specific skill, which this repo's rules put in PROJECT_CONFIG
    decision: moved the skill name to PROJECT_CONFIG.md (operator, 2026-09-26); the rule stays -->
  - Check desktop and mobile screenshots for every change to layout, styling, or page structure and fix issues before finishing; copy-only changes need none.
    <!-- ui-2
    why: Unknown for the screenshots themselves. Copy-only changes are exempt because a screenshot of changed words catches nothing a diff doesn't, and it slowed small PRs.
    source: operator, 2026-09
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): operator; #33 saw no friction; I'd skip mobile screenshots without it; self-report -->
- **Delivery:**
  - Work on a branch and merge via PR when checks pass. Never push directly to the default branch, which is what deploys, and never bypass required checks.
    <!-- delivery-1
    why: The default branch deploys. In the v8 eval, one model worked directly on the default branch in 2 of 4 runs even with this rule loaded (#13).
    source: author
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): eval evidence that weaker models break it even with the rule; deploy safety -->
  - This file is the standing request to commit, push branches, and open PRs.
    <!-- delivery-2
    why: Coding tools' built-in prompts say to commit only when asked, and one model obeyed that over the branch/PR rule: DeepSeek left its work uncommitted in 4 of 4 stored eval runs, 2 of them on the default branch, citing "commit only when asked" (#13, #20).
    source: eval, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): eval evidence; corrected the count to the 4 stored runs -->
  - Encode repeatable checks in repo commands and CI.
    <!-- delivery-3
    why: Unknown.
    source: author
    review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; repo hygiene agents don't do unprompted, but no failure recorded; self-report -->
  - Scope CI to what changed: docs-only changes can skip build and test jobs via path filters, but still pass every required check.
    <!-- delivery-4
    why: Full build and test runs on docs-only changes cost time for no signal. A path-skipped required workflow blocks the merge, so required checks must still report.
    source: operator
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): operator; the path-filter vs required-check trap is a real mechanism agents miss; self-report -->
  - Gate automatic deployment on static checks, build, migrations, and critical integration/E2E tests.
    <!-- delivery-5
    why: Unknown.
    source: author
    review: cut, confidence low (claude-fable-5-1, 2026-09-26): Unknown; overlaps delivery-1 (never bypass checks) and delivery-3; self-report
    decision: keep (operator, 2026-09-26): delivery-1 covers PR checks, this gates the deploy pipeline itself -->
  - Re-check live contracts before shipping integration changes. Keep a recovery path; verify deploys with safe synthetic data.
    <!-- delivery-6
    why: Unknown.
    source: author
    review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; synthetic-data verification sits near the autonomy-2 boundary, the rest is generic; self-report -->
  - Isolate each parallel writer in its own git worktree and branch.
    <!-- delivery-7
    why: A tool that shared one working directory across branches made parallel agents see each other's half-finished edits in builds and tests.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident -->
  - Every branch, including one cut in the main checkout, starts from the freshly fetched remote default branch, never a local copy.
    <!-- delivery-8
    why: A session cut a branch from a local default branch that lacked a PR merged 12 minutes earlier; its PR conflicted on open, got no CI run, and auto-merge waited silently. `scripts/branch-check.sh` and `scripts/pr-wait.sh` catch it before and while waiting.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident, with scripts that depend on the rule -->
  - Rebase only on a conflict, which stalls a PR: it gets no CI run and auto-merge never fires. A green check merges, and the suite rerun on the default branch still gates the deploy.
    <!-- delivery-9
    why: With "require branches to be up to date" on, every merge invalidated every other open PR's check, so parallel agents queued behind each other for reruns. Overlapping files alone don't call for a rebase: the default-branch rerun gates the deploy and catches the rare semantic clash.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident; pairs with INSTALL step 6 -->
  - A PR refused as not up to date means the ruleset drifted: fix it (INSTALL.md step 6).
    <!-- delivery-10
    why: The up-to-date requirement drifted back on after delivery-9, and agents updated their branches instead of fixing the setting (#36).
    source: incident, 2026-09
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): incident (#36); narrow trigger, but agents rebased twice before finding the setting -->
  - After merging, remove the worktree and branch.
    <!-- delivery-11
    why: Unknown.
    source: author
    review: keep, confidence low (claude-fable-5-1, 2026-09-26): Unknown; cheap, and I'd leave worktrees behind without it; self-report -->
  - After merging, fast-forward the main checkout to the freshly fetched default branch, merge it (never rebase or force-push) into clean active branches, skip worktrees with uncommitted changes, and notify the agent that owns each updated branch.
    <!-- delivery-12
    why: Unknown. Parallel branches drifted from a merged default branch until their own PR update, hiding conflicts and stale dependencies from the agents working on them.
    source: operator, 2026-09
    review: move, confidence medium (claude-fable-5-1, 2026-09-26): operator, no incident; a long procedure that fits the runbook's finish-a-PR section behind a one-line trigger
    decision: keep (operator, 2026-09-26): added in v23, too new to judge -->
- **Documentation:** docs/ is a wiki: small, single-topic Markdown pages, cross-linked, indexed by docs/README.md, which links every page. Link an existing page instead of repeating it; update it, or add one and link it from the index, as part of the change or before closing a sprint.
  <!-- docs-1
  why: Docs drift and duplicate as agents add pages; a linked index lets an agent find the existing page instead of writing a new one.
  source: design
  review: keep, confidence medium (claude-fable-5-1, 2026-09-26): design; #33 item 2 shows a fix recorded in an unrelated doc -->
- **Runbook:** Before bootstrapping a worktree, running the app, or calling a vendor CLI, read docs/RUNBOOK.md; when a command or vendor error costs more than one attempt, record the working form there in the same PR.
  <!-- runbook-1
  why: Every worktree re-derived the local dev recipe (38 fresh installs, 53 env-file edits, 6 port collisions, the hosting CLI invoked 4 ways), and vendor errors learned by failure were recorded nowhere reusable (#33).
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident with counts (#33) -->
- **Migrations:** Before adding one, list the other agent sessions on this machine (the runtime's session list, and `git worktree list` for their branches) and ask each whether its work touches the same tables or migration sequence; if one doesn't answer, have a T3 subagent compare that branch's migrations and schema with the default branch. Pause applying the migration while a conflict exists, and record the pause in the task's issue.
  <!-- migrations-1
  why: Two parallel branches both created the same migration number, and a table rebuild on one failed after another branch changed a child table. Worktrees on one machine are the normal case (#33).
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident (#33); the trigger has to live here even though it fires rarely -->
- **Languages:** Before editing code in a language, read docs/languages/<language>.md if it exists.
  <!-- languages-1
  why: Keeps language rules out of every session's context.
  source: design
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): design: it is the on-demand link mechanism -->
- **Maintenance:** Follow docs/MAINTENANCE.md.
  <!-- maintenance-1
  why: The audit lived only in MAINTENANCE.md, which agents rarely opened, so `harness check` now nags when it's overdue.
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-1, 2026-09-26): design: the link `harness check` nags about -->
- **Delegation:**
  - Delegate bounded research, testing, review, and exploration when isolation or parallelism outweighs coordination cost; handle quick questions inline. Keep tightly coupled work together, avoid conflicting edits, and require concise, evidence-backed results.
    <!-- delegation-1
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): predecessor; the README procedure and tiers assume it; eval runs delegated under it; self-report -->
  - Stay on the committed sprint: search open issues, then file newly found work as new issues.
    <!-- delegation-2
    why: Parallel sessions filed the same issue twice, two pairs in two days (#33).
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): incident (#33) -->
  - Unless a new issue needs an operator decision, have the orchestrating session start a subagent on it.
    <!-- delegation-3
    why: Filing discovered work and stopping left it waiting on the operator to start another session mid-sprint.
    source: operator, 2026-09
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): operator; the failure is described but not counted -->
- **Model selection:**
  - Follow the model tiers in PROJECT_CONFIG.md when the runtime allows.
    <!-- models-1
    why: Operator's tiering: the strongest model plans, a cheaper one codes and runs the session, and subagents research, test, and review.
    source: operator
    review: keep, confidence high (claude-fable-5-1, 2026-09-26): operator's tiering; eval saw one run use the wrong subagent model even with the rule -->
  - Never claim a model or effort change you can't verify.
    <!-- models-2
    why: Unknown. The eval notes record that the CLI doesn't echo the requested effort level, so a claimed effort change can't be checked from a transcript (eval, 2026-09-23).
    source: author
    review: keep, confidence medium (claude-fable-5-1, 2026-09-26): eval notes show effort isn't observable, so unverifiable claims are plausible; no incident -->
