# Subagent context watch (the snitch)

`scripts/snitch.sh` watches subagent context size at zero model tokens. It is a bash loop, not an agent. It replaces polling `scripts/context-watch.py` by hand, which cost tokens on every poll and was often forgotten.

## How it works

- Every `SNITCH_INTERVAL` seconds (default 300), it finds every Claude Code session, **in any project**, with a subagent transcript changed in the last `SNITCH_ACTIVE_MINS` minutes (default 15), and runs `scripts/context-watch.py <session-id>` for each. Scanning all sessions is deliberate: `context-watch.py` alone sees only one session, and other sessions' agents went unnoticed. It reads only each transcript's last usage line and the subagent's task description.
- `context-watch.py` thresholds: `warn` at 200k tokens, `handoff` at 250k (`CONTEXT_WARN`, `CONTEXT_HANDOFF`). It also prints `compact-now` for the orchestrating session itself.
- The loop **exits** on the first scan that finds a line it has not reported. The exit is the alert: under `run_in_background`, it wakes the orchestrator through the task notification.
- It sets `CONTEXT_RUNNING_SECS` to `SNITCH_ACTIVE_MINS * 60` (unless set), so a subagent counts as running for exactly as long as its session counts as active. A long tool call is not read as a finished agent, and a finished agent can be reported up to 15 minutes late, once.
- Each snitch touches a heartbeat (`alive-<session-id>` beside the seen-file) on every scan. A session whose own snitch is alive (heartbeat within two intervals) is reported only by that snitch, whose exit is the one that wakes it. Other snitches report only sessions that have no live snitch, as `other` lines.
- An append-only dedupe file (`SNITCH_SEEN`, default `${TMPDIR:-/tmp}/snitch-$USER/seen`) outlives restarts on purpose, and all snitches on the machine share it. It holds three key shapes:
  - `<session> <agent> <status>`: a `warn` does not repeat; a later `handoff` for the same agent does.
  - `<session> session compact-now` and `<session> session compact-clear`: the last one wins. `compact-clear` is appended when a scan of an active session no longer shows `compact-now`, so a regrowth after compaction alerts again.
  - `<session> - error <cksum>`: any output that is not a status line (a `context-watch:` error, a traceback, a missing `python3`) is reported once per distinct message, so the watcher cannot go silent.
- Delivery is at most once: a key is appended before the alert prints, and the file is never rewritten, so concurrent snitches cannot drop each other's keys.
- It exits with an `idle:` line after `SNITCH_IDLE_SECS` (default 7200) in which no subagent transcript changed within `SNITCH_ACTIVE_MINS`; so the exit comes about 2h15m after the last subagent activity (AGENTS.md, Processes).

## Start it

From the repo root, with the Bash tool's `run_in_background`:

```bash
bash scripts/snitch.sh
```

`bash scripts/snitch.sh --once` does one scan, prints the lines a background snitch would report next, and exits. It records nothing and leaves no heartbeat, so a manual check never consumes an alert that the owning session's snitch must deliver.

## Act on an alert

Output is `SNITCH HH:MM`, then one line per alert: `<self|other>  <session-id>  <project-dir>  <context-watch line>`. `self` means the session whose `CLAUDE_CODE_SESSION_ID` started the snitch.

- `self ... handoff`: stop that subagent at a safe point, relaunch it fresh with a short prompt naming its issue and branch, and tell the operator.
- `self ... warn`: no action; a `handoff` follows if it keeps growing.
- `self ... compact-now`: tell the operator.
- `other ...`: the alert belongs to a session with no snitch of its own. Find it in the runtime's session list (match by session start time or project directory) and send it the line.
- `context-watch: ...`: the watcher cannot read a transcript; tell the operator.
- `idle:`: do not restart it; start it again when you next launch subagents.

Otherwise, start the snitch again.

The snitch wraps `scripts/context-watch.py` without changing it. Like that script, it is specific to Claude Code transcripts; projects on other runtimes can ignore both.
