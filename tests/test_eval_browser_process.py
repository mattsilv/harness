"""A failed Chrome launch must also stop its surviving profile writer."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'posix', 'Chrome process groups require POSIX')
class BrowserProcessTests(unittest.TestCase):
    def test_failed_browser_leader_cannot_leave_a_profile_writer(self):
        self.check_cleanup(interrupt=False)

    def test_interrupted_evaluator_stops_its_detached_browser_group(self):
        self.check_cleanup(interrupt=True)

    def check_cleanup(self, *, interrupt):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'index.html').write_text('<h1>Fixture</h1>')
            marker, pidfile = root / 'late-write', root / 'child-pid'
            child = ('import pathlib,time; time.sleep(0.8); '
                     f'pathlib.Path({str(marker)!r}).write_text("writer survived"); '
                     'time.sleep(20)')
            shim = root / 'chrome'
            shim.write_text(f'#!{sys.executable}\nimport pathlib,subprocess,sys\n'
                            f'p=subprocess.Popen([sys.executable,"-c",{child!r}], '
                            'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                            f'pathlib.Path({str(pidfile)!r}).write_text(str(p.pid))\n'
                            + ('import time; time.sleep(20)\n' if interrupt else ''))
            shim.chmod(0o755)
            try:
                proc = subprocess.Popen(['node', str(ROOT / 'eval/check.mjs'), '--task', 'create', str(root)],
                                        env={**os.environ, 'CHROME_PATH': str(shim), 'TMPDIR': str(root)},
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    if interrupt:
                        deadline = time.monotonic() + 5
                        while not pidfile.exists() and time.monotonic() < deadline:
                            time.sleep(0.01)
                        self.assertTrue(pidfile.exists(), 'fake Chrome did not start')
                        proc.terminate()
                    stdout, stderr = proc.communicate(timeout=5)
                    self.assertNotEqual(proc.returncode, 0)
                    if interrupt:
                        self.assertEqual(proc.returncode, 143, stderr)
                    else:
                        self.assertIn('Chrome exited', stderr)
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.communicate()
                time.sleep(1)
                self.assertFalse(marker.exists(), 'Chrome child continued after evaluator cleanup')
                self.assertEqual(list(root.glob('harness-eval-*')), [])
            finally:
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass


if __name__ == '__main__':
    unittest.main()
