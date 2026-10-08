"""Exercise the capture CLI contract without requiring a browser in fixture CI."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "template/scripts/ui-capture.mjs"
DRIVER = """
import { appendFileSync } from 'node:fs';
const log = value => appendFileSync(process.env.CAPTURE_LOG, value + '\\n');
export const engine = { launch: async () => ({
  newContext: async ({ viewport }) => ({
    setDefaultTimeout() {},
    newPage: async () => {
      let url;
      return {
        goto: async value => { url = value; return { ok: () => !url.includes('fail'), status: () => 500 }; },
        url: () => url + (process.env.CAPTURE_SUFFIX || ''),
        locator: () => ({ waitFor: async () => {} }),
        evaluate: async () => {},
        screenshot: async () => Buffer.from(`${url}:${viewport.width}:${process.env.CAPTURE_REV || '1'}`),
        close: async () => log('page closed'),
      };
    },
    close: async () => log('context closed'),
  }),
  close: async () => log('browser closed'),
}) };
"""


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / "templates.json"
        self.driver = self.root / "driver.mjs"
        self.driver.write_text(DRIVER)
        self.log = self.root / "capture.log"
        self.data = {
            "viewports": {"desktop": {"width": 1440, "height": 900}, "mobile": {"width": 390, "height": 844}},
            "templates": [
                {"id": "home", "title": "Home", "path": "/", "ready": "main"},
                {"id": "detail", "title": "Detail", "path": "/items/example", "parent": "home", "ready": "main"},
            ],
        }

    def run_capture(self, *args, revision="1", suffix=""):
        self.manifest.write_text(json.dumps(self.data))
        return subprocess.run([
            "node", str(SCRIPT), "--driver", str(self.driver), "--browser", "engine",
            "--url", "http://localhost:1234", "--manifest", str(self.manifest), *args,
        ], cwd=self.root, env={**os.environ, "CAPTURE_LOG": str(self.log), "CAPTURE_REV": revision, "CAPTURE_SUFFIX": suffix},
            capture_output=True, text=True, timeout=30)

    def test_capture_sitemap_and_nonmutating_freshness_check(self):
        result = self.run_capture()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.root.glob("screenshots/*/*.png"))), 4)
        self.assertIn("  - Detail (detail)", (self.root / "README.md").read_text())
        self.assertEqual(self.run_capture("--check").returncode, 0)
        before = (self.root / "screenshots/home/mobile.png").read_bytes()
        result = self.run_capture("--check", revision="2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("screenshots/home/mobile.png", result.stderr)
        self.assertEqual((self.root / "screenshots/home/mobile.png").read_bytes(), before)

    def test_failed_batch_preserves_previous_images_and_closes_browser(self):
        self.assertEqual(self.run_capture().returncode, 0)
        before = (self.root / "screenshots/home/desktop.png").read_bytes()
        self.data["templates"][1]["path"] = "/fail"
        result = self.run_capture(revision="2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("detail/desktop", result.stderr)
        self.assertEqual((self.root / "screenshots/home/desktop.png").read_bytes(), before)
        self.assertTrue(self.log.read_text().endswith("browser closed\n"))

    def test_removed_templates_are_detected_and_cleaned(self):
        self.assertEqual(self.run_capture().returncode, 0)
        self.data["templates"].pop()
        self.assertNotEqual(self.run_capture("--check").returncode, 0)
        self.assertEqual(self.run_capture().returncode, 0)
        self.assertFalse((self.root / "screenshots/detail/desktop.png").exists())

    def test_commonjs_driver_default_export(self):
        self.driver = self.root / "driver.cjs"
        self.driver.write_text(DRIVER.replace("import { appendFileSync } from 'node:fs';", "const { appendFileSync } = require('node:fs');")
                               .replace("export const engine =", "const engine =") + "module.exports = (() => ({ engine }))();\n")
        result = self.run_capture()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_trailing_slash_is_not_a_redirect(self):
        self.assertEqual(self.run_capture(suffix="/").returncode, 0)
        result = self.run_capture(suffix="x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected redirect", result.stderr)

    def test_invalid_tree_and_paths_fail_before_browser_launch(self):
        for field, value in [("id", "../escape"), ("parent", "detail"), ("path", "//example.invalid/")]:
            with self.subTest(field=field):
                original = dict(self.data["templates"][1])
                self.data["templates"][1][field] = value
                self.assertNotEqual(self.run_capture().returncode, 0)
                self.assertFalse(self.log.exists())
                self.data["templates"][1] = original


if __name__ == "__main__":
    unittest.main()
