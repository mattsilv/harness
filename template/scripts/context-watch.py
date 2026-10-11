#!/usr/bin/env python3
"""Context-window watchdog for Claude Code sessions (AGENTS.md Delegation; dependency-free, Python 3.9+).

Prints one line per running subagent whose context is at or above WARN, and a
`compact-now` line for the orchestrating session when it is at or above HANDOFF while
any subagent runs. Prints nothing otherwise. Exits 0 after watching at least one running
subagent, 3 when none is running (nothing was watched), and 2 with a message on any
surprise in the (undocumented) transcript format. Never acts on its own; the
orchestrator decides.

Usage: python3 scripts/context-watch.py [session-id]
Session id: argument, else $CLAUDE_CODE_SESSION_ID, else the newest transcript in the
project dir derived from the current directory. Transcripts are found by session id
under $CLAUDE_PROJECTS_DIR (default $CLAUDE_CONFIG_DIR/projects, then ~/.claude/projects),
so worktrees work too. A subagent is running if its transcript changed within
CONTEXT_RUNNING_SECS and its last message is neither a finished assistant turn (stop_reason
end_turn) nor the user's interrupt; such an agent is not reported, however recent. An agent
that ended its turn to wait on its own background work reads as finished until it resumes.
Env: CONTEXT_WARN (200000), CONTEXT_HANDOFF (250000), CONTEXT_RUNNING_SECS (120),
CONTEXT_TAIL_BYTES (524288).
"""
import json, os, re, sys, time
from pathlib import Path

WARN = int(os.environ.get("CONTEXT_WARN", 200000))
HANDOFF = int(os.environ.get("CONTEXT_HANDOFF", 250000))
RUNNING = int(os.environ.get("CONTEXT_RUNNING_SECS", 120))
TAIL = int(os.environ.get("CONTEXT_TAIL_BYTES", 524288))
ROOT = Path(os.environ.get("CLAUDE_PROJECTS_DIR")
            or os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude", "projects")).expanduser()


class Fail(Exception):
    pass


def die(msg):
    raise Fail(msg)


def find_session():
    sid = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not sid:
        slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
        files = list((ROOT / slug).glob("*.jsonl"))
        if not files:
            die(f"no session id (arg or CLAUDE_CODE_SESSION_ID) and no transcripts in {ROOT / slug}")
        sid = max(files, key=lambda p: p.stat().st_mtime).stem
    hits = list(ROOT.glob(f"*/{sid}.jsonl"))
    if len(hits) != 1:
        die(f"expected one transcript for session {sid} under {ROOT}, found {len(hits)}")
    return sid, hits[0]


def tail_records(path):
    """The transcript's last TAIL bytes as lines, and whether that is the whole file."""
    size = path.stat().st_size
    with open(path, "rb") as f:
        f.seek(max(0, size - TAIL))
        data = f.read()
    lines = data.split(b"\n")
    if size > TAIL:
        lines = lines[1:]  # first line is probably cut mid-record
    return lines, size <= TAIL


def finished(lines):
    """True if the last message record is an assistant turn that ended (stop_reason end_turn)
    or the user's interrupt. A running agent ends on a tool_use, a tool_result, or a
    still-streaming record; an agent resumed with a new message ends on that user record."""
    for raw in reversed(lines):
        if b'"assistant"' not in raw and b'"user"' not in raw:
            continue
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        if d.get("type") == "assistant":
            return (d.get("message") or {}).get("stop_reason") == "end_turn"
        if d.get("type") == "user":
            c = (d.get("message") or {}).get("content")
            text = c if isinstance(c, str) else "".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
            return text.startswith("[Request interrupted by user")
    return False


def context_tokens(path, lines=None, whole=None):
    """Tokens in context at the last assistant turn; None if the file has no turn yet."""
    if lines is None:
        lines, whole = tail_records(path)
    for raw in reversed(lines):
        if b'"assistant"' not in raw:
            continue
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        if d.get("type") != "assistant":
            continue
        u = (d.get("message") or {}).get("usage")
        if isinstance(u, dict):
            try:
                total = sum(int(u.get(k, 0) or 0) for k in
                            ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            except (TypeError, ValueError):
                die(f"{path.name}: non-numeric usage fields")
            if total:  # all-zero usage is a synthetic turn; keep looking
                return total
    if whole:
        return None  # whole file read, no assistant turn yet: agent just started
    die(f"{path}: no assistant usage line in the last {TAIL} bytes; transcript format changed?")


def main():
    sid, session_file = find_session()
    sub_dir = session_file.parent / sid / "subagents"
    now, out, running, errors = time.time(), [], 0, []
    for f in sorted(sub_dir.glob("agent-*.jsonl")) if sub_dir.is_dir() else []:
        try:
            if now - f.stat().st_mtime > RUNNING:
                continue
            lines, whole = tail_records(f)
            if finished(lines):
                continue
            running += 1
            tokens = context_tokens(f, lines, whole)
        except (Fail, OSError) as e:  # one bad transcript must not hide the others
            errors.append(str(e))
            continue
        if tokens is None or tokens < WARN:
            continue
        desc = ""
        try:
            desc = json.loads(f.with_suffix(".meta.json").read_text()).get("description", "")
        except (OSError, ValueError):
            pass
        out.append(f"{f.stem.removeprefix('agent-')}  {tokens}  {'handoff' if tokens >= HANDOFF else 'warn'}  {desc}")
    if running:
        try:
            tokens = context_tokens(session_file)
            if tokens is None:
                die(f"{session_file}: no assistant usage line")
            if tokens >= HANDOFF:
                out.append(f"session  {tokens}  compact-now  orchestrator")
        except (Fail, OSError) as e:
            errors.append(str(e))
    if out:
        print("\n".join(out))
    for e in errors:
        print(f"context-watch: {e}", file=sys.stderr)
    return 2 if errors else 0 if running else 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print(f"context-watch: {e}", file=sys.stderr)
        sys.exit(2)
