# Project Configuration

Defaults and identifiers only; never store secret values here.

- **Secrets manager:** Doppler.
- **Doppler project and config:** Set during setup (one project per repo or client; distinguish app and environment configs). If unset, stop and ask.
- **Stack:** TypeScript monorepo (frontend and backend), serverless, SQL (typically Cloudflare D1), Tailwind CSS.
- **Primary model:** OpenAI Sol or Anthropic Opus, medium effort.
- **Subagent model (research, testing, review):** OpenAI Terra or Anthropic Sonnet, high effort.
- **Effort levels:** Starting points; their meaning shifts between model generations.
- **Committed sprint:** The open GitHub milestone with the nearest due date.
- **Maintenance tracking issue:** Set during setup.
- **Merge policy:** Set during setup: `auto` (merge when required checks pass; merging deploys; the default branch must require CI status checks, and until it does treat the policy as `on-request`) or `on-request` (open the PR; merge only when asked). If unset, stop and ask.
- **Docs:** docs/.
