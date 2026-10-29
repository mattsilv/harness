# Secrets procedures

Upgrade from inline configuration: preserve any local secret-entry or provider instructions from PROJECT_CONFIG.md here before resolving a merge conflict. Keep the provider and location in PROJECT_CONFIG.md with its procedure link.

Follow the general rules below and the section for the provider named in PROJECT_CONFIG.md. Provider examples do not authorize a new service. Preserve the shared secrets and approval rules.

  - **Operator enters a value:** The agent must hand the operator the vendor's native interactive prompt, so the value never goes into the chat, a command argument, or shell history.
    - The agent must never ask for the value in chat, put it in a command argument, or wrap it in its own `read` prompt.
    - The agent must give the bare command with no value, plus the vendor's steps to finish it.
    - When the project also needs the value elsewhere, the agent gives the matching no-value command; for a GitHub Actions secret, `gh secret set <NAME>` also prompts.
    - The agent must copy the command to the clipboard when the platform supports it (macOS `pbcopy`).
    - The agent must say the command needs a real terminal window, not an agent-run shell or chat input.
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
