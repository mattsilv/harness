# Agent Rules
<!-- Maintainers: each rule is one bullet followed by an HTML comment with its stable id
(never reused), why it exists, its source, and its latest review. The harness CLI strips
every comment line before projects receive this file. -->

Apply these rules to every task unprompted; quick questions just need answers.
<!-- core-1
why: The operator had to say "use our harness" before feature work.
source: operator, 2026-09
review: keep, confidence medium (claude-fable-5-2, 2026-11-10): operator evidence (#32) that agents skipped the harness until told; no session in this review needed the reminder; operator evidence -->

- **Configuration:**
  - Read PROJECT_CONFIG.md at session start and when it changes. Use its defaults, including model tiers, and load only the adapter mapped to the active coding agent.
    <!-- config-1
    why: PROJECT_CONFIG.md is the one place for project values and model tiers, so agents need to load it before acting on them.
    source: design
    review: rewrite, confidence high (claude-fable-5-2, 2026-11-10): it is the load mechanism; agents read the file in every reviewed session; transcripts; 2026-11-24: absorbed models-1 so model tiers stay loaded without a separate section -->
  - Ask the operator for any value marked "set during setup" before other work.
    <!-- config-3
    why: Guessing merge policy would bring back the conflicting-policy failures behind docs-3. `harness check` repeats the question until it's answered.
    source: design
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): blocks guessing merge policy; enrollment ran cleanly in two new projects; transcripts -->
- **Autonomy:**
  - Define observable acceptance criteria; implement, verify, and correct within the authorized task until they and required review pass, including delivery per PROJECT_CONFIG.md. Act on your own recommendation and report it; stop only for an approval below, a blocker, a configured limit, or a question whose one-line answer would greatly change the result.
    <!-- autonomy-1
    why: Agents stopped before task completion until the operator prompted them to continue; completion includes evidence and authorized delivery, without bypassing approval or the two-cycle failure stop (#71). The question clause exists because "stop only for" otherwise forbids the one cheap question that saves a wrong build; "one-line" and "greatly" keep the bar high so asking does not become the default again.
    source: operator, #71, 2026-10-29
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): transcripts show agents asking "want me to build it?" after the operator stated the need and listing decisions they already had a recommendation for (3 projects); 2026-11-25: added the question clause at the operator's request, confidence low. Evidence is thin and points both ways, so the clause is narrow: a keyword search of about 1,570 operator messages in 17 projects found about 16 "go with your rec" replies in 7 projects (the agent waited on a choice it had already made), about 5 corrections of a wrong guess about intent, and no complaint about too many questions. Revisit at the next review; cut the clause if "go with your rec" replies rise. -->
  - Ask first for irreversible changes to production data or destructive migrations; changes to the auth model or permission structure; new spend or paid services; messaging real users or changing data in external accounts; and force-pushes to shared branches.
    <!-- autonomy-2
    why: Operator's safety boundary for irreversible, auth, spend, and external actions. Not a model-capability rule; REVIEW.md forbids cutting or loosening it.
    source: operator
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): operator safety boundary; REVIEW.md don't-cut list; agents asked before irreversible actions in the reviewed sessions; transcripts -->
  - Report results and unverified risks accurately. When a task changed anything, wait for CI and the deploy before finishing; start the final report with `Done` or `Not done: <what remains>`, and end it with the merge state, deploy state, and a link plus one line on what to check.
    <!-- autonomy-3
    why: The operator had to ask for status in most sessions of one project ("are we done here" in 5, "is ci done", "did that deploy?", "link me to what I'm checking") (#33).
    source: incident, 2026-09
    review: rewrite, confidence high (claude-fable-5-2, 2026-11-10): agents reported "deploy unchecked" and stopped, so "are we done" recurred (about 7 times in one project, 4 of 12 sessions in another); the ritual was also appended to answers that changed nothing; reworded 2026-11-24 after a transcript review found 6 more status asks in 3 weeks, and tightened to "before finishing" so yielding an intermediate turn for a background wakeup does not contradict it -->
  - Write questions and reports for the operator, and instructions for users, in ASD-STE100 style: answer first, short active sentences, each point once, "must" or "can" instead of "should" or "may", one name for each thing, numbered questions with lettered options (recommendation first), and a table only to compare items on the same fields. Keep the final report within PROJECT_CONFIG.md's report length.
    <!-- autonomy-4
    why: The operator reads and answers this text, and users follow instructions step by step, so both must be fast to scan and unambiguous. Models default to long, hedged prose; "should" and "may" hide whether a step is required. Borrows the controlled-English rules of ASD-STE100, not its word list, which costs words and flags normal technical terms.
    source: operator, 2026-10
    review: keep, confidence low (claude-fable-5-2, 2026-11-10): no transcript evidence either way; self-report; 2026-11-25: added answer first, each point once, the table test, and the configurable report length after a review of about 1,570 operator messages in 17 projects found reports long enough that the operator re-asked for the one thing needed, text stated twice, and tables used for prose (wide on mobile); a five-agent research pass (2026-11, mostly practitioner reports, not controlled studies) agreed that a vague "be concise" does little while a stated shape and a countable cap hold. The cap is a PROJECT_CONFIG.md value because the right length differs by project. Same day (v54): added numbered questions with lettered options, recommendation first, so the operator can answer "1a 2b" or just "yes"; the operator asked for enumerated choices he can tap instead of typing, and bare "yes" and "go with your rec" were his most common replies to questions. -->
- **Implementation:**
  - Share business logic and authorization across all interfaces (web, API, MCP, chat, jobs); keep interfaces thin.
    <!-- impl-2
    why: Unknown.
    source: author
    review: keep, confidence low (claude-fable-5-2, 2026-11-10): operator decision 2026-09-26 stands; no session showed it applied or broken; operator decision
    decision: keep (operator, 2026-09-26): agents duplicate logic per interface, and the non-auth half isn't covered elsewhere -->
  - Define each shared value once, including design tokens, and reference it everywhere.
    <!-- impl-3
    why: Unknown.
    source: author
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): kept the design-token clause the operator asked for; the token list and the when-to-extract clause are default judgment; self-report
    decision: rewritten (operator, 2026-09-26): kept the design-token clause, dropped the list -->
  - Deliver only what the task asks for: no unrequested features, sections, labels, disclaimers, or copy.
    <!-- impl-4
    why: The operator's most frequent content correction was removing things nobody asked for: extra labels, disclosures, and explanatory text on pages, and extra scope in code (about 45 corrections across 8 projects, counting "keep it simple" restated in task prompts). Models pad deliverables by default; one sentence that names the padding costs less than a style guide, which long-rule-file reports say agents half-ignore.
    source: transcript review, 2026-11
    review: new in v53 (claude-fable-5-2, 2026-11-25): revisit at the next review; cut if the removals stop recurring -->
