"""Fixture tests for template/scripts/snitch.sh. Run: python3 -m unittest discover tests"""
import json, os, re, subprocess, tempfile, time, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "template/scripts/snitch.sh"
SID = "11111111-2222-3333-4444-555555555555"
# The caller's own session and thresholds must not leak into the fake.
BASE_ENV = {k: v for k, v in os.environ.items() if not re.match(r"^(CONTEXT_|SNITCH_|CLAUDE_)", k)}


def turn(tokens, stop=None):
    """One assistant record; stop="end_turn" is the final record of a finished agent."""
    return json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": tokens},
                                                        "stop_reason": stop}}) + "\n"


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

    def run_loop(self, *args, timeout=None, **env):
        """One scan in loop mode: exits on a new alert, or at once with an idle line (SNITCH_IDLE_SECS=0).
        A None value drops that variable from the environment."""
        e = {**BASE_ENV, "CLAUDE_PROJECTS_DIR": str(self.projects), "SNITCH_SEEN": str(self.seen),
             "CLAUDE_CODE_SESSION_ID": SID, "SNITCH_IDLE_SECS": "0", **env}
        e = {k: v for k, v in e.items() if v is not None}
        return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=e, timeout=timeout)

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

    # Issue #54 regressions, one test per finding.

    def test_1_claude_config_dir_locates_projects(self):
        self.agent.write_text(turn(260_000))
        r = self.run_loop(CLAUDE_PROJECTS_DIR=None, CLAUDE_CONFIG_DIR=self.tmp.name)
        self.assertIn("handoff", alerts(r), r.stdout + r.stderr)

    def test_2_compact_clear_needs_a_successful_scan(self):
        self.agent.write_text(turn(1000))
        self.session.write_text(turn(260_000))
        self.assertIn("compact-now", alerts(self.run_loop()))
        # context-watch errors on the session transcript (rc=2): no evidence the orchestrator compacted.
        good = self.session.read_text()
        self.session.write_text("x" * 600_000)
        self.assertRegex(alerts(self.run_loop()), r"context-watch: ")
        self.session.write_text(good)
        self.assertEqual(alerts(self.run_loop()), "")  # compact-now must not re-fire
        # The agent is active for find (-mmin) but not for context-watch (CONTEXT_RUNNING_SECS): no scan of the session.
        t = time.time() - 300
        os.utime(self.agent, (t, t))
        self.assertEqual(alerts(self.run_loop(CONTEXT_RUNNING_SECS="60")), "")
        self.agent.write_text(turn(1000))
        self.assertEqual(alerts(self.run_loop(CONTEXT_RUNNING_SECS="60")), "")  # still no re-fire
        self.session.write_text(turn(10_000))
        self.assertEqual(alerts(self.run_loop()), "")  # a real clear
        self.session.write_text(turn(270_000))
        self.assertIn("compact-now", alerts(self.run_loop()))

    def test_3_claim_is_atomic_marker_not_seen_grep(self):
        self.agent.write_text(turn(260_000))
        self.state.mkdir()
        (self.state / f"key-{SID}_abc_handoff").touch()  # another snitch claimed it; its append may not have landed yet
        self.assertEqual(alerts(self.run_loop()), "")
        (self.state / f"key-{SID}_abc_handoff").unlink()
        self.assertIn("handoff", alerts(self.run_loop()))
        self.assertTrue((self.state / f"key-{SID}_abc_handoff").exists())  # the claim is the marker

    def test_3_concurrent_snitches_deliver_a_handoff_once(self):
        self.agent.write_text(turn(260_000))
        e = {**BASE_ENV, "CLAUDE_PROJECTS_DIR": str(self.projects), "SNITCH_SEEN": str(self.seen),
             "CLAUDE_CODE_SESSION_ID": "someone-else", "SNITCH_IDLE_SECS": "0"}
        procs = [subprocess.Popen(["bash", str(SCRIPT)], stdout=subprocess.PIPE, text=True, env=e) for _ in range(8)]
        outs = [p.communicate(timeout=60)[0] for p in procs]
        lines = [l for o in outs for l in o.splitlines() if "handoff" in l]
        self.assertEqual(len(lines), 1, outs)

    def test_4_idle_timer_ignores_sessions_owned_by_another_snitch(self):
        self.agent.write_text(turn(260_000))
        self.state.mkdir()
        (self.state / f"alive-{SID}").touch()
        r = self.run_loop(CLAUDE_CODE_SESSION_ID="someone-else", SNITCH_IDLE_SECS="1", SNITCH_INTERVAL="1", timeout=20)
        self.assertRegex(r.stdout, r"idle: no active subagents")

    def test_5_finished_agent_is_not_reported(self):
        self.agent.write_text(turn(240_000) + turn(260_000, stop="end_turn"))
        self.session.write_text(turn(260_000))
        self.assertEqual(alerts(self.run_loop()), "")  # no handoff, and no compact-now: nothing runs
        self.agent.write_text(turn(260_000, stop="end_turn") + json.dumps({"type": "user"}) + "\n")  # resumed
        self.assertIn("handoff", alerts(self.run_loop()))


if __name__ == "__main__":
    unittest.main()
