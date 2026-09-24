# Project Configuration

Defaults and identifiers only; never store secret values here. Every value is a default unless recorded otherwise.

- **Stack:** TypeScript monorepo (frontend and backend), Tailwind CSS.
- **T1, planning model (always a subagent: plans, architecture, hard decisions):** OpenAI Astra or Anthropic Fable, medium effort.
- **T2, primary model (the session: coding, merging):** OpenAI Sol or Anthropic Opus, medium effort.
- **T3, subagent model (research, testing, review):** OpenAI Luna or Anthropic Sonnet, high effort.
- **Effort levels:** Starting points; rules name tiers (T1–T3), never models; their meaning shifts between model generations.
- **Committed sprint:** The open GitHub milestone with the nearest due date.
- **Maintenance tracking issue:** Set during setup.
- **Merge policy:** Set during setup: `auto` or `on-request`. If unset, stop and ask.
- **Merge policies:** Both commit on a branch and open a PR. `auto` means the agent merges its own PRs without asking once required checks pass, queuing the host's auto-merge when available (merging deploys; the default branch must require CI status checks, and until it does treat the policy as `on-request`); `on-request` merges only when asked.
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
