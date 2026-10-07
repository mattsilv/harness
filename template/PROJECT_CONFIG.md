# Project Configuration

Defaults and identifiers only; never store secret values here. Every value is a default unless recorded otherwise.

- **Stack:** TypeScript monorepo (frontend and backend), Tailwind CSS.
- **Design skill:** frontend-design in Claude Code; none for other runtimes.
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
  - **Secret names:** Each name must carry a project prefix, so one config can hold several projects' secrets (`<PROJECT>_CLOUDFLARE_API_TOKEN`, not `CLOUDFLARE_API_TOKEN`).
  - **Operator enters a value:** The agent must hand the operator the vendor's native interactive prompt, so the value never goes into the chat, a command argument, or shell history.
    - The agent must never ask for the value in chat, put it in a command argument, or wrap it in its own `read` prompt.
    - With Doppler, the agent must give the bare command with no value: `doppler secrets set <SECRET_NAME> --project <project> --config <config>`.
    - The agent must give these steps with it: 1. Paste the value. 2. Press Enter twice. 3. Type `.` and press Enter.
    - When the project also needs the value elsewhere, the agent gives the matching no-value command; for a GitHub Actions secret, `gh secret set <NAME>` also prompts.
    - The agent must copy the command to the clipboard when the platform supports it (macOS `pbcopy`).
    - The agent must say the command needs a real terminal window, not the Claude Code `!` prefix or an agent-run shell.
- **Secrets location:** Set during setup (project and config, vault, or file path; one per repo or client, separate app and environment configs).
- **Hosting/deploy:** Serverless (e.g. Cloudflare) unless recorded otherwise.
- **Database:** SQL (e.g. Cloudflare D1) unless recorded otherwise.
- **Package managers:** uv (Python), pnpm (TypeScript).
- **Auth:** Record when chosen.
- **Email/SMS:** Record when chosen.
- **Error monitoring/analytics:** Record when chosen.