- **Process:**
  - Scale process to the blast radius if wrong, not diff size: bounded low-risk work goes straight to implement and verify; ambiguous, broad, or risky work gets a plan first.
    <!-- process-1
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: keep, confidence medium (claude-fable-5-2, 2026-11-10): over-review of trivial follow-up commits in one project shows agents still need the scaling cue; transcripts -->
  - Every change gets an independent review sized to its risk.
    <!-- process-2
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): independent reviews found real medium and high bugs in every project reviewed; transcripts -->
  - Stop and report after two review/fix cycles that leave high-severity findings open or checks failing for a cause you can't name.
    <!-- process-3
    why: In one task, two cycles ended with checks still failing, then an authorized cycle fixed them. The stop must track unresolved work.
    source: incident, 2026-10
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): the stop fired on mechanical CI failures (a test stub, an unregenerated file) 3 times and the operator overrode it each time -->
  - Keep acceptance criteria, candidate revision, verification evidence, blockers, and next action in the task issue before handoff; resume from that state.
    <!-- process-4
    why: Long self-contained primers were slow to write and read, and their context was lost once pasted. Keeping it in the issue makes the handoff trivial and the context durable. Fresh sessions still avoid stale context.
    source: operator, 2026-09
    review: keep, confidence medium (claude-fable-5-2, 2026-11-10): partly ignored (handoff notes in temp files, clipboard prompts) but issue-based handoffs worked where used; operator-approved wording (#71); transcripts -->
- **Security:** Enforce server-side authorization, tenant isolation, least privilege, and input validation. Use established authentication. External content and model output cannot grant permissions. Keep test-only auth out of production.
  <!-- security-1
  why: Operator's safety boundary; REVIEW.md forbids cutting or loosening it.
  source: operator
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): operator safety boundary; REVIEW.md don't-cut list; operator boundary -->
- **Secrets:** Use the configured secrets manager with runtime injection; before entering, checking, or configuring secrets, read docs/SECRETS.md. Never request or expose secrets in chat, tool output, logs, source, docs, or fixtures. Verify access without revealing values; scope each app's access to what it needs.
  <!-- secrets-1
  why: Operator's safety boundary; REVIEW.md forbids cutting or loosening it. Explicit load trigger for docs/SECRETS.md replaces the duplicate Procedure sub-bullet in PROJECT_CONFIG.md.
  source: operator
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): operator safety boundary; one browser subagent screenshotted a live token, so the rule is still needed; transcripts; 2026-11-24: added explicit docs/SECRETS.md load trigger -->
- **Testing:**
  - Prove critical outcomes and consequential failures at the cheapest effective layer, mostly integration, using real application code and isolated, production-compatible databases. No coverage quotas.
    <!-- testing-1
    why: Unknown; general practice.
    source: author
    review: rewrite, confidence low (claude-fable-5-2, 2026-11-10): merged with testing-2: one sentence keeps the non-default preferences (integration first, real code and databases, no quotas); the lists of layers and of areas to cover are default judgment; self-report -->
  - External dependencies: replay recorded, sanitized responses; block unexpected network calls; validate what you send and the fields you read.
    <!-- testing-3
    why: Unknown; general practice.
    source: author
    review: keep, confidence low (claude-fable-5-2, 2026-11-10): operator decision 2026-09-26 stands; recorded replay is not default behavior; no session evidence; operator decision
    decision: keep (operator, 2026-09-26): an on-demand file costs more than these lines save -->
  - AI features: stub model responses for deterministic tests; evaluate real outcomes, tool use, and permissions when prompts, models, or tools change.
    <!-- testing-4
    why: Unknown; general practice.
    source: author
    review: keep, confidence low (claude-fable-5-2, 2026-11-10): operator decision 2026-09-26 stands; no session evidence; operator decision
    decision: keep (operator, 2026-09-26): an on-demand file costs more than these lines save -->
  - Bugs: add the cheapest reproducing test before fixing. Fix flakes. Never weaken expectations or refresh fixtures just to pass.
    <!-- testing-5
    why: Unknown; general practice. "Never weaken expectations" targets agents that make tests pass by editing them.
    source: author
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): agents proved tests fail without the fix in 4 sessions; editing tests to pass remains a known failure mode; transcripts -->
- **UI:**
  - Use the design skill PROJECT_CONFIG.md names for your runtime, if any, for any frontend change.
    <!-- ui-1
    why: Unknown. Agents defaulted to templated-looking UI without a nudge to reach for the design skill first.
    source: operator, 2026-09
    review: keep, confidence medium (claude-fable-5-2, 2026-11-10): operator request (#38); cheap pointer; self-report
    decision: moved the skill name to PROJECT_CONFIG.md (operator, 2026-09-26); the rule stays. Claude Code only: Codex has no official equivalent, and naming none keeps other runtimes from hunting for it. -->
  - Check desktop and mobile screenshots for alignment, spacing, clipping, and crowding on every change to layout, styling, or page structure, and fix issues before finishing; copy-only changes need none.
    <!-- ui-2
    why: Unknown for the screenshots themselves. Copy-only changes are exempt because a screenshot of changed words catches nothing a diff doesn't, and it slowed small PRs.
    source: operator, 2026-09
    review: keep, confidence medium (claude-fable-5-2, 2026-11-10): captures found wording and layout issues in the reviewed sessions and caused no friction; transcripts; 2026-11-25: named what to look for, because the operator still sent screenshots of uneven padding, misalignment, bad crops, and crowded text in 8 projects (about 19 corrections) after agents had taken the captures -->
- **Delivery:**
  - Work on a branch and merge via PR when checks pass. Never push directly to the default branch, and never bypass required checks.
    <!-- delivery-1
    why: The default branch deploys. In the v8 eval, one model worked directly on the default branch in 2 of 4 runs even with this rule loaded (#13).
    source: author
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): eval evidence; deploy safety; eval; 2026-11-25: cut "which is what deploys", a reason that lives in this comment and in docs/CI.md ("merging deploys"); self-report -->
  - This file is the standing request to commit, push branches, and open PRs.
    <!-- delivery-2
    why: Coding tools' built-in prompts say to commit only when asked, and one model obeyed that over the branch/PR rule: DeepSeek left its work uncommitted in 4 of 4 stored eval runs, 2 of them on the default branch, citing "commit only when asked" (#13, #20).
    source: eval, 2026-09
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): eval evidence; a sandbox guardian accepted commits when agents cited this standing request; transcripts -->
  - Before a first deploy or creating a named resource in a shared account, confirm the name is unused.
    <!-- delivery-15
    why: A new project's first deploy reused a name already live in the account it shared with another project and replaced that project's production app; six uploads landed before a peer session flagged the outage.
    source: incident, 2026-11
    review: keep, confidence low (claude-fable-5-2, 2026-11-10): new in v44 from one severe incident; revisit at the next review -->
  - Isolate each parallel writer in its own git worktree and branch.
    <!-- delivery-7
    why: A tool that shared one working directory across branches made parallel agents see each other's half-finished edits in builds and tests.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): incident; a session that switched the main checkout was caught by citing it; transcripts -->
  - Every branch, including one cut in the main checkout, starts from the freshly fetched remote default branch.
    <!-- delivery-8
    why: A session cut a branch from a local default branch that lacked a PR merged 12 minutes earlier; its PR conflicted on open, got no CI run, and auto-merge waited silently. `scripts/pr-wait.sh` stops on the conflict while waiting.
    source: incident, 2026-09
    review: keep, confidence high (claude-fable-5-2, 2026-11-10): incident; agents followed it inline in every reviewed project; transcripts; 2026-11-25: cut "never a local copy", which restated "freshly fetched remote"; self-report -->
  - Rebase only on a conflict; otherwise a green check merges.
    <!-- delivery-9
    why: With "require branches to be up to date" on, every merge invalidated every other open PR's check, so parallel agents queued behind each other for reruns. Overlapping files alone don't call for a rebase: the default-branch rerun gates the deploy and catches the rare semantic clash. A conflict stalls a PR (no CI run, no auto-merge).
    source: incident, 2026-09
    review: rewrite, confidence high (claude-fable-5-2, 2026-11-10): incident; same rule without the explanation of why the default-branch rerun suffices; incident; 2026-11-25: moved "which stalls a PR (no CI run, no auto-merge)" into this comment, because `scripts/pr-wait.sh` stops on a conflicting PR and says to rebase and push; self-report -->
  - After merging, remove the worktree and branch and fast-forward the main checkout.
    <!-- delivery-11
    why: Unknown.
    source: author
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): cleanup happened in every project; absorbs the one cheap step of delivery-12; transcripts -->
  - Before opening a PR, run `scripts/overlap-check.sh`; on a hit in another session's work, agree with its owner who lands first.
    <!-- delivery-13
    why: In one project 12 PRs in 7 days conflicted with the default branch because parallel sessions edited the same files (one route file in 7 of them, the docs index in 6), and nothing surfaced it before the merge. The script lists files that other open PRs and local worktrees also change.
    source: incident, 2026-10
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): about 200 runs across 5 projects found about 3 real cross-session hits; most hits were the session's own PRs and worktrees, so one run and "another session's work" -->
  - Before changing CI workflows, runners, or test storage, read docs/CI.md.
    <!-- delivery-14
    why: A project ran 8 self-hosted runner slots on one host. Its test suite created databases with write-ahead logging and full durability, so concurrent jobs queued on the shared disk's filesystem journal and a 20 s suite took 337 s; adding slots made it worse. Test workspaces on tmpfs and slots sized from measured throughput fixed it.
    source: incident, 2026-10
    review: move, confidence medium (claude-fable-5-2, 2026-11-10): docs/CI.md already states the storage and capacity rules, and the path-filter rule that was delivery-4; only the trigger stays here -->
