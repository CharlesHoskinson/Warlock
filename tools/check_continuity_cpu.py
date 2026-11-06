#!/usr/bin/env python3
"""Fixed mocked continuity suite; no queue, service, compiler or native campaign."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from qa_cpu import continuity_inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base  # ty: ignore[import-not-found]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 1:
        raise RuntimeError('This runner accepts no arguments')
    scope = require_qa_scope()
    runtime_base()
    output = ROOT / '.warlock-contributor' / ('continuity-cpu-' + str(time.time_ns()))
    output.mkdir(parents=True, mode=0o700)
    sources = {name: digest(ROOT / name) for name in sorted(continuity_inputs(ROOT))}
    python = Path(sys.executable).resolve()
    interpreter_hash = digest(python)
    report: dict = {'schema': 1, 'passed': False, 'scope': 'Mocked continuity support checks only',
                  'nativeAcceptance': False, 'releaseAccepted': False, 'protectedScope': scope,
                  'sources': sources, 'commands': []}
    try:
        argv = [str(python), '-I', '-B', '-m', 'unittest', 'discover',
                '-s', str(ROOT / 'tools'), '-p', 'test_warlock_continuity.py', '-q']
        child = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=180, check=False,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        (output / 'unittest.stdout').write_text(child.stdout)
        (output / 'unittest.stderr').write_text(child.stderr)
        report['commands'].append({'argv': argv, 'exit': child.returncode})
        if child.returncode:
            raise RuntimeError('Mocked continuity suite failed; see retained logs')
        if any(digest(ROOT / name) != sha for name, sha in sources.items()) or digest(python) != interpreter_hash:
            raise RuntimeError('Continuity source or interpreter changed during execution')
        report['passed'] = True
    except Exception as error:  # noqa: BLE001 -- retain failure evidence before exiting
        report['error'] = str(error)
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
