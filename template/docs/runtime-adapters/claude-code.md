# Claude Code adapter

Load only in Claude Code (`CLAUDE.md` imports `@AGENTS.md` and `@docs/runtime-adapters/claude-code.md`).

- Wait on `scripts/pr-wait.sh` via `Monitor` or `Bash` `run_in_background` (foreground Bash stops at 10 minutes, `sleep` chains are blocked, and macOS has no `timeout`).
- In `isolation: "worktree"` subagents, edit files with `Edit`/`Write` (never heredocs or inline `python3`), run each `git` call as a standalone command without `cd` or `-C`, and leave worktree removal and main-checkout fast-forward to the caller.
