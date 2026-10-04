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
def run(name, arguments, expected_failure=False):
    command = [QUINT, *arguments]
    process = subprocess.run(command, cwd=OUT / 'spec', capture_output=True, text=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(process.stdout)
    (OUT / (name + '.stderr')).write_text(process.stderr)
    report['commands'].append({'command': command, 'exitCode': process.returncode})
    print(name, process.returncode, flush=True)
    if expected_failure:
        assert process.returncode != 0 and 'safety' in process.stdout and 'violation' in process.stdout.lower(), process.stdout + process.stderr
    else:
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
        assert set(counts) == set(witnesses)
        sparse = {'capacityRefused', 'unknownRebound'}
        assert all(count > 0 for name, count in counts.items() if name not in sparse), counts
        assert 'Trace length statistics: max=41, min=41, average=41.00' in (OUT / 'sampled.stdout').read_text()
        targeted_witnesses = ['capacityReached', 'capacityRefused', 'capacityFreed', 'unknownRebound']
        run('targeted', ['run', 'menu.qnt', '--backend=typescript', '--step=capacityStep',
                         '--max-samples=1000', '--max-steps=40', '--seed=284204', '--invariants=safety',
                         '--witnesses', *targeted_witnesses, '--out-itf=../targeted-{seq}.itf.json'])
        targeted_counts = {name: int(count) for name, count in re.findall(
            r'(\w+) was witnessed in (\d+) trace', (OUT / 'targeted.stdout').read_text())}
        assert set(targeted_counts) == set(targeted_witnesses) and all(count > 0 for count in targeted_counts.values()), targeted_counts
        assert 'Trace length statistics: max=41, min=41, average=41.00' in (OUT / 'targeted.stdout').read_text()
        combined = {name: count + targeted_counts.get(name, 0) for name, count in counts.items()}
        assert all(count > 0 for count in combined.values())
        # Unsafe guard mutation must typecheck, then fail the independent safety
        # invariant. A parse/type failure cannot count as mutation detection.
        mutant = OUT / 'mutant-wrong-receipt'
        shutil.copytree(OUT / 'spec', mutant)
        source = (mutant / 'menu.qnt').read_text()
        anchor = 'found or (op.id == id and op.binding == b)'
        assert source.count(anchor) == 1
        (mutant / 'menu.qnt').write_text(source.replace(anchor, 'found or (op.id == id)'))
        run('mutant-typecheck', ['typecheck', '../mutant-wrong-receipt/menu.qnt'])
        run('mutant-invariant', ['run', '../mutant-wrong-receipt/menu.qnt', '--backend=typescript',
                                '--max-samples=1000', '--max-steps=40', '--seed=284205',
                                '--invariants=safety', '--out-itf=../mutant-counterexample.itf.json'], expected_failure=True)
        report.update(namedScenarios=len(tests), invariantSamples=2000, maxSteps=40,
                      witnesses=combined, sampledProfiles=[
                          {'step': 'step', 'samples': 1000, 'witnesses': counts},
                          {'step': 'capacityStep', 'samples': 1000, 'witnesses': targeted_counts}],
                      unsafeGuardMutationDetected=True)
    for relative, digest in inputs.items():
        assert sha(ROOT / relative) == digest, relative
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
report['artifacts'] = {str(path.relative_to(OUT)): sha(path) for path in OUT.rglob('*') if path.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
