"""Protected incremental and final sampled Quint checks, never exhaustive verify."""
import argparse
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
parser = argparse.ArgumentParser()
parser.add_argument('--stage', choices=['sketch','smoke','final'], default='final')
args = parser.parse_args()
OUT = ROOT / 'qa' / ('model-' + str(time.time_ns()))
OUT.mkdir()
files = [*sorted((ROOT / 'spec').glob('*.qnt')), ROOT / 'spec/README.md', ROOT / 'qa/model.py']
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
inputs = {}
for path in files:
    destination = OUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    inputs[str(path.relative_to(ROOT))] = sha(path)
report = {'passed':False, 'stage':args.stage, 'scope':'Single-actor abstract context-menu safety; sampled evidence only', 'inputs':inputs, 'commands':[]}
QUINT = '/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
def run(name, arguments):
    command = [QUINT, *arguments]
    process = subprocess.run(command, cwd=OUT / 'spec', capture_output=True, text=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(process.stdout)
    (OUT / (name + '.stderr')).write_text(process.stderr)
    report['commands'].append({'command':command, 'exitCode':process.returncode})
    print(name, process.returncode, flush=True)
    assert process.returncode == 0, process.stdout + process.stderr
try:
    run('types-typecheck', ['typecheck','menu-types.qnt'])
    if args.stage != 'sketch':
        run('typecheck', ['typecheck','menu.qnt'])
        run('smoke', ['run','menu.qnt','--backend=typescript','--max-samples=10','--max-steps=10','--seed=174201','--invariants=safety'])
    if args.stage == 'final':
        run('test-typecheck', ['typecheck','menu_test.qnt'])
        tests = __import__('re').findall(r'\brun\s+(\w+Test)\s*=', (OUT / 'spec/menu_test.qnt').read_text())
        assert tests and len(tests) == len(set(tests))
        run('named', ['test','menu_test.qnt','--backend=typescript','--match=^('+'|'.join(tests)+')$', '--max-samples=1','--seed=174202','--out-itf=../named-{test}-{seq}.itf.json'])
        assert len(list(OUT.glob('named-*.itf.json'))) == len(tests)
        run('sampled', ['run','menu.qnt','--backend=typescript','--max-samples=1000','--max-steps=40','--seed=174203','--invariants=safety','--witnesses', 'opened', 'navigated', 'activated', 'dismissed', 'received', 'observed', 'retired', 'staleReceived', 'rejected','--out-itf=../sample-{seq}.itf.json'])
        witnesses = {name: int(count) for name,count in __import__('re').findall(r'(\w+) was witnessed in (\d+) trace', (OUT / 'sampled.stdout').read_text())}
        assert set(witnesses) == {'opened','navigated','activated','dismissed','received','observed','retired','staleReceived','rejected'}
        assert all(count > 0 for count in witnesses.values()), witnesses
        assert 'Trace length statistics: max=41, min=41, average=41.00' in (OUT / 'sampled.stdout').read_text()
        report.update(namedScenarios=len(tests), invariantSamples=1000, maxSteps=40, witnesses=witnesses)
    for relative,digest in inputs.items(): assert sha(ROOT / relative) == digest, relative
    report['passed'] = True
except Exception as error: report['error'] = repr(error)
report['artifacts'] = {str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
