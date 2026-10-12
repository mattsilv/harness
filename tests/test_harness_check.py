"""Fixture tests for the harness CLI's always-loaded context warning."""
import contextlib, io, os, tempfile, unittest
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


if __name__ == "__main__":
    unittest.main()
