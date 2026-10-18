#!/usr/bin/env python3
"""One bounded, maintainer-only comparison. See EVAL.md; no API-key billing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TASKS = ('create', 'update', 'delivery')
TRIGGER = '\nBefore reporting completed code work, run `python3 scripts/delivery-check.py` and resolve any failure.\n'


def command(args, *, cwd=ROOT, env=None, timeout=30):
    return subprocess.run(list(map(str, args)), cwd=cwd, env=env, text=True,
                          capture_output=True, timeout=timeout, check=True).stdout.strip()


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def clean_env(work):
    # Do not pass API keys, shell startup hooks, or external Git configuration to tools.
    return {'PATH': '/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin',
            'LANG': 'en_US.UTF-8', 'TMPDIR': str(work / '.tmp'),
            'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
            'GIT_AUTHOR_NAME': 'eval', 'GIT_COMMITTER_NAME': 'eval',
            'GIT_AUTHOR_EMAIL': 'eval@example.invalid',
            'GIT_COMMITTER_EMAIL': 'eval@example.invalid'}


def permissions(work):
    # Explicit exclusions are required: :minimal includes system temporary paths.
    fs = {':root': 'deny', ':minimal': 'read', '/Users': 'deny',
          '/private/tmp': 'deny', '/private/var/folders': 'deny',
          '/opt/homebrew': 'read', str(work): 'write',
          str(work / '.git'): 'write', str(work / '.git' / 'config'): 'read',
          str(work / '.git' / 'info'): 'read',
          str(work / '.codex'): 'deny', str(work / '.agents'): 'deny',
          str(work / '.git' / 'hooks'): 'deny'}
    # TOML inline table, with JSON quoting for string keys and values.
    table = '{' + ','.join(f'{json.dumps(k)}={json.dumps(v)}' for k, v in fs.items()) + '}'
    return ['-c', 'permissions.eval.filesystem=' + table,
            '-c', 'permissions.eval.network.enabled=false']


def settings(work, model, effort):
    flags = ['--ignore-user-config', '--ignore-rules', '--ephemeral', '--strict-config',
             '-c', 'default_permissions="eval"', '-c', 'approval_policy="never"',
             '-c', 'web_search="disabled"', '-c', f'model_reasoning_effort="{effort}"',
             '-c', 'shell_environment_policy.inherit="none"',
             '-c', 'shell_environment_policy.set=' + '{' + ','.join(
                 f'{json.dumps(k)}={json.dumps(v)}' for k, v in clean_env(work).items()) + '}',
             '-c', 'shell_environment_policy.ignore_default_excludes=false',
             '-m', model, '-C', str(work)] + permissions(work)
    for name in ('apps', 'plugins', 'browser_use', 'browser_use_external', 'computer_use',
                 'in_app_browser', 'image_generation', 'multi_agent', 'memories', 'hooks',
                 'shell_snapshot', 'view_image', 'skill_search'):
        flags += ['--disable', name]
    flags += ['--enable', 'skip_host_skill_discovery']
    return flags


def preflight(work, hidden):
    """Fail closed before any model call if the runtime cannot enforce boundaries."""
    code = '''import pathlib,socket,sys
root,hidden=map(pathlib.Path,sys.argv[1:])
p=root/'probe'; p.write_text('ok'); assert p.read_text()=='ok'; p.unlink()
for path in (hidden, pathlib.Path.home()/'.codex'/'auth.json'):
 try: path.read_bytes()
 except PermissionError: pass
 else: raise SystemExit('private read was not denied')
s=socket.socket(); s.settimeout(1)
try: s.connect(('127.0.0.1',9))
except PermissionError: pass
except OSError as e: raise SystemExit('network denial unproven: '+str(e.errno))
else: raise SystemExit('network was allowed')
'''
    command(['codex', 'sandbox', '-P', 'eval', '-C', work, *permissions(work),
             sys.executable, '-c', code, work, hidden], cwd=work, env=clean_env(work))


def prompt(task):
    text = (ROOT / 'EVAL.md').read_text()
    match = re.search(rf'^## {task.title()} prompt\n\n> (.+)$', text, re.M)
    if not match:
        raise ValueError(f'missing {task} prompt')
    return match[1]


def prepare(work, revision, candidate, task, fixture_bytes, helper_bytes):
    work.mkdir()
    env = clean_env(work)
    command(['git', 'init', '-q', '-b', 'main', work], env=env)
    names = command(['git', 'ls-tree', '-r', '--name-only', revision, '--', 'template']).splitlines()
    for name in names:
        target = work / Path(name).relative_to('template')
        target.parent.mkdir(parents=True, exist_ok=True)
        data = command(['git', 'show', f'{revision}:{name}']) + '\n'
        if name.endswith('.md'):
            data = re.sub(r'^[ \t]*<!--.*?-->[ \t]*\n', '', data, flags=re.M | re.S)
        target.write_text(data)
    cfg = work / 'PROJECT_CONFIG.md'
    values = {'Stack': 'A single static HTML/JS page with localStorage; no build step and no server.',
              'Merge policy': '`on-request`.', 'Maintenance tracking issue': 'None.',
              'Secrets': 'None needed.', 'Secrets location': 'None needed.'}
    text = cfg.read_text()
    for key, value in values.items():
        text = re.sub(rf'^- \*\*{key}:\*\*.*$', f'- **{key}:** {value}', text, flags=re.M)
    if 'set during setup' in text.lower():
        raise ValueError('unresolved setup values')
    # No remote exists: task work must end as a local reviewable branch, not a remote PR.
    text += '\nEvaluation environment: no remote, network, external services, or subagents. Use local checks. Stop after a clean branch commit and report; do not publish.\n'
    cfg.write_text(text)
    (work / '.gitignore').write_text('.tmp/\n')
    (work / '.tmp').mkdir()
    if task != 'create':
        (work / 'index.html').write_bytes(fixture_bytes)
    if candidate:
        (work / 'scripts' / 'delivery-check.py').write_bytes(helper_bytes)
        with (work / 'AGENTS.md').open('a') as out:
            out.write(TRIGGER)
    command(['git', 'add', '-A'], cwd=work, env=env)
    command(['git', 'commit', '-qm', 'Baseline'], cwd=work, env=env)
    return command(['git', 'rev-parse', 'HEAD'], cwd=work, env=env)


def run_process(args, work, log, timeout):
    """Bound the whole process group, including children, on timeout and normal exit."""
    start = time.monotonic()
    with log.open('w') as out, log.with_suffix('.stderr').open('w') as err:
        proc = subprocess.Popen(list(map(str, args)), cwd=work, env=clean_env(work),
                                stdout=out, stderr=err, start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout)
            state = 'completed' if rc == 0 else 'failed'
        except subprocess.TimeoutExpired:
            state, rc = 'timeout', None
        finally:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            # A child can outlive its parent or ignore TERM. Clean the entire group.
            time.sleep(0.1)
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    return state, rc, round(time.monotonic() - start, 3)


def usage(log):
    found = None
    for line in log.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get('type') == 'turn.completed':
            found = event.get('usage')
    return found or 'unavailable'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, help='pinned harness Git revision')
    parser.add_argument('--out', required=True, type=Path, help='new directory outside this checkout')
    parser.add_argument('--model', required=True)
    parser.add_argument('--effort', choices=['low', 'medium', 'high'], default='high')
    parser.add_argument('--seconds', type=int, default=180, help='per-model-run wall limit (1..600)')
    parser.add_argument('--run-subscription', action='store_true', help='run 12 calls using existing ChatGPT login; never API keys')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        parser.error('this first adapter is verified on macOS only')
    if not 1 <= args.seconds <= 600:
        parser.error('--seconds must be 1..600')
    out = args.out.resolve()
    if out.is_relative_to(ROOT) or out.exists():
        parser.error('--out must be a new directory outside the checkout')
    revision = command(['git', 'rev-parse', '--verify', '--end-of-options', args.baseline + '^{commit}'])
    out.mkdir(parents=True)
    fixture_bytes = (HERE / 'fixture' / 'index.html').read_bytes()
    helper_bytes = (HERE / 'candidates' / 'delivery-check.py').read_bytes()
    manifest = {'baseline': revision, 'candidate': {'base': revision, 'helper_sha256': digest(helper_bytes), 'trigger': TRIGGER},
                'evaluator': command(['git', 'rev-parse', 'HEAD']),
                'evaluator_sha256': digest((HERE / 'check.mjs').read_bytes()),
                'delivery_evaluator_sha256': digest((HERE / 'delivery.mjs').read_bytes()),
                'fixture_sha256': digest(fixture_bytes),
                'runner_sha256': digest(Path(__file__).read_bytes()),
                'model_requested': args.model, 'effort_requested': args.effort,
                'model_version_verified': False, 'sampling_seed': 'not supported',
                'cli': command(['codex', '--version']), 'repetitions': 2,
                'seconds_per_run': args.seconds, 'maximum_runs': 12,
                'billing': 'existing subscription only; incremental cost unavailable',
                'network': 'task tools denied; model transport outside tool sandbox',
                'status': 'planned', 'prompts': {task: prompt(task) for task in TASKS}}
    dump(out / 'manifest.json', manifest)
    if not args.run_subscription:
        print(json.dumps({'status': 'planned', 'manifest': str(out / 'manifest.json')}))
        return
    # Check the normal CLI's auth mode without reading or copying credentials.
    auth = subprocess.run(['codex', 'login', 'status'], capture_output=True, text=True, timeout=30)
    if auth.returncode or 'Logged in using ChatGPT' not in auth.stdout + auth.stderr:
        raise RuntimeError('existing ChatGPT login required; no API-key fallback')
    canary = out / 'private-canary'
    canary.write_text('evaluator-owned')
    records = out / 'results.jsonl'
    manifest['status'] = 'running'
    dump(out / 'manifest.json', manifest)
    # Counterbalance revision order between repetitions. Never discard failed runs.
    for task in TASKS:
        for repetition in (1, 2):
            for variant in (('baseline', 'candidate') if repetition == 1 else ('candidate', 'baseline')):
                name = f'{task}-{repetition}-{variant}'
                work = out / name
                try:
                    base = prepare(work, revision, variant == 'candidate', task, fixture_bytes, helper_bytes)
                    preflight(work, canary)
                except (ValueError, OSError, subprocess.SubprocessError) as error:
                    record = {'run': name, 'status': 'blocked', 'error': type(error).__name__}
                    with records.open('a') as dest:
                        dest.write(json.dumps(record) + '\n')
                    manifest['status'] = 'blocked'
                    manifest['blocked_run'] = name
                    dump(out / 'manifest.json', manifest)
                    raise
                # The evaluator and runner are trusted inputs; stop on concurrent edits.
                if (digest((HERE / 'check.mjs').read_bytes()) != manifest['evaluator_sha256'] or
                        digest((HERE / 'delivery.mjs').read_bytes()) != manifest['delivery_evaluator_sha256']):
                    raise RuntimeError('evaluator changed during comparison')
                instruction_bytes = sum((work / p).stat().st_size for p in ('AGENTS.md', 'CLAUDE.md', 'PROJECT_CONFIG.md'))
                log = out / f'{name}.events.jsonl'
                cmd = ['codex', 'exec', *settings(work, args.model, args.effort), '--json', manifest['prompts'][task]]
                state, rc, elapsed = run_process(cmd, work, log, args.seconds)
                record = {'run': name, 'task': task, 'variant': variant, 'repetition': repetition,
                          'status': state, 'exit_code': rc, 'wall_seconds': elapsed, 'usage': usage(log),
                          'cost_usd': 'unavailable', 'instruction_bytes': instruction_bytes,
                          'initial_commit': base, 'harness': revision, 'checks': None,
                          'helper_invocation': 'not observed'}
                # The trusted evaluator runs only after the candidate process group exits.
                checklog = out / f'{name}.check.json'
                check_state, check_rc, _ = run_process(
                    ['node', HERE / 'check.mjs', '--task', task, work, '--baseline', base,
                     '--model', args.model, '--effort', args.effort, '--harness', revision +
                     ('+delivery-candidate' if variant == 'candidate' else '')], work, checklog, 90)
                record['check_exit_code'] = check_rc
                try:
                    record['checks'] = json.loads(checklog.read_text())
                except json.JSONDecodeError:
                    record['check_error'] = check_state + ': no valid evaluator record'
                # Commands are evidence of invocation, not proof that the helper passed.
                for line in log.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    item = event.get('item', {})
                    if item.get('type') == 'command_execution' and 'python3 scripts/delivery-check.py' in item.get('command', ''):
                        record['helper_invocation'] = 'observed command'
                with records.open('a') as dest:
                    dest.write(json.dumps(record) + '\n')
                print(json.dumps({'run': name, 'status': state, 'check_exit_code': record.get('check_exit_code')}), flush=True)
    manifest['status'] = 'complete'
    manifest['decision'] = 'requires review; no automatic adoption'
    dump(out / 'manifest.json', manifest)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'compare: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(2)
