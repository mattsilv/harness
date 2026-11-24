"""Fixture tests for the harness CLI: context size, required CI check, seeds, maintenance, audit."""
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


WORKFLOW = "jobs:\n  checks:\n    runs-on: ubuntu-latest\n"
NOT_PROTECTED = (1, "", "gh: Branch not protected (HTTP 404)")
NO_RULES = (0, "[]", "")


def ok(data):
    return 0, json.dumps(data), ""


class RequiredCiCheck(unittest.TestCase):
    """report_ci_gate against stubbed `gh api` replies; no network."""

    def run_gate(self, gh, config="- **Merge policy:** `auto`\n", workflow=WORKFLOW, runs=1):
        """gh maps an API path suffix to (returncode, stdout, stderr), a list of them, or an exception."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "PROJECT_CONFIG.md").write_text(config)
        if workflow:
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(workflow)
        old = os.getcwd()
        os.chdir(root)
        self.addCleanup(os.chdir, old)
        calls = []

        def fake_run(cmd, **kw):
            if cmd[0] != "gh":
                return subprocess.CompletedProcess(cmd, 0, "origin/main\n", "")
            calls.append(cmd[2])
            reply = next(v for k, v in gh.items() if cmd[2].endswith(k))
            if isinstance(reply, list):
                reply = reply.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return subprocess.CompletedProcess(cmd, *reply)

        outs = []
        with mock.patch.object(harness, "CACHE", root / "cache"), \
                mock.patch.object(harness.subprocess, "run", fake_run):
            for _ in range(runs):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    harness.report_ci_gate()
                outs.append(out.getvalue())
        return (outs[0] if runs == 1 else outs), calls

    def test_classic_protection_requiring_the_check_passes(self):
        out, _ = self.run_gate({"rules/branches/main": NO_RULES, "/protection": ok(
            {"required_status_checks": {"strict": False, "contexts": ["checks"],
                                        "checks": [{"context": "checks", "app_id": 15368}]}})})
        self.assertEqual("", out)

    def test_ruleset_requiring_the_check_passes_without_reading_protection(self):
        out, calls = self.run_gate({"rules/branches/main": ok([{
            "type": "required_status_checks", "ruleset_id": 7,
            "parameters": {"required_status_checks": [{"context": "checks"}]}}])})
        self.assertEqual("", out)
        self.assertEqual(1, len(calls))

    def test_unprotected_branch_prints_the_put_command(self):
        out, _ = self.run_gate({"rules/branches/main": NO_RULES, "/protection": NOT_PROTECTED})
        self.assertIn("`main` does not require the CI check `checks`", out)
        cmd = next(l for l in out.splitlines() if "gh api -X PUT" in l)
        body = json.loads(cmd.split("'")[1])
        self.assertEqual([{"context": "checks", "app_id": 15368}],
                         body["required_status_checks"]["checks"])
        self.assertFalse(body["required_status_checks"]["strict"])
        self.assertFalse(body["allow_force_pushes"])
        self.assertIn("repos/{owner}/{repo}/branches/main/protection --input -", cmd)
        self.assertIn("treat merges as `on-request`", out)

    def test_existing_required_checks_are_kept(self):
        out, _ = self.run_gate({"rules/branches/main": NO_RULES, "/protection": ok(
            {"required_status_checks": {"strict": True, "contexts": ["build"],
                                        "checks": [{"context": "build", "app_id": None}]}})})
        cmd = next(l for l in out.splitlines() if "gh api -X PATCH" in l)
        self.assertEqual({"strict": True, "checks": [{"context": "build"},
                                                     {"context": "checks", "app_id": 15368}]},
                         json.loads(cmd.split("'")[1]))
        self.assertIn("(it requires `build`)", out)

    def test_ruleset_requiring_other_checks_names_the_ruleset(self):
        out, _ = self.run_gate({"rules/branches/main": ok([{
            "type": "required_status_checks", "ruleset_id": 42,
            "parameters": {"required_status_checks": [{"context": "lint"}]}}]),
            "/protection": NOT_PROTECTED})
        self.assertIn("ruleset 42", out)
        self.assertNotIn("gh api -X PUT", out)

    def test_private_repo_without_protection_on_its_plan(self):
        upgrade = (1, "", "gh: Upgrade to GitHub Pro or make this repository public to "
                          "enable this feature. (HTTP 403)")
        out, _ = self.run_gate({"rules/branches/main": upgrade, "/protection": upgrade})
        self.assertIn("plan has no branch protection or rulesets", out)
        self.assertIn("**Required CI check:** `none`", out)

    def test_gh_not_authenticated(self):
        out, _ = self.run_gate({"rules/branches/main": (
            4, "", "To get started with GitHub CLI, please run:  gh auth login")})
        self.assertIn("could not verify", out)
        self.assertIn("gh auth login", out)
        self.assertIn("treat merges as `on-request`", out)

    def test_gh_not_installed(self):
        out, _ = self.run_gate({"rules/branches/main": FileNotFoundError("gh")})
        self.assertIn("gh is not installed", out)

    def test_missing_workflow_is_reported_even_when_the_branch_requires_it(self):
        out, _ = self.run_gate({"rules/branches/main": ok([{
            "type": "required_status_checks", "ruleset_id": 7,
            "parameters": {"required_status_checks": [{"context": "checks"}]}}])}, workflow=None)
        self.assertIn("no workflow in .github/workflows has a job reporting", out)
        self.assertIn("harness apply .github/workflows/checks.yml scripts/checks.sh", out)

    def test_on_request_still_checks_without_the_auto_note(self):
        out, _ = self.run_gate({"rules/branches/main": NO_RULES, "/protection": NOT_PROTECTED},
                               config="- **Merge policy:** `on-request`\n")
        self.assertIn("does not require the CI check", out)
        self.assertNotIn("treat merges as", out)

    def test_custom_check_name_and_opt_out(self):
        out, _ = self.run_gate({"rules/branches/main": NO_RULES, "/protection": NOT_PROTECTED},
                               config="- **Required CI check:** `ci`\n", workflow=WORKFLOW)
        self.assertIn("required check `ci`", out)
        out, calls = self.run_gate({}, config="- **Required CI check:** `none`\n")
        self.assertEqual(("", []), (out, calls))

    def test_no_github_remote_is_quiet_unless_auto(self):
        none = {"rules/branches/main": (1, "", "unable to expand placeholder in path: none of "
                                              "the git remotes configured for this repository "
                                              "point to a known GitHub host. To tell gh about a "
                                              "new GitHub host, please use `gh auth login`")}
        out, _ = self.run_gate(dict(none), config="- **Merge policy:** `on-request`\n")
        self.assertEqual("", out)
        out, _ = self.run_gate(dict(none))
        self.assertIn("could not verify", out)

    def test_only_a_passing_answer_is_cached(self):
        passing = ok([{"type": "required_status_checks", "ruleset_id": 7,
                       "parameters": {"required_status_checks": [{"context": "checks"}]}}])
        outs, calls = self.run_gate({"rules/branches/main": [NO_RULES, passing],
                                     "/protection": NOT_PROTECTED}, runs=3)
        self.assertIn("does not require", outs[0])
        self.assertEqual(["", ""], outs[1:])
        self.assertEqual(3, len(calls), "failure re-asked, then the pass served from cache")


class WorkflowCheckNames(unittest.TestCase):
    def test_job_name_overrides_id_and_step_names_do_not_count(self):
        text = """name: checks