- **Documentation:** docs/ is a wiki of small, single-topic pages indexed by docs/README.md. Update or link an existing page instead of repeating it, and link any new page from the index, as part of the change.
  <!-- docs-1
  why: Docs drift and duplicate as agents add pages; a linked index lets an agent find the existing page instead of writing a new one.
  source: design
  review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): same rule in fewer words; #33 evidence stands; incident -->
  - State each rule once; put area-specific instructions in the affected directory or a linked doc, not root agent files.
    <!-- docs-3
    why: Duplicate rules across tools gave agents contradictory merge and push instructions (formerly config-2), and area-specific context bloated root instructions; scoped rules and selected adapters prevent both (#57, #71).
    source: incident, 2026-09; token audit of one project's root context (via #57), 2026-10
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): kept the part a project agent acts on (area context out of root files, from the token audit); 2026-11-24: absorbed config-2 so rule non-duplication lives in one place -->
- **Runbook:** Before bootstrapping a worktree, running the app, or calling a vendor CLI, read docs/RUNBOOK.md; when a command or vendor error costs more than one attempt, record the working form there in the same PR.
  <!-- runbook-1
  why: Every worktree re-derived the local dev recipe (38 fresh installs, 53 env-file edits, 6 port collisions, the hosting CLI invoked 4 ways), and vendor errors learned by failure were recorded nowhere reusable (#33).
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): incident (#33); recipes were still re-derived where the runbook was skipped; transcripts -->
- **Processes:** Stop every process you start (servers, test runners, watchers, browsers and their pages or sessions) before the task ends, and report any left running; give persistent automation daemons an idle timeout.
  <!-- processes-1
  why: Agents across many sessions left a shared browser-automation daemon running for 10 days with its idle timeout disabled: 14 named browsers, some idle 45+ hours, ~140 headless browser processes, one browser with 71 tabs. Load average reached 10-12 and parallel E2E runs slowed to a crawl. Every task can start a process, so the rule is every-task.
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): incident; transcripts still show orphaned watchers (3 left for a closed PR in one session) -->
  - Show the operator a page by printing its URL; unless asked, never `open <url>` or launch a browser from a shell.
    <!-- processes-2
    why: Agents ran `open http://127.0.0.1:<port>/` from Bash to show a dev page. On macOS 26.6 with Chrome 156 that spawned a second Chrome process from the terminal coalition, which aborted in HIServices _RegisterApplication 35 ms after launch and showed the operator a "Google Chrome quit unexpectedly" dialog on every call, while the page opened anyway in the running browser.
    source: incident, 2026-10
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): the operator asked agents to open a page 6 times in 3 sessions, and the rule forbade it -->
- **Migrations:** Before adding one, check other worktrees and sessions for overlapping schema work and coordinate with its owners; if you can't see them, say so instead of assuming none. Apply no migration while a conflict is unresolved.
  <!-- migrations-1
  why: Two parallel branches both created the same migration number, and a table rebuild on one failed after another branch changed a child table. Worktrees on one machine are the normal case (#33).
  source: incident, 2026-09
  review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): same rule in fewer words; no transcript evidence against it -->
