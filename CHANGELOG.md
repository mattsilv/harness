# Changelog

One line per `VERSION`, newest first: version, date, PR, what changed in `template/`.
Projects record the version they last applied in `.harness/version`.

- **10** · 2026-09-23 · #22 · PROJECT_CONFIG: `auto` merge policy says the agent merges its own PRs without asking once required checks pass, using the host's auto-merge when available. No action needed.
- **10** · 2026-09-23 · #TBD · Planning model tier (Astra or Fable), always a subagent of the primary session; subagent default OpenAI Luna replaces Terra.
- **9** · 2026-09-23 · #20 · Delivery: this file is the standing request to commit, push branches, and open PRs. PROJECT_CONFIG: merge policy meanings on their own line, so recording a value keeps them; both policies commit on a branch and open a PR. Existing projects resolve one conflict on apply: keep the recorded value and take the new line.
- **8** · 2026-09-23 · #12 · Package managers move to PROJECT_CONFIG; every config value is a default unless recorded otherwise.
- **7** · 2026-09-23 · #11 · PROJECT_CONFIG: Vendors section (secrets, hosting, database, auth, email/SMS, monitoring); secrets manager no longer assumes Doppler.
- **6** · 2026-09-23 · #10 · Delivery: docs-only changes may skip build/test via CI path filters but still update from the default branch and pass required checks.
- **5** · 2026-09-23 · #9 · Monthly audit reviews one area untouched 4+ months: confirm it is live, then remove it or make the smallest improvement. Audit checks run on subagents using the subagent model.
- **4** · 2026-09-23 · #6 · Add `docs/languages/typescript.md` (pnpm, strict).
- **3** · 2026-09-23 · #5 · Docs as a linked wiki indexed by `docs/README.md`; maintenance audit monthly, with docs pare/dedupe pass.
- **2** · 2026-09-23 · #1 · Python rule moved to `docs/languages/python.md`; Languages bullet added.
- **1** · 2026-09-23 · seed · Imported from the Google Doc harness.
