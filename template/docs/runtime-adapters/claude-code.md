# Claude Code adapter

Load only in Claude Code, through the mapping in PROJECT_CONFIG.md. Shared rules remain in AGENTS.md; CLAUDE.md imports them with `@AGENTS.md`.

Run `scripts/pr-wait.sh` with `run_in_background`: foreground Bash stops at 10 minutes, and macOS has no `timeout`.
