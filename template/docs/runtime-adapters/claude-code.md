# Claude Code adapter

Load only in Claude Code, through the mapping in PROJECT_CONFIG.md. Shared rules remain in AGENTS.md; CLAUDE.md imports them with `@AGENTS.md`.

When running subagents, read [the context watcher procedure](../SUBAGENT-CONTEXT-WATCH.md), start `bash scripts/snitch.sh` in the background, and act on its alerts as documented. Use the runtime's background-task notification mechanism. If that capability is unavailable, report the limitation; do not claim the watcher is active. Stop the watcher when the task ends.
