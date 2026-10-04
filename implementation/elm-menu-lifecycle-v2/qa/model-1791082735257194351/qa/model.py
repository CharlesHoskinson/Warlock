"""Protected incremental sampled Quint evidence; never exhaustive verify."""
import argparse
import hashlib
import json
import re
import resource
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
parser = argparse.ArgumentParser()
parser.add_argument('--stage', choices=['types', 'smoke', 'final'], default='final')
args = parser.parse_args()
OUT = ROOT / 'qa' / ('model-' + str(time.time_ns()))
OUT.mkdir()
files = [*sorted((ROOT / 'spec').glob('*.qnt')), ROOT / 'qa/model.py']
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
inputs = {}
for path in files:
    destination = OUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    inputs[str(path.relative_to(ROOT))] = sha(path)
report = {'passed': False, 'stage': args.stage,
          'scope': 'Sampled single-actor bounded abstract lifecycle; not native acceptance or implementation equivalence',
          'inputs': inputs, 'commands': []}
QUINT = '/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
def run(name, arguments):
    command = [QUINT, *arguments]
    process = subprocess.run(command, cwd=OUT / 'spec', capture_output=True, text=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(process.stdout)
    (OUT / (name + '.stderr')).write_text(process.stderr)
    report['commands'].append({'command': command, 'exitCode': process.returncode})
    print(name, process.returncode, flush=True)
    assert process.returncode == 0, process.stdout + process.stderr
try:
    run('types', ['typecheck', 'menu-types.qnt'])
    if args.stage != 'types':
        run('typecheck', ['typecheck', 'menu.qnt'])
        run('smoke', ['run', 'menu.qnt', '--backend=typescript', '--max-samples=10',
                      '--max-steps=10', '--seed=284201', '--invariants=safety'])
    if args.stage == 'final':
        run('test-typecheck', ['typecheck', 'menu_test.qnt'])
        tests = re.findall(r'\brun\s+(\w+Test)\s*=', (OUT / 'spec/menu_test.qnt').read_text())
        assert tests and len(tests) == len(set(tests))
        run('named', ['test', 'menu_test.qnt', '--backend=typescript',
                      '--match=^(' + '|'.join(tests) + ')$', '--max-samples=1',
                      '--seed=284202', '--out-itf=../named-{test}-{seq}.itf.json'])
        assert len(list(OUT.glob('named-*.itf.json'))) == len(tests)
        witnesses = ['opened', 'activated', 'received', 'rejectedReceipt', 'dismissed', 'navigated',
                     'capacityReached', 'capacityRefused', 'capacityFreed',
                     'retired', 'duplicateRetired', 'exhaustedReached',
                     'exhaustedReceipt', 'unknownRebound', 'rejectedActivation']
        run('sampled', ['run', 'menu.qnt', '--backend=typescript', '--max-samples=1000',
                        '--max-steps=40', '--seed=284203', '--invariants=safety',
                        '--witnesses', *witnesses, '--out-itf=../sample-{seq}.itf.json'])
        counts = {name: int(count) for name, count in re.findall(
            r'(\w+) was witnessed in (\d+) trace', (OUT / 'sampled.stdout').read_text())}
        assert set(counts) == set(witnesses) and all(count > 0 for count in counts.values()), counts
        assert 'Trace length statistics: max=41, min=41, average=41.00' in (OUT / 'sampled.stdout').read_text()
        report.update(namedScenarios=len(tests), invariantSamples=1000, maxSteps=40, witnesses=counts)
    for relative, digest in inputs.items():
        assert sha(ROOT / relative) == digest, relative
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
report['artifacts'] = {str(path.relative_to(OUT)): sha(path) for path in OUT.rglob('*') if path.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
