# Project Configuration

Defaults and identifiers only; never store secret values here. Every value is a default unless recorded otherwise.

- **Stack:** TypeScript monorepo (frontend and backend), Tailwind CSS.
- **Design skill:** frontend-design in Claude Code; none for other runtimes.
- **Frontend review:** `off`; set to `on` to follow [docs/FRONTEND.md](docs/FRONTEND.md) for frontend changes.
  - **Visual reviewer:** Independent T2 subagent, alongside the T3 PR review.
  - **Capture runner:** Playwright with Chromium; reuse an equivalent project runner when available.
  - **Capture command:** `node scripts/ui-capture.mjs --driver playwright --browser chromium --url <local-app-url>`; add `--check` in CI.
  - **Screenshots:** `committed` (default) or `local` (gitignore `docs/ui/screenshots/`; commit the manifest and sitemap; no `--check`).
  - **Viewports:** Initially desktop 1440 × 900 and mobile 390 × 844; record the chosen sizes in `docs/ui/templates.json` when enabling.
- **Runtime adapters:** Claude Code: [docs/runtime-adapters/claude-code.md](docs/runtime-adapters/claude-code.md); Codex: none; OpenCode: none; other runtimes: none. Load only the matching adapter; add one only for a tool-specific procedure.
- **Model tiers:** Model and effort defaults when delegation is useful; shared rules determine when to delegate.
  - **T1, planning model:** Astra in Codex or Fable in Claude Code, medium effort. For delegated planning, architecture, and hard decisions.
  - **T2, primary model:** GPT-6.1 Sol in Codex or Opus in Claude Code, medium effort. Runs the session and does the coding and merging.
  - **T3, subagent model:** Luna in Codex or Sonnet in Claude Code, high effort, for research and testing. Use when delegation is warranted by task risk or isolation.
    - **PR review:** Terra, extra high effort, in Codex; Sonnet, high effort, in Claude Code.
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
  - **Procedure:** Before entering, checking, or configuring secrets, read [docs/SECRETS.md](docs/SECRETS.md); follow the general rules and only the configured provider's section.
- **Secrets location:** Set during setup (project and config, vault, or file path; one per repo or client, separate app and environment configs).
- **Hosting/deploy:** Serverless (e.g. Cloudflare) unless recorded otherwise.
- **CI runners:** Hosted (default). Self-hosted only per [docs/CI.md](docs/CI.md); then record the values below.
  - **Labels:** None (hosted).
  - **Slots per host:** None; set from measured throughput.
  - **Workspace storage:** Ephemeral per job (tmpfs); dependency caches on durable disk.
  - **Who adds capacity:** The operator; an agent proposes it with a measurement.
- **Database:** SQL (e.g. Cloudflare D1) unless recorded otherwise.
- **Package managers:** uv (Python), pnpm (TypeScript).
- **Auth:** Record when chosen.
- **Email/SMS:** Record when chosen.
- **Error monitoring/analytics:** Record when chosen.
