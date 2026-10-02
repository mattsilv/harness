"""Fixture tests for template/scripts/context-watch.py. Run: python3 -m unittest discover tests"""
import json, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "template/scripts/context-watch.py"
SID = "sess-1"


def turn(tokens, kind="assistant"):
    u = {"input_tokens": 2, "cache_read_input_tokens": tokens - 12, "cache_creation_input_tokens": 10, "output_tokens": 5}
    return json.dumps({"type": kind, "message": {"usage": u}})


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.proj = Path(self.tmp.name) / "-proj"
        self.subs = self.proj / SID / "subagents"
        self.subs.mkdir(parents=True)
        self.session(10000)

    def session(self, tokens):
        (self.proj / f"{SID}.jsonl").write_text("\n".join(["{}", turn(tokens)]) + "\n")

    def agent(self, name, lines, desc="task", age=0):
        f = self.subs / f"agent-{name}.jsonl"
        f.write_text("\n".join(lines) + "\n")
        (self.subs / f"agent-{name}.meta.json").write_text(json.dumps({"description": desc}))
        if age:
            t = time.time() - age
            os.utime(f, (t, t))

    def run_watch(self, **env):
        e = {**os.environ, "CLAUDE_PROJECTS_DIR": self.tmp.name, "CLAUDE_CODE_SESSION_ID": SID, **env}
        return subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=e)


class ContextWatch(Fixture):
    def test_thresholds(self):
        self.agent("low", ["{}", turn(199999)])
        self.agent("warn", ["{}", turn(200000)], "at warn")
        self.agent("mid", ["{}", turn(249999)], "below handoff")
        self.agent("hand", ["{}", turn(250000)], "at handoff")
        self.agent("over", ["{}", turn(300000)], "over")
        r = self.run_watch()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [
            "hand  250000  handoff  at handoff", "mid  249999  warn  below handoff",
            "over  300000  handoff  over", "warn  200000  warn  at warn"])

    def test_last_assistant_line_wins_and_ignores_other_types(self):
        self.agent("a", [turn(290000), turn(100000), turn(999999, "user")])
        self.assertEqual(self.run_watch().stdout, "")

    def test_stale_agent_ignored(self):
        self.agent("old", [turn(400000)], age=600)
        self.assertEqual(self.run_watch().stdout, "")

    def test_env_overrides(self):
        self.agent("a", [turn(1000)], "small")
        self.session(100)
        self.assertEqual(self.run_watch(CONTEXT_WARN="500", CONTEXT_HANDOFF="900").stdout, "a  1000  handoff  small\n")

    def test_missing_usage_errors(self):
        self.agent("bad", ["x" * 100] * 3)
        r = self.run_watch(CONTEXT_TAIL_BYTES="100")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no assistant usage line", r.stderr)

    def test_just_started_agent_is_fine(self):
        self.agent("new", ['{"type":"user"}'])
        r = self.run_watch()
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_orchestrator_notice_needs_running_agent(self):
        self.session(260000)
        self.assertEqual(self.run_watch().stdout, "")
        self.agent("a", [turn(1000)])
        self.assertEqual(self.run_watch().stdout, "session  260000  compact-now  orchestrator\n")
        self.session(249999)
        self.assertEqual(self.run_watch().stdout, "")

    def test_unknown_session_errors(self):
        r = self.run_watch(CLAUDE_CODE_SESSION_ID="nope")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
