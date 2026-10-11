#!/usr/bin/env bash
# Snitch: a zero-token background watcher for subagent context size (docs/SUBAGENT-CONTEXT-WATCH.md).
#
# Every interval it runs scripts/context-watch.py for each Claude Code session, in any project,
# whose subagents wrote a transcript recently. It EXITS on the first scan that finds a line it
# has not reported before; that exit is what wakes the orchestrator (run_in_background task
# notification). The orchestrator acts on each line, then starts the snitch again.
# It also exits when no session has active subagents for SNITCH_IDLE_SECS.
#
# Usage: bash scripts/snitch.sh [--once]      (--once: one scan, print new lines, exit 0)
# Output: "SNITCH HH:MM" then one line per alert:
#   <self|other>  <session-id>  <project-dir>  <context-watch line>
# Env:
#   SNITCH_INTERVAL     seconds between scans (300)
#   SNITCH_ACTIVE_MINS  a session counts if a subagent transcript changed within this many minutes (15)
#   SNITCH_IDLE_SECS    exit after this long with no active subagents anywhere (7200)
#   SNITCH_SEEN         dedupe file (${TMPDIR:-/tmp}/snitch-$USER/seen); keys are "<session> <agent> <status>",
#                       "<session> session compact-now" (dropped when the condition clears), "<session> - error <cksum>"
#   CLAUDE_PROJECTS_DIR transcripts root (${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects)
#   CONTEXT_RUNNING_SECS defaults to SNITCH_INTERVAL+60 so an agent in a long tool call is not skipped;
#   CONTEXT_WARN, CONTEXT_HANDOFF and the other context-watch.py variables pass through.
set -u

ONCE=0
case "${1:-}" in
  --once) ONCE=1 ;;
  "") ;;
  *) echo "usage: snitch.sh [--once]" >&2; exit 2 ;;
esac

CW="$(cd "$(dirname "$0")" && pwd)/context-watch.py"
export CLAUDE_PROJECTS_DIR="${CLAUDE_PROJECTS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects}"
INTERVAL="${SNITCH_INTERVAL:-300}"
ACTIVE_MINS="${SNITCH_ACTIVE_MINS:-15}"
IDLE_SECS="${SNITCH_IDLE_SECS:-7200}"
export CONTEXT_RUNNING_SECS="${CONTEXT_RUNNING_SECS:-$((INTERVAL + 60))}"
SEEN="${SNITCH_SEEN:-${TMPDIR:-/tmp}/snitch-${USER:-$(id -un)}/seen}"
SELF="${CLAUDE_CODE_SESSION_ID:-}"

{ mkdir -p "$(dirname "$SEEN")" && touch "$SEEN"; } || { echo "snitch: cannot write $SEEN" >&2; exit 2; }
[ -f "$CW" ] || { echo "snitch: missing $CW" >&2; exit 2; }

# Prints one "<session-dir>" per session with a subagent transcript changed in the window.
active_sessions() {
  find "$CLAUDE_PROJECTS_DIR" -path '*/subagents/*' -name 'agent-*.jsonl' -mmin "-$ACTIVE_MINS" 2>/dev/null |
    while IFS= read -r f; do dirname "$(dirname "$f")"; done | sort -u
}

# Prints new alert lines and records them in $SEEN; returns 0 if any session was active.
scan() {
  local sdir sid proj who line key status out rc compact found=1
  while IFS= read -r sdir; do
    [ -n "$sdir" ] || continue
    found=0
    sid=$(basename "$sdir")
    proj=$(basename "$(dirname "$sdir")")
    who=other; [ "$sid" = "$SELF" ] && who=self
    out=$(python3 "$CW" "$sid" 2>&1); rc=$?
    case "$rc" in 0|2) ;; *) out+=$'\n'"context-watch exited $rc" ;; esac
    compact=0
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      status=$(awk '{print $3}' <<<"$line")
      case "$status" in
        warn|handoff) key="$sid $(awk '{print $1}' <<<"$line") $status" ;;
        compact-now) compact=1; key="$sid session compact-now" ;;
        # Anything else (context-watch: errors, tracebacks, a missing python3) must not go unseen.
        *) key="$sid - error $(printf '%s' "$line" | cksum | awk '{print $1}')" ;;
      esac
      grep -qxF -- "$key" "$SEEN" && continue
      echo "$key" >>"$SEEN"
      printf '%s  %s  %s  %s\n' "$who" "$sid" "$proj" "$line"
    done <<<"$out"
    # Once the orchestrator is back under HANDOFF, a later regrowth must alert again.
    if [ "$compact" = 0 ] && grep -qxF -- "$sid session compact-now" "$SEEN"; then
      grep -vxF -- "$sid session compact-now" "$SEEN" >"$SEEN.tmp"; mv "$SEEN.tmp" "$SEEN"
    fi
  done < <(active_sessions)
  return "$found"
}

last_active=$(date +%s)
while true; do
  new=$(scan) && last_active=$(date +%s)
  if [ -n "$new" ]; then
    echo "SNITCH $(date +%H:%M)"
    printf '%s\n' "$new"
    exit 0
  fi
  [ "$ONCE" = 1 ] && exit 0
  idle=$(( $(date +%s) - last_active ))
  if [ "$idle" -ge "$IDLE_SECS" ]; then
    echo "SNITCH $(date +%H:%M) idle: no active subagents for $((idle / 60)) min; exiting"
    exit 0
  fi
  sleep "$INTERVAL"
done
