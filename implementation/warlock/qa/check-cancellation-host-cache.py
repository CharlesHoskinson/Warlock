"""Protected exact cache/certificate and coordinator output checks; C writer/native doubles."""
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from qa_launch import require_qa_scope

scope = require_qa_scope()
ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = ROOT / 'qa/cancellation-host-cache-cases'
OUT = ROOT / 'qa/runs' / ('cancellation-host-cache-' + str(time.time_ns()))
OUT.mkdir(parents=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
paths = [ROOT / 'adapter' / name for name in [
    'cancellation_coordinator.py', 'daemon.py', 'cancellation_host_admission.py', 'cancellation_host_cache.py',
    'cancellation_host_settlement.py', 'cancellation_ledger.py',
    'cancellation_legacy.py', 'recovery_store.py', 'cancellation_endpoint.py',
    'effect_endpoint.py', 'endpoint.py', 'recovery_journal.py', 'durable_ledger.py',
    'admission_ledger.py', 'retirement_ledger.py', 'delivery_ledger.py',
    'workspace_navigation.py', 'reconciliation.py', 'grant_endpoint.py']]
paths += sorted((ROOT / 'qa/cancellation-coordinator-cases').glob('*.py')) + sorted(CASES.glob('*.py')) + [ROOT / 'qa/cancellation-store-cases/fixture.py', pathlib.Path(__file__)]
inputs = {str(p.relative_to(ROOT)): sha(p) for p in paths}
report = {'passed': False, 'scope': scope, 'inputs': inputs, 'commands': [],
          'nativeAcceptance': False, 'originalAcceptance': False,
          'productionDefaultCancellationEnabled': False,
          'completeRuntimeClosureClaimed': False,
          'limits': 'Actual coordinator and daemon with real V6/V7 stores; strict native-schema response and inert service/event doubles. No C/Elm/deadline-origin/physical-input/authenticated-transport/release acceptance.'}
try:
    for name in ['cache', 'faults', 'orphan', 'reader_guards', 'check_pair_lookup', 'orphan_faults']:
        args = [sys.executable, '-B', str(CASES / (name + '.py'))]
        try:
            result = subprocess.run(args, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired as error:
            (OUT / (name + '.stdout')).write_bytes(error.stdout or b'')
            (OUT / (name + '.stderr')).write_bytes(error.stderr or b'')
            report['commands'].append({'name': name, 'argv': args, 'timedOut': True})
            raise
        (OUT / (name + '.stdout')).write_bytes(result.stdout)
        (OUT / (name + '.stderr')).write_bytes(result.stderr)
        command = {'name': name, 'argv': args, 'exitCode': result.returncode,
                   'stdoutSHA256': sha(OUT / (name + '.stdout')),
                   'stderrSHA256': sha(OUT / (name + '.stderr'))}
        report['commands'].append(command)
        if result.returncode:
            raise RuntimeError(name + ' failed')
        observed = json.loads(result.stdout)
        if observed.get('passed') is not True:
            raise RuntimeError(name + ' did not report passing assertions')
        command['observations'] = observed
    for p in paths:
        if sha(p) != inputs[str(p.relative_to(ROOT))]:
            raise RuntimeError('Input changed during run: ' + str(p))
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'),
                  'error': report.get('error')}))
sys.exit(0 if report['passed'] else 1)
