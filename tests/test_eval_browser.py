"""Browser regression checks for evaluator-owned task controls (no model calls)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHROME = os.environ.get('CHROME_PATH') or next((str(p) for p in [
    Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
    Path('/Applications/Chromium.app/Contents/MacOS/Chromium')]
    if p.exists()), None) or shutil.which('google-chrome') or shutil.which('chromium')

if os.environ.get('EVAL_REQUIRE_BROWSER') == '1' and not CHROME:
    raise RuntimeError('CI requires Chrome for evaluator integration tests')


@unittest.skipUnless(CHROME, 'Chrome is required for the evaluator integration test')
class BrowserEvaluatorTests(unittest.TestCase):
    def button_toggle_fixture(self, *, allow_blank=False):
        html = (ROOT / 'eval/fixture/index.html').read_text()
        html = html.replace('document.createElement("input")', 'document.createElement("button")')
        html = html.replace('box.type = "checkbox";', 'box.type = "button";')
        html = html.replace('box.checked = t.done;', 'box.setAttribute("aria-pressed", String(t.done));')
        html = html.replace('box.onchange =', 'box.onclick =').replace('t.done = box.checked', 't.done = !t.done')
        if allow_blank:
            html = html.replace('if (!text) return;', '')
        return html

    def run_app(self, html):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'index.html').write_text(html)
            result = subprocess.run(['node', str(ROOT / 'eval/check.mjs'), '--task', 'create', str(root)],
                                  capture_output=True, text=True, timeout=60,
                                  env={**os.environ, 'CHROME_PATH': CHROME})
            self.assertTrue(result.stdout.strip(),
                            f'evaluator exited {result.returncode} without JSON:\n{result.stderr}')
            return result

    def test_task_text_cannot_turn_a_toggle_into_a_delete_control(self):
        # Real button toggles are supported by the evaluator. A task containing the
        # word Delete must not cause its toggle's accessible name to match Delete.
        result = self.run_app(self.button_toggle_fixture())
        record = json.loads(result.stdout)
        self.assertEqual(record['checks']['delete'], 'pass', result.stderr)
        self.assertEqual(record['checks']['persist_reload'], 'pass', result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_button_toggle_count_catches_whitespace_task_regression(self):
        # Removing blank-input validation must fail even when tasks use aria-pressed buttons.
        result = self.run_app(self.button_toggle_fixture(allow_blank=True))
        record = json.loads(result.stdout)
        self.assertEqual(record['checks']['reject_blank'], 'fail', result.stderr)
        self.assertEqual(result.returncode, 1, result.stderr)


if __name__ == '__main__':
    unittest.main()
