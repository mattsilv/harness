"""Fixture tests for template/scripts/snitch.sh. Run: python3 -m unittest discover tests"""
import json, os, re, subprocess, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "template/scripts/snitch.sh"
SID = "11111111-2222-3333-4444-555555555555"
# The caller's own session and thresholds must not leak into the fake.
BASE_ENV = {k: v for k, v in os.environ.items() if not re.match(r"^(CONTEXT_|SNITCH_|CLAUDE_)", k)}


def turn(tokens):
    return json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": tokens}}}) + "\n"


class Snitch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.projects = root / "projects"
        proj = self.projects / "-Users-x-repo"
        sub = proj / SID / "subagents"
        sub.mkdir(parents=True)
        self.session = proj / f"{SID}.jsonl"
        self.session.write_text(turn(1000))
        self.agent = sub / "agent-abc.jsonl"
        (sub / "agent-abc.meta.json").write_text(json.dumps({"description": "big task"}))
        self.seen = root / "state" / "seen"

    def run_once(self, **env):
        e = {**BASE_ENV, "CLAUDE_PROJECTS_DIR": str(self.projects), "SNITCH_SEEN": str(self.seen),
             "CLAUDE_CODE_SESSION_ID": SID, **env}
        return subprocess.run(["bash", str(SCRIPT), "--once"], capture_output=True, text=True, env=e)

    def test_alerts_once_per_status_and_again_on_escalation(self):
        self.agent.write_text(turn(210_000))
        first = self.run_once()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertRegex(first.stdout, r"^SNITCH \d\d:\d\d\n")
        self.assertIn(f"self  {SID}  -Users-x-repo  abc  210010  warn  big task", first.stdout)
        self.assertEqual(self.run_once().stdout, "")  # same warn: deduped
        self.agent.write_text(turn(260_000))
        third = self.run_once()
        self.assertIn("abc  260010  handoff", third.stdout)
        self.assertNotIn("warn", third.stdout)

    def test_other_session_label_and_quiet_below_warn(self):
        self.agent.write_text(turn(50_000))
        self.assertEqual(self.run_once().stdout, "")
        self.agent.write_text(turn(210_000))
        self.assertIn(f"other  {SID}", self.run_once(CLAUDE_CODE_SESSION_ID="someone-else").stdout)

    def test_reports_context_watch_failure(self):
        self.agent.write_text("x" * 600_000)  # over the tail window with no usage line
        self.assertRegex(self.run_once().stdout, r"context-watch: .*no assistant usage line")

    def test_compact_now_rearms_after_regrowth(self):
        self.agent.write_text(turn(1000))
        self.session.write_text(turn(260_000))
        self.assertIn("session  260010  compact-now", self.run_once().stdout)
        self.assertEqual(self.run_once().stdout, "")
        self.session.write_text(turn(10_000))
        self.assertEqual(self.run_once().stdout, "")
        self.session.write_text(turn(270_000))
        self.assertIn("session  270010  compact-now", self.run_once().stdout)

    def test_rejects_unknown_argument(self):
        r = subprocess.run(["bash", str(SCRIPT), "--onc"], capture_output=True, text=True, env=BASE_ENV)
        self.assertEqual(r.returncode, 2)

    def test_idle_exit_when_no_subagent_is_active(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        e = {**BASE_ENV, "CLAUDE_PROJECTS_DIR": str(empty), "SNITCH_SEEN": str(self.seen), "SNITCH_IDLE_SECS": "0"}
        r = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 0)
        self.assertRegex(r.stdout, r"idle: no active subagents")


if __name__ == "__main__":
    unittest.main()
