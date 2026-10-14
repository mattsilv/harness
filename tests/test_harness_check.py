"""Fixture tests for the harness CLI's always-loaded context warning."""
import contextlib, io, json, os, subprocess, tempfile, unittest
from unittest import mock
from importlib.machinery import SourceFileLoader
from pathlib import Path

harness = SourceFileLoader("harness", str(Path(__file__).parent.parent / "harness")).load_module()


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


if __name__ == "__main__":
    unittest.main()