- **Languages:** Before editing code in a language, read docs/languages/<language>.md if it exists.
  <!-- languages-1
  why: Keeps language rules out of every session's context.
  source: design
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): design: the on-demand link mechanism; design -->
- **Maintenance:** Before maintenance, read docs/MAINTENANCE.md.
  <!-- maintenance-1
  why: The audit lived only in MAINTENANCE.md, which agents rarely opened, so `harness check` now nags when it's overdue.
  source: incident, 2026-09
  review: keep, confidence high (claude-fable-5-2, 2026-11-10): design: the link `harness check` nags about; design; 2026-11-24: given a load trigger, since `harness check` already computes due lists -->
- **Delegation:**
  - Delegate bounded work when isolation or parallelism outweighs coordination cost; require concise, evidence-backed results.
    <!-- delegation-1
    why: Carried over from the predecessor harness. Incident not recorded.
    source: predecessor
    review: rewrite, confidence medium (claude-fable-5-2, 2026-11-10): delegation and model tiers were followed everywhere; what to delegate and keeping coupled work together are default judgment, the cost test and evidence-backed results stay; transcripts -->
  - Search open issues, then file found work; a parallel subagent fixes and ships it at once, escalating only key decisions.
    <!-- delegation-2
    why: Parallel sessions filed the same issue twice, two pairs in two days (#33).
    source: incident, 2026-09
    review: rewrite, confidence high (claude-fable-5-2, 2026-11-10): merged with delegation-3, which said the second half (operator, #71: one verified task per run; automatic execution of discovered issues expands scope); 2026-11-25: operator reversed the second half: filed-but-unfixed bugs piled up (a project filed an issue and stopped), so objective fixes now go to a subagent through the normal PR flow, which keeps the main task's scope; judgment calls stay filed; same day: operator asked for the fix to start in parallel immediately and ship automatically, with only key decisions coming back to them -->
