"""Fixture tests for the harness CLI's always-loaded context warning."""
import contextlib, datetime, io, json, os, subprocess, tempfile, unittest
from unittest import mock
from importlib.machinery import SourceFileLoader
from pathlib import Path

import types
harness = types.ModuleType("harness")  # load_module() was removed in Python 3.15
SourceFileLoader("harness", str(Path(__file__).parent.parent / "harness")).exec_module(harness)


class ContextSizeWarning(unittest.TestCase):
    def run_in(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        for name, size in files.items():
            (Path(tmp.name) / name).write_text("x" * size)
        old = os.getcwd()
        os.chdir(tmp.name)
        self.addCleanup(os.chdir, old)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            harness.report_context_size()
        return out.getvalue()

    def test_warns_over_threshold(self):
        out = self.run_in({"AGENTS.md": 9000, "CLAUDE.md": 9000, "PROJECT_CONFIG.md": 9000})
        self.assertIn("always-loaded context", out)
        self.assertIn("27000", out)

    def test_quiet_under_threshold(self):
        out = self.run_in({"AGENTS.md": 100, "CLAUDE.md": 10, "PROJECT_CONFIG.md": 100})
        self.assertEqual("", out)


class CiGateCache(unittest.TestCase):
    def run_gate(self, replies, runs):
        """Run report_ci_gate `runs` times with `gh` replying from `replies`; return (outputs, gh calls)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        (Path(tmp.name) / "PROJECT_CONFIG.md").write_text("- **Merge policy:** `auto`\n")
        old = os.getcwd()
        os.chdir(tmp.name)
        self.addCleanup(os.chdir, old)
        replies = iter(json.dumps(r) for r in replies)
        calls = []

        def fake_run(cmd, **kw):
            if cmd[0] == "gh":
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, next(replies), "")
            return subprocess.CompletedProcess(cmd, 0, "origin/main\n", "")

        outs = []
        with mock.patch.object(harness, "CACHE", Path(tmp.name) / "cache"), \
                mock.patch.object(harness.subprocess, "run", fake_run):
            for _ in range(runs):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    harness.report_ci_gate()
                outs.append(out.getvalue())
        return outs, calls

    def test_empty_answer_is_not_cached(self):
        outs, calls = self.run_gate([[], [{"type": "required_status_checks"}]], 2)
        self.assertIn("requires no CI checks", outs[0])
        self.assertEqual("", outs[1])
        self.assertEqual(2, len(calls))

    def test_positive_answer_is_cached(self):
        outs, calls = self.run_gate([[{"type": "required_status_checks"}]], 2)
        self.assertEqual(["", ""], outs)
        self.assertEqual(1, len(calls))


class MaintenanceStatus(unittest.TestCase):
    def run_checks(self, bodies):
        """Run report_maintenance once per issue body, all inside the cache window; return (outputs, gh calls)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "PROJECT_CONFIG.md").write_text("- **Maintenance tracking issue:** acme/app#1\n")
        (root / "docs").mkdir()
        (root / "docs" / "MAINTENANCE.md").write_text(
            "## Daily: last completed 1 or more days ago\n\n- a\n")
        old = os.getcwd()
        os.chdir(root)
        self.addCleanup(os.chdir, old)
        replies = iter(json.dumps({"number": 1, "labels": [], "body": b}) for b in bodies)
        calls = []

        def fake_run(cmd, **kw):
            if cmd[0] == "gh":
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, next(replies), "")
            return subprocess.CompletedProcess(cmd, 0, "2020-01-01\n", "")

        outs = []
        with mock.patch.object(harness, "CACHE", root / "cache"), \
                mock.patch.object(harness.subprocess, "run", fake_run):
            for _ in bodies:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    harness.report_maintenance()
                outs.append(out.getvalue())
        return outs, calls

    def test_status_edit_shows_immediately(self):
        today = datetime.date.today().isoformat()
        outs, calls = self.run_checks([
            "- **Daily last completed:** 2020-01-01 00:00 UTC",
            f"- **Daily last completed:** {today} 00:00 UTC",
        ])
        self.assertIn("daily maintenance due", outs[0])
        self.assertEqual("", outs[1])
        self.assertEqual(2, len(calls), "the status edit must be read, not served from cache")


class AuditSignals(unittest.TestCase):
    def session(self, lines):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        self.addCleanup(os.unlink, tmp.name)
        tmp.write("\n".join(json.dumps(x) for x in lines))
        tmp.close()
        return harness.audit_session(Path(tmp.name))

    def test_claude_tool_calls_count(self):
        fired = self.session([
            {"cwd": "/repo"},
            {"message": {"content": [{"type": "tool_use", "name": "Task", "input": {}}]}},
            {"message": {"content": [{"type": "tool_use", "name": "Bash",
                                      "input": {"command": "gh pr create"}}]}},
        ])
        self.assertEqual({"spawns a subagent", "creates a PR"}, fired)

    def test_prose_mentions_do_not_count(self):
        # Injected AGENTS.md text mentions every behavior; it must not inflate counts.
        fired = self.session([{"message": {"content": [
            {"type": "text", "text": "read PROJECT_CONFIG.md, use a worktree, gh issue create"}]}}])
        self.assertEqual(set(), fired)

    def test_codex_tool_calls_count(self):
        fired = self.session([
            {"payload": {"type": "custom_tool_call", "name": "exec",
                         "input": 'tools.exec_command({cmd:"cat PROJECT_CONFIG.md"})'}},
            {"payload": {"type": "function_call", "name": "shell",
                         "arguments": "cat docs/languages/python.md"}},
            {"payload": {"type": "custom_tool_call_output",  # output text must not count
                         "output": "gh issue create PROJECT_CONFIG.md"}},
        ])
        self.assertEqual({"touches PROJECT_CONFIG.md", "reads language rules"}, fired)

    def test_type_confused_lines_do_not_crash(self):
        fired = self.session([
            {"message": "tool_use"}, ["tool_use"], "function_call",
            {"message": {"content": "tool_use"}}, {"payload": "function_call"},
            {"message": {"content": [{"type": "tool_use", "name": "Bash",
                                      "input": {"command": "gh issue create"}}]}},
        ])
        self.assertEqual({"creates an issue"}, fired)

    def test_session_cwd(self):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        self.addCleanup(os.unlink, tmp.name)
        tmp.write(json.dumps({"payload": {"cwd": "/repo/sub"}}))
        tmp.close()
        self.assertEqual("/repo/sub", harness.session_cwd(Path(tmp.name)))


if __name__ == "__main__":
    unittest.main()
