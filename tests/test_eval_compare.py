"""Comparison controls and failure recording; no model calls or network."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('compare', ROOT / 'eval' / 'compare.py')
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


class ComparisonTests(unittest.TestCase):
    def test_prepare_uses_real_init_and_keeps_evaluation_assets_out(self):
        with tempfile.TemporaryDirectory() as name:
            work = Path(name) / 'task'
            revision = compare.command(['git', 'rev-parse', 'HEAD'])
            baseline = compare.prepare(work, revision, False, 'delivery',
                (ROOT / 'eval/fixture/index.html').read_bytes(), b'')
            self.assertEqual(len(baseline), 40)
            self.assertEqual((work / 'CLAUDE.md').read_text(), '@AGENTS.md\n')
            self.assertTrue((work / '.harness/version').is_file())
            self.assertFalse((work / 'eval').exists())
            self.assertFalse((work / 'EVAL.md').exists())
            self.assertFalse((work / 'scripts/delivery-check.py').exists())
            self.assertEqual(compare.command(['git', 'status', '--porcelain'], cwd=work), '')

    def test_timeout_is_retained_and_process_group_stopped(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / '.tmp').mkdir()
            log = root / 'run.jsonl'
            state, code, duration = compare.run_process(
                [sys.executable, '-u', '-c', 'import time; print("started"); time.sleep(60)'],
                root, log, 0.2)
            self.assertEqual((state, code), ('timeout', None))
            self.assertIn('started', log.read_text())
            self.assertLess(duration, 5)

    def test_failed_command_keeps_output(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            log = root / 'failed.jsonl'
            state, code, _ = compare.run_process(
                [sys.executable, '-c', 'print("failure evidence"); raise SystemExit(7)'],
                root, log, 10)
            self.assertEqual((state, code), ('failed', 7))
            self.assertEqual(log.read_text().strip(), 'failure evidence')

    def test_usage_never_invents_zero(self):
        with tempfile.TemporaryDirectory() as name:
            log = Path(name) / 'events'
            log.write_text('not json\n{}\n')
            self.assertEqual(compare.usage(log), 'unavailable')
            log.write_text(json.dumps({'type': 'turn.completed', 'usage': {
                'input_tokens': 15, 'cached_input_tokens': 5, 'output_tokens': 3}}) + '\n')
            self.assertEqual(compare.usage(log)['input_tokens'], 15)

    def test_no_credentials_or_shell_startup_environment_is_forwarded(self):
        env = compare.clean_env(Path('/tmp/task'))
        for key in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'BASH_ENV', 'ENV', 'SSH_AUTH_SOCK'):
            self.assertNotIn(key, env)
        self.assertEqual(env['GIT_CONFIG_GLOBAL'], '/dev/null')
        self.assertEqual(env['GIT_CONFIG_SYSTEM'], '/dev/null')

    def test_all_prompts_exist_and_are_distinct(self):
        prompts = [compare.prompt(task) for task in compare.TASKS]
        self.assertEqual(len(set(prompts)), 3)
        self.assertIn('My tasks', prompts[-1])


if __name__ == '__main__':
    unittest.main()
