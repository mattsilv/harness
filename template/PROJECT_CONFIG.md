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
  - **Operator enters a value:** The agent must hand the operator the vendor's native interactive prompt, so the value never goes into the chat, a command argument, or shell history.
    - The agent must never ask for the value in chat, put it in a command argument, or wrap it in its own `read` prompt.
    - The agent must give the bare command with no value, plus the vendor's steps to finish it.
    - When the project also needs the value elsewhere, the agent gives the matching no-value command; for a GitHub Actions secret, `gh secret set <NAME>` also prompts.
    - The agent must copy the command to the clipboard when the platform supports it (macOS `pbcopy`).
    - The agent must say the command needs a real terminal window, not the Claude Code `!` prefix or an agent-run shell.
    - Stdin is the other safe way to set a value from a file.
  - **Checking secrets:** The agent must never print a secret value; it lists names, and checks presence by length.
  - **With Doppler:**
    - **Structure:** Doppler recommends one project per app, named lowercase with hyphens, with `dev`, `stg`, and `prd` configs. When the operator keeps several apps in one shared project, every secret name must carry the app's prefix (`<PROJECT>_CLOUDFLARE_API_TOKEN`, not `CLOUDFLARE_API_TOKEN`).
    - **Enter a value:** `doppler secrets set <SECRET_NAME> --project <project> --config <config>`, then: 1. Paste the value. 2. Press Enter twice. 3. Type `.` and press Enter.
    - **From a file:** `cat <file> | doppler secrets set <SECRET_NAME>`.
    - **Check:** `doppler secrets --only-names` lists names; `doppler secrets get <SECRET_NAME> --plain | wc -c` checks presence by length.
    - **Local dev:** Run local commands as `doppler run -- <cmd>`, or `doppler run --mount .env -- <cmd>` for an ephemeral file. `doppler setup -p <project> -c <config>` scopes a directory. Do not write a `.env` file, and never commit one.
    - **CI:** CI must use a read-only service token scoped to one config, or OIDC through a service account; never a personal or CLI token. For one config, Doppler recommends its GitHub sync app, which is one-way: edit values only in Doppler.
    - **Token expiry:** Give each CI service token an expiry (`doppler configs tokens create <name> --project <project> --config <config> --max-age <duration>`), or record its rotation date in docs/MAINTENANCE.md.
    - **Targets without a sync** (for example Cloudflare Workers): Set the target's secrets from CI by piping `doppler secrets download --no-file --format json` into the target's bulk-secret command. Do not edit secrets in the target by hand.
    - **Rotation:** After a leak or a revocation, rotate the value at its source. Revoking a Doppler token does not clear the CLI's local fallback cache.
    - **Pitfall:** `inject-env-vars: true` in the fetch action exposes secrets to every later step.
    - **Pitfall:** Some injected variable names can enable code execution, so inject only what the app needs.
    - **Pitfall:** Renaming a referenced secret leaves the `${NAME}` reference as literal text.
- **Secrets location:** Set during setup (project and config, vault, or file path; one per repo or client, separate app and environment configs).
- **Hosting/deploy:** Serverless (e.g. Cloudflare) unless recorded otherwise.
- **Database:** SQL (e.g. Cloudflare D1) unless recorded otherwise.
- **Package managers:** uv (Python), pnpm (TypeScript).
- **Auth:** Record when chosen.
- **Email/SMS:** Record when chosen.
- **Error monitoring/analytics:** Record when chosen.
