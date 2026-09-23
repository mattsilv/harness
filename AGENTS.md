# Working on this repo

This repo is the harness itself. Files under `template/` ship to every project that
uses it; everything else is for maintaining it. These rules apply here, not in projects.

- **Changing a rule:** edit `template/`, and in the same PR add or update the rule's
  line in `RATIONALE.md`. Before adding a rule, try the REVIEW.md test: would a current
  frontier model get this wrong without it? Prefer cutting or moving (to
  `PROJECT_CONFIG.md` or an on-demand file) over adding.
- **Version:** any PR that changes `template/` bumps `VERSION` by one and adds a
  `CHANGELOG.md` line (version, date, PR, what changed). CI enforces the bump.
- **Budget:** CI caps `template/AGENTS.md` by word count (`.github/workflows/budget.yml`).
  Raise the cap only deliberately, with the reason in the PR.
- **Parsed strings:** `harness-sync` reads "Set during setup", `**Merge policy:**`,
  `**Maintenance tracking issue:**`, and "<N> or more days ago" in
  `template/docs/MAINTENANCE.md`. Change them only together with `harness-sync`.
- **Preview:** from a project that uses the harness, run
  `HARNESS_SYNC_SOURCE=<this checkout>/template harness-sync diff`.
- **harness-sync:** standard-library Python only. Before merging a change, test `init`
  in a scratch git repo and `check`/`diff` in a real project.
- **Public:** no PII, hostnames, secrets, or project specifics anywhere in this repo.
- **Delivery:** branch and PR; squash-merge when CI passes. Merging publishes to every
  project on its next `check`, and each project still approves `apply`.
- **Model review:** when a new frontier model ships, or quarterly, follow `REVIEW.md`.
- **Maintenance (monthly, or when touching these files):** README's file table matches
  the tree; every rule in `template/` has a `RATIONALE.md` line; no rule is duplicated
  across template files; `INSTALL.md` still matches how `harness-sync` behaves.
