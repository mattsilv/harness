#!/usr/bin/env bash
# Snitch: a zero-token background watcher for subagent context size (docs/SUBAGENT-CONTEXT-WATCH.md).
#
# Every interval it runs scripts/context-watch.py for each Claude Code session, in any project,
# whose subagents wrote a transcript recently. It EXITS on the first scan that finds a line it
# has not reported before; that exit is what wakes the orchestrator (run_in_background task
# notification). The orchestrator acts on each line, then starts the snitch again.
# It also exits when no session has active subagents for SNITCH_IDLE_SECS.
#
# Usage: bash scripts/snitch.sh [--once]      (--once: one scan, print unreported lines, record nothing, exit 0)
# Output: "SNITCH HH:MM" then one line per alert:
#   <self|other>  <session-id>  <project-dir>  <context-watch line>
# A session whose own snitch is alive (heartbeat file touched within 2 intervals) is reported only
# by that snitch; other snitches report sessions that have none.
# Env:
#   SNITCH_INTERVAL     seconds between scans (300)
#   SNITCH_ACTIVE_MINS  a session counts if a subagent transcript changed within this many minutes (15)
#   SNITCH_IDLE_SECS    exit after this long with no active subagents anywhere (7200)
#   SNITCH_SEEN         append-only dedupe file (${TMPDIR:-/tmp}/snitch-$USER/seen); heartbeats live beside it.
#                       Keys: "<session> <agent> <status>", "<session> session compact-now|compact-clear"
#                       (the last one wins), "<session> - error <cksum>"
#   CLAUDE_PROJECTS_DIR transcripts root ($HOME/.claude/projects, as in context-watch.py)
#   CONTEXT_RUNNING_SECS defaults to SNITCH_ACTIVE_MINS*60, so a subagent counts as running for as long
#                       as its session counts as active; CONTEXT_WARN, CONTEXT_HANDOFF and the other
#                       context-watch.py variables pass through.
set -u

ONCE=0
case "${1:-}" in
  --once) ONCE=1 ;;
  "") ;;
  *) echo "usage: snitch.sh [--once]" >&2; exit 2 ;;
esac

CW="$(cd "$(dirname "$0")" && pwd)/context-watch.py"
export CLAUDE_PROJECTS_DIR="${CLAUDE_PROJECTS_DIR:-$HOME/.claude/projects}"
INTERVAL="${SNITCH_INTERVAL:-300}"
ACTIVE_MINS="${SNITCH_ACTIVE_MINS:-15}"
IDLE_SECS="${SNITCH_IDLE_SECS:-7200}"
export CONTEXT_RUNNING_SECS="${CONTEXT_RUNNING_SECS:-$((ACTIVE_MINS * 60))}"
SEEN="${SNITCH_SEEN:-${TMPDIR:-/tmp}/snitch-${USER:-$(id -un)}/seen}"
STATE_DIR="$(dirname "$SEEN")"
SELF="${CLAUDE_CODE_SESSION_ID:-}"
ALIVE_MINS=$(( (INTERVAL * 2 + 59) / 60 ))

{ mkdir -p "$STATE_DIR" && touch "$SEEN"; } || { echo "snitch: cannot write $SEEN" >&2; exit 2; }
[ -f "$CW" ] || { echo "snitch: missing $CW" >&2; exit 2; }

# Prints one "<session-dir>" per session with a subagent transcript changed in the window.
active_sessions() {
  find "$CLAUDE_PROJECTS_DIR" -path '*/subagents/*' -name 'agent-*.jsonl' -mmin "-$ACTIVE_MINS" 2>/dev/null |
    while IFS= read -r f; do dirname "$(dirname "$f")"; done | sort -u
}

# Another snitch owns this session if its heartbeat is fresh.
owned_elsewhere() { [ -n "$(find "$STATE_DIR" -maxdepth 1 -name "alive-$1" -mmin "-$ALIVE_MINS" 2>/dev/null)" ]; }
seen() { grep -qxF -- "$1" "$SEEN"; }
record() { [ "$ONCE" = 1 ] || echo "$1" >>"$SEEN"; }   # append-only: safe with several snitches on one file
compact_state() { grep -F -- "$1 session compact-" "$SEEN" | tail -n 1; }

# Prints new alert lines and records them; returns 0 if any session was active.
scan() {
  local sdir sid proj who line key agent status out rc compact found=1
  [ -n "$SELF" ] && [ "$ONCE" = 0 ] && touch "$STATE_DIR/alive-$SELF"
  while IFS= read -r sdir; do
    [ -n "$sdir" ] || continue
    found=0
    sid=$(basename "$sdir")
    proj=$(basename "$(dirname "$sdir")")
    who=other; [ "$sid" = "$SELF" ] && who=self
    [ "$who" = other ] && owned_elsewhere "$sid" && continue
    out=$(python3 "$CW" "$sid" 2>&1); rc=$?
    case "$rc" in 0|2) ;; *) out+=$'\n'"context-watch exited $rc" ;; esac
    compact=0
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      read -r agent _ status _ <<<"$line"
      case "$status" in
        warn|handoff) key="$sid $agent $status" ;;
        compact-now) compact=1; key="$sid session compact-now"
          [ "$(compact_state "$sid")" = "$key" ] && continue ;;
        # Anything else (context-watch: errors, tracebacks, a missing python3) must not go unseen.
        *) key="$sid - error $(printf '%s' "$line" | cksum | cut -d' ' -f1)" ;;
      esac
      [ "$status" = compact-now ] || ! seen "$key" || continue
      record "$key"
      printf '%s  %s  %s  %s\n' "$who" "$sid" "$proj" "$line"
    done <<<"$out"
    # Once the orchestrator is back under HANDOFF, a later regrowth must alert again.
    if [ "$compact" = 0 ] && [ "$(compact_state "$sid")" = "$sid session compact-now" ]; then
      record "$sid session compact-clear"
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
