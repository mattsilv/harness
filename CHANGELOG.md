# Changelog

One line per `VERSION`, newest first: version, date, PR, what changed in `template/`.
Projects record the version they last applied in `.harness/version`.

- **17** · 2026-09-25 · #32 · Handoffs keep context in the issue and are a short prompt naming it (no more self-contained primers). Newly found work is filed and, unless it needs an operator decision, the orchestrating session starts a subagent on it. Rules apply to every task unprompted; quick questions exempt. No action needed.
- **16** · 2026-09-25 · #30 · PROJECT_CONFIG: under `auto`, turn on the host's auto-merge the moment the PR opens instead of waiting on CI to merge by hand. No action needed.
- **15** · 2026-09-24 · #29 · Fast path for small changes. UI: screenshots only for layout, styling, or page-structure changes; copy-only changes need none. Delivery: update a branch before merging only when it conflicts or the default branch changed files it touches, otherwise merge on a green check; docs-only changes no longer update first. Projects should require the CI check but turn off "require branches to be up to date" (INSTALL.md step 6).
- **14** · 2026-09-23 · #28 · PROJECT_CONFIG: a T3 subagent reviews each PR before it merges.
- **13** · 2026-09-23 · #27 · PROJECT_CONFIG: model tiers grouped under one **Model tiers** bullet as the default procedure; every implementation task gets at least one T3 testing and one T3 research subagent. AGENTS.md Model selection now points there. Projects that recorded their own models resolve one conflict on apply: keep their model names in the new sub-bullets.
- **12** · 2026-09-23 · #26 · Process: end each phase or sprint with a handoff primer for a fresh session.
- **11** · 2026-09-23 · #25 · Model tiers T1 (planning), T2 (session, coding), T3 (research, testing, review); rules name tiers, not models. Planning model tier (Astra or Fable), always a subagent of the primary session; subagent default OpenAI Luna replaces Terra.
- **10** · 2026-09-23 · #22 · PROJECT_CONFIG: `auto` merge policy says the agent merges its own PRs without asking once required checks pass, using the host's auto-merge when available. No action needed.
- **9** · 2026-09-23 · #20 · Delivery: this file is the standing request to commit, push branches, and open PRs. PROJECT_CONFIG: merge policy meanings on their own line, so recording a value keeps them; both policies commit on a branch and open a PR. Existing projects resolve one conflict on apply: keep the recorded value and take the new line.
- **8** · 2026-09-23 · #12 · Package managers move to PROJECT_CONFIG; every config value is a default unless recorded otherwise.
- **7** · 2026-09-23 · #11 · PROJECT_CONFIG: Vendors section (secrets, hosting, database, auth, email/SMS, monitoring); secrets manager no longer assumes Doppler.
- **6** · 2026-09-23 · #10 · Delivery: docs-only changes may skip build/test via CI path filters but still update from the default branch and pass required checks.
- **5** · 2026-09-23 · #9 · Monthly audit reviews one area untouched 4+ months: confirm it is live, then remove it or make the smallest improvement. Audit checks run on subagents using the subagent model.
- **4** · 2026-09-23 · #6 · Add `docs/languages/typescript.md` (pnpm, strict).
- **3** · 2026-09-23 · #5 · Docs as a linked wiki indexed by `docs/README.md`; maintenance audit monthly, with docs pare/dedupe pass.
- **2** · 2026-09-23 · #1 · Python rule moved to `docs/languages/python.md`; Languages bullet added.
- **1** · 2026-09-23 · seed · Imported from the Google Doc harness.