on: push
jobs:
    build:
        name: "Build"
        steps:
            - uses: x
              name: checks
    test:  # comment
        runs-on: x
        steps:
            - name: checks
permissions: {}
"""
        self.assertEqual(["Build", "test"], harness.workflow_check_names(text))

    def test_template_workflow_provides_checks(self):
        text = (Path(__file__).parent.parent / "template/.github/workflows/checks.yml").read_text()
        self.assertEqual(["checks"], harness.workflow_check_names(text))


class SeededCiFiles(unittest.TestCase):
    """The default CI workflow is added only when no workflow provides the required check."""

    def init_in(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        src = root / "harness" / "template"
        for p, text in {".github/workflows/checks.yml": WORKFLOW, "scripts/checks.sh": "x\n",
                        "AGENTS.md": "rules\n"}.items():
            (src / p).parent.mkdir(parents=True, exist_ok=True)
            (src / p).write_text(text)
        repo = root / "repo"
        for p, text in files.items():
            (repo / p).parent.mkdir(parents=True, exist_ok=True)
            (repo / p).write_text(text)
        repo.mkdir(exist_ok=True)
        old = os.getcwd()
        os.chdir(repo)
        self.addCleanup(os.chdir, old)
        with mock.patch.object(harness, "SOURCE", str(src)), \
                contextlib.redirect_stdout(io.StringIO()):
            harness.cmd_init()
            return repo, harness.changed(harness.fetch())

    def test_seeded_when_absent_then_managed(self):
        repo, changed = self.init_in({})
        self.assertEqual(WORKFLOW, (repo / ".github/workflows/checks.yml").read_text())
        self.assertTrue((repo / ".harness/base/scripts/checks.sh").exists())
        self.assertEqual([], changed)

    def test_existing_workflow_is_left_alone(self):
        own = "jobs:\n  lint:\n    name: checks\n    runs-on: x\n"
        repo, changed = self.init_in({".github/workflows/ci.yml": own})
        self.assertFalse((repo / ".github/workflows/checks.yml").exists())
        self.assertFalse((repo / "scripts/checks.sh").exists())
        self.assertEqual([], changed, "skipped seeds must not show as harness changes")

    def test_existing_checks_yml_is_never_overwritten(self):
        own = "jobs:\n  build:\n    runs-on: x\n"
        repo, changed = self.init_in({".github/workflows/checks.yml": own})
        self.assertEqual(own, (repo / ".github/workflows/checks.yml").read_text())
        self.assertFalse((repo / ".harness/base/.github/workflows/checks.yml").exists())
        self.assertEqual([], changed)


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

    def test_date_is_found_anywhere_on_the_field_line(self):
        today = datetime.date.today().isoformat()
        outs, _ = self.run_checks([f"| Daily last completed: | done by agent | {today} |"])
        self.assertEqual("", outs[0])

    def test_status_edit_shows_immediately(self):
        today = datetime.date.today().isoformat()
        outs, calls = self.run_checks([
            "- **Daily last completed:** 2020-01-01 00:00 UTC",
            f"- **Daily last completed:** {today} 00:00 UTC",
        ])
        self.assertIn("daily maintenance due (last completed: 2020-01-01", outs[0])
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
