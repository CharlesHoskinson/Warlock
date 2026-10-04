"""Freeze source inputs, compile the real Elm worker, and assert external fixtures.
Run through the protected qa_run.py launcher. This is CPU evidence only.
"""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
OUT = ROOT / 'qa' / ('replay-' + str(time.time_ns()))
OUT.mkdir()
INPUT = OUT / 'inputs'
INPUT.mkdir()
files = [ROOT / 'elm.json', *sorted((ROOT / 'src').glob('*.elm')),
         ROOT / 'qa/replay.cjs', ROOT / 'qa/fixtures.json', ROOT / 'qa/replay.py', ROOT / 'qa/mutations.py']
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed': False, 'scope': 'Compiled pure Elm context-menu CPU behavior; no native GUI acceptance',
          'inputs': {str(p.relative_to(ROOT)): sha(p) for p in files}, 'commands': []}
for path in files:
    destination = INPUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
try:
    for name, command in [
        ('compile', ['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--',
                     'elm', 'make', 'src/Replay.elm', '--output=' + str(OUT / 'replay.js')]),
        ('checks', ['node', str(INPUT / 'qa/replay.cjs'), str(OUT / 'replay.js'),
                    str(INPUT / 'qa/fixtures.json'), str(OUT / 'checks.json')])]:
        process = subprocess.run(command, cwd=INPUT, capture_output=True, text=True, timeout=180)
        (OUT / (name + '.stdout')).write_text(process.stdout)
        (OUT / (name + '.stderr')).write_text(process.stderr)
        report['commands'].append({'command': command, 'exitCode': process.returncode})
        print(name, process.returncode, flush=True)
        assert process.returncode == 0, process.stdout + process.stderr
    checks = json.loads((OUT / 'checks.json').read_text())
    assert checks['passed']
    for relative, digest in report['inputs'].items():
        assert sha(ROOT / relative) == digest, 'Source changed during replay: ' + relative
    report.update(checks)
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
