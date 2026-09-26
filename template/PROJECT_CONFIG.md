# Project Configuration

Defaults and identifiers only; never store secret values here. Every value is a default unless recorded otherwise.

- **Stack:** TypeScript monorepo (frontend and backend), Tailwind CSS.
- **Design skill:** frontend-design.
- **Model tiers:** The default procedure for which model does what; rules name tiers, never models.
  - **T1, planning model:** OpenAI Astra or Anthropic Fable, medium effort. Does any planning, architecture, and hard decisions, always as a subagent of the session.
  - **T2, primary model:** OpenAI Sol or Anthropic Opus, medium effort. Runs the session and does the coding and merging.
  - **T3, subagent model:** OpenAI Luna or Anthropic Sonnet, high effort. Every implementation task gets at least one T3 subagent for testing and one for research, and a T3 subagent reviews each PR before it merges.
  - **Effort levels:** Starting points; their meaning shifts between model generations.
  - **One model available:** Use it for every tier.
- **Committed sprint:** The open GitHub milestone with the nearest due date.
- **Maintenance tracking issue:** Set during setup.
- **Merge policy:** Set during setup: `auto` or `on-request`. If unset, stop and ask.
- **Merge policies:** Both commit on a branch and open a PR. `auto` means the agent merges its own PRs without asking once required checks pass, turning on the host's auto-merge the moment the PR opens when available, never waiting on CI to merge by hand (merging deploys; the default branch must require CI status checks, and until it does treat the policy as `on-request`); `on-request` merges only when asked.
- **Docs:** docs/.

## Vendors

Record each choice once, here; adding a vendor is new spend, so ask first.

- **Secrets:** Set during setup (e.g. Doppler, 1Password, a cloud secret manager, or a gitignored .env). If unset, stop and ask.
- **Secrets location:** Set during setup (project and config, vault, or file path; one per repo or client, separate app and environment configs).
- **Hosting/deploy:** Serverless (e.g. Cloudflare) unless recorded otherwise.
- **Database:** SQL (e.g. Cloudflare D1) unless recorded otherwise.
- **Package managers:** uv (Python), pnpm (TypeScript).
- **Auth:** Record when chosen.
- **Email/SMS:** Record when chosen.
- **Error monitoring/analytics:** Record when chosen.
