"""Compile the actual pure Elm policy from captured inputs; protected CPU only."""
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT.parents[1] / 'implementation/elm-menu-native-pair-v8/elm.json'
OUT = ROOT / 'qa' / ('geometry-policy-' + str(time.time_ns()))
OUT.mkdir()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


files = [ROOT / 'src/WindowGeometry.elm', ROOT / 'qa/geometry-policy-worker.elm',
         ROOT / 'qa/geometry-policy-tests.js', Path(__file__).resolve()]
hashes = {str(path.relative_to(ROOT)): sha(path) for path in files}
report = {'passed': False, 'nativeAcceptance': False, 'transportIntegrated': False,
          'scope': 'Actual compiled Elm pure policy with independent external scenario oracles',
          'inputs': hashes, 'package': str(PACKAGE), 'packageSHA256': sha(PACKAGE), 'commands': []}
for path in files:
    dest = OUT / 'inputs' / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    dest.chmod(0o444)
shutil.copy2(PACKAGE, OUT / 'inputs/elm.json')
shutil.copy2(ROOT / 'qa/geometry-policy-worker.elm', OUT / 'inputs/src/GeometryPolicyWorker.elm')


def run(name, args):
    proc = subprocess.run(args, cwd=OUT / 'inputs', capture_output=True, timeout=180)
    (OUT / (name + '.stdout')).write_bytes(proc.stdout)
    (OUT / (name + '.stderr')).write_bytes(proc.stderr)
    report['commands'].append({'name': name, 'command': args, 'exitCode': proc.returncode})
    print(name, proc.returncode, flush=True)
    assert proc.returncode == 0, proc.stderr.decode(errors='replace')[-6000:]
    return proc.stdout


try:
    run('compile', ['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--', 'elm', 'make',
                    'src/GeometryPolicyWorker.elm', '--output=' + str(OUT / 'worker.js')])
    raw = run('scenarios', ['node', str(OUT / 'inputs/qa/geometry-policy-tests.js'), str(OUT / 'worker.js')])
    checks = json.loads(raw.decode().strip().splitlines()[-1])
    assert checks['passed'] and checks['checkCount'] >= 30
    for rel, value in hashes.items():
        assert sha(ROOT / rel) == sha(OUT / 'inputs' / rel) == value, rel
    assert sha(PACKAGE) == sha(OUT / 'inputs/elm.json') == report['packageSHA256']
    assert sha(OUT / 'inputs/src/GeometryPolicyWorker.elm') == hashes['qa/geometry-policy-worker.elm']
    report.update(checks, compiledWorkerSHA256=sha(OUT / 'worker.js'))
except Exception as error:
    report.update(passed=False, error=repr(error))
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
raise SystemExit(not report['passed'])
