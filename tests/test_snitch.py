"""Fixture tests for template/scripts/snitch.sh. Run: python3 -m unittest discover tests"""
import json, os, re, subprocess, tempfile, time, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "template/scripts/snitch.sh"
SID = "11111111-2222-3333-4444-555555555555"
# The caller's own session and thresholds must not leak into the fake.
BASE_ENV = {k: v for k, v in os.environ.items() if not re.match(r"^(CONTEXT_|SNITCH_|CLAUDE_)", k)}


def turn(tokens):
    return json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": tokens}}}) + "\n"


def alerts(r):
    """Alert lines only: drops the SNITCH header and the idle exit line."""
    return "\n".join(l for l in r.stdout.splitlines() if not l.startswith("SNITCH "))


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
        self.state = root / "state"
        self.seen = self.state / "seen"

    def run_loop(self, *args, **env):
        """One scan in loop mode: exits on a new alert, or at once with an idle line (SNITCH_IDLE_SECS=0)."""
        e = {**BASE_ENV, "CLAUDE_PROJECTS_DIR": str(self.projects), "SNITCH_SEEN": str(self.seen),
             "CLAUDE_CODE_SESSION_ID": SID, "SNITCH_IDLE_SECS": "0", **env}
        return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=e)

    def test_alerts_once_per_status_and_again_on_escalation(self):
        self.agent.write_text(turn(210_000))
        first = self.run_loop()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertRegex(first.stdout, r"^SNITCH \d\d:\d\d\n")
        self.assertEqual(alerts(first), f"self  {SID}  -Users-x-repo  abc  210010  warn  big task")
        self.assertEqual(alerts(self.run_loop()), "")  # same warn: deduped
        self.agent.write_text(turn(260_000))
        third = alerts(self.run_loop())
        self.assertIn("abc  260010  handoff", third)
        self.assertNotIn("warn", third)

    def test_other_session_label_and_quiet_below_warn(self):
        self.agent.write_text(turn(50_000))
        self.assertEqual(alerts(self.run_loop(CLAUDE_CODE_SESSION_ID="someone-else")), "")
        self.agent.write_text(turn(210_000))
        self.assertIn(f"other  {SID}", alerts(self.run_loop(CLAUDE_CODE_SESSION_ID="someone-else")))

    def test_session_with_a_live_snitch_is_left_to_it(self):
        self.agent.write_text(turn(260_000))
        self.state.mkdir()
        (self.state / f"alive-{SID}").touch()  # SID's own snitch scanned recently
        self.assertEqual(alerts(self.run_loop(CLAUDE_CODE_SESSION_ID="someone-else")), "")
        self.assertIn("self  ", alerts(self.run_loop()))  # the owner still reports it
        self.assertTrue((self.state / "alive-someone-else").exists())  # each snitch leaves a heartbeat

    def test_once_reports_but_records_nothing(self):
        self.agent.write_text(turn(260_000))
        self.assertIn("handoff", alerts(self.run_loop("--once")))
        self.assertEqual(self.seen.read_text(), "")
        self.assertFalse((self.state / f"alive-{SID}").exists())
        self.assertIn("handoff", alerts(self.run_loop()))  # the background snitch still delivers it

    def test_reports_context_watch_failure(self):
        self.agent.write_text("x" * 600_000)  # over the tail window with no usage line
        self.assertRegex(alerts(self.run_loop()), r"context-watch: .*no assistant usage line")
        self.assertEqual(alerts(self.run_loop()), "")  # once per distinct message

    def test_compact_now_rearms_only_after_regrowth(self):
        self.agent.write_text(turn(1000))
        self.session.write_text(turn(260_000))
        self.assertIn("session  260010  compact-now", alerts(self.run_loop()))
        self.assertEqual(alerts(self.run_loop()), "")
        t = time.time() - 420  # a 7-minute pause in the subagent is not a compaction
        os.utime(self.agent, (t, t))
        self.assertEqual(alerts(self.run_loop()), "")
        self.agent.write_text(turn(1000))
        self.assertEqual(alerts(self.run_loop()), "")
        self.session.write_text(turn(10_000))
        self.assertEqual(alerts(self.run_loop()), "")
        self.session.write_text(turn(270_000))
        self.assertIn("session  270010  compact-now", alerts(self.run_loop()))

    def test_rejects_unknown_argument(self):
        r = subprocess.run(["bash", str(SCRIPT), "--onc"], capture_output=True, text=True, env=BASE_ENV)
        self.assertEqual(r.returncode, 2)

    def test_idle_exit_when_no_subagent_is_active(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        r = self.run_loop(CLAUDE_PROJECTS_DIR=str(empty))
        self.assertEqual(r.returncode, 0)
        self.assertRegex(r.stdout, r"idle: no active subagents")


if __name__ == "__main__":
    unittest.main()
