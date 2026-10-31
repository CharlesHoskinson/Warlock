#!/usr/bin/env python3
"""Root-only original REV005 admission regression; no product/native execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from qa_cpu import registry_inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    scope = require_qa_scope()
    runtime_base()
    output = ROOT / '.warlock-contributor' / ('registry-cpu-' + str(time.time_ns()))
    output.mkdir(parents=True)
    sources = {name: sha(ROOT / name) for name in sorted(registry_inputs(ROOT, args.self_test))}
    tools = {name: Path(path).resolve() for name, path in [('python', sys.executable), ('git', shutil.which('git') or '/missing-git')]}
    report = {'schema': 1, 'requirement': 'ELM-REV-005', 'scenario': 'requirement-ownership',
              'scope': 'Actual development admission transactions in disposable Git fixtures; administrative EARS only',
              'passed': False, 'nativeAcceptance': False, 'releaseAccepted': False,
              'protectedScope': scope, 'sources': sources, 'commands': [],
              'tools': {name: {'path': str(path), 'sha256': sha(path)} for name, path in tools.items()}}

    def run(name, command, timeout=180):
        child = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        (output / (name + '.stdout')).write_text(child.stdout)
        (output / (name + '.stderr')).write_text(child.stderr)
        report['commands'].append({'name': name, 'argv': command, 'exit': child.returncode})
        print(name, child.returncode, flush=True)
        if child.returncode:
            raise RuntimeError(name + ' failed; retained raw stdout/stderr')

    try:
        run('python-version', [sys.executable, '--version'])
        run('git-version', [str(tools['git']), '--version'])
        run('registry-admission', [sys.executable, '-B', str(ROOT / 'implementation/warlock/qa/check-registry-admission.py'), str(output / 'admission.json')])
        if args.self_test:
            run('plugin-self-test', [sys.executable, '-B', str(ROOT / 'plugins/warlock-contributor/scripts/warlock.py'),
                                     '--repo', str(ROOT), '--json', 'self-test'])
        if not all(sha(ROOT / name) == digest for name, digest in sources.items()):
            raise RuntimeError('Reviewed source inputs changed during verification')
        if not all(sha(Path(row['path'])) == row['sha256'] for row in report['tools'].values()):
            raise RuntimeError('Development interpreter changed during verification')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json'), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
