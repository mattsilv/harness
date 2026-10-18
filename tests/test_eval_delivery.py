"""Deterministic delivery-check fixtures; these tests do not launch a browser."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "eval" / "delivery.mjs"
CANDIDATE = ROOT / "eval" / "candidates" / "delivery-check.py"


class DeliveryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Harness Test")
        self.git("config", "user.email", "harness-test@example.invalid")
        (self.repo / "index.html").write_text("<!doctype html><h1>To-do</h1>\n")
        self.git("add", "index.html")
        self.git("commit", "-m", "baseline")
        self.baseline = self.git("rev-parse", "HEAD")
        self.git("switch", "-c", "feat/title")
        (self.repo / "delivery.txt").write_text("feature branch work\n")
        self.git("add", "delivery.txt")
        self.git("commit", "-m", "record feature work")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def run_delivery(self, baseline=None):
        args = ["node", str(DELIVERY), str(self.repo)]
        if baseline is not None:
            args.append(baseline)
        return subprocess.run(args, capture_output=True, text=True, timeout=10)

    def run_candidate(self, repo=None):
        return subprocess.run([sys.executable, str(CANDIDATE), str(repo or self.repo)],
                              capture_output=True, text=True, timeout=10)

    def run_unpinned_delivery(self, repo):
        module = DELIVERY.as_uri()
        code = f'import {{ delivery }} from "{module}"; console.log(JSON.stringify(delivery(process.argv[1])))'
        return subprocess.run(["node", "--input-type=module", "-e", code, str(repo)],
                              capture_output=True, text=True, timeout=10)

    def test_clean_feature_branch_delivery_passes(self):
        result = self.run_delivery(self.baseline)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({"committed": "pass", "on_branch": "pass", "default_untouched": "pass"},
                         json.loads(result.stdout))
        candidate = self.run_candidate()
        self.assertEqual(candidate.returncode, 0, candidate.stderr)
        self.assertTrue(json.loads(candidate.stdout)["passed"])

    def test_dirty_tracked_and_untracked_paths_fail(self):
        (self.repo / "index.html").write_text("<!doctype html><h1>Changed</h1>\n")
        (self.repo / "scratch.txt").write_text("untracked\n")
        result = json.loads(self.run_delivery(self.baseline).stdout)
        self.assertTrue(result["committed"].startswith("fail:"))
        self.assertFalse(json.loads(self.run_candidate().stdout)["passed"])

    def test_default_branch_movement_fails_even_with_feature_commit(self):
        self.git("switch", "main")
        (self.repo / "baseline-extra.txt").write_text("main changed\n")
        self.git("add", "baseline-extra.txt")
        self.git("commit", "-m", "move main")
        self.git("switch", "feat/title")
        result = json.loads(self.run_delivery(self.baseline).stdout)
        self.assertEqual("pass", result["committed"])
        self.assertEqual("pass", result["on_branch"])
        self.assertTrue(result["default_untouched"].startswith("fail:"))
        self.assertFalse(json.loads(self.run_candidate().stdout)["passed"])

    def test_tag_named_main_does_not_stand_in_for_default_branch(self):
        self.git("branch", "-D", "main")
        self.git("tag", "main", self.baseline)
        result = self.run_delivery(self.baseline)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(all(value.startswith("fail:") for value in json.loads(result.stdout).values()))
        self.assertFalse(json.loads(self.run_candidate().stdout)["passed"])

    def test_wrong_and_missing_baselines_fail_closed(self):
        wrong = "0" * 40
        result = self.run_delivery(wrong)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(all(value.startswith("fail:") for value in json.loads(result.stdout).values()))
        wrong_existing = self.git("rev-parse", "HEAD")
        result = self.run_delivery(wrong_existing)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(all(value.startswith("fail:") for value in json.loads(result.stdout).values()))
        missing = self.run_delivery()
        self.assertEqual(missing.returncode, 2)
        self.assertIn("usage:", missing.stderr)

    def test_legacy_unpinned_non_repository_remains_unverified(self):
        empty = Path(self.temp.name) / "not-a-repo"
        empty.mkdir()
        result = json.loads(self.run_unpinned_delivery(empty).stdout)
        self.assertEqual({"committed": "unverified", "on_branch": "unverified",
                          "default_untouched": "unverified"}, result)

    def test_candidate_does_not_read_app_files_or_reveal_task_answer(self):
        outside = Path(self.temp.name) / "outside.html"
        outside.write_text("<!doctype html><h1>My tasks</h1>\n")
        (self.repo / "index.html").unlink()
        (self.repo / "index.html").symlink_to(outside)
        self.git("add", "index.html")
        self.git("commit", "-m", "replace app file with symlink")
        result = json.loads(self.run_candidate().stdout)
        self.assertTrue(result["passed"])
        self.assertEqual({"clean_worktree", "committed_feature_branch", "main_unchanged"},
                         set(result["checks"]))


if __name__ == "__main__":
    unittest.main()
